from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Load API Credentials
MARKETO_CLIENT_ID = os.getenv("MARKETO_CLIENT_ID")
MARKETO_CLIENT_SECRET = os.getenv("MARKETO_CLIENT_SECRET")
MARKETO_BASE_URL = os.getenv("MARKETO_BASE_URL")

# Define the Marketo List ID where leads will be added/removed
MARKETO_LIST_ID = "1907"  # Replace with your actual List ID

def get_marketo_token():
    """Fetch and return Marketo API Access Token"""
    auth_url = f"{MARKETO_BASE_URL}/identity/oauth/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": MARKETO_CLIENT_ID,
        "client_secret": MARKETO_CLIENT_SECRET
    }
    response = requests.get(auth_url, params=params)
    response_json = response.json()
    
    if "access_token" in response_json:
        return response_json["access_token"]
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
    """Add lead to a specific Marketo Static List"""
    token = get_marketo_token()
    if not token:
        return

    url = f"{MARKETO_BASE_URL}/rest/v1/lists/{MARKETO_LIST_ID}/leads.json"
    payload = {
        "input": [{"email": email}]
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    print(f"Add to List Response: {response.json()}")

def remove_subscriber_from_list(email):
    """Remove lead from a specific Marketo Static List"""
    token = get_marketo_token()
    if not token:
        return

    url = f"{MARKETO_BASE_URL}/rest/v1/lists/{MARKETO_LIST_ID}/leads.json"
    payload = {
        "input": [{"email": email}]
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    response = requests.delete(url, json=payload, headers=headers)
    print(f"Remove from List Response: {response.json()}")

if __name__ == "__main__":
    app.run(debug=True)
