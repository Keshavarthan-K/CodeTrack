"""
Central configuration for CodeTrack.

Everything environment-specific (usernames, DB path, secrets) is read
from environment variables / a .env file here, instead of being
hardcoded across the codebase. Copy `.env.example` to `.env` and fill
in your own values.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# backend/
BACKEND_DIR = Path(__file__).resolve().parent.parent

# Load backend/.env if present (safe no-op if the file doesn't exist)
load_dotenv(BACKEND_DIR / ".env")


def _get_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


class Settings:
    # --- Database -----------------------------------------------------
    # Always an absolute path so it doesn't matter which directory you
    # run `uvicorn` from.
    DATABASE_PATH: Path = Path(
        os.getenv("DATABASE_PATH", str(BACKEND_DIR / "data" / "codetrack.db"))
    )
    DATABASE_URL: str = f"sqlite:///{DATABASE_PATH}"
    SQL_ECHO: bool = _get_bool("SQL_ECHO", False)

    # --- Platform usernames (the account CodeTrack tracks) ------------
    CODEFORCES_USERNAME: str = os.getenv("CODEFORCES_USERNAME", "tourist")
    LEETCODE_USERNAME: str = os.getenv("LEETCODE_USERNAME", "")
    CODECHEF_USERNAME: str = os.getenv("CODECHEF_USERNAME", "")

    # --- Optional LeetCode authentication (needed for a *full* solve
    # history sync; without it only the last ~20 accepted submissions
    # are visible). See docs/leetcode.md for how to obtain these.
    LEETCODE_SESSION: str = os.getenv("LEETCODE_SESSION", "")
    LEETCODE_CSRF_TOKEN: str = os.getenv("LEETCODE_CSRF_TOKEN", "")

    # --- Analytics ---------------------------------------------------
    # "today" / "this week" / "this month" boundaries are computed in
    # this timezone, then converted to UTC to match how
    # first_solved_at is stored. Use an IANA name, e.g. "Asia/Kolkata".
    APP_TIMEZONE: str = os.getenv("APP_TIMEZONE", "UTC")

    # --- App -------------------------------------------------------
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    ]
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
