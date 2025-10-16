"""
Configurações da aplicação carregadas do arquivo .env
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from app.utils.exceptions import ConfigurationError

# Carregar variáveis de ambiente do arquivo .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """
    Classe de configuração que carrega e valida as variáveis de ambiente
    """
    
    # API Settings
    API_KEY: str = os.getenv('API_KEY', '')
    
    # Request Settings
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv('MAX_CONCURRENT_REQUESTS', '3'))
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    ACCOUNTS_CSV_PATH: str = os.getenv('ACCOUNTS_CSV_PATH', 'data/accounts.csv')
    SESSIONS_DIR_PATH: str = os.getenv('SESSIONS_DIR_PATH', 'data/sessions')
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Instagram API Settings
    INSTAGRAM_DELAY_MIN: int = int(os.getenv('INSTAGRAM_DELAY_MIN', '1'))
    INSTAGRAM_DELAY_MAX: int = int(os.getenv('INSTAGRAM_DELAY_MAX', '3'))
    
    # Account Management
    ACCOUNT_FREEZE_DURATION_MINUTES: int = int(os.getenv('ACCOUNT_FREEZE_DURATION_MINUTES', '60'))
    MAX_RETRIES_PER_REQUEST: int = int(os.getenv('MAX_RETRIES_PER_REQUEST', '3'))
    
    @classmethod
    def get_absolute_path(cls, relative_path: str) -> Path:
        """
        Converte caminho relativo para absoluto baseado no BASE_DIR
        
        Args:
            relative_path: Caminho relativo
            
        Returns:
            Path absoluto
        """
        return cls.BASE_DIR / relative_path
    
    @classmethod
    def validate(cls) -> None:
        """
        Valida se todas as configurações necessárias estão presentes e corretas
        
        Raises:
            ConfigurationError: Se alguma configuração estiver inválida
        """
        errors = []
        
        # Validar API_KEY
        if not cls.API_KEY:
            errors.append("API_KEY não está definida no arquivo .env")
        
        # Validar MAX_CONCURRENT_REQUESTS
        if cls.MAX_CONCURRENT_REQUESTS < 1:
            errors.append("MAX_CONCURRENT_REQUESTS deve ser maior que 0")
        
        # Validar ACCOUNTS_CSV_PATH existe
        accounts_path = cls.get_absolute_path(cls.ACCOUNTS_CSV_PATH)
        if not accounts_path.exists():
            errors.append(f"Arquivo de contas não encontrado: {accounts_path}")
        
        # Validar SESSIONS_DIR_PATH existe (criar se não existir)
        sessions_path = cls.get_absolute_path(cls.SESSIONS_DIR_PATH)
        if not sessions_path.exists():
            try:
                sessions_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Não foi possível criar diretório de sessões: {e}")
        
        # Validar LOG_LEVEL
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if cls.LOG_LEVEL.upper() not in valid_log_levels:
            errors.append(f"LOG_LEVEL inválido. Valores aceitos: {', '.join(valid_log_levels)}")
        
        # Validar delays
        if cls.INSTAGRAM_DELAY_MIN < 0 or cls.INSTAGRAM_DELAY_MAX < 0:
            errors.append("INSTAGRAM_DELAY_MIN e INSTAGRAM_DELAY_MAX devem ser >= 0")
        
        if cls.INSTAGRAM_DELAY_MIN > cls.INSTAGRAM_DELAY_MAX:
            errors.append("INSTAGRAM_DELAY_MIN não pode ser maior que INSTAGRAM_DELAY_MAX")
        
        # Validar freeze duration
        if cls.ACCOUNT_FREEZE_DURATION_MINUTES < 1:
            errors.append("ACCOUNT_FREEZE_DURATION_MINUTES deve ser maior que 0")
        
        # Validar max retries
        if cls.MAX_RETRIES_PER_REQUEST < 1:
            errors.append("MAX_RETRIES_PER_REQUEST deve ser maior que 0")
        
        # Se houver erros, lançar exceção
        if errors:
            error_message = "Erros de configuração encontrados:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ConfigurationError(error_message)
    
    @classmethod
    def get_config_summary(cls) -> dict:
        """
        Retorna um resumo das configurações (sem dados sensíveis)
        
        Returns:
            Dicionário com configurações
        """
        return {
            'api_key_configured': bool(cls.API_KEY),
            'max_concurrent_requests': cls.MAX_CONCURRENT_REQUESTS,
            'accounts_csv_path': str(cls.get_absolute_path(cls.ACCOUNTS_CSV_PATH)),
            'sessions_dir_path': str(cls.get_absolute_path(cls.SESSIONS_DIR_PATH)),
            'log_level': cls.LOG_LEVEL,
            'log_file': cls.LOG_FILE,
            'instagram_delay_range': f"{cls.INSTAGRAM_DELAY_MIN}-{cls.INSTAGRAM_DELAY_MAX}s",
            'account_freeze_duration': f"{cls.ACCOUNT_FREEZE_DURATION_MINUTES} minutes",
            'max_retries': cls.MAX_RETRIES_PER_REQUEST
        }


# Criar instância global de configuração
config = Config()

# Validar configurações na importação (opcional - comente se quiser validar manualmente)
try:
    config.validate()
except ConfigurationError as e:
    print(f"⚠️  AVISO: {e}")
    print("A aplicação pode não funcionar corretamente.")