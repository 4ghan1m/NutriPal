"""PyInstaller build script for NutriPal."""
import json
import shutil
import subprocess
import sys
from pathlib import Path


def build():
    project_root = Path(__file__).parent
    dist_dir = project_root / "dist" / "NutriPal"

    # Preserve user's API key if already set in dist config
    old_config = None
    old_config_path = dist_dir / "config.json"
    if old_config_path.exists():
        try:
            with open(old_config_path, "r", encoding="utf-8") as f:
                old_config = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Clean previous build
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",
        "--name", "NutriPal",
        "--clean",
        "--noconfirm",
        str(project_root / "main.py"),
    ]

    subprocess.run(cmd, check=True)

    # Copy config.json (keep old API key if it was set)
    if old_config and old_config.get("deepseek_api_key", "").strip():
        with open(old_config_path, "w", encoding="utf-8") as f:
            json.dump(old_config, f, ensure_ascii=False, indent=2)
        print("Preserved existing API key in dist config.")
    else:
        shutil.copy(project_root / "config.json", old_config_path)

    # Create empty data dir
    data_dir = dist_dir / "data"
    data_dir.mkdir(exist_ok=True)
    (data_dir / ".gitkeep").touch()

    print(f"\nBuild complete! Output in {dist_dir}/")
    print("Run: dist/NutriPal/NutriPal.exe")


if __name__ == "__main__":
    build()
