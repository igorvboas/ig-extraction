# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2025-10-16

### ✨ Adicionado

- **API REST completa** com FastAPI
  - Endpoint `POST /posts` - Extração de posts
  - Endpoint `POST /stories` - Extração de stories
  - Endpoint `GET /health` - Health check
  - Endpoint `GET /status` - Status detalhado do pool
  - Endpoint `GET /` - Informações da API

- **Sistema de Autenticação**
  - Middleware de validação de API Key
  - Header `Authorization` obrigatório em rotas protegidas

- **Account Manager**
  - Pool de contas Instagram
  - Rotação automática de contas
  - Sistema de freezing temporário
  - Tracking de uso e erros por conta
  - Detecção automática de separador CSV

- **Instagram Extractor**
  - Extração robusta de posts com retry
  - Extração de stories com suporte a vídeo
  - Conversão de carrosséis (álbuns)
  - Sistema de 3 tentativas por request
  - Rotação automática em caso de falha

- **Instagram Client**
  - Sessões persistentes (cache de login)
  - Suporte a proxies configuráveis
  - Fingerprint customizável por conta
  - Auto-retry em falhas temporárias
  - Delay configurável entre requests

- **Exception Handling**
  - Exceções customizadas (`ProfileNotFound`, `RateLimitExceeded`, etc)
  - Mapeamento para HTTP status codes apropriados
  - Error responses padronizados em JSON

- **Sistema de Logs**
  - Logs estruturados com rotação
  - Níveis configuráveis (DEBUG, INFO, WARNING, ERROR)
  - Encoding UTF-8 para suporte a emojis
  - Logs separados por módulo

- **Scripts de Teste**
  - `debug_extractor.py` - Debug standalone sem API
  - `test_api_client.py` - Cliente de teste da API
  - `test_simple.py` - Testes rápidos

- **Documentação**
  - README completo com exemplos
  - Swagger UI automático (`/docs`)
  - ReDoc automático (`/redoc`)
  - Comentários detalhados no código
  - Este CHANGELOG

- **Modelos Pydantic**
  - Validação automática de requests
  - Response models com exemplos
  - Validators customizados (username, quantity)

### 🔧 Configurações

- Variáveis de ambiente via `.env`
- Configurações centralizadas em `config.py`
- Suporte a múltiplos ambientes

### 🐛 Correções

- **Erro 422 em endpoints POST**
  - Problema: FastAPI esperava wrapper no body
  - Solução: Uso correto de parâmetros `Body(...)`
  
- **Proxy Authentication Errors**
  - Problema: Proxies sem credenciais causavam erro 407
  - Solução: Desabilitação automática de proxies no startup

- **Unicode Encoding Errors**
  - Problema: Emojis causavam crashes no Windows
  - Solução: Configuração UTF-8 forçada nos logs

### 🔒 Segurança

- API Key obrigatória em rotas sensíveis
- Sessões fora do repositório (`.gitignore`)
- Accounts CSV não versionado
- CORS configurável

### 📊 Performance

- Sessões persistentes (reduz logins)
- Connection pooling HTTP
- Retry exponencial com backoff
- Cache de user_id por username

---

## [Unreleased]

### 🚧 Planejado

- [ ] Suporte a extração de Reels
- [ ] Extração de comentários
- [ ] Extração de likes
- [ ] Webhook para notificações
- [ ] Rate limiting por usuário
- [ ] Dashboard de monitoramento
- [ ] Docker e docker-compose
- [ ] CI/CD com GitHub Actions
- [ ] Métricas com Prometheus
- [ ] Cache com Redis
- [ ] Fila de tarefas com Celery

### 🔮 Em Consideração

- [ ] Suporte a múltiplos perfis por request
- [ ] Extração de highlights
- [ ] Busca por hashtags
- [ ] Extração de seguidores/seguindo
- [ ] Análise de engagement
- [ ] Export para CSV/Excel

---

## Notas de Versão

### [1.0.0] - Release Inicial

Esta é a primeira versão estável da Instagram Extractor API. Todas as features principais estão implementadas e testadas:

✅ Extração de posts e stories funcionando  
✅ Sistema de rotação de contas robusto  
✅ Retry automático em falhas  
✅ API REST completa e documentada  
✅ Logs detalhados para debugging  
✅ Testes e scripts de validação  

**Conhecido Issues:**
- Proxies requerem desabilitação manual (linha 52-55 do `main.py`)
- Encoding de emojis pode falhar em alguns terminais Windows
- Rate limits do Instagram podem variar

**Breaking Changes:**
- Nenhum (primeira versão)

---

**Formato de Versionamento:**

- **MAJOR** (1.x.x): Mudanças incompatíveis na API
- **MINOR** (x.1.x): Novas funcionalidades (compatíveis)
- **PATCH** (x.x.1): Correções de bugs

**Tags no Git:**
```bash
git tag -a v1.0.0 -m "Release inicial - Instagram Extractor API"
git push origin v1.0.0
```

