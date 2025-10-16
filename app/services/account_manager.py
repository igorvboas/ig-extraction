"""
Gerenciador de pool de contas do Instagram
"""
import pandas as pd
from typing import List, Optional
from pathlib import Path
import threading
from app.models.account import Account
from app.config import Config
from app.utils.logger import get_logger
from app.utils.exceptions import (
    AccountPoolExhausted,
    AccountNotAvailable,
    CSVParseError,
    ConfigurationError
)

logger = get_logger("account_manager")


class AccountManager:
    """
    Gerencia o pool de contas do Instagram
    Responsável por carregar, rotacionar e gerenciar estado das contas
    """
    
    def __init__(self, csv_path: Optional[str] = None):
        """
        Inicializa o gerenciador de contas
        
        Args:
            csv_path: Caminho do arquivo CSV (usa Config se não fornecido)
        """
        self.csv_path = csv_path or Config.get_absolute_path(Config.ACCOUNTS_CSV_PATH)
        self.accounts: List[Account] = []
        self.current_index = 0
        self._lock = threading.Lock()  # Thread-safe para requisições concorrentes
        
        logger.info(f"Inicializando AccountManager com CSV: {self.csv_path}")
        self._load_accounts()
    
    def _load_accounts(self):
        """
        Carrega contas do arquivo CSV
        
        Raises:
            CSVParseError: Se houver erro ao ler o CSV
            ConfigurationError: Se o arquivo não existir
        """
        if not Path(self.csv_path).exists():
            raise ConfigurationError(f"Arquivo CSV não encontrado: {self.csv_path}")
        
        try:
            # Ler CSV (detectar separador automaticamente)
            # Primeiro tenta ler linha para detectar separador
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
            
            # Determinar separador (ponto-e-vírgula ou espaço)
            separator = ';' if ';' in first_line else ' '
            logger.info(f"Detectado separador do CSV: '{separator}'")
            
            # Ler CSV com separador correto
            df = pd.read_csv(self.csv_path, sep=separator, skipinitialspace=True)
            
            # Verificar colunas necessárias
            required_columns = ['email', 'username', 'password', 'status', 
                              'created_at', 'fingerprint', 'proxy_used', 'thread_id']
            missing_columns = set(required_columns) - set(df.columns)
            if missing_columns:
                raise CSVParseError(f"Colunas faltando no CSV: {missing_columns}")
            
            # Criar objetos Account
            for _, row in df.iterrows():
                try:
                    account = Account(
                        email=row['email'],
                        username=row['username'],
                        password=row['password'],
                        status=row['status'],
                        created_at=str(row['created_at']),
                        fingerprint=row['fingerprint'],
                        proxy_used=row['proxy_used'],
                        thread_id=int(row['thread_id'])
                    )
                    self.accounts.append(account)
                except Exception as e:
                    logger.warning(f"Erro ao processar conta {row.get('username', 'unknown')}: {e}")
                    continue
            
            logger.info(f"✓ Carregadas {len(self.accounts)} contas do CSV")
            
            # Log de estatísticas
            available = sum(1 for acc in self.accounts if acc.is_available())
            logger.info(f"  - Contas disponíveis: {available}/{len(self.accounts)}")
            logger.info(f"  - Contas com status 'success': {sum(1 for acc in self.accounts if acc.status == 'success')}")
            
            if len(self.accounts) == 0:
                raise CSVParseError("Nenhuma conta válida encontrada no CSV")
            
        except pd.errors.ParserError as e:
            raise CSVParseError(f"Erro ao fazer parse do CSV: {e}")
        except Exception as e:
            if isinstance(e, (CSVParseError, ConfigurationError)):
                raise
            raise CSVParseError(f"Erro inesperado ao carregar CSV: {e}")
    
    def get_next_account(self) -> Account:
        """
        Retorna a próxima conta disponível (rotação round-robin)
        
        Returns:
            Account disponível
            
        Raises:
            AccountPoolExhausted: Se nenhuma conta estiver disponível
        """
        with self._lock:
            attempts = 0
            max_attempts = len(self.accounts)
            
            while attempts < max_attempts:
                # Pegar conta atual
                account = self.accounts[self.current_index]
                
                # Avançar índice (round-robin)
                self.current_index = (self.current_index + 1) % len(self.accounts)
                attempts += 1
                
                # Verificar se está disponível
                if account.is_available():
                    logger.info(f"✓ Conta selecionada: {account.username} (uso: {account.usage_count}x)")
                    return account
                else:
                    reason = "frozen" if account.is_frozen else f"status={account.status}"
                    logger.debug(f"  Conta {account.username} indisponível ({reason}), tentando próxima...")
            
            # Nenhuma conta disponível
            raise AccountPoolExhausted(
                "Todas as contas estão indisponíveis ou em quarentena",
                details=self.get_pool_status()
            )
    
    def get_account_by_username(self, username: str) -> Optional[Account]:
        """
        Busca uma conta específica pelo username
        
        Args:
            username: Username da conta
            
        Returns:
            Account ou None se não encontrada
        """
        for account in self.accounts:
            if account.username == username:
                return account
        return None
    
    def get_available_accounts(self) -> List[Account]:
        """
        Retorna lista de todas as contas disponíveis
        
        Returns:
            Lista de contas disponíveis
        """
        return [acc for acc in self.accounts if acc.is_available()]
    
    def freeze_account(self, username: str, duration_minutes: int = None, reason: str = None):
        """
        Congela uma conta específica
        
        Args:
            username: Username da conta
            duration_minutes: Duração do congelamento (usa Config se None)
            reason: Motivo do congelamento
        """
        account = self.get_account_by_username(username)
        if account:
            duration = duration_minutes or Config.ACCOUNT_FREEZE_DURATION_MINUTES
            account.freeze(duration_minutes=duration, reason=reason)
            logger.warning(f"⚠️  Conta {username} congelada por {duration} minutos. Motivo: {reason}")
        else:
            logger.error(f"Conta {username} não encontrada para congelar")
    
    def unfreeze_account(self, username: str):
        """
        Descongela uma conta específica
        
        Args:
            username: Username da conta
        """
        account = self.get_account_by_username(username)
        if account:
            account.unfreeze()
            logger.info(f"✓ Conta {username} descongelada")
        else:
            logger.error(f"Conta {username} não encontrada para descongelar")
    
    def mark_account_used(self, username: str):
        """
        Marca que uma conta foi usada
        
        Args:
            username: Username da conta
        """
        account = self.get_account_by_username(username)
        if account:
            account.mark_used()
            logger.debug(f"Conta {username} marcada como usada (total: {account.usage_count}x)")
    
    def mark_account_error(self, username: str, error_message: str):
        """
        Registra um erro em uma conta
        
        Args:
            username: Username da conta
            error_message: Mensagem de erro
        """
        account = self.get_account_by_username(username)
        if account:
            account.mark_error(error_message)
            logger.error(f"✗ Erro registrado na conta {username}: {error_message}")
    
    def get_pool_status(self) -> dict:
        """
        Retorna status do pool de contas
        
        Returns:
            Dicionário com estatísticas
        """
        total = len(self.accounts)
        available = len(self.get_available_accounts())
        frozen = sum(1 for acc in self.accounts if acc.is_frozen)
        failed_status = sum(1 for acc in self.accounts if acc.status != 'success')
        
        return {
            'total_accounts': total,
            'available': available,
            'frozen': frozen,
            'failed_status': failed_status,
            'accounts': [acc.to_dict() for acc in self.accounts]
        }
    
    def reload_accounts(self):
        """
        Recarrega contas do CSV (útil se o arquivo foi atualizado)
        """
        logger.info("Recarregando contas do CSV...")
        self.accounts.clear()
        self.current_index = 0
        self._load_accounts()
    
    def __len__(self) -> int:
        """Retorna número total de contas"""
        return len(self.accounts)
    
    def __repr__(self) -> str:
        available = len(self.get_available_accounts())
        return f"AccountManager(total={len(self.accounts)}, available={available})"