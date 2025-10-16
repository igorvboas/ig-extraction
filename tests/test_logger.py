"""
Script para testar o sistema de logging
"""
from app.utils.logger import get_logger
import time


def test_logger():
    print("="*50)
    print("Testando Sistema de Logging")
    print("="*50)
    print("Os logs abaixo devem aparecer no console E no arquivo logs/app.log\n")
    
    # Logger principal
    logger = get_logger()
    
    logger.debug("Mensagem DEBUG - detalhes técnicos")
    logger.info("Mensagem INFO - informação geral")
    logger.warning("Mensagem WARNING - alerta")
    logger.error("Mensagem ERROR - erro recuperável")
    logger.critical("Mensagem CRITICAL - erro crítico")
    
    # Child logger (módulo específico)
    account_logger = get_logger("account_manager")
    account_logger.info("Log do módulo account_manager")
    
    extractor_logger = get_logger("extractor")
    extractor_logger.info("Log do módulo extractor")
    
    # Teste de exceção com logging
    try:
        resultado = 10 / 0
    except Exception as e:
        logger.exception("Erro ao dividir por zero (com stack trace)")
    
    print("\n✅ Teste de logging concluído!")
    print("Verifique o arquivo 'logs/app.log' para confirmar que os logs foram salvos.")


if __name__ == "__main__":
    test_logger()