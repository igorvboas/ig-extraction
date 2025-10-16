"""
Exceções customizadas para a API de extração do Instagram
"""


class InstagramAPIException(Exception):
    """Exceção base para todas as exceções da API"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(InstagramAPIException):
    """Erro de autenticação da API (header Authorization inválido)"""
    pass


class AccountPoolExhausted(InstagramAPIException):
    """Todas as contas do pool estão indisponíveis ou em quarentena"""
    pass


class AccountNotAvailable(InstagramAPIException):
    """Conta específica não está disponível para uso"""
    pass


class AccountLoginFailed(InstagramAPIException):
    """Falha ao fazer login com a conta do Instagram"""
    pass


class SessionLoadError(InstagramAPIException):
    """Erro ao carregar sessão persistida de uma conta"""
    pass


class ExtractionError(InstagramAPIException):
    """Erro genérico durante extração de dados"""
    pass


class ProfileNotFound(ExtractionError):
    """Perfil do Instagram não foi encontrado"""
    pass


class PrivateProfileError(ExtractionError):
    """Perfil é privado e a conta não tem permissão"""
    pass


class MediaDownloadError(ExtractionError):
    """Erro ao baixar mídia (foto/vídeo)"""
    pass


class RateLimitExceeded(ExtractionError):
    """Limite de taxa excedido pelo Instagram"""
    pass


class ProxyError(InstagramAPIException):
    """Erro relacionado ao proxy"""
    pass


class ConfigurationError(InstagramAPIException):
    """Erro de configuração (arquivo .env, accounts.csv, etc)"""
    pass


class CSVParseError(ConfigurationError):
    """Erro ao fazer parse do accounts.csv"""
    pass


class InvalidRequestError(InstagramAPIException):
    """Requisição inválida (parâmetros faltando ou incorretos)"""
    pass


class MaxRetriesExceeded(InstagramAPIException):
    """Número máximo de tentativas excedido"""
    pass