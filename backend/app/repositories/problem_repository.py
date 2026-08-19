from sqlalchemy.orm import Session

from app.database.models import Problem


def get_problem(
    db: Session,
    platform: str,
    platform_problem_id: str,
):
    return (
        db.query(Problem)
        .filter(
            Problem.platform == platform,
            Problem.platform_problem_id == platform_problem_id,
        )
        .first()
    )


def create_problem(
    db: Session,
    problem_data: dict,
):
    problem = Problem(
        platform=problem_data["platform"],
        platform_problem_id=problem_data["platform_problem_id"],
        title=problem_data["title"],
        difficulty=None,
        rating=problem_data["rating"],
        url=f"https://codeforces.com/problemset/problem/{problem_data['contest_id']}/{problem_data['index']}",
    )

    db.add(problem)
    db.flush()      # Gives us problem.id without committing

    return problem