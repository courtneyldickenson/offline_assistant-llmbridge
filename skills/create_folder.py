# llmbridge/skills/create_folder.py

import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Create a new folder.")
    parser.add_argument("--path", required=True, help="Full path for the folder to create.")
    args = parser.parse_args()

    try:
        os.makedirs(args.path, exist_ok=True)
        print(f"Created folder: {args.path}")
    except Exception as e:
        print(f"Error creating folder: {e}")

if __name__ == "__main__":
    main()
