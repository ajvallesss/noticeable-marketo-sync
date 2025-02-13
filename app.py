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

MARKETO_ACCESS_TOKEN = get_marketo_access_token()

def get_list_by_id(list_id=1908):
    global MARKETO_ACCESS_TOKEN
    url = f"{MARKETO_BASE_URL}/rest/asset/v1/staticList/{list_id}.json"
    headers = {"Authorization": f"Bearer {MARKETO_ACCESS_TOKEN}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    data = response.json()
    if "result" in data and isinstance(data["result"], list):
        for lst in data["result"]:
            if lst["id"] == list_id:
                print(f"✅ Found List {list_id}: {lst['name']}")
                return lst
    print(f"❌ List {list_id} not found. Response: {data}")
    return None

@app.route("/", methods=["GET"])
def home():
    return "Noticeable-Marketo Sync is Running!"

@app.route("/add-subscriber", methods=["POST"])
def add_subscriber():
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"error": "Missing email"}), 400
    url = f"{MARKETO_BASE_URL}/rest/v1/lists/{MARKETO_LIST_ID}/leads.json"
    payload = {"input": [{"email": email}]}
    headers = {"Authorization": f"Bearer {MARKETO_ACCESS_TOKEN}", "Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
