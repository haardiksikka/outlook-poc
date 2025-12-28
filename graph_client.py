import requests
from typing import List, Optional
from config import GRAPH_BASE
from model import Email, EmailAddress
from datetime import datetime, timedelta, timezone
from urllib.parse import quote


def _parse_email_from_graph(msg_data: dict) -> Optional[Email]:
    """
    Parse Microsoft Graph email response to Email model.
    
    Args:
        msg_data: Raw email data from Microsoft Graph API
    
    Returns:
        Email model instance, or None if required fields are missing
    """
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
    """
    Fetch emails from Microsoft Graph API filtered by client and date range.
    
    Args:
        access_token: Bearer token for authentication
        user_email: User's email address (for logging)
        client_email: Client email to filter conversations
        months: Number of months to look back (default: 3)
    
    Returns:
        List of Email objects from the past N months involving the client
    
    Raises:
        requests.exceptions.HTTPError: If API request fails
    
    Note:
        Uses simple $search with client email, then filters by date in Python.
        Microsoft Graph $search endpoint has limited KQL support on /me/messages,
        so we do: Search API -> fetch all matching -> Python filter by date.
    """
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
            print(f"❌ Error {resp.status_code}: {resp.text}")
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
            print(f"  Fetched {batch_size} messages, fetching next page...")
        else:
            url = None

    print(f"\n✅ Successfully fetched {total_fetched} total messages")
    print(f"✅ Filtered to {emails_in_range} emails within {months} months\n")
    return emails
