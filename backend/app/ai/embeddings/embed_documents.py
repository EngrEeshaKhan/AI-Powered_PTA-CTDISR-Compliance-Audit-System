from __future__ import annotations

from typing import Any

from app.ai.embeddings.embedding_cache import (
    cache_embedding,
    get_cached_embedding,
)
from app.ai.embeddings.embedding_model import generate_embeddings


def embed_chunks(
    chunks: list[dict[str, Any]],
    batch_size: int = 32,
) -> list[dict[str, Any]]:
    """
    Generate embeddings for document chunks.

    Already-cached chunks are reused.
    Only new chunks are sent to the embedding model.
    """

    if not chunks:
        return []

    results: list[dict[str, Any]] = []

    texts_to_embed: list[str] = []
    new_chunk_positions: list[int] = []

    # Check the cache first
    for position, chunk in enumerate(chunks):
        text = chunk.get("text", "").strip()

        if not text:
            continue

        cached_embedding = get_cached_embedding(text)

        if cached_embedding is not None:
            results.append(
                {
                    "chunk": chunk,
                    "embedding": cached_embedding,
                }
            )
        else:
            texts_to_embed.append(text)
            new_chunk_positions.append(position)

    # Generate embeddings only for new chunks
    if texts_to_embed:
        new_embeddings = generate_embeddings(
            texts_to_embed,
            batch_size=batch_size,
        )

        for text, embedding, position in zip(
            texts_to_embed,
            new_embeddings,
            new_chunk_positions,
        ):
            chunk = chunks[position]

            cache_embedding(
                text=text,
                embedding=embedding,
                metadata={
                    "chunk_index": chunk.get("chunk_index"),
                    "section_index": chunk.get("section_index"),
                    "part_index": chunk.get("part_index"),
                    "document_type": chunk.get("document_type"),
                    "file_name": chunk.get("file_name"),
                    "sheet": chunk.get("sheet"),
                    "row_index": chunk.get("row_index"),
                    "asset_serial_number": chunk.get(
                        "asset_serial_number"
                    ),
                },
            )

            results.append(
                {
                    "chunk": chunk,
                    "embedding": embedding,
                }
            )

    return results