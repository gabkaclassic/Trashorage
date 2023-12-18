import logging
from logging.handlers import RotatingFileHandler
from settings import logging_path
from os.path import join, exists
from os import makedirs

max_log_size = 1024 * 1024 * 5  # 5MB
backup_count = 3
info_path = join(logging_path, 'info.log')
error_path = join(logging_path, 'error.log')

if not exists(logging_path):
    makedirs(logging_path, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
info_file_handler = RotatingFileHandler(info_path, maxBytes=max_log_size, backupCount=backup_count)
info_file_handler.setLevel(logging.INFO)

file_handler = RotatingFileHandler(error_path, maxBytes=max_log_size, backupCount=backup_count)
file_handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(info_file_handler)
logger.addHandler(file_handler)
