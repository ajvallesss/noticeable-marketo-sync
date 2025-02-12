from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Use the provided Marketo Access Token
MARKETO_ACCESS_TOKEN = "20d5f0ce-fac6-40b1-8f30-1f6693169d6c:ab"
MARKETO_BASE_URL = "https://841-CLM-681.mktorest.com"
MARKETO_LIST_ID = "1907"  # Replace with your actual Marketo List ID

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
    url = f"{MARKETO_BASE_URL}/rest/v1/lists/{MARKETO_LIST_ID}/leads.json"
    payload = {"input": [{"email": email}]}
    headers = {
        "Authorization": f"Bearer {MARKETO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    print(f"Add to List Response: {response.json()}")  # Debugging

def remove_subscriber_from_list(email):
    """Remove lead from a specific Marketo Static List"""
    url = f"{MARKETO_BASE_URL}/rest/v1/lists/{MARKETO_LIST_ID}/leads.json"
    payload = {"input": [{"email": email}]}
    headers = {
        "Authorization": f"Bearer {MARKETO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.delete(url, json=payload, headers=headers)
    print(f"Remove from List Response: {response.json()}")  # Debugging

if __name__ == "__main__":
    app.run(debug=True)
