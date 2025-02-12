from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Load API Keys from Heroku Environment Variables
NOTICEABLE_API_KEY = os.getenv("NOTICEABLE_API_KEY")
MARKETO_CLIENT_ID = os.getenv("MARKETO_CLIENT_ID")
MARKETO_CLIENT_SECRET = os.getenv("MARKETO_CLIENT_SECRET")
MARKETO_BASE_URL = os.getenv("MARKETO_BASE_URL")

def get_marketo_token():
    """Get Marketo Auth Token"""
    auth_url = f"{MARKETO_BASE_URL}/identity/oauth/token?grant_type=client_credentials&client_id={MARKETO_CLIENT_ID}&client_secret={MARKETO_CLIENT_SECRET}"
    response = requests.get(auth_url)
    return response.json().get("access_token")

@app.route("/", methods=["GET"])
def home():
    return "Noticeable to Marketo Sync is Running!"

@app.route("/noticeable-webhook", methods=["POST"])
def noticeable_webhook():
    """Handle Noticeable Webhooks for Subscribers and Announcements"""
    data = request.json
    event_type = data.get("type")

    if event_type == "subscriber.created":
        email = data["data"]["email"]
        add_subscriber_to_marketo(email)

    elif event_type == "subscriber.deleted":
        email = data["data"]["email"]
        remove_subscriber_from_marketo(email)

    elif event_type == "announcement.published":
        announcement = data["data"]["content"]
        update_marketo_token(announcement)

    return jsonify({"status": "success"})

def add_subscriber_to_marketo(email):
    """Add subscriber to Marketo List"""
    token = get_marketo_token()
    url = f"{MARKETO_BASE_URL}/rest/v1/leads.json"
    payload = {
        "action": "createOrUpdate",
        "lookupField": "email",
        "input": [{"email": email}]
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

def remove_subscriber_from_marketo(email):
    """Remove subscriber from Marketo List"""
    token = get_marketo_token()
    url = f"{MARKETO_BASE_URL}/rest/v1/leads.json?_method=DELETE"
    payload = {"input": [{"email": email}]}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

def update_marketo_token(content):
    """Update Marketo Program Token with Noticeable Release Notes"""
    token = get_marketo_token()
    url = f"{MARKETO_BASE_URL}/rest/asset/v1/folder/byName.json?name=Your-Folder-Name"
    payload = {"content": content}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    app.run(debug=True)
