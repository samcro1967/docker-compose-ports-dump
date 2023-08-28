"""
dcpd_stats.py

This module provides functions to generate statistics based on data from a SQLite3 database and other sources.
The statistics include information about Docker Compose files, unique services, port mappings, host networking,
and system performance metrics.

Module Contents:
- compute_lines_in_docker_compose: Compute the total number of lines across all docker-compose.yml files.
- fetch_unique_service_count: Fetch the count of unique services from the database.
- fetch_all_services: Fetch all service details from the database.
- fetch_all_port_mappings: Fetch all port mapping details from the database.
- fetch_all_host_networking: Fetch all host networking details from the database.
- write_statistics_to_file: Write generated statistics to an output file.
- execute_statistics_generation: Fetch data, generate statistics, and write them to an output file.
- get_system_info: Fetch the current CPU and memory utilization of the system.
- generate_statistics: Generate statistics based on the data from the SQLite3 database.

Usage:
The functions in this module can be used to collect and analyze data related to Docker Compose files and services.
The resulting statistics can be written to an output file for further analysis and reporting.
"""

# Import required modules
import datetime
import os
import sqlite3
import sys
from typing import Dict, Tuple, List, Any
import psutil

# Add config to the sys path
# pylint: disable=wrong-import-position
sys.path.extend(['.', '../config'])

# Third-party imports (if any)
import dcpd_config

# Custom module imports
import dcpd_log_debug
import dcpd_log_info

# Create an alias for convenience
logger_info = dcpd_log_info.logger
logger_debug = dcpd_log_debug.logger

default_docker_compose_file = dcpd_config.DEFAULT_DOCKER_COMPOSE_FILE
OUTPUT_FILE = "../data/dcpd_stats.txt"

# -------------------------------------------------------------------------
def compute_lines_in_docker_compose(args) -> int:
    """
    Compute the total number of lines across all the docker-compose.yml files
    specified in the dcpd_config.

    This function reads each file and calculates its number of lines. If the
    docker-compose file is specified as a list, it reads through each file in the list.

    Returns:
        int: Total number of lines across all the docker-compose.yml files.
    """

    # Logging the initiation of the function. If verbosity is enabled using `args`,
    # the function prints an informative message about the start of the computation.
    logger_info.info("Entered compute_lines_in_docker_compose()")
    if args.verbose:
        print("Starting computation of total lines in docker-compose.yml files...")

    total_lines = 0

    # The function first checks if `default_docker_compose_file` is a list or a single string.
    # This allows the function to handle configurations that specify multiple docker-compose files.
    if isinstance(default_docker_compose_file, list):
        for file in default_docker_compose_file:
            try:
                # For each file in the list, the function reads the file and counts its lines.
                with open(file, 'r', encoding='utf-8') as file:
                    lines = len(file.readlines())
                    total_lines += lines
                    if args.verbose:
                        print(f"File {file} has {lines} lines.")
            except IOError as ioerror:
                # If there's an issue reading the file, an error is logged.
                logger_info.error("Error reading %s: %s", file, ioerror)
                logger_info.error("Error reading %s: %s", default_docker_compose_file, ioerror)
    else:
        # If `default_docker_compose_file` is a string, it represents a single file.
        # The function reads this file and counts its lines.
        try:
            with open(default_docker_compose_file, 'r', encoding='utf-8') as file:
                lines = len(file.readlines())
                total_lines += lines
                if args.verbose:
                    print(f"File {default_docker_compose_file} has {lines} lines.")
        except IOError as ioerror:
            # Log any errors that occur while reading the file.
            logger_info.error("Error reading %s: %s", default_docker_compose_file, ioerror)
            logger_debug.exception("IOError while reading %s", default_docker_compose_file)


    # At the end, the function logs the total number of lines across all files.
    # If verbosity is enabled, this total is also printed to the console.
    logger_info.info("Total lines across all docker-compose.yml files: %s", total_lines)
    if args.verbose:
        print(f"Computed total lines in docker-compose.yml files: {total_lines}")

    # The function concludes by returning the total line count.
    return total_lines

# -------------------------------------------------------------------------
def fetch_unique_service_count(cursor: sqlite3.Cursor, args) -> int:
    """
    Fetch the count of unique services from the database.

    Args:
        cursor (sqlite3.Cursor): Database cursor to execute SQL commands.

    Returns:
        int: Count of unique services.
    """

    # The function starts by logging its initiation. If verbosity is enabled (via the `args`
    # parameter), it also prints an informative message about the start of the fetching process.
    logger_info.info("Entered fetch_unique_service_count()")
    if args.verbose:
        print("Fetching count of unique services from the database...")

    try:
        # The SQL query executed here selects and counts all distinct `service_name`
        # entries from the `service_info` table. This helps in determining the
        # number of unique services.
        cursor.execute("SELECT COUNT(DISTINCT service_name) FROM service_info")
        unique_service_count = cursor.fetchone()[0]

        # Upon successfully fetching the count, the function logs this value.
        # Additionally, if verbosity is enabled, this count is printed to the console.
        logger_info.info("Count of unique services fetched: %s", unique_service_count)
        if args.verbose:
            print("Fetched count of unique services: %s", unique_service_count)

        return unique_service_count
    except sqlite3.Error as error:
        # If there is any issue in executing the SQL query or any other database-related error,
        # it gets caught here. The error is logged for both informational and debugging purposes.
        logger_info.error("Failed to fetch unique services count: %s", error)
        logger_debug.exception("SQLite error while fetching unique service count")

        # The function returns a value of 0 in case of any errors to signify that no
        # unique services could be counted, possibly because of an error.
        return 0

# -------------------------------------------------------------------------
def fetch_all_services(cursor: sqlite3.Cursor, args) -> List[Tuple[Any]]:
    """
    Fetch all service details from the database.

    Args:
        cursor (sqlite3.Cursor): Database cursor to execute SQL commands.

    Returns:
        List[Tuple[Any]]: List of service data.
    """

    # At the beginning of the function, a log entry is made to mark its start.
    # If the verbose mode is on (controlled by the `args` parameter), a message is printed to the console.
    logger_info.info("Entered fetch_all_services()")
    if args.verbose:
        print("Fetching all service details from the database...")

    try:
        # The SQL query here aims to select all columns from the `service_info` table.
        # This fetches all details of all services.
        cursor.execute("SELECT * FROM service_info")
        services = cursor.fetchall()

        # After successfully obtaining the list of services, the function logs the number of fetched services.
        # If verbose mode is enabled, the count is printed to the console as well.
        logger_info.info("Successfully fetched %s service(s) from the database.", len(services))
        if args.verbose:
            print("Fetched %s service(s) from the database.", len(services))

        return services
    except sqlite3.Error as error:
        # In case of any errors while executing the SQL command or related database operations,
        # this block will catch them. Detailed error logs are made for both informational and debugging purposes.
        logger_info.error("Failed to fetch services: %s", error)
        logger_debug.exception("SQLite error while fetching all services")

        # The function returns an empty list if there's a problem in retrieving the services.
        return []


# -------------------------------------------------------------------------
def fetch_all_port_mappings(cursor: sqlite3.Cursor, args) -> List[Tuple[Any]]:
    """
    Fetch all port mapping details from the database.

    Args:
        cursor (sqlite3.Cursor): Database cursor to execute SQL commands.

    Returns:
        List[Tuple[Any]]: List of port mapping data.
    """

    # At the beginning of the function, a log entry is made to indicate the start of the operation.
    # If verbose mode is activated (through the `args` parameter), a message is also printed to the console.
    logger_info.info("Entered fetch_all_port_mappings()")
    if args.verbose:
        print("Fetching all port mapping details from the database...")

    try:
        # This SQL command is executed to select all columns from the `port_mappings` table.
        # It aims to gather details of all port mappings.
        cursor.execute("SELECT * FROM port_mappings")
        mappings = cursor.fetchall()

        # After successfully obtaining the list of port mappings, the function logs the number of fetched mappings.
        # If verbose mode is enabled, this count is also printed to the console.
        logger_info.info("Successfully fetched %s port mapping record(s) from the database.", len(mappings))
        if args.verbose:
            print("Fetched %s port mapping record(s) from the database.", len(mappings))

        return mappings
    except sqlite3.Error as error:
        # Should there be any errors during the SQL command execution or related database operations,
        # this block will handle them. It ensures that detailed error logs are created, beneficial for both
        # informational and debugging purposes.
        logger_info.error("Failed to fetch port mappings: %s", error)
        logger_debug.exception("SQLite error while fetching port mappings")

        # If there's an issue retrieving the port mappings, the function returns an empty list.
        return []

# -------------------------------------------------------------------------
def fetch_all_host_networking(cursor: sqlite3.Cursor, args) -> List[Tuple[Any]]:
    """
    Fetch all host networking details from the database.

    Args:
        cursor (sqlite3.Cursor): Database cursor to execute SQL commands.

    Returns:
        List[Tuple[Any]]: List of host networking data.
    """

    # The function starts by logging its entry into the `fetch_all_host_networking` function.
    # If verbose logging is activated (checked through the `args` parameter), an additional console message is displayed.
    logger_info.info("Entered fetch_all_host_networking()")
    if args.verbose:
        print("Fetching all host networking details from the database...")

    try:
        # Here, an SQL command is executed to gather all records from the `host_networking` table.
        cursor.execute("SELECT * FROM host_networking")
        networking = cursor.fetchall()

        # The function logs the total number of host networking records retrieved.
        # If verbose mode is enabled, this count is also displayed on the console.
        logger_info.info("Successfully fetched %s host networking record(s) from the database.", len(networking))
        if args.verbose:
            print("Fetched %s host networking record(s) from the database.", len(networking))

        return networking
    except sqlite3.Error as error:
        # If any errors arise during the SQL command execution or any related database operations,
        # they are gracefully handled within this block. Proper error logs are generated,
        # which are instrumental for both general knowledge and debugging.
        logger_info.error("Failed to fetch host networking details: %s", error)
        logger_debug.exception("SQLite error while fetching host networking details")

        # In the event of any issues in retrieving host networking details, the function returns an empty list.
        return []

# -------------------------------------------------------------------------
def write_statistics_to_file(stats: Dict[str, int], args) -> None:
    """
    Write the generated statistics to the output file.

    Args:
        stats (Dict[str, int]): Dictionary containing the generated statistics.
        args: Object that may contain a verbose flag for detailed logging.

    Returns:
        None
    """

    # The function starts by logging its entry into the `write_statistics_to_file` function.
    # If verbose logging is activated (checked through the `args` parameter), an additional console message is displayed.
    logger_info.info("Entered write_statistics_to_file()")
    if args.verbose:
        print("Writing statistics to the output file...")

    # The function ensures that the directory containing the OUTPUT_FILE exists.
    # If it doesn't, it creates the necessary directories.
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    try:
        # The function attempts to open the OUTPUT_FILE for writing.
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as file:
            # For each statistic in the `stats` dictionary, the function writes the key-value pair to the file.
            for key, value in stats.items():
                file.write(f"{key}: {value}\n")

        # Once the writing process is complete, the function logs the successful write action.
        # If verbose mode is enabled, this information is also displayed on the console.
        logger_info.info("Statistics written to %s", OUTPUT_FILE)
        if args.verbose:
            print("Statistics written to %s", OUTPUT_FILE)

    except IOError as error:
        # If there's any error during the file writing process (like permissions issues, disk space problems, etc.),
        # the function captures and logs the error. An additional detailed exception log is also created for debugging.
        logger_info.error("Error writing statistics to file: %s", error)
        logger_debug.exception("Error encountered while writing statistics to file")

# -------------------------------------------------------------------------
def execute_statistics_generation(cursor: sqlite3.Cursor, args) -> None:
    """
    Fetch data, generate statistics, and write them to an output file.

    Args:
        cursor (sqlite3.Cursor): Database cursor to execute SQL commands.
        args: Object that may contain a verbose flag for detailed logging.

    Returns:
        None
    """

    # The function starts by logging its entry into the `execute_statistics_generation` function.
    # If verbose logging is activated (checked through the `args` parameter), an additional console message is displayed.
    logger_info.info("Entered execute_statistics_generation()")
    if args.verbose:
        print("Starting statistics generation...")

    # The `generate_statistics` function is invoked using the given cursor and arguments.
    # This function would likely fetch data from the database and calculate various statistics based on that data.
    # The returned value is a dictionary of statistics.
    stats = generate_statistics(cursor, args)

    # Once the statistics are generated, they are written to an output file using the `write_statistics_to_file` function.
    write_statistics_to_file(stats, args)

    # After the statistics have been successfully written to the file, the function logs the completion of this process.
    # If verbose mode is enabled, this information is also displayed on the console.
    logger_info.info("Statistics generation completed.")
    if args.verbose:
        print("Statistics generation completed.")

# -------------------------------------------------------------------------
def get_system_info(args) -> dict:
    """
    Fetch the current CPU and memory utilization of the system.

    Retrieves the CPU and memory utilization and returns the data
    as a dictionary, which contains utilization percentages and
    total, used, and available memory values.

    Args:
        args (object): An argument object with a 'verbose' attribute for controlling verbosity.

    Returns:
        dict: Contains CPU and memory utilization data.
    """

    entry_msg = "Entering get_system_info() function..."
    logger_info.info(entry_msg)
    if args.verbose:
        print(entry_msg)

    try:
        cpu_percent = psutil.cpu_percent(interval=None)
        memory_info = psutil.virtual_memory()
        system_info = {
            "cpu_percent": cpu_percent,
            "total_memory": memory_info.total,
            "used_memory": memory_info.used,
            "available_memory": memory_info.available,
            "memory_percent": memory_info.percent,
            "perf_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        logger_debug.debug("System Info: %s", system_info)

        exit_msg = "Exiting get_system_info() function with data retrieved successfully..."
        logger_info.info(exit_msg)
        if args.verbose:
            print(f"System Information: {system_info}")
            print(exit_msg)

        return system_info

    except psutil.Error as psutil_error:
        error_msg = f"Error fetching system info from psutil: {psutil_error}"
        logger_info.error(error_msg)
        if args.verbose:
            print(error_msg)

        exit_err_msg = "Exiting get_system_info() function due to a psutil error..."
        logger_info.error(exit_err_msg)
        if args.verbose:
            print(exit_err_msg)

        return {}

# -------------------------------------------------------------------------
def generate_statistics(cursor: sqlite3.Cursor, args) -> Dict[str, int]:
    """
    Generate statistics based on the data from the SQLite3 database.

    Args:
        cursor (sqlite3.Cursor): Database cursor to execute SQL commands.
        args: Object that may contain a verbose flag for detailed logging.

    Returns:
        Dict[str, int]: Dictionary containing the generated statistics.
    """

    # The function initiates by logging its entry into the `generate_statistics` function.
    # If verbose logging is activated (checked through the `args` parameter), a console message is displayed.
    logger_info.info("Entered generate_statistics()")
    if args.verbose:
        print("Generating statistics based on the database data...")

    # The function proceeds to compute and fetch various pieces of data:

    # This line computes the total number of lines across all docker-compose.yml files.
    total_docker_compose_lines = compute_lines_in_docker_compose(args)

    # This fetches the number of unique services from the database.
    unique_service_count = fetch_unique_service_count(cursor, args)

    # This fetches all port mapping details from the database.
    port_mappings = fetch_all_port_mappings(cursor, args)

    # This fetches all host networking details from the database.
    host_networking = fetch_all_host_networking(cursor, args)

    # This fetches system and cpu info.
    perf_data = get_system_info(args)

    # Using the gathered data, a dictionary called `stats` is created to store the calculated statistics.
    # It aggregates the data into named keys with associated counts or lengths.
    stats = {
        'total_docker_compose_lines': total_docker_compose_lines,
        'total_unique_services': unique_service_count,
        'total_port_mappings': len(port_mappings),
        'total_host_networking': len(host_networking)
    }

    # Add the performance data from get_system_info to the stats dictionary
    stats.update(perf_data)

    # Once the statistics dictionary is formed, its content is logged for reference.
    # If verbose logging is active, each statistic is also printed out to the console.
    logger_debug.info("Generated statistics: %s", stats)
    if args.verbose:
        for key, value in stats.items():
            print(f"{key}: {value}")

    # The function concludes by returning the statistics dictionary.
    return stats
