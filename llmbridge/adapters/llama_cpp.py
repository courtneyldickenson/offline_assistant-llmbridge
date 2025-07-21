from .base import BaseAdapter


class LlamaCppAdapter(BaseAdapter):
    def generate(self, prompt: str, **kwargs) -> str:
        return "Fake llama.cpp output"
