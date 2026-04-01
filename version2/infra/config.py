import os
import tomllib
from pathlib import Path
from pydantic import BaseModel


# -----------------------------
# Pydantic Config Models
# -----------------------------

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


class AppConfig(BaseModel):
    supabase: SupabaseConfig
    embeddings: EmbeddingsConfig
    resume_extraction: ResumeExtractionConfig
    ui: UIConfig = UIConfig()


# -----------------------------
# Load settings.toml
# -----------------------------

def load_settings(path: str | None = None) -> AppConfig:
    """
    Load settings.toml and return a fully structured AppConfig.
    Matches your existing TOML structure:
    
    [embeddings]
    provider = "..."
    model_name = "..."
    batch_size = 128
    normalize = true

    [resume_extraction]
    provider = "groq"
    model = "llama-3.1-70b-versatile"
    endpoint = "https://api.groq.com/openai/v1/chat/completions"
    """


    
    if path is None:
        path = Path(__file__).parent / "settings.toml"

    with open(path, "rb") as f:
        data = tomllib.load(f)

    return AppConfig(
        supabase=SupabaseConfig(
            url=os.getenv("SUPABASE_URL"),
            key=os.getenv("SUPABASE_PUBLISHABLE_KEY"),
        ),
        embeddings=EmbeddingsConfig(**data["embeddings"]),
        resume_extraction=ResumeExtractionConfig(**data["resume_extraction"]),
        ui=UIConfig(**data["ui"]) if "ui" in data else UIConfig(),
    )
