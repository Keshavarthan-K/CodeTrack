import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "CodeTrack")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./data/codetrack.db",
    )

    codeforces_username: str = os.getenv(
        "CODEFORCES_USERNAME",
        "",
    )

    leetcode_username: str = os.getenv(
        "LEETCODE_USERNAME",
        "",
    )

    codechef_username: str = os.getenv(
        "CODECHEF_USERNAME",
        "",
    )


settings = Settings()