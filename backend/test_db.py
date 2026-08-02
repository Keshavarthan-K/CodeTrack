from app.database.database import SessionLocal
from app.repositories.problem_repository import (
    get_problem,
    create_problem,
)

db = SessionLocal()

problem = get_problem(
    db,
    "codeforces",
    "9999-A"
)

if problem is None:

    problem = create_problem(
        db,
        {
            "platform": "codeforces",
            "platform_problem_id": "9999-A",
            "contest_id": 9999,
            "index": "A",
            "title": "Test Problem",
            "rating": 800,
        }
    )

print(problem.id)
print(problem.title)

db.close()