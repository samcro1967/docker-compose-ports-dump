"""
dcpd_debug.py

Debugging and Reporting Module for Docker Compose Ports Dump

This module provides functions to generate comprehensive debug reports, display environment information,
and output statistics related to Docker Compose Ports Dump. It contains utility functions for printing
debug informationand formatting data for presentation.

"""

import os
import platform
import re
import sqlite3
import subprocess
from typing import Any, Dict, List, Optional, Tuple
import sys
import pkg_resources
from tabulate import tabulate

# Add config to the sys path
# pylint: disable=wrong-import-position
sys.path.extend(['.', '../config'])

# Third-party imports (if any)
import dcpd_config
import dcpd_compose_parser as dcpd_cp
import dcpd_log_debug
import dcpd_log_info
import dcpd_pip
import dcpd_utils

# pylint: disable=R0914,R0913
# Variables from dcpd_config.py
import dcpd_arguments_parser as dcpd_ap
default_docker_compose_file = dcpd_config.DEFAULT_DOCKER_COMPOSE_FILE
default_vpn_container_name = dcpd_config.DEFAULT_VPN_CONTAINER_NAME
lines_per_page = dcpd_config.LINES_PER_PAGE
default_web_page_background_color = dcpd_config.DEFAULT_WEB_PAGE_BACKGROUND_COLOR
default_web_page_text_color = dcpd_config.DEFAULT_WEB_PAGE_TEXT_COLOR
terminal_color_reset = dcpd_config.TERMINAL_COLOR_RESET
debug_report_header_color = dcpd_config.DEBUG_REPORT_HEADER_COLOR

# Constants for table headers
PORT_MAPPINGS_HEADERS = ['ID', 'External Port', 'Mapping Values']
PORTS_DATA_HEADERS = ['ID', 'service_name', 'external_port', 'internal_port', 'has_port_mapping', 'mapped_app']

# Create an alias for convenience
logger_info = dcpd_log_info.logger
logger_debug = dcpd_log_debug.logger
version=dcpd_config.VERSION

# Parsing command-line arguments to determine the user's desired functionality.
args = dcpd_ap.parse_arguments()

# Modify the path for files
debug_txt = os.path.join("..", "data", "dcpd_debug.txt")

# Global map for special cases where module name and pip package name differ
module_to_package_map = {
    "yaml": "PyYAML",
    "markdown_it": "markdown-it-py",
}

# -------------------------------------------------------------------------
def generate_debug_info(cursor: Any, verbose: bool = False) -> Tuple[Dict[str, Any], str, str, List[str]]:
    """
    Generate debug information for troubleshooting purposes.

    Parameters
    ----------
    cursor : Any
        A cursor object for executing SQL commands on the database.
    verbose : bool, optional
        Flag to control verbosity of logging, by default False.

    Returns
    -------
    Tuple[Dict[str, Any], str, str, List[str]]
        - debug_info: A dictionary containing various debug information.
        - port_mapping_str: A string representation of the port mappings.
        - ports_data_str: A string representation of the port data.
        - environment_data_lines: List of strings representing environment data.
    """

    logger_info.info("Starting debug info generation.")
    if verbose:
        print("Starting debug info generation.")

    # Initialize debug_info here
    debug_info = {
        "environment_data": get_environment_data()
    }

    try:
        # Assemble the environment data section
        environment_data_lines = [
            f"os_name: {debug_info['environment_data']['os_name']}",
            f"platform_system: {debug_info['environment_data']['platform_system']}",
            f"platform_release: {debug_info['environment_data']['platform_release']}",
        ]
        for key, value in debug_info['environment_data'].items():
            if key not in ['os_name', 'platform_system', 'platform_release']:
                environment_data_lines.append(f"{key}: {value}")

        # Fetching port mappings and service information from the database using helper methods.
        port_mappings = dcpd_cp.fetch_port_mappings(cursor, args)
        raw_ports_data = dcpd_cp.fetch_service_info(cursor, args)

        # Convert the raw_ports_data to a structured list of tuples
        ports_data = [
            (row['id'], row['service_name'], row['external_port'], row['internal_port'], row['has_port_mapping'], row['mapped_app'])
            for row in raw_ports_data
        ]

        # Getting pip version using subprocess
        pip_version = subprocess.run(["pip", "--version"], capture_output=True, text=True, check=True).stdout.strip()

        # Fetching SQLite version
        sqlite_version = cursor.connection.execute('SELECT sqlite_version()').fetchone()[0]

        # Convert the port_mappings to a structured list of tuples
        port_mappings = [(row['id'], row['external_port'], row['mapping_values']) for row in port_mappings]

        # Convert module names to package names
        required_modules = dcpd_pip.get_required_pip_modules(args)
        required_packages = [module_to_package(module_name, args) for module_name in required_modules]

        # Get versions of the required packages
        package_versions = get_package_versions(required_packages, args)

        # Sort packages alphabetically ignoring case
        sorted_packages_with_versions = dict(sorted(package_versions.items(), key=lambda item: item[0].lower()))

        # Compiling all debug information into a dictionary
        debug_info.update({
            "port_mappings": port_mappings,
            "ports_data": ports_data,
            "python_version": platform.python_version(),
            "pip_version": pip_version,
            "sqlite_version": sqlite_version,
            "installed_packages_list": sorted_packages_with_versions,
            "docker_compose_file": default_docker_compose_file,
            "vpn_container_name": default_vpn_container_name,
        })

        # Generating string representations for port mappings and ports data using helper methods
        port_mapping_str = generate_port_mapping_str(port_mappings)

        ports_data_str = generate_ports_data_str(ports_data)

        logger_info.info("Finished generating debug info.")

        return debug_info, port_mapping_str, ports_data_str, environment_data_lines

    except subprocess.CalledProcessError:
        msg = "Failed to fetch the pip version."
        logger_info.error(msg)
        if verbose:
            print(msg)
        raise
    except sqlite3.Error as error:
        msg = f"Database error: {error}"
        logger_info.error(msg)
        if verbose:
            print(msg)
        raise
    except Exception as error:
        msg = f"Unexpected error during debug info generation: {error}"
        logger_info.error(msg)
        if verbose:
            print(msg)
        raise

# -------------------------------------------------------------------------
def module_to_package(module_name: str, cmdline_args) -> str:
    """
    Convert a module name to its corresponding package name.

    Parameters:
    - module_name (str): The name of the module to be converted.
    - cmdline_args: Parsed command-line arguments.

    Returns:
    - str: The package name corresponding to the module. If no mapping exists, returns the module name.
    """
    logger_debug.info("Function module_to_package() started for module: %s.", module_name)
    if cmdline_args.verbose:
        print(f"Function module_to_package() started for module: {module_name}.")

    package_name = module_to_package_map.get(module_name, module_name)
    logger_debug.debug("Converted %s to %s.", module_name, package_name)

    logger_debug.info("Function module_to_package() completed. Module %s mapped to package %s.", module_name, package_name)
    if cmdline_args.verbose:
        print(f"Function module_to_package() completed. Module {module_name} mapped to package {package_name}.")

    return package_name

# -------------------------------------------------------------------------
def get_package_versions(package_list: list, cmd_args) -> dict:
    """
    Get the version numbers of the given packages.

    Parameters:
    - package_list (list): List of package names to check versions for.
    - cmd_args: Parsed command-line arguments.

    Returns:
    - dict: A dictionary where keys are package names and values are their respective versions.
    """
    logger_info.info("Function get_package_versions() started.")
    if cmd_args.verbose:
        print("Function get_package_versions() started.")

    versions = {}
    for package in package_list:
        try:
            versions[package] = pkg_resources.get_distribution(package).version
            logger_debug.debug("Package %s version: %s", package, versions[package])
        except pkg_resources.DistributionNotFound:
            versions[package] = "Not Installed"
            logger_debug.debug("Package %s is not installed.", package)

    logger_info.info("Function get_package_versions() completed.")
    if args.verbose:
        print("Function get_package_versions() completed.")

    return versions

# -------------------------------------------------------------------------
def get_environment_data(verbose: bool = False) -> Dict[str, str]:
    """
    Retrieve relevant environment variables and system information for debugging purposes.

    Args:
        verbose (bool, optional): Flag to control verbosity of logging. Defaults to False.

    Returns:
        Dict[str, str]: A dictionary containing environment variable names and their values.
    """

    # Dictionary to hold environment data.
    environment_data = {}

    # List of environment variables to fetch.
    env_var_names = ["PATH", "HOME", "PWD"]

    # Fetch values for the specified environment variables.
    for var in env_var_names:
        environment_data[var] = os.environ.get(var, 'Not Set')

    # Fetch and store system-specific data.
    environment_data["os_name"] = os.name
    environment_data["platform_system"] = platform.system()

    # Fetch details about the operating platform.
    system = platform.system()
    release = platform.release()
    platform_version = platform.version()

    environment_data["platform_system_alias"] = platform.system_alias(system, release, platform_version)
    environment_data["platform_release"] = release
    environment_data["platform_machine"] = platform.machine()

    # Fetch specific data from FreeDesktop OS release details.
    keys_to_include = ["VERSION", "ID_LIKE"]
    try:
        freedesktop_os_data = platform.freedesktop_os_release()
        for key in keys_to_include:
            if key in freedesktop_os_data:
                environment_data[f"freedesktop_{key}"] = freedesktop_os_data[key]
    except (FileNotFoundError, NotImplementedError) as error:
        # Handle issues while fetching FreeDesktop OS details.
        for key in keys_to_include:
            environment_data[f"freedesktop_{key}"] = "Not available or failed to fetch"
        if verbose:
            print(f"Failed to retrieve FreeDesktop OS data: {error}")

    # Log environment data for debugging.
    dcpd_utils.log_separator_data(logger_debug)
    logger_debug.debug("Raw environment_data: %s", environment_data)
    dcpd_utils.log_separator_data(logger_debug)

    # If verbose flag is set, print the environment data.
    if verbose:
        print("Environment Data:")
        for key, value in environment_data.items():
            print(f"{key}: {value}")

    return environment_data

# -------------------------------------------------------------------------
def print_debug_output(debug_info: Dict[str, Any], port_mapping_str: str, ports_data_str: str, environment_data_lines: List[str], paginate: bool = True, display: bool = False, verbose: bool = False):
    """
    Print the debug information for troubleshooting purposes.

    Args:
        debug_info (Dict[str, Any]): Information related to configuration, dependencies, etc.
        port_mapping_str (str): Formatted string representation of port mappings.
        ports_data_str (str): Formatted string representation of port data.
        environment_data_lines (List[str]): System and environment related data.
        paginate (bool): Whether to paginate the output for better readability. Defaults to True.
        display (bool): If True, display the output. If False, just generate a debug file. Defaults to False.
        verbose (bool): Flag to control verbosity of logging and output. Defaults to False.
    """

    # Start the logging process for debug output generation.
    logger_info.info("Beginning to print the debug output.")

    try:
        # Creating a comprehensive report string for debugging. This string encompasses:
        # - System and environment information
        # - Configuration data sourced from dcpd_config.py
        # - Dependency version information (like Python, pip, SQLite)
        # - Details of installed pip modules

        # Constructing the main debug info string:
        # - Information about the configuration setup from dcpd_config.py
        # - Version details of dependencies such as Python, pip, and SQLite
        # - Installed pip modules and their respective versions
        report_str = "\n".join([
            f"{debug_report_header_color}Debug Report:{terminal_color_reset}",
            f"\nDocker Compose Ports Dump Version:  {version}",
            f"{debug_report_header_color}\nEnvironment Data:{terminal_color_reset}",
            "\n".join(environment_data_lines),
            f"{debug_report_header_color}\nVariables defined in dcpd_config.py:{terminal_color_reset}",
            f"Default Docker Compose File: {default_docker_compose_file}",
            f"Default VPN Container Name: {default_vpn_container_name}",
            f"Lines per Page: {lines_per_page}",
            f"Default Web Page Background Color: {default_web_page_background_color}",
            f"Default Web Page Accent Color: {dcpd_config.DEFAULT_WEB_PAGE_ACCENT_COLOR}",
            f"Default Web Page Text Color: {default_web_page_text_color}",
            f"Default Web Page Font Name: {dcpd_config.DEFAULT_WEB_PAGE_FONT_NAME}",
            f"Default Web Page Font Size: {dcpd_config.DEFAULT_WEB_PAGE_FONT_SIZE}",
            f"{debug_report_header_color}\nDependency Versions:{terminal_color_reset}",
            f"Python3: {debug_info['python_version']}",
            f"pip3: {debug_info['pip_version']}",
            f"SQLite: {debug_info['sqlite_version']}",
            f"{debug_report_header_color}\nPip Package Versions:{terminal_color_reset}",
            "\n".join(f"{module}: {debug_info['installed_packages_list'][module]}" for module in debug_info['installed_packages_list']),  # Print module name and version
            f"{debug_report_header_color}\nPort Mapping Environment Variables from Docker Compose:{terminal_color_reset}"
        ])

        # Combining main debug info with port details
        combined_debug_str = report_str + port_mapping_str + ports_data_str

        # Removing ANSI escape sequences
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        cleaned_debug_str = ansi_escape.sub('', combined_debug_str)

        # Writing the debug info to a file
        with open(debug_txt, 'w', encoding='utf-8') as file:
            file.write(cleaned_debug_str)

        # Control the output display based on the 'display' flag
        if not display:
            if verbose:
                print("Debug information written to 'dcpd_debug.txt'.")
            return
        if display:
            if paginate:
                dcpd_utils.paginate_output(combined_debug_str)
            else:
                print(combined_debug_str)

        logger_info.info("Finished printing the debug output.")

    # Handle interruptions and exceptions
    except Exception as error:
        logger_info.error("An error occurred during debug output generation: %s", error)
        raise error

# -------------------------------------------------------------------------
def generate_port_mapping_str(port_mappings: List[Tuple[int, int, str]], verbose: bool = False) -> str:
    """
    Generate a string representation of the port mappings table.

    Args:
        port_mappings (List[Tuple[int, int, str]]): List of port mapping tuples.
        Each tuple contains:
        - Host port (int)
        - Container port (int)
        - Service name (str)
        verbose (bool, optional): Controls the verbosity of the function's output. Defaults to False.

    Returns:
        str: A formatted string representation of the port mappings in tabulated form.

    Raises:
        ValueError: If the input port mappings list is empty or malformed.
    """

    try:
        # Logging and optionally printing the start of the function.
        logger_info.info("Beginning port mapping string generation.")
        if verbose:
            print("Beginning port mapping string generation...")

        # Check the integrity of the input data.
        if not port_mappings or not all(isinstance(tup, tuple) and len(tup) == 3 for tup in port_mappings):
            logger_info.error("Invalid or empty port mappings provided.")
            raise ValueError("Port mappings should be a non-empty list of 3-element tuples.")

        # Header for the port mappings table
        port_mapping_header = "\n======= Port Mappings Table =======\n"

        # Sorting the port mappings based on the service name (3rd element of the tuple)
        sorted_port_mappings = sorted(port_mappings, key=lambda x: x[2])

        # Optionally print the sorted mappings if verbosity is enabled.
        if verbose:
            print("Sorted port mappings:")
            for mapping in sorted_port_mappings:
                print(mapping)

        # Generating the tabulated format of the port mappings.
        result = port_mapping_header + tabulate(sorted_port_mappings, headers=PORT_MAPPINGS_HEADERS, tablefmt='grid')

        # Logging and optionally printing the completion of the function.
        logger_info.info("Finished port mapping string generation.")
        if verbose:
            print("Finished port mapping string generation.")

        return result

    except Exception as error:
        logger_info.error("Error occurred while generating port mapping string: %s", error)
        raise

# -------------------------------------------------------------------------
def generate_ports_data_str(ports_data: List[Tuple[int, str, Optional[int], Optional[int], str, str]], verbose: bool = False) -> str:
    """
    Generate a string representation of the ports data table.

    Args:
        ports_data (List[Tuple[int, str, Optional[int], Optional[int], str, str]]): List of tuples representing port data.
            Each tuple contains:
            - An index (int)
            - Service name (str)
            - Host port (int or None)
            - Container port (int or None)
            - A flag (1 or 0 indicating True or False)
            - A description (str)
        verbose (bool, optional): Controls the verbosity of the function's output. Defaults to False.

    Returns:
        str: A formatted string representation of the ports data in tabulated form.

    Raises:
        ValueError: If the input ports data list is empty or malformed.
    """

    try:
        # Logging and optionally printing the start of the function.
        logger_info.info("Beginning generation of the ports data string.")
        if verbose:
            print("Starting generation of ports data string...")

        # Check the integrity of the input data.
        if not ports_data or not all(isinstance(tup, tuple) and len(tup) == 6 for tup in ports_data):
            raise ValueError("Ports data should be a non-empty list of 6-element tuples.")

        # Header for the ports data table.
        ports_data_header = "\n======= Ports Data Table =======\n"

        # Sorting the ports data based on the service name.
        sorted_ports_data = sorted(ports_data, key=lambda x: x[1].lower())

        # Optionally print the sorted data if verbosity is enabled.
        if verbose:
            print("Sorted ports data:")
            for data in sorted_ports_data:
                print(data)

        # Formatting the ports data.
        formatted_ports_data = [
            (idx, service, host if host is not None else "N/A", container if container is not None else "N/A",
             'True' if flag == 1 else 'False', description)
            for idx, service, host, container, flag, description in sorted_ports_data
        ]

        # Logging and optionally printing the completion of the function.
        logger_info.info("Finished generation of the ports data string.")
        if verbose:
            print("Ports data string generation completed.")

        # Returning the ports data in a tabulated format.
        return ports_data_header + tabulate(formatted_ports_data, headers=PORTS_DATA_HEADERS, tablefmt='grid', numalign="center", stralign="center")

    except ValueError as value_error:
        logger_info.error("Value Error: %s", value_error)
        raise
    except Exception as error:
        logger_info.error("Unexpected error occurred: %s", error)
        raise
