import yaml
from embeddings.nomic_embedder import NomicEmbedder
from llms.ollama_client import OllamaClient
import subprocess

class UniversalAdapter:
    def __init__(self, config_path):
        # Load config
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        # Setup embedding and LLM backends
        self.embedder = NomicEmbedder()  # swap out as needed
        self.llm = OllamaClient()        # swap out as needed
        # Precompute skill vectors
        self.skills = self.config["skills"]
        self.skill_descs = [s["description"] for s in self.skills]
        self.skill_vectors = self.embedder.encode(self.skill_descs)

    def classify_sentiment(self, text):
        # Simple placeholder: use a keyword, real one would use a model
        if "asap" in text.lower() or "now" in text.lower():
            return "urgent"
        return "neutral"

    def route(self, user_input):
        # 1. Embed user input
        user_vec = self.embedder.encode([user_input])
        # 2. Cosine sim to all skill descriptions
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity
        sims = cosine_similarity(user_vec, self.skill_vectors)[0]
        best_idx = int(np.argmax(sims))
        chosen_skill = self.skills[best_idx]
        sentiment = self.classify_sentiment(user_input)
        reasoning = f"Matched skill '{chosen_skill['name']}' with score {sims[best_idx]:.2f}"

        # Optionally run the skill's command (fake for now)
        # subprocess.run(chosen_skill['command'], shell=True)

        return {
            "chosen_skill": chosen_skill["name"],
            "sentiment": sentiment,
            "reasoning": reasoning,
            "command": chosen_skill["command"],
            "score": float(sims[best_idx])
        }
