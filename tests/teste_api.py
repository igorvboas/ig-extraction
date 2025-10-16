"""
Script para testar a API completa
"""
import requests
import json
from app.config import Config


# Configurações
BASE_URL = "http://localhost:8000"
API_KEY = Config.API_KEY

# Headers
headers = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}


def test_api():
    print("="*50)
    print("Testando Instagram Extractor API")
    print("="*50)
    print(f"Base URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:10]}..." if API_KEY else "⚠️  Sem API Key")
    print("="*50)
    
    # ========== TESTE 1: Root endpoint ==========
    print("\n[TESTE 1] GET / (Root endpoint)")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        print("✓ Root endpoint OK")
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False
    
    # ========== TESTE 2: Health check ==========
    print("\n[TESTE 2] GET /health (sem autenticação)")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        assert response.status_code == 200
        assert data['status'] == 'healthy'
        print("✓ Health check OK")
    except Exception as e:
        print(f"✗ Erro: {e}")
    
    # ========== TESTE 3: Status endpoint (COM autenticação) ==========
    print("\n[TESTE 3] GET /status (com autenticação)")
    try:
        response = requests.get(f"{BASE_URL}/status", headers=headers)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Contas totais: {data['pool_status']['total_accounts']}")
        print(f"Contas disponíveis: {data['pool_status']['available']}")
        print(f"Contas congeladas: {data['pool_status']['frozen']}")
        assert response.status_code == 200
        print("✓ Status endpoint OK")
    except Exception as e:
        print(f"✗ Erro: {e}")
    
    # ========== TESTE 4: Status endpoint SEM autenticação ==========
    print("\n[TESTE 4] GET /status (SEM autenticação - deve falhar)")
    try:
        response = requests.get(f"{BASE_URL}/status")
        print(f"Status: {response.status_code}")
        assert response.status_code == 401
        print("✓ Autenticação funcionando corretamente (bloqueou acesso)")
    except Exception as e:
        print(f"✗ Erro: {e}")
    
    # ========== TESTE 5: Extrair posts COM autenticação ==========
    print("\n[TESTE 5] POST /posts (extrair posts)")
    
    payload = {
        "username": "instagram",
        "quantity": 3
    }
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("Aguarde... (pode demorar alguns segundos)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/posts",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success: {data['success']}")
            print(f"✓ Username: {data['username']}")
            print(f"✓ Total posts: {data['total_posts']}")
            print(f"✓ Message: {data['message']}")
            
            # Mostrar primeiro post
            if data['posts']:
                post = data['posts'][0]
                print(f"\n  Primeiro post:")
                print(f"    ID: {post['id']}")
                print(f"    Caption: {post['caption'][:50]}..." if post['caption'] else "    Caption: (vazio)")
                print(f"    Likes: {post['like_count']:,}")
                print(f"    Comments: {post['comment_count']:,}")
                print(f"    Mídias: {len(post['medias'])}")
            
            print("\n✓ Extração de posts OK")
        else:
            print(f"✗ Erro: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("✗ Timeout - requisição demorou muito")
    except Exception as e:
        print(f"✗ Erro: {e}")
    
    # ========== TESTE 6: Extrair posts SEM autenticação ==========
    print("\n[TESTE 6] POST /posts (SEM autenticação - deve falhar)")
    try:
        response = requests.post(
            f"{BASE_URL}/posts",
            json=payload
        )
        print(f"Status: {response.status_code}")
        assert response.status_code == 401
        print("✓ Bloqueou corretamente (sem autenticação)")
    except Exception as e:
        print(f"✗ Erro: {e}")
    
    # ========== TESTE 7: Extrair posts de perfil inexistente ==========
    print("\n[TESTE 7] POST /posts (perfil inexistente)")
    
    payload_fake = {
        "username": "usuario_que_nao_existe_12345678",
        "quantity": 1
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/posts",
            headers=headers,
            json=payload_fake,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 404:
            data = response.json()
            print(f"✓ Erro esperado: {data['error']}")
            print(f"✓ Message: {data['message']}")
            print("✓ ProfileNotFound tratado corretamente")
        else:
            print(f"⚠️  Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Erro: {e}")
    
    # ========== TESTE 8: Validação de request (quantity inválido) ==========
    print("\n[TESTE 8] POST /posts (quantity inválido - deve falhar)")
    
    payload_invalid = {
        "username": "instagram",
        "quantity": 100  # Máximo é 50
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/posts",
            headers=headers,
            json=payload_invalid
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 422:
            print("✓ Validação funcionando (rejeitou quantity > 50)")
        else:
            print(f"⚠️  Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Erro: {e}")
    
    # ========== TESTE 9: Extrair stories ==========
    print("\n[TESTE 9] POST /stories (extrair stories)")
    
    payload_stories = {
        "username": "instagram"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/stories",
            headers=headers,
            json=payload_stories,
            timeout=60
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success: {data['success']}")
            print(f"✓ Username: {data['username']}")
            print(f"✓ Total stories: {data['total_stories']}")
            print(f"✓ Message: {data['message']}")
            print("✓ Extração de stories OK")
        else:
            print(f"⚠️  Status: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Erro: {e}")
    
    # ========== TESTE 10: Documentação automática ==========
    print("\n[TESTE 10] Verificar documentação (Swagger UI)")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✓ Swagger UI disponível em: {BASE_URL}/docs")
        
        response = requests.get(f"{BASE_URL}/redoc")
        if response.status_code == 200:
            print(f"✓ ReDoc disponível em: {BASE_URL}/redoc")
    except Exception as e:
        print(f"⚠️  Erro: {e}")
    
    print("\n" + "="*50)
    print("✅ Testes da API concluídos!")
    print("="*50)
    print(f"\n📊 URLs úteis:")
    print(f"  - API Root: {BASE_URL}/")
    print(f"  - Health: {BASE_URL}/health")
    print(f"  - Swagger UI: {BASE_URL}/docs")
    print(f"  - ReDoc: {BASE_URL}/redoc")
    
    return True


if __name__ == "__main__":
    print("\n⚠️  IMPORTANTE: A API deve estar rodando em http://localhost:8000")
    print("Execute em outro terminal: uvicorn app.main:app --reload\n")
    
    response = input("A API está rodando? (s/n): ")
    if response.lower() != 's':
        print("Inicie a API primeiro e execute este teste novamente.")
        exit(1)
    
    try:
        success = test_api()
        if success:
            print("\n✅ Todos os testes passaram!")
            exit(0)
        else:
            print("\n⚠️  Alguns testes falharam")
            exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        exit(1)
    except Exception as e:
        print(f"\n✗ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        exit(1)