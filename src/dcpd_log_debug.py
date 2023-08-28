# File: dcpd_log_debug.py

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

# Create logger with a custom name
logger = logging.getLogger("dcpd_logger_debug")
logger.setLevel(logging.DEBUG)

# Resolve the absolute path
log_directory = os.path.abspath(dcpd_config.DEFAULT_LOG_DIRECTORY)

# Create file handler and set level to INFO
log_file = os.path.join(log_directory, "dcpd_log_debug.log")

# Create rotating file handler
file_handler = RotatingFileHandler(log_file, maxBytes=max_log_size, backupCount=log_retention_count)

# Set file log level to debug
file_handler.setLevel(logging.DEBUG)

# Stop the logger from propagating messages up to the root logger
logger.propagate = False

# Create formatter with the custom time format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(funcName)s] - %(message)s', datefmt=log_time_format)  # Corrected variable name

# Set formatter for the file handler
file_handler.setFormatter(formatter)

# Clear any existing handlers to avoid duplicate logging
logger.handlers.clear()

# Add the handler to the logger
logger.addHandler(file_handler)
