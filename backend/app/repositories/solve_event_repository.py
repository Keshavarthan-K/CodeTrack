from sqlalchemy.orm import Session

from app.database.models import SolvedProblem


def get_solve_event(
    db: Session,
    user_id: int,
    problem_id: int,
):
    return (
        db.query(SolvedProblem)
        .filter(
            SolvedProblem.user_id == user_id,
            SolvedProblem.problem_id == problem_id,
        )
        .first()
    )


def create_solve_event(
    db: Session,
    user_id: int,
    problem_id: int,
    problem_data: dict,
):
    solve = SolvedProblem(
        user_id=user_id,
        problem_id=problem_id,
        first_solved_at=problem_data["first_solved_at"],
        language=problem_data["language"],
    )

    db.add(solve)

    return solve