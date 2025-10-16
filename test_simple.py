"""Teste simples para debugar o problema do 422"""
import requests
import json

url = "http://localhost:8000/posts"
headers = {
    "Content-Type": "application/json",
    "Authorization": "B6s5o96euVxtER8Ul69JqlQf2j3hMkD8"
}
payload = {
    "username": "instagram",
    "quantity": 2
}

print("Enviando request para:", url)
print("Headers:", headers)
print("Payload:", json.dumps(payload, indent=2))
print("\n" + "="*50 + "\n")

response = requests.post(url, headers=headers, json=payload)

print(f"Status Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print(f"\nResponse Body:")
print(json.dumps(response.json(), indent=2))

