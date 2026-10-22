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
        if not url.lower().startswith(("rtsp://", "rtsps://")):
            raise ValueError("source_url must use rtsp:// or rtsps://")
        if not url.split("://", 1)[1]:
            raise ValueError("source_url must include a host")
        return SecretStr(url)
