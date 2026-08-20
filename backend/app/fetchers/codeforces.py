import requests

BASE_URL = "https://codeforces.com/api"


def fetch_submissions(handle: str):
    url = f"{BASE_URL}/user.status?handle={handle}"

    response = requests.get(url, timeout=10)

    response.raise_for_status()

    data = response.json()

    if data["status"] != "OK":
        raise Exception(data["comment"])

    return data["result"]


def fetch_submissions_incremental(
    handle: str,
    last_submission_id: int | None = None,
    page_size: int = 100,
    max_pages: int = 100,
) -> list[dict]:
    """
    Paginates user.status (newest-first) and stops as soon as it
    reaches a submission id it has already seen, instead of always
    re-downloading the user's entire history (spec section 40,
    "Incremental Sync"). If last_submission_id is None, this behaves
    like a full fetch bounded by max_pages * page_size.

    This is purely a performance optimization - correctness still
    comes from the (user_id, problem_id) unique constraint at the DB
    layer, so even if this function's bookkeeping were wrong, syncing
    can never insert a duplicate solve (spec section 41).
    """
    all_new: list[dict] = []
    start = 1

    for _ in range(max_pages):
        url = f"{BASE_URL}/user.status?handle={handle}&from={start}&count={page_size}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data["status"] != "OK":
            raise Exception(data["comment"])

        page = data["result"]
        if not page:
            break

        for submission in page:
            if last_submission_id is not None and submission["id"] <= last_submission_id:
                return all_new
            all_new.append(submission)

        if len(page) < page_size:
            break

        start += page_size

    return all_new


def fetch_rating_history(handle: str):
    """
    Codeforces' user.rating endpoint returns one entry per rated
    contest the user participated in, each with old/new rating. Used
    to populate the RatingHistory table (spec section 38).
    """
    url = f"{BASE_URL}/user.rating?handle={handle}"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    if data["status"] != "OK":
        raise Exception(data["comment"])

    return data["result"]