import logging
import os
from config.settings import settings

def setup_logger():
    # Tạo thư mục logs nếu chưa tồn tại
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger('LDPlayerManager')
    logger.setLevel(settings.config['logging']['level'])

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Sửa đường dẫn file log
    log_file = os.path.join(log_dir, 'ldplayer.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()