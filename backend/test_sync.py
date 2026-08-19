from app.database.database import SessionLocal
from app.database.models import User

from app.fetchers.codeforces import fetch_submissions
from app.services.submission_processor import (
    extract_unique_solved_problems,
)
from app.services.sync_service import sync_codeforces


db = SessionLocal()

user = (
    db.query(User)
    .filter(User.codeforces_username == "tourist")
    .first()
)

if user is None:

    user = User(
        name="Tourist",
        leetcode_username="",
        codeforces_username="tourist",
        codechef_username="",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

print("Fetching submissions...")

submissions = fetch_submissions("tourist")

print(f"Fetched {len(submissions)} submissions")

print("Processing...")

problems = extract_unique_solved_problems(submissions)

print(f"Unique solved problems : {len(problems)}")

print("Syncing...")

stats = sync_codeforces(
    db,
    user,
    problems,
)

print()

print("Sync completed")

print(stats)

db.close()