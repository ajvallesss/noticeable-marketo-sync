from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Load environment variables
NOTICEABLE_API_KEY = os.getenv("NOTICEABLE_API_KEY")
MARKETO_CLIENT_ID = os.getenv("MARKETO_CLIENT_ID")
MARKETO_CLIENT_SECRET = os.getenv("MARKETO_CLIENT_SECRET")
MARKETO_BASE_URL = os.getenv("MARKETO_BASE_URL", "https://841-CLM-681.mktorest.com")
MARKETO_LIST_ID = os.getenv("MARKETO_LIST_ID", "1907")  # Default to 1907
MARKETO_ACCESS_TOKEN = None  # Will be set dynamically

# Function to refresh Marketo access token
def get_marketo_access_token():
    """Retrieve or refresh Marketo Access Token"""
    global MARKETO_ACCESS_TOKEN

    url = f"{MARKETO_BASE_URL}/identity/oauth/token?grant_type=client_credentials&client_id={MARKETO_CLIENT_ID}&client_secret={MARKETO_CLIENT_SECRET}"
    response = requests.get(url)
    data = response.json()

    if "access_token" in data:
        MARKETO_ACCESS_TOKEN = data["access_token"]
        print(f"🔄 Refreshed Marketo Access Token: {MARKETO_ACCESS_TOKEN[:6]}...")  # Masked for security
        return MARKETO_ACCESS_TOKEN
    else:
        print(f"❌ Error fetching Marketo token: {data}")
        return None

# Ensure we always have a valid token
MARKETO_ACCESS_TOKEN = get_marketo_access_token()

# Add subscriber to Marketo list
def add_subscriber_to_list(email):
    """Add lead to the correct Marketo Static List"""
    global MARKETO_ACCESS_TOKEN

    url = f"{MARKETO_BASE_URL}/rest/v1/lists/{MARKETO_LIST_ID}/leads.json"
    payload = {
        "input": [{"email": email}]
    }
    
    headers = {
        "Authorization": f"Bearer {MARKETO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    print(f"📤 Sending request to Marketo: {url}")
    print(f"📨 Payload: {payload}")

    response = requests.post(url, json=payload, headers=headers)
    response_data = response.json()

    # If Marketo returns an invalid list ID error, log it
    if "errors" in response_data:
        print(f"❌ Error adding to list: {response_data['errors']}")

    # If token is expired, refresh it and retry once
    if "errors" in response_data and response_data["errors"][0]["code"] in ["601", "602"]:
        print("🔄 Token expired. Refreshing and retrying...")
        MARKETO_ACCESS_TOKEN = get_marketo_access_token()
        headers["Authorization"] = f"Bearer {MARKETO_ACCESS_TOKEN}"
        response = requests.post(url, json=payload, headers=headers)

    print(f"✅ Add to List Response: {response.json()}")


# Remove subscriber from Marketo list
def remove_subscriber_from_list(email):
    """Remove lead from the Marketo Static List"""
    global MARKETO_ACCESS_TOKEN

    url = f"{MARKETO_BASE_URL}/rest/v1/lists/{MARKETO_LIST_ID}/leads.json"
    payload = {
        "input": [{"email": email}],
        "action": "remove"
    }
    
    headers = {
        "Authorization": f"Bearer {MARKETO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    print(f"📤 Removing lead from Marketo list: {url}")
    response = requests.post(url, json=payload, headers=headers)
    response_data = response.json()

    # If token is expired, refresh it and retry once
    if "errors" in response_data and response_data["errors"][0]["code"] in ["601", "602"]:
        print("🔄 Token expired. Refreshing and retrying...")
        MARKETO_ACCESS_TOKEN = get_marketo_access_token()
        headers["Authorization"] = f"Bearer {MARKETO_ACCESS_TOKEN}"
        response = requests.post(url, json=payload, headers=headers)

    print(f"✅ Remove from List Response: {response.json()}")

# Fetch latest Noticeable release notes
def fetch_latest_noticeable_update():
    """Retrieve the latest product update from Noticeable"""
    url = "https://api.noticeable.io/v1/projects/YOUR_PROJECT_ID/timelines"  # Replace YOUR_PROJECT_ID
    headers = {"Authorization": f"Bearer {NOTICEABLE_API_KEY}"}
    
    response = requests.get(url, headers=headers)
    data = response.json()

    if "timelines" in data and len(data["timelines"]) > 0:
        latest_update = data["timelines"][0]["content"]["blocks"]
        return "\n".join([block["text"] for block in latest_update if "text" in block])
    else:
        return "No recent updates available."

# Update Marketo Program Token with Noticeable release notes
def update_marketo_program_token(content):
    """Update Marketo email token with Noticeable release notes"""
    global MARKETO_ACCESS_TOKEN

    url = f"{MARKETO_BASE_URL}/rest/asset/v1/program/1234/tokens.json"  # Replace 1234 with your program ID
    payload = {
        "name": "product_update",
        "type": "text",
        "value": content
    }
    
    headers = {
        "Authorization": f"Bearer {MARKETO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    print(f"✅ Marketo Token Update Response: {response.json()}")

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

    elif event_type == "timeline.published":
        print("📝 New product update detected!")
        latest_update = fetch_latest_noticeable_update()
        update_marketo_program_token(latest_update)

    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
