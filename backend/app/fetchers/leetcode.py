"""
LeetCode fetcher.

IMPORTANT - read this before wiring LeetCode into the scheduler:

LeetCode has no official public API, and unlike Codeforces, its
unauthenticated GraphQL endpoint does NOT expose a user's full
accepted-submission history. Verified while building this file
(Aug 2026):

  Without login (`https://leetcode.com/graphql`):
    - `recentAcSubmissionList(username, limit)` -> last ~20 accepted
      submissions only, each with a real timestamp. Good for topping
      up "what did I solve recently", not for a full backfill.
    - `matchedUser.submitStatsGlobal.acSubmissionNum` -> total solved
      counts per difficulty (Easy/Medium/Hard), but NO timestamps and
      NO per-problem list.

  With login (LEETCODE_SESSION + csrftoken cookies from your browser):
    - `submissionList(offset, limit, lastKey, questionSlug)` returns
      submissions, but *scoped to one questionSlug at a time* - there
      is no authenticated global "give me every submission" feed
      equivalent to Codeforces' user.status. To backfill full history
      you'd fetch your solved-question slugs first, then call this
      per-slug (see fetch_first_ac_for_slug below) - one request per
      solved problem. That's ~1 request per problem you've solved,
      which is fine for a personal sync but budget for rate limiting.

Because of this, the MVP here defaults to the safe, unauthenticated
"recent submissions" mode, which is correct as far as it goes (every
timestamp it returns is real) but won't have your full LeetCode
history on first sync - only the most recent ~20 solves. Re-running it
periodically (e.g. daily, via the scheduler) will gradually catch
everything you solve *going forward*, but a true backfill needs the
authenticated per-slug path.

If LeetCode changes this API (it has before - see the module-level
warning this docstring itself is repeating), fix it here; nothing
above app.fetchers should ever need to know how LeetCode's data is
actually shaped, since submission_processor.py normalizes it into the
same internal representation Codeforces uses.
"""

import requests

GRAPHQL_URL = "https://leetcode.com/graphql"

RECENT_AC_QUERY = """
query recentAcSubmissions($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    id
    title
    titleSlug
    timestamp
  }
}
"""

USER_STATS_QUERY = """
query userStats($username: String!) {
  matchedUser(username: $username) {
    submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
      }
    }
  }
}
"""

SUBMISSION_LIST_QUERY = """
query submissionList($offset: Int!, $limit: Int!, $lastKey: String, $questionSlug: String!) {
  submissionList(offset: $offset, limit: $limit, lastKey: $lastKey, questionSlug: $questionSlug) {
    lastKey
    hasNext
    submissions {
      id
      statusDisplay
      timestamp
      lang
    }
  }
}
"""


def _post(query: str, variables: dict, cookies: dict | None = None) -> dict:
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}

    response = requests.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables},
        headers=headers,
        cookies=cookies,
        timeout=10,
    )
    response.raise_for_status()

    payload = response.json()
    if payload.get("errors"):
        raise Exception(f"LeetCode GraphQL error: {payload['errors']}")

    return payload["data"]


def fetch_recent_accepted_submissions(username: str, limit: int = 20) -> list[dict]:
    """
    Unauthenticated. Returns up to `limit` (LeetCode caps this around
    20) of the user's most recent Accepted submissions, each with a
    real timestamp. Safe default sync path - see module docstring.
    """
    data = _post(RECENT_AC_QUERY, {"username": username, "limit": limit})
    return data["recentAcSubmissionList"]


def fetch_solved_counts_by_difficulty(username: str) -> dict:
    """Unauthenticated. {"Easy": n, "Medium": n, "Hard": n} totals (no timestamps)."""
    data = _post(USER_STATS_QUERY, {"username": username})
    counts = {"Easy": 0, "Medium": 0, "Hard": 0}
    for entry in data["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]:
        if entry["difficulty"] in counts:
            counts[entry["difficulty"]] = entry["count"]
    return counts


def fetch_first_ac_for_slug(
    question_slug: str,
    session_cookie: str,
    csrf_token: str,
) -> dict | None:
    """
    Authenticated. Paginates through the logged-in user's submission
    history for ONE problem and returns the oldest Accepted one (i.e.
    the true first solve), or None if never accepted.

    Requires LEETCODE_SESSION and csrftoken cookies from a logged-in
    browser session (see .env.example / docs/leetcode.md). These
    typically expire after about a week, so this is meant for an
    occasional manual "full backfill" run, not the daily scheduler.
    """
    cookies = {"LEETCODE_SESSION": session_cookie, "csrftoken": csrf_token}

    offset = 0
    last_key = ""
    oldest_accepted = None

    while True:
        data = _post(
            SUBMISSION_LIST_QUERY,
            {"offset": offset, "limit": 20, "lastKey": last_key, "questionSlug": question_slug},
            cookies=cookies,
        )
        result = data["submissionList"]

        for sub in result["submissions"]:
            if sub["statusDisplay"] == "Accepted":
                oldest_accepted = sub  # keep overwriting; last one seen is oldest (list is newest -> oldest)

        if not result["hasNext"]:
            break

        offset += 20
        last_key = result["lastKey"]

    return oldest_accepted
