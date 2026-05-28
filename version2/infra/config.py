import os
import re
import tomllib
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, field_validator

# ---------------------------------------------------------------------------
# Environment detection
# ---------------------------------------------------------------------------

AppEnv = Literal["dev", "prod"]

def get_app_env() -> AppEnv:
    """Read APP_ENV from the environment. Defaults to 'dev' if not set."""
    raw = os.getenv("APP_ENV", "dev").strip().lower()
    if raw not in ("dev", "prod"):
        raise ValueError(f"APP_ENV must be 'dev' or 'prod', got '{raw}'")
    return raw  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Pydantic Config Models
# ---------------------------------------------------------------------------

class SupabaseConfig(BaseModel):
    url: str | None
    key: str | None


class EmbeddingsConfig(BaseModel):
    provider: str
    model_name: str
    batch_size: int = 128
    normalize: bool = True


class ResumeExtractionConfig(BaseModel):
    provider: str
    model: str
    endpoint: str


class AppEnvConfig(BaseModel):
    env: AppEnv = "dev"
    debug: bool = False


class ServerConfig(BaseModel):
    port: int = 8300
    log_level: str = "error"


_HEX_COLOR = re.compile(r'^#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3})?$')


class UIConfig(BaseModel):
    app_name: str = "CareerPivots"
    logo_size_px: int = 56
    header_font_size_rem: float = 2.0
    body_font_size_rem: float = 1.0
    card_title_font_size_rem: float = 1.1
    insight_value_font_size_rem: float = 1.05
    sidebar_font_size_rem: float = 0.95
    background_color: str = "#f4f6f9"
    card_background_color: str = "#ffffff"
    accent_color: str = "#14b8a6"
    header_text_color: str = "#111111"
    body_text_color: str = "#333333"
    muted_text_color: str = "#666666"

    @field_validator(
        "background_color", "card_background_color", "accent_color",
        "header_text_color", "body_text_color", "muted_text_color",
        mode="before",
    )
    @classmethod
    def validate_hex_color(cls, v: str) -> str:
        if not _HEX_COLOR.match(v):
            raise ValueError(
                f"Invalid color value '{v}'. Must be a hex color like #fff or #1a2b3c."
            )
        return v

    @field_validator(
        "header_font_size_rem", "body_font_size_rem", "card_title_font_size_rem",
        "insight_value_font_size_rem", "sidebar_font_size_rem",
        mode="before",
    )
    @classmethod
    def validate_font_size(cls, v: float) -> float:
        if not (0.5 <= float(v) <= 5.0):
            raise ValueError(f"Font size {v}rem is out of range (0.5–5.0).")
        return v

    @field_validator("logo_size_px", mode="before")
    @classmethod
    def validate_logo_size(cls, v: int) -> int:
        if not (16 <= int(v) <= 256):
            raise ValueError(f"logo_size_px {v} is out of range (16–256).")
        return v


class LimitsConfig(BaseModel):
    max_resume_chars: int = 50000
    max_upload_mb: int = 5

    @field_validator("max_resume_chars", mode="before")
    @classmethod
    def validate_max_chars(cls, v: int) -> int:
        if not (1000 <= int(v) <= 500000):
            raise ValueError(f"max_resume_chars {v} must be between 1000 and 500000.")
        return v

    @field_validator("max_upload_mb", mode="before")
    @classmethod
    def validate_max_mb(cls, v: int) -> int:
        if not (1 <= int(v) <= 50):
            raise ValueError(f"max_upload_mb {v} must be between 1 and 50.")
        return v


class PrepConfig(BaseModel):
    log_level: str = "error"
    batch_size: int = 16
    skip_if_exists: bool = True
    source_table: str = "jobhop_raw"


class AppConfig(BaseModel):
    app_env: AppEnvConfig = AppEnvConfig()
    server: ServerConfig = ServerConfig()
    supabase: SupabaseConfig
    embeddings: EmbeddingsConfig
    resume_extraction: ResumeExtractionConfig
    ui: UIConfig = UIConfig()
    limits: LimitsConfig = LimitsConfig()
    prep: PrepConfig = PrepConfig()

    @property
    def is_dev(self) -> bool:
        return self.app_env.env == "dev"

    @property
    def is_prod(self) -> bool:
        return self.app_env.env == "prod"


# ---------------------------------------------------------------------------
# TOML deep-merge helper
# ---------------------------------------------------------------------------

def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base. Override wins on conflicts."""
    result = dict(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result


# ---------------------------------------------------------------------------
# Load settings
# ---------------------------------------------------------------------------

def load_settings(path: str | None = None) -> AppConfig:
    """
    Load and merge configuration:
      1. settings.toml          (base, always loaded)
      2. settings.<env>.toml    (environment override, if present)

    The active environment is determined by the APP_ENV environment variable
    (default: 'dev'). Secrets are never stored in TOML files — they come
    from environment variables.
    """
    infra_dir = Path(__file__).parent if path is None else Path(path).parent
    base_path = infra_dir / "settings.toml" if path is None else Path(path)

    with open(base_path, "rb") as f:
        data = tomllib.load(f)

    # Load environment-specific overrides
    env = get_app_env()
    env_path = infra_dir / f"settings.{env}.toml"
    if env_path.exists():
        with open(env_path, "rb") as f:
            env_data = tomllib.load(f)
        data = _deep_merge(data, env_data)

    return AppConfig(
        app_env=AppEnvConfig(**data.get("app", {"env": env})),
        server=ServerConfig(**data.get("server", {})),
        supabase=SupabaseConfig(
            url=os.getenv("SUPABASE_URL"),
            key=os.getenv("SUPABASE_PUBLISHABLE_KEY"),
        ),
        embeddings=EmbeddingsConfig(**data["embeddings"]),
        resume_extraction=ResumeExtractionConfig(**data["resume_extraction"]),
        ui=UIConfig(**data["ui"]) if "ui" in data else UIConfig(),
        limits=LimitsConfig(**data["limits"]) if "limits" in data else LimitsConfig(),
        prep=PrepConfig(**data["prep"]) if "prep" in data else PrepConfig(),
    )
