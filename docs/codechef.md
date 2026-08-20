# CodeChef integration notes

## Reality check first

CodeChef has **no official public API**. Everything in
`app/fetchers/codechef.py` talks to either:

- the public profile page HTML (`codechef.com/users/<handle>`), or
- an internal, undocumented endpoint the profile page itself calls
  (`codechef.com/recent/user`) to render the "Recent Activity" feed.

Both can change or break without notice - there's no changelog to
watch. Treat this fetcher as a starting point you'll need to patch,
not a finished integration.

## Before you rely on it

1. Run `fetch_recent_activity("your_handle")` from a Python shell and
   print the raw JSON. Confirm the field names (`code`, `time`, etc.)
   match what `extract_unique_solved_problems_codechef` expects in
   `app/services/submission_processor.py`. Adjust the field lookups if
   CodeChef's response shape has changed.
2. Confirm what a *non-accepted* submission looks like in that feed
   (partial credit / wrong answer). The current stub assumes every
   entry passed in is already a solve, which is only true if
   `/recent/user` only ever reports successes - verify this for your
   account before trusting it.
3. Watch for rate limiting - this endpoint isn't meant for
   programmatic polling. Don't schedule it more than once a day, and
   back off entirely if you start getting non-200 responses.

## Why it's not in the automatic scheduler by default

`app/services/scheduler.py` deliberately leaves CodeChef (and
LeetCode) commented out of the daily job. Codeforces has a real,
documented, stable API and is safe to run unattended. CodeChef isn't,
yet - wire it in once you've validated step 1-3 above against your own
account and you're comfortable with the failure mode (a broken
CodeChef sync should never be allowed to raise past the try/except in
`run_daily_sync()` and take Codeforces syncing down with it - the
current code already guards this, just don't remove that guard).
