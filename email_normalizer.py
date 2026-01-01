def normalize_email(message: dict) -> dict:
    return {
        "id": message["id"],
        "subject": message.get("subject", ""),
        "from": message.get("from", {}).get("emailAddress", {}).get("address", ""),
        "to": [
            r["emailAddress"]["address"]
            for r in message.get("toRecipients", [])
        ],
        "cc": [
            r["emailAddress"]["address"]
            for r in message.get("ccRecipients", [])
        ],
        "received_at": message.get("receivedDateTime"),
        "body_preview": message.get("bodyPreview", ""),
        "body": message.get("body", {}).get("content", "")
    }
