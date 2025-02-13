from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Load environment variables
NOTICEABLE_API_KEY = os.getenv("NOTICEABLE_API_KEY")
MARKETO_CLIENT_ID = os.getenv("MARKETO_CLIENT_ID")
MARKETO_CLIENT_SECRET = os.getenv("MARKETO_CLIENT_SECRET")
MARKETO_BASE_URL = os.getenv("MARKETO_BASE_URL")
MARKETO_LIST_ID = os.getenv("MARKETO_LIST_ID")

# Function to refresh Marketo access token
def get_marketo_access_token():
    """Retrieve or refresh Marketo Access Token"""
    url = f"{MARKETO_BASE_URL}/identity/oauth/token?grant_type=client_credentials&client_id={MARKETO_CLIENT_ID}&client_secret={MARKETO_CLIENT_SECRET}"
    response = requests.get(url)
    data = response.json()
    return data.get("access_token")

# Ensure we always have a valid token
MARKETO_ACCESS_TOKEN = get_marketo_access_token()

# Add subscriber to Marketo list
def add_subscriber_to_list(email):
    """Add a lead to the Marketo Static List"""
    global MARKETO_ACCESS_TOKEN
    url = f"{MARKETO_BASE_URL}/rest/v1/lists/{MARKETO_LIST_ID}/leads.json"
    payload = {"input": [{"email": email}]}
    headers = {
        "Authorization": f"Bearer {MARKETO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Remove subscriber from Marketo list
def remove_subscriber_from_list(email):
    """Remove lead from the Marketo Static List"""
    global MARKETO_ACCESS_TOKEN
    url = f"{MARKETO_BASE_URL}/rest/v1/lists/{MARKETO_LIST_ID}/leads.json"
    payload = {"input": [{"email": email}], "action": "remove"}
    headers = {
        "Authorization": f"Bearer {MARKETO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Flask Routes
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
        return jsonify(add_subscriber_to_list(email))

    elif event_type == "subscriber.deleted":
        email = data["data"]["email"]
        return jsonify(remove_subscriber_from_list(email))

    return jsonify({"status": "error", "message": "Invalid webhook type"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
