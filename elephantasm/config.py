"""Configuration management via environment variables."""

from pydantic_settings import BaseSettings


class ElephantasmSettings(BaseSettings):
    """SDK configuration loaded from environment variables.

    Environment variables:
        ELEPHANTASM_API_KEY: API key for authentication
        ELEPHANTASM_ANIMA_ID: Default anima ID for operations
        ELEPHANTASM_ENDPOINT: API endpoint (default: https://api.elephantasm.com)
        ELEPHANTASM_TIMEOUT: Request timeout in seconds (default: 30)
    """

    api_key: str | None = None
    anima_id: str | None = None
    endpoint: str = "https://api.elephantasm.com"
    timeout: int = 30

    model_config = {"env_prefix": "ELEPHANTASM_"}


settings = ElephantasmSettings()
