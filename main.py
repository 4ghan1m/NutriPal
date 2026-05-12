"""NutriPal - AI Nutritionist in your terminal."""
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

DATA_DIR = BASE_DIR / "data"
CONFIG_PATH = BASE_DIR / "config.json"


def main():
    from nutripal.app import App
    app = App(data_dir=DATA_DIR, config_path=CONFIG_PATH)
    app.run()


if __name__ == "__main__":
    main()
