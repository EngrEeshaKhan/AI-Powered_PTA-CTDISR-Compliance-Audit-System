from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[4]

CACHE_DIR = PROJECT_ROOT / "storage" / "cache" / "embeddings"
CACHE_FILE = CACHE_DIR / "embedding_cache.json"


def _ensure_cache_dir() -> None:
    """Create the embedding cache directory if it does not exist."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def create_text_hash(text: str) -> str:
    """
    Create a stable SHA-256 hash for a chunk of text.

    The hash lets us determine whether a chunk has already
    been embedded.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_cache() -> dict[str, Any]:
    """Load the persistent embedding cache."""
    _ensure_cache_dir()

    if not CACHE_FILE.exists():
        return {}

    with CACHE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_cache(cache: dict[str, Any]) -> None:
    """Save the embedding cache to disk."""
    _ensure_cache_dir()

    with CACHE_FILE.open("w", encoding="utf-8") as file:
        json.dump(cache, file, indent=2, ensure_ascii=False)


def is_cached(text: str) -> bool:
    """Return True if this text already has a cached embedding."""
    cache = load_cache()
    text_hash = create_text_hash(text)

    return text_hash in cache


def get_cached_embedding(text: str) -> list[float] | None:
    """Return a cached embedding, or None if it does not exist."""
    cache = load_cache()
    text_hash = create_text_hash(text)

    entry = cache.get(text_hash)

    if entry is None:
        return None

    return entry["embedding"]


def cache_embedding(
    text: str,
    embedding: list[float],
    metadata: dict[str, Any] | None = None,
) -> None:
    """Save an embedding and its metadata in the persistent cache."""
    cache = load_cache()
    text_hash = create_text_hash(text)

    cache[text_hash] = {
        "embedding": embedding,
        "metadata": metadata or {},
    }

    save_cache(cache)


def get_cache_size() -> int:
    """Return the number of cached embeddings."""
    cache = load_cache()
    return len(cache)


def clear_cache() -> None:
    """Delete all cached embeddings."""
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()