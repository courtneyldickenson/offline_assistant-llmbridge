class BaseAdapter:
    def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError("Subclasses must implement generate")
