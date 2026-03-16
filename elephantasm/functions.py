"""Module-level convenience functions using a lazy default client."""

from datetime import datetime
from typing import Any
from uuid import UUID

from .client import Elephantasm
from .types import Anima, Event, EventType, MemoryPack

# Lazy-initialized default client
_default_client: Elephantasm | None = None


def _get_client() -> Elephantasm:
    """Get or create the default client instance.

    Returns:
        Default Elephantasm client configured from environment variables.

    Raises:
        ValueError: If ELEPHANTASM_API_KEY not set.
    """
    global _default_client
    if _default_client is None:
        _default_client = Elephantasm()
    return _default_client


def create_anima(
    name: str,
    description: str | None = None,
    meta: dict[str, Any] | None = None,
) -> Anima:
    """Create a new anima (agent entity).

    Uses the default client configured from environment variables.

    Args:
        name: Human-readable name for the anima.
        description: Optional description.
        meta: Optional metadata dictionary.

    Returns:
        Created Anima object.

    Example:
        >>> from elephantasm import create_anima
        >>> anima = create_anima("my-agent", description="Test agent")
    """
    return _get_client().create_anima(name, description, meta)


def inject(
    anima_id: str | UUID | None = None,
    query: str | None = None,
    preset: str | None = None,
) -> MemoryPack | None:
    """Retrieve the latest memory pack for context injection.

    Uses the default client configured from environment variables.

    Args:
        anima_id: Anima ID. Falls back to ELEPHANTASM_ANIMA_ID.
        query: Optional query for semantic retrieval.
        preset: Optional preset name (conversational, self_determined).

    Returns:
        MemoryPack with context ready for LLM injection, or None if no packs exist.

    Example:
        >>> from elephantasm import inject
        >>> pack = inject()
        >>> if pack:
        ...     system_prompt = f"You are a helpful assistant.\\n\\n{pack.as_prompt()}"
    """
    return _get_client().inject(anima_id, query, preset)


def extract(
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

    Uses the default client configured from environment variables.

    Args:
        event_type: Type of event (e.g., EventType.MESSAGE_IN).
        content: Event content (message text, tool output, etc.).
        anima_id: Anima ID. Falls back to ELEPHANTASM_ANIMA_ID.
        session_id: Optional session identifier for grouping events.
        role: Message role (user, assistant, system, tool).
        author: Author identifier (username, model name, tool name).
        occurred_at: When the event occurred (defaults to now).
        meta: Optional metadata dictionary.
        importance_score: Optional importance score (0.0-1.0).

    Returns:
        Created Event object.

    Example:
        >>> from elephantasm import extract, EventType
        >>> extract(EventType.MESSAGE_IN, "Hello!", role="user")
        >>> extract(EventType.MESSAGE_OUT, "Hi there!", role="assistant")
    """
    return _get_client().extract(
        event_type=event_type,
        content=content,
        anima_id=anima_id,
        session_id=session_id,
        role=role,
        author=author,
        occurred_at=occurred_at,
        meta=meta,
        importance_score=importance_score,
    )
