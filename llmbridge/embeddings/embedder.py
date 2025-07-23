# llmbridge/embeddings/embedder.py

from sentence_transformers import SentenceTransformer
import numpy as np

class Embedder:
    def __init__(self, model_name="BAAI/bge-small-en-v1.5"):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        return np.array(self.model.encode(texts, convert_to_numpy=True))
