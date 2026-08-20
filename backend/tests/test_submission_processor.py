"""
Spec section 43, Case 1:

    WA
    WA
    OK
    OK
    OK

Expected: 1 solved problem, not 3, and not 5.
"""

from app.services.submission_processor import extract_unique_solved_problems


def _submission(verdict, ts, problem=None):
    return {
        "verdict": verdict,
        "creationTimeSeconds": ts,
        "programmingLanguage": "GNU C++20",
        "problem": problem or {
            "contestId": 1,
            "index": "A",
            "name": "Theatre Square",
            "rating": 1000,
            "tags": ["math"],
        },
    }


def test_duplicate_accepted_submissions_count_once():
    # Codeforces returns newest -> oldest.
    submissions = [
        _submission("OK", 5000),
        _submission("OK", 4000),
        _submission("OK", 3000),
        _submission("WRONG_ANSWER", 2000),
        _submission("WRONG_ANSWER", 1000),
    ]

    solved = extract_unique_solved_problems(submissions)

    assert len(solved) == 1
    assert solved[0]["platform_problem_id"] == "1-A"


def test_only_ok_verdict_counts_as_solved():
    verdicts = [
        "WRONG_ANSWER",
        "TIME_LIMIT_EXCEEDED",
        "MEMORY_LIMIT_EXCEEDED",
        "RUNTIME_ERROR",
        "COMPILATION_ERROR",
    ]
    submissions = [_submission(v, 1000 + i) for i, v in enumerate(verdicts)]

    solved = extract_unique_solved_problems(submissions)

    assert solved == []


def test_first_accepted_submission_timestamp_is_kept():
    # Oldest AC is the true first solve, even though newer ACs exist.
    submissions = [
        _submission("OK", 3_000_000),  # newest
        _submission("OK", 2_000_000),
        _submission("OK", 1_000_000),  # oldest -> true first solve
    ]

    solved = extract_unique_solved_problems(submissions)

    assert len(solved) == 1
    assert solved[0]["first_solved_at"].timestamp() == 1_000_000


def test_multiple_distinct_problems_each_count():
    submissions = [
        _submission("OK", 1000, problem={"contestId": 1, "index": "A", "name": "P1", "rating": 800, "tags": []}),
        _submission("OK", 1100, problem={"contestId": 1, "index": "B", "name": "P2", "rating": 900, "tags": []}),
        _submission("WRONG_ANSWER", 1200, problem={"contestId": 1, "index": "A", "name": "P1", "rating": 800, "tags": []}),
    ]

    solved = extract_unique_solved_problems(submissions)

    assert len(solved) == 2
    ids = {p["platform_problem_id"] for p in solved}
    assert ids == {"1-A", "1-B"}
