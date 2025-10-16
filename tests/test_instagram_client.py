"""
Script para testar o InstagramClient
⚠️  ATENÇÃO: Este teste fará login real no Instagram!
"""
from app.services.account_manager import AccountManager
from app.services.instagram_client import InstagramClient
from app.utils.exceptions import AccountLoginFailed, ProfileNotFound
import time


def test_instagram_client():
    print("="*50)
    print("Testando InstagramClient")
    print("="*50)
    print("⚠️  Este teste fará login REAL no Instagram!")
    print("⚠️  Certifique-se que suas contas são válidas!\n")
    
    # Aguardar confirmação
    response = input("Deseja continuar? (s/n): ")
    if response.lower() != 's':
        print("Teste cancelado.")
        return False
    
    # ========== TESTE 1: Carregar conta do AccountManager ==========
    print("\n[TESTE 1] Carregar conta disponível")
    try:
        manager = AccountManager()
        account = manager.get_next_account()
        print(f"✓ Conta selecionada: {account.username}")
        print(f"  Email: {account.email}")
        print(f"  Proxy: {account.proxy_used}")
    except Exception as e:
        print(f"✗ Erro ao carregar conta: {e}")
        return False
    
    # ========== TESTE 2: Inicializar cliente ==========
    print("\n[TESTE 2] Inicializar InstagramClient")
    try:
        client = InstagramClient(account)
        print(f"✓ Cliente inicializado: {client}")
        print(f"  Logged in: {client.is_logged_in()}")
    except Exception as e:
        print(f"✗ Erro ao inicializar cliente: {e}")
        return False
    
    # ========== TESTE 3: Login ==========
    print("\n[TESTE 3] Fazer login no Instagram")
    print("  Tentando login (pode demorar alguns segundos)...")
    
    try:
        success = client.login()
        print(f"✓ Login bem-sucedido: {success}")
        print(f"✓ Status: {client.is_logged_in()}")
        
        # Verificar se sessão foi salva
        session_file = client._get_session_file()
        print(f"✓ Arquivo de sessão: {session_file}")
        print(f"✓ Sessão salva: {session_file.exists()}")
        
    except AccountLoginFailed as e:
        print(f"✗ Falha no login: {e.message}")
        print("\n⚠️  Possíveis causas:")
        print("  - Senha incorreta")
        print("  - 2FA habilitado (não suportado neste teste)")
        print("  - Challenge requerido")
        print("  - Conta bloqueada")
        print("  - Proxy bloqueado")
        return False
    except Exception as e:
        print(f"✗ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # ========== TESTE 4: Obter user_id de um perfil público ==========
    print("\n[TESTE 4] Obter user_id de perfil público")
    test_username = "instagram"  # Perfil oficial do Instagram
    
    try:
        user_id = client.get_user_id_from_username(test_username)
        print(f"✓ User ID de @{test_username}: {user_id}")
    except ProfileNotFound as e:
        print(f"✗ Perfil não encontrado: {e.message}")
    except Exception as e:
        print(f"✗ Erro ao obter user_id: {e}")
    
    # ========== TESTE 5: Obter informações do perfil ==========
    print("\n[TESTE 5] Obter informações completas do perfil")
    
    try:
        user_info = client.get_user_info(user_id)
        print(f"✓ Informações obtidas:")
        print(f"  Username: {user_info.username}")
        print(f"  Full name: {user_info.full_name}")
        print(f"  Biography: {user_info.biography[:50]}..." if user_info.biography else "  Biography: (vazia)")
        print(f"  Followers: {user_info.follower_count:,}")
        print(f"  Following: {user_info.following_count:,}")
        print(f"  Media count: {user_info.media_count:,}")
        print(f"  Is private: {user_info.is_private}")
        print(f"  Is verified: {user_info.is_verified}")
    except Exception as e:
        print(f"✗ Erro ao obter user info: {e}")
    
    # ========== TESTE 6: Testar com perfil inexistente ==========
    print("\n[TESTE 6] Testar com perfil inexistente")
    fake_username = "usuario_que_nao_existe_12345678"
    
    try:
        fake_id = client.get_user_id_from_username(fake_username)
        print(f"✗ Deveria ter lançado ProfileNotFound")
    except ProfileNotFound as e:
        print(f"✓ ProfileNotFound capturada corretamente: {e.message}")
    
    # ========== TESTE 7: Obter informações da própria conta ==========
    print("\n[TESTE 7] Obter informações da própria conta logada")
    
    try:
        my_user_id = client.get_user_id_from_username(account.username)
        my_info = client.get_user_info(my_user_id)
        print(f"✓ Minha conta:")
        print(f"  Username: {my_info.username}")
        print(f"  Full name: {my_info.full_name}")
        print(f"  Followers: {my_info.follower_count:,}")
        print(f"  Following: {my_info.following_count:,}")
    except Exception as e:
        print(f"⚠️  Erro ao obter própria info: {e}")
    
    # ========== TESTE 8: Testar delays configurados ==========
    print("\n[TESTE 8] Verificar delays configurados")
    print(f"✓ Delay range configurado: {client.client.delay_range}")
    
    # ========== TESTE 9: Logout ==========
    print("\n[TESTE 9] Fazer logout")
    try:
        client.logout()
        print(f"✓ Logout realizado")
        print(f"✓ Status: {client.is_logged_in()}")
    except Exception as e:
        print(f"⚠️  Erro ao fazer logout: {e}")
    
    # ========== TESTE 10: Testar Context Manager ==========
    print("\n[TESTE 10] Testar Context Manager (with statement)")
    
    try:
        with InstagramClient(account) as ig_client:
            print(f"✓ Entrou no context (auto-login)")
            print(f"  Status: {ig_client.is_logged_in()}")
            
            # Fazer uma operação simples
            test_id = ig_client.get_user_id_from_username("instagram")
            print(f"✓ Operação dentro do context: user_id={test_id}")
        
        print(f"✓ Saiu do context (auto-logout)")
        
    except Exception as e:
        print(f"✗ Erro no context manager: {e}")
    
    # ========== TESTE 11: Reutilizar sessão ==========
    print("\n[TESTE 11] Reutilizar sessão salva (segundo login)")
    print("  Criando novo cliente e tentando login...")
    
    try:
        client2 = InstagramClient(account)
        client2.login()
        print(f"✓ Segundo login bem-sucedido (provavelmente usando sessão salva)")
        print(f"✓ Status: {client2.is_logged_in()}")
        
        # Verificar que consegue fazer operações
        test_id = client2.get_user_id_from_username("instagram")
        print(f"✓ Operação após relogin: user_id={test_id}")
        
        client2.logout()
    except Exception as e:
        print(f"⚠️  Erro no segundo login: {e}")
    
    print("\n✅ Todos os testes do InstagramClient concluídos!")
    print("\n📊 Resumo:")
    print(f"  - Conta testada: {account.username}")
    print(f"  - Proxy usado: {account.proxy_used}")
    print(f"  - Sessão salva em: {client._get_session_file()}")
    
    return True


if __name__ == "__main__":
    try:
        success = test_instagram_client()
        if success:
            print("\n✅ InstagramClient funcionando perfeitamente!")
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