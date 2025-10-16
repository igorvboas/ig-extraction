"""
Wrapper do cliente Instagrapi com gerenciamento de sessões e exceções
"""
from instagrapi import Client
from instagrapi.exceptions import (
    LoginRequired,
    BadPassword,
    TwoFactorRequired,
    ChallengeRequired,
    FeedbackRequired,
    PleaseWaitFewMinutes,
    RateLimitError,
    UserNotFound,
    PrivateError
)
from pathlib import Path
from typing import Optional
import json

from app.models.account import Account
from app.config import Config
from app.utils.logger import get_logger
from app.utils.exceptions import (
    AccountLoginFailed,
    SessionLoadError,
    ProfileNotFound,
    PrivateProfileError,
    RateLimitExceeded
)

logger = get_logger("instagram_client")


class InstagramClient:
    """
    Wrapper do Client do Instagrapi com gerenciamento de sessões,
    proxy, fingerprint e tratamento de exceções
    """
    
    def __init__(self, account: Account):
        """
        Inicializa o cliente Instagram para uma conta específica
        
        Args:
            account: Objeto Account com credenciais e configurações
        """
        self.account = account
        self.client = Client()
        self._is_logged_in = False
        
        # Configurar delays entre requisições
        self.client.delay_range = [Config.INSTAGRAM_DELAY_MIN, Config.INSTAGRAM_DELAY_MAX]
        
        logger.info(f"Inicializando InstagramClient para: {account.username}")
        
        # Configurar proxy
        self._setup_proxy()
        
        # Configurar device settings baseado no fingerprint
        self._setup_device()
        
        # Configurar handler de exceções customizado
        self.client.handle_exception = self._handle_exception
    
    def _setup_proxy(self):
        """Configura proxy para a conta"""
        try:
            # Só configurar se proxy_used não estiver vazio
            if self.account.proxy_used and self.account.proxy_used.strip():
                proxy_url = self.account.get_proxy_url(with_protocol=True)
                self.client.set_proxy(proxy_url)
                logger.info(f"Proxy configurado: {self.account.proxy_used}")
            else:
                logger.warning("Proxy não configurado (proxy_used está vazio)")
        except Exception as e:
            logger.warning(f"Erro ao configurar proxy: {e}")
    
    def _setup_device(self):
        """Configura device settings baseado no fingerprint da conta"""
        try:
            fingerprint = self.account.fingerprint_dict
            
            # Mapear fingerprint do navegador para device Android (aproximado)
            # Instagram mobile API espera device Android
            settings = {
                "user_agent": fingerprint.get("user_agent", ""),
                "timezone_offset": self._get_timezone_offset(fingerprint.get("timezone", "America/New_York")),
                "locale": fingerprint.get("language", "en_US").replace("-", "_"),
            }
            
            # Aplicar settings se houver
            if settings["user_agent"]:
                # Note: instagrapi gera automaticamente device UUID na primeira vez
                # Aqui apenas logamos o fingerprint disponível
                logger.debug(f"Fingerprint disponível: {fingerprint}")
        
        except Exception as e:
            logger.warning(f"Erro ao configurar device: {e}")
    
    def _get_timezone_offset(self, timezone: str) -> int:
        """
        Converte timezone string para offset em segundos
        
        Args:
            timezone: Timezone (ex: "America/New_York")
            
        Returns:
            Offset em segundos
        """
        # Mapeamento simplificado de timezones comuns
        timezone_offsets = {
            "America/New_York": -18000,  # UTC-5
            "America/Chicago": -21600,   # UTC-6
            "America/Los_Angeles": -28800, # UTC-8
            "Europe/London": 0,          # UTC+0
            "Europe/Paris": 3600,        # UTC+1
            "Europe/Berlin": 3600,       # UTC+1
        }
        return timezone_offsets.get(timezone, -18000)
    
    def login(self, verification_code: str = None) -> bool:
        """
        Faz login na conta do Instagram
        Tenta carregar sessão existente primeiro, depois faz login fresh
        
        Args:
            verification_code: Código 2FA (opcional)
        
        Returns:
            True se login bem-sucedido
            
        Raises:
            AccountLoginFailed: Se não conseguir fazer login
        """
        session_file = self._get_session_file()
        
        # Tentar carregar sessão existente
        if session_file.exists():
            try:
                logger.info(f"Tentando carregar sessão de: {session_file}")
                self.client.load_settings(session_file)
                self.client.login(self.account.username, self.account.password)
                
                # Verificar se sessão é válida
                self.client.get_timeline_feed()
                
                self._is_logged_in = True
                logger.info(f"✓ Login via sessão bem-sucedido: {self.account.username}")
                return True
                
            except LoginRequired:
                logger.info("Sessão inválida, fazendo login fresh...")
            except Exception as e:
                logger.warning(f"Erro ao carregar sessão: {e}")
        
        # Login fresh
        try:
            logger.info(f"Fazendo login fresh: {self.account.username}")
            
            # Login com ou sem 2FA
            if verification_code:
                logger.info("Usando código 2FA fornecido")
                self.client.login(
                    self.account.username, 
                    self.account.password,
                    verification_code=verification_code
                )
            else:
                self.client.login(self.account.username, self.account.password)
            
            # Salvar sessão
            self._save_session()
            
            self._is_logged_in = True
            logger.info(f"✓ Login fresh bem-sucedido: {self.account.username}")
            return True
            
        except BadPassword as e:
            logger.error(f"Senha incorreta para {self.account.username}")
            raise AccountLoginFailed(f"Senha incorreta: {e}")
        
        except TwoFactorRequired as e:
            logger.error(f"2FA requerido para {self.account.username}")
            # Tentar usar código 2FA se configurado
            two_factor_code = self._get_2fa_code()
            if two_factor_code:
                try:
                    logger.info("Tentando login com código 2FA...")
                    code = self.client.two_factor_login(two_factor_code)
                    self._save_session()
                    self._is_logged_in = True
                    logger.info(f"✓ Login 2FA bem-sucedido: {self.account.username}")
                    return True
                except Exception as e2:
                    logger.error(f"Falha no 2FA: {e2}")
            
            raise AccountLoginFailed(f"2FA requerido e não configurado: {e}")
        
        except ChallengeRequired as e:
            logger.error(f"Challenge requerido para {self.account.username}")
            raise AccountLoginFailed(f"Challenge requerido: {e}")
        
        except Exception as e:
            logger.error(f"Erro ao fazer login: {e}")
            raise AccountLoginFailed(f"Falha no login: {e}")
    
    def _get_2fa_code(self) -> str:
        """
        Obtém código 2FA da conta
        Pode ser implementado de várias formas:
        - Ler do fingerprint/CSV se tiver campo totp_seed
        - Gerar via pyotp se tiver secret
        - Callback para input manual
        
        Returns:
            Código 2FA ou None
        """
        # Verificar se tem totp_seed no fingerprint
        fingerprint = self.account.fingerprint_dict
        totp_seed = fingerprint.get("totp_seed")
        
        if totp_seed:
            try:
                import pyotp
                totp = pyotp.TOTP(totp_seed)
                code = totp.now()
                logger.info("Código 2FA gerado via TOTP")
                return code
            except ImportError:
                logger.warning("pyotp não instalado, não é possível gerar código 2FA")
            except Exception as e:
                logger.warning(f"Erro ao gerar código 2FA: {e}")
        
        return None
    
    def _get_session_file(self) -> Path:
        """
        Retorna caminho do arquivo de sessão para a conta
        
        Returns:
            Path do arquivo de sessão
        """
        sessions_dir = Config.get_absolute_path(Config.SESSIONS_DIR_PATH)
        sessions_dir.mkdir(parents=True, exist_ok=True)
        return sessions_dir / f"{self.account.username}_session.json"
    
    def _save_session(self):
        """Salva sessão atual em arquivo"""
        try:
            session_file = self._get_session_file()
            self.client.dump_settings(session_file)
            logger.info(f"✓ Sessão salva: {session_file}")
        except Exception as e:
            logger.warning(f"Erro ao salvar sessão: {e}")
    
    def _handle_exception(self, client, exception):
        """
        Handler customizado de exceções do Instagram
        
        Args:
            client: Cliente instagrapi
            exception: Exceção capturada
        """
        logger.error(f"Exceção capturada: {type(exception).__name__} - {exception}")
        
        # Aqui você pode adicionar lógica específica de tratamento
        # Por enquanto, apenas loga e re-lança
        raise exception
    
    def is_logged_in(self) -> bool:
        """Retorna se está logado"""
        return self._is_logged_in
    
    def get_user_id_from_username(self, username: str) -> int:
        """
        Obtém user_id a partir do username
        
        Args:
            username: Username do Instagram
            
        Returns:
            User ID
            
        Raises:
            ProfileNotFound: Se perfil não existir
        """
        try:
            user_id = self.client.user_id_from_username(username)
            return user_id
        except UserNotFound as e:
            logger.error(f"Perfil não encontrado: {username}")
            raise ProfileNotFound(f"Perfil {username} não existe")
        except Exception as e:
            logger.error(f"Erro ao buscar user_id: {e}")
            raise
    
    def get_user_info(self, user_id: int):
        """
        Obtém informações completas do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Objeto User do instagrapi
        """
        try:
            return self.client.user_info(user_id)
        except PrivateError as e:
            raise PrivateProfileError(f"Perfil privado: {e}")
        except Exception as e:
            logger.error(f"Erro ao obter user info: {e}")
            raise
    
    def logout(self):
        """Faz logout e limpa sessão"""
        try:
            if self._is_logged_in:
                # Não há método logout explícito no instagrapi
                # Apenas marcamos como deslogado
                self._is_logged_in = False
                logger.info(f"Logout: {self.account.username}")
        except Exception as e:
            logger.warning(f"Erro ao fazer logout: {e}")
    
    def __enter__(self):
        """Context manager - entrada"""
        if not self._is_logged_in:
            self.login()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager - saída"""
        self.logout()
        return False
    
    def __repr__(self) -> str:
        status = "logged_in" if self._is_logged_in else "logged_out"
        return f"InstagramClient(username={self.account.username}, status={status})"