import argparse
from .bridge import LLMBridge


def main():
    parser = argparse.ArgumentParser(description="LLMBridge CLI")
    parser.add_argument("prompt")
    parser.add_argument("--adapter", default="ollama")
    parser.add_argument("--model", default="default-model")
    args = parser.parse_args()

    bridge = LLMBridge(adapter=args.adapter, config={"model": args.model})
    output = bridge.generate(args.prompt)
    print(output)


if __name__ == "__main__":
    main()
