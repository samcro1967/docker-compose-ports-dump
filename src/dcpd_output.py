# dcpd_output.py
# This file contains functions to generate a web page with the port mappings from the parsed docker-compose.yml file.

import sys

# Add config to the sys path
sys.path.append('../config')

import ast
import csv
import datetime
import dcpd_config as dcpd_config
import dcpd_log_debug as dcpd_log_debug
import dcpd_log_info as dcpd_log_info
import dcpd_utils as dcpd_utils
import importlib.util
import json
import os
import re
import pkg_resources
import pkgutil
import requests
import sqlite3
import subprocess
import sysconfig
import time
from typing import List, Tuple, Any
import psutil

# Using the variables from config.py
default_docker_compose_file = dcpd_config.DEFAULT_DOCKER_COMPOSE_FILE
default_vpn_container_name = dcpd_config.DEFAULT_VPN_CONTAINER_NAME
default_output_html_file_name = dcpd_config.DEFAULT_OUTPUT_HTML_FILE_NAME
default_web_page_background_color = dcpd_config.DEFAULT_WEB_PAGE_BACKGROUND_COLOR
default_web_page_text_color = dcpd_config.DEFAULT_WEB_PAGE_TEXT_COLOR
default_sort_order = dcpd_config.DEFAULT_SORT_ORDER
default_debug_mode=dcpd_config.DEFAULT_DEBUG_MODE
location_cache_hours=dcpd_config.LOCATION_CACHE_HOURS
version=dcpd_config.VERSION

# Modify the path for files
default_output_html_file = os.path.join("..", "config", default_output_html_file_name)
html_template_file = os.path.join("..", "web", 'dcpd_output_template.html')
output_csv_file = os.path.join("..", "data", "dcpd.csv")
output_json_file = os.path.join("..", "data", "dcpd_html.json")
CACHE_FILE = os.path.join("..", "data", "dcpd_cache_location.json")
CACHE_DURATION = datetime.timedelta(hours=location_cache_hours)  # Cache data for 24 hours

# Create an alias for convenience
logger_info = dcpd_log_info.logger
logger_debug = dcpd_log_debug.logger

# -------------------------------------------------------------------------
def is_valid_background_theme(theme_name: str, args) -> bool:
    """
    Checks if the provided background theme name is valid.

    Args:
    - theme_name (str): The name of the background theme to be checked.
    - args (object): An argument object with a 'verbose' attribute determining the verbosity.

    Returns:
    bool: True if the theme name is valid, False otherwise.

    Notes:
    - Logs the validity check result to the debug log file.
    - Outputs to the console when 'args.verbose' is set to True.
    """
    
    entry_msg = f"Starting the validity check for background theme: {theme_name}."
    logger_info.info(entry_msg)
    if args.verbose:
        print(entry_msg)

    # List of valid background themes
    valid_themes = [
        "hotpink",
        "cyan",
        "teal",
        "orange",
        "purple",
        "lime",
        "magenta",
        "navy",
        "olive",
        "steelblue",
        "scarlet",
        "grey"
    ]

    if theme_name.lower() in valid_themes:
        success_msg = f"Background theme {theme_name} is valid."
        logger_debug.debug(success_msg)
        if args.verbose:
            print(success_msg)
        return True
    else:
        failure_msg = f"Background theme {theme_name} is invalid."
        logger_debug.debug(failure_msg)
        if args.verbose:
            print(failure_msg)
        return False


# -------------------------------------------------------------------------
def generate_table_rows(ports_data: List[Tuple[str, Any]], args) -> str:
    """
    Generates HTML table rows based on the provided port data.

    Args:
    - ports_data (List[Tuple]): A list of tuples containing port data.
    - args (object): An argument object with a 'verbose' attribute determining the verbosity.

    Returns:
    str: A string containing HTML table rows.

    Notes:
    - Logs the process of generating table rows to the debug log file.
    - Outputs to the console when 'args.verbose' is set to True.
    """

    entry_msg = "Starting to generate table rows for port data."
    logger_info.info(entry_msg)
    if args.verbose:
        print(entry_msg)

    rows = ""
    try:
        for row in ports_data:
            # Unpack the port mapping data for each row
            service_name, external_port, internal_port, has_port_mapping, mapped_app = row

            # Skip the placeholder row for table header
            if service_name == "{{ row[\"Service Name\"] | escape }}":
                continue

            # Map the has_port_mapping value to "True" or "False" based on the BOOLEAN type
            port_mapping = "True" if has_port_mapping == 1 else "False"

            # Append the table row to the rows string
            rows += f"""
                <tr>
                    <td>{service_name}</td>
                    <td>{external_port}</td>
                    <td>{internal_port}</td>
                    <td>{port_mapping}</td>
                    <td>{mapped_app}</td>
                </tr>
            """

        success_msg = "Table rows successfully generated."
        logger_info.info(success_msg)
        if args.verbose:
            print(success_msg)
            
    except Exception as e:
        error_msg = f"Error while generating table rows: {e}"
        logger_info.error(error_msg)
        if args.verbose:
            print(error_msg)

    return rows.strip()  # Remove any trailing newline characters

# -------------------------------------------------------------------------
def generate_csv(data: List[Tuple[str, Any]], csv_file_path: str, args) -> None:
    """
    Generates a CSV file from the provided data.

    Args:
    - data (List[Tuple]): A list of tuples containing the data to be written to the CSV file.
    - csv_file_path (str): The path to the CSV file to be created.
    - args (object): An argument object with a 'verbose' attribute determining the verbosity.

    Returns:
    None

    Notes:
    - Logs the process of generating a CSV file to the debug log file.
    - Outputs to the console when 'args.verbose' is set to True.
    """
    
    entry_msg = "Starting CSV file generation."
    logger_info.info(entry_msg)
    if args.verbose:
        print(entry_msg)

    try:
        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_ALL)

            # Write header without quotes
            file.write("Service Name,External Port,Internal Port,Port Mapping,Mapped App\n")

            # Process and write data rows
            for row in data:
                service_name, external_port, internal_port, has_port_mapping, mapped_app = row

                # Convert 0 to False and 1 to True for the 'has_port_mapping' column
                has_port_mapping = "True" if has_port_mapping else "False"
                
                # Convert NULL/None values to "None"
                external_port = "None" if external_port is None else external_port
                internal_port = "None" if internal_port is None else internal_port

                # Write the row
                writer.writerow([service_name, external_port, internal_port, has_port_mapping, mapped_app])
            
            success_msg = f"CSV file successfully generated at {csv_file_path}."
            logger_info.info(success_msg)
            if args.verbose:
                print(success_msg)

    except Exception as e:
        error_msg = f"Error during CSV file generation: {e}"
        logger_info.error(error_msg)
        if args.verbose:
            print(error_msg)
            
# -------------------------------------------------------------------------
def generate_pretty_web_page(cursor: sqlite3.Cursor, args) -> None:
    """
    Generate a pretty web page displaying port mapping information.

    This function takes a database cursor and generates a web page using a template,
    replaces placeholders with actual data, and returns the content.

    Args:
        cursor (sqlite3.Cursor): The cursor connected to the database.

    Returns:
        None
    """
    
    logger_info.info("Generate Web Page")

    # Generate json file with variables for reading into JavaScript
    generate_output_json(args)
    
    # Get the current timestamp without seconds
    current_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    # Read the content of html_template_file as the template
    with open(html_template_file, 'r') as template_file:
        html_content = template_file.read()

    # Replace placeholders for file name and timestamp in the HTML content
    html_content = html_content.replace("{{output_file_name}}", default_output_html_file)
    html_content = html_content.replace("{{timestamp}}", str(current_timestamp))

    # Update the version in the template to the current version
    version_pattern = r'(<div class="version-info">Version: )(v[\d.]+)(</div>)'

    # Find matches for the version pattern
    matches = re.findall(version_pattern, html_content)

    # If in verbose mode, print matched versions and the updated version
    if args.verbose and matches:
        for match in matches:
            print(f"Original Matched Version: {match[1]}")
            print(f"Updated Version: {version}")

    # Substitute the matched version with the updated version
    new_html_content = re.sub(version_pattern, r'\1' + version + r'\3', html_content)

    # Write the updated HTML content back to the file
    with open(html_template_file, 'w') as file_handle:  # Changed 'file' to 'file_handle' for clarity
        file_handle.write(new_html_content)


    # Fetch the port mapping data from docker.db using the provided cursor
    cursor.execute("SELECT service_name, external_port, internal_port, has_port_mapping, mapped_app FROM service_info")
    ports_data = cursor.fetchall()

    # Generate CSV for this data
    generate_csv(ports_data, output_csv_file, args)

    # Generate the table rows
    rows = generate_table_rows(ports_data, args)

    # Replace the placeholder for table rows in the template with the generated rows
    html_content = html_content.replace("<!-- Add a hidden placeholder row -->", rows)

    # Call the function to remove the placeholder row from the generated HTML content
    updated_html_content = remove_placeholder_row(html_content, args)

    # Write the updated HTML content to the output HTML file
    with open(default_output_html_file, 'w') as output_file:
        output_file.write(updated_html_content)

    logger_info.info("Finished generating and writing web page.")

# -------------------------------------------------------------------------
def remove_placeholder_row(html_content: str, args) -> str:
    """
    Removes the placeholder row from the provided HTML content.

    This function identifies a placeholder row within the HTML content using a specific 
    pattern, removes it, and returns the updated content.

    Args:
    - html_content (str): The HTML content containing the placeholder row.
    - args (object): An argument object with a 'verbose' attribute determining the verbosity.

    Returns:
    - str: The updated HTML content without the placeholder row.

    Notes:
    - Logs the process of removing the placeholder row to the debug log file.
    - Outputs to the console when 'args.verbose' is set to True.
    """

    entry_msg = "Starting the removal of the placeholder row."
    logger_info.info(entry_msg)
    if args.verbose:
        print(entry_msg)

    try:
        # Define the regex pattern for the placeholder row
        placeholder_row_pattern = (r"<tr>\s*<td>{{ row\[\"Service Name\"\] }}</td>\s*<td>{{ "
                                   "row\[\"External Port\"\] }}</td>\s*<td>{{ row\[\"Internal Port\"\] }}</td>"
                                   "\s*<td>{{ row\[\"Port Mapping\"\] }}</td>\s*<td>{{ row\[\"Mapped App\"\] }}</td>\s*</tr>")
        
        # Remove the placeholder row from the HTML content
        updated_content = re.sub(placeholder_row_pattern, "", html_content)

        success_msg = "Successfully removed the placeholder row."
        logger_info.info(success_msg)
        if args.verbose:
            print(success_msg)

        return updated_content

    except Exception as e:
        error_msg = f"Error during placeholder row removal: {e}"
        logger_info.error(error_msg)
        if args.verbose:
            print(error_msg)

        return html_content  # Return the original content in case of an error

# -------------------------------------------------------------------------
def generate_output_json(args) -> None:
    """
    Generate a JSON file containing location-based weather details.

    The function retrieves the current location of the user based on their IP address.
    It then fetches weather details for the identified location and saves the information
    to a JSON file. If the cache is valid, cached data is used. Otherwise, new data is fetched
    and cached.

    Args:
    - args (object): An argument object with a 'verbose' attribute for controlling verbosity.

    Notes:
    - Handles logging of various events and outputs to the console based on verbosity.
    """
    
    entry_msg = "Starting: generate_output_json"
    logger_info.info(entry_msg)
    if args.verbose:
        print(entry_msg)
    
    try:
        # Load cached data
        logger_debug.debug("Loading cached data...")
        cached_data = load_cached_data(args)

        if is_cache_valid(cached_data, args):
            location_data = cached_data
            logger_info.info("Using valid cached data.")
        else:
            location_response = requests.get('https://ipinfo.io/json')
            location_data = location_response.json()
            logger_info.info("Fetched new location data.")
            
            # Cache the fetched data
            location_data["timestamp"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_cached_data(location_data, args)

        # Extract latitude and longitude
        latitude, longitude = location_data['loc'].split(',')
        logger_debug.debug(f"Latitude: {latitude}, Longitude: {longitude}")

        # Fetch weather information for the location
        weather_response = requests.get(f'https://wttr.in/{latitude},{longitude}?format=%t', timeout=5)
        temperature_F = weather_response.text.strip()
        temperature_C = get_temperature_in_celsius(temperature_F, args)  # Convert F to C

    except requests.exceptions.Timeout:
        logger_info.error("Timeout encountered while fetching weather data.")
        temperature_F, temperature_C = "N/A", "N/A"

    # Prepare the data for JSON output
    location = f"{location_data['city']}, {location_data['region']}, {location_data['country']}"
    versions = fetch_versions(args)
    last_updated = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    temperature_C_formatted = f"+{temperature_C}°C"
    perf_data = get_system_info(args)

    output_data = {
        'location': location,
        'temperature_F': temperature_F,
        'temperature_C': temperature_C_formatted,
        'last_updated': last_updated,
        'html_file_name': default_output_html_file,
        'background_color': dcpd_config.WEB_COLOR_MAP.get(dcpd_config.DEFAULT_WEB_PAGE_BACKGROUND_COLOR, dcpd_config.DEFAULT_WEB_PAGE_BACKGROUND_COLOR),
        'text_color': dcpd_config.WEB_COLOR_MAP.get(dcpd_config.DEFAULT_WEB_PAGE_TEXT_COLOR, dcpd_config.DEFAULT_WEB_PAGE_TEXT_COLOR),
        'current_version': versions.get("current-version", "N/A"),
        'latest_version': versions.get("latest-version", "N/A")
    }

    output_data.update(perf_data)
    logger_debug.debug(f"Prepared output data: {output_data}")

    # Save the data to a JSON file
    with open(output_json_file, 'w') as json_file:
        json.dump(output_data, json_file)
    
    exit_msg = "Completed: generate_output_json"
    logger_info.info(exit_msg)
    if args.verbose:
        print(exit_msg)

# -------------------------------------------------------------------------
def get_temperature_in_celsius(temperature_F: str, args) -> str:
    """
    Convert a given temperature from Fahrenheit to Celsius and format the result.

    Args:
        temperature_F (str): Temperature in Fahrenheit, expected in the format "XX.X°F".
        args (object): An argument object with a 'verbose' attribute for controlling verbosity.

    Returns:
        str: The temperature in Celsius, rounded to the nearest whole number, or "N/A" if conversion fails.
    """
    entry_msg = f"Converting temperature from Fahrenheit to Celsius: {temperature_F}"
    logger_info.info(entry_msg)
    if args.verbose:
        print(entry_msg)

    try:
        temperature_numerical = temperature_F.rstrip('°F')
        temperature_C = (float(temperature_numerical) - 32) * 5.0 / 9.0

        exit_msg = f"Converted temperature: {round(temperature_C)}°C"
        logger_info.info(exit_msg)
        if args.verbose:
            print(exit_msg)
        
        return f"{round(temperature_C)}"

    except ValueError as e:
        error_msg = f"Error converting temperature: {e}"
        logger_info.error(error_msg)
        if args.verbose:
            print(error_msg)
        return "N/A"

# -------------------------------------------------------------------------
def load_cached_data(args) -> dict:
    """
    Load cached data from a cache file.

    Attempts to load cached data from the cache file. If there's an issue reading the file
    or decoding the JSON, None is returned.

    Args:
        args (object): An argument object with a 'verbose' attribute for controlling verbosity.

    Returns:
        dict or None: Cached data if exists and is valid; otherwise, None.
    """
    entry_msg = "Loading cached data from cache file."
    logger_info.info(entry_msg)
    if args.verbose:
        print(entry_msg)
    
    try:
        with open(CACHE_FILE, "r") as cache_file:
            cached_data = json.load(cache_file)

            success_msg = "Cached data loaded successfully."
            logger_info.info(success_msg)
            if args.verbose:
                print(success_msg)
                print("Cached Data:", cached_data)  # Display cached data in verbose mode
            
            return cached_data

    except (FileNotFoundError, json.JSONDecodeError):
        error_msg = "Failed to load cached data from cache file."
        logger_info.warning(error_msg)
        if args.verbose:
            print(error_msg)
        return None

# -------------------------------------------------------------------------
def save_cached_data(data: dict, args) -> None:
    """
    Save data to a cache file in JSON format.

    Args:
        data (dict): The data to be cached.
        args (object): An argument object with a 'verbose' attribute for controlling verbosity.
    """
    entry_msg = "Saving data to cache file."
    logger_info.info(entry_msg)
    if args.verbose:
        print(entry_msg)
    
    try:
        with open(CACHE_FILE, "w") as cache_file:
            json.dump(data, cache_file)

        success_msg = "Data saved to cache file successfully."
        logger_info.info(success_msg)
        if args.verbose:
            print(success_msg)

    except Exception as e:
        error_msg = f"Error saving data to cache file: {e}"
        logger_info.error(error_msg)
        if args.verbose:
            print(error_msg)

# -------------------------------------------------------------------------
def is_cache_valid(cached_data: dict, args) -> bool:
    """
    Check if the cached data is still valid.

    Validates cached data by comparing its timestamp with the current time. If the data is within the valid cache duration,
    it returns True; otherwise, it returns False.

    Args:
        cached_data (dict or None): Cached data to be validated.
        args (object): An argument object with a 'verbose' attribute for controlling verbosity.

    Returns:
        bool: True if cached data is valid, False otherwise.
    """
    if cached_data is None:
        absence_msg = "Cached data is not available."
        logger_info.info(absence_msg)
        if args.verbose:
            print(absence_msg)
        return False

    try:
        cached_timestamp = datetime.datetime.strptime(cached_data.get("timestamp", ""), "%Y-%m-%d %H:%M:%S")
        current_time = datetime.datetime.now()
        cache_duration = current_time - cached_timestamp

        if cache_duration <= CACHE_DURATION:
            valid_msg = "Cached data is still valid."
            logger_info.info(valid_msg)
            if args.verbose:
                print(valid_msg)
            return True
        else:
            expired_msg = "Cached data has expired."
            logger_info.info(expired_msg)
            if args.verbose:
                print(expired_msg)
            return False

    except Exception as e:
        error_msg = f"Error checking cache validity: {e}"
        logger_info.error(error_msg)
        if args.verbose:
            print(error_msg)
        return False

# -------------------------------------------------------------------------
def fetch_versions(args) -> dict:
    """
    Fetch the current and latest software versions from the specified base URL.

    Tries to fetch version data for 'current-version' and 'latest-version' 
    endpoints. If an error occurs during the fetch, logs the error and sets 
    the version to "N/A" for that endpoint.

    Args:
        args (object): An argument object with a 'verbose' attribute for controlling verbosity.

    Returns:
        dict: Contains fetched 'current-version' and 'latest-version' or "N/A" if an error occurred.
    """
    
    base_url = "http://localhost:81/api/proxy/"
    endpoints = ["current-version", "latest-version"]
    version_data = {}

    for endpoint in endpoints:
        try:
            response = requests.get(base_url + endpoint)
            response_content = response.content.decode('utf-8')

            info_msg = f"Fetched {endpoint}: {response_content}"
            logger_info.info(info_msg)
            if args.verbose:
                print(info_msg)
            
            if response.status_code == 200:
                version_data[endpoint] = response.json().get("version", "N/A")
            else:
                error_msg = f"Error fetching {endpoint}. Response Code: {response.status_code}. Response: {response_content}"
                logger_info.error(error_msg)
                if args.verbose:
                    print(error_msg)
                
        except requests.RequestException as re:
            error_msg = f"RequestException fetching {endpoint}: {re}"
            logger_info.error(error_msg)
            if args.verbose:
                print(error_msg)
            version_data[endpoint] = "N/A"
            
        except Exception as e:
            error_msg = f"Exception fetching {endpoint}: {e}"
            logger_info.error(error_msg)
            if args.verbose:
                print(error_msg)
            version_data[endpoint] = "N/A"

    return version_data

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
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        system_info = {
            "cpu_percent": cpu_percent,
            "total_memory": memory_info.total,
            "used_memory": memory_info.used,
            "available_memory": memory_info.available,
            "memory_percent": memory_info.percent,
            "perf_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        logger_debug.debug(f"System Info: {system_info}")

        exit_msg = "Exiting get_system_info() function with data retrieved successfully..."
        logger_info.info(exit_msg)
        if args.verbose:
            print(f"System Information: {system_info}")
            print(exit_msg)

        return system_info

    except Exception as e:
        error_msg = f"Error fetching system info: {e}"
        logger_info.error(error_msg)
        if args.verbose:
            print(error_msg)

        exit_err_msg = "Exiting get_system_info() function due to an error..."
        logger_info.error(exit_err_msg)
        if args.verbose:
            print(exit_err_msg)

        return {}