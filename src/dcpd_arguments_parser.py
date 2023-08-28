"""
dcpd_arguments_parser.py

This script contains functions for parsing and validating command-line arguments for the Docker Compose Ports Dump (DCPD) utility. It defines argument parsing, validation, and default value setting.

Dependencies:
- sys: Standard library for system-specific parameters and functions.
- argparse: Library for parsing command-line arguments.
- os: Standard library for interacting with the operating system.
- traceback: Standard library for printing exception traceback.
- dcpd_config: Configuration module containing relevant constants and settings.
- dcpd_log_debug and dcpd_log_info: Logging modules for debugging and information-level logs.
- dcpd_utils: Utility functions for various purposes.

Note:
- Ensure the provided paths in the script are valid and accessible.
- The script relies on the presence of certain modules, make sure they exist before executing.
- The script utilizes configuration constants and logging modules for streamlined functionality.
"""

# Importing standard libraries
import sys
import argparse
import os
import traceback

# Add config to the sys path
# pylint: disable=wrong-import-position
sys.path.append('../config')

# Importing configurations from config module
import dcpd_config
import dcpd_log_debug
import dcpd_log_info
import dcpd_utils

# Configurations
default_docker_compose_file = dcpd_config.DEFAULT_DOCKER_COMPOSE_FILE
default_vpn_container_name = dcpd_config.DEFAULT_VPN_CONTAINER_NAME
default_output_html_file_name = dcpd_config.DEFAULT_OUTPUT_HTML_FILE_NAME
default_sort_order = dcpd_config.DEFAULT_SORT_ORDER
default_debug_mode=dcpd_config.DEFAULT_DEBUG_MODE

# Create an alias for conveniencelogger_info = dcpd_log_info.logger
logger_debug = dcpd_log_debug.logger
logger_info = dcpd_log_info.logger

# Modify the path for files
output_csv_file = os.path.join("..", "data", "dcpd_host_networking.csv")

# -------------------------------------------------------------------------
def validate_file_arguments(args) -> None:
    """
    Validates the file arguments for -o.
    Raises exceptions if the paths are invalid.

    Parameters:
        args: A namespace object that holds the arguments.

    Raises:
        FileNotFoundError: If a specified directory or file does not exist.
        PermissionError: If a specified directory is not writable.
    """

    # Validate the output HTML file path if provided by the user
    if args.output_html:
        # Use the default output HTML file name
        output_html_file_path = default_output_html_file_name

        # Extract the directory from the file path
        output_dir = os.path.dirname(output_html_file_path) or '.'

        # Validate the existence of the directory
        if not os.path.exists(output_dir):
            msg = f"Error: Directory {output_dir} does not exist."
            logger_info.error(msg)
            raise FileNotFoundError(msg)

        # Validate write permissions for the directory
        if not os.access(output_dir, os.W_OK):
            msg = f"Error: Directory {output_dir} is not writable."
            logger_info.error(msg)
            raise PermissionError(msg)

    # Validate the default Docker Compose file paths
    for file_path in default_docker_compose_file:
        if not os.path.exists(file_path):
            msg = f"Error: Invalid path or file provided for Docker Compose file: {file_path}"
            logger_info.error(msg)
            raise FileNotFoundError(msg)

# -------------------------------------------------------------------------
def parse_arguments():
    """
    Parses command-line arguments for the docker_ports_dump script.
    Returns a namespace object containing parsed arguments.
    """

    # Write entering function to the info log
    logger_info.info("Beginning parsing the arguments.")

    # Initializing argument parser with a custom description
    parser = argparse.ArgumentParser(description="Parse Docker Compose file and extract ports.", add_help=False)


    # Define other command-line arguments
    parser = argparse.ArgumentParser(description="Parse Docker Compose file and extract ports.", add_help=False)
    parser.add_argument("-e", "--sort-by-external-port", action="store_true", help="Sort the table by External Port.")
    parser.add_argument("-n", "--sort-by-service-name", action="store_true", help="Sort the table by Service Name.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode.")
    parser.add_argument("-s", "--show-examples", action="store_true", help="Show examples of port.mapping configuration in a docker-compose.yml file.")
    parser.add_argument("-V", "--version", action="store_true", help="Show version information and exit.")
    parser.add_argument("-o", "--output-html", action="store_true", help="Generate a web page with the port mappings.")
    parser.add_argument("-h", "--help", action="store_true", help="Show this help message and exit.")
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode')

    try:
        # Parse the arguments
        args = parser.parse_args()

        # Validate file arguments based on the provided or default filenames
        validate_file_arguments(args)

        # Log successful completion to info log
        logger_info.info("Arguments have been parsed.")

        # Logging the raw arguments for debugging purposes
        dcpd_utils.log_separator_data(logger_debug)
        logger_debug.debug("Raw arguments: %s", args)
        dcpd_utils.log_separator_data(logger_debug)

    except Exception as error:
        logger_info.error("Error while parsing arguments: %s", error)
        logger_info.error(traceback.format_exc())
        raise error

    try:
        # Validate argument combinations and set default values
        validate_and_set_defaults(args, parser)
    except Exception as error:
        logger_info.error("Error during validation and setting defaults: %s", error)
        raise error

    return args

# -------------------------------------------------------------------------
def validate_and_set_defaults(args, parser):
    """
    Validates command-line argument combinations and sets default values where required.
    """

    try:
        # Log a message indicating the validation process is starting.
        logger_info.info("Beginning to validate arguments.")

        # If the help or version flags are provided, log the occurrence and return early
        # since no further processing is needed.
        if args.help or args.version:
            logger_info.info("Help or version flags provided. No further processing needed.")
            return

        # Extract all provided command-line arguments excluding the script name
        command_line_args = sys.argv[1:]
        provided_flags = set(command_line_args)

        # Define valid argument combinations and their optional flags.
        valid_combinations = {
            (): [],
            ("-d",): [],
            ("-s",): [],
            ("-h",): [],
            ("-V",): [],
            ("-e",): [],
            ("-n",): [],
            ("-o",): ["-v"],
        }

        # Define argument combinations that conflict with each other
        invalid_combinations = {
            (): [],
            ("-d",): ["-e", "-n", "-s", "-o", "-h", "-V"],
            ("-s",): ["-d", "-e", "-n", "-o", "-h", "-V"],
            ("-e",): ["-d", "-n", "-s", "-o", "-h", "-V"],
            ("-n",): ["-d", "-e", "-s", "-o", "-h", "-V"],
            ("-o",): ["-d", "-e", "-n", "-s", "-h", "-V"],
        }

        # Validate provided flags against valid combinations.
        is_valid_combination = any(
            set(valid_combination_flags).issubset(provided_flags)
            and not any(flag in conflicting_flags for flag in provided_flags)
            for valid_combination_flags, conflicting_flags in valid_combinations.items()
        )

        # Validate provided flags against invalid combinations
        for invalid_combination_flags, conflicting_flags in invalid_combinations.items():
            if set(invalid_combination_flags).issubset(provided_flags) and any(flag in conflicting_flags for flag in provided_flags):
                logger_info.error("Invalid argument combination detected.")
                parser.error("Invalid argument combination detected. Check usage for details.")
                break  # Found an invalid combination

        # If no valid combinations are found, raise an error
        if not is_valid_combination:
            logger_info.error("Invalid argument combination detected.")
            parser.error("Invalid argument combination detected. Check usage for details.")

        logger_info.info("Finished validating arguments.")

    # Handle specific ValueError exception during the validation process
    except ValueError as value_error:
        logger_info.error(str(value_error))
        parser.error(str(value_error))
    # Handle specific argparse.ArgumentError exception
    except argparse.ArgumentError as arg_error:
        logger_info.error(str(arg_error))
        parser.error(str(arg_error))
    # Handle specific exceptions related to file operations or permissions
    except (FileNotFoundError, PermissionError) as file_error:
        logger_info.error(str(file_error))
        parser.error(str(file_error))
