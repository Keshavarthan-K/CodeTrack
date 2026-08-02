from app.fetchers.codeforces import fetch_submissions
from app.services.submission_processor import extract_unique_solved_problems

submissions = fetch_submissions("tourist")

problems = extract_unique_solved_problems(submissions)

print(f"Submissions : {len(submissions)}")
print(f"Solved      : {len(problems)}")

print()

print()

for p in problems[:10]:
    print(
        p["platform_problem_id"],
        p["title"],
        p["first_solved_at"],
    )