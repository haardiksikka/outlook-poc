import requests
from datetime import datetime, timedelta
from auth import get_app_token

GRAPH_BASE = "https://graph.microsoft.com/v1.0"

def create_subscription():
    token = get_app_token()

    expiration = (
        datetime.utcnow() + timedelta(hours=6)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = {
        "changeType": "created",
        "notificationUrl": "https://mysimon-hidden-through-batch.trycloudflare.com/webhook",
        "resource": "/users/pocuser1@cmopoc.onmicrosoft.com/mailFolders('Inbox')/messages",
        "expirationDateTime": expiration,
        "clientState": "poc-secret-123"
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    resp = requests.post(
        f"{GRAPH_BASE}/subscriptions",
        json=payload,
        headers=headers
    )

    if not resp.ok:
        print("Status:", resp.status_code)
        print("Response:", resp.text)
        raise Exception("Subscription creation failed")

    print("Subscription created:", resp.json())

if __name__ == "__main__":
    create_subscription()
