import json
import re
import hashlib
import secrets
from datetime import datetime
from config import USERS_FILE, DATA_DIR


def _ensure_users_file():
    DATA_DIR.mkdir(exist_ok=True)

    if not USERS_FILE.exists():
        USERS_FILE.write_text("[]", encoding="utf-8")


def _load_users():
    _ensure_users_file()

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def _save_users(users):
    _ensure_users_file()

    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=4)


def _hash_password(password, salt):
    value = f"{password}{salt}".encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def _is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


def sign_up(email, password):
    email = email.lower().strip()

    if not _is_valid_email(email):
        return {
            "success": False,
            "message": "Please enter a valid email address."
        }

    if len(password) < 6:
        return {
            "success": False,
            "message": "Password must contain at least 6 characters."
        }

    users = _load_users()

    for user in users:
        if user["email"] == email:
            return {
                "success": False,
                "message": "This email is already registered."
            }

    salt = secrets.token_hex(16)
    password_hash = _hash_password(password, salt)

    new_user = {
        "id": secrets.token_hex(8),
        "email": email,
        "salt": salt,
        "password_hash": password_hash,
        "created_at": datetime.now().isoformat()
    }

    users.append(new_user)
    _save_users(users)

    return {
        "success": True,
        "message": "Account created successfully.",
        "user": {
            "id": new_user["id"],
            "email": new_user["email"]
        }
    }


def sign_in(email, password):
    email = email.lower().strip()

    users = _load_users()

    for user in users:
        if user["email"] == email:
            password_hash = _hash_password(password, user["salt"])

            if password_hash == user["password_hash"]:
                return {
                    "success": True,
                    "message": "Signed in successfully.",
                    "user": {
                        "id": user["id"],
                        "email": user["email"]
                    }
                }

            return {
                "success": False,
                "message": "Incorrect password."
            }

    return {
        "success": False,
        "message": "No account found with this email."
    }