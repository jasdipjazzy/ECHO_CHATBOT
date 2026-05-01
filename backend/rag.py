import json
import numpy as np
import os
from pathlib import Path
import google.generativeai as genai

DATA_DIR = Path(__file__).parent / "data"
EMBEDDINGS_PATH = DATA_DIR / "embeddings.npy"
DOCSTORE_PATH = DATA_DIR / "docstore.json"


def cosine_similarity(a, b):
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


class VectorStore:
    def __init__(self):
        self.documents = []
        self.embeddings = None
        self.ready = False

    def load(self):
        if not EMBEDDINGS_PATH.exists() or not DOCSTORE_PATH.exists():
            raise FileNotFoundError("Run python ingest.py first")
        self.embeddings = np.load(str(EMBEDDINGS_PATH))
        with open(DOCSTORE_PATH, encoding="utf-8") as f:
            self.documents = json.load(f)
        self.ready = True
        print(f"[RAG] Loaded {len(self.documents)} documents.")

    def search(self, query, top_k=3):
        if not self.ready:
            raise RuntimeError("Vector store not loaded.")
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=query,
            task_type="retrieval_query",
        )
        query_vec = np.array(result["embedding"])
        scores = [cosine_similarity(query_vec, self.embeddings[i])
                  for i in range(len(self.documents))]
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            {**self.documents[i], "score": round(scores[i], 4)}
            for i in top_indices if scores[i] > 0.3
        ]


vector_store = VectorStore()
