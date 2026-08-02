from datetime import datetime, UTC


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

        solved[key] = {
            "platform": "codeforces",
            "platform_problem_id": f'{problem["contestId"]}-{problem["index"]}',
            "contest_id": problem["contestId"],
            "index": problem["index"],
            "title": problem["name"],
            "rating": problem.get("rating"),
            "tags": problem.get("tags", []),
            "language": submission["programmingLanguage"],
            "first_solved_at": datetime.fromtimestamp(
                submission["creationTimeSeconds"],
                UTC,
            ),
        }

    return list(solved.values())