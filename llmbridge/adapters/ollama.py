from .base import BaseAdapter


class OllamaAdapter(BaseAdapter):
    def generate(self, prompt: str, **kwargs) -> str:
        return "Fake Ollama output"
