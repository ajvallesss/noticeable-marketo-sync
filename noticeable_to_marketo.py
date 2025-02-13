import requests

# Noticeable API Details
NOTICEABLE_API_KEY = "o74oUVnnfAlGV3E4C8b8"
NOTICEABLE_GRAPHQL_ENDPOINT = "https://api.noticeable.io/graphql"
NOTICEABLE_PROJECT_ID = "iNtAqOXXDnStXBh6qJG4"

# GraphQL Query to Fetch a Single Subscriber (Replace Email)
query = f"""
query {{
    emailSubscription(projectId: "{NOTICEABLE_PROJECT_ID}", email: "tliu@nzsuperfund.co.nz") {{
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
