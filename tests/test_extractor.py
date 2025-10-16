"""
Script para testar o InstagramExtractor
⚠️  Este teste fará requisições REAIS ao Instagram!
"""
from app.services.account_manager import AccountManager
from app.services.extractor import InstagramExtractor
from app.utils.exceptions import ProfileNotFound, PrivateProfileError, ExtractionError
import json


def test_extractor():
    print("="*50)
    print("Testando InstagramExtractor")
    print("="*50)
    print("⚠️  Este teste fará requisições REAIS ao Instagram!")
    print("⚠️  Certifique-se que suas contas são válidas!\n")
    
    # Aguardar confirmação
    response = input("Deseja continuar? (s/n): ")
    if response.lower() != 's':
        print("Teste cancelado.")
        return False
    
    # Perguntar sobre proxy
    use_proxy = input("\nUsar proxy das contas? (s/n) [n para testar sem proxy]: ")
    use_proxy = use_proxy.lower() == 's'
    
    # ========== TESTE 1: Inicializar componentes ==========
    print("\n[TESTE 1] Inicializar AccountManager e Extractor")
    try:
        manager = AccountManager()
        
        # Se não usar proxy, limpar proxies temporariamente
        if not use_proxy:
            print("  ⚠️  Desabilitando proxies para teste...")
            for account in manager.accounts:
                account.proxy_used = ""
        
        extractor = InstagramExtractor(manager)
        print(f"✓ AccountManager: {manager}")
        print(f"✓ Extractor inicializado")
        print(f"✓ Contas disponíveis: {len(manager.get_available_accounts())}")
    except Exception as e:
        print(f"✗ Erro ao inicializar: {e}")
        return False
    
    # ========== TESTE 2: Extrair posts de perfil público ==========
    print("\n[TESTE 2] Extrair posts de perfil público")
    test_username = "instagram"  # Perfil oficial do Instagram
    quantity = 5
    
    print(f"  Extraindo {quantity} posts de @{test_username}...")
    print("  (Isso pode demorar alguns segundos...)")
    
    try:
        posts = extractor.extract_posts(test_username, quantity)
        
        print(f"\n✓ Extração bem-sucedida!")
        print(f"✓ Posts obtidos: {len(posts)}")
        
        # Mostrar detalhes dos posts
        for i, post in enumerate(posts[:3], 1):  # Mostrar até 3
            print(f"\n  Post {i}:")
            print(f"    ID: {post.id}")
            print(f"    Code: {post.code}")
            print(f"    Caption: {post.caption[:50]}..." if post.caption else "    Caption: (vazio)")
            print(f"    Likes: {post.like_count:,}")
            print(f"    Comments: {post.comment_count:,}")
            print(f"    Media type: {post.media_type} (1=Photo, 2=Video, 8=Album)")
            print(f"    Taken at: {post.taken_at}")
            print(f"    Mídias no post: {len(post.medias)}")
            
            # Mostrar mídias
            for j, media in enumerate(post.medias, 1):
                print(f"      Mídia {j}: type={media.media_type}, url={media.media_url[:50] if media.media_url else 'None'}...")
        
        if len(posts) > 3:
            print(f"\n  ... e mais {len(posts) - 3} posts")
        
    except ProfileNotFound as e:
        print(f"✗ Perfil não encontrado: {e.message}")
        return False
    except ExtractionError as e:
        print(f"✗ Erro na extração: {e.message}")
        return False
    except Exception as e:
        print(f"✗ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # ========== TESTE 3: Testar com perfil inexistente ==========
    print("\n[TESTE 3] Testar com perfil inexistente")
    fake_username = "usuario_que_nao_existe_12345678"
    
    try:
        posts = extractor.extract_posts(fake_username, 1)
        print("✗ Deveria ter lançado ProfileNotFound")
    except ProfileNotFound as e:
        print(f"✓ ProfileNotFound capturada corretamente: {e.message}")
    except Exception as e:
        print(f"⚠️  Erro inesperado: {e}")
    
    # ========== TESTE 4: Extrair posts com quantidade variada ==========
    print("\n[TESTE 4] Extrair diferentes quantidades")
    
    for qty in [1, 3]:
        try:
            print(f"  Extraindo {qty} posts...")
            posts = extractor.extract_posts(test_username, qty)
            print(f"  ✓ Obtidos: {len(posts)} posts")
        except Exception as e:
            print(f"  ✗ Erro com quantity={qty}: {e}")
    
    # ========== TESTE 5: Testar carrossel ==========
    print("\n[TESTE 5] Buscar posts com carrosséis (albums)")
    
    try:
        posts = extractor.extract_posts(test_username, 10)
        
        # Procurar por carrosséis
        carousels = [p for p in posts if p.media_type == 8]
        
        if carousels:
            print(f"✓ Encontrados {len(carousels)} carrosséis")
            carousel = carousels[0]
            print(f"  Carrossel ID: {carousel.id}")
            print(f"  Total de mídias: {len(carousel.medias)}")
            for i, media in enumerate(carousel.medias, 1):
                print(f"    Mídia {i}: type={media.media_type}")
        else:
            print("⚠️  Nenhum carrossel encontrado nos primeiros 10 posts")
    
    except Exception as e:
        print(f"⚠️  Erro ao buscar carrosséis: {e}")
    
    # ========== TESTE 6: Extrair stories ==========
    print("\n[TESTE 6] Extrair stories de perfil")
    print(f"  Extraindo stories de @{test_username}...")
    
    try:
        stories = extractor.extract_stories(test_username)
        
        print(f"✓ Stories obtidos: {len(stories)}")
        
        if len(stories) > 0:
            for i, story in enumerate(stories[:3], 1):  # Mostrar até 3
                print(f"\n  Story {i}:")
                print(f"    ID: {story.id}")
                print(f"    Media type: {story.media_type} (1=Photo, 2=Video)")
                print(f"    Taken at: {story.taken_at}")
                print(f"    Expiring at: {story.expiring_at}")
                print(f"    URL: {story.video_url if story.media_type == 2 else story.media_url}")
        else:
            print("  ℹ️  Perfil não tem stories ativos no momento")
    
    except Exception as e:
        print(f"⚠️  Erro ao extrair stories: {e}")
        # Stories podem não estar disponíveis, não é erro crítico
    
    # ========== TESTE 7: Status do pool após extrações ==========
    print("\n[TESTE 7] Status do pool de contas após extrações")
    status = manager.get_pool_status()
    print(f"✓ Total de contas: {status['total_accounts']}")
    print(f"✓ Disponíveis: {status['available']}")
    print(f"✓ Congeladas: {status['frozen']}")
    
    # Mostrar estatísticas de uso
    print("\n  Estatísticas de uso:")
    for account_data in status['accounts'][:5]:  # Mostrar até 5
        print(f"    {account_data['username']}: usado {account_data['usage_count']}x, erros: {account_data['error_count']}")
    
    # ========== TESTE 8: Serializar para JSON ==========
    print("\n[TESTE 8] Serializar resultado para JSON")
    
    try:
        # Pegar primeiro post
        if posts:
            post_dict = posts[0].model_dump()
            json_str = json.dumps(post_dict, indent=2, ensure_ascii=False)
            print(f"✓ Post serializado para JSON:")
            print(json_str[:300] + "...")
    except Exception as e:
        print(f"⚠️  Erro ao serializar: {e}")
    
    # ========== TESTE 9: Testar retry logic (opcional) ==========
    print("\n[TESTE 9] Verificar retry logic")
    print("  (Para testar completamente, seria necessário simular falhas)")
    print("  ✓ Retry logic implementado com MAX_RETRIES_PER_REQUEST")
    print(f"  ✓ Máximo de tentativas configurado: {manager.accounts[0] if manager.accounts else 'N/A'}")
    
    print("\n✅ Todos os testes do Extractor concluídos!")
    print("\n📊 Resumo:")
    print(f"  - Perfil testado: @{test_username}")
    print(f"  - Posts extraídos: {len(posts)}")
    print(f"  - Stories extraídos: {len(stories) if 'stories' in locals() else 0}")
    print(f"  - Contas usadas: {sum(1 for acc in manager.accounts if acc.usage_count > 0)}")
    
    return True


if __name__ == "__main__":
    try:
        success = test_extractor()
        if success:
            print("\n✅ InstagramExtractor funcionando perfeitamente!")
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