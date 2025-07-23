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
        print("[DEBUG] Initializing UniversalAdapter...")
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        embed_model = self.config.get("embedding_backend", "BAAI/bge-small-en-v1.5")
        print(f"[DEBUG] Embedder model: {embed_model}")
        self.embedder = Embedder(model_name=embed_model)

        self.arg_suggester_mode = self.config.get("argument_suggester", {}).get("mode", "api")
        self.rag_api_url = self.config.get("argument_suggester", {}).get("api_url", "http://localhost:8000/search")
        print(f"[DEBUG] RAG API URL: {self.rag_api_url}")

        self.skills = self.config["skills"]
        self.skill_descs = [s["description"] for s in self.skills]
        print(f"[DEBUG] Loaded {len(self.skills)} skills: {[s['name'] for s in self.skills]}")
        self.skill_vectors = self.embedder.encode(self.skill_descs)
        print("[DEBUG] Skill embeddings computed.")

    def classify_sentiment(self, text):
        lowered = text.lower()
        if "asap" in lowered or "now" in lowered:
            return "urgent"
        return "neutral"

    def get_required_args(self, command_template):
        args = re.findall(r"\{(\w+)\}", command_template)
        print(f"[DEBUG] Required args for '{command_template}': {args}")
        return args

    def trigger_scan(self):
        scan_url = self.rag_api_url.replace("/search", "/scan")
        try:
            print(f"[DEBUG] Sending scan request to {scan_url} ...")
            start_time = time.time()
            resp = requests.post(scan_url, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            elapsed = round(time.time() - start_time, 2)
            print(f"[DEBUG] [SCAN COMPLETE] {data} (took {elapsed}s)")
        except Exception as e:
            print(f"[DEBUG] [SCAN ERROR] Could not complete scan: {e}")

    def prompt_for_argument(self, arg_name, user_query):
        print(f"[DEBUG] Prompting for argument '{arg_name}' with query '{user_query}'")
        self.trigger_scan()
        candidates = self.query_rag_api(user_query, top_k=20)
        print(f"[DEBUG] RAG API returned {len(candidates)} candidates")
        page = 0
        page_size = 5
        while True:
            options = candidates[page * page_size : (page + 1) * page_size]
            if not options:
                print("[DEBUG] No more matches in RAG results.")
                break
            print(f"\nWhich {arg_name} did you mean?")
            for idx, match in enumerate(options, 1):
                print(f"{idx}. {match.get('path', str(match))}")
            print("[n] Next page")
            print("[x] Cancel")
            choice = input("> ").strip().lower()
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                chosen = options[int(choice)-1].get("path", str(options[int(choice)-1]))
                print(f"[DEBUG] User chose: {chosen}")
                return chosen
            elif choice == "n":
                page += 1
            elif choice == "x":
                print("[DEBUG] User canceled argument selection.")
                break
            else:
                print("Please enter a number, n, or x.")
        manual = input(f"Enter {arg_name} manually: ")
        print(f"[DEBUG] User manually entered: {manual}")
        return manual

    def query_rag_api(self, query, top_k=10):
        payload = {"query": query}
        print(f"[DEBUG] Querying RAG API at {self.rag_api_url} with: {payload}")
        try:
            resp = requests.post(self.rag_api_url, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            print(f"[DEBUG] RAG API response: {str(data)[:300]}...")  # Only first 300 chars to keep it readable
            return data.get("results", [])
        except Exception as e:
            print(f"[DEBUG] Error querying RAG API: {e}")
            return []

    def fill_command_template(self, command, args):
        print(f"[DEBUG] Filling command template: '{command}' with args: {args}")
        for k, v in args.items():
            command = command.replace(f"{{{k}}}", str(v))
        print(f"[DEBUG] Final filled command: '{command}'")
        return command

    def extract_args_from_query(self, user_query):
        print(f"[DEBUG] Extracting args from user query: '{user_query}'")
        return {}

    def route(self, user_input):
        print(f"[DEBUG] Routing user input: '{user_input}'")
        user_vec = self.embedder.encode([user_input])
        sims = cosine_similarity(user_vec, self.skill_vectors)[0]
        print(f"[DEBUG] Cosine similarities: {sims}")
        best_idx = int(np.argmax(sims))
        chosen_skill = self.skills[best_idx]
        print(f"[DEBUG] Chosen skill: {chosen_skill['name']}")
        sentiment = self.classify_sentiment(user_input)
        reasoning = f"Matched skill '{chosen_skill['name']}' with score {sims[best_idx]:.2f}"

        skill_command = chosen_skill["command"]
        required_args = self.get_required_args(skill_command)
        provided_args = self.extract_args_from_query(user_input)
        for arg in required_args:
            if arg not in provided_args or not provided_args[arg]:
                provided_args[arg] = self.prompt_for_argument(arg, user_input)
        filled_command = self.fill_command_template(skill_command, provided_args)

        result = {
            "chosen_skill": chosen_skill["name"],
            "sentiment": sentiment,
            "reasoning": reasoning,
            "command": filled_command,
            "score": float(sims[best_idx]),
            "description": chosen_skill["description"]
        }
        print(f"[DEBUG] Routing result: {result}")
        return result

    def confirm_and_log(self, user_input):
        print(f"[DEBUG] Starting confirm_and_log for: '{user_input}'")
        result = self.route(user_input)
        print(f"\nDid you mean: '{result['description']}' (Skill: {result['chosen_skill']})? [y/n]")
        user_confirmation = input("> ").strip().lower() == "y"
        print(f"[DEBUG] User confirmation: {user_confirmation}")

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

        print(f"[DEBUG] Log entry: {log_entry}")
        return log_entry

# CLI mode for local dev/testing
if __name__ == "__main__":
    ua = UniversalAdapter("config.yaml")
    while True:
        user_input = input("\nType your command (or 'quit'): ")
        if user_input.strip().lower() == "quit":
            break
        ua.confirm_and_log(user_input)
