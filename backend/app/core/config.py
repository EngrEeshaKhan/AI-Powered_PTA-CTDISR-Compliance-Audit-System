from pathlib import Path
from pydantic_settings import BaseSettings


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "PTA CTDISR Compliance Audit System"

    # Storage
    STORAGE_DIR: Path = PROJECT_ROOT / "storage"
    DOCUMENTS_DIR: Path = STORAGE_DIR / "documents"
    VECTORS_DIR: Path = STORAGE_DIR / "vectors"

    # Local AI models
    LLAMA_MODEL_DIR: Path = (
        PROJECT_ROOT / "models" / "llama-3.2-3b-instruct"
    )

    LORA_MODEL_DIR: Path = (
        PROJECT_ROOT / "models" / "pta-llama-3.2-3b-lora" / "final"
    )

    EMBEDDING_MODEL_DIR: Path = (
        PROJECT_ROOT
        / "models"
        / "embedding-model"
        / "models--sentence-transformers--all-MiniLM-L6-v2"
        / "snapshots"
        / "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
    )

    # Embedding
    EMBEDDING_DIMENSION: int = 384

    # LLM
    MAX_NEW_TOKENS: int = 700

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()