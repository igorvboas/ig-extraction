"""Teste enviando payload com wrapper 'data'"""
import requests
import json

url = "http://localhost:8000/posts"
headers = {
    "Content-Type": "application/json",
    "Authorization": "B6s5o96euVxtER8Ul69JqlQf2j3hMkD8"
}

# Tentando com wrapper
payload_wrapped = {
    "data": {
        "username": "test",
        "quantity": 1
    }
}

print("Tentando com wrapper 'data':")
print(json.dumps(payload_wrapped, indent=2))
response = requests.post(url, headers=headers, json=payload_wrapped)
print(f"\nStatus: {response.status_code}")
print(json.dumps(response.json(), indent=2))

