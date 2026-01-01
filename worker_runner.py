from email_fetcher import fetch_email_by_id
from email_normalizer import normalize_email

def process_message(message_id: str, user_email: str):
    print("🔄 Fetching email:", message_id)

    email = fetch_email_by_id(user_email, message_id)
    normalized = normalize_email(email)

    print("📧 Email fetched:")
    print("From:", normalized["from"])
    print("Subject:", normalized["subject"])

    return normalized
