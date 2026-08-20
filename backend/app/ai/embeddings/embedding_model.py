
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from sentence_transformers import SentenceTransformer


# Project root:
# backend/app/ai/embeddings/embedding_model.py
#                       ↑
# parents[4] = project root
PROJECT_ROOT = Path(__file__).resolve().parents[4]

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "embedding-model"
    / "models--sentence-transformers--all-MiniLM-L6-v2"
    / "snapshots"
    / "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
)


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load the local embedding model.

    The model is loaded from the repository's models directory.
    No internet download is required.
    """

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Local embedding model not found: {MODEL_PATH}"
        )

    return SentenceTransformer(
        str(MODEL_PATH),
        local_files_only=True,
    )


def generate_embeddings(
    texts: list[str],
    batch_size: int = 32,
) -> list[list[float]]:
    """
    Generate normalized embeddings for text chunks.

    all-MiniLM-L6-v2 produces 384-dimensional vectors.
    """

    if not texts:
        return []

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embeddings.tolist()
