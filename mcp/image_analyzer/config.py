"""image_analyzer settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class ImageAnalyzerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="IMAGE_ANALYZER_", env_file=".env", extra="ignore")

    host: str = "127.0.0.1"
    port: int = 8103
    transport: str = "stdio"  # "stdio" | "sse" | "streamable-http"

    # Providers: "mock" ships by default; set real keys to go live.
    vision_provider: str = "mock"
    vision_api_key: str | None = None
    ocr_provider: str = "mock"
    request_timeout_s: float = 30.0


settings = ImageAnalyzerSettings()
