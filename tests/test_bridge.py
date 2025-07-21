from llmbridge.bridge import LLMBridge


def test_ollama_fake_output():
    bridge = LLMBridge(adapter="ollama")
    assert bridge.generate("test") == "Fake Ollama output"
