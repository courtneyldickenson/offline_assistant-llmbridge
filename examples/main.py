# examples/main.py

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from llmbridge.universal_adapter import UniversalAdapter

if __name__ == "__main__":
    # Path to your config.yaml (adjust if it's not at project root)
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")

    # Initialize the router
    adapter = UniversalAdapter(config_path=CONFIG_PATH)

    # Try out some example inputs
    test_inputs = [
        "Please open the downloads folder",
        "Can you delete this file now?",
        "Remove my document",
        "Open the project folder asap"
    ]

    for text in test_inputs:
        result = adapter.route(text)
        print(f"\n🧠 Input: {text}")
        print(f"📎 Matched Skill: {result['chosen_skill']}")
        print(f"🗣️ Sentiment: {result['sentiment']}")
        print(f"🧠 Reasoning: {result['reasoning']}")
        print(f"💻 Command: {result['command']}")
        print(f"📊 Score: {result['score']:.3f}")
