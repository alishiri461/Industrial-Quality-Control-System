from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

class CameraConfig(BaseModel):
    """Private camera configuration; never return this model from public API routes."""
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=160)
    source_type: str = "rtsp"
    source_url: SecretStr
    enabled: bool = True
    reconnect_initial_seconds: float = Field(default=1.0, ge=0.25, le=30.0)
    reconnect_max_seconds: float = Field(default=30.0, ge=1.0, le=300.0)
    open_timeout_ms: int = Field(default=5000, ge=500, le=60000)
    read_timeout_ms: int = Field(default=5000, ge=500, le=60000)

    @field_validator("source_type")
    @classmethod
    def supported_source(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"rtsp"}:
            raise ValueError("Only RTSP sources are supported by the current ingestion adapter")
        return normalized

    @field_validator("source_url")
    @classmethod
    def valid_rtsp_url(cls, value: SecretStr) -> SecretStr:
        url = value.get_secret_value().strip()
        try:
            parsed = urlsplit(url)
            valid = parsed.scheme.lower() in {"rtsp", "rtsps"} and bool(parsed.hostname)
            # Accessing .port also validates malformed port values.
            _ = parsed.port
        except ValueError as exc:
            raise ValueError("source_url must be a valid RTSP URL with a host") from exc
        if not valid:
            raise ValueError("source_url must be a valid RTSP URL with a host")
        return SecretStr(url)
