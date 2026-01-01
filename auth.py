import msal
from config import CLIENT_ID, CLIENT_SECRET, AUTHORITY, SCOPES, WEBHOOK_SECRET

SCOPE = ["https://graph.microsoft.com/.default"]

def get_token(auth_code: str, redirect_uri: str):
    app = msal.ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=AUTHORITY
    )

    result = app.acquire_token_by_authorization_code(
        auth_code,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )

    if "access_token" not in result:
        raise Exception(result)

    return result["access_token"], result["id_token_claims"]

def get_token_device_flow():
    app = msal.PublicClientApplication(
        client_id=CLIENT_ID,
        authority=AUTHORITY
    )

    flow = app.initiate_device_flow(scopes=SCOPES)
    print(flow["message"])  # Shows login URL + code

    result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        raise Exception(result)

    return result["access_token"], result["id_token_claims"]

def get_token_device_flow2():
    app = msal.PublicClientApplication(
        client_id=CLIENT_ID,
        authority=AUTHORITY
    )

    flow = app.initiate_device_flow(scopes=SCOPES)

    if "user_code" not in flow:
        raise Exception("Failed to create device flow")

    print(flow["message"])  # Login instructions

    result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        raise Exception(result)

    # Debug: Print full token info
    print(f"SCOPES IN TOKEN: {result.get('scope', 'N/A')}")
    claims = result["id_token_claims"]
    print(f"AUD: {claims.get('aud', 'N/A')}")
    print(f"UPN: {claims.get('upn', 'N/A')}")
    print(f"EMAIL: {claims.get('email', 'N/A')}")
    print(f"OID: {claims.get('oid', 'N/A')}")
    print(f"TENANT: {claims.get('tid', 'N/A')}")

    return result["access_token"], result["id_token_claims"]

# def is_user_authorized(access_token: str) -> bool:
#     headers = {
#         "Authorization": f"Bearer {access_token}"
#     }

#     url = f"{GRAPH_BASE}/me/memberOf?$select=id"

#     while url:
#         resp = requests.get(url, headers=headers)
#         resp.raise_for_status()
#         data = resp.json()

#         for group in data.get("value", []):
#             if group.get("id") == GROUP_ID:
#                 return True

#         url = data.get("@odata.nextLink")

#     return False

def get_app_token():
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=WEBHOOK_SECRET
    )

    result = app.acquire_token_for_client(scopes=SCOPE)

    if "access_token" not in result:
        raise Exception(result)

    return result["access_token"]
