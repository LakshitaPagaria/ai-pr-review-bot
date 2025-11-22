import time
import jwt
import os
import httpx

GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
GITHUB_PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH")


def _create_jwt():
    with open(GITHUB_PRIVATE_KEY_PATH, "r") as f:
        private_key = f.read()

    now = int(time.time())

    payload = {
        "iat": now - 60,
        "exp": now + (10 * 60),
        "iss": GITHUB_APP_ID,
    }

    encoded = jwt.encode(payload, private_key, algorithm="RS256")
    return encoded


def get_installation_token(installation_id):
    jwt_token = _create_jwt()

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
    }

    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"

    r = httpx.post(url, headers=headers)
    r.raise_for_status()

    return r.json()["token"]


def fetch_pr_files(owner, repo, pr_number, token):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }

    files = []
    page = 1

    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files?page={page}&per_page=100"
        r = httpx.get(url, headers=headers)
        r.raise_for_status()

        data = r.json()
        if not data:
            break

        files.extend(data)
        page += 1

    return files


def post_pr_comment(owner, repo, pr_number, body_text, token):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"

    r = httpx.post(url, headers=headers, json={"body": body_text})
    r.raise_for_status()
    return r.json()
