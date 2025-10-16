# Guia de Contribuição

Obrigado por considerar contribuir com a Instagram Extractor API! 🎉

## 📋 Índice

- [Código de Conduta](#código-de-conduta)
- [Como Contribuir](#como-contribuir)
- [Processo de Desenvolvimento](#processo-de-desenvolvimento)
- [Padrões de Código](#padrões-de-código)
- [Testes](#testes)
- [Commit Messages](#commit-messages)
- [Pull Requests](#pull-requests)

## 📜 Código de Conduta

Este projeto segue um código de conduta. Ao participar, você concorda em manter um ambiente respeitoso e inclusivo.

## 🤝 Como Contribuir

### Reportar Bugs

Se encontrou um bug:

1. **Verifique** se já não existe uma issue aberta
2. **Crie uma nova issue** com:
   - Título descritivo
   - Passos para reproduzir
   - Comportamento esperado vs atual
   - Versão do Python e SO
   - Logs relevantes

**Template de Bug Report:**
```markdown
**Descrição do Bug**
Descrição clara do problema.

**Passos para Reproduzir**
1. Vá para '...'
2. Execute '...'
3. Veja o erro

**Comportamento Esperado**
O que deveria acontecer.

**Screenshots/Logs**
Se aplicável, adicione logs.

**Ambiente**
- OS: [e.g. Windows 11]
- Python: [e.g. 3.11.2]
- Versão da API: [e.g. 1.0.0]
```

### Sugerir Features

Para sugerir novas funcionalidades:

1. **Abra uma issue** com tag `enhancement`
2. **Descreva**:
   - O problema que resolve
   - Solução proposta
   - Alternativas consideradas
   - Impacto em features existentes

### Contribuir com Código

1. **Fork** o repositório
2. **Clone** seu fork
3. **Crie uma branch** para sua feature
4. **Implemente** as mudanças
5. **Teste** completamente
6. **Commit** seguindo os padrões
7. **Push** para seu fork
8. **Abra um Pull Request**

## 🔧 Processo de Desenvolvimento

### 1. Setup do Ambiente

```bash
# Clone seu fork
git clone https://github.com/seu-usuario/instagram-extractor-api.git
cd instagram-extractor-api/instagram-api

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt

# Configure .env
cp .env.example .env
# Edite .env com suas configurações
```

### 2. Crie uma Branch

```bash
git checkout -b feature/nome-da-feature
# ou
git checkout -b fix/nome-do-bug
```

**Convenção de Nomes:**
- `feature/` - Novas funcionalidades
- `fix/` - Correções de bugs
- `docs/` - Documentação
- `refactor/` - Refatoração de código
- `test/` - Adição/melhoria de testes
- `chore/` - Tarefas de manutenção

### 3. Desenvolva

- ✅ Mantenha commits pequenos e focados
- ✅ Escreva código limpo e documentado
- ✅ Adicione testes para novas features
- ✅ Atualize documentação quando necessário
- ✅ Siga os padrões de código do projeto

### 4. Teste

```bash
# Rode os testes
pytest tests/ -v

# Com cobertura
pytest --cov=app tests/

# Teste a API manualmente
python debug_extractor.py
python test_api_client.py
```

### 5. Commit

```bash
git add .
git commit -m "tipo: descrição curta"
```

### 6. Push

```bash
git push origin feature/nome-da-feature
```

### 7. Pull Request

Abra um PR para a branch `main` com:
- Título descritivo
- Descrição detalhada das mudanças
- Issues relacionadas (se houver)
- Checklist de revisão

## 📝 Padrões de Código

### Python Style Guide

Seguimos **PEP 8** com algumas adaptações:

```python
# ✅ BOM
def extract_posts(username: str, quantity: int) -> List[Post]:
    """
    Extrai posts de um perfil.
    
    Args:
        username: Username do perfil
        quantity: Quantidade de posts
        
    Returns:
        Lista de Posts
    """
    logger.info(f"Extraindo {quantity} posts de @{username}")
    # ...

# ❌ RUIM
def extractPosts(user,qty):
    print(f"extracting {qty} from {user}")
    # ...
```

### Docstrings

Use **Google Style**:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Breve descrição da função.
    
    Descrição mais detalhada se necessário.
    
    Args:
        param1: Descrição do primeiro parâmetro
        param2: Descrição do segundo parâmetro
        
    Returns:
        Descrição do retorno
        
    Raises:
        ExceptionType: Quando ocorre X
    """
    pass
```

### Type Hints

Sempre use type hints:

```python
# ✅ BOM
def get_user_id(username: str) -> Optional[int]:
    pass

# ❌ RUIM
def get_user_id(username):
    pass
```

### Imports

Organize imports:

```python
# 1. Standard library
import os
from typing import List, Optional

# 2. Third-party
from fastapi import FastAPI
from pydantic import BaseModel

# 3. Local
from app.models.account import Account
from app.utils.logger import get_logger
```

### Naming Conventions

```python
# Classes: PascalCase
class InstagramExtractor:
    pass

# Functions/variables: snake_case
def extract_posts():
    user_name = "example"

# Constants: UPPER_CASE
MAX_RETRIES = 3
API_KEY = "..."

# Private: _prefixo
def _internal_method():
    pass
```

## 🧪 Testes

### Estrutura de Testes

```
tests/
├── __init__.py
├── test_extractor.py
├── test_account_manager.py
├── test_instagram_client.py
└── test_api.py
```

### Escrevendo Testes

Use **pytest**:

```python
import pytest
from app.services.extractor import InstagramExtractor

def test_extract_posts_success():
    """Testa extração bem-sucedida de posts"""
    # Arrange
    extractor = InstagramExtractor(mock_manager)
    
    # Act
    posts = extractor.extract_posts("instagram", 5)
    
    # Assert
    assert len(posts) == 5
    assert posts[0].username == "instagram"

def test_extract_posts_not_found():
    """Testa erro quando perfil não existe"""
    with pytest.raises(ProfileNotFound):
        extractor.extract_posts("usuario_inexistente", 1)
```

### Rodando Testes

```bash
# Todos os testes
pytest

# Com verbosidade
pytest -v

# Arquivo específico
pytest tests/test_extractor.py

# Teste específico
pytest tests/test_extractor.py::test_extract_posts_success

# Com cobertura
pytest --cov=app --cov-report=html
```

## 📨 Commit Messages

Siga o padrão **Conventional Commits**:

```
tipo(escopo): descrição curta

Descrição mais detalhada (opcional)

Closes #123
```

### Tipos

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação (não afeta código)
- `refactor`: Refatoração
- `test`: Adicionar/modificar testes
- `chore`: Tarefas de build/config

### Exemplos

```bash
# Feature
git commit -m "feat(extractor): adiciona suporte a Reels"

# Bug fix
git commit -m "fix(api): corrige erro 422 em /posts"

# Documentação
git commit -m "docs(readme): adiciona seção de troubleshooting"

# Refactoring
git commit -m "refactor(client): simplifica lógica de retry"

# Teste
git commit -m "test(extractor): adiciona testes para stories"
```

## 🔀 Pull Requests

### Checklist

Antes de abrir um PR, verifique:

- [ ] Código segue os padrões do projeto
- [ ] Todos os testes passam
- [ ] Testes adicionados para novas features
- [ ] Documentação atualizada
- [ ] Commit messages seguem o padrão
- [ ] Branch está atualizada com `main`
- [ ] Sem conflitos

### Template de PR

```markdown
## Descrição
Breve descrição das mudanças.

## Tipo de Mudança
- [ ] Bug fix (non-breaking change)
- [ ] Nova feature (non-breaking change)
- [ ] Breaking change (fix ou feature que quebra compatibilidade)
- [ ] Documentação

## Como Testar?
1. Passo 1
2. Passo 2
3. ...

## Screenshots (se aplicável)
...

## Checklist
- [ ] Código segue style guide
- [ ] Self-review feito
- [ ] Comentários em código complexo
- [ ] Documentação atualizada
- [ ] Sem warnings
- [ ] Testes adicionados
- [ ] Testes passam

## Issues Relacionadas
Closes #123
```

### Processo de Review

1. **Automatic checks** rodam (testes, linting)
2. **Code review** por mantainer
3. **Mudanças solicitadas** (se necessário)
4. **Aprovação** e merge

## 🎯 Boas Práticas

### DOs ✅

- Escreva código limpo e legível
- Adicione testes para novas features
- Mantenha commits pequenos
- Documente código complexo
- Atualize documentação
- Siga os padrões existentes

### DON'Ts ❌

- Não commite código quebrado
- Não commite arquivos de log/cache
- Não faça PRs gigantes
- Não ignore falhas de teste
- Não adicione dependências desnecessárias
- Não commit credenciais

## 🐛 Debug

### Logs Úteis

```python
from app.utils.logger import get_logger

logger = get_logger(__name__)

logger.debug("Detalhes técnicos")
logger.info("Informação geral")
logger.warning("Aviso")
logger.error("Erro", exc_info=True)
```

### Debugging Local

```python
# Use debug_extractor.py para testar isoladamente
python debug_extractor.py

# Ou use breakpoints
import pdb; pdb.set_trace()
```

## 📚 Recursos

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pydantic Docs](https://pydantic-docs.helpmanual.io/)
- [instagrapi Docs](https://github.com/subzeroid/instagrapi)
- [PEP 8 Style Guide](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

## ❓ Dúvidas?

- Abra uma **issue** com tag `question`
- Entre em contato: [seu-email@exemplo.com]

---

**Obrigado por contribuir! 🙏**

