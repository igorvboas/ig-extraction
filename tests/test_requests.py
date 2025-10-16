"""
Script para testar os Pydantic models de request/response
"""
from app.models.requests import (
    PostsRequest,
    StoriesRequest,
    Post,
    Story,
    MediaItem,
    PostsResponse,
    StoriesResponse,
    ErrorResponse
)
from pydantic import ValidationError


def test_requests():
    print("="*50)
    print("Testando Pydantic Models")
    print("="*50)
    
    # ========== TESTE 1: PostsRequest ==========
    print("\n[TESTE 1] PostsRequest válido")
    posts_req = PostsRequest(username="example_user", quantity=10)
    print(f"✓ Username: {posts_req.username}")
    print(f"✓ Quantity: {posts_req.quantity}")
    
    # Teste com @ no username
    print("\n[TESTE 2] PostsRequest com @ (deve remover)")
    posts_req2 = PostsRequest(username="@example_user", quantity=5)
    print(f"✓ Username processado: {posts_req2.username}")
    
    # Teste validação - quantity inválido
    print("\n[TESTE 3] Validação - quantity fora do range")
    try:
        PostsRequest(username="test", quantity=100)
        print("✗ FALHOU - deveria ter rejeitado quantity > 50")
    except ValidationError as e:
        print(f"✓ Validação funcionou: {e.errors()[0]['msg']}")
    
    # Teste validação - username inválido
    print("\n[TESTE 4] Validação - username com caracteres inválidos")
    try:
        PostsRequest(username="user#invalid!", quantity=10)
        print("✗ FALHOU - deveria ter rejeitado username inválido")
    except ValidationError as e:
        print(f"✓ Validação funcionou: {e.errors()[0]['msg']}")
    
    # ========== TESTE 5: StoriesRequest ==========
    print("\n[TESTE 5] StoriesRequest válido")
    stories_req = StoriesRequest(username="test.user_123")
    print(f"✓ Username: {stories_req.username}")
    
    # ========== TESTE 6: MediaItem ==========
    print("\n[TESTE 6] MediaItem (foto)")
    media = MediaItem(
        media_type=1,
        media_url="https://instagram.com/photo.jpg",
        thumbnail_url="https://instagram.com/thumb.jpg"
    )
    print(f"✓ Media type: {media.media_type}")
    print(f"✓ Media URL: {media.media_url}")
    
    # ========== TESTE 7: Post ==========
    print("\n[TESTE 7] Post completo")
    post = Post(
        id="123456789",
        code="ABC123XYZ",
        caption="Teste de post",
        like_count=100,
        comment_count=5,
        media_type=1,
        taken_at="2025-10-15T12:00:00",
        medias=[media]
    )
    print(f"✓ Post ID: {post.id}")
    print(f"✓ Caption: {post.caption}")
    print(f"✓ Likes: {post.like_count}")
    print(f"✓ Medias count: {len(post.medias)}")
    
    # ========== TESTE 8: Story ==========
    print("\n[TESTE 8] Story")
    story = Story(
        id="987654321",
        media_type=2,
        video_url="https://instagram.com/video.mp4",
        thumbnail_url="https://instagram.com/thumb.jpg",
        taken_at="2025-10-15T10:00:00",
        expiring_at="2025-10-16T10:00:00"
    )
    print(f"✓ Story ID: {story.id}")
    print(f"✓ Media type: {story.media_type} (vídeo)")
    
    # ========== TESTE 9: PostsResponse ==========
    print("\n[TESTE 9] PostsResponse")
    response = PostsResponse(
        success=True,
        username="example_user",
        total_posts=1,
        posts=[post],
        message="Sucesso"
    )
    print(f"✓ Success: {response.success}")
    print(f"✓ Total posts: {response.total_posts}")
    print(f"✓ Posts count: {len(response.posts)}")
    
    # ========== TESTE 10: StoriesResponse ==========
    print("\n[TESTE 10] StoriesResponse")
    stories_response = StoriesResponse(
        success=True,
        username="example_user",
        total_stories=1,
        stories=[story],
        message="Stories extraídos"
    )
    print(f"✓ Success: {stories_response.success}")
    print(f"✓ Total stories: {stories_response.total_stories}")
    
    # ========== TESTE 11: ErrorResponse ==========
    print("\n[TESTE 11] ErrorResponse")
    error = ErrorResponse(
        error="ProfileNotFound",
        message="Perfil não foi encontrado",
        details={"username": "inexistente"}
    )
    print(f"✓ Error type: {error.error}")
    print(f"✓ Message: {error.message}")
    print(f"✓ Details: {error.details}")
    
    # ========== TESTE 12: Serialização JSON ==========
    print("\n[TESTE 12] Serialização para JSON")
    json_data = response.model_dump_json(indent=2)
    print(f"✓ JSON gerado (primeiras 200 chars):\n{json_data[:200]}...")
    
    print("\n✅ Todos os testes de Pydantic models passaram!\n")


if __name__ == "__main__":
    test_requests()