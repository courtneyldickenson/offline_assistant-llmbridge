import yaml
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from llmbridge.embeddings.embedder import Embedder

import subprocess
import json
from pathlib import Path
from datetime import datetime

LOG_PATH = Path("logs/skill_router.log.jsonl")
LOG_PATH.parent.mkdir(exist_ok=True)

class UniversalAdapter:
    def __init__(self, config_path, use_llm=False):
        # Load config file
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Get embedder model name from config or default to BGE small
        embed_model = self.config.get("embedding_backend", "BAAI/bge-small-en-v1.5")
        self.embedder = Embedder(model_name=embed_model)

        # Precompute skill description embeddings for matching
        self.skills = self.config["skills"]
        self.skill_descs = [s["description"] for s in self.skills]
        self.skill_vectors = self.embedder.encode(self.skill_descs)

    def classify_sentiment(self, text):
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

        return {
            "chosen_skill": chosen_skill["name"],
            "sentiment": sentiment,
            "reasoning": reasoning,
            "command": chosen_skill["command"],
            "score": float(sims[best_idx]),
            "description": chosen_skill["description"]
        }

    def confirm_and_log(self, user_input):
        result = self.route(user_input)
        print(f"\nDid you mean: '{result['description']}' (Skill: {result['chosen_skill']})? [y/n]")
        user_confirmation = input("> ").strip().lower() == "y"

        # Log the interaction
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "predicted_skill": result["chosen_skill"],
            "description": result["description"],
            "score": result["score"],
            "sentiment": result["sentiment"],
            "confirmed": user_confirmation
        }
        with open(LOG_PATH, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        if user_confirmation:
            print(f"Running: {result['command']}")
            subprocess.run(result["command"], shell=True)
        else:
            print("Not executing. (Feedback logged.)")

        return log_entry

# CLI for fast test
if __name__ == "__main__":
    ua = UniversalAdapter("config.yaml")
    while True:
        user_input = input("\nType your command (or 'quit'): ")
        if user_input.strip().lower() == "quit":
            break
        ua.confirm_and_log(user_input)
