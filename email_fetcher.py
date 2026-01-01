import requests
from auth import get_app_token

GRAPH_BASE = "https://graph.microsoft.com/v1.0"

def fetch_email_by_id(user_email: str, message_id: str) -> dict:
    token = get_app_token()

    url = f"{GRAPH_BASE}/{user_email}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.get(url, headers=headers)

    # Handle transient issues gracefully
    if resp.status_code == 404:
        raise Exception("Email not found (deleted or moved)")

    resp.raise_for_status()
    return resp.json()
