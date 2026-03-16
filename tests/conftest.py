"""Shared test fixtures and mock setup."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
import respx

from elephantasm import Elephantasm


@pytest.fixture
def api_key() -> str:
    """Test API key."""
    return "sk_test_abc123def456"


@pytest.fixture
def anima_id() -> str:
    """Test anima ID."""
    return str(uuid4())


@pytest.fixture
def endpoint() -> str:
    """Test API endpoint."""
    return "https://test.api.elephantasm.com"


@pytest.fixture
def client(api_key: str, anima_id: str, endpoint: str) -> Elephantasm:
    """Create test client instance."""
    return Elephantasm(
        api_key=api_key,
        anima_id=anima_id,
        endpoint=endpoint,
    )


@pytest.fixture
def mock_anima(anima_id: str) -> dict:
    """Mock anima response."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "id": anima_id,
        "name": "Test Anima",
        "description": "A test anima",
        "meta": {"test": True},
        "user_id": str(uuid4()),
        "created_at": now,
        "updated_at": now,
    }


@pytest.fixture
def mock_event(anima_id: str) -> dict:
    """Mock event response."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "id": str(uuid4()),
        "anima_id": anima_id,
        "event_type": "message.in",
        "role": "user",
        "author": "test-user",
        "summary": None,
        "content": "Hello, world!",
        "occurred_at": now,
        "session_id": "session-123",
        "meta": {},
        "source_uri": None,
        "dedupe_key": None,
        "importance_score": None,
        "created_at": now,
        "updated_at": now,
    }


@pytest.fixture
def mock_memory_pack(anima_id: str) -> dict:
    """Mock memory pack response."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "id": str(uuid4()),
        "anima_id": anima_id,
        "query": None,
        "preset_name": "conversational",
        "session_memory_count": 2,
        "knowledge_count": 3,
        "long_term_memory_count": 1,
        "has_identity": True,
        "token_count": 1500,
        "max_tokens": 4000,
        "content": {
            "context": "You have memories of past conversations with this user.",
            "identity": {
                "personality_type": "INTJ",
                "communication_style": "direct",
                "self_reflection": {"core_values": ["accuracy", "efficiency"]},
                "prose": "You are a thoughtful assistant.",
            },
            "session_memories": [
                {
                    "id": str(uuid4()),
                    "summary": "User asked about weather",
                    "score": 0.9,
                    "reason": "Recent and relevant",
                    "breakdown": {"recency": 0.95, "importance": 0.85},
                }
            ],
            "knowledge": [
                {
                    "id": str(uuid4()),
                    "content": "User prefers concise responses",
                    "type": "preference",
                    "score": 0.85,
                    "similarity": 0.78,
                }
            ],
            "long_term_memories": [
                {
                    "id": str(uuid4()),
                    "summary": "User works in tech",
                    "score": 0.75,
                    "reason": "Background context",
                    "breakdown": {"importance": 0.8, "confidence": 0.7},
                    "similarity": 0.65,
                }
            ],
            "temporal_context": {
                "last_event_at": now,
                "hours_ago": 2.5,
                "memory_summary": "discussing project plans",
                "formatted": "Your last conversation was 2.5 hours ago about project plans.",
            },
        },
        "compiled_at": now,
        "created_at": now,
    }


@pytest.fixture
def mock_api(endpoint: str):
    """Context manager for mocking API calls."""
    with respx.mock(base_url=f"{endpoint}/api") as respx_mock:
        yield respx_mock
