import numpy as np

class NomicEmbedder:
    def encode(self, texts):
        """
        Fake embedding method.
        Given a list of texts, returns a numpy array of shape (len(texts), 10).
        Each text is represented by a vector of length 10, where all values
        are simply the length of the text (just for dummy differentiation).
        Replace this with actual embedding logic later.
        """
        return np.array([[len(text)] * 10 for text in texts])
