"""
Middleware de autenticação para validar API Key
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.config import Config
from app.utils.logger import get_logger
from app.utils.exceptions import AuthenticationError

logger = get_logger("auth_middleware")

security = HTTPBearer()


async def verify_api_key(request: Request, credentials: HTTPAuthorizationCredentials = None) -> bool:
    """
    Verifica se a API key no header Authorization é válida
    
    Args:
        request: Request do FastAPI
        credentials: Credenciais do header Authorization
        
    Returns:
        True se autenticado
        
    Raises:
        HTTPException: Se não autenticado
    """
    # Extrair token do header Authorization
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        logger.warning(f"Requisição sem header Authorization de {request.client.host}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header Authorization não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Remover prefixo "Bearer " se existir
    token = auth_header
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
    
    # Validar token
    if token != Config.API_KEY:
        logger.warning(f"Tentativa de acesso com API key inválida de {request.client.host}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug(f"Requisição autenticada de {request.client.host}")
    return True


def get_api_key_from_header(authorization: str) -> Optional[str]:
    """
    Extrai API key do header Authorization
    
    Args:
        authorization: Valor do header Authorization
        
    Returns:
        API key ou None
    """
    if not authorization:
        return None
    
    # Remover prefixo "Bearer " se existir
    if authorization.startswith("Bearer "):
        return authorization[7:]
    
    return authorization


class AuthMiddleware:
    """
    Middleware de autenticação para FastAPI
    Pode ser usado como dependency em rotas
    """
    
    def __init__(self):
        self.api_key = Config.API_KEY
    
    async def __call__(self, request: Request):
        """
        Valida autenticação na requisição
        
        Args:
            request: Request do FastAPI
            
        Raises:
            HTTPException: Se não autenticado
        """
        await verify_api_key(request)