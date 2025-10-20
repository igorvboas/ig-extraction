# 🔧 Fix: Erro de Validação em Produção

## Problema Identificado

O erro `1 validation error for Media - clips_creation_entry_point_fraction_settings` ocorre devido a diferenças de versões entre ambiente local e produção.

### Causa Raiz
- `requirements.txt` sem versões fixadas
- Produção instalando versões diferentes das bibliotecas
- API do Instagram mudou formato de resposta
- Versão antiga do `instagrapi` não compatível com novos campos

## Solução Aplicada

### 1. ✅ Versões Fixadas no requirements.txt

Atualizamos o `requirements.txt` com versões específicas:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
instagrapi==2.1.2
pydantic==2.5.0
python-dotenv==1.0.0
pandas==2.1.3
```

### 2. ✅ Tratamento de Erros de Validação

Adicionado tratamento específico para `ValidationError` no extractor que:
- Captura erros de validação do Pydantic
- Tenta com outra conta automaticamente
- Registra logs detalhados
- Fornece mensagem clara sobre o problema

### 3. ✅ Configuração de Warnings

Adicionada configuração no `InstagramClient` para suprimir warnings do Pydantic.

## 📋 Passos para Deploy

### Opção 1: Re-deploy via Docker Compose (Recomendado)

```bash
# 1. Fazer commit das mudanças
git add requirements.txt app/services/extractor.py app/services/instagram_client.py
git commit -m "fix: Corrigir erro de validação em produção com versões fixadas"
git push origin main

# 2. No servidor, parar e remover o serviço atual
docker service rm instagram-extractor-api

# 3. Re-criar o serviço (vai baixar o código atualizado do GitHub)
docker stack deploy -c docker-compose.yaml instagram-stack

# 4. Verificar logs
docker service logs -f instagram-extractor-api
```

### Opção 2: Atualização Manual no Container

```bash
# 1. Entrar no container em execução
docker exec -it $(docker ps -q -f name=instagram-extractor-api) /bin/bash

# 2. Atualizar dependências
pip install --upgrade --no-cache-dir instagrapi==2.1.2 pydantic==2.5.0

# 3. Reiniciar o serviço
docker service update --force instagram-extractor-api
```

### Opção 3: Build de Imagem Personalizada (Mais Estável)

Criar um `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (melhor cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Criar diretórios necessários
RUN mkdir -p data/sessions logs

# Expor porta
EXPOSE 8000

# Comando
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Então fazer build e deploy:
```bash
# Build
docker build -t instagram-extractor-api:latest .

# Push (se usar registry)
docker tag instagram-extractor-api:latest seu-registry/instagram-extractor-api:latest
docker push seu-registry/instagram-extractor-api:latest

# Atualizar docker-compose.yaml para usar a imagem customizada
```

## 🔍 Verificação Pós-Deploy

Após o deploy, verificar se está funcionando:

```bash
# 1. Verificar logs
docker service logs -f instagram-extractor-api

# 2. Testar endpoint de health
curl -H "X-API-Key: SUA_API_KEY" https://ig-video-manager.gdeapps.uk/health

# 3. Testar extração de posts
curl -X POST "https://ig-video-manager.gdeapps.uk/extract/posts" \
  -H "X-API-Key: SUA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"username": "instagram", "quantity": 3}'
```

## 📊 Logs Esperados

Após o fix, você deve ver logs como:
```
✓ Login via sessão bem-sucedido: username
✓ Extração bem-sucedida: 3 posts obtidos
```

Em vez de:
```
❌ 1 validation error for Media
❌ clips_creation_entry_point_fraction_settings: None [type=missing]
```

## 🚨 Troubleshooting

### Se ainda ocorrer erro:

1. **Verificar versões instaladas:**
```bash
docker exec -it $(docker ps -q -f name=instagram-extractor-api) pip list | grep -E "instagrapi|pydantic"
```

2. **Limpar cache do pip:**
```bash
docker exec -it $(docker ps -q -f name=instagram-extractor-api) pip cache purge
```

3. **Forçar reinstalação:**
```bash
docker exec -it $(docker ps -q -f name=instagram-extractor-api) pip install --force-reinstall --no-cache-dir instagrapi==2.1.2
```

4. **Verificar se o código foi atualizado:**
```bash
docker exec -it $(docker ps -q -f name=instagram-extractor-api) cat /app/requirements.txt
```

## 📝 Notas Importantes

1. **Sempre fixar versões em produção** - Evita problemas de compatibilidade
2. **Testar em staging primeiro** - Se possível, teste em ambiente similar antes de produção
3. **Monitorar logs após deploy** - Primeiros minutos são críticos
4. **Manter backup das sessões** - Arquivos em `data/sessions/` são importantes

## 🔗 Referências

- [instagrapi GitHub](https://github.com/subzeroid/instagrapi)
- [instagrapi Changelog](https://github.com/subzeroid/instagrapi/releases)
- [Pydantic V2 Migration](https://docs.pydantic.dev/latest/migration/)

---

**Data da Correção:** 2025-10-20
**Versões Testadas:** 
- instagrapi==2.1.2 ✅
- pydantic==2.5.0 ✅
- Python 3.11 ✅

