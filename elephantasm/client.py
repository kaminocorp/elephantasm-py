"""Main Elephantasm client class for HTTP API communication."""

from datetime import datetime
from typing import Any
from uuid import UUID

import httpx

from .config import settings
from .exceptions import (
    AuthenticationError,
    ElephantasmError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .types import Anima, AnimaCreate, Event, EventCreate, EventType, MemoryPack

# Mapping from uppercase enum names to dot-notation API values
_EVENT_TYPE_ALIASES: dict[str, str] = {
    "MESSAGE_IN": "message.in",
    "MESSAGE_OUT": "message.out",
    "TOOL_CALL": "tool.call",
    "TOOL_RESULT": "tool.result",
    "SYSTEM": "system",
}

_VALID_EVENT_TYPES: set[str] = {
    "message.in", "message.out", "tool.call", "tool.result", "system",
}


def _resolve_event_type(event_type: str | EventType) -> str:
    """Resolve event_type to a valid API string value.

    Accepts:
      - EventType enum members (EventType.TOOL_CALL -> "tool.call")
      - Dot-notation strings ("tool.call" -> "tool.call")
      - Uppercase enum names ("TOOL_CALL" -> "tool.call")

    Raises:
        ValueError: For unrecognized strings.
    """
    if isinstance(event_type, EventType):
        return event_type.value

    if event_type in _VALID_EVENT_TYPES:
        return event_type

    alias = _EVENT_TYPE_ALIASES.get(event_type.upper())
    if alias:
        return alias

    raise ValueError(
        f"Invalid event_type '{event_type}'. "
        f"Valid values: {sorted(_VALID_EVENT_TYPES)}. "
        f"Hint: use EventType enum members (e.g. EventType.MESSAGE_IN) or "
        f"dot-notation strings (e.g. 'message.in')."
    )


class Elephantasm:
    """HTTP client for Elephantasm Long-Term Agentic Memory API.

    Example:
        >>> from elephantasm import Elephantasm
        >>> client = Elephantasm(api_key="sk_live_...", anima_id="...")
        >>> pack = client.inject()
        >>> print(pack.as_prompt())
    """

    def __init__(
        self,
        api_key: str | None = None,
        anima_id: str | None = None,
        endpoint: str | None = None,
        timeout: int | None = None,
    ):
        """Initialize the Elephantasm client.

        Args:
            api_key: API key for authentication. Falls back to ELEPHANTASM_API_KEY.
            anima_id: Default anima ID. Falls back to ELEPHANTASM_ANIMA_ID.
            endpoint: API endpoint URL. Falls back to ELEPHANTASM_ENDPOINT.
            timeout: Request timeout in seconds. Falls back to ELEPHANTASM_TIMEOUT.

        Raises:
            ValueError: If no API key is provided or found in environment.
        """
        self.api_key = api_key or settings.api_key
        self.anima_id = anima_id or settings.anima_id
        self.endpoint = (endpoint or settings.endpoint).rstrip("/")
        self.timeout = timeout or settings.timeout

        if not self.api_key:
            raise ValueError(
                "API key required. Provide api_key parameter or set ELEPHANTASM_API_KEY."
            )

        self._client = httpx.Client(
            base_url=f"{self.endpoint}/api",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=self.timeout,
        )

    def _handle_response(self, response: httpx.Response) -> dict[str, Any] | None:
        """Handle API response and map errors to exceptions.

        Args:
            response: HTTP response from API.

        Returns:
            Parsed JSON response data, or None if response body is null.

        Raises:
            AuthenticationError: On 401 responses.
            NotFoundError: On 404 responses.
            ValidationError: On 422 responses.
            RateLimitError: On 429 responses.
            ServerError: On 5xx responses.
            ElephantasmError: On other error responses.
        """
        if response.is_success:
            return response.json()

        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text

        status = response.status_code

        if status == 401:
            raise AuthenticationError(detail)
        elif status == 404:
            raise NotFoundError(detail)
        elif status == 422:
            raise ValidationError(str(detail))
        elif status == 429:
            raise RateLimitError(detail)
        elif status >= 500:
            raise ServerError(detail)
        else:
            raise ElephantasmError(detail, status_code=status)

    def create_anima(
        self,
        name: str,
        description: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> Anima:
        """Create a new anima (agent entity).

        Args:
            name: Human-readable name for the anima.
            description: Optional description.
            meta: Optional metadata dictionary.

        Returns:
            Created Anima object.
        """
        data = AnimaCreate(name=name, description=description, meta=meta)
        response = self._client.post("/animas", json=data.model_dump(exclude_none=True))
        result = self._handle_response(response)
        return Anima(**result)

    def inject(
        self,
        anima_id: str | UUID | None = None,
        query: str | None = None,
        preset: str | None = None,
    ) -> MemoryPack | None:
        """Retrieve the latest memory pack for context injection.

        Args:
            anima_id: Anima ID. Falls back to client's default anima_id.
            query: Optional query for semantic retrieval.
            preset: Optional preset name (conversational, self_determined).

        Returns:
            MemoryPack with context ready for LLM injection, or None if no packs exist.

        Raises:
            ValueError: If no anima_id provided and no default set.
        """
        aid = str(anima_id) if anima_id else self.anima_id
        if not aid:
            raise ValueError(
                "anima_id required. Provide parameter or set default in client."
            )

        params: dict[str, Any] = {}
        if query:
            params["query"] = query
        if preset:
            params["preset"] = preset

        response = self._client.get(f"/animas/{aid}/memory-packs/latest", params=params)
        result = self._handle_response(response)
        if result is None:
            return None
        return MemoryPack(**result)

    def extract(
        self,
        event_type: str | EventType,
        content: str,
        anima_id: str | UUID | None = None,
        session_id: str | None = None,
        role: str | None = None,
        author: str | None = None,
        occurred_at: datetime | None = None,
        meta: dict[str, Any] | None = None,
        importance_score: float | None = None,
    ) -> Event:
        """Capture an event (message, tool call, etc.) for memory synthesis.

        Args:
            event_type: Type of event (e.g., EventType.MESSAGE_IN).
            content: Event content (message text, tool output, etc.).
            anima_id: Anima ID. Falls back to client's default anima_id.
            session_id: Optional session identifier for grouping events.
            role: Message role (user, assistant, system, tool).
            author: Author identifier (username, model name, tool name).
            occurred_at: When the event occurred (defaults to now).
            meta: Optional metadata dictionary.
            importance_score: Optional importance score (0.0-1.0).

        Returns:
            Created Event object.

        Raises:
            ValueError: If no anima_id provided and no default set.
        """
        aid = anima_id if anima_id else self.anima_id
        if not aid:
            raise ValueError(
                "anima_id required. Provide parameter or set default in client."
            )

        # Normalize and validate event_type before API call
        event_type_str = _resolve_event_type(event_type)

        data = EventCreate(
            anima_id=UUID(str(aid)),
            event_type=event_type_str,
            content=content,
            session_id=session_id,
            role=role,
            author=author,
            occurred_at=occurred_at,
            meta=meta or {},
            importance_score=importance_score,
        )

        payload = data.model_dump(mode="json", exclude_none=True)
        response = self._client.post("/events", json=payload)
        result = self._handle_response(response)
        return Event(**result)

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self._client.close()

    def __enter__(self) -> "Elephantasm":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit - closes the client."""
        self.close()
