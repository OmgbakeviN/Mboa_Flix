import json
from copy import deepcopy
from pathlib import Path

from config import BASE_DIR, DATA_DIR

MOVIES_FILE = DATA_DIR / "movies.json"

EMPTY_CATALOG = {
    "top_movies": [],
    "categories": []
}


def _ensure_movies_file():
    DATA_DIR.mkdir(exist_ok=True)

    if not MOVIES_FILE.exists():
        MOVIES_FILE.write_text(
            json.dumps(EMPTY_CATALOG, indent=4),
            encoding="utf-8"
        )


def load_catalog():
    _ensure_movies_file()

    try:
        with open(MOVIES_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        data = deepcopy(EMPTY_CATALOG)

    data.setdefault("top_movies", [])
    data.setdefault("categories", [])

    return data


def get_featured_movie(catalog=None):
    catalog = catalog or load_catalog()

    if catalog.get("top_movies"):
        return catalog["top_movies"][0]

    for category in catalog.get("categories", []):
        movies = category.get("movies", [])
        if movies:
            return movies[0]

    return None


def search_catalog(query):
    catalog = load_catalog()
    query = query.strip().lower()

    if not query:
        return catalog

    def matches(movie):
        searchable_values = [
            movie.get("title", ""),
            movie.get("category", ""),
            movie.get("type", ""),
            movie.get("year", ""),
            movie.get("description", ""),
            " ".join(movie.get("tags", []))
        ]

        searchable_text = " ".join(
            str(value).lower() for value in searchable_values
        )

        return query in searchable_text

    filtered_catalog = {
        "top_movies": [
            movie for movie in catalog.get("top_movies", [])
            if matches(movie)
        ],
        "categories": []
    }

    for category in catalog.get("categories", []):
        movies = [
            movie for movie in category.get("movies", [])
            if matches(movie)
        ]

        if movies:
            filtered_catalog["categories"].append({
                "id": category.get("id"),
                "title": category.get("title"),
                "movies": movies
            })

    return filtered_catalog


def resolve_media_path(path_value):
    if not path_value:
        return None

    path_value = str(path_value).strip()

    if path_value.startswith("http://") or path_value.startswith("https://"):
        return None

    path = Path(path_value)
    candidate = path if path.is_absolute() else BASE_DIR / path

    if candidate.exists():
        return candidate

    return None