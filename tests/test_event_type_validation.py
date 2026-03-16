"""Tests for event_type normalization and validation."""

from uuid import uuid4

import pytest
from pydantic import ValidationError as PydanticValidationError

from elephantasm.client import _resolve_event_type
from elephantasm.types import EventCreate, EventType


class TestResolveEventType:
    """Tests for the _resolve_event_type helper."""

    # --- EventType enum passthrough ---

    def test_enum_message_in(self):
        assert _resolve_event_type(EventType.MESSAGE_IN) == "message.in"

    def test_enum_message_out(self):
        assert _resolve_event_type(EventType.MESSAGE_OUT) == "message.out"

    def test_enum_tool_call(self):
        assert _resolve_event_type(EventType.TOOL_CALL) == "tool.call"

    def test_enum_tool_result(self):
        assert _resolve_event_type(EventType.TOOL_RESULT) == "tool.result"

    def test_enum_system(self):
        assert _resolve_event_type(EventType.SYSTEM) == "system"

    # --- Dot-notation strings passthrough ---

    def test_string_message_in(self):
        assert _resolve_event_type("message.in") == "message.in"

    def test_string_message_out(self):
        assert _resolve_event_type("message.out") == "message.out"

    def test_string_tool_call(self):
        assert _resolve_event_type("tool.call") == "tool.call"

    def test_string_tool_result(self):
        assert _resolve_event_type("tool.result") == "tool.result"

    def test_string_system(self):
        assert _resolve_event_type("system") == "system"

    # --- Uppercase enum name normalization ---

    def test_uppercase_message_in(self):
        assert _resolve_event_type("MESSAGE_IN") == "message.in"

    def test_uppercase_message_out(self):
        assert _resolve_event_type("MESSAGE_OUT") == "message.out"

    def test_uppercase_tool_call(self):
        assert _resolve_event_type("TOOL_CALL") == "tool.call"

    def test_uppercase_tool_result(self):
        assert _resolve_event_type("TOOL_RESULT") == "tool.result"

    def test_uppercase_system(self):
        assert _resolve_event_type("SYSTEM") == "system"

    # --- Case-insensitive normalization ---

    def test_mixed_case_tool_call(self):
        assert _resolve_event_type("Tool_Call") == "tool.call"

    def test_lowercase_underscore(self):
        assert _resolve_event_type("message_in") == "message.in"

    # --- Invalid strings ---

    def test_invalid_string_raises(self):
        with pytest.raises(ValueError, match="Invalid event_type 'invalid'"):
            _resolve_event_type("invalid")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="Invalid event_type ''"):
            _resolve_event_type("")

    def test_partial_match_raises(self):
        with pytest.raises(ValueError, match="Invalid event_type"):
            _resolve_event_type("TOOL_CALL_EXTRA")

    def test_error_message_includes_valid_values(self):
        with pytest.raises(ValueError, match="message.in"):
            _resolve_event_type("bad")

    def test_error_message_includes_hint(self):
        with pytest.raises(ValueError, match="Hint"):
            _resolve_event_type("nope")


class TestEventCreateValidator:
    """Tests for the EventCreate field_validator safety net."""

    def _make(self, event_type: str) -> EventCreate:
        return EventCreate(
            anima_id=uuid4(),
            event_type=event_type,
            content="test",
        )

    def test_valid_dot_notation(self):
        ec = self._make("message.in")
        assert ec.event_type == "message.in"

    def test_valid_all_types(self):
        for val in ("message.in", "message.out", "tool.call", "tool.result", "system"):
            ec = self._make(val)
            assert ec.event_type == val

    def test_invalid_uppercase_rejected(self):
        with pytest.raises(PydanticValidationError, match="Invalid event_type"):
            self._make("TOOL_CALL")

    def test_invalid_random_string_rejected(self):
        with pytest.raises(PydanticValidationError, match="Invalid event_type"):
            self._make("foobar")
