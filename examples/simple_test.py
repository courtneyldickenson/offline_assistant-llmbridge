from llmbridge import LLMBridge

bridge = LLMBridge(adapter="ollama")
print(bridge.generate("Hello"))
