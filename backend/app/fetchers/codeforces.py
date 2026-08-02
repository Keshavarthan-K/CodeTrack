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