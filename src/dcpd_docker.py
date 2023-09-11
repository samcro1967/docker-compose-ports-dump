"""
dcpd_docker.py - Docker Compose Ports Dump (DCPD) Docker Utility

This script provides utility functions to collect and export information
about Docker containers, including port mappings and environment variables.

Module Dependencies:
- subprocess: For executing external commands.
- json: For parsing JSON data.
- dcpd_log_debug: Custom logger for debug messages.
- dcpd_log_info: Custom logger for info messages.
- re: Regular expression module for pattern matching.
- sqlite3: SQLite database interface.
- os: Operating system interface.
- csv: CSV file handling.

Global Constants:
- logger_info: Alias for the info logger.
- logger_debug: Alias for the debug logger.
- output_csv_file: Path for the CSV output file.

Functions:
- get_container_ports(cursor: sqlite3.Cursor, args: object) -> None:
    Retrieves port mapping information of running Docker containers.

- get_container_mappings(cursor: sqlite3.Cursor, args: object) -> None:
    Retrieves selected environment variables of running Docker containers.

- export_container_ports_to_csv(cursor: sqlite3.Cursor, args: object,
                                output_file: str = output_csv_file) -> None:
    Export the container_ports table from the SQLite database to a CSV file.

- export_container_info_to_csv(args: object) -> None:
    Export the current container info from Docker to a CSV file.

- export_container_stats_to_txt(args: object) -> None:
    Export the current container stats from Docker to a text file.
"""
import subprocess
import sqlite3
import os
from sqlite3 import Cursor, Error
import csv
import docker

import dcpd_log_debug
import dcpd_log_info

# Create an alias for convenience
logger_info = dcpd_log_info.logger
logger_debug = dcpd_log_debug.logger
output_csv_file = os.path.join("..", "data", "dcpd_docker_inspect.csv")

# -------------------------------------------------------------------------
BATCH_SIZE = 20  # Adjust the batch size based on performance testing
# pylint: disable=R0914
def get_container_ports(cursor: sqlite3.Cursor, args):
    """
    Retrieves the port mapping information of running Docker containers.

    This function collects port mappings from all currently running Docker containers
    and stores them in the `container_ports` table in the SQLite database.

    Parameters:
    - cursor (sqlite3.Cursor): A SQLite cursor object for executing SQL commands.
    - args (object): An argument object, typically obtained from argparse or a similar library.
                     It should have a 'verbose' attribute to determine the verbosity of the function.

    Returns:
    - None: The function doesn't return any value but commits the stored port mappings in the database.

    Raises:
    - subprocess.CalledProcessError: If there's an error executing the Docker commands.
    """
    # Log and optionally print the function entry message
    logger_info.info("Entered get_container_ports function.")
    if args.verbose:
        print("Started fetching container port information.")

    client = docker.from_env()

    try:
        containers = client.containers.list()

        batch_inserts = []
        for container in containers:
            data = container.attrs

            container_name = data.get('Name', '').lstrip('/')
            port_data = data.get('NetworkSettings', {}).get('Ports', {})

            for key, values in port_data.items():
                internal_port, protocol = key.split('/')
                if protocol not in ['TCP', 'UDP', 'tcp', 'udp']:
                    continue

                if values is None:
                    continue  # Skip if values are None

                for value in values:
                    if value.get('HostIp') != '0.0.0.0':
                        continue

                    external_port = value.get('HostPort', '')
                    batch_inserts.append((container_name, internal_port, external_port, protocol))

                    if len(batch_inserts) >= BATCH_SIZE:
                        insert_batch(cursor, batch_inserts)
                        batch_inserts = []

                    if args.verbose:
                        print(f"Stored port mapping for {container_name}: {key} -> {external_port}")

        if batch_inserts:
            insert_batch(cursor, batch_inserts)

        cursor.connection.commit()
        logger_info.info("Container port data fetched and stored successfully.")
        if args.verbose:
            print("Finished fetching container port information.")

    except subprocess.CalledProcessError as error:
        logger_info.error("Error encountered while executing Docker commands: %s", error, exc_info=True)
        raise error
    except Exception as error:
        logger_info.error("Error encountered while fetching/storing container port data: %s", error, exc_info=True)
        raise error

# -------------------------------------------------------------------------
def insert_batch(cursor: sqlite3.Cursor, batch_inserts: list):
    """
    Inserts a batch of port mappings into the container_ports table.

    This function performs a batch insertion of port mappings from Docker containers
    into the `container_ports` table in the SQLite database to improve performance
    and reduce the number of individual insert operations.

    Parameters:
    - cursor (sqlite3.Cursor): A SQLite cursor object for executing SQL commands.
    - batch_inserts (list): A list of tuples, where each tuple contains:
        1. container_name (str): The name of the Docker container.
        2. internal_port (str): The internal port used by the Docker container.
        3. external_port (str): The port mapped on the host system.
        4. protocol (str): The protocol used (e.g., "TCP" or "UDP").

    Returns:
    - None: The function does not return any value, but executes the batch insert operations on the database.

    Raises:
    - sqlite3.Error: In case of any SQLite database errors.
    """
    query = "INSERT INTO container_ports (container_name, internal_port, external_port, protocol) VALUES (?, ?, ?, ?)"
    cursor.executemany(query, batch_inserts)


# -------------------------------------------------------------------------
def get_container_mappings(cursor: sqlite3.Cursor, args):
    """
    Retrieves selected environment variables of running Docker containers.

    This function collects environment variables with names starting with "host.mapping" or "port.mapping"
    from all currently running Docker containers and stores them in the `container_ports` table in the SQLite database.

    Parameters:
    - cursor (sqlite3.Cursor): A SQLite cursor object for executing SQL commands.
    - args (object): An argument object, typically obtained from argparse or a similar library.
                     It should have a 'verbose' attribute to determine the verbosity of the function.

    Returns:
    - None: The function doesn't return any value but commits the stored environment variable mappings in the database.

    Raises:
    - subprocess.CalledProcessError: If there's an error executing the Docker commands.
    """

    # Log and optionally print the function entry message
    logger_info.info("Entered get_container_mappings function.")
    if args.verbose:
        print("Started fetching container environment variable mappings.")

    client = docker.from_env()

    try:
        containers = client.containers.list()

        batch_inserts = []

        for container in containers:
            data = container.attrs

            container_name = data.get('Name', '').lstrip('/')
            env_data = data.get('Config', {}).get('Env', [])

            for env_entry in env_data:
                if '=' not in env_entry:
                    continue
                name, value = env_entry.split("=", 1)  # Split only on the first '='
                if name.startswith('host.mapping') or name.startswith('port.mapping'):
                    batch_inserts.append((container_name, name, value))

                    # Optional verbosity
                    if args.verbose:
                        print(f"Prepared environment variable mapping for {container_name}: {name} -> {value}")

                # Check the size of batch_inserts and insert if needed
                if len(batch_inserts) >= BATCH_SIZE:
                    insert_env_batch(cursor, batch_inserts)
                    batch_inserts = []

        if batch_inserts:
            insert_env_batch(cursor, batch_inserts)

        # Commit the executed queries
        cursor.connection.commit()

        # Log and optionally print the function exit message
        logger_info.info("Container environment variable data fetched and stored successfully.")
        if args.verbose:
            print("Finished fetching container environment variable mappings.")
    except docker.errors.APIError as error:
        logger_info.error("Error encountered while fetching container data from Docker SDK: %s", error, exc_info=True)
        raise error
    except Exception as error:
        logger_info.error("Error encountered while fetching/storing container environment variable data: %s", error, exc_info=True)
        raise error
    try:
        # Export the container_ports table to a CSV
        export_container_ports_to_csv(cursor, args)
    except Exception as exc:
        error_msg = "Unexpected error while exporting container_ports to CSV."
        logger_info.exception(error_msg)
        if args.verbose:
            print(error_msg)
        raise exc

# -------------------------------------------------------------------------
def insert_env_batch(cursor: sqlite3.Cursor, batch_inserts: list):
    """
    Inserts a batch of environment variable mappings into the container_ports table.

    This function performs a batch insertion of environment variable mappings
    into the `container_ports` table in the SQLite database to improve performance
    and reduce the number of individual insert operations.

    Parameters:
    - cursor (sqlite3.Cursor): A SQLite cursor object for executing SQL commands.
    - batch_inserts (list): A list of tuples, where each tuple contains:
        1. container_name (str): The name of the Docker container.
        2. mapping_name (str): The name of the environment variable (e.g., "host.mappingXXX").
        3. mapping_value (str): The value of the environment variable.

    Returns:
    - None: The function does not return any value, but executes the batch insert operations on the database.

    Raises:
    - sqlite3.Error: In case of any SQLite database errors.
    """
    query = "INSERT INTO container_ports (container_name, mapping_name, mapping_value) VALUES (?, ?, ?)"
    cursor.executemany(query, batch_inserts)

# -------------------------------------------------------------------------
def export_container_ports_to_csv(cursor: Cursor, args, output_file: str = output_csv_file):
    """
    Export the container_ports table from the SQLite database to a CSV file.

    Parameters:
    - cursor (Cursor): SQLite database cursor to fetch data.
    - args (object): An argument object with a 'verbose' attribute determining the verbosity.
    - output_file (str): The file path for the output CSV. Default is determined by the "output_csv_file" variable.

    Raises:
    - FileNotFoundError: If there's an issue accessing the output file.
    - Error: If there's a database-specific error.
    - Exception: For any unexpected error that occurs.

    Notes:
    - Always logs function entry, exit, and important steps to the info log file.
    - Outputs to the console when 'args.verbose' is set to True.
    """

    entry_msg = f"Starting the export of container_ports table to {output_file}."
    logger_info.info(entry_msg)
    if args.verbose:
        print(entry_msg)

    try:
        # Fetch all records from container_ports table
        cursor.execute("SELECT * FROM container_ports")
        rows = cursor.fetchall()

        # If no rows are fetched, then there's no data to export
        if not rows:
            no_data_msg = "No data available in container_ports to export."
            logger_info.info(no_data_msg)
            if args.verbose:
                print(no_data_msg)
            return

        # Extract column names (headers) from the cursor description
        headers = [column[0] for column in cursor.description]

        # Write data to the specified CSV file
        if args.verbose:
            print(f"Exporting data to CSV: {output_file}")
        with open(output_file, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file, lineterminator='\n')

            # Write headers and rows to CSV
            csv_writer.writerow(headers)
            csv_writer.writerows(rows)

        success_msg = f"Successfully exported container_ports data to {output_file}."
        logger_info.info(success_msg)
        if args.verbose:
            print(success_msg)

    except FileNotFoundError:
        error_msg = f"Output file not found or inaccessible: {output_file}"
        logger_info.error(error_msg)
        if args.verbose:
            print(error_msg)
        raise
    except Error as db_error:
        error_msg = f"Database error while fetching data from container_ports table: {db_error}"
        logger_info.error(error_msg)
        if args.verbose:
            print(error_msg)
        raise
    except Exception as exc:
        error_msg = "Unexpected error while exporting container_ports to CSV."
        logger_debug.exception(error_msg)
        if args.verbose:
            print(error_msg)
        raise exc
    finally:
        exit_msg = f"Finished the export of container_ports table to {output_file}."
        logger_info.info(exit_msg)
        if args.verbose:
            print(exit_msg)

# -------------------------------------------------------------------------
def export_container_info_to_csv(args):
    """
    Export the current container info from Docker to a CSV file.

    Parameters:
    - args (object): An argument object with a 'verbose' attribute determining the verbosity.

    Raises:
    - subprocess.CalledProcessError: If there's an error executing the Docker commands.
    """
    csv_filename = os.path.join("..", "data", "dcpd_docker_ps.csv")

    entry_msg = f"Starting the export of container info to {csv_filename}."
    logger_info.info(entry_msg)
    if args.verbose:
        print(entry_msg)

    try:
        # Execute the docker ps command with the desired format
        docker_output = subprocess.getoutput('docker ps -a --format "{{.ID}},{{.Image}},{{.Command}},{{.CreatedAt}},{{.Status}},{{.Names}}"')

        # Write the output to the CSV file
        with open(csv_filename, 'w', encoding='utf-8') as file:
            # Write the header row first
            file.write("ID,IMAGE,COMMAND,CREATED AT,STATUS,NAMES\n")
            # Write the docker output
            file.write(docker_output + '\n')

        success_msg = f"Successfully exported container info to {csv_filename}."
        logger_info.info(success_msg)
        if args.verbose:
            print(success_msg)
    except subprocess.CalledProcessError as error:
        error_msg = f"Error encountered while executing Docker commands: {error}"
        logger_info.error(error_msg, exc_info=True)
        if args.verbose:
            print(error_msg)
        raise error

# -------------------------------------------------------------------------
def export_container_stats_to_txt(args):
    """
    Export the current container stats from Docker to a text file

    Parameters:
    - args (object): An argument object with a 'verbose' attribute determining the verbosity.

    Raises:
    - subprocess.CalledProcessError: If there's an error executing the Docker commands.
    """
    txt_filename = os.path.join("..", "data", "dcpd_docker_stats.txt")

    entry_msg = f"Starting the export of container stats to {txt_filename}."
    logger_info.info(entry_msg)
    if args.verbose:
        print(entry_msg)

    cmd = [
        "docker",
        "stats",
        "--no-stream",
        "--format",
        "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Write the output to the text file with an additional newline at the end
        with open(txt_filename, 'w', encoding='utf-8') as file:
            file.write(result.stdout + '\n')

        success_msg = f"Successfully exported container stats to {txt_filename}."
        logger_info.info(success_msg)
        if args.verbose:
            print(success_msg)

    except subprocess.CalledProcessError:
        error_msg = "Error encountered while executing Docker commands."
        logger_info.error(error_msg, exc_info=True)
        if args.verbose:
            print(error_msg)
        raise

    except Exception as error:
        error_msg = f"Unexpected error: {error}"
        logger_info.error(error_msg, exc_info=True)
        if args.verbose:
            print(error_msg)
        raise error
