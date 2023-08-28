#!/usr/bin/env python3

"""
dcpd_api.py - Docker Compose Ports Dump (DCPD) API

This script defines the REST API endpoints for the Docker Compose Ports Dump (DCPD) utility.
The API allows users to retrieve information about the utility's health, current version,
latest version from GitHub, and data from the SQLite database.

The API includes the following endpoints:
    - /api/system/health: Health check endpoint.
    - /api/system/current_version: Returns the current version of the DCPD utility.
    - /api/system/latest_version: Returns the latest version of the DCPD utility from GitHub.
    - /api/proxy/version/<endpoint>: Proxies requests to /api/system/current_version or /api/system/latest_version.
    - /api/proxy/database/<endpoint>/<table_name>: Proxies requests to fetch data from SQLite database tables.
    - /api/data/fetch_table/<table_name>: Fetches data from SQLite database tables.

The API is built using Flask and uses Flask-Caching for caching responses.
"""

import json
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
import sqlite3
import subprocess

from flask import Flask, jsonify, request
from flasgger import Swagger
from flask_caching import Cache
import requests

# Add config to the sys path
# pylint: disable=wrong-import-position
sys.path.append('../config')

# Third-party imports (if any)
import dcpd_config

# Create an alias for convenience
version = dcpd_config.VERSION
github_repo_url = dcpd_config.GITHUB_REPO_URL
api_key = dcpd_config.API_KEY
cache_type = dcpd_config.CACHE_TYPE
api_port = dcpd_config.API_PORT

dcpd_api = Flask(__name__)

# Setting up Flask logger to write to a specific file:
logger = logging.getLogger(__name__)

# Determine the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Construct a relative path for the log file
log_file_path = os.path.join(script_dir, '..', 'data', 'dcpd_flask.log')

# Create the RotatingFileHandler with the relative path
log_handler = RotatingFileHandler(log_file_path, maxBytes=100000, backupCount=5)

log_handler.setLevel(logging.INFO)
log_handler.setFormatter(logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"))
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

# -------------------------------------------------------------------------
@dcpd_api.before_request
def check_api_key():
    """
    API Key Checking Before Request

    This function is a before-request handler for the DCPD API endpoints. It checks the provided API key
    against the configured API key to ensure that requests are authorized.

    The function excludes API key checking for Swagger URLs, static assets, and /api/proxy paths.
    For all other paths, it checks the provided 'apikey' query parameter against the configured API key.
    If the API key is missing or invalid, a 403 Forbidden response is returned.

    Args:
        None

    Returns:
        None if API key is valid, otherwise returns a 403 Forbidden response with an error message.
    """
    # Exclude Swagger URLs and its static assets
    if (
        request.path.startswith('/flasgger_static/')
        or request.path in ['/apidocs/', '/apidocs/index.html', '/apispec_1.json']
        or request.path.startswith('/api/proxy/')
    ):
        return None  # Don't check API key for Swagger URLs, its assets, or /api/proxy paths

    # Check API key for all other paths
    provided_api_key = request.args.get('apikey')
    if not provided_api_key or provided_api_key != api_key:
        return jsonify(error="Invalid or missing API key"), 403

    return None  # Return None for the default case

# https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/
template = {
    "swagger": "2.0",
    "info": {
        "title": "dcpd API",
        "description": "dcpd API Documentation",
        "version": version
    },
    "basePath": "/",
    "securityDefinitions": {   # Add this block to define security schemes
        "ApiKey": {
            "type": "apiKey",
            "name": "apikey",
            "in": "query"
        }
    },
    "security": [    # Apply the security scheme globally
        {
            "ApiKey": []
        }
    ]
}

swagger = Swagger(dcpd_api, template=template)

# -------------------------------------------------------------------------
@dcpd_api.errorhandler(500)
def internal_server_error(exception):
    """
    Internal Server Error Handler

    This function is an error handler for the DCPD API endpoints. It is invoked when a 500 Internal Server Error occurs.
    The function logs the error message using the Flask logger at the 'error' level and returns a JSON response with a
    500 status code and an error message indicating the internal server error.

    Args:
        exception (Exception): The exception object representing the error.

    Returns:
        A JSON response with a 500 status code and an error message indicating the internal server error.
    """
    logger.error("Internal Server Error: %s", exception)
    return jsonify(error="Internal Server Error"), 500

# -------------------------------------------------------------------------
@dcpd_api.errorhandler(404)
def not_found_error(_):
    """
    Not Found Error Handler

    This function is an error handler for the DCPD API endpoints. It is invoked when a 404 Not Found error occurs.
    The function logs the request URL using the Flask logger at the 'warning' level and returns a JSON response with a
    404 status code and an error message indicating that the requested resource was not found.

    Args:
        exception (Exception): The exception object representing the error.

    Returns:
        A JSON response with a 404 status code and an error message indicating that the requested resource was not found.
    """
    logger.warning("Not Found: %s", request.url)

    return jsonify(error="Not Found"), 404

# -------------------------------------------------------------------------
@dcpd_api.route('/api/system/health', methods=['GET'])
def health_check():
    """
    Health Check Endpoint
    ---
    responses:
      200:
        description: Returns health status
    """
    try:
        logger.info('/api/system/health called')
        response = jsonify(status='Healthy', code=200)
        logger.info("Response: %s", response.get_json())  # Log the response data
        return response, 200
    except json.JSONDecodeError as exception:
        logger.exception("Error parsing JSON response: %s", exception)
        error_response = jsonify(error="Error parsing JSON response")
        logger.info("Error Response: %s", error_response.get_json())  # Log the error response data
        return error_response, 500
    except AttributeError as exception:
        logger.exception("Attribute error: %s", exception)
        error_response = jsonify(error="Attribute error")
        logger.info("Error Response: %s", error_response.get_json())  # Log the error response data
        return error_response, 500

# -------------------------------------------------------------------------
@dcpd_api.route('/api/system/current_version', methods=['GET'])
def get_current_version():
    """
    Current Version Endpoint
    ---
    responses:
      200:
        description: Returns version
    """
    try:
        logger.info('/api/system/current_version called')
        response = jsonify(version=version, code=200)
        logger.info("Response: %s", response.get_json())  # Log the response data

        return response, 200
    except ValueError as exception:
        logger.info("ValueError fetching current version: %s", exception)
        error_response = jsonify(error="Error fetching current version")
        logger.info("Error Response: %s", error_response.get_json())  # Log the error response data
        return error_response, 500
    except RuntimeError as exception:
        logger.info("RuntimeError fetching current version: %s", exception)
        error_response = jsonify(error="Error fetching current version")
        logger.info("Error Response: %s", error_response.get_json())  # Log the error response data
        return error_response, 500

# -------------------------------------------------------------------------
# Initialize Cache
dcpd_api.config['CACHE_TYPE'] = dcpd_config.CACHE_TYPE  # Use the value from dcpd_config
cache = Cache(dcpd_api)

# -------------------------------------------------------------------------
@dcpd_api.route('/api/system/latest-version', methods=['GET'])
@cache.cached(timeout=86400)  # Cache the result for 24 hours
def get_latest_version():
    """
    Latest Version Endpoint
    ---
    responses:
      200:
        description: Returns the latest GitHub version
      500:
        description: Error fetching the latest version from GitHub
    """
    try:
        logger.info('/api/system/latest_version')
        response = requests.get(github_repo_url, timeout=10)  # Add timeout argument
        response.raise_for_status()
        data = response.json()
        return jsonify(code=200, version=data["tag_name"]), 200
    except requests.ConnectionError as connection_error:
        logger.exception("Connection error while fetching the latest version from GitHub: %s", connection_error)
        return jsonify(error="Connection error while fetching the latest version from GitHub"), 500
    except requests.Timeout as timeout_error:
        logger.exception("Timeout error while fetching the latest version from GitHub: %s", timeout_error)
        return jsonify(error="Timeout error while fetching the latest version from GitHub"), 500
    except requests.RequestException as request_error:
        logger.exception("General request error while fetching the latest version from GitHub: %s", request_error)
        return jsonify(error="Request error while fetching the latest version from GitHub"), 500
    except KeyError as key_error:
        logger.exception("Key error, check the response structure: %s", key_error)
        return jsonify(error="Key error in the GitHub API response"), 500

# -------------------------------------------------------------------------
ALLOWED_VERSION_ENDPOINTS = ["current-version", "latest-version"]

@dcpd_api.route('/api/proxy/version/<endpoint>', methods=['GET'])
def proxy_version_endpoint(endpoint):
    """
    Version Proxy Endpoint
    ---
    parameters:
      - name: endpoint
        in: path
        type: string
        required: true
        enum: ["current-version", "latest-version"]
    responses:
      200:
        description: Proxy returns the data from the desired endpoint
    hidden: true
    """

    if endpoint not in ALLOWED_VERSION_ENDPOINTS:
        return jsonify(error="Invalid version endpoint"), 400

    try:
        if endpoint == "current-version":
            return get_current_version()
        if endpoint == "latest-version":
            return get_latest_version()
        error_msg = f"Endpoint {endpoint} not supported"
        logger.error(error_msg)
        return jsonify(error=error_msg), 400
    except (requests.ConnectionError, requests.Timeout, requests.RequestException, KeyError) as error:
        error_msg = f"Error proxying request for {endpoint}"
        logger.exception("%s: %s", error_msg, error)
        return jsonify(error=error_msg), 500

# -------------------------------------------------------------------------
ALLOWED_DATABASE_ENDPOINTS = ["fetch_table"]

@dcpd_api.route('/api/proxy/database/<endpoint>/<string:table_name>', methods=['GET'])
def proxy_database_endpoint(endpoint, table_name):
    """
    Database Proxy Endpoint
    ---
    parameters:
      - name: endpoint
        in: path
        type: string
        required: true
        enum: ["fetch_table"]
      - name: table_name
        in: path
        type: string
        required: true
        enum: ['container_ports', 'host_networking', 'port_mappings', 'service_info']
    responses:
      200:
        description: Proxy returns the data from the desired database table
      400:
        description: Invalid table name provided or unsupported database operation
    """

    if endpoint not in ALLOWED_DATABASE_ENDPOINTS:
        return jsonify(error="Unsupported database operation"), 400

    if table_name not in ALLOWED_TABLES:
        return jsonify(error="Invalid table name provided"), 400

    try:
        if endpoint == "fetch_table":
            return get_data_from_db(table_name)
        return jsonify(error=f"Endpoint {endpoint} not supported"), 400
    except sqlite3.Error as db_error:
        logger.exception("SQLite error while proxying request for %s: %s", endpoint, db_error)
        return jsonify(error=f"SQLite error while proxying request for {endpoint}"), 500
    except KeyError as key_error:
        logger.exception("Key error while proxying request for %s: %s", endpoint, key_error)
        return jsonify(error=f"Key error while proxying request for {endpoint}"), 500

# -------------------------------------------------------------------------
# Determine the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Construct a relative path for the database file
DATABASE_PATH = os.path.join(script_dir, '..', 'data', 'dcpd.db')

def query_db(query, args=(), one=False):
    """
    Execute a database query and fetch results.

    This function executes the specified database query using an SQLite connection to the database file.
    It fetches the results of the query and returns them as a list of tuples.

    Args:
        query (str): The SQL query to execute.
        args (tuple): Optional parameters to pass to the query (default: ()).
        one (bool): If True, fetch only one result; if False, fetch all results (default: False).

    Returns:
        list or tuple: The fetched results, either as a list of tuples or a single tuple, depending on 'one'.
    """
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute(query, args)
        result = cur.fetchall()
        return (result[0] if result else None) if one else result

# -------------------------------------------------------------------------
ALLOWED_TABLES = ['container_ports', 'host_networking', 'port_mappings', 'service_info']

@dcpd_api.route('/api/data/fetch_table/<string:table_name>', methods=['GET'])
def get_data_from_db(table_name):
    """
    Fetch Data from SQLite Endpoint
    ---
    parameters:
      - name: table_name
        in: path
        type: string
        required: true
        enum: ['container_ports', 'host_networking', 'port_mappings', 'service_info']
    responses:
      200:
        description: Returns data from the SQLite database
      400:
        description: Invalid table name provided
      500:
        description: Error fetching data from the SQLite database
    """
    if table_name not in ALLOWED_TABLES:
        return jsonify(error="Invalid table name provided"), 400

    try:
        query = f'SELECT * FROM {table_name}'
        data = query_db(query)
        return jsonify(data=data, code=200), 200
    except sqlite3.Error as db_error:
        logger.exception("SQLite error while fetching data from %s: %s", table_name, db_error)
        return jsonify(error=f"SQLite error while fetching data from {table_name}"), 500
    except KeyError as key_error:
        logger.exception("Key error while fetching data from %s: %s", table_name, key_error)
        return jsonify(error=f"Key error while fetching data from {table_name}"), 500

# -------------------------------------------------------------------------
api_spec_url = f'http://localhost:{api_port}/apispec_1.json'
output_api_spec = os.path.join("..", "src", "dcpd_api_spec.json")

def fetch_and_save_openapi_spec(url, output_file):
    """
    Fetch the OpenAPI specification and save it to a file.

    This function fetches the OpenAPI specification from the provided URL using a cURL command.
    The fetched JSON data is then pretty-printed using the 'jq' command, and the prettified JSON
    is saved to the specified output file.

    Args:
        url (str): The URL of the OpenAPI specification.
        output_file (str): The path to the file where the prettified JSON will be saved.

    Returns:
        None
    """
    # Run the curl command to fetch the OpenAPI spec
    curl_command = f'curl -s {url} 2>/dev/null'
    spec_json = subprocess.check_output(curl_command, shell=True, text=True)

    # Run the jq command to pretty-print the JSON
    jq_command = 'jq "."'
    pretty_spec = subprocess.check_output(jq_command, input=spec_json, shell=True, text=True)

    # Save the pretty-printed JSON to the output file
    with open(output_file, 'w', encoding='utf-8') as out_file:
        out_file.write(pretty_spec)

# -------------------------------------------------------------------------
if __name__ == '__main__':
    dcpd_api.run(host='0.0.0.0', port=api_port, debug=False)
