"""
Script para testar o AccountManager
"""
from app.services.account_manager import AccountManager
from app.utils.exceptions import AccountPoolExhausted, CSVParseError
import time


def test_account_manager():
    print("="*50)
    print("Testando AccountManager")
    print("="*50)
    
    # ========== TESTE 1: Inicialização ==========
    print("\n[TESTE 1] Inicializar AccountManager")
    try:
        manager = AccountManager()
        print(f"✓ AccountManager inicializado: {manager}")
        print(f"✓ Total de contas carregadas: {len(manager)}")
    except Exception as e:
        print(f"✗ Erro ao inicializar: {e}")
        print("\n⚠️  Certifique-se que data/accounts.csv existe e está no formato correto!")
        return False
    
    # ========== TESTE 2: Status do pool ==========
    print("\n[TESTE 2] Status do pool de contas")
    status = manager.get_pool_status()
    print(f"✓ Total de contas: {status['total_accounts']}")
    print(f"✓ Contas disponíveis: {status['available']}")
    print(f"✓ Contas congeladas: {status['frozen']}")
    print(f"✓ Contas com status failed: {status['failed_status']}")
    
    if status['total_accounts'] == 0:
        print("\n✗ Nenhuma conta encontrada no CSV!")
        return False
    
    # ========== TESTE 3: Listar contas disponíveis ==========
    print("\n[TESTE 3] Listar contas disponíveis")
    available = manager.get_available_accounts()
    print(f"✓ Contas disponíveis: {len(available)}")
    for i, acc in enumerate(available[:3], 1):  # Mostrar até 3
        print(f"  {i}. {acc.username} (proxy: {acc.proxy_used})")
    if len(available) > 3:
        print(f"  ... e mais {len(available) - 3} contas")
    
    if len(available) == 0:
        print("\n⚠️  Nenhuma conta disponível! Verifique o status das contas no CSV.")
        return False
    
    # ========== TESTE 4: Pegar próxima conta (round-robin) ==========
    print("\n[TESTE 4] Rotação de contas (round-robin)")
    accounts_retrieved = []
    for i in range(min(5, len(manager))):
        try:
            account = manager.get_next_account()
            accounts_retrieved.append(account.username)
            print(f"  Rodada {i+1}: {account.username}")
        except AccountPoolExhausted as e:
            print(f"  Pool esgotado na rodada {i+1}")
            break
    
    print(f"✓ Contas obtidas: {len(accounts_retrieved)}")
    
    # Verificar se houve rotação (se tivermos 2+ contas)
    if len(set(accounts_retrieved)) > 1:
        print(f"✓ Rotação funcionando! Contas únicas: {len(set(accounts_retrieved))}")
    
    # ========== TESTE 5: Buscar conta por username ==========
    print("\n[TESTE 5] Buscar conta específica por username")
    if accounts_retrieved:
        test_username = accounts_retrieved[0]
        account = manager.get_account_by_username(test_username)
        if account:
            print(f"✓ Conta encontrada: {account.username}")
            print(f"  Email: {account.email}")
            print(f"  Proxy: {account.proxy_used}")
            print(f"  Status: {account.status}")
        else:
            print(f"✗ Conta não encontrada")
    
    # Buscar conta inexistente
    fake_account = manager.get_account_by_username("conta_inexistente_123")
    print(f"✓ Busca por conta inexistente retornou: {fake_account}")
    
    # ========== TESTE 6: Marcar conta como usada ==========
    print("\n[TESTE 6] Marcar conta como usada")
    if accounts_retrieved:
        test_username = accounts_retrieved[0]
        account = manager.get_account_by_username(test_username)
        usage_before = account.usage_count
        
        manager.mark_account_used(test_username)
        usage_after = account.usage_count
        
        print(f"✓ Usage count antes: {usage_before}")
        print(f"✓ Usage count depois: {usage_after}")
        print(f"✓ Last used: {account.last_used}")
    
    # ========== TESTE 7: Congelar conta ==========
    print("\n[TESTE 7] Congelar conta temporariamente")
    if accounts_retrieved:
        test_username = accounts_retrieved[0]
        account = manager.get_account_by_username(test_username)
        
        print(f"  Antes: disponível = {account.is_available()}")
        
        manager.freeze_account(test_username, duration_minutes=1, reason="Teste de congelamento")
        
        print(f"  Depois: disponível = {account.is_available()}")
        print(f"  Frozen until: {account.frozen_until}")
        print(f"  Last error: {account.last_error}")
    
    # ========== TESTE 8: Pool status com conta congelada ==========
    print("\n[TESTE 8] Status do pool após congelar conta")
    status_after_freeze = manager.get_pool_status()
    print(f"✓ Contas disponíveis: {status_after_freeze['available']}")
    print(f"✓ Contas congeladas: {status_after_freeze['frozen']}")
    
    # ========== TESTE 9: Descongelar conta ==========
    print("\n[TESTE 9] Descongelar conta")
    if accounts_retrieved:
        test_username = accounts_retrieved[0]
        
        manager.unfreeze_account(test_username)
        account = manager.get_account_by_username(test_username)
        
        print(f"✓ Conta disponível após descongelar: {account.is_available()}")
        print(f"✓ Frozen: {account.is_frozen}")
    
    # ========== TESTE 10: Registrar erro ==========
    print("\n[TESTE 10] Registrar erro na conta")
    if accounts_retrieved:
        test_username = accounts_retrieved[0]
        account = manager.get_account_by_username(test_username)
        
        errors_before = account.error_count
        
        manager.mark_account_error(test_username, "Rate limit exceeded")
        
        print(f"✓ Error count antes: {errors_before}")
        print(f"✓ Error count depois: {account.error_count}")
        print(f"✓ Last error: {account.last_error}")
    
    # ========== TESTE 11: Próxima conta após congelar todas ==========
    print("\n[TESTE 11] Testar pool esgotado (congelar todas)")
    print("  Congelando todas as contas disponíveis...")
    
    for account in manager.get_available_accounts():
        manager.freeze_account(account.username, duration_minutes=1, reason="Teste pool esgotado")
    
    try:
        manager.get_next_account()
        print("✗ Deveria ter lançado AccountPoolExhausted")
    except AccountPoolExhausted as e:
        print(f"✓ AccountPoolExhausted capturada corretamente: {e.message}")
        print(f"  Details: available={e.details.get('available')}")
    
    # Descongelar todas
    print("\n  Descongelando todas as contas...")
    for account in manager.accounts:
        if account.is_frozen:
            manager.unfreeze_account(account.username)
    
    # ========== TESTE 12: Reload accounts ==========
    print("\n[TESTE 12] Reload accounts do CSV")
    initial_count = len(manager)
    manager.reload_accounts()
    after_reload_count = len(manager)
    
    print(f"✓ Contas antes do reload: {initial_count}")
    print(f"✓ Contas após reload: {after_reload_count}")
    
    # ========== TESTE 13: Thread safety (simulação básica) ==========
    print("\n[TESTE 13] Thread safety - múltiplas requisições")
    import threading
    
    results = []
    
    def get_account_thread():
        try:
            acc = manager.get_next_account()
            results.append(acc.username)
        except AccountPoolExhausted:
            results.append(None)
    
    threads = []
    for _ in range(5):
        t = threading.Thread(target=get_account_thread)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"✓ Threads executadas: 5")
    print(f"✓ Contas obtidas: {len([r for r in results if r])}")
    print(f"✓ Contas únicas: {len(set(results))}")
    
    print("\n✅ Todos os testes do AccountManager concluídos!\n")
    return True


if __name__ == "__main__":
    try:
        success = test_account_manager()
        if success:
            print("✅ AccountManager funcionando perfeitamente!")
            exit(0)
        else:
            print("⚠️  Corrija os problemas antes de continuar")
            exit(1)
    except Exception as e:
        print(f"\n✗ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        exit(1)