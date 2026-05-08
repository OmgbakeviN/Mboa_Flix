from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"

USERS_FILE = DATA_DIR / "users.json"

APP_NAME = "Mboa Flix"
WINDOW_SIZE = "1100x680"

COLORS = {
    "background": "#050505",
    "surface": "#111111",
    "surface_light": "#1c1c1c",
    "primary": "#E50914",
    "primary_hover": "#F6121D",
    "secondary": "#2d2d2d",
    "text": "#FFFFFF",
    "muted": "#B3B3B3",
    "error": "#FF5A5F",
    "success": "#36D399",
}