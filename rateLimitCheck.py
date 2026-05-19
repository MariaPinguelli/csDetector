import requests
import os
from dotenv import load_dotenv

def check_rate_limit():
    load_dotenv()
    PAT = os.getenv("SECRET_PAT")
    
    if not PAT:
        print("❌ SECRET_PAT não encontrado")
        return
    
    headers = {"Authorization": f"Bearer {PAT}"}
    
    # GraphQL
    graphql_response = requests.post(
        "https://api.github.com/graphql",
        json={"query": "query { rateLimit { limit used remaining resetAt } }"},
        headers=headers
    )
    
    if graphql_response.status_code == 200:
        data = graphql_response.json()
        rl = data["data"]["rateLimit"]
        print("📊 GraphQL Rate Limit:")
        print(f"   Usado: {rl['used']}/{rl['limit']}")
        print(f"   Restante: {rl['remaining']}")
        print(f"   Reset: {rl['resetAt']}")
    else:
        print(f"❌ Erro GraphQL: {graphql_response.status_code}")
    
    # REST
    rest_response = requests.get("https://api.github.com/rate_limit", headers=headers)
    if rest_response.status_code == 200:
        core = rest_response.json()["resources"]["core"]
        print("\n📍 REST Rate Limit:")
        print(f"   Restante: {core['remaining']}/{core['limit']}")
        print(f"   Reset: {core['reset']}")

if __name__ == "__main__":
    check_rate_limit()