"""Elephantasm - Long-Term Agentic Memory SDK.

A Python SDK for the Elephantasm LTAM framework, enabling AI agents
to have persistent, evolving memory across sessions.

Quick Start:
    >>> from elephantasm import inject, extract, EventType
    >>>
    >>> # Capture events
    >>> extract(EventType.MESSAGE_IN, "Hello!", role="user")
    >>> extract(EventType.MESSAGE_OUT, "Hi there!", role="assistant")
    >>>
    >>> # Retrieve memory pack for context injection
    >>> pack = inject()
    >>> system_prompt = f"You are helpful.\\n\\n{pack.as_prompt()}"

With explicit client:
    >>> from elephantasm import Elephantasm
    >>> with Elephantasm(api_key="sk_live_...", anima_id="...") as client:
    ...     pack = client.inject()
    ...     client.extract(EventType.MESSAGE_IN, "Hello!")
"""

__version__ = "0.2.0"

from .client import Elephantasm
from .exceptions import (
    AuthenticationError,
    ElephantasmError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .functions import create_anima, extract, inject
from .types import (
    Anima,
    AnimaCreate,
    Event,
    EventCreate,
    EventType,
    IdentityContext,
    Memory,
    MemoryPack,
    MemoryState,
    ScoredKnowledge,
    ScoredMemory,
    TemporalContext,
)

__all__ = [
    # Version
    "__version__",
    # Client
    "Elephantasm",
    # Functions
    "create_anima",
    "inject",
    "extract",
    # Types
    "Anima",
    "AnimaCreate",
    "Event",
    "EventCreate",
    "EventType",
    "Memory",
    "MemoryPack",
    "MemoryState",
    "ScoredMemory",
    "ScoredKnowledge",
    "IdentityContext",
    "TemporalContext",
    # Exceptions
    "ElephantasmError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
    "ServerError",
]
