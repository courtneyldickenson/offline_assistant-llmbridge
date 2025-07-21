# offline_assistant-llmbridge

Simple modular connector for experimenting with language model adapters.

## Usage
```python
from llmbridge import LLMBridge

llm = LLMBridge(adapter="ollama")
print(llm.generate("Hello"))
```

Extensions can implement new adapters under `llmbridge/adapters`.
