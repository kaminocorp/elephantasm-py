"""Pydantic models matching backend API schemas."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class EventType(str, Enum):
    """Event types for message capture."""

    MESSAGE_IN = "message.in"
    MESSAGE_OUT = "message.out"
    TOOL_CALL = "tool.call"
    TOOL_RESULT = "tool.result"
    SYSTEM = "system"


class MemoryState(str, Enum):
    """Lifecycle states for memory recall and curation."""

    ACTIVE = "active"
    DECAYING = "decaying"
    ARCHIVED = "archived"


class Anima(BaseModel):
    """Agent entity that owns memories and events."""

    id: UUID
    name: str
    description: str | None = None
    meta: dict[str, Any] | None = None
    user_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class AnimaCreate(BaseModel):
    """Data required to create an Anima."""

    name: str = Field(max_length=255)
    description: str | None = None
    meta: dict[str, Any] | None = None


class Event(BaseModel):
    """Atomic unit of experience (message, tool call, etc.)."""

    id: UUID
    anima_id: UUID
    event_type: str
    role: str | None = None
    author: str | None = None
    summary: str | None = None
    content: str
    occurred_at: datetime | None = None
    session_id: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    source_uri: str | None = None
    dedupe_key: str | None = None
    importance_score: float | None = None
    created_at: datetime
    updated_at: datetime


class EventCreate(BaseModel):
    """Data required to create an Event."""

    anima_id: UUID
    event_type: str
    content: str
    role: str | None = None
    author: str | None = None
    summary: str | None = None
    occurred_at: datetime | None = None
    session_id: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    source_uri: str | None = None
    dedupe_key: str | None = None
    importance_score: float | None = Field(default=None, ge=0.0, le=1.0)

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        valid = {"message.in", "message.out", "tool.call", "tool.result", "system"}
        if v not in valid:
            raise ValueError(
                f"Invalid event_type '{v}'. "
                f"Valid values: {sorted(valid)}."
            )
        return v


class Memory(BaseModel):
    """Subjective interpretation of events."""

    id: UUID
    anima_id: UUID
    content: str | None = None
    summary: str | None = None
    importance: float | None = None
    confidence: float | None = None
    state: MemoryState | None = None
    recency_score: float | None = None
    decay_score: float | None = None
    time_start: datetime | None = None
    time_end: datetime | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class ScoredMemory(BaseModel):
    """Memory with scoring breakdown from pack compilation."""

    id: UUID
    summary: str | None = None
    score: float
    reason: str | None = None
    breakdown: dict[str, float] = Field(default_factory=dict)
    similarity: float | None = None


class ScoredKnowledge(BaseModel):
    """Knowledge item with similarity score from pack compilation."""

    id: UUID
    content: str
    type: str
    score: float
    similarity: float | None = None


class TemporalContext(BaseModel):
    """Temporal awareness context for bridging session gaps."""

    last_event_at: datetime
    hours_ago: float
    memory_summary: str | None = None
    formatted: str


class IdentityContext(BaseModel):
    """Identity layer context from pack compilation."""

    personality_type: str | None = None
    communication_style: str | None = None
    self_reflection: dict[str, Any] | None = None
    prose: str | None = None


class MemoryPack(BaseModel):
    """Compiled memory pack for LLM context injection."""

    id: UUID
    anima_id: UUID
    query: str | None = None
    preset_name: str | None = None
    session_memory_count: int = 0
    knowledge_count: int = 0
    long_term_memory_count: int = 0
    has_identity: bool = False
    token_count: int = 0
    max_tokens: int = 4000
    content: dict[str, Any] = Field(default_factory=dict)
    compiled_at: datetime
    created_at: datetime

    def as_prompt(self) -> str:
        """Return the formatted context string for LLM injection.

        Returns:
            Pre-formatted prompt string from the pack's context field.
        """
        if not self.content:
            return ""
        return self.content.get("context", "")

    @property
    def identity(self) -> IdentityContext | None:
        """Extract identity context if present."""
        if not self.content:
            return None
        identity_data = self.content.get("identity")
        if identity_data:
            return IdentityContext(**identity_data)
        return None

    @property
    def session_memories(self) -> list[ScoredMemory]:
        """Extract session memories with scores."""
        if not self.content:
            return []
        items = self.content.get("session_memories", [])
        return [ScoredMemory(**item) for item in items]

    @property
    def knowledge(self) -> list[ScoredKnowledge]:
        """Extract knowledge items with scores."""
        if not self.content:
            return []
        items = self.content.get("knowledge", [])
        return [ScoredKnowledge(**item) for item in items]

    @property
    def long_term_memories(self) -> list[ScoredMemory]:
        """Extract long-term memories with scores."""
        if not self.content:
            return []
        items = self.content.get("long_term_memories", [])
        return [ScoredMemory(**item) for item in items]

    @property
    def temporal_context(self) -> TemporalContext | None:
        """Extract temporal awareness context if present."""
        if not self.content:
            return None
        temporal_data = self.content.get("temporal_context")
        if temporal_data:
            return TemporalContext(**temporal_data)
        return None
