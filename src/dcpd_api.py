#!/usr/bin/env python3
# dcpd_api.py

from flask import Flask, jsonify, request
from flasgger import Swagger
from flask_caching import Cache
import sys
sys.path.append('/app/config')
import dcpd_config
import logging
from logging.handlers import RotatingFileHandler
import requests
import pprint

# Create an alias for convenience
version=dcpd_config.VERSION
github_repo_url=dcpd_config.GITHUB_REPO_URL
api_key=dcpd_config.API_KEY
cache_type=dcpd_config.CACHE_TYPE

dcpd_api = Flask(__name__)

# Setting up Flask logger to write to a specific file:
logger = logging.getLogger(__name__)
log_handler = RotatingFileHandler('/app/data/dcpd_flask.log', maxBytes=100000, backupCount=5)
log_handler.setLevel(logging.INFO)
log_handler.setFormatter(logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"))
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

# -------------------------------------------------------------------------
@dcpd_api.before_request
def check_api_key():
    # Exclude Swagger URLs and its static assets
    if (
        request.path.startswith('/flasgger_static/')
        or request.path in ['/apidocs/', '/apidocs/index.html', '/apispec_1.json']
        or request.path.startswith('/api/proxy/')
    ):
        return  # Don't check API key for Swagger URLs, its assets, or /api/proxy paths
    
    # Check API key for all other paths
    provided_api_key = request.args.get('apikey')
    if not provided_api_key or provided_api_key != api_key:
        return jsonify(error="Invalid or missing API key"), 403

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
def internal_server_error(e):
    logger.error(f"Internal Server Error: {e}")
    return jsonify(error="Internal Server Error"), 500

# -------------------------------------------------------------------------
@dcpd_api.errorhandler(404)
def not_found_error(e):
    logger.warning(f"Not Found: {request.url}")
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
        logger.info(f"Response: {response.get_json()}")  # Log the response data
        return response, 200
    except Exception as e:
        logger.exception(f"Error fetching health: {e}")
        error_response = jsonify(error="Error fetching health")
        logger.info(f"Error Response: {error_response.get_json()}")  # Log the error response data
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
        logger.info(f"Response: {response.get_json()}")  # Log the response data
        return response, 200
    except Exception as e:
        logger.info(f"Error fetching current version: {e}")
        error_response = jsonify(error="Error fetching current version")
        logger.info(f"Error Response: {error_response.get_json()}")  # Log the error response data
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
        response = requests.get(github_repo_url)  # Use the URL from dcpd_config
        logger.info(f"GitHub Response: {response.text}")
        response.raise_for_status()
        data = response.json()
        return jsonify(code=200, version=data["tag_name"]), 200
    except requests.ConnectionError:
        logger.exception("Connection error while fetching the latest version from GitHub")
        return jsonify(error="Connection error while fetching the latest version from GitHub"), 500
    except requests.Timeout:
        logger.exception("Timeout error while fetching the latest version from GitHub")
        return jsonify(error="Timeout error while fetching the latest version from GitHub"), 500
    except requests.RequestException:
        logger.exception("General request error while fetching the latest version from GitHub")
        return jsonify(error="Request error while fetching the latest version from GitHub"), 500
    except KeyError:
        logger.exception("Key error, check the response structure")
        return jsonify(error="Key error in the GitHub API response"), 500
    except Exception as e:
        logger.exception("Error fetching latest version from GitHub")
        return jsonify(error="Error fetching latest version from GitHub"), 500

# -------------------------------------------------------------------------
ALLOWED_ENDPOINTS = ["current-version", "latest-version"]

@dcpd_api.route('/api/proxy/<endpoint>', methods=['GET'])
def proxy_endpoint(endpoint):
    """
    Generic Proxy Endpoint
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
    
    # Ensure we only proxy to allowed endpoints to avoid potential misuse
    if endpoint not in ALLOWED_ENDPOINTS:
        return jsonify(error="Invalid endpoint"), 400

    try:
        if endpoint == "current-version":
            return get_current_version()
        elif endpoint == "latest-version":
            return get_latest_version()
        else:
            return jsonify(error=f"Endpoint {endpoint} not supported"), 400
    except Exception:
        return jsonify(error=f"Error proxying request for {endpoint}"), 500

# -------------------------------------------------------------------------
if __name__ == '__main__':
    logger.info('Starting Flask app')
    dcpd_api.run(debug=True)