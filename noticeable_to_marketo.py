import requests
import json
import os

# Marketo API Credentials
MARKETO_BASE_URL = os.getenv("MARKETO_BASE_URL")
MARKETO_CLIENT_ID = os.getenv("MARKETO_CLIENT_ID")
MARKETO_CLIENT_SECRET = os.getenv("MARKETO_CLIENT_SECRET")
MARKETO_LIST_ID = os.getenv("MARKETO_LIST_ID")  # Static list ID

# Noticeable API Credentials
NOTICEABLE_API_KEY = os.getenv("NOTICEABLE_API_KEY")
NOTICEABLE_GRAPHQL_ENDPOINT = "https://api.noticeable.io/graphql"
NOTICEABLE_PROJECT_ID = "iNtAqOXXDnStXBh6qJG4"  # Hardcoded Project ID

# Function to get Marketo access token
def get_marketo_access_token():
    url = f"{MARKETO_BASE_URL}/identity/oauth/token?grant_type=client_credentials&client_id={MARKETO_CLIENT_ID}&client_secret={MARKETO_CLIENT_SECRET}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception("Failed to get Marketo access token")

# Function to fetch Noticeable subscribers
def get_noticeable_subscribers():
    headers = {"Authorization": f"Apikey {NOTICEABLE_API_KEY}", "Content-Type": "application/json"}
    query = f"""
    query {{
        EmailSubscription(projectId: "{NOTICEABLE_PROJECT_ID}") {{  
            email
            fullName
            createdAt
            status
        }}
    }}
    """
    response = requests.post(NOTICEABLE_GRAPHQL_ENDPOINT, json={"query": query}, headers=headers)

    print("Noticeable API Response:", response.status_code, response.text)  # Debugging Line

    if response.status_code == 200:
        return response.json().get("data", {}).get("EmailSubscription", [])
    else:
        raise Exception(f"Failed to fetch Noticeable subscribers: {response.text}")

# Function to update Marketo static list
def update_marketo_list(subscribers, remove=False):
    if not subscribers:
        return "No updates needed."
    
    access_token = get_marketo_access_token()
    endpoint = f"{MARKETO_BASE_URL}/rest/v1/lists/{MARKETO_LIST_ID}/leads.json"
    if remove:
        endpoint = f"{MARKETO_BASE_URL}/rest/v1/lists/{MARKETO_LIST_ID}/leads/delete.json"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {"input": [{
        "email": sub.get("email"),
        "fullName": sub.get("fullName", ""),
        "status": sub.get("status", ""),
        "createdAt": sub.get("createdAt", "")
    } for sub in subscribers]}
    
    response = requests.post(endpoint, headers=headers, json=payload)
    return response.json()

# Main execution
def main():
    print("Fetching subscribers from Noticeable...")
    subscribers = get_noticeable_subscribers()
    
    new_subscribers = [s for s in subscribers if not s.get("unsubscribedAt")]
    unsubscribers = [s for s in subscribers if s.get("unsubscribedAt")]
    
    if new_subscribers:
        print("Adding new subscribers to Marketo...")
        add_response = update_marketo_list(new_subscribers)
        print("Add Response:", add_response)
    
    if unsubscribers:
        print("Removing unsubscribed users from Marketo...")
        remove_response = update_marketo_list(unsubscribers, remove=True)
        print("Remove Response:", remove_response)
    
    print("Sync Complete.")

if __name__ == "__main__":
    main()
