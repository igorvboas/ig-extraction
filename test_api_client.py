"""
Script Python para testar a API de extração do Instagram
"""
import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"
API_KEY = "B6s5o96euVxtER8Ul69JqlQf2j3hMkD8"

# Headers
headers = {
    "Content-Type": "application/json",
    "Authorization": API_KEY
}


def extract_posts(username: str, quantity: int):
    """
    Extrai posts de um perfil
    
    Args:
        username: Username do perfil (sem @)
        quantity: Quantidade de posts (1-50)
    """
    print(f"\n{'='*70}")
    print(f"📸 Extraindo {quantity} posts de @{username}")
    print(f"{'='*70}\n")
    
    url = f"{BASE_URL}/posts"
    payload = {
        "username": username,
        "quantity": quantity
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso!")
            print(f"Total de posts: {data['total_posts']}")
            print(f"Mensagem: {data['message']}\n")
            
            # Mostrar posts
            for i, post in enumerate(data['posts'], 1):
                print(f"Post {i}:")
                print(f"  ID: {post['id']}")
                print(f"  Caption: {post['caption'][:60]}..." if post['caption'] else "  Caption: (vazio)")
                print(f"  Likes: {post['like_count']:,}")
                print(f"  Comments: {post['comment_count']:,}")
                print(f"  Mídias: {len(post['medias'])}")
                print()
            
            # Salvar JSON completo em arquivo
            with open(f"posts_{username}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 JSON salvo em: posts_{username}.json")
            
            return data
        else:
            print(f"❌ Erro {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - requisição demorou muito")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - a API está rodando?")
        return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


def extract_stories(username: str):
    """
    Extrai stories de um perfil
    
    Args:
        username: Username do perfil (sem @)
    """
    print(f"\n{'='*70}")
    print(f"📱 Extraindo stories de @{username}")
    print(f"{'='*70}\n")
    
    url = f"{BASE_URL}/stories"
    payload = {
        "username": username
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso!")
            print(f"Total de stories: {data['total_stories']}")
            print(f"Mensagem: {data['message']}\n")
            
            # Mostrar stories
            if data['stories']:
                for i, story in enumerate(data['stories'], 1):
                    print(f"Story {i}:")
                    print(f"  ID: {story['id']}")
                    print(f"  Type: {'Vídeo' if story['media_type'] == 2 else 'Foto'}")
                    print(f"  Taken at: {story['taken_at']}")
                    print()
                
                # Salvar JSON completo em arquivo
                with open(f"stories_{username}.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"💾 JSON salvo em: stories_{username}.json")
            else:
                print("ℹ️  Perfil não tem stories ativos no momento")
            
            return data
        else:
            print(f"❌ Erro {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - requisição demorou muito")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - a API está rodando?")
        return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


def check_health():
    """Verifica se a API está online"""
    print(f"\n{'='*70}")
    print("🏥 Verificando saúde da API")
    print(f"{'='*70}\n")
    
    url = f"{BASE_URL}/health"
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API está online!")
            print(f"Status: {data['status']}")
            print(f"Total de contas: {data['accounts']['total']}")
            print(f"Contas disponíveis: {data['accounts']['available']}")
            print(f"Contas congeladas: {data['accounts']['frozen']}")
            return True
        else:
            print(f"❌ API retornou status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à API")
        print("Certifique-se que a API está rodando em http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


if __name__ == "__main__":
    print("="*70)
    print("🚀 Instagram Extractor API - Cliente de Teste")
    print("="*70)
    
    # Verificar se API está online
    if not check_health():
        print("\n⚠️  Inicie a API primeiro:")
        print("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        exit(1)
    
    # Exemplo 1: Extrair posts
    extract_posts("eusoumarcospaulo", 2)
    
    # Exemplo 2: Extrair stories
    extract_stories("eusoumarcospaulo")
    
    print("\n" + "="*70)
    print("✅ Testes concluídos!")
    print("="*70)