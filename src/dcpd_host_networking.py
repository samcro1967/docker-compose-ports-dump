# dcpd_host_networking.py

import sys

# Add config to the sys path
sys.path.append('../config')

# Import required modules
import csv
import os
import pprint
import sqlite3
from sqlite3 import Cursor, Error
from typing import Any, Dict, List, Tuple, Union
import yaml

# Custom Modules imports
import dcpd_config as dcpd_config
import dcpd_log_debug as dcpd_log_debug
import dcpd_log_info as dcpd_log_info
import dcpd_utils as dcpd_utils

# Create an alias for convenience
logger_info = dcpd_log_info.logger
logger_debug = dcpd_log_debug.logger

# Variables from dcpd_config.py
default_docker_compose_file = dcpd_config.DEFAULT_DOCKER_COMPOSE_FILE
default_vpn_container_name = dcpd_config.DEFAULT_VPN_CONTAINER_NAME

# Modify the path for files
output_csv_file = os.path.join("..", "data", "dcpd_host_networking.csv")

# -------------------------------------------------------------------------
def host_networking(cursor: Cursor, args):
    """
    Collects service names from the default_docker_compose_file that have network_mode set to 'host'.
    Inserts these services into the host_networking table in the database, and exports to a CSV.

    Parameters:
    - cursor (Cursor): Database cursor for executing SQL commands.
    - args (object): An argument object with a 'verbose' attribute determining the verbosity.

    Raises:
    - FileNotFoundError: If the default_docker_compose_file doesn't exist.
    - yaml.YAMLError: If there's a problem parsing the YAML content.
    - Error: If there's a database error.
    - Exception: If an unexpected error occurs.

    Notes:
    - Always logs function entry, exit, and important steps to the info log file.
    - Outputs to the console when 'args.verbose' is set to True.
    """
    
    entry_msg = "Starting the processing of host networking..."
    logger_info.info(entry_msg)
    if args.verbose:
        print(entry_msg)

    for file_path in default_docker_compose_file:
        # Read and parse the docker-compose file
        try:
            with open(file_path, 'r') as file:
                compose_content = yaml.safe_load(file)
        except FileNotFoundError:
            error_msg = f"File not found: {file_path}"
            logger_info.error(error_msg)
            if args.verbose:
                print(error_msg)
            raise
        except yaml.YAMLError as exc:
            error_msg = f"Error parsing YAML file {file_path}: {exc}"
            logger_info.error(error_msg)
            if args.verbose:
                print(error_msg)
            raise

        try:
            # Extract services with network_mode set to "host"
            services_with_host_networking = [
                service_name for service_name, service_config in compose_content.get('services', {}).items() 
                if service_config.get('network_mode') == "host"
            ]
            
            # Sort the services alphabetically
            services_with_host_networking.sort()

            # Insert services into the database
            for service_name in services_with_host_networking:
                cursor.execute("INSERT INTO host_networking (service_name) VALUES (?)", (service_name,))

            processed_services = []

            for service_name, service_config in compose_content.get('services', {}).items():
                process_host_mappings(cursor, service_name, service_config, args)
                processed_services.append(service_name)

            # Print to console if verbose
            if args.verbose:
                print(f"Processed host mappings for services: {', '.join(processed_services)}")

            # Log to debug log
            logger_debug.debug(f"Processed host mappings for services: {', '.join(processed_services)}")  

            # Commit the changes to the database
            cursor.connection.commit()

            # Logging
            logger_info.info(f"Successfully inserted {len(services_with_host_networking)} service names into the host_networking table.")
            logger_debug.debug(f"Services with host networking: {', '.join(services_with_host_networking)}")

        except Error as db_error:
            error_msg = f"Database error while inserting service names into the host_networking table: {db_error}"
            logger_info.error(error_msg)
            if args.verbose:
                print(error_msg)
            raise
        except Exception as exc:
            error_msg = "Unexpected error while processing host networking data."
            logger_info.exception(error_msg)
            if args.verbose:
                print(error_msg)
            raise exc

        exit_msg = "Processing of host networking completed successfully!"
        logger_info.info(exit_msg)
        if args.verbose:
            print(exit_msg)

        try:
            # Export the host_networking table to a CSV
            export_host_networking_to_csv(cursor, args)  
        except Exception as exc:
            error_msg = "Unexpected error while exporting host networking to CSV."
            logger_info.exception(error_msg)
            if args.verbose:
                print(error_msg)
            raise exc

# -------------------------------------------------------------------------
def export_host_networking_to_csv(cursor: Cursor, args, output_file: str = output_csv_file):
    """
    Export the host_networking table from the SQLite database to a CSV file.

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
    
    entry_msg = f"Starting the export of host_networking table to {output_file}."
    logger_info.info(entry_msg)
    if args.verbose:
        print(entry_msg)

    try:
        # Fetch all records from host_networking table
        cursor.execute("SELECT * FROM host_networking")
        rows = cursor.fetchall()

        # If no rows are fetched, then there's no data to export
        if not rows:
            no_data_msg = "No data available in host_networking to export."
            logger_info.info(no_data_msg)
            if args.verbose:
                print(no_data_msg)
            return
        
        # Extract column names (headers) from the cursor description
        headers = [column[0] for column in cursor.description]

        # Write data to the specified CSV file
        if args.verbose:
            print(f"Exporting data to CSV: {output_file}")
        with open(output_file, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, lineterminator='\n')
            
            # Write headers and rows to CSV
            csv_writer.writerow(headers)
            csv_writer.writerows(rows)

        success_msg = f"Successfully exported host_networking data to {output_file}."
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
        error_msg = f"Database error while fetching data from host_networking table: {db_error}"
        logger_info.error(error_msg)
        if args.verbose:
            print(error_msg)
        raise
    except Exception as exc:
        error_msg = "Unexpected error while exporting host_networking to CSV."
        logger_debug.exception(error_msg)
        if args.verbose:
            print(error_msg)
        raise exc
    finally:
        exit_msg = f"Finished the export of host_networking table to {output_file}."
        logger_info.info(exit_msg)
        if args.verbose:
            print(exit_msg)

# -------------------------------------------------------------------------
def process_host_mappings(cursor: sqlite3.Cursor, service_name: str, service_config: dict, args):
    """
    Processes 'host.mapping' values from the service configuration and inserts 
    them into the 'service_info' table. The function will process all 'host.mapping' 
    values associated with the specified service.

    Args:
    - cursor (sqlite3.Cursor): Cursor for database interactions.
    - service_name (str): Name of the Docker service.
    - service_config (dict): Configuration details of the service, specifically the 'environment' details.
    - args (object): An argument object with a 'verbose' attribute determining the verbosity.

    Returns:
    None

    Notes:
    - Always logs function entry, exit, and important steps to the info log file.
    - Outputs to the console when 'args.verbose' is set to True.
    """
    
    entry_msg = f"Starting the processing of host mappings for service: {service_name}."
    logger_info.info(entry_msg)
    if args.verbose:
        print(entry_msg)

    environment_data = service_config.get('environment', [])
    
    # Extract host.mapping values from the environment data
    host_mappings = [s.split('=')[1] for s in environment_data if s.startswith("host.mapping")]

    for port_value in host_mappings:
        if port_value:
            try:
                # Inserting data into the database
                cursor.execute(
                    """
                    INSERT INTO service_info 
                    (service_name, external_port, internal_port, has_port_mapping, mapped_app) 
                    VALUES (?, ?, ?, ?, ?)
                    """, 
                    ("host", port_value, port_value, 1, service_name)
                )

                success_msg = f"Data for service: {service_name} with host.mapping={port_value} added to service_info table."
                logger_info.info(success_msg)
                if args.verbose:
                    print(success_msg)

                logger_debug.debug(f"Service {service_name} host.mapping={port_value} processed.")

            except sqlite3.IntegrityError:
                warning_msg = f"Duplicate entry for service: {service_name} with host.mapping={port_value}. Skipping."
                logger_info.warning(warning_msg)
                if args.verbose:
                    print(warning_msg)
                continue
            except sqlite3.Error as e:
                error_msg = f"DB error processing service: {service_name} with host.mapping={port_value}. Error: {e}"
                logger_info.error(error_msg)
                if args.verbose:
                    print(error_msg)
                continue
            except Exception as e:
                error_msg = f"Unexpected error processing service: {service_name}. Error: {e}"
                logger_debug.exception(error_msg)
                if args.verbose:
                    print(error_msg)
                continue

    # Commit once after processing all host mappings for the current service
    cursor.connection.commit()

    exit_msg = f"Finished processing of host mappings for service: {service_name}."
    logger_info.info(exit_msg)
    if args.verbose:
        print(exit_msg)