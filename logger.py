"""
Настройка логирования
"""

import logging
import sys
from config import Config

def setup_logger():
    """Настройка логгера"""
    
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
    
    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger