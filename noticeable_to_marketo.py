import requests

# Noticeable API Details
NOTICEABLE_API_KEY = "o74oUVnnfAlGV3E4C8b8"
NOTICEABLE_GRAPHQL_ENDPOINT = "https://api.noticeable.io/graphql"

# GraphQL Query to Check Available Fields
query = """
query {
    __schema {
        queryType {
            fields {
                name
            }
        }
    }
}
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
