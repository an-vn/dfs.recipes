import os
import logging
import dotenv

dotenv.load_dotenv()

log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
log_level = getattr(logging, log_level, logging.INFO)
log_format = '%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s'

root_logger = logging.getLogger()
root_logger.handlers.clear()

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(log_format))

root_logger.addHandler(console_handler)
root_logger.setLevel(log_level)
