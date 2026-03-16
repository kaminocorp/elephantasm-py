"""Tests for module-level convenience functions."""

import os
from unittest.mock import patch

import pytest
import respx
from httpx import Response

from elephantasm import EventType


class TestModuleFunctions:
    """Tests for inject(), extract(), create_anima() module functions."""

    @pytest.fixture(autouse=True)
    def reset_modules(self):
        """Reset the config and functions modules before each test."""
        # Clear cached modules to force reload with new env vars
        import sys
        modules_to_clear = [
            "elephantasm",
            "elephantasm.config",
            "elephantasm.client",
            "elephantasm.functions",
            "elephantasm.types",
            "elephantasm.exceptions",
        ]
        for mod in modules_to_clear:
            if mod in sys.modules:
                del sys.modules[mod]
        yield
        # Cleanup after test
        for mod in modules_to_clear:
            if mod in sys.modules:
                del sys.modules[mod]

    def test_inject_uses_default_client(
        self, api_key: str, anima_id: str, endpoint: str, mock_memory_pack: dict
    ):
        """inject() should use lazy default client from env vars."""
        with patch.dict(
            os.environ,
            {
                "ELEPHANTASM_API_KEY": api_key,
                "ELEPHANTASM_ANIMA_ID": anima_id,
                "ELEPHANTASM_ENDPOINT": endpoint,
            },
            clear=False,
        ):
            # Import after patching env
            from elephantasm import inject

            with respx.mock(base_url=f"{endpoint}/api") as mock_api:
                mock_api.get(f"/animas/{anima_id}/memory-packs/latest").mock(
                    return_value=Response(200, json=mock_memory_pack)
                )

                pack = inject()

                assert pack is not None
                assert pack.session_memory_count == 2

    def test_extract_uses_default_client(
        self, api_key: str, anima_id: str, endpoint: str, mock_event: dict
    ):
        """extract() should use lazy default client from env vars."""
        with patch.dict(
            os.environ,
            {
                "ELEPHANTASM_API_KEY": api_key,
                "ELEPHANTASM_ANIMA_ID": anima_id,
                "ELEPHANTASM_ENDPOINT": endpoint,
            },
            clear=False,
        ):
            # Import after patching env
            from elephantasm import extract

            with respx.mock(base_url=f"{endpoint}/api") as mock_api:
                mock_api.post("/events").mock(
                    return_value=Response(201, json=mock_event)
                )

                event = extract(EventType.MESSAGE_IN, "Hello!")

                assert event is not None
                assert event.event_type == "message.in"

    def test_create_anima_uses_default_client(
        self, api_key: str, endpoint: str, mock_anima: dict
    ):
        """create_anima() should use lazy default client from env vars."""
        with patch.dict(
            os.environ,
            {
                "ELEPHANTASM_API_KEY": api_key,
                "ELEPHANTASM_ENDPOINT": endpoint,
            },
            clear=False,
        ):
            # Import after patching env
            from elephantasm import create_anima

            with respx.mock(base_url=f"{endpoint}/api") as mock_api:
                mock_api.post("/animas").mock(
                    return_value=Response(201, json=mock_anima)
                )

                anima = create_anima(name="Test Anima")

                assert anima is not None
                assert anima.name == "Test Anima"

    def test_default_client_reused(
        self, api_key: str, anima_id: str, endpoint: str, mock_memory_pack: dict
    ):
        """Default client should be reused across calls."""
        with patch.dict(
            os.environ,
            {
                "ELEPHANTASM_API_KEY": api_key,
                "ELEPHANTASM_ANIMA_ID": anima_id,
                "ELEPHANTASM_ENDPOINT": endpoint,
            },
            clear=False,
        ):
            # Import after patching env
            from elephantasm import functions as fn
            from elephantasm import inject

            with respx.mock(base_url=f"{endpoint}/api") as mock_api:
                mock_api.get(f"/animas/{anima_id}/memory-packs/latest").mock(
                    return_value=Response(200, json=mock_memory_pack)
                )

                # First call creates client
                inject()
                client1 = fn._default_client

                # Second call reuses client
                inject()
                client2 = fn._default_client

                assert client1 is client2

    def test_inject_with_explicit_anima_id(
        self, api_key: str, endpoint: str, mock_memory_pack: dict
    ):
        """inject() should accept explicit anima_id override."""
        from uuid import uuid4
        explicit_anima_id = str(uuid4())
        mock_memory_pack["anima_id"] = explicit_anima_id

        with patch.dict(
            os.environ,
            {
                "ELEPHANTASM_API_KEY": api_key,
                "ELEPHANTASM_ANIMA_ID": "default-anima-id",
                "ELEPHANTASM_ENDPOINT": endpoint,
            },
            clear=False,
        ):
            # Import after patching env
            from elephantasm import inject

            with respx.mock(base_url=f"{endpoint}/api") as mock_api:
                mock_api.get(f"/animas/{explicit_anima_id}/memory-packs/latest").mock(
                    return_value=Response(200, json=mock_memory_pack)
                )

                pack = inject(anima_id=explicit_anima_id)

                assert str(pack.anima_id) == explicit_anima_id
