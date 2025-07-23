# llmbridge/skills/rename_folder.py

import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Rename a folder.")
    parser.add_argument("--old_path", required=True, help="Current folder path.")
    parser.add_argument("--new_path", required=True, help="New folder path/name.")
    args = parser.parse_args()

    try:
        os.rename(args.old_path, args.new_path)
        print(f"Renamed folder: {args.old_path} -> {args.new_path}")
    except Exception as e:
        print(f"Error renaming folder: {e}")

if __name__ == "__main__":
    main()
