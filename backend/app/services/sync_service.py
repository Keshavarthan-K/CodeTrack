from app.repositories.problem_repository import (
    get_problem,
    create_problem,
)

from app.repositories.solve_event_repository import (
    get_solve_event,
    create_solve_event,
)


def sync_platform(
    db,
    user,
    solved_problems,
):
    """
    Generic sync for a normalized list of solved-problem dicts from
    any platform's fetcher+processor. Works because the dicts already
    conform to the same internal shape (see submission_processor.py /
    docs section "Normalized Internal Data").
    """
    created_problems = 0
    created_solves = 0

    for problem_data in solved_problems:

        problem = get_problem(
            db,
            problem_data["platform"],
            problem_data["platform_problem_id"],
        )

        if problem is None:
            problem = create_problem(
                db,
                problem_data,
            )
            created_problems += 1

        solve = get_solve_event(
            db,
            user.id,
            problem.id,
        )

        if solve is None:
            create_solve_event(
                db,
                user.id,
                problem.id,
                problem_data,
            )

            created_solves += 1

    db.commit()

    return {
        "new_problems": created_problems,
        "new_solves": created_solves,
    }


# Backwards-compatible alias - existing scripts (test_sync.py) import
# sync_codeforces specifically, and the name still reads fine since
# Codeforces was the first platform wired up.
sync_codeforces = sync_platform