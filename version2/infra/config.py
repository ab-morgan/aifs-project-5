import os
import toml
import pathlib

# Directory where config.py lives
INFRA_DIR = pathlib.Path(__file__).resolve().parent

# Load settings.toml from the same directory
SETTINGS = toml.load(INFRA_DIR / "settings.toml")

# --- Supabase ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")

# --- Embeddings ---
EMBEDDING_PROVIDER = SETTINGS["embeddings"]["provider"]
EMBEDDING_MODEL_NAME = SETTINGS["embeddings"]["model_name"]
EMBEDDING_BATCH_SIZE = SETTINGS["embeddings"]["batch_size"]
EMBEDDING_NORMALIZE = SETTINGS["embeddings"]["normalize"]

def load_settings():
    return {
        "supabase": {
            "url": SUPABASE_URL,
            "key": SUPABASE_PUBLISHABLE_KEY,
        },
        "embeddings": {
            "provider": EMBEDDING_PROVIDER,
            "model_name": EMBEDDING_MODEL_NAME,
            "batch_size": EMBEDDING_BATCH_SIZE,
            "normalize": EMBEDDING_NORMALIZE,
        },
    }
