import requests
from datetime import datetime, timezone

def create_session(handle, app_password):
    url = "https://bsky.social/xrpc/com.atproto.server.createSession"

    response = requests.post(url, json={
        "identifier": handle,
        "password": app_password
    })

    response.raise_for_status()
    return response.json()["accessJwt"]

def post(access_token, handle, text):
    url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"

    record = {
        "text": text,
        "createdAt": datetime.now(timezone.utc).isoformat()
    }

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(url, headers=headers, json={
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": record
    })

    response.raise_for_status()
    return response.json()