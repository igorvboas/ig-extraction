"""
Script para testar as exceções customizadas
"""
from app.utils.exceptions import (
    InstagramAPIException,
    AuthenticationError,
    AccountPoolExhausted,
    ProfileNotFound,
    RateLimitExceeded
)


def test_exceptions():
    print("="*50)
    print("Testando Exceções Customizadas")
    print("="*50)
    
    # Teste 1: Exceção base
    try:
        raise InstagramAPIException("Erro genérico", details={"code": 500})
    except InstagramAPIException as e:
        print(f"✓ InstagramAPIException capturada: {e.message}")
        print(f"  Details: {e.details}")
    
    # Teste 2: AuthenticationError
    try:
        raise AuthenticationError("Token inválido")
    except AuthenticationError as e:
        print(f"✓ AuthenticationError capturada: {e.message}")
    
    # Teste 3: AccountPoolExhausted
    try:
        raise AccountPoolExhausted("Todas as contas estão em quarentena")
    except AccountPoolExhausted as e:
        print(f"✓ AccountPoolExhausted capturada: {e.message}")
    
    # Teste 4: ProfileNotFound
    try:
        raise ProfileNotFound("Perfil @teste não existe", details={"username": "teste"})
    except ProfileNotFound as e:
        print(f"✓ ProfileNotFound capturada: {e.message}")
        print(f"  Details: {e.details}")
    
    # Teste 5: Herança - capturar qualquer exceção da API
    try:
        raise RateLimitExceeded("Muitas requisições")
    except InstagramAPIException as e:
        print(f"✓ Capturada como InstagramAPIException (herança): {e.message}")
    
    print("\n✅ Todos os testes de exceções passaram!\n")


if __name__ == "__main__":
    test_exceptions()