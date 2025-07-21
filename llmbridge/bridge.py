from .exceptions import AdapterInitializationError, AdapterGenerationError
from .adapters import ollama, llama_cpp, openai

ADAPTERS = {
    "ollama": ollama.OllamaAdapter,
    "llama_cpp": llama_cpp.LlamaCppAdapter,
    "openai": openai.OpenAIAdapter,
}


class LLMBridge:
    def __init__(self, adapter: str, config=None):
        try:
            self.adapter = ADAPTERS[adapter]()
        except KeyError as e:
            raise AdapterInitializationError(f"Unknown adapter: {adapter}") from e

    def generate(self, prompt: str, **kwargs) -> str:
        try:
            return self.adapter.generate(prompt, **kwargs)
        except Exception as e:
            raise AdapterGenerationError(str(e))
