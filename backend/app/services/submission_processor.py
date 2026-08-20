from datetime import datetime, UTC


def difficulty_from_cf_rating(rating):
    """
    Codeforces doesn't label problems Easy/Medium/Hard directly - it
    only gives a numeric rating. Bucket it so the rest of CodeTrack
    (difficulty-wise analytics, dashboard charts) has a consistent
    Easy/Medium/Hard concept across all three platforms.

    Boundaries are a reasonable default and easy to retune later.
    """
    if rating is None:
        return None
    if rating < 1400:
        return "Easy"
    if rating < 2100:
        return "Medium"
    return "Hard"


def extract_unique_solved_problems_leetcode(recent_ac_submissions: list[dict]) -> list[dict]:
    """
    Normalizes LeetCode's recentAcSubmissionList (already Accepted-only,
    already newest -> oldest) into CodeTrack's internal shape. Because
    LeetCode's public API caps this list at ~20, this only surfaces
    recent solves - see app/fetchers/leetcode.py docstring for the
    full explanation and the authenticated backfill path.
    """
    solved = {}

    for submission in reversed(recent_ac_submissions):  # oldest -> newest, same convention as CF
        slug = submission["titleSlug"]

        if slug in solved:
            continue

        solved[slug] = {
            "platform": "leetcode",
            "platform_problem_id": slug,
            "title": submission["title"],
            "url": f"https://leetcode.com/problems/{slug}/",
            "rating": None,
            "difficulty": None,  # not present on this query; see fetchers/leetcode.py
            "tags": [],
            "language": None,
            "first_solved_at": datetime.fromtimestamp(int(submission["timestamp"]), UTC),
        }

    return list(solved.values())


def extract_unique_solved_problems_codechef(recent_activity: list[dict]) -> list[dict]:
    """
    Normalizes CodeChef's /recent/user feed into CodeTrack's internal
    shape. STUB - the field names below (`code`, `time`) are best-guess
    based on how that endpoint has historically looked; confirm them
    against a real response for your handle before relying on this
    (see app/fetchers/codechef.py docstring). Filter down to
    accepted-only entries once you've confirmed what a non-accepted
    entry looks like in a live payload - this stub assumes every
    entry passed in is already a solve.
    """
    solved = {}

    for entry in reversed(recent_activity):  # assume newest -> oldest, like CF/LeetCode
        code = entry.get("code") or entry.get("problem_code")
        if not code or code in solved:
            continue

        raw_time = entry.get("time") or entry.get("timestamp")
        if raw_time is None:
            continue

        try:
            solved_at = datetime.fromisoformat(str(raw_time)).replace(tzinfo=UTC)
        except ValueError:
            continue

        solved[code] = {
            "platform": "codechef",
            "platform_problem_id": code,
            "title": entry.get("name", code),
            "url": f"https://www.codechef.com/problems/{code}",
            "rating": None,
            "difficulty": None,
            "tags": [],
            "language": entry.get("language"),
            "first_solved_at": solved_at,
        }

    return list(solved.values())


def extract_unique_solved_problems(submissions):
    solved = {}

    # Codeforces returns newest -> oldest
    # Reverse so we process oldest -> newest

    for submission in reversed(submissions):

        if submission.get("verdict") != "OK":
            continue

        problem = submission["problem"]

        key = (
            problem["contestId"],
            problem["index"]
        )

        if key in solved:
            continue

        rating = problem.get("rating")

        solved[key] = {
            "platform": "codeforces",
            "platform_problem_id": f'{problem["contestId"]}-{problem["index"]}',
            "contest_id": problem["contestId"],
            "index": problem["index"],
            "title": problem["name"],
            "rating": rating,
            "difficulty": difficulty_from_cf_rating(rating),
            "tags": problem.get("tags", []),
            "language": submission["programmingLanguage"],
            "first_solved_at": datetime.fromtimestamp(
                submission["creationTimeSeconds"],
                UTC,
            ),
        }

    return list(solved.values())