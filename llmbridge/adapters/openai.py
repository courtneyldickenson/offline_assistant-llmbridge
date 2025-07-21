from .base import BaseAdapter


class OpenAIAdapter(BaseAdapter):
    def generate(self, prompt: str, **kwargs) -> str:
        return "Fake OpenAI output"
