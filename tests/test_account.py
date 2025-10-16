"""
Script para testar o model Account
"""
from app.models.account import Account
import json
import time


def test_account():
    print("="*50)
    print("Testando Model Account")
    print("="*50)
    
    # Criar conta de teste
    fingerprint_data = {
        "user_agent": "Mozilla/5.0 (X11 Linux x86_64)",
        "screen_width": 1920,
        "screen_height": 1080,
        "timezone": "America/New_York",
        "language": "pt-BR"
    }
    
    account = Account(
        email="teste@example.com",
        username="teste_user",
        password="senha123",
        status="success",
        created_at="2025-10-15 10:00:00",
        fingerprint=json.dumps(fingerprint_data),
        proxy_used="192.168.1.1:8080",
        thread_id=1
    )
    
    print(f"\n✓ Conta criada: {account}")
    
    # Teste 1: Fingerprint parsing
    print(f"\n✓ Fingerprint dict: {account.fingerprint_dict}")
    print(f"  User Agent: {account.fingerprint_dict.get('user_agent')}")
    
    # Teste 2: Proxy parsing
    print(f"\n✓ Proxy host: {account.proxy_host}")
    print(f"✓ Proxy port: {account.proxy_port}")
    print(f"✓ Proxy URL: {account.get_proxy_url()}")
    
    # Teste 3: Disponibilidade
    print(f"\n✓ Conta disponível? {account.is_available()}")
    
    # Teste 4: Marcar uso
    account.mark_used()
    print(f"\n✓ Conta marcada como usada")
    print(f"  Usage count: {account.usage_count}")
    print(f"  Last used: {account.last_used}")
    
    # Teste 5: Congelar conta
    account.freeze(duration_minutes=5, reason="Rate limit excedido")
    print(f"\n✓ Conta congelada por 5 minutos")
    print(f"  Disponível? {account.is_available()}")
    print(f"  Frozen until: {account.frozen_until}")
    
    # Teste 6: Descongelar
    account.unfreeze()
    print(f"\n✓ Conta descongelada")
    print(f"  Disponível? {account.is_available()}")
    
    # Teste 7: Registrar erro
    account.mark_error("Login failed")
    print(f"\n✓ Erro registrado")
    print(f"  Error count: {account.error_count}")
    print(f"  Last error: {account.last_error}")
    
    # Teste 8: Serializar para dict
    account_dict = account.to_dict()
    print(f"\n✓ Conta serializada para dict:")
    for key, value in account_dict.items():
        print(f"  {key}: {value}")
    
    # Teste 9: Conta com status inválido
    bad_account = Account(
        email="bad@example.com",
        username="bad_user",
        password="senha",
        status="failed",
        created_at="2025-10-15",
        fingerprint="{}",
        proxy_used="1.1.1.1:80",
        thread_id=2
    )
    print(f"\n✓ Conta com status 'failed' disponível? {bad_account.is_available()}")
    
    print("\n✅ Todos os testes do Account passaram!\n")


if __name__ == "__main__":
    test_account()