from flask import Flask, request, jsonify
import os
import requests
import sys

app = Flask(__name__)

# Load environment variables
NOTICEABLE_API_KEY = os.getenv("NOTICEABLE_API_KEY")
MARKETO_CLIENT_ID = os.getenv("MARKETO_CLIENT_ID")
MARKETO_CLIENT_SECRET = os.getenv("MARKETO_CLIENT_SECRET")
MARKETO_BASE_URL = os.getenv("MARKETO_BASE_URL", "https://841-CLM-681.mktorest.com")
MARKETO_ACCESS_TOKEN = None  # Will be set dynamically
MARKETO_LIST_ID = 1908  # Searching for this list ID

# Function to refresh Marketo access token
def get_marketo_access_token():
    """Retrieve or refresh Marketo Access Token"""
    global MARKETO_ACCESS_TOKEN

    url = f"{MARKETO_BASE_URL}/identity/oauth/token?grant_type=client_credentials&client_id={MARKETO_CLIENT_ID}&client_secret={MARKETO_CLIENT_SECRET}"
    response = requests.get(url)
    data = response.json()

    if "access_token" in data:
        MARKETO_ACCESS_TOKEN = data["access_token"]
        print(f"🔄 Refreshed Marketo Access Token: {MARKETO_ACCESS_TOKEN[:6]}...")
        return MARKETO_ACCESS_TOKEN
    else:
        print(f"❌ Error fetching Marketo token: {data}")
        return None

# Ensure we always have a valid token
MARKETO_ACCESS_TOKEN = get_marketo_access_token()

def find_list_by_id(target_list_id=1908):
    """Search through Marketo lists and find the correct list by ID"""
    global MARKETO_ACCESS_TOKEN

    offset = 0
    limit = 200  # Max items per page

    while True:
        url = f"{MARKETO_BASE_URL}/rest/v1/lists.json"
        params = {"offset": offset, "maxReturn": limit}
        headers = {"Authorization": f"Bearer {MARKETO_ACCESS_TOKEN}", "Content-Type": "application/json"}

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if "result" in data:
            for item in data["result"]:
                if item["id"] == target_list_id:
                    print(f"✅ Found List ID {target_list_id}: {item['name']}")
                    return item["id"]  # Found the list

        if not data.get("moreResult"):  # If there are no more results, stop
            print(f"❌ List ID {target_list_id} not found after full pagination.")
            return None

        offset += limit  # Move to the next batch

# Add subscriber to Marketo list
def add_subscriber_to_list(email):
    """Add lead to the correct Marketo Static List"""
    global MARKETO_ACCESS_TOKEN, MARKETO_LIST_ID

    if find_list_by_id(MARKETO_LIST_ID) is None:
        print("❌ List not found. Cannot add subscriber.")
        return

    url = f"{MARKETO_BASE_URL}/rest/v1/lists/{MARKETO_LIST_ID}/leads.json"
    payload = {"input": [{"email": email}]}
    
    headers = {"Authorization": f"Bearer {MARKETO_ACCESS_TOKEN}", "Content-Type": "application/json"}

    print(f"📤 Sending request to Marketo: {url}")
    response = requests.post(url, json=payload, headers=headers)
    print(f"✅ Add to List Response: {response.json()}")

# Remove subscriber from Marketo list
def remove_subscriber_from_list(email):
    """Remove lead from the Marketo Static List"""
    global MARKETO_ACCESS_TOKEN, MARKETO_LIST_ID

    if find_list_by_id(MARKETO_LIST_ID) is None:
        print("❌ List not found. Cannot remove subscriber.")
        return

    url = f"{MARKETO_BASE_URL}/rest/v1/lists/{MARKETO_LIST_ID}/leads.json"
    payload = {"input": [{"email": email}], "action": "remove"}
    
    headers = {"Authorization": f"Bearer {MARKETO_ACCESS_TOKEN}", "Content-Type": "application/json"}

    print(f"📤 Removing lead from Marketo list: {url}")
    response = requests.post(url, json=payload, headers=headers)
    print(f"✅ Remove from List Response: {response.json()}")

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
        print(f"🟢 New subscriber detected: {email}")
        add_subscriber_to_list(email)

    elif event_type == "subscriber.deleted":
        email = data["data"]["email"]
        print(f"🔴 Subscriber opted out: {email}")
        remove_subscriber_from_list(email)

    return jsonify({"status": "success"})

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "find_list":
        find_list_by_id()  # This runs when you explicitly call "find_list"
    else:
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
