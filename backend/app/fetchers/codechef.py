"""
CodeChef fetcher.

IMPORTANT - read this before wiring CodeChef into the scheduler:

CodeChef has no official public API at all (unlike Codeforces) and no
reliable authenticated GraphQL-style endpoint (unlike LeetCode). Every
"CodeChef API" you'll find on GitHub is a scraper of the HTML profile
page or of an internal endpoint the website itself uses - and both
break whenever CodeChef changes its frontend, without warning.

Two data sources were evaluated for this file:

1. Profile page (https://www.codechef.com/users/<handle>) - a `<script>`
   tag or embedded state on that page includes `problem_fully_solved`
   / `problem_partially_solved` *counts* and a rating. Good for a
   totals sanity-check, but has no per-problem list or timestamps.

2. `https://www.codechef.com/recent/user?page=N&user_handle=<handle>`
   - an internal endpoint the profile page itself calls to render the
     "Recent Activity" feed. This DOES return individual solve-like
     entries with a problem code and a time, paginated - closest thing
     CodeChef has to Codeforces' user.status. It is undocumented,
     unofficial, and can rate-limit or change shape at any time.

Given that, this fetcher implements (2) as the primary path, but:
  - Treat every field name below as "verify against a live response
    before depending on it" - CodeChef can and does change this.
  - Wrap every call site in try/except (the sync route below already
    does) so a CodeChef breakage never takes down Codeforces/LeetCode
    syncing.
  - Consider this fetcher a "best effort, patch as needed" starting
    point rather than a finished, stable integration - which is
    exactly what the project spec asks for ("do not scrape blindly",
    "first determine the current reliable data source").
"""

import re

import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CodeTrack/1.0)"}


def fetch_profile_summary(handle: str) -> dict:
    """
    Scrapes https://www.codechef.com/users/<handle> for total solved
    counts and current rating. No per-problem data, no timestamps -
    useful only as a cross-check against what the recent-activity feed
    (below) has accumulated over time.
    """
    url = f"https://www.codechef.com/users/{handle}"
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    html = response.text

    def _search_int(pattern):
        m = re.search(pattern, html)
        return int(m.group(1)) if m else None

    return {
        "handle": handle,
        "problems_fully_solved": _search_int(r'Total Problems Solved\s*:\s*(\d+)') or
                                   _search_int(r'"problem_fully_solved"\s*:\s*(\d+)'),
        "rating": _search_int(r'"rating"\s*:\s*(\d+)'),
    }


def fetch_recent_activity(handle: str, max_pages: int = 20) -> list[dict]:
    """
    Paginates the internal /recent/user feed. Each returned dict is
    expected to look roughly like:
        {"code": "TWOTRAINS", "time": "2026-08-01 10:15:00", ...}
    but VERIFY the actual JSON shape against a live response first
    (curl the URL below with your own handle) - the field names here
    are a best-effort based on how this endpoint has looked
    historically, not a guarantee of the current shape.
    """
    url = "https://www.codechef.com/recent/user"
    all_entries = []

    for page in range(max_pages):
        response = requests.get(
            url,
            params={"page": page, "user_handle": handle},
            headers=HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        entries = data.get("content") or data.get("data") or []
        if not entries:
            break

        all_entries.extend(entries)

    return all_entries
