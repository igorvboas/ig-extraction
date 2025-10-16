"""
Script de debug para testar extração do Instagram
Configure as 3 variáveis no início e execute
"""
import json
from app.services.account_manager import AccountManager
from app.services.extractor import InstagramExtractor
from app.utils.logger import get_logger

# ==================== CONFIGURAÇÕES ====================
# Mude aqui para testar diferentes cenários

USERNAME = "romeroalbuquerque44"          # Username do perfil (sem @)
AMOUNT_POST = 3                 # Quantidade de posts (1-50)
FEED_OR_STORY = "story"          # "feed" ou "story"

USE_PROXY = False               # True = usa proxy / False = sem proxy

# =======================================================

logger = get_logger("debug")

def main():
    print("="*70)
    print("🔍 DEBUG - Instagram Extractor")
    print("="*70)
    print(f"📋 Configurações:")
    print(f"  - Username: @{USERNAME}")
    print(f"  - Tipo: {FEED_OR_STORY.upper()}")
    if FEED_OR_STORY == "feed":
        print(f"  - Quantidade: {AMOUNT_POST} posts")
    print(f"  - Proxy: {'Sim' if USE_PROXY else 'Não'}")
    print("="*70)
    print()
    
    # ========== PASSO 1: Inicializar AccountManager ==========
    print("📦 [PASSO 1] Inicializando AccountManager...")
    try:
        manager = AccountManager()
        print(f"✅ AccountManager inicializado")
        print(f"   Total de contas: {len(manager)}")
        print(f"   Contas disponíveis: {len(manager.get_available_accounts())}")
        
        # Desabilitar proxies se configurado
        if not USE_PROXY:
            print("⚠️  Desabilitando proxies para debug...")
            for account in manager.accounts:
                account.proxy_used = ""
        
    except Exception as e:
        print(f"❌ ERRO ao inicializar AccountManager: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    
    # ========== PASSO 2: Pegar primeira conta disponível ==========
    print("🔑 [PASSO 2] Obtendo conta disponível...")
    try:
        account = manager.get_next_account()
        print(f"✅ Conta selecionada: {account.username}")
        print(f"   Email: {account.email}")
        print(f"   Proxy: {account.proxy_used if account.proxy_used else '(sem proxy)'}")
        print(f"   Status: {account.status}")
    except Exception as e:
        print(f"❌ ERRO ao obter conta: {e}")
        return
    
    print()
    
    # ========== PASSO 3: Inicializar Extractor ==========
    print("🔧 [PASSO 3] Inicializando Extractor...")
    try:
        extractor = InstagramExtractor(manager)
        print(f"✅ Extractor inicializado")
    except Exception as e:
        print(f"❌ ERRO ao inicializar Extractor: {e}")
        return
    
    print()
    
    # ========== PASSO 4: Fazer extração ==========
    if FEED_OR_STORY.lower() == "feed":
        print(f"📸 [PASSO 4] Extraindo {AMOUNT_POST} posts de @{USERNAME}...")
        print("   (Isso pode demorar alguns segundos...)")
        print()
        
        try:
            posts = extractor.extract_posts(USERNAME, AMOUNT_POST)
            
            print()
            print("="*70)
            print("✅ EXTRAÇÃO BEM-SUCEDIDA!")
            print("="*70)
            print(f"📊 Total de posts extraídos: {len(posts)}")
            print()
            
            # Mostrar detalhes dos posts
            for i, post in enumerate(posts, 1):
                print(f"📄 Post {i}:")
                print(f"   ID: {post.id}")
                print(f"   Code: {post.code}")
                print(f"   Caption: {post.caption[:60]}..." if post.caption else "   Caption: (vazio)")
                print(f"   Likes: {post.like_count:,}")
                print(f"   Comments: {post.comment_count:,}")
                print(f"   Media type: {post.media_type} (1=Photo, 2=Video, 8=Album)")
                print(f"   Taken at: {post.taken_at}")
                print(f"   Mídias: {len(post.medias)}")
                
                # Mostrar primeira mídia
                if post.medias:
                    media = post.medias[0]
                    print(f"   Primeira mídia:")
                    print(f"     - Type: {media.media_type}")
                    print(f"     - URL: {media.media_url[:60] if media.media_url else 'None'}...")
                
                print()
            
            # Serializar TODOS os posts para JSON
            print("="*70)
            print("📋 JSON de TODOS os posts:")
            print("="*70)
            all_posts_json = [post.model_dump() for post in posts]
            print(json.dumps(all_posts_json, indent=2, ensure_ascii=False))
            print()
            
        except Exception as e:
            print()
            print("="*70)
            print("❌ ERRO NA EXTRAÇÃO")
            print("="*70)
            print(f"Tipo: {type(e).__name__}")
            print(f"Mensagem: {e}")
            print()
            print("Stack trace completo:")
            import traceback
            traceback.print_exc()
            return
    
    elif FEED_OR_STORY.lower() == "story":
        print(f"📱 [PASSO 4] Extraindo stories de @{USERNAME}...")
        print("   (Isso pode demorar alguns segundos...)")
        print()
        
        try:
            stories = extractor.extract_stories(USERNAME)
            
            print()
            print("="*70)
            print("✅ EXTRAÇÃO BEM-SUCEDIDA!")
            print("="*70)
            print(f"📊 Total de stories extraídos: {len(stories)}")
            print()
            
            if len(stories) == 0:
                print("ℹ️  Perfil não tem stories ativos no momento (stories duram 24h)")
            else:
                # Mostrar detalhes dos stories
                for i, story in enumerate(stories, 1):
                    print(f"📱 Story {i}:")
                    print(f"   ID: {story.id}")
                    print(f"   Media type: {story.media_type} (1=Photo, 2=Video)")
                    print(f"   Taken at: {story.taken_at}")
                    print(f"   Expiring at: {story.expiring_at}")
                    
                    if story.media_type == 1:
                        print(f"   Photo URL: {story.media_url[:60] if story.media_url else 'None'}...")
                    else:
                        print(f"   Video URL: {story.video_url[:60] if story.video_url else 'None'}...")
                    
                    print()
                
                # Serializar TODOS os stories para JSON
                print("="*70)
                print("📋 JSON de TODOS os stories:")
                print("="*70)
                all_stories_json = [story.model_dump() for story in stories]
                print(json.dumps(all_stories_json, indent=2, ensure_ascii=False))
                print()
            
        except Exception as e:
            print()
            print("="*70)
            print("❌ ERRO NA EXTRAÇÃO")
            print("="*70)
            print(f"Tipo: {type(e).__name__}")
            print(f"Mensagem: {e}")
            print()
            print("Stack trace completo:")
            import traceback
            traceback.print_exc()
            return
    
    else:
        print(f"❌ ERRO: FEED_OR_STORY deve ser 'feed' ou 'story', não '{FEED_OR_STORY}'")
        return
    
    # ========== PASSO 5: Status final do pool ==========
    print("="*70)
    print("📊 Status final do pool de contas")
    print("="*70)
    status = manager.get_pool_status()
    print(f"Total de contas: {status['total_accounts']}")
    print(f"Disponíveis: {status['available']}")
    print(f"Congeladas: {status['frozen']}")
    print()
    
    # Mostrar contas usadas
    used_accounts = [acc for acc in manager.accounts if acc.usage_count > 0]
    if used_accounts:
        print("Contas utilizadas:")
        for acc in used_accounts:
            print(f"  - {acc.username}: usado {acc.usage_count}x, erros: {acc.error_count}")
    
    print()
    print("="*70)
    print("✅ DEBUG CONCLUÍDO COM SUCESSO!")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()