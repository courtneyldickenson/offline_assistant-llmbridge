import yaml
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from embeddings.nomic_embedder import NomicEmbedder

import subprocess


class UniversalAdapter:
    def __init__(self, config_path, use_llm=False):
        # Load config file
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Setup embedding backend (Nomic) for intent/sentiment
        self.embedder = NomicEmbedder()

    

        # Precompute skill description embeddings for matching
        self.skills = self.config["skills"]
        self.skill_descs = [s["description"] for s in self.skills]
        self.skill_vectors = self.embedder.encode(self.skill_descs)

    def classify_sentiment(self, text):
        # placeholder sentiment classifier
        lowered = text.lower()
        if "asap" in lowered or "now" in lowered:
            return "urgent"
        return "neutral"

    def route(self, user_input):
        # Embed user input
        user_vec = self.embedder.encode([user_input])

        # Compute cosine similarity with skill vectors
        sims = cosine_similarity(user_vec, self.skill_vectors)[0]
        best_idx = int(np.argmax(sims))

        chosen_skill = self.skills[best_idx]
        sentiment = self.classify_sentiment(user_input)
        reasoning = f"Matched skill '{chosen_skill['name']}' with score {sims[best_idx]:.2f}"

        # Optionally execute the matched skill command (commented out for safety)
        # subprocess.run(chosen_skill['command'], shell=True)

        # Return structured result
        return {
            "chosen_skill": chosen_skill["name"],
            "sentiment": sentiment,
            "reasoning": reasoning,
            "command": chosen_skill["command"],
            "score": float(sims[best_idx])
        }
