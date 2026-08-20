from sqlalchemy.orm import Session

from app.database.models import Problem


def _build_url(problem_data: dict) -> str:
    """
    Fallback URL builder for platforms (like Codeforces) that don't
    hand us a ready-made URL. Other platforms should just set "url"
    directly in their normalized problem dict.
    """
    platform = problem_data.get("platform")

    if platform == "codeforces" and problem_data.get("contest_id") and problem_data.get("index"):
        return f"https://codeforces.com/problemset/problem/{problem_data['contest_id']}/{problem_data['index']}"

    return ""


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
        difficulty=problem_data.get("difficulty"),
        rating=problem_data.get("rating"),
        url=problem_data.get("url") or _build_url(problem_data),
    )

    db.add(problem)
    db.flush()      # Gives us problem.id without committing

    return problem