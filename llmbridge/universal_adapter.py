import yaml
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from llmbridge.embeddings.embedder import Embedder

import subprocess
import json
from pathlib import Path
from datetime import datetime
import re
import requests
import time

LOG_PATH = Path("logs/skill_router.log.jsonl")
LOG_PATH.parent.mkdir(exist_ok=True)

class UniversalAdapter:
    def __init__(self, config_path, use_llm=False):
        # Load config
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Embedder setup
        embed_model = self.config.get("embedding_backend", "BAAI/bge-small-en-v1.5")
        self.embedder = Embedder(model_name=embed_model)

        # RAG config
        self.arg_suggester_mode = self.config.get("argument_suggester", {}).get("mode", "api")
        self.rag_api_url = self.config.get("argument_suggester", {}).get("api_url", "http://localhost:8000/search")

        # Load skill data + embed
        self.skills = self.config["skills"]
        self.skill_descs = [s["description"] for s in self.skills]
        self.skill_vectors = self.embedder.encode(self.skill_descs)

    def classify_sentiment(self, text):
        lowered = text.lower()
        if "asap" in lowered or "now" in lowered:
            return "urgent"
        return "neutral"

    def get_required_args(self, command_template):
        return re.findall(r"\{(\w+)\}", command_template)

    

    def trigger_scan(self):
        """Trigger the RAG backend to scan & ingest updated files, and wait for completion."""
        scan_url = self.rag_api_url.replace("/search", "/scan")
        try:
            print("[SCAN] Scanning files for changes...")
            start_time = time.time()
            resp = requests.post(scan_url, timeout=120)  # Increase timeout if needed
            resp.raise_for_status()
            data = resp.json()
            elapsed = round(time.time() - start_time, 2)
            print(f"[SCAN COMPLETE] {data} (took {elapsed}s)")
        except Exception as e:
            print(f"[SCAN ERROR] Could not complete scan: {e}")


    def prompt_for_argument(self, arg_name, user_query):
        self.trigger_scan()  # Always scan before prompting (****assumes the backend only scans for )
        candidates = self.query_rag_api(user_query, top_k=20)
        page = 0
        page_size = 5
        while True:
            options = candidates[page * page_size : (page + 1) * page_size]
            if not options:
                print("No more matches.")
                break
            print(f"\nWhich {arg_name} did you mean?")
            for idx, match in enumerate(options, 1):
                print(f"{idx}. {match.get('path', str(match))}")
            print("[n] Next page")
            print("[x] Cancel")
            choice = input("> ").strip().lower()
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                return options[int(choice)-1].get("path", str(options[int(choice)-1]))
            elif choice == "n":
                page += 1
            elif choice == "x":
                break
            else:
                print("Please enter a number, n, or x.")
        return input(f"Enter {arg_name} manually: ")

    def query_rag_api(self, query, top_k=10):
        payload = {"query": query}
        try:
            resp = requests.post(self.rag_api_url, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data.get("results", [])
        except Exception as e:
            print(f"Error querying RAG API: {e}")
            return []

    def fill_command_template(self, command, args):
        for k, v in args.items():
            command = command.replace(f"{{{k}}}", str(v))
        return command

    def extract_args_from_query(self, user_query):
        # Optional: use LLM or regex in the future
        return {}

    def route(self, user_input):
        user_vec = self.embedder.encode([user_input])
        sims = cosine_similarity(user_vec, self.skill_vectors)[0]
        best_idx = int(np.argmax(sims))
        chosen_skill = self.skills[best_idx]
        sentiment = self.classify_sentiment(user_input)
        reasoning = f"Matched skill '{chosen_skill['name']}' with score {sims[best_idx]:.2f}"

        # Fill arguments
        skill_command = chosen_skill["command"]
        required_args = self.get_required_args(skill_command)
        provided_args = self.extract_args_from_query(user_input)
        for arg in required_args:
            if arg not in provided_args or not provided_args[arg]:
                provided_args[arg] = self.prompt_for_argument(arg, user_input)
        filled_command = self.fill_command_template(skill_command, provided_args)

        return {
            "chosen_skill": chosen_skill["name"],
            "sentiment": sentiment,
            "reasoning": reasoning,
            "command": filled_command,
            "score": float(sims[best_idx]),
            "description": chosen_skill["description"]
        }

    def confirm_and_log(self, user_input):
        result = self.route(user_input)
        print(f"\nDid you mean: '{result['description']}' (Skill: {result['chosen_skill']})? [y/n]")
        user_confirmation = input("> ").strip().lower() == "y"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "predicted_skill": result["chosen_skill"],
            "description": result["description"],
            "score": result["score"],
            "sentiment": result["sentiment"],
            "confirmed": user_confirmation,
            "final_command": result["command"]
        }
        with open(LOG_PATH, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        if user_confirmation:
            print(f"Running: {result['command']}")
            subprocess.run(result["command"], shell=True)
        else:
            print("Not executing. (Feedback logged.)")

        return log_entry

# CLI mode for local dev/testing
if __name__ == "__main__":
    ua = UniversalAdapter("config.yaml")
    while True:
        user_input = input("\nType your command (or 'quit'): ")
        if user_input.strip().lower() == "quit":
            break
        ua.confirm_and_log(user_input)
