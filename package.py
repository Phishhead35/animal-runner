#!/usr/bin/env python3
"""
Animal Runner - Distribution Packager
Creates a release zip for Ko-fi, itch.io, or GitHub.
Usage:
    python package.py             # package current version
    python package.py --version 2.1
"""

import argparse
import shutil
import zipfile
from datetime import date
from pathlib import Path


VERSION = "2.0"
GAME_FILE = "animal_runner.html"
README_FILE = "README.md"
SCREENSHOT_DIR = "screenshots"


README_TEMPLATE = """# 🐸 Cartoon Animal Runner v{version}

An endless runner game playable directly in any modern web browser — no install required.

## How to Play

1. Open `animal_runner.html` in Chrome, Firefox, Safari, or Edge.
2. Press **Space** or **↑** to jump (hold to charge a higher jump).
3. Press **↓** or **S** to duck.
4. Survive as long as possible and collect coins!

## Controls

| Key / Button      | Action                          |
|-------------------|---------------------------------|
| Space / ↑         | Jump (hold = higher jump)       |
| ↓ / S             | Duck                            |
| Double-tap Space  | Quick mid-height jump           |
| 1 / 2 / 3         | Buy Shield / Magnet / Doubler   |
| S (start screen)  | Open Shop                       |
| L                 | Toggle Leaderboard              |
| A                 | Toggle Assist Mode              |
| M                 | Toggle Music                    |

## Features

- **12 playable characters** — Frog, Dog, Cat, Monkey, Capybara, Hippo, Elephant,
  Puffin, Axolotl, Pig, Moose, Bear
- **48 unlockable skins** — 4 per character, purchased with coins
- **6 biomes** — Grasslands → Desert → Night Desert → Storm → Arctic → Underwater
- **3 power-ups** — Shield, Magnet, Score Doubler
- **Local leaderboard** — top 10 scores saved in the browser
- **Assist Mode** — gentler physics for casual players
- **Background music** — two original chiptune tracks (looping)
- **Mobile-friendly** — touch controls + responsive layout

## System Requirements

Any modern web browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+).
No internet connection required after download.

## Files

```
animal_runner_v{version}.zip
├── animal_runner.html        ← the complete game (single file)
├── README.md                 ← this file
└── screenshots/
    ├── 01_title.png
    ├── 02_grasslands.png
    ├── 03_night.png
    ├── 04_storm.png
    ├── 05_arctic.png
    ├── 06_underwater.png
    ├── 07_shop.png
    └── 08_powerups.png
```

## License

Free to play and share. Please don't redistribute as your own work.

---
Made with ❤️ and JavaScript · Released {today}
"""


def build_readme(version: str) -> str:
    return README_TEMPLATE.format(version=version, today=date.today().strftime("%B %d, %Y"))


def package(version: str, output_dir: Path):
    root = Path(__file__).parent
    game = root / GAME_FILE
    readme = root / README_FILE
    screenshots = root / SCREENSHOT_DIR

    if not game.exists():
        raise FileNotFoundError(f"Game file not found: {game}")

    zip_name = f"animal_runner_v{version}.zip"
    zip_path = output_dir / zip_name
    output_dir.mkdir(exist_ok=True)

    # Write (or refresh) README
    readme.write_text(build_readme(version), encoding="utf-8")
    print(f"  Wrote {README_FILE}")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(game,   GAME_FILE)
        zf.write(readme, README_FILE)
        print(f"  Added {GAME_FILE}")
        print(f"  Added {README_FILE}")

        if screenshots.exists():
            for png in sorted(screenshots.glob("*.png")):
                arcname = f"screenshots/{png.name}"
                zf.write(png, arcname)
                print(f"  Added {arcname}")
        else:
            print(f"  (No screenshots folder found — skipping)")

    size_kb = zip_path.stat().st_size / 1024
    print(f"\n✅ Created: {zip_path.name}  ({size_kb:.1f} KB)")
    return zip_path


def main():
    parser = argparse.ArgumentParser(description="Package Animal Runner for distribution")
    parser.add_argument("--version", default=VERSION, help=f"Version string (default: {VERSION})")
    parser.add_argument("--output", default=".", help="Output directory (default: current dir)")
    args = parser.parse_args()

    print(f"🐸 Animal Runner Distribution Packager")
    print(f"   Version: v{args.version}\n")

    try:
        zip_path = package(args.version, Path(args.output))
        print(f"\nUpload '{zip_path.name}' to Ko-fi, itch.io, or attach to your GitHub release.")
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        print(f"Make sure '{GAME_FILE}' is in the same directory as this script.")


if __name__ == "__main__":
    main()
