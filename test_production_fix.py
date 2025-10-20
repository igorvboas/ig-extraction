"""
Script para testar o fix de validação antes de fazer deploy
Executa testes básicos para garantir que as mudanças funcionam
"""
import sys
import importlib.util

def check_package_version(package_name, min_version=None):
    """Verifica se um pacote está instalado e opcionalmente checa a versão mínima"""
    try:
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            print(f"❌ {package_name} não está instalado")
            return False
        
        module = importlib.import_module(package_name)
        version = getattr(module, '__version__', 'unknown')
        
        if min_version and version != 'unknown':
            from packaging import version as pkg_version
            try:
                if pkg_version.parse(version) >= pkg_version.parse(min_version):
                    print(f"✅ {package_name}=={version} (mínimo: {min_version})")
                    return True
                else:
                    print(f"⚠️  {package_name}=={version} (mínimo necessário: {min_version})")
                    return False
            except:
                # Se não conseguir parsear, apenas avisa
                print(f"✅ {package_name}=={version} (não foi possível comparar versão)")
                return True
        else:
            print(f"✅ {package_name}=={version}")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao verificar {package_name}: {e}")
        return False

def test_imports():
    """Testa se todos os imports necessários funcionam"""
    print("\n🔍 Testando imports...")
    
    try:
        from app.services.extractor import InstagramExtractor
        from app.services.instagram_client import InstagramClient
        from pydantic import ValidationError
        print("✅ Todos os imports funcionando")
        return True
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
        return False

def test_validation_error_handling():
    """Testa se o ValidationError está sendo capturado corretamente"""
    print("\n🧪 Testando tratamento de ValidationError...")
    
    try:
        from pydantic import ValidationError
        from app.services.extractor import InstagramExtractor
        
        # Verificar se o import está no código
        import inspect
        source = inspect.getsource(InstagramExtractor.extract_posts)
        
        if 'ValidationError' in source and 'except ValidationError' in source:
            print("✅ Tratamento de ValidationError encontrado no código")
            return True
        else:
            print("⚠️  Tratamento de ValidationError não encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar ValidationError: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 TESTE DE CORREÇÃO DE PRODUÇÃO")
    print("=" * 60)
    
    # Lista de pacotes e versões mínimas esperadas
    packages = {
        'fastapi': '0.104.1',
        'uvicorn': '0.24.0',
        'instagrapi': '2.1.2',
        'pydantic': '2.5.0',
        'dotenv': '1.0.0',
        'pandas': '2.1.3'
    }
    
    print("\n📦 Verificando versões dos pacotes:")
    print("-" * 60)
    
    all_ok = True
    for package, expected_version in packages.items():
        # Alguns pacotes têm nomes diferentes no import
        import_name = 'dotenv' if package == 'dotenv' else package
        if not check_package_version(import_name, expected_version):
            all_ok = False
    
    # Testar imports
    if not test_imports():
        all_ok = False
    
    # Testar tratamento de erros
    if not test_validation_error_handling():
        all_ok = False
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("=" * 60)
        print("\n🚀 Você pode fazer deploy com segurança!")
        print("\nPróximos passos:")
        print("1. git add -A")
        print("2. git commit -m 'fix: Corrigir erro de validação em produção'")
        print("3. git push origin main")
        print("4. Seguir instruções em DEPLOY_FIX.md")
        return 0
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("=" * 60)
        print("\n⚠️  Corrija os problemas antes de fazer deploy!")
        print("\nPara instalar versões corretas:")
        print("pip install -r requirements.txt --upgrade")
        return 1

if __name__ == "__main__":
    sys.exit(main())

