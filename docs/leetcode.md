# LeetCode integration notes

## Two sync modes

**Default (no login needed):** `POST /api/sync/leetcode` calls
`fetch_recent_accepted_submissions`, which uses LeetCode's public
GraphQL endpoint. This is safe to run on a schedule but only ever sees
your **last ~20 accepted submissions** - LeetCode does not expose a
full history without logging in. Run it regularly (e.g. daily) and it
will gradually catch everything you solve *going forward*; it will not
retroactively backfill problems solved before you started running it.

**Full backfill (optional, manual):** `fetch_first_ac_for_slug()` in
`app/fetchers/leetcode.py` can get the true first-AC timestamp for a
specific problem, authenticated as you. To use it for a one-time full
backfill of your existing LeetCode history, you'd:

1. Get your list of solved problem slugs (LeetCode's own site shows
   this under your profile's "Solved" tab; there's also a
   `matchedUser.submitStats` + problem-list-with-status query if you
   want to script it - check the current GraphQL schema, since exact
   field names shift over time).
2. Call `fetch_first_ac_for_slug(slug, session, csrf)` once per slug.
3. Feed the results through the same normalization shape used in
   `extract_unique_solved_problems_leetcode` and pass them to
   `sync_platform()`.

This isn't wired into an endpoint by default because it's a slower,
one-request-per-problem operation you'd run occasionally, not
something to schedule nightly.

## Getting LEETCODE_SESSION and csrftoken

1. Log into leetcode.com in your browser.
2. Open DevTools → Application (Chrome) or Storage (Firefox) → Cookies
   → `https://leetcode.com`.
3. Copy the values of `LEETCODE_SESSION` and `csrftoken`.
4. Put them in `backend/.env`:
   ```
   LEETCODE_SESSION=...
   LEETCODE_CSRF_TOKEN=...
   ```

These cookies typically expire in about a week, so this is meant for
occasional manual backfills, not a permanently-configured credential.

## If LeetCode changes its API again

It will, eventually - this endpoint isn't official or documented, and
has changed shape before. When it does: only `app/fetchers/leetcode.py`
needs to change. `submission_processor.py`, `sync_service.py`, and
everything downstream only care about the normalized dict shape (see
spec section 37), not where the data came from.
