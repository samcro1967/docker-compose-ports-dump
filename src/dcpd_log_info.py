# File: dcpd_log_info.py

import logging
from logging.handlers import RotatingFileHandler
import os

# Custom Modules imports
import dcpd_config as dcpd_config

# Create an alias for convenience
max_log_size = dcpd_config.MAX_LOG_SIZE
log_retention_count = dcpd_config.LOG_RETENTION_COUNT
log_time_format = dcpd_config.LOG_TIME_FORMAT
default_log_directory = dcpd_config.DEFAULT_LOG_DIRECTORY
console_logging_level = dcpd_config.CONSOLE_LOGGING_LEVEL

logging.basicConfig(level=logging.INFO)

# Create logger with a custom name
logger = logging.getLogger("dcpd_logger_info")
logger.setLevel(logging.INFO)

# Resolve the absolute path
log_directory = os.path.abspath(dcpd_config.DEFAULT_LOG_DIRECTORY)

# Create file handler and set level to INFO
log_file = os.path.join(log_directory, "dcpd_log_info.log")

# Create rotating file handler
file_handler = RotatingFileHandler(log_file, maxBytes=max_log_size, backupCount=log_retention_count)

# Set file log level to info
file_handler.setLevel(logging.INFO)

# Create console handler and set level to ERROR
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, console_logging_level))

# Stop the logger from propagating messages up to the root logger and prevent messages from being printed to the console
logger.propagate = False

# Create formatter with the custom time format
# https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(funcName)s] - %(message)s', datefmt=log_time_format)

# Set formatter for both file and console handlers
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Clear any existing handlers to avoid duplicate logging
logger.handlers.clear()

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
