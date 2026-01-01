import requests
from typing import List, Optional
from config import GRAPH_BASE
from model import Email, EmailAddress
from datetime import datetime, timedelta, timezone
from urllib.parse import quote


def _parse_email_from_graph(msg_data: dict) -> Optional[Email]:
    try:
        # Extract sender information
        sender_data = msg_data.get("from", {}).get("emailAddress", {})
        sender = EmailAddress(
            address=sender_data.get("address", ""),
            name=sender_data.get("name")
        ) if sender_data.get("address") else None
        
        # Parse received date
        received_str = msg_data.get("receivedDateTime")
        received_at = None
        if received_str:
            try:
                received_at = datetime.fromisoformat(received_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass
        
        # Create Email model
        email = Email(
            id=msg_data.get("id", ""),
            subject=msg_data.get("subject", ""),
            sender=sender,
            body=msg_data.get("body", {}).get("content", ""),
            receivedDateTime=received_at or datetime.utcnow(),
            webLink=msg_data.get("webLink")  # Direct URL from Microsoft Graph
        )
        
        return email
    
    except Exception as e:
        print(f"Warning: Failed to parse email {msg_data.get('id', 'unknown')}: {e}")
        return None


def fetch_client_emails(
    access_token: str,
    user_email: str,
    client_email: str,
    months: int = 3
) -> List[Email]:
    # Calculate cutoff date (make it timezone-aware in UTC)
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=30 * months)
    cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")
    
    # Use simple email search (Microsoft Graph supports this)
    # We'll do date filtering in Python
    search_term = quote(f'"{client_email}"')

    # First request - search for emails with client email address
    # Include webLink in $select to get direct URL to open email
    url = (
        f"{GRAPH_BASE}/me/messages"
        f"?$search={search_term}"
        f"&$select=id,subject,from,body,receivedDateTime,webLink"
        f"&$top=500"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "ConsistencyLevel": "eventual"
    }

    emails: List[Email] = []
    total_fetched = 0
    emails_in_range = 0

    print(f"Searching for emails with client '{client_email}'...")
    print(f"Filtering to last {months} months (since {cutoff_date_str})\n")

    while url:
        resp = requests.get(url, headers=headers)
        
        # Debug: Print error if not successful
        if resp.status_code != 200:
            resp.raise_for_status()
        
        data = resp.json()
        batch_size = len(data.get("value", []))
        
        # Parse each message to Email model
        for msg_data in data.get("value", []):
            email = _parse_email_from_graph(msg_data)
            if email:
                # Filter by date (in Python since API search is limited)
                if email.receivedDateTime >= cutoff_date:
                    emails.append(email)
                    emails_in_range += 1

        total_fetched += batch_size
        
        # Check if there are more pages
        next_url = data.get("@odata.nextLink")
        if next_url:
            url = next_url
        else:
            url = None

    return emails
