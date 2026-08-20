from __future__ import annotations

from pathlib import Path
from typing import Any

import faiss
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[4]

VECTOR_DIR = PROJECT_ROOT / "storage" / "vectors"

INDEX_FILE = VECTOR_DIR / "knowledge.index"
METADATA_FILE = VECTOR_DIR / "knowledge_metadata.json"

EMBEDDING_DIMENSION = 384


class VectorManager:
    """
    Persistent FAISS vector store.

    Responsibilities:
        - create/load FAISS index
        - add embeddings
        - keep chunk metadata aligned with vectors
        - save/load index and metadata
        - perform similarity search
    """

    def __init__(
        self,
        index_file: Path | str = INDEX_FILE,
        metadata_file: Path | str = METADATA_FILE,
    ) -> None:

        self.index_file = Path(index_file)
        self.metadata_file = Path(metadata_file)

        self.index_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.index: faiss.Index | None = None
        self.metadata: list[dict[str, Any]] = []

        self.load()

    # ---------------------------------------------------------
    # INDEX CREATION
    # ---------------------------------------------------------

    def _create_index(self) -> faiss.Index:
        """
        Create an empty FAISS index.

        Embeddings are already normalized by the embedding model,
        therefore inner product gives cosine similarity.
        """

        return faiss.IndexFlatIP(
            EMBEDDING_DIMENSION
        )

    # ---------------------------------------------------------
    # LOAD
    # ---------------------------------------------------------

    def load(self) -> None:
        """
        Load existing vector index and metadata.

        If nothing exists yet, create an empty index.
        """

        if self.index_file.exists():

            self.index = faiss.read_index(
                str(self.index_file)
            )

        else:

            self.index = self._create_index()

        if self.metadata_file.exists():

            import json

            with self.metadata_file.open(
                "r",
                encoding="utf-8",
            ) as file:

                self.metadata = json.load(file)

        else:

            self.metadata = []

        # -----------------------------------------------------
        # SAFETY CHECK
        # -----------------------------------------------------

        if self.index.ntotal != len(self.metadata):

            raise RuntimeError(
                "Vector store is inconsistent: "
                f"FAISS contains {self.index.ntotal} vectors "
                f"but metadata contains {len(self.metadata)} records."
            )

    # ---------------------------------------------------------
    # ADD
    # ---------------------------------------------------------

    def add(
        self,
        embeddings: list[list[float]],
        metadata: list[dict[str, Any]],
    ) -> int:
        """
        Add embeddings and their metadata.

        Returns:
            Number of vectors added.
        """

        if not embeddings:
            return 0

        if len(embeddings) != len(metadata):

            raise ValueError(
                "Number of embeddings must equal "
                "number of metadata records."
            )

        if self.index is None:

            self.index = self._create_index()

        vectors = np.asarray(
            embeddings,
            dtype=np.float32,
        )

        if vectors.ndim != 2:

            raise ValueError(
                "Embeddings must be a 2-dimensional array."
            )

        if vectors.shape[1] != EMBEDDING_DIMENSION:

            raise ValueError(
                "Embedding dimension mismatch. "
                f"Expected {EMBEDDING_DIMENSION}, "
                f"received {vectors.shape[1]}."
            )

        # -----------------------------------------------------
        # IMPORTANT
        # -----------------------------------------------------
        # The embedding model already normalizes vectors.
        # Normalize again defensively in case another caller
        # supplies non-normalized vectors.

        faiss.normalize_L2(vectors)

        self.index.add(vectors)

        self.metadata.extend(metadata)

        return len(embeddings)

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    def save(self) -> None:
        """
        Persist FAISS index and metadata to disk.
        """

        if self.index is None:

            self.index = self._create_index()

        self.index_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        faiss.write_index(
            self.index,
            str(self.index_file),
        )

        import json

        with self.metadata_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                self.metadata,
                file,
                indent=2,
                ensure_ascii=False,
            )

    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Search the vector store.

        Returns metadata together with similarity scores.
        """

        if self.index is None:
            return []

        if self.index.ntotal == 0:
            return []

        vector = np.asarray(
            [query_embedding],
            dtype=np.float32,
        )

        if vector.shape[1] != EMBEDDING_DIMENSION:

            raise ValueError(
                "Query embedding dimension mismatch."
            )

        faiss.normalize_L2(vector)

        top_k = min(
            top_k,
            self.index.ntotal,
        )

        scores, indices = self.index.search(
            vector,
            top_k,
        )

        results: list[dict[str, Any]] = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):

            if index < 0:
                continue

            if index >= len(self.metadata):
                continue

            results.append(
                {
                    "score": float(score),
                    "metadata": self.metadata[index],
                }
            )

        return results

    # ---------------------------------------------------------
    # PROPERTIES
    # ---------------------------------------------------------

    @property
    def count(self) -> int:
        """Return the number of vectors currently stored."""

        if self.index is None:
            return 0

        return int(self.index.ntotal)

    # ---------------------------------------------------------
    # CLEAR
    # ---------------------------------------------------------

    def clear(self) -> None:
        """
        Delete all vectors from the current in-memory store.
        """

        self.index = self._create_index()
        self.metadata = []

    # ---------------------------------------------------------
    # SAVE + CLEAR
    # ---------------------------------------------------------

    def clear_and_save(self) -> None:

        self.clear()
        self.save()