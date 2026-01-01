import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["User.Read", "Mail.Read"]

GRAPH_BASE = "https://graph.microsoft.com/v1.0"

# Object ID of the Security Group you created in Entra
GROUP_ID = os.getenv("GROUP_ID")

