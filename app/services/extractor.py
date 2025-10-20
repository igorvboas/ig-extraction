"""
Serviço de extração de dados do Instagram (posts e stories)
"""
from typing import List, Optional
from datetime import datetime

from instagrapi.exceptions import (
    UserNotFound,
    PrivateError,
    MediaError,
    RateLimitError,
    PleaseWaitFewMinutes,
    LoginRequired
)
from pydantic import ValidationError

from app.services.instagram_client import InstagramClient
from app.services.account_manager import AccountManager
from app.models.requests import Post, Story, MediaItem
from app.config import Config
from app.utils.logger import get_logger
from app.utils.exceptions import (
    ProfileNotFound,
    PrivateProfileError,
    RateLimitExceeded,
    ExtractionError,
    MaxRetriesExceeded,
    AccountPoolExhausted
)

logger = get_logger("extractor")


class InstagramExtractor:
    """
    Responsável por extrair posts e stories do Instagram
    Gerencia retry logic e rotação de contas
    """
    
    def __init__(self, account_manager: AccountManager):
        """
        Inicializa o extractor
        
        Args:
            account_manager: Gerenciador de contas
        """
        self.account_manager = account_manager
        logger.info("InstagramExtractor inicializado")
    
    def extract_posts(self, username: str, quantity: int) -> List[Post]:
        """
        Extrai posts de um perfil do Instagram
        
        Args:
            username: Username do perfil (sem @)
            quantity: Quantidade de posts a extrair
            
        Returns:
            Lista de Posts
            
        Raises:
            ProfileNotFound: Se perfil não existir
            PrivateProfileError: Se perfil for privado e não tiver acesso
            MaxRetriesExceeded: Se exceder tentativas
        """
        logger.info(f"Iniciando extração de {quantity} posts de @{username}")
        
        max_retries = Config.MAX_RETRIES_PER_REQUEST
        attempt = 0
        
        while attempt < max_retries:
            attempt += 1
            
            try:
                # Obter conta disponível
                account = self.account_manager.get_next_account()
                logger.info(f"Tentativa {attempt}/{max_retries} com conta: {account.username}")
                
                # Criar cliente e fazer extração
                with InstagramClient(account) as client:
                    # Obter user_id
                    user_id = client.get_user_id_from_username(username)
                    
                    # Extrair medias
                    medias = client.client.user_medias(user_id, amount=quantity)
                    
                    # Converter para nosso formato
                    posts = self._convert_medias_to_posts(medias, client)
                    
                    # Marcar conta como usada com sucesso
                    self.account_manager.mark_account_used(account.username)
                    
                    logger.info(f"✓ Extração bem-sucedida: {len(posts)} posts obtidos")
                    return posts
                    
            except UserNotFound as e:
                logger.error(f"Perfil @{username} não encontrado")
                raise ProfileNotFound(f"Perfil @{username} não existe")
            
            except PrivateError as e:
                logger.warning(f"Perfil @{username} é privado")
                # Perfil privado: tentar com outra conta que possa ter acesso
                if attempt < max_retries:
                    logger.info("Tentando com outra conta...")
                    continue
                else:
                    raise PrivateProfileError(f"Perfil @{username} é privado e nenhuma conta tem acesso")
            
            except (RateLimitError, PleaseWaitFewMinutes) as e:
                logger.warning(f"Rate limit atingido: {e}")
                # Congelar conta e tentar com outra
                self.account_manager.freeze_account(
                    account.username,
                    duration_minutes=60,
                    reason="Rate limit exceeded"
                )
                
                if attempt < max_retries:
                    logger.info("Tentando com outra conta...")
                    continue
                else:
                    raise RateLimitExceeded("Rate limit excedido em todas as tentativas")
            
            except LoginRequired as e:
                logger.error(f"Login requerido: {e}")
                # Congelar conta e tentar com outra
                self.account_manager.freeze_account(
                    account.username,
                    duration_minutes=120,
                    reason="Login required"
                )
                
                if attempt < max_retries:
                    logger.info("Tentando com outra conta...")
                    continue
                else:
                    raise ExtractionError("Falha de autenticação em todas as tentativas")
            
            except ValidationError as e:
                logger.error(f"Erro de validação do Pydantic: {e}")
                logger.info("Tentando com outra conta (possível problema de versão da API)...")
                self.account_manager.mark_account_error(account.username, f"Validation error: {str(e)[:100]}")
                
                if attempt < max_retries:
                    continue
                else:
                    raise ExtractionError(f"Erro de validação persistente. Atualize o instagrapi: pip install --upgrade instagrapi")
            
            except AccountPoolExhausted as e:
                logger.error("Pool de contas esgotado")
                raise
            
            except Exception as e:
                logger.error(f"Erro inesperado na tentativa {attempt}: {e}")
                self.account_manager.mark_account_error(account.username, str(e))
                
                if attempt < max_retries:
                    logger.info("Tentando novamente...")
                    continue
                else:
                    raise ExtractionError(f"Falha após {max_retries} tentativas: {e}")
        
        raise MaxRetriesExceeded(f"Excedido número máximo de tentativas ({max_retries})")
    
    def extract_stories(self, username: str) -> List[Story]:
        """
        Extrai stories de um perfil do Instagram
        
        Args:
            username: Username do perfil (sem @)
            
        Returns:
            Lista de Stories
            
        Raises:
            ProfileNotFound: Se perfil não existir
            MaxRetriesExceeded: Se exceder tentativas
        """
        logger.info(f"Iniciando extração de stories de @{username}")
        
        max_retries = Config.MAX_RETRIES_PER_REQUEST
        attempt = 0
        
        while attempt < max_retries:
            attempt += 1
            
            try:
                # Obter conta disponível
                account = self.account_manager.get_next_account()
                logger.info(f"Tentativa {attempt}/{max_retries} com conta: {account.username}")
                
                # Criar cliente e fazer extração
                with InstagramClient(account) as client:
                    # Obter user_id
                    user_id = client.get_user_id_from_username(username)
                    
                    # Extrair stories
                    stories_data = client.client.user_stories(user_id)
                    
                    # Converter para nosso formato
                    stories = self._convert_stories_data(stories_data)
                    
                    # Marcar conta como usada com sucesso
                    self.account_manager.mark_account_used(account.username)
                    
                    logger.info(f"✓ Extração bem-sucedida: {len(stories)} stories obtidos")
                    return stories
                    
            except UserNotFound as e:
                logger.error(f"Perfil @{username} não encontrado")
                raise ProfileNotFound(f"Perfil @{username} não existe")
            
            except (RateLimitError, PleaseWaitFewMinutes) as e:
                logger.warning(f"Rate limit atingido: {e}")
                self.account_manager.freeze_account(
                    account.username,
                    duration_minutes=60,
                    reason="Rate limit exceeded"
                )
                
                if attempt < max_retries:
                    continue
                else:
                    raise RateLimitExceeded("Rate limit excedido em todas as tentativas")
            
            except ValidationError as e:
                logger.error(f"Erro de validação do Pydantic (stories): {e}")
                logger.info("Tentando com outra conta (possível problema de versão da API)...")
                self.account_manager.mark_account_error(account.username, f"Validation error: {str(e)[:100]}")
                
                if attempt < max_retries:
                    continue
                else:
                    raise ExtractionError(f"Erro de validação persistente. Atualize o instagrapi: pip install --upgrade instagrapi")
            
            except AccountPoolExhausted as e:
                logger.error("Pool de contas esgotado")
                raise
            
            except Exception as e:
                logger.error(f"Erro inesperado na tentativa {attempt}: {e}")
                self.account_manager.mark_account_error(account.username, str(e))
                
                if attempt < max_retries:
                    continue
                else:
                    raise ExtractionError(f"Falha após {max_retries} tentativas: {e}")
        
        raise MaxRetriesExceeded(f"Excedido número máximo de tentativas ({max_retries})")
    
    def _convert_medias_to_posts(self, medias, client: InstagramClient) -> List[Post]:
        """
        Converte objetos Media do instagrapi para nossos Posts
        
        Args:
            medias: Lista de Media do instagrapi
            client: Cliente Instagram (para obter URLs)
            
        Returns:
            Lista de Posts
        """
        posts = []
        
        for media in medias:
            try:
                # Extrair mídias (para carrosséis)
                media_items = []
                
                if media.media_type == 8:  # Album/Carousel
                    # Obter todas as mídias do carrossel
                    for resource in media.resources:
                        media_item = MediaItem(
                            media_type=resource.media_type,
                            media_url=str(resource.thumbnail_url) if resource.thumbnail_url else None,
                            thumbnail_url=str(resource.thumbnail_url) if resource.thumbnail_url else None,
                            video_url=str(resource.video_url) if resource.media_type == 2 and resource.video_url else None
                        )
                        media_items.append(media_item)
                else:
                    # Post simples (foto ou vídeo)
                    media_item = MediaItem(
                        media_type=media.media_type,
                        media_url=str(media.thumbnail_url) if media.thumbnail_url else None,
                        thumbnail_url=str(media.thumbnail_url) if media.thumbnail_url else None,
                        video_url=str(media.video_url) if media.media_type == 2 and media.video_url else None
                    )
                    media_items.append(media_item)
                
                # Criar Post
                post = Post(
                    id=str(media.pk),
                    code=media.code,
                    caption=media.caption_text if media.caption_text else "",
                    like_count=media.like_count,
                    comment_count=media.comment_count,
                    media_type=media.media_type,
                    taken_at=media.taken_at.isoformat() if media.taken_at else datetime.now().isoformat(),
                    medias=media_items
                )
                
                posts.append(post)
                
            except Exception as e:
                logger.warning(f"Erro ao converter media {media.pk}: {e}")
                continue
        
        return posts
    
    def _convert_stories_data(self, stories_data) -> List[Story]:
        """
        Converte objetos Story do instagrapi para nossos Stories
        
        Args:
            stories_data: Lista de Story do instagrapi
            
        Returns:
            Lista de Stories
        """
        stories = []
        
        for story in stories_data:
            try:
                # Pegar campos com fallback seguro
                story_id = str(getattr(story, 'pk', getattr(story, 'id', 'unknown')))
                media_type = getattr(story, 'media_type', 1)
                thumbnail_url = getattr(story, 'thumbnail_url', None)
                video_url = getattr(story, 'video_url', None)
                taken_at = getattr(story, 'taken_at', None)
                expiring_at = getattr(story, 'expiring_at', None)
                
                story_obj = Story(
                    id=story_id,
                    media_type=media_type,
                    media_url=str(thumbnail_url) if media_type == 1 and thumbnail_url else None,
                    video_url=str(video_url) if media_type == 2 and video_url else None,
                    thumbnail_url=str(thumbnail_url) if thumbnail_url else None,
                    taken_at=taken_at.isoformat() if taken_at else datetime.now().isoformat(),
                    expiring_at=expiring_at.isoformat() if expiring_at else datetime.now().isoformat()
                )
                
                stories.append(story_obj)
                
            except Exception as e:
                logger.warning(f"Erro ao converter story {getattr(story, 'pk', 'unknown')}: {e}")
                continue
        
        return stories