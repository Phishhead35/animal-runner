#!/usr/bin/env python3
"""
Animal Runner - Game Launcher
Opens the game in the default web browser.
"""

import os
import sys
import webbrowser
from pathlib import Path


def main():
    game_file = Path(__file__).parent / "animal_runner.html"

    if not game_file.exists():
        print(f"ERROR: Could not find '{game_file}'")
        print("Make sure 'animal_runner.html' is in the same folder as this script.")
        sys.exit(1)

    url = game_file.resolve().as_uri()
    print(f"🐸 Animal Runner v2.0")
    print(f"Opening: {url}")
    webbrowser.open(url)
    print("Game launched! Close the browser tab when done.")


if __name__ == "__main__":
    main()
