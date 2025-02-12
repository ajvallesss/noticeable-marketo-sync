import requests
import os

MARKETO_CLIENT_ID = os.getenv("MARKETO_CLIENT_ID")
MARKETO_CLIENT_SECRET = os.getenv("MARKETO_CLIENT_SECRET")
MARKETO_BASE_URL = os.getenv("MARKETO_BASE_URL")

def get_marketo_token():
    """Fetch Marketo API Token"""
    auth_url = f"{MARKETO_BASE_URL}/identity/oauth/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": MARKETO_CLIENT_ID,
        "client_secret": MARKETO_CLIENT_SECRET
    }
    response = requests.get(auth_url, params=params)
    return response.json().get("access_token")

def update_marketo_token(content):
    """Update Marketo Token with Release Notes"""
    token = get_marketo_token()
    program_id = "YOUR_MARKETO_PROGRAM_ID"
    token_name = "my.Noticeable-Release-Notes"

    url = f"{MARKETO_BASE_URL}/rest/asset/v1/textToken.json"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"programId": program_id, "name": token_name, "value": content}

    response = requests.post(url, json=payload, headers=headers)
    print(response.json())
