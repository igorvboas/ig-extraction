"""
Script para testar as configurações do app/config.py
"""
from app.config import Config, config
from app.utils.exceptions import ConfigurationError
from pathlib import Path


def test_config():
    print("="*50)
    print("Testando Configurações (app/config.py)")
    print("="*50)
    
    # ========== TESTE 1: Valores carregados ==========
    print("\n[TESTE 1] Valores carregados do .env")
    print(f"✓ API_KEY configurada: {'Sim' if Config.API_KEY else 'Não'}")
    print(f"✓ MAX_CONCURRENT_REQUESTS: {Config.MAX_CONCURRENT_REQUESTS}")
    print(f"✓ ACCOUNTS_CSV_PATH: {Config.ACCOUNTS_CSV_PATH}")
    print(f"✓ SESSIONS_DIR_PATH: {Config.SESSIONS_DIR_PATH}")
    print(f"✓ LOG_LEVEL: {Config.LOG_LEVEL}")
    print(f"✓ LOG_FILE: {Config.LOG_FILE}")
    print(f"✓ INSTAGRAM_DELAY_MIN: {Config.INSTAGRAM_DELAY_MIN}")
    print(f"✓ INSTAGRAM_DELAY_MAX: {Config.INSTAGRAM_DELAY_MAX}")
    print(f"✓ ACCOUNT_FREEZE_DURATION_MINUTES: {Config.ACCOUNT_FREEZE_DURATION_MINUTES}")
    print(f"✓ MAX_RETRIES_PER_REQUEST: {Config.MAX_RETRIES_PER_REQUEST}")
    
    # ========== TESTE 2: BASE_DIR ==========
    print(f"\n[TESTE 2] BASE_DIR (diretório raiz do projeto)")
    print(f"✓ BASE_DIR: {Config.BASE_DIR}")
    print(f"✓ BASE_DIR existe? {Config.BASE_DIR.exists()}")
    
    # ========== TESTE 3: Caminhos absolutos ==========
    print(f"\n[TESTE 3] Conversão para caminhos absolutos")
    accounts_path = Config.get_absolute_path(Config.ACCOUNTS_CSV_PATH)
    sessions_path = Config.get_absolute_path(Config.SESSIONS_DIR_PATH)
    print(f"✓ Accounts CSV (absoluto): {accounts_path}")
    print(f"✓ Accounts CSV existe? {accounts_path.exists()}")
    print(f"✓ Sessions DIR (absoluto): {sessions_path}")
    print(f"✓ Sessions DIR existe? {sessions_path.exists()}")
    
    # ========== TESTE 4: Validação ==========
    print(f"\n[TESTE 4] Validação de configurações")
    try:
        Config.validate()
        print("✓ Todas as configurações são válidas!")
    except ConfigurationError as e:
        print(f"✗ Erro de configuração detectado:")
        print(f"  {e}")
        print("\n⚠️  Corrija o arquivo .env e/ou crie os arquivos necessários")
    
    # ========== TESTE 5: Resumo de configurações ==========
    print(f"\n[TESTE 5] Resumo de configurações (sem dados sensíveis)")
    summary = Config.get_config_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # ========== TESTE 6: Instância global ==========
    print(f"\n[TESTE 6] Instância global 'config'")
    print(f"✓ config.API_KEY configurada: {'Sim' if config.API_KEY else 'Não'}")
    print(f"✓ config.MAX_CONCURRENT_REQUESTS: {config.MAX_CONCURRENT_REQUESTS}")
    
    # ========== TESTE 7: Verificar .env ==========
    print(f"\n[TESTE 7] Verificar arquivo .env")
    env_file = Config.BASE_DIR / '.env'
    if env_file.exists():
        print(f"✓ Arquivo .env encontrado: {env_file}")
        with open(env_file, 'r') as f:
            lines = f.readlines()
        print(f"✓ Linhas no .env: {len(lines)}")
        print(f"✓ Variáveis definidas:")
        for line in lines:
            if line.strip() and not line.startswith('#'):
                key = line.split('=')[0]
                print(f"    - {key}")
    else:
        print(f"✗ Arquivo .env NÃO encontrado em: {env_file}")
        print("  Crie o arquivo .env na raiz do projeto!")
    
    # ========== TESTE 8: Verificar accounts.csv ==========
    print(f"\n[TESTE 8] Verificar arquivo accounts.csv")
    if accounts_path.exists():
        print(f"✓ Arquivo accounts.csv encontrado")
        # Ler primeira linha para verificar header
        with open(accounts_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
        print(f"✓ Header: {first_line[:100]}...")
    else:
        print(f"✗ Arquivo accounts.csv NÃO encontrado em: {accounts_path}")
        print("  Crie o arquivo com suas contas do Instagram!")
    
    # ========== TESTE 9: Diretório de sessões ==========
    print(f"\n[TESTE 9] Diretório de sessões")
    if sessions_path.exists():
        print(f"✓ Diretório de sessões existe: {sessions_path}")
        session_files = list(sessions_path.glob('*.json'))
        print(f"✓ Arquivos de sessão encontrados: {len(session_files)}")
    else:
        print(f"⚠️  Diretório de sessões será criado: {sessions_path}")
    
    print("\n✅ Teste de configurações concluído!\n")
    
    # Retornar se passou ou não
    try:
        Config.validate()
        return True
    except ConfigurationError:
        return False


if __name__ == "__main__":
    success = test_config()
    if not success:
        print("\n⚠️  ATENÇÃO: Corrija os erros de configuração antes de continuar!")
        exit(1)
    else:
        print("✅ Configuração OK! Pronto para próxima fase.")
        exit(0)