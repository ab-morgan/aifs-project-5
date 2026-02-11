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


class AppConfig(BaseModel):
    supabase: SupabaseConfig
    embeddings: EmbeddingsConfig
    resume_extraction: ResumeExtractionConfig


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
    )
