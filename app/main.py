"""
FastAPI application - API de extração do Instagram
"""
from fastapi import FastAPI, Depends, Request, status, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.models.requests import (
    PostsRequest,
    PostsResponse,
    StoriesRequest,
    StoriesResponse,
    ErrorResponse
)
from app.services.account_manager import AccountManager
from app.services.extractor import InstagramExtractor
from app.middleware.auth import verify_api_key
from app.config import Config
from app.utils.logger import get_logger
from app.utils.exceptions import (
    InstagramAPIException,
    ProfileNotFound,
    PrivateProfileError,
    AccountPoolExhausted,
    RateLimitExceeded,
    AuthenticationError
)

logger = get_logger("main")

# Variáveis globais para managers
account_manager: AccountManager = None
extractor: InstagramExtractor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia lifecycle da aplicação (startup e shutdown)
    """
    # Startup
    logger.info("🚀 Iniciando aplicação...")
    
    global account_manager, extractor
    
    try:
        # Inicializar AccountManager
        account_manager = AccountManager()
        logger.info(f"✓ AccountManager inicializado: {len(account_manager)} contas")
        
        # Desabilitar proxies (temporário - até configurar credenciais de proxy)
        logger.info("⚠️  Desabilitando proxies...")
        for account in account_manager.accounts:
            account.proxy_used = ""
        
        # Inicializar Extractor
        extractor = InstagramExtractor(account_manager)
        logger.info("✓ InstagramExtractor inicializado")
        
        # Log de configurações
        config_summary = Config.get_config_summary()
        logger.info("📊 Configurações:")
        for key, value in config_summary.items():
            logger.info(f"  {key}: {value}")
        
        logger.info("✅ Aplicação iniciada com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar aplicação: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando aplicação...")


# Criar aplicação FastAPI
app = FastAPI(
    title="Instagram Extractor API",
    description="API para extração de posts e stories do Instagram",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origins permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== EXCEPTION HANDLERS ====================

@app.exception_handler(InstagramAPIException)
async def instagram_api_exception_handler(request: Request, exc: InstagramAPIException):
    """Handler para exceções da API"""
    logger.error(f"InstagramAPIException: {exc.message}")
    
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    # Mapear exceções para status codes apropriados
    if isinstance(exc, AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, ProfileNotFound):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, (AccountPoolExhausted, RateLimitExceeded)):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif isinstance(exc, PrivateProfileError):
        status_code = status.HTTP_403_FORBIDDEN
    
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.message,
            details=exc.details
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler para exceções gerais"""
    logger.error(f"Erro não tratado: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="Erro interno do servidor",
            details={"error": str(exc)}
        ).model_dump()
    )


# ==================== ROTAS ====================

@app.get("/", tags=["Sistema"])
async def root():
    """
    Endpoint raiz - informações da API
    """
    return {
        "name": "Instagram Extractor API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "posts": "/posts",
            "stories": "/stories",
            "health": "/health",
            "status": "/status"
        }
    }


@app.get("/health", tags=["Sistema"])
async def health_check():
    """
    Health check da aplicação
    """
    pool_status = account_manager.get_pool_status()
    
    return {
        "status": "healthy",
        "accounts": {
            "total": pool_status['total_accounts'],
            "available": pool_status['available'],
            "frozen": pool_status['frozen']
        }
    }


@app.get("/status", tags=["Sistema"], dependencies=[Depends(verify_api_key)])
async def get_status():
    """
    Status detalhado do pool de contas (requer autenticação)
    """
    pool_status = account_manager.get_pool_status()
    
    return {
        "success": True,
        "pool_status": pool_status,
        "config": Config.get_config_summary()
    }


@app.post("/posts", response_model=PostsResponse, tags=["Extração"], dependencies=[Depends(verify_api_key)])
async def extract_posts(username: str = Body(...), quantity: int = Body(..., ge=1, le=50)):
    """
    Extrai posts de um perfil do Instagram
    
    - **username**: Username do perfil (sem @)
    - **quantity**: Quantidade de posts (1-50)
    
    Requer header: `Authorization: <API_KEY>`
    """
    logger.info(f"📥 POST /posts - username: {username}, quantity: {quantity}")
    
    try:
        # Extrair posts
        posts = extractor.extract_posts(username, quantity)
        
        # Montar response
        response = PostsResponse(
            success=True,
            username=username,
            total_posts=len(posts),
            posts=posts,
            message=f"Posts extraídos com sucesso de @{username}"
        )
        
        logger.info(f"✓ Extração concluída: {len(posts)} posts de @{username}")
        
        return response
        
    except InstagramAPIException:
        # Re-lançar para ser tratado pelo exception handler
        raise
    except Exception as e:
        logger.error(f"Erro ao extrair posts: {e}")
        raise


@app.post("/stories", response_model=StoriesResponse, tags=["Extração"], dependencies=[Depends(verify_api_key)])
async def extract_stories(username: str = Body(...)):
    """
    Extrai stories de um perfil do Instagram
    
    - **username**: Username do perfil (sem @)
    
    Requer header: `Authorization: <API_KEY>`
    """
    logger.info(f"📥 POST /stories - username: {username}")
    
    try:
        # Extrair stories
        stories = extractor.extract_stories(username)
        
        # Montar response
        response = StoriesResponse(
            success=True,
            username=username,
            total_stories=len(stories),
            stories=stories,
            message=f"Stories extraídos com sucesso de @{username}" if stories else f"Perfil @{username} não tem stories ativos"
        )
        
        logger.info(f"✓ Extração concluída: {len(stories)} stories de @{username}")
        
        return response
        
    except InstagramAPIException:
        # Re-lançar para ser tratado pelo exception handler
        raise
    except Exception as e:
        logger.error(f"Erro ao extrair stories: {e}")
        raise


# ==================== STARTUP MESSAGE ====================

if __name__ == "__main__":
    import uvicorn
    
    print("="*50)
    print("Instagram Extractor API")
    print("="*50)
    print(f"API Key: {Config.API_KEY[:10]}..." if Config.API_KEY else "⚠️  API Key não configurada!")
    print(f"Max concurrent requests: {Config.MAX_CONCURRENT_REQUESTS}")
    print("="*50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )