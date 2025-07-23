# skills/open_folder.py

import argparse
import os
import sys
import subprocess

def open_folder(path):
    if not os.path.exists(path):
        print(f"[ERROR] Path does not exist: {path}")
        sys.exit(1)
    if not os.path.isdir(path):
        print(f"[ERROR] Path is not a directory: {path}")
        sys.exit(1)

    # Platform-specific open command
    try:
        if sys.platform.startswith("darwin"):
            subprocess.run(["open", path])
        elif sys.platform.startswith("win"):
            os.startfile(path)
        else:  # Assume Linux
            subprocess.run(["xdg-open", path])
        print(f"[INFO] Opened folder: {path}")
    except Exception as e:
        print(f"[ERROR] Could not open folder: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Open a folder in the file explorer")
    parser.add_argument("--path", required=True, help="Path to folder")
    args = parser.parse_args()
    open_folder(args.path)
