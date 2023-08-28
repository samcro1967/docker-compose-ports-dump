"""
dcpd_log_debug.py

This module is responsible for setting up and configuring a logger for the Docker Compose Ports Dump (DCPD) application. The logger focuses on debugging messages.

Attributes:
    max_log_size (int): The maximum size of the log file before it gets rotated.
    log_retention_count (int): Number of old log files to retain.
    log_time_format (str): Format for time in log entries.
    default_log_directory (str): Default directory to store log files.
    logger (logging.Logger): Logger instance used for debug logging in the DCPD application.
    log_directory (str): Absolute path to the log directory.
    log_file (str): Full path to the debug log file.
    file_handler (RotatingFileHandler): Rotating file handler for log rotation based on size.

Usage:
    Import this module to get the `logger` instance which is set up and ready to log debug messages for the DCPD application.

Example:
    from dcpd_log_debug import logger
    logger.debug("This is a debug message.")

Note:
    Ensure the configuration in `dcpd_config` is set appropriately before using this logger.
    Also, the logger does not propagate messages to avoid any duplication in log entries.
"""

import logging
from logging.handlers import RotatingFileHandler
import os
import sys

# Add config to the sys path
sys.path.append('../config')

# Custom Modules imports
# pylint: disable=wrong-import-position
import dcpd_config

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
