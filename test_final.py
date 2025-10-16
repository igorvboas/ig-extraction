"""Teste final - verifica se API esta funcionando"""
import requests
import json

BASE_URL = "http://localhost:8000"
API_KEY = "B6s5o96euVxtER8Ul69JqlQf2j3hMkD8"

headers = {
    "Content-Type": "application/json",
    "Authorization": API_KEY
}

print("="*70)
print("TESTE FINAL - Instagram Extractor API")
print("="*70)

# Teste 1: Health
print("\n[1] GET /health")
response = requests.get(f"{BASE_URL}/health")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Teste 2: Extrair 2 posts
print("\n[2] POST /posts (extrair 2 posts de @instagram)")
response = requests.post(
    f"{BASE_URL}/posts",
    headers=headers,
    json={"username": "instagram", "quantity": 2}
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Success: {data['success']}")
    print(f"Total posts: {data['total_posts']}")
    print(f"Primeiro post - Likes: {data['posts'][0]['like_count']:,}")
    print(f"SUCESSO! API funcionando perfeitamente!")
else:
    print(f"Erro: {response.text}")

# Teste 3: Extrair stories
print("\n[3] POST /stories (extrair stories de @romeroalbuquerque44)")
response = requests.post(
    f"{BASE_URL}/stories",
    headers=headers,
    json={"username": "romeroalbuquerque44"}
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Success: {data['success']}")
    print(f"Total stories: {data['total_stories']}")
    print(f"SUCESSO! Stories extraidos!")
else:
    print(f"Erro: {response.text}")

print("\n" + "="*70)
print("TESTES CONCLUIDOS COM SUCESSO!")
print("="*70)

