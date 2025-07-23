# llmbridge/embeddings/nomic_embedder.py
import nomic
from nomic import embed
import numpy as np

class NomicEmbedder:
    def __init__(self, model_name="nomic-embed-text-v1.5"):
        self.model_name = model_name
       

    def encode(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        result = embed.text(texts, model=self.model_name)
        embeddings = np.array(result["embeddings"])
        return embeddings
