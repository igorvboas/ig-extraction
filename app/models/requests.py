"""
Pydantic models para requisições e respostas da API
"""
from typing import List, Optional, Any
from pydantic import BaseModel, Field, validator


# ==================== REQUEST MODELS ====================

class PostsRequest(BaseModel):
    """Request para extrair posts de um perfil"""
    username: str = Field(..., description="Username do perfil (sem @)", min_length=1, max_length=30)
    quantity: int = Field(..., description="Quantidade de posts a extrair", ge=1, le=50)
    
    @validator('username')
    def validate_username(cls, v):
        """Remove @ se fornecido e valida caracteres"""
        username = v.strip().lstrip('@')
        if not username:
            raise ValueError("Username não pode ser vazio")
        # Instagram usernames: alfanuméricos, pontos e underscores
        if not all(c.isalnum() or c in '._' for c in username):
            raise ValueError("Username contém caracteres inválidos")
        return username
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "example_user",
                "quantity": 10
            }
        }


class StoriesRequest(BaseModel):
    """Request para extrair stories de um perfil"""
    username: str = Field(..., description="Username do perfil (sem @)", min_length=1, max_length=30)
    
    @validator('username')
    def validate_username(cls, v):
        """Remove @ se fornecido e valida caracteres"""
        username = v.strip().lstrip('@')
        if not username:
            raise ValueError("Username não pode ser vazio")
        if not all(c.isalnum() or c in '._' for c in username):
            raise ValueError("Username contém caracteres inválidos")
        return username
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "example_user"
            }
        }


# ==================== RESPONSE MODELS ====================

class MediaItem(BaseModel):
    """Representa uma mídia (foto/vídeo)"""
    media_type: int = Field(..., description="Tipo: 1=Photo, 2=Video, 8=Album")
    media_url: Optional[str] = Field(None, description="URL da mídia")
    thumbnail_url: Optional[str] = Field(None, description="URL da thumbnail")
    video_url: Optional[str] = Field(None, description="URL do vídeo (se for vídeo)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "media_type": 1,
                "media_url": "https://instagram.com/...",
                "thumbnail_url": "https://instagram.com/..."
            }
        }


class Post(BaseModel):
    """Representa um post do Instagram"""
    id: str = Field(..., description="ID único do post")
    code: str = Field(..., description="Shortcode do post")
    caption: Optional[str] = Field(None, description="Legenda/descrição do post")
    like_count: int = Field(0, description="Número de curtidas")
    comment_count: int = Field(0, description="Número de comentários")
    media_type: int = Field(..., description="Tipo: 1=Photo, 2=Video, 8=Album")
    taken_at: str = Field(..., description="Data de publicação")
    medias: List[MediaItem] = Field(default_factory=list, description="Lista de mídias (para carrosséis)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "1234567890",
                "code": "ABC123",
                "caption": "Exemplo de post",
                "like_count": 100,
                "comment_count": 10,
                "media_type": 1,
                "taken_at": "2025-10-15T12:00:00",
                "medias": [
                    {
                        "media_type": 1,
                        "media_url": "https://instagram.com/..."
                    }
                ]
            }
        }


class Story(BaseModel):
    """Representa um story do Instagram"""
    id: str = Field(..., description="ID único do story")
    media_type: int = Field(..., description="Tipo: 1=Photo, 2=Video")
    media_url: Optional[str] = Field(None, description="URL da mídia")
    video_url: Optional[str] = Field(None, description="URL do vídeo (se for vídeo)")
    thumbnail_url: Optional[str] = Field(None, description="URL da thumbnail")
    taken_at: str = Field(..., description="Data de publicação")
    expiring_at: str = Field(..., description="Data de expiração (24h)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "1234567890",
                "media_type": 2,
                "video_url": "https://instagram.com/...",
                "taken_at": "2025-10-15T12:00:00",
                "expiring_at": "2025-10-16T12:00:00"
            }
        }


class PostsResponse(BaseModel):
    """Response para extração de posts"""
    success: bool = Field(..., description="Se a operação foi bem-sucedida")
    username: str = Field(..., description="Username do perfil extraído")
    total_posts: int = Field(..., description="Total de posts retornados")
    posts: List[Post] = Field(default_factory=list, description="Lista de posts")
    message: Optional[str] = Field(None, description="Mensagem adicional")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "username": "example_user",
                "total_posts": 10,
                "posts": [],
                "message": "Posts extraídos com sucesso"
            }
        }


class StoriesResponse(BaseModel):
    """Response para extração de stories"""
    success: bool = Field(..., description="Se a operação foi bem-sucedida")
    username: str = Field(..., description="Username do perfil extraído")
    total_stories: int = Field(..., description="Total de stories retornados")
    stories: List[Story] = Field(default_factory=list, description="Lista de stories")
    message: Optional[str] = Field(None, description="Mensagem adicional")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "username": "example_user",
                "total_stories": 5,
                "stories": [],
                "message": "Stories extraídos com sucesso"
            }
        }


class ErrorResponse(BaseModel):
    """Response para erros"""
    success: bool = Field(False, description="Sempre False para erros")
    error: str = Field(..., description="Tipo de erro")
    message: str = Field(..., description="Mensagem de erro detalhada")
    details: Optional[Any] = Field(None, description="Detalhes adicionais do erro")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "ProfileNotFound",
                "message": "Perfil não encontrado",
                "details": None
            }
        }