# CodeTrack

A coding-progress analytics platform that tracks **uniquely solved
problems** (not submissions) across Codeforces, LeetCode, and
CodeChef.

## What's in this update

Starting from the working Codeforces ingestion pipeline (5,467
submissions → 3,027 unique solves, verified), this build finishes the
MVP described in the project spec:

- **Bug fixes**: `app/__inti__.py` → `__init__.py`; the SQLite path was
  relative (`./data/codetrack.db`), which broke depending on your
  current directory — now absolute; `difficulty` was hardcoded to
  `None` even though Codeforces gives a rating to bucket from; and
  `leetcode_username`/`codechef_username` had a DB-level `unique=True`
  that would break the moment a second user left them blank.
- **Analytics** (`app/repositories/analytics_repository.py` +
  `app/services/analytics_service.py`): total / today / this week /
  this month / this year, daily / monthly / yearly breakdowns,
  platform-wise, difficulty-wise, rating distribution — all derived
  strictly from `first_solved_at`, never from submission counts.
- **Streaks**: current + longest streak.
- **Dashboard endpoint**: `GET /api/dashboard`.
- **17 pytest tests** (`backend/tests/`) covering every "critical
  case" from the spec (duplicate Accepted submissions, cross-day,
  cross-month, cross-year, sync idempotency, DB-level uniqueness) —
  run with an isolated in-memory DB, never touching your real data.
- **Rating history**: new `RatingHistory` model + Codeforces rating
  sync (`POST /api/sync/codeforces/rating`) + `GET
  /api/analytics/rating-history`.
- **LeetCode fetcher**: works, with an honest limitation documented in
  `docs/leetcode.md` — LeetCode's public API only exposes your last
  ~20 accepted submissions without logging in.
- **CodeChef fetcher**: best-effort scraper, documented as fragile in
  `docs/codechef.md` — CodeChef has no official API at all.
- **Automatic + incremental sync**: `app/services/scheduler.py` runs a
  daily job; `SyncState` + `fetch_submissions_incremental()` mean it
  doesn't re-download your entire Codeforces history every night.
- **React dashboard** (`frontend/`): summary cards, a commit-graph-style
  activity heatmap, platform/difficulty breakdowns, monthly trend
  chart, and a manual "sync" button.
- **Config via `.env`**: usernames, DB path, timezone, CORS origins —
  see `backend/.env.example`.

## Project structure

```
CodeTrack/
├── backend/
│   ├── app/
│   │   ├── main.py                 FastAPI app, CORS, scheduler lifespan
│   │   ├── config.py                .env-driven settings
│   │   ├── dependencies.py          get_current_user, get_db
│   │   ├── schemas.py               Pydantic response models
│   │   ├── database/
│   │   │   ├── database.py
│   │   │   └── models.py            User, Problem, SolvedProblem,
│   │   │                            RatingHistory, SyncState
│   │   ├── fetchers/
│   │   │   ├── codeforces.py        submissions, rating, incremental fetch
│   │   │   ├── leetcode.py          recent AC list, per-slug backfill
│   │   │   └── codechef.py          profile scrape, recent-activity scrape
│   │   ├── services/
│   │   │   ├── submission_processor.py   raw → unique solved problems
│   │   │   ├── sync_service.py           sync_platform() (generic)
│   │   │   ├── analytics_service.py      date ranges, streaks, dashboard
│   │   │   ├── rating_service.py         CF rating sync
│   │   │   └── scheduler.py              daily background job
│   │   ├── repositories/
│   │   │   ├── problem_repository.py
│   │   │   ├── solve_event_repository.py
│   │   │   ├── analytics_repository.py   first_solved_at queries only
│   │   │   ├── rating_repository.py
│   │   │   └── sync_state_repository.py
│   │   └── routes/
│   │       ├── dashboard.py
│   │       ├── analytics.py
│   │       └── sync.py
│   ├── tests/                       pytest suite, isolated in-memory DB
│   ├── data/codetrack.db            your real data (untouched)
│   ├── .env.example
│   └── requirements.txt
├── frontend/                        React + Vite + recharts dashboard
├── docs/
│   ├── leetcode.md
│   └── codechef.md
└── README.md
```

## Setup

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: set CODEFORCES_USERNAME to your own handle,
# and APP_TIMEZONE if you're not in UTC (e.g. Asia/Kolkata)

uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs
- Trigger a sync: `curl -X POST http://127.0.0.1:8000/api/sync/codeforces`
- Check the dashboard: `curl http://127.0.0.1:8000/api/dashboard`

Run the tests:

```bash
cd backend
python3 -m pytest tests/ -v
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_URL=http://127.0.0.1:8000
npm run dev
```

Open http://localhost:5173. Click **sync codeforces** to pull fresh
data, or hit the API endpoint directly as shown above.

## API reference

| Endpoint | Description |
|---|---|
| `GET /api/dashboard` | Summary numbers matching spec section 33 |
| `GET /api/analytics/daily?days=N` | Daily new-solve counts |
| `GET /api/analytics/monthly` | Monthly new-solve counts |
| `GET /api/analytics/yearly` | Yearly new-solve counts |
| `GET /api/analytics/platforms` | Solved count per platform |
| `GET /api/analytics/difficulty` | Solved count per difficulty |
| `GET /api/analytics/rating-distribution` | Solved count per CF rating bucket |
| `GET /api/analytics/streak` | Current + longest streak |
| `GET /api/analytics/heatmap` | Date to count, for a calendar heatmap |
| `GET /api/analytics/rating-history?platform=` | Rating time series |
| `POST /api/sync/codeforces` | Full Codeforces sync |
| `POST /api/sync/codeforces/rating` | Codeforces rating sync |
| `POST /api/sync/leetcode` | LeetCode sync (recent ~20 only, see docs/leetcode.md) |

## Automatic sync

The scheduler starts automatically with the app (see the `lifespan`
context in `app/main.py`) and runs `run_daily_sync()` once a day at
03:00 server time by default. It:

1. Reads each user's `SyncState.last_submission_id` for Codeforces.
2. Fetches only submissions newer than that (paginated, stops early).
3. Runs them through the same `submission_processor` -> `sync_platform`
   pipeline as a manual sync.
4. Updates `SyncState` with the newest submission id seen.
5. Syncs Codeforces rating history too.

LeetCode and CodeChef are **not** auto-scheduled by default. Read
`docs/leetcode.md` and `docs/codechef.md` first, then uncomment the
relevant block in `app/services/scheduler.py::run_daily_sync()` once
you've validated those fetchers against your own account.

Change the schedule time via `start_scheduler(hour=, minute=)` in
`app/main.py`, or swap `CronTrigger` for `IntervalTrigger` if you'd
rather sync every N hours.

## What to do next

The spec's own recommended order (section 44) still applies from
here:

1. Analytics repository/service/API - done, tested.
2. React dashboard - done (`frontend/`).
3. Rating history - Codeforces done; LeetCode/CodeChef rating
   history isn't wired up (both platforms make this harder - LeetCode
   contest rating needs a different, separate query; CodeChef rating
   is on the profile page you're already scraping for `docs/codechef.md`).
4. **LeetCode** - validate `docs/leetcode.md`'s backfill path against
   your own account if you want full history, otherwise the recent-20
   default is already live.
5. **CodeChef** - follow the checklist in `docs/codechef.md` before
   trusting it with real data.
6. **Alembic migrations** - `Base.metadata.create_all()` is still
   doing schema creation, same as before. Fine for solo/dev use;
   worth adding once the schema stabilizes and you don't want to lose
   data on a schema change.
7. **Pydantic request/response schemas everywhere** - the analytics
   and sync routes have them (`app/schemas.py`); the internal
   normalized-problem dicts passed between fetcher -> processor -> sync
   are still plain dicts, which matches how the original codebase was
   written (spec section 42 lists this as a "recommended" cleanup, not
   a blocker).
