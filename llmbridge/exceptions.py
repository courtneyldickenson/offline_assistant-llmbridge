class LLMBridgeError(Exception):
    pass


class AdapterInitializationError(LLMBridgeError):
    pass


class AdapterGenerationError(LLMBridgeError):
    pass
