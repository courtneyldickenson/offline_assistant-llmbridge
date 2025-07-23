from .exceptions import AdapterInitializationError, AdapterGenerationError
from .universal_adapter import UniversalAdapter

class LLMBridge:
    def __init__(self, config_path: str):
        try:
            self.adapter = UniversalAdapter(config_path)
        except Exception as e:
            raise AdapterInitializationError(f"Failed to initialize UniversalAdapter: {e}") from e

    def route(self, user_input: str) -> dict:
        try:
            return self.adapter.route(user_input)
        except Exception as e:
            raise AdapterGenerationError(str(e))
