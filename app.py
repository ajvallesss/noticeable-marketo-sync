from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Hardcoded Marketo Access Token
MARKETO_ACCESS_TOKEN = "c4df60da-abd8-4abc-ac61-89b5ec99a8b8:ab"
MARKETO_BASE_URL = "https://841-CLM-681.mktorest.com"
MARKETO_LIST_ID = "1907"

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
    url = f"{MARKETO_BASE_URL}/rest/v1/lists/{MARKETO_LIST_ID}/leads.json"
    
    # Correct payload format for Marketo
    payload = {
        "input": [{"email": email}],
        "action": "add"
    }
    
    headers = {
        "Authorization": f"Bearer {MARKETO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    print(f"Add to List Response: {response.json()}")  # Debugging

def remove_subscriber_from_list(email):
    """Remove lead from the correct Marketo Static List"""
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
