"""Tests for the Elephantasm client class."""

import pytest
from httpx import Response

from elephantasm import Elephantasm, EventType
from elephantasm.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


class TestClientInit:
    """Tests for client initialization."""

    def test_init_requires_api_key(self):
        """Client should raise ValueError if no API key provided."""
        with pytest.raises(ValueError, match="API key required"):
            Elephantasm(api_key=None)

    def test_init_with_api_key(self, api_key: str):
        """Client should initialize with valid API key."""
        client = Elephantasm(api_key=api_key)
        assert client.api_key == api_key
        assert client.endpoint == "https://api.elephantasm.com"

    def test_init_with_custom_endpoint(self, api_key: str, endpoint: str):
        """Client should accept custom endpoint."""
        client = Elephantasm(api_key=api_key, endpoint=endpoint)
        assert client.endpoint == endpoint

    def test_init_with_anima_id(self, api_key: str, anima_id: str):
        """Client should accept default anima_id."""
        client = Elephantasm(api_key=api_key, anima_id=anima_id)
        assert client.anima_id == anima_id

    def test_context_manager(self, api_key: str):
        """Client should work as context manager."""
        with Elephantasm(api_key=api_key) as client:
            assert client.api_key == api_key


class TestInject:
    """Tests for the inject method."""

    def test_inject_success(
        self, client: Elephantasm, anima_id: str, mock_api, mock_memory_pack: dict
    ):
        """inject() should return MemoryPack on success."""
        mock_api.get(f"/animas/{anima_id}/memory-packs/latest").mock(
            return_value=Response(200, json=mock_memory_pack)
        )

        pack = client.inject()

        assert pack.id is not None
        assert pack.anima_id is not None
        assert pack.session_memory_count == 2
        assert pack.has_identity is True

    def test_inject_as_prompt(
        self, client: Elephantasm, anima_id: str, mock_api, mock_memory_pack: dict
    ):
        """MemoryPack.as_prompt() should return context string."""
        mock_api.get(f"/animas/{anima_id}/memory-packs/latest").mock(
            return_value=Response(200, json=mock_memory_pack)
        )

        pack = client.inject()
        prompt = pack.as_prompt()

        assert isinstance(prompt, str)
        assert "memories" in prompt.lower()

    def test_inject_with_query(
        self, client: Elephantasm, anima_id: str, mock_api, mock_memory_pack: dict
    ):
        """inject() should pass query parameter."""
        route = mock_api.get(f"/animas/{anima_id}/memory-packs/latest").mock(
            return_value=Response(200, json=mock_memory_pack)
        )

        client.inject(query="user preferences")

        assert "query=user+preferences" in str(route.calls[0].request.url)

    def test_inject_requires_anima_id(self, api_key: str, endpoint: str):
        """inject() should raise ValueError if no anima_id."""
        client = Elephantasm(api_key=api_key, endpoint=endpoint)

        with pytest.raises(ValueError, match="anima_id required"):
            client.inject()

    def test_inject_returns_none_when_no_packs(
        self, client: Elephantasm, anima_id: str, mock_api
    ):
        """inject() should return None when API returns null."""
        mock_api.get(f"/animas/{anima_id}/memory-packs/latest").mock(
            return_value=Response(
                200, content=b"null", headers={"content-type": "application/json"}
            )
        )

        pack = client.inject()
        assert pack is None

    def test_inject_not_found(self, client: Elephantasm, anima_id: str, mock_api):
        """inject() should raise NotFoundError on 404."""
        mock_api.get(f"/animas/{anima_id}/memory-packs/latest").mock(
            return_value=Response(404, json={"detail": "Anima not found"})
        )

        with pytest.raises(NotFoundError, match="Anima not found"):
            client.inject()

    def test_inject_auth_error(self, client: Elephantasm, anima_id: str, mock_api):
        """inject() should raise AuthenticationError on 401."""
        mock_api.get(f"/animas/{anima_id}/memory-packs/latest").mock(
            return_value=Response(401, json={"detail": "Invalid API key"})
        )

        with pytest.raises(AuthenticationError, match="Invalid API key"):
            client.inject()

    def test_inject_identity_accessor(
        self, client: Elephantasm, anima_id: str, mock_api, mock_memory_pack: dict
    ):
        """MemoryPack.identity should return IdentityContext."""
        mock_api.get(f"/animas/{anima_id}/memory-packs/latest").mock(
            return_value=Response(200, json=mock_memory_pack)
        )

        pack = client.inject()
        identity = pack.identity

        assert identity is not None
        assert identity.personality_type == "INTJ"
        assert identity.prose is not None

    def test_inject_session_memories_accessor(
        self, client: Elephantasm, anima_id: str, mock_api, mock_memory_pack: dict
    ):
        """MemoryPack.session_memories should return list of ScoredMemory."""
        mock_api.get(f"/animas/{anima_id}/memory-packs/latest").mock(
            return_value=Response(200, json=mock_memory_pack)
        )

        pack = client.inject()
        memories = pack.session_memories

        assert len(memories) == 1
        assert memories[0].summary == "User asked about weather"
        assert memories[0].score == 0.9


class TestExtract:
    """Tests for the extract method."""

    def test_extract_success(
        self, client: Elephantasm, anima_id: str, mock_api, mock_event: dict
    ):
        """extract() should return Event on success."""
        mock_api.post("/events").mock(return_value=Response(201, json=mock_event))

        event = client.extract(EventType.MESSAGE_IN, "Hello!")

        assert event.id is not None
        assert event.event_type == "message.in"
        assert event.content == "Hello, world!"

    def test_extract_with_all_params(
        self, client: Elephantasm, anima_id: str, mock_api, mock_event: dict
    ):
        """extract() should accept all optional parameters."""
        mock_api.post("/events").mock(return_value=Response(201, json=mock_event))

        event = client.extract(
            event_type=EventType.MESSAGE_IN,
            content="Hello!",
            session_id="session-123",
            role="user",
            author="test-user",
            meta={"key": "value"},
            importance_score=0.8,
        )

        assert event is not None

    def test_extract_requires_anima_id(self, api_key: str, endpoint: str):
        """extract() should raise ValueError if no anima_id."""
        client = Elephantasm(api_key=api_key, endpoint=endpoint)

        with pytest.raises(ValueError, match="anima_id required"):
            client.extract(EventType.MESSAGE_IN, "Hello!")

    def test_extract_auth_error(self, client: Elephantasm, mock_api):
        """extract() should raise AuthenticationError on 401."""
        mock_api.post("/events").mock(
            return_value=Response(401, json={"detail": "Invalid API key"})
        )

        with pytest.raises(AuthenticationError):
            client.extract(EventType.MESSAGE_IN, "Hello!")

    def test_extract_rate_limit(self, client: Elephantasm, mock_api):
        """extract() should raise RateLimitError on 429."""
        mock_api.post("/events").mock(
            return_value=Response(429, json={"detail": "Rate limit exceeded"})
        )

        with pytest.raises(RateLimitError):
            client.extract(EventType.MESSAGE_IN, "Hello!")

    def test_extract_invalid_type_raises_locally(self, client: Elephantasm):
        """extract() should raise ValueError for invalid event_type before HTTP call."""
        with pytest.raises(ValueError, match="Invalid event_type"):
            client.extract("invalid_type", "Hello!")

    def test_extract_server_validation_error(self, client: Elephantasm, mock_api):
        """extract() should raise ValidationError on 422 from server."""
        mock_api.post("/events").mock(
            return_value=Response(422, json={"detail": "Invalid event_type"})
        )

        with pytest.raises(ValidationError):
            client.extract(EventType.MESSAGE_IN, "Hello!")

    def test_extract_server_error(self, client: Elephantasm, mock_api):
        """extract() should raise ServerError on 5xx."""
        mock_api.post("/events").mock(
            return_value=Response(500, json={"detail": "Internal error"})
        )

        with pytest.raises(ServerError):
            client.extract(EventType.MESSAGE_IN, "Hello!")


class TestCreateAnima:
    """Tests for the create_anima method."""

    def test_create_anima_success(
        self, client: Elephantasm, mock_api, mock_anima: dict
    ):
        """create_anima() should return Anima on success."""
        mock_api.post("/animas").mock(return_value=Response(201, json=mock_anima))

        anima = client.create_anima(name="Test Anima", description="A test anima")

        assert anima.id is not None
        assert anima.name == "Test Anima"
        assert anima.description == "A test anima"

    def test_create_anima_with_meta(
        self, client: Elephantasm, mock_api, mock_anima: dict
    ):
        """create_anima() should accept meta parameter."""
        mock_api.post("/animas").mock(return_value=Response(201, json=mock_anima))

        anima = client.create_anima(
            name="Test Anima",
            meta={"environment": "production"},
        )

        assert anima is not None

    def test_create_anima_auth_error(self, client: Elephantasm, mock_api):
        """create_anima() should raise AuthenticationError on 401."""
        mock_api.post("/animas").mock(
            return_value=Response(401, json={"detail": "Invalid API key"})
        )

        with pytest.raises(AuthenticationError):
            client.create_anima(name="Test")
