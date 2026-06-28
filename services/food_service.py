import json
from config import DATA_DIR

FOODS_FILE = DATA_DIR / "foods.json"


def load_foods():
    if not FOODS_FILE.exists():
        return []

    try:
        with open(FOODS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []