from flask import Flask, request, jsonify
import requests
import os
import time

app = Flask(__name__)

# Marketo Credentials
MARKETO_CLIENT_ID = os.getenv("MARKETO_CLIENT_ID")
MARKETO_CLIENT_SECRET = os.getenv("MARKETO_CLIENT_SECRET")
MARKETO_BASE_URL = "https://841-CLM-681.mktorest.com"
MARKETO_LIST_ID = "1907"  # ✅ Replace with your actual Marketo List ID

# Cache token and expiration
marketo_token = None
token_expiration = 0

def get_marketo_token():
    """Fetch and return a valid Marketo API Access Token"""
    global marketo_token, token_expiration

    # If token is still valid, return it
    if marketo_token and time.time() < token_expiration:
        return marketo_token

    auth_url = f"{MARKETO_BASE_URL}/identity/oauth/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": MARKETO_CLIENT_ID,
        "client_secret": MARKETO_CLIENT_SECRET
    }
    response = requests.get(auth_url, params=params)
    response_json = response.json()

    if "access_token" in response_json:
        marketo_token = response_json["access_token"]
        token_expiration = time.time() + response_json["expires_in"] - 60  # Subtract 60s for buffer
        return marketo_token
    else:
        print("Error fetching Marketo token:", response_json)
        return None

@app.route("/", methods=["GET"])
def home():
    return "Noticeable-Marketo Sync is Running!"

@app.route("/noticeable-webhook", methods=["POST"])
def noticeable_webhook():
    """Handles Noticeable Webhooks"""
    data = request.json
    event_type = data.get("type")

    if event_type == "subscriber.created":
        email = data["data"]["email"]
        add_subscriber_to_list(email)

    elif event_type == "subscriber.deleted":
        email = data["data"]["email"]
        remove_subscriber_from_list(email)

    return jsonify({"status": "success"})

def add_subscriber_to_list(email):
    """Add lead to the correct Marketo Static List"""
    token = get_marketo_token()
    if not token:
        print("Error: Could not get Marketo token")
        return

    url = f"{MARKETO_BASE_URL}/rest/v1/lists/{MARKETO_LIST_ID}/leads.json"
    payload = {"input": [{"email": email}]}
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    print(f"Add to List Response: {response.json()}")  # Debugging

def remove_subscriber_from_list(email):
    """Remove lead from the correct Marketo Static List"""
    token = get_marketo_token()
    if not token:
        print("Error: Could not get Marketo token")
        return

    url = f"{MARKETO_BASE_URL}/rest/v1/lists/{MARKETO_LIST_ID}/leads.json"
    payload = {"input": [{"email": email}]}
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.delete(url, json=payload, headers=headers)
    print(f"Remove from List Response: {response.json()}")  # Debugging

if __name__ == "__main__":
    app.run(debug=True)
