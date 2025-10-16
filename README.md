# Instagram Extractor API

API REST robusta para extração de posts e stories do Instagram com sistema inteligente de rotação de contas e retry automático.

## 📋 Índice

- [Features](#-features)
- [Arquitetura](#-arquitetura)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Uso](#-uso)
- [Endpoints da API](#-endpoints-da-api)
- [Modelos de Dados](#-modelos-de-dados)
- [Sistema de Contas](#-sistema-de-contas)
- [Debug e Testes](#-debug-e-testes)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

- ✅ **API REST** completa com FastAPI
- ✅ **Extração de Posts** com suporte a carrosséis
- ✅ **Extração de Stories** com URLs de mídia
- ✅ **Sistema de Rotação de Contas** automático
- ✅ **Retry Automático** em caso de falhas
- ✅ **Gerenciamento de Rate Limit** com freezing de contas
- ✅ **Autenticação via API Key**
- ✅ **Pool de Contas** com status tracking
- ✅ **Sessões Persistentes** do Instagram
- ✅ **Logs Detalhados** para debugging
- ✅ **CORS habilitado** para integração frontend
- ✅ **Documentação Automática** (Swagger/ReDoc)

---

## 🏗️ Arquitetura

O sistema utiliza uma arquitetura em camadas:

```
┌─────────────────────────────────────────────────┐
│              FastAPI Application                │
│           (main.py - Endpoints HTTP)            │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│           Instagram Extractor                   │
│      (extractor.py - Lógica de Extração)       │
│  • Retry Logic  • Account Rotation  • Error    │
└─────────────────────┬───────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼──────┐ ┌───▼────────┐ ┌─▼──────────────┐
│ Account      │ │ Instagram  │ │ Exception      │
│ Manager      │ │ Client     │ │ Handlers       │
│              │ │            │ │                │
│ • Pool       │ │ • Login    │ │ • ProfileNot   │
│ • Rotation   │ │ • Session  │ │   Found        │
│ • Freezing   │ │ • Scraping │ │ • RateLimit    │
└──────────────┘ └────────────┘ └────────────────┘
```

---

## 📁 Estrutura do Projeto

```
instagram-api/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configurações globais
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py                # Autenticação via API Key
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── account.py             # Modelo de conta Instagram
│   │   └── requests.py            # Modelos Pydantic (request/response)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── account_manager.py     # Gerenciamento do pool de contas
│   │   ├── extractor.py           # Lógica de extração (posts/stories)
│   │   └── instagram_client.py    # Cliente Instagram (instagrapi)
│   │
│   └── utils/
│       ├── __init__.py
│       ├── exceptions.py          # Exceções customizadas
│       └── logger.py              # Sistema de logs
│
├── data/
│   ├── accounts.csv               # Pool de contas Instagram
│   └── sessions/                  # Sessões persistentes
│       └── *_session.json
│
├── logs/
│   └── app.log                    # Arquivo de logs
│
├── tests/                         # Testes unitários
│   ├── test_api.py
│   ├── test_extractor.py
│   └── ...
│
├── debug_extractor.py             # Script de debug standalone
├── test_api_client.py             # Cliente de teste da API
├── requirements.txt               # Dependências Python
└── README.md                      # Este arquivo
```

---

## 📦 Instalação

### 1. Pré-requisitos

- Python 3.11+
- pip

### 2. Clone o repositório

```bash
git clone <repo-url>
cd instagram_extractor_api/instagram-api
```

### 3. Crie o ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuração

### 1. Configure o arquivo `.env`

Crie um arquivo `.env` na raiz do projeto:

```env
# API Configuration
API_KEY=sua_api_key_aqui_gere_uma_chave_segura

# Instagram Configuration
ACCOUNTS_CSV_PATH=data/accounts.csv
SESSIONS_DIR=data/sessions
LOG_FILE=logs/app.log
LOG_LEVEL=INFO

# Rate Limiting
MAX_CONCURRENT_REQUESTS=3
MAX_RETRIES_PER_REQUEST=3
INSTAGRAM_DELAY_MIN=1
INSTAGRAM_DELAY_MAX=3

# Account Management
ACCOUNT_FREEZE_DURATION_MINUTES=60
```

### 2. Configure as contas no `data/accounts.csv`

Formato do CSV (separador: `;`):

```csv
email;username;password;status;created_at;fingerprint;proxy_used;thread_id
user@email.com;username123;password123;success;2025-10-16 12:00:00;{};46.203.44.19:6018;1
```

**Campos:**
- `email`: Email da conta Instagram
- `username`: Username (sem @)
- `password`: Senha da conta
- `status`: `success`, `desligado`, etc.
- `created_at`: Data de criação
- `fingerprint`: JSON com user agent, screen size, etc.
- `proxy_used`: Proxy (formato `ip:porta`) ou vazio
- `thread_id`: ID da thread

---

## 🚀 Uso

### Iniciar a API

```bash
# Método 1: Usando uvicorn diretamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Método 2: Usando o script principal
python -m app.main
```

A API estará disponível em: `http://localhost:8000`

### Acessar Documentação Interativa

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔌 Endpoints da API

### 1. **GET /** - Informações da API

```bash
curl http://localhost:8000/
```

**Response:**
```json
{
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
```

---

### 2. **GET /health** - Health Check

Verifica se a API está online e quantas contas estão disponíveis.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "accounts": {
    "total": 107,
    "available": 1,
    "frozen": 0
  }
}
```

---

### 3. **GET /status** - Status Detalhado 🔒

Informações completas do pool de contas (requer autenticação).

```bash
curl http://localhost:8000/status \
  -H "Authorization: YOUR_API_KEY"
```

**Response:**
```json
{
  "success": true,
  "pool_status": {
    "total_accounts": 107,
    "available": 1,
    "frozen": 0,
    "accounts": [...]
  },
  "config": {
    "API_KEY": "configured",
    "MAX_RETRIES": 3
  }
}
```

---

### 4. **POST /posts** - Extrair Posts 🔒

Extrai posts de um perfil do Instagram.

```bash
curl -X POST http://localhost:8000/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: YOUR_API_KEY" \
  -d '{
    "username": "instagram",
    "quantity": 5
  }'
```

**Request Body:**
```json
{
  "username": "instagram",  // Username sem @
  "quantity": 5             // 1-50 posts
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "username": "instagram",
  "total_posts": 5,
  "posts": [
    {
      "id": "3744758141436394487",
      "code": "DP4DbBmEXv3",
      "caption": "Post caption...",
      "like_count": 164037,
      "comment_count": 2128,
      "media_type": 2,
      "taken_at": "2025-10-16T16:03:18+00:00",
      "medias": [
        {
          "media_type": 2,
          "media_url": "https://...",
          "thumbnail_url": "https://...",
          "video_url": "https://..."
        }
      ]
    }
  ],
  "message": "Posts extraídos com sucesso de @instagram"
}
```

**Response (404 - Perfil não encontrado):**
```json
{
  "error": "ProfileNotFound",
  "message": "Perfil @usuario não existe",
  "details": {}
}
```

---

### 5. **POST /stories** - Extrair Stories 🔒

Extrai stories de um perfil do Instagram.

```bash
curl -X POST http://localhost:8000/stories \
  -H "Content-Type: application/json" \
  -H "Authorization: YOUR_API_KEY" \
  -d '{
    "username": "romeroalbuquerque44"
  }'
```

**Request Body:**
```json
{
  "username": "romeroalbuquerque44"  // Username sem @
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "username": "romeroalbuquerque44",
  "total_stories": 2,
  "stories": [
    {
      "id": "3744810535155133791",
      "media_type": 2,
      "media_url": null,
      "video_url": "https://...",
      "thumbnail_url": "https://...",
      "taken_at": "2025-10-16T17:37:04+00:00",
      "expiring_at": "2025-10-17T17:37:04+00:00"
    }
  ],
  "message": "Stories extraídos com sucesso de @romeroalbuquerque44"
}
```

---

## 📊 Modelos de Dados

### Media Types

| Valor | Tipo |
|-------|------|
| 1 | Foto |
| 2 | Vídeo |
| 8 | Álbum/Carrossel |

### Account Status

| Status | Descrição |
|--------|-----------|
| `success` | Conta ativa e disponível |
| `desligado` | Conta desativada |
| `frozen` | Conta temporariamente congelada (rate limit) |

---

## 🔄 Sistema de Contas

### Rotação Automática

O sistema rotaciona contas automaticamente quando:
- Uma conta atinge rate limit
- Ocorre erro de autenticação
- Uma extração falha

### Freezing de Contas

Contas são temporariamente congeladas quando:
- **Rate Limit** (60 minutos)
- **Login Required** (120 minutos)
- **Erro Crítico** (configurável)

### Pool Status

```python
# Verificar status do pool
GET /status

# Response mostra:
{
  "total_accounts": 107,      # Total de contas
  "available": 85,            # Disponíveis agora
  "frozen": 22,               # Temporariamente congeladas
  "accounts": [...]           # Detalhes de cada conta
}
```

---

## 🐛 Debug e Testes

### Script de Debug Standalone

Para testar a extração sem subir a API:

```bash
python debug_extractor.py
```

**Configure no início do arquivo:**

```python
USERNAME = "romeroalbuquerque44"  # Perfil alvo
AMOUNT_POST = 3                   # Quantidade de posts
FEED_OR_STORY = "story"           # "feed" ou "story"
USE_PROXY = False                 # True/False
```

**Vantagens:**
- ✅ Não precisa de API rodando
- ✅ Output detalhado no console
- ✅ JSON completo dos resultados
- ✅ Stack trace completo em erros
- ✅ Status do pool de contas

---

### Cliente de Teste da API

Para testar a API completa:

```bash
python test_api_client.py
```

**Testa:**
- ✅ Health check
- ✅ Extração de posts
- ✅ Extração de stories
- ✅ Salva JSON em arquivos

---

### Testes Unitários

```bash
# Rodar todos os testes
pytest tests/

# Rodar teste específico
pytest tests/test_extractor.py -v

# Com cobertura
pytest --cov=app tests/
```

---

## 🔧 Troubleshooting

### Erro 401 - Unauthorized

**Problema:** API Key inválida ou ausente

**Solução:**
```bash
# Verificar se o header Authorization está correto
curl -H "Authorization: SUA_API_KEY_AQUI" http://localhost:8000/status
```

---

### Erro 422 - Unprocessable Entity

**Problema:** Payload JSON inválido

**Solução:**
```json
// ❌ Errado
{"user": "instagram"}

// ✅ Correto
{"username": "instagram", "quantity": 5}
```

---

### Erro 503 - Service Unavailable

**Problema:** Pool de contas esgotado (todas congeladas)

**Solução:**
1. Aguarde o descongelamento automático (60-120 min)
2. Adicione mais contas no `accounts.csv`
3. Verifique logs: `tail -f logs/app.log`

---

### Erro 500 - Proxy Authentication Required

**Problema:** Proxies configurados sem autenticação

**Solução:** Os proxies foram **automaticamente desabilitados** no startup da API (linha 52-55 do `main.py`). Se quiser usar proxies:

1. Configure credenciais de proxy no CSV
2. Remova as linhas 52-55 do `main.py`:
```python
# Comentar ou remover:
# for account in account_manager.accounts:
#     account.proxy_used = ""
```

---

### Posts/Stories não aparecem

**Problema:** Perfil privado ou sem conteúdo

**Verificar:**
```bash
# Usar debug script para ver detalhes
python debug_extractor.py
```

**Logs mostrarão:**
- `PrivateError`: Perfil é privado
- `UserNotFound`: Perfil não existe
- `[]` vazio: Perfil sem posts/stories

---

### Logs não aparecem

**Problema:** Configuração de encoding no Windows

**Solução:** Configure a variável de ambiente:
```bash
# Windows PowerShell
$env:PYTHONIOENCODING="utf-8"
python -m app.main

# Ou no código (já está configurado no logger.py)
```

---

## 📝 Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `API_KEY` | - | Chave de autenticação (obrigatório) |
| `ACCOUNTS_CSV_PATH` | `data/accounts.csv` | Caminho para CSV de contas |
| `SESSIONS_DIR` | `data/sessions` | Diretório de sessões |
| `LOG_FILE` | `logs/app.log` | Arquivo de logs |
| `LOG_LEVEL` | `INFO` | Nível de log (DEBUG, INFO, WARNING, ERROR) |
| `MAX_RETRIES_PER_REQUEST` | `3` | Tentativas por requisição |
| `MAX_CONCURRENT_REQUESTS` | `3` | Requisições simultâneas |
| `INSTAGRAM_DELAY_MIN` | `1` | Delay mínimo entre requests (seg) |
| `INSTAGRAM_DELAY_MAX` | `3` | Delay máximo entre requests (seg) |

---

## 🔒 Segurança

### API Key

- ✅ Gere uma chave forte: `openssl rand -hex 32`
- ✅ Armazene no `.env` (nunca no código)
- ✅ Use HTTPS em produção
- ✅ Rotacione periodicamente

### Credenciais Instagram

- ✅ CSV fora do git (adicione ao `.gitignore`)
- ✅ Use variáveis de ambiente em produção
- ✅ Encrypt sessões sensíveis

---

## 📈 Performance

### Otimizações Implementadas

- ✅ **Sessões Persistentes**: Reutiliza login
- ✅ **Connection Pooling**: Reusa conexões HTTP
- ✅ **Retry Exponencial**: Backoff inteligente
- ✅ **Account Rotation**: Distribui carga

### Limites

| Métrica | Valor |
|---------|-------|
| Posts por request | 1-50 |
| Tentativas por request | 3 |
| Contas simultâneas | 1 por request |
| Delay entre requests | 1-3 segundos |

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto é privado e proprietário.

---

## 👥 Autores

- **APOGEU Team** - Desenvolvimento inicial

---

## 🙏 Agradecimentos

- [instagrapi](https://github.com/subzeroid/instagrapi) - Cliente Instagram
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Validação de dados

---

## 📞 Suporte

Para suporte, contate: [seu-email@exemplo.com]

---

**Made with ❤️ by APOGEU Team**
