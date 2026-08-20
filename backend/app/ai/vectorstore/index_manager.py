from __future__ import annotations

from typing import Any

from app.ai.vectorstore.vector_manager import VectorManager


class IndexManager:
    """
    High-level manager for adding embedded document chunks
    to the persistent vector store.

    The same chunk text is not inserted into the FAISS index
    twice for the same document.
    """

    def __init__(
        self,
        vector_manager: VectorManager | None = None,
    ) -> None:

        self.vector_manager = (
            vector_manager
            if vector_manager is not None
            else VectorManager()
        )

    # ---------------------------------------------------------
    # EXISTING CHUNK IDENTIFIERS
    # ---------------------------------------------------------

    def _existing_chunk_keys(self) -> set[str]:
        """
        Build a set of identifiers for chunks already indexed.
        """

        keys: set[str] = set()

        for item in self.vector_manager.metadata:

            key = item.get("chunk_key")

            if key:
                keys.add(key)

        return keys

    # ---------------------------------------------------------
    # ADD EMBEDDED CHUNKS
    # ---------------------------------------------------------

    def add_embedded_chunks(
        self,
        embedded_chunks: list[dict[str, Any]],
    ) -> int:
        """
        Add embedded chunks to the persistent vector index.

        Each item must contain:

            {
                "chunk": {...},
                "embedding": [...]
            }

        Returns:
            Number of newly indexed chunks.
        """

        if not embedded_chunks:
            return 0

        existing_keys = self._existing_chunk_keys()

        embeddings: list[list[float]] = []
        metadata: list[dict[str, Any]] = []

        for item in embedded_chunks:

            chunk = item.get("chunk")
            embedding = item.get("embedding")

            if not chunk:
                continue

            if embedding is None:
                continue

            chunk_key = chunk.get("chunk_key")

            if not chunk_key:

                raise ValueError(
                    "Chunk is missing required 'chunk_key'."
                )

            # -------------------------------------------------
            # Avoid duplicate vector insertion
            # -------------------------------------------------

            if chunk_key in existing_keys:
                continue

            embeddings.append(embedding)

            metadata.append(
                {
                    **chunk,

                    # Keep the original chunk text.
                    "text": chunk.get(
                        "text",
                        "",
                    ),

                    "chunk_key": chunk_key,
                }
            )

            existing_keys.add(chunk_key)

        if not embeddings:
            return 0

        added = self.vector_manager.add(
            embeddings=embeddings,
            metadata=metadata,
        )

        self.vector_manager.save()

        return added

    # ---------------------------------------------------------
    # STATISTICS
    # ---------------------------------------------------------

    def count(self) -> int:

        return self.vector_manager.count

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    def save(self) -> None:

        self.vector_manager.save()