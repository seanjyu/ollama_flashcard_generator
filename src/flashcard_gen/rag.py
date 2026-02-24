# src/flashcard_gen/rag.py
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from .chunker import BaseChunker, Chunk, ChunkHeaderThenParagraph


class FAISSRetriever:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.encoder = SentenceTransformer(model_name)
        self.index = None
        self.chunks: list[Chunk] = []

    def index_chunks(self, chunks: list[Chunk]) -> None:
        """Index pre-chunked content."""
        self.chunks = chunks

        if not self.chunks:
            return

        texts = [c.content for c in self.chunks]
        embeddings = self.encoder.encode(texts)
        embeddings = np.array(embeddings).astype('float32')

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)

    def index_document(self, content: str, chunker: BaseChunker |None = None, max_words: int = 300) -> None:
        """Hierarchical chunking then FAISS index."""
        chunker = chunker or ChunkHeaderThenParagraph()
        chunks = chunker.chunk(content)
        self.index_chunks(chunks)

        if not self.chunks:
            return

        texts = [c.content for c in self.chunks]
        embeddings = self.encoder.encode(texts)
        embeddings = np.array(embeddings).astype('float32')

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)

    def retrieve(self, query: str, k: int = 3) -> list[Chunk]:
        """Retrieve top-k relevant chunks."""
        if not self.index or not self.chunks:
            return self.chunks[:k]

        query_embedding = self.encoder.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')

        k = min(k, len(self.chunks))
        distances, indices = self.index.search(query_embedding, k)

        return [self.chunks[i] for i in indices[0] if i < len(self.chunks)]

    def get_all_chunks(self) -> list[Chunk]:
        return self.chunks
