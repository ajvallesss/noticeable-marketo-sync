import requests

# Noticeable API Details
NOTICEABLE_API_KEY = "o74oUVnnfAlGV3E4C8b8"
NOTICEABLE_GRAPHQL_ENDPOINT = "https://api.noticeable.io/graphql"
NOTICEABLE_PROJECT_ID = "iNtAqOXXDnStXBh6qJG4"  # If required

# GraphQL Query to Fetch Subscribers (Testing)
query = f"""
query {{
    emailSubscription(email: "test@example.com") {{
        email
        fullName
        createdAt
        status
        isArchived
        origin
        updatedAt
    }}
}}
"""

# Headers for Authorization
headers = {
    "Authorization": f"Apikey {NOTICEABLE_API_KEY}",
    "Content-Type": "application/json"
}

# Make API Request
response = requests.post(NOTICEABLE_GRAPHQL_ENDPOINT, json={"query": query}, headers=headers)

# Output Response
print("Status Code:", response.status_code)
print("Response:", response.json())
