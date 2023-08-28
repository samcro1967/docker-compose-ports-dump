#!/usr/bin/env python3
# dcpd_main.py

import sys

# Add config to the sys path
sys.path.append('../config')

# Import custom, standard, and thrid-party modules
import argparse
from colorama import Fore, Style
import dcpd_config
import dcpd_compose_parser as dcpd_cp
import dcpd_debug
import dcpd_help
import dcpd_host_networking as dcpd_hn
import dcpd_log_debug
import dcpd_log_info
import dcpd_markdown
import dcpd_output
import dcpd_port_printer as dcpd_pp
import dcpd_redaction
import dcpd_stats
import dcpd_utils
import os
import pkg_resources
import platform
import sqlite3
import subprocess
import tabulate
import time
from typing import Any, List, Tuple
import yaml

# Create an alias for convenience
logger_info = dcpd_log_info.logger
logger_debug = dcpd_log_debug.logger

# Configurations
default_docker_compose_file = dcpd_config.DEFAULT_DOCKER_COMPOSE_FILE
default_vpn_container_name = dcpd_config.DEFAULT_VPN_CONTAINER_NAME
default_output_html_file_name = dcpd_config.DEFAULT_OUTPUT_HTML_FILE_NAME
dcpd_stats_txt = os.path.join("..", "data", "dcpd_stats.txt")
version=dcpd_config.VERSION

# -------------------------------------------------------------------------
def has_port_mappings(cursor: Any) -> bool:
    """
    Determine if there are any port mappings present in the database.

    This function checks the 'service_info' table of the SQLite database
    to see if there are any records (i.e., port mappings) stored.

    Args:
        cursor (Any): A SQLite database cursor object that can execute SQL commands.

    Returns:
        bool: True if port mappings exist in the database, False otherwise.
    """
    # Execute a SQL command to count the number of records in the 'service_info' table.
    cursor.execute("SELECT COUNT(*) FROM service_info")
    
    # Fetch the result of the SQL command, which is the count of records.
    count = cursor.fetchone()[0]
    
    # Return True if there's at least one record (port mapping) in the database, False otherwise.
    return count > 0

# -------------------------------------------------------------------------
def dcpd(args):
    """
    The main function for Docker Compose Ports Dump (DCPD) utility.

    This function manages the overall execution flow of the DCPD program,
    orchestrating the tasks of argument parsing, data extraction, and data presentation.

    Args:
        None

    Returns:
        None
    """

    # Capture the raw command line arguments for debugging and verbose output.
    command_line_args = sys.argv[1:]

    if args.verbose:
        print("Starting the Docker Compose Ports Dump (DCPD) utility.")
    logger_info.info("Starting the Docker Compose Ports Dump (DCPD) utility.")

    # If VERBOSE flag is activated, print all detected command-line arguments.
    if args.verbose:
        print("Command-line arguments:")
        print(command_line_args)

    # Log the current state of arguments for diagnostic purposes.
    dcpd_utils.log_separator_data(logger_debug)
    logger_debug.debug("Parsed Command-Line Arguments")
    logger_debug.debug(args)
    dcpd_utils.log_separator_data(logger_debug)

    # Identify and act upon special command-line arguments that display program information without interacting with the database.
    # Such as version, help, and examples.
    if args.version:
        logger_info.info("Version argument detected.")
        print(f"Docker Compose Ports Dump Version: {version}")
        sys.exit(0)
    elif args.show_examples:
        logger_info.info("Show examples argument detected.")
        dcpd_help.print_examples()
        sys.exit(0)
    elif args.help:
        logger_info.info("Help argument detected.")
        dcpd_help.print_help()
        sys.exit(0)

    # Establish a connection to the SQLite database for data storage and extraction.
    conn, cursor = dcpd_cp.create_connection(args)
    if not conn or not cursor:
        logger_info.error("Error! Cannot create the database connection.")
        sys.exit(1)
    else:
        logger_info.info("Database connection successfully created.")

    try:
        # Set up the core table for Docker Compose port mappings in the database.
        dcpd_cp.create_table(cursor, args)
        logger_info.info("Docker Compose table initialized in database.")

        # Extract port data from the Docker Compose file and store it in the database.
        dcpd_cp.parse_docker_compose_and_update_mappings(cursor, args)
        logger_info.info("Docker Compose file parsed & mappings updated.")

        # After database update, retrieve all stored port data.
        all_ports_data = dcpd_cp.parse_docker_compose_and_get_service_ports(cursor, args)
        logger_info.info(f"Number of ports fetched: {len(all_ports_data)}")

        # Logging the extracted port data for debugging.
        dcpd_utils.log_separator_data(logger_debug)
        logger_debug.debug("Parsed Docker Compose & Extracted Ports")
        logger_debug.debug(f"all_ports_data: {all_ports_data}")
        dcpd_utils.log_separator_data(logger_debug)

        # Update database to reflect services that have associated port mappings.
        dcpd_cp.update_has_port_mapping(cursor, args)
        logger_info.info("Database updated with service port mappings.")

        # Further refine database records by associating services with corresponding applications.
        dcpd_cp.update_mapped_app_from_db(cursor, args)
        logger_info.info("Database updated with mapped apps for the vpn container if applicable.")

        # Gather services attached to the host network
        dcpd_hn.host_networking(cursor, args)
        logger_info.info("Services attached to host networking collected.")

        # Generate an exhaustive debug report covering environment, port mappings, and software details and create dcpd_debug.txt.
        debug_info, port_mapping_str, ports_data_str, environment_data_lines = dcpd_debug.generate_debug_info(cursor)
        dcpd_debug.print_debug_output(debug_info, port_mapping_str, ports_data_str, environment_data_lines, paginate=True, display=False)

        # Generate the statistics and write to a file
        dcpd_stats.execute_statistics_generation(cursor, args)

        # Process arguments that require extracting and presenting data from the database in various ways.
        if args.debug:
            # Generate an exhaustive debug report covering environment, port mappings, and software details and display to console.
            debug_info, port_mapping_str, ports_data_str, environment_data_lines = dcpd_debug.generate_debug_info(cursor)

            # Generate data files
            dcpd_output.generate_pretty_web_page(cursor, args)
            dcpd_debug.print_debug_output(debug_info, port_mapping_str, ports_data_str, environment_data_lines, paginate=True, display=True)

            return
        elif args.sort_by_external_port:
            # Format and display port data sorted by external port numbers.
            dcpd_pp.format_all_ports(cursor, args, "-e")
        elif args.sort_by_service_name:
            # Format and display port data sorted by service names.
            dcpd_pp.format_all_ports(cursor, args, "-n")
        elif args.output_html:
            # Produce an HTML webpage containing the formatted port data.
            dcpd_output.generate_pretty_web_page(cursor, args)
            logger_info.info("Web page output generated.")
        else:
            # Default: Format and display port data in a general manner.
            dcpd_pp.format_all_ports(cursor, args)

        # Commit any changes made to the database.
        conn.commit()
        logger_info.info("Database changes committed.")

    except sqlite3.Error as e:
        # Handle SQLite specific errors.
        logger_info.error(f"Database error: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)
    except Exception as e:
        # Generic exception handler to log unexpected errors and provide diagnostic information.
        import traceback
        logger_info.error("======= Diagnostic Traceback =======")
        logger_info.error(traceback.format_exc())
        logger_info.error("====================================")
    finally:
        # Ensure the database connection is closed, regardless of the program's exit path.
        if conn:
            conn.close()

        if args.verbose:
            print("Finished executing the Docker Compose Ports Dump (DCPD) utility.")
        logger_info.info("Finished executing the Docker Compose Ports Dump (DCPD) utility.")

# -------------------------------------------------------------------------
def execute_dcpd(args):
    """
    Execute the Docker Compose Ports Dump (DCPD) utility.

    Handles the initialization, execution, and termination of the DCPD utility.
    Logs execution time, system details, and other relevant information.

    Note:
        Verbose mode provides detailed console output for better user interaction.
    """
    
    # Entry messages
    logger_info.info("Starting the Docker Compose Ports Dump (DCPD) execution.")
    if args.verbose:
        print("Starting the Docker Compose Ports Dump (DCPD) execution.")

    # Provide separators in logs for better clarity.
    dcpd_utils.log_separator_info(logger_info)
    dcpd_utils.log_separator_debug(logger_debug)

    # Logging the OS context can be beneficial for debugging platform-specific issues.
    logger_info.info(f"Running on: {platform.platform()}")

    start_time = time.time()

    execution_time = 0  # Initialize the variable before the try block
    
    try:
        # Execute the main functionality.
        dcpd(args)

        # Calculate the total execution time.
        end_time = time.time()
        execution_time = end_time - start_time
        logger_info.info(f"Operation took {execution_time:.2f} seconds.")

        # Update statistics file with the new execution time.
        with open(dcpd_stats_txt, "r") as stats_file:
            stats_lines = stats_file.readlines()

        stats_lines.append(f"execution_time_seconds: {execution_time:.2f}\n")

        with open(dcpd_stats_txt, "w") as stats_file:
            stats_file.writelines(stats_lines)

        # Redact sensitive data from the output files.
        dcpd_redaction.execute_redaction(args)
        logger_info.info("Data files redacted.")

        # Generate documentation.
        dcpd_markdown.generate_html_with_anchors(args)
        logger_info.info("README.html generated.")

        # Set ownership and permissions
        dcpd_utils.set_permissions_and_ownership(args)

    except Exception as e:
        # Generic exception handling to cover unexpected errors.
        logger_info.error(f"Encountered an unexpected error: {str(e)}")

    # If verbosity is enabled, provide more granular feedback to the console.
    if args.verbose:
        print(f"Operation took {execution_time:.2f} seconds.")

    # Exit messages.
    logger_info.info("Docker Compose Ports Dump finished.")
    logger_debug.debug("Docker Compose Ports Dump finished.")

    if args.verbose:
        print("Finished the Docker Compose Ports Dump (DCPD) execution.")


# -------------------------------------------------------------------------
if __name__ == '__main__':
    try:
        execute_dcpd(args)
    except (KeyboardInterrupt, EOFError):
        logger_info.error("Process interrupted. Exiting gracefully.")
        # Optionally, you can exit the script with a status code.
        sys.exit(1)