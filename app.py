from flask import Flask, request, jsonify
import os
import requests
import time

app = Flask(__name__)

# Load environment variables
NOTICEABLE_API_KEY = os.getenv("NOTICEABLE_API_KEY")
MARKETO_CLIENT_ID = os.getenv("MARKETO_CLIENT_ID")
MARKETO_CLIENT_SECRET = os.getenv("MARKETO_CLIENT_SECRET")
MARKETO_BASE_URL = os.getenv("MARKETO_BASE_URL", "https://841-CLM-681.mktorest.com")
MARKETO_LIST_NAME = os.getenv("MARKETO_LIST_NAME", "Noticeable Subscriber List")  # Default list name
MARKETO_LIST_ID = None  # Will be determined dynamically
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

def find_list_id():
    """Searches through Marketo static lists until it finds the target list"""
    global MARKETO_ACCESS_TOKEN, MARKETO_LIST_ID

    offset = 0
    batch_size = 200  # Maximum allowed batch size

    while True:
        url = f"{MARKETO_BASE_URL}/rest/asset/v1/staticLists.json"
        params = {"offset": offset, "maxReturn": batch_size}
        headers = {"Authorization": f"Bearer {MARKETO_ACCESS_TOKEN}", "Content-Type": "application/json"}

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if "result" in data:
            for item in data["result"]:
                if item["name"] == MARKETO_LIST_NAME:  # Match by list name
                    MARKETO_LIST_ID = item["id"]
                    print(f"✅ Found List '{MARKETO_LIST_NAME}' with ID {MARKETO_LIST_ID}")
                    return True  # Found the list, store its ID

            # If the number of results is less than batch_size, we've reached the end
            if len(data["result"]) < batch_size:
                break
        else:
            print(f"❌ Error retrieving lists: {data.get('errors', 'Unknown error')}")
            break

        offset += batch_size  # Move to the next batch

    print(f"❌ List '{MARKETO_LIST_NAME}' not found after full pagination.")
    return False  # List was not found

# Add subscriber to Marketo list
def add_subscriber_to_list(email):
    """Add lead to the correct Marketo Static List"""
    global MARKETO_ACCESS_TOKEN

    if not MARKETO_LIST_ID and not find_list_id():
        print(f"❌ List '{MARKETO_LIST_NAME}' not found. Cannot add subscriber.")
        return

    url = f"{MARKETO_BASE_URL}/rest/v1/lists/{MARKETO_LIST_ID}/leads.json"
    payload = {"input": [{"email": email}]}
    
    headers = {"Authorization": f"Bearer {MARKETO_ACCESS_TOKEN}", "Content-Type": "application/json"}

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

    if not MARKETO_LIST_ID and not find_list_id():
        print(f"❌ List '{MARKETO_LIST_NAME}' not found. Cannot remove subscriber.")
        return

    url = f"{MARKETO_BASE_URL}/rest/v1/lists/{MARKETO_LIST_ID}/leads.json"
    payload = {"input": [{"email": email}], "action": "remove"}
    
    headers = {"Authorization": f"Bearer {MARKETO_ACCESS_TOKEN}", "Content-Type": "application/json"}

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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
