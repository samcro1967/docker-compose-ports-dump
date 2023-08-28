"""
dcpd_log_info.py

This module sets up and configures the information-level logger for the Docker Compose Ports Dump (DCPD) application.

Attributes:
    max_log_size (int): The maximum size of the log file before it undergoes rotation.
    log_retention_count (int): The number of old log files to retain.
    log_time_format (str): Format for time in log entries.
    default_log_directory (str): Default directory to store log files.
    console_logging_level (str): The logging level for console output.
    logger (logging.Logger): Logger instance tailored for information-level logging in the DCPD application.
    log_directory (str): Absolute path to the log directory.
    log_file (str): Full path to the info log file.
    file_handler (RotatingFileHandler): Rotating file handler set for log rotation based on file size.
    console_handler (logging.StreamHandler): Console handler to output log messages to the terminal.

Usage:
    This module offers a `logger` instance tailored for information-level logging in the DCPD application. To make use of it, simply import the logger into your desired module.

Example:
    from dcpd_log_info import logger
    logger.info("This is an informational message.")

Note:
    Before using this logger, ensure the settings in `dcpd_config` are appropriately configured.
    The logger doesn't propagate messages to prevent potential duplication in log entries and offers an option to print messages to the console.
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
