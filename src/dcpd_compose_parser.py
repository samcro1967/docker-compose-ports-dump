"""
dcpd_compose_parser.py

Description:
This module provides utilities for parsing DCPD Compose data and interacting with an SQLite database
containing service-related information. Each function offers detailed logging and verbosity features
for traceability and auditability.

Functions:
- parse_compose_file(compose_file_path: str) -> Dict[str, Any]:
    Parses the given DCPD Compose file and extracts essential service information. Returns a dictionary
    containing service details.

- validate_service_data(service_data: Dict[str, Any]) -> bool:
    Validates the extracted service data. Returns True if the data is valid, otherwise returns False.

- write_service_data_to_db(cursor: sqlite3.Cursor, service_data: Dict[str, Any]):
    Writes the extracted and validated service data to the SQLite database.

- fetch_service_info(cursor: sqlite3.Cursor, args) -> List[Dict[str, Union[int, str, bool]]]:
    Fetches all entries from the 'service_info' table. Raises ValueError if the provided cursor is invalid,
    sqlite3.Error for SQLite related issues, and other Exceptions for unexpected issues. Outputs to console
    when verbosity is enabled.

Dependencies:
- sqlite3: Used for database interactions.
- typing: For type hinting.

Notes:
- Ensure that the logger named 'logger_info' is correctly set up before using this module.
- Functions in this module will raise exceptions when encountering issues to allow for upstream handling.
"""

# Import required modules
import os
import sqlite3
import sys
from typing import Dict, List, Union
import yaml

# Add config to the sys path
# pylint: disable=wrong-import-position
sys.path.extend(['.', '../config'])

# Third-party imports (if any)
import dcpd_config
import dcpd_log_debug
import dcpd_log_info
import dcpd_utils

# Create an alias for convenience
logger_info = dcpd_log_info.logger
logger_debug = dcpd_log_debug.logger

# Variables from dcpd_config.py
default_docker_compose_file = dcpd_config.DEFAULT_DOCKER_COMPOSE_FILE
default_vpn_container_name = dcpd_config.DEFAULT_VPN_CONTAINER_NAME

# Modify the path for files
dcpd_db = os.path.join("..", "data", "dcpd.db")

# -------------------------------------------------------------------------
def validate_file_arguments(file_paths: List[str], args):
    """
    Validate the existence of the provided file paths.

    This function checks whether each file path in the provided list exists in the filesystem.
    If any of the paths do not exist, the function prints an error message (if verbosity is enabled)
    and raises a ValueError.

    Parameters:
    - file_paths (List[str]): A list of strings, where each string is a path to a file that needs validation.
    - args (object): An argument object, typically sourced from argparse or a similar library. It should have a
      'verbose' attribute to determine the verbosity of the function.

    Raises:
    - ValueError: If any of the provided file paths do not exist in the filesystem.

    Notes:
    - The function prints error messages to stdout if the 'verbose' attribute of 'args' is True.
    - It's recommended to handle the ValueError in the calling context to decide on further actions
      (like aborting the program or trying an alternative path).
    """
    for file_path in file_paths:
        if not os.path.exists(file_path):
            if args.verbose:
                print(f"Provided docker-compose file path {file_path} does not exist!")
            logger_info.error("Provided docker-compose file path %s does not exist!", file_path)
            raise ValueError(f"Provided docker-compose file path {file_path} does not exist!")

# -------------------------------------------------------------------------
def create_connection(args):
    """
    Create and return a SQLite3 database connection and its associated cursor.

    This function first attempts to delete any existing database to ensure that the docker-compose.yml is the
    authoritative source for the application. After removing any old database, it establishes a new connection
    to the SQLite database and initializes a cursor to perform SQL operations.

    Parameters:
    - args (object): An argument object, typically sourced from argparse or a similar library. It should have a
      'verbose' attribute to determine the verbosity of the function.

    Returns:
    - tuple: A tuple containing two elements - (1) the SQLite3 connection object, and (2) the SQLite3 cursor object.
      If the function fails to establish a connection or initialize a cursor, the returned tuple might contain None
      values.

    Raises:
    - sqlite3.Error: If any SQLite-specific error occurs during connection or cursor initialization.
    - Exception: For any non-SQLite-specific exceptions, particularly during deletion of the old database.

    Notes:
    - The function uses the global variable `dcpd_db` to determine the database file's name and path.
    - The old database, if it exists, is deleted to maintain data consistency with the docker-compose.yml.
    - All significant actions and errors within the function are logged using the `logger_info` logger.
    """
    # If a database already exists, it's removed to ensure docker-compose.yml is the authoritative source
    if args.verbose:
        print("Attempting to delete existing database and create a new one.")
    logger_info.info("Attempting to delete existing database and create a new one.")

    if os.path.exists(dcpd_db):
        try:
            os.remove(dcpd_db)
            logger_info.info("Old database file dcpd_db deleted successfully.")
        except Exception as error:
            logger_info.error("Error encountered while deleting the old dcpd.db: %s", error)
            raise error

    # Try to establish a new connection and initialize a cursor for SQLite operations
    conn = None
    cursor = None
    try:
        conn = sqlite3.connect(dcpd_db)  # Connect to the SQLite database
        conn.row_factory = sqlite3.Row  # Set the row factory for result rows
        cursor = conn.cursor()  # Initialize a cursor to execute SQL commands
        logger_info.info("Successfully created a new database connection and initialized a cursor for dcpd_db.")
    except sqlite3.Error as error:
        logger_info.error("Encountered a database error while trying to establish a connection.", exc_info=True)
        raise error

    if args.verbose:
        print("Database connection established and cursor initialized.")
    logger_info.info("Database connection established and cursor initialized.")
    return conn, cursor  # Return the connection and cursor objects

# -------------------------------------------------------------------------
def create_table(cursor: sqlite3.Cursor, args):
    """
    Create necessary tables in the SQLite3 database.

    This function creates four tables in the SQLite database: `service_info`, `port_mappings`, `host_networking`,
    and `container_ports`. Each table is created using a predefined query. If the tables already exist, they
    won't be recreated.

    Parameters:
    - cursor (sqlite3.Cursor): A SQLite cursor object for executing SQL commands.
    - args (object): An argument object, typically obtained from argparse or a similar library. It should have a
      'verbose' attribute to determine the verbosity of the function.

    Returns:
    - None: The function doesn't return any value but commits the creation of tables in the database.

    Raises:
    - sqlite3.Error: If any SQLite-specific error occurs during table creation.

    Notes:
    - The `service_info` table contains details about services, including their names, ports, port mappings, etc.
    - The `port_mappings` table maintains information about external ports and their respective mapping values.
    - The `host_networking` table keeps track of services associated with host networking.
    - The `container_ports` table captures the port mapping information for each container, including container name,
      internal port, external port, and the protocol (TCP/UDP).
    - Any errors encountered during table creation will be logged and raised.
    """
    try:
        if args.verbose:
            print("Attempting to create database tables.")
        logger_info.info("Attempting to create database tables.")

        # Queries for table creation
        service_info_table_query = """
        CREATE TABLE IF NOT EXISTS service_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            external_port TEXT,
            internal_port TEXT,
            has_port_mapping BOOLEAN,
            mapped_app TEXT
        );
        """
        port_mappings_table_query = """
        CREATE TABLE IF NOT EXISTS port_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_port INTEGER,
            mapping_values TEXT
        );
        """
        host_networking_table_query = """
        CREATE TABLE IF NOT EXISTS host_networking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT
        );
        """

        container_ports_table_query = """
        CREATE TABLE IF NOT EXISTS container_ports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            container_name TEXT NOT NULL,
            internal_port INTEGER,
            external_port INTEGER,
            mapping_name TEXT,
            mapping_value INTEGER,
            protocol TEXT CHECK(protocol IN ('TCP', 'UDP', 'tcp', 'udp'))
        );
        """

        # Execute table creation queries
        cursor.execute(service_info_table_query)
        cursor.execute(port_mappings_table_query)
        cursor.execute(host_networking_table_query)
        cursor.execute(container_ports_table_query)

        # Commit the executed queries
        cursor.connection.commit()

        # Log and optionally print a success message
        logger_info.info("Tables created successfully.")
        if args.verbose:
            print("Tables created successfully.")
    except sqlite3.Error as error:
        # Log any encountered errors and raise the exception
        logger_info.error("Error encountered while creating tables: %s", error, exc_info=True)
        raise error

# -------------------------------------------------------------------------
def read_docker_compose_file(file_path, args):
    """
    Read and parse the provided docker-compose file.

    Parameters:
    - file_path (str): Path to the docker-compose file to be read.
    - args: Runtime arguments, such as verbosity level.

    Returns:
    - dict: Parsed content of the docker-compose file.
    """
    try:
        with open(file_path, "r", encoding='utf-8') as stream:
            return yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        if hasattr(exc, 'problem_mark'):
            mark = exc.problem_mark
            error_msg = f"Error parsing docker-compose file at line {mark.line + 1}, column {mark.column + 1}. Content: '{stream.readlines()[mark.line].strip()}'"
            if args.verbose:
                print(error_msg)
            logger_info.error(error_msg)
        else:
            error_msg = "An unknown error occurred while parsing the docker-compose file."
            if args.verbose:
                print(error_msg)
            logger_info.error(error_msg, exc_info=True)
        sys.exit(1)
    except PermissionError:
        error_msg = f"Permission denied when trying to read {file_path}."
        if args.verbose:
            print(error_msg)
        logger_info.error(error_msg)
        return None

# -------------------------------------------------------------------------
def extract_port_mappings(services):
    """
    Extract port mappings from the provided services data.

    Parameters:
    - services (dict): Dictionary containing service details from the docker-compose file.

    Returns:
    - dict: Dictionary containing port mappings, where keys are external ports and values are service names.
    """
    port_mappings = {}
    for service_name, service_data in services.items():
        for item in service_data.get("environment", []):
            key_value_pair = item.split("=", 1)
            if len(key_value_pair) == 2:
                key, value = key_value_pair
                if key.startswith("port.mapping"):
                    external_port = int(value.strip())
                    port_mappings.setdefault(external_port, []).append(service_name)
    return port_mappings

# -------------------------------------------------------------------------
def update_database_mappings(cursor, port_mappings, args):
    """
    Update the database with the provided port mappings.

    Parameters:
    - cursor (sqlite3.Cursor): A SQLite cursor object for executing SQL commands.
    - port_mappings (dict): Dictionary containing port mappings to be updated in the database.
    - args: Runtime arguments, such as verbosity level.

    Returns:
    - None
    """
    for external_port, mapped_apps in port_mappings.items():
        mapped_app_str = ", ".join(mapped_apps)
        try:
            cursor.execute("INSERT INTO port_mappings (external_port, mapping_values) VALUES (?, ?)", (external_port, mapped_app_str))
        except sqlite3.IntegrityError as integrity_error:
            error_msg = f"IntegrityError for external_port {external_port}. Error message: {str(integrity_error)}"
            if args.verbose:
                print(error_msg)
            logger_info.error(error_msg)
        except sqlite3.Error as error:
            error_msg = f"SQLite error for external_port {external_port}. Error message: {str(error)}"
            if args.verbose:
                print(error_msg, exc_info=True)
            logger_info.error(error_msg, exc_info=True)
            break

    try:
        cursor.connection.commit()
        cursor.execute("SELECT COUNT(*) FROM port_mappings")
        total_mappings = cursor.fetchone()[0]
        msg = f"Total number of port mappings in the database: {total_mappings}"
        if args.verbose:
            print(msg)
        logger_info.info(msg)
    except sqlite3.Error as error:
        error_msg = "Error committing changes to the database."
        if args.verbose:
            print(error_msg, exc_info=True)
        logger_info.error(error_msg, exc_info=True)
        raise error

# -------------------------------------------------------------------------
def parse_docker_compose_and_update_mappings(cursor: sqlite3.Cursor, args):
    """
    Parse the docker-compose file, extract port mappings, and update the database.

    This function scans through the provided docker-compose file(s) to identify port
    mappings defined within the environment settings of each service. The port mappings are
    then used to update the `port_mappings` table in the database, which maintains the
    relationship between external ports and the services that use them.

    Parameters:
    - cursor (sqlite3.Cursor): A SQLite cursor object for executing SQL commands.
    - args: An object containing runtime arguments, such as verbosity level.

    Returns:
    - None: The function doesn't return any value, but it updates the database in place.

    Notes:
    - The function specifically targets port mappings that are defined as environment
      variables starting with the prefix "port.mapping".
    """
    if args.verbose:
        print("Starting the process of parsing the docker-compose file and updating mappings.")

    if not cursor or not cursor.connection:
        error_msg = "Error! Cannot create the database connection."
        if args.verbose:
            print(error_msg)
        logger_info.error(error_msg)
        return

    for file_path in default_docker_compose_file:
        logger_info.info("Starting collection of port.mapping(s) from %s in docker compose.", file_path)

        docker_compose = read_docker_compose_file(file_path, args)
        if not docker_compose:
            continue

        services = docker_compose.get("services", {})
        port_mappings = extract_port_mappings(services)
        update_database_mappings(cursor, port_mappings, args)

        logger_info.info("Completed collecting port.mapping(s) from docker compose.")

    if args.verbose:
        print("Finished parsing the docker-compose file and updating mappings.")
    logger_info.info("Finished parsing the docker-compose file and updating mappings.")

# -------------------------------------------------------------------------
def read_docker_compose_file2(file_path, args):
    """
    Read and parse the docker-compose file at the specified path.

    Parameters:
    - file_path (str): Path to the docker-compose file.
    - args: Command-line arguments, including verbosity level.

    Returns:
    - dict: Parsed content of the docker-compose YAML file.

    Raises:
    - FileNotFoundError: If the specified docker-compose file is not found.
    - PermissionError: If there's no permission to read the docker-compose file.
    - yaml.YAMLError: If there's an error parsing the docker-compose YAML file.
    """
    if args.verbose:
        print(f"Processing docker-compose file: {file_path}")
    logger_info.info("Processing docker-compose file: %s", file_path)

    try:
        with open(file_path, "r", encoding='utf-8') as stream:
            return yaml.safe_load(stream)
    except (FileNotFoundError, PermissionError, yaml.YAMLError) as error:
        if args.verbose:
            print(str(error))
        logger_info.error(str(error))
        raise

# -------------------------------------------------------------------------
def extract_service_port_details(service_name, service_data, args):
    """
    Extract port details for a given service.

    Parameters:
    - service_name (str): Name of the service.
    - service_data (dict): Service-specific data from the docker-compose file.
    - args: Command-line arguments, including verbosity level.

    Returns:
    - list: A list of tuples containing port details (service name, external port, internal port, mapping).
    """
    port_details = []

    port_mappings_for_service = [
        item.split("=", 1)[1].strip() for item in service_data.get("environment", [])
        if item.startswith("port.mapping")
    ]

    if "ports" in service_data:
        for port in service_data["ports"]:
            host_port, container_port = port.split(":")
            external_port = int(host_port)
            internal_port = int(container_port.split("/")[0])

            port_info = f"Port data found for service {service_name} - External: {external_port}, Internal: {internal_port}"
            if args.verbose:
                print(port_info)
            logger_debug.info(port_info)

            port_details.append((service_name, external_port, internal_port, "N/A"))

    elif port_mappings_for_service:
        for port_mapping in port_mappings_for_service:
            env_info = f"Environment port mapping found for service {service_name} - Mapping: {port_mapping}"
            if args.verbose:
                print(env_info)
            logger_debug.info(env_info)

            port_details.append((service_name, None, None, port_mapping))

    else:
        warn_msg = f"No port data or environment port mapping found for service {service_name}. Using default values."
        if args.verbose:
            print(warn_msg)
        logger_debug.warning(warn_msg)

        port_details.append((service_name, None, None, "N/A"))

    return port_details

# -------------------------------------------------------------------------
def update_database_with_port_details(cursor, port_details, args):
    """
    Update the database with the provided port details.

    Parameters:
    - cursor (sqlite3.Cursor): SQLite cursor for executing SQL commands.
    - port_details (list): List of tuples containing port details to be updated.
    - args: Command-line arguments, including verbosity level.

    Raises:
    - sqlite3.IntegrityError: If a database integrity error occurs during insertion.
    - sqlite3.Error: If any other SQLite-specific error occurs during insertion.
    """
    formatted_port_details = [
        (service_name,
         str(external_port) if external_port else None,
         str(internal_port) if internal_port else None,
         mapping)
        for service_name, external_port, internal_port, mapping in port_details
    ]

    try:
        cursor.executemany(
            "INSERT INTO service_info (service_name, external_port, internal_port, mapped_app) VALUES (?, ?, ?, ?)",
            formatted_port_details
        )
        cursor.connection.commit()
    except (sqlite3.IntegrityError, sqlite3.Error, Exception) as error:
        if args.verbose:
            print(str(error))
        logger_info.error(str(error))
        raise

# -------------------------------------------------------------------------
def parse_docker_compose_and_get_service_ports(cursor: sqlite3.Cursor, args) -> list:
    """
    Parse the docker-compose file and extract port information for each service.

    This function reads through the provided docker-compose file(s) and identifies the
    port mappings for each service. The port data, both from direct "ports" configurations
    and from environment-based "port.mapping", is extracted. The collected port information
    is then updated in the `service_info` table in the database and also returned as a list.

    Parameters:
    - cursor (sqlite3.Cursor): A SQLite cursor object for executing SQL commands.
    - args: An object containing runtime arguments, such as verbosity level.

    Returns:
    - list: A list of tuples. Each tuple contains the service name, external port (or None),
      internal port (or None), and the port mapping from the environment (or 'N/A').

    Raises:
    - FileNotFoundError, PermissionError, yaml.YAMLError: If there are issues with reading and parsing the docker-compose file.
    - sqlite3.IntegrityError, sqlite3.Error: If there are database-related errors.
    """

    # Log start of process
    if args.verbose:
        print("Starting the process of collecting ports from docker compose.")
    logger_info.info("Starting the process of collecting ports from docker compose.")

    all_ports_data = []
    bulk_service_port_details = []

    for file_path in default_docker_compose_file:

        # Check for database connection validity
        if not cursor.connection or not cursor:
            error_msg = "Database connection is not established."
            if args.verbose:
                print(error_msg)
            logger_info.error(error_msg)
            return all_ports_data

        for file_path in default_docker_compose_file:
            if args.verbose:
                print(f"Processing docker-compose file: {file_path}")
            logger_info.info("Processing docker-compose file: %s", file_path)

            # Use helper function to read the docker-compose file
            docker_compose = read_docker_compose_file2(file_path, args)

            services = docker_compose.get("services", {})

            dcpd_utils.log_separator_debug(logger_debug)

        for service_name, service_data in services.items():
            service_port_details = extract_service_port_details(service_name, service_data, args)

            # Collect port details for bulk update later
            bulk_service_port_details.extend(service_port_details)
            all_ports_data.extend(service_port_details)

        dcpd_utils.log_separator_debug(logger_debug)

    # Bulk update the database outside the loop
    update_database_with_port_details(cursor, bulk_service_port_details, args)

    if args.verbose:
        print("Finished collecting ports from docker compose.")
    logger_info.info("Finished collecting ports from docker compose.")

    return all_ports_data

# -------------------------------------------------------------------------
def update_has_port_mapping(cursor: sqlite3.Cursor, args) -> None:
    """
    Update the 'has_port_mapping' column for each service in the `service_info` table.

    This function first resets the 'has_port_mapping' column for all services, setting them
    to False (0). It then identifies and updates those services which have associated port
    mappings, setting their 'has_port_mapping' column to True (1).

    Parameters:
    - cursor (sqlite3.Cursor): A SQLite cursor object for executing SQL commands.
    - args: An object containing runtime arguments, such as verbosity level.

    Raises:
    - sqlite3.Error: If any SQLite-specific errors occur during the update process.
    - Exception: If any unexpected errors occur during the update process.

    Notes:
    - The 'has_port_mapping' column is a binary flag (0 or 1) indicating whether a service
      has an associated port mapping.
    - This function commits the changes to the database upon successful update.
    """

    # Starting point of the function
    if args.verbose:
        print("Starting the process of updating 'has_port_mapping' for services.")
    logger_info.info("Starting the process of updating 'has_port_mapping' for services.")

    try:
        # Initialize the has_port_mapping column to 0 (False) for all rows
        if args.verbose:
            print("Resetting 'has_port_mapping' for all services to False (0).")
        logger_info.info("Resetting 'has_port_mapping' for all services to False (0).")

        cursor.execute("UPDATE service_info SET has_port_mapping = 0")

        # Identify services with port mappings
        if args.verbose:
            print("Identifying services with associated port mappings.")
        logger_info.info("Identifying services with associated port mappings.")

        cursor.execute("""
            UPDATE service_info
            SET has_port_mapping = 1
            WHERE service_name IN (SELECT DISTINCT mapping_values FROM port_mappings)
        """)

        cursor.connection.commit()

        if args.verbose:
            print("'has_port_mapping' updated successfully for services.")
        logger_info.info("'has_port_mapping' updated successfully for services.")

    except sqlite3.Error as error:
        error_msg = f"SQLite database error while updating 'has_port_mapping': {str(error)}"
        if args.verbose:
            print(error_msg)
        logger_info.error(error_msg)
        raise
    except Exception as error:
        error_msg = f"Unexpected error during 'has_port_mapping' update: {str(error)}"
        if args.verbose:
            print(error_msg)
        logger_info.error(error_msg)
        raise

# -------------------------------------------------------------------------
def update_mapped_app_from_db(cursor: sqlite3.Cursor, args):
    """
    Updates the 'mapped_app' field in the 'service_info' table based on data
    from the 'port_mappings' table.

    Parameters:
    - cursor (sqlite3.Cursor): A cursor object to execute SQLite commands.
    - args (object): An argument object with a 'verbose' attribute determining the verbosity.

    Raises:
    - ValueError: If the provided cursor or its connection is not active.
    - sqlite3.Error: For SQLite related issues.
    - Exception: For other unexpected issues.

    Notes:
    - Always logs function entry, exit, and important steps to the info log file.
    - Outputs to the console when 'args.verbose' is set to True.
    """

    # Log the start of the app mapping process.
    entry_msg = "Starting the process of mapping apps for VPN container ports."
    logger_info.info(entry_msg)
    if args.verbose:
        print(entry_msg)

    # Ensure the cursor and its connection are active.
    if not cursor or not cursor.connection:
        msg = "Error! The provided cursor or its connection is not active."
        logger_info.error(msg)
        if args.verbose:
            print(msg)
        raise ValueError(msg)

    try:
        # Initialize 'mapped_app' column with default value
        init_msg = "Initializing 'mapped_app' for all services to 'N/A'."
        logger_info.info(init_msg)
        if args.verbose:
            print(init_msg)
        cursor.execute("UPDATE service_info SET mapped_app = 'N/A'")

        # Fetch app-port mappings
        fetch_msg = "Fetching app-port mappings from 'port_mappings' table."
        logger_info.info(fetch_msg)
        if args.verbose:
            print(fetch_msg)
        port_mappings = fetch_port_mappings(cursor, args)

        # Update 'mapped_app' based on the fetched mappings
        for row in port_mappings:
            external_port = int(row["external_port"])
            app_names = row["mapping_values"].split(", ")
            primary_app_name = app_names[0] if app_names else "N/A"

            update_msg = f"Updating mapped app for external port {external_port} to '{primary_app_name}'."
            logger_debug.info(update_msg)
            if args.verbose:
                print(update_msg)

            cursor.execute("""
                UPDATE service_info
                SET mapped_app = ?
                WHERE service_name = ? AND external_port = ?
                """,
                (primary_app_name, default_vpn_container_name, str(external_port))
            )

        # Commit changes to the database
        cursor.connection.commit()

        exit_msg = "Completed app mapping for VPN container ports."
        logger_info.info(exit_msg)
        if args.verbose:
            print(exit_msg)

    except sqlite3.Error as error:
        error_msg = f"SQLite database error encountered during app mapping: {str(error)}"
        logger_info.error(error_msg)
        if args.verbose:
            print(error_msg)
        raise
    except Exception as error:
        error_msg = f"Unexpected error during app mapping process: {str(error)}"
        logger_info.error(error_msg)
        if args.verbose:
            print(error_msg)
        raise


# -------------------------------------------------------------------------
def fetch_port_mappings(cursor: sqlite3.Cursor, args) -> List[Dict[str, Union[int, str]]]:
    """
    Fetches all entries from the 'port_mappings' table in the SQLite database.

    Parameters:
    - cursor (sqlite3.Cursor): A cursor object to execute SQLite commands.
    - args (object): An argument object with a 'verbose' attribute determining the verbosity.

    Returns:
    - List[Dict[str, Union[int, str]]]: A list of dictionaries containing port mapping entries.

    Raises:
    - ValueError: If the provided cursor or its connection is not active.
    - sqlite3.Error: For SQLite related issues.
    - Exception: For other unexpected issues.

    Notes:
    - Always logs function entry, exit, and important steps to the info log file.
    - Outputs to the console when 'args.verbose' is set to True.
    """

    entry_msg = "Starting retrieval of port mapping entries from the database."
    logger_info.info(entry_msg)
    if args.verbose:
        print(entry_msg)

    # Validate the cursor and its connection.
    if not cursor or not cursor.connection:
        msg = "Error! The provided cursor or its connection is not active."
        logger_info.error(msg)
        if args.verbose:
            print(msg)
        raise ValueError(msg)

    try:
        # Execute the SQL query to get all entries from the 'port_mappings' table.
        cursor.execute("SELECT * FROM port_mappings")

        # Convert rows to a list of dictionaries using column names
        columns = [desc[0] for desc in cursor.description]
        port_mappings = [dict(zip(columns, row)) for row in cursor.fetchall()]

        exit_msg = f"Successfully fetched {len(port_mappings)} port mapping entries from the database."
        logger_info.info(exit_msg)
        if args.verbose:
            print(exit_msg)

        return port_mappings

    except sqlite3.Error as error:
        error_msg = f"SQLite database error encountered during port mapping retrieval: {str(error)}"
        logger_info.error(error_msg)
        if args.verbose:
            print(error_msg)
        raise
    except Exception as error:
        error_msg = f"Unexpected error during port mapping retrieval: {str(error)}"
        logger_info.error(error_msg)
        if args.verbose:
            print(error_msg)
        raise

# -------------------------------------------------------------------------
def fetch_service_info(cursor: sqlite3.Cursor, args) -> List[Dict[str, Union[int, str, bool]]]:
    """
    Fetches all entries from the 'service_info' table in the SQLite database.

    Parameters:
    - cursor (sqlite3.Cursor): A cursor object to execute SQLite commands.
    - args (object): An argument object with a 'verbose' attribute determining the verbosity.

    Returns:
    - List[Dict[str, Union[int, str, bool]]]: A list of dictionaries containing service-related entries.

    Raises:
    - ValueError: If the provided cursor or its connection is not active.
    - sqlite3.Error: For SQLite related issues.
    - Exception: For other unexpected issues.

    Notes:
    - Always logs function entry, exit, and important steps to the info log file.
    - Outputs to the console when 'args.verbose' is set to True.
    """

    entry_msg = "Starting retrieval of service-related entries from the database."
    logger_info.info(entry_msg)
    if args.verbose:
        print(entry_msg)

    # Validate the cursor and its connection.
    if not cursor or not cursor.connection:
        msg = "Error! The provided cursor or its connection is not active."
        logger_info.error(msg)
        if args.verbose:
            print(msg)
        raise ValueError(msg)

    try:
        # Execute the SQL query to get all entries from the 'service_info' table.
        cursor.execute("SELECT * FROM service_info")

        # Convert the rows into a list of dictionaries using column names.
        columns = [desc[0] for desc in cursor.description]
        service_entries = [dict(zip(columns, row)) for row in cursor.fetchall()]

        exit_msg = f"Successfully fetched {len(service_entries)} service-related entries from the database."
        logger_info.info(exit_msg)
        if args.verbose:
            print(exit_msg)

        return service_entries

    except sqlite3.Error as error:
        error_msg = f"SQLite database error encountered during service info retrieval: {str(error)}"
        logger_info.error(error_msg)
        if args.verbose:
            print(error_msg)
        raise
    except Exception as error:
        error_msg = f"Unexpected error during service info retrieval: {str(error)}"
        logger_info.error(error_msg)
        if args.verbose:
            print(error_msg)
        raise
