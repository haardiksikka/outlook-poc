from email_fetcher import fetch_email_by_id
from email_normalizer import normalize_email

def process_message(resource: str):
    email = fetch_email_by_id(resource=resource)
    normalized = normalize_email(email)

    print("Email fetched:")
    print("From:", normalized["from"])
    print("Subject:", normalized["subject"])

    return normalized
