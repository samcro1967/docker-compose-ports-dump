"""
dcpd_redaction.py

A script designed to perform data redaction on various data files related to the DCPD (Data Collection and Processing Daemon) system.

Features:
- Redacts location information from dcpd_html.json file, replacing it with '[REDACTED]' and saving the redacted content into a new file named redacted_dcpd_html.json.
- Redacts sensitive data fields such as IP address, hostname, city, region, and more from the dcpd_cache_location.json file.
The redacted data is saved into a new file named redacted_dcpd_cache_location.json.
- Redacts potential username exposures from paths in dcpd_debug.txt, ensuring data privacy. The redacted content is saved into a new file named redacted_dcpd_debug.txt.
- Compresses and encrypts the redacted files into a .zip archive with AES encryption using the provided password from the configuration.

Dependencies:
- json: For parsing and editing JSON files.
- re: For regular expression operations to redact data.
- os: For OS-level operations such as checking file existence.
- pyzipper: For compressing and encrypting files.
- dcpd_config: Configuration for DCPD related operations.
- dcpd_log_info and dcpd_log_debug: Logging modules specific to DCPD operations for information and debug levels respectively.

Note:
- Ensure the provided paths in the script are valid and accessible.
- The script relies on the presence of certain files and directories, make sure they exist before executing.
- Ensure the pyzipper library is installed and the encryption password is correctly set in dcpd_config.
"""

import json
import re
import os

import pyzipper

import dcpd_config
import dcpd_log_info
import dcpd_log_debug


# Create an alias for convenience
logger_info = dcpd_log_info.logger
logger_debug = dcpd_log_debug.logger

redacted_zip_file_password=dcpd_config.REDACTED_ZIP_FILE_PASSWORD

# -------------------------------------------------------------------------
def redact_dcpd_html_location(args):
    """
    Redact location information from the dcpd_html.json file.

    The 'location' field in the dcpd_html.json file will be replaced with '[REDACTED]'.
    The redacted content is saved to a new file named: redacted_dcpd_html.json.

    Args:
    None

    Returns:
    None
    """

    # Logging the initiation of the function and, if verbosity is enabled,
    # notifying the user of the start of the redaction process.
    logger_info.info("Entered redact_dcpd_html_location()")
    if args.verbose:
        print("Starting redaction of location information from dcpd_html.json...")

    try:
        with open('../data/dcpd_html.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            data['location'] = '[REDACTED]'
        with open('../data/redacted_dcpd_html.json', 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, indent=4)

        logger_info.info("Successfully redacted location information from dcpd_html.json")
        if args.verbose:
            print("Redaction of location information from dcpd_html.json completed.")

    except (FileNotFoundError, PermissionError, IOError) as file_error:
        logger_info.error("File operation error during redaction: %s", file_error)
        logger_debug.exception("File operation error during redaction with detailed traceback")
        if args.verbose:
            print(f"File operation error during redaction: {file_error}")

    except json.JSONDecodeError as json_error:
        logger_info.error("JSON parsing error during redaction: %s", json_error)
        logger_debug.exception("JSON parsing error with detailed traceback")
        if args.verbose:
            print(f"JSON parsing error during redaction: {json_error}")

    # Logging the conclusion of the function and, if verbosity is enabled,
    logger_info.info("Exiting redact_dcpd_html_location()")
    if args.verbose:
        print("Redaction process of location information from dcpd_html.json ended.")

# -------------------------------------------------------------------------
def redact_dcpd_cache_location(args):
    """
    Redact sensitive information from the dcpd_cache_location.json file.

    The redacted fields include IP address, hostname, city, region, country,
    location coordinates, organization, postal code, and timezone.

    The redacted content is saved to a new file named: redacted_dcpd_cache_location.json.

    Args:
    None

    Returns:
    None
    """

    # Logging the initiation of the function. If verbosity is enabled,
    # a print statement notifies the user of the start of the redaction process.
    logger_info.info("Entered redact_dcpd_cache_location()")
    if args.verbose:
        print("Starting sensitive data redaction from dcpd_cache_location.json...")

    try:
        with open('../data/dcpd_cache_location.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            data['ip'] = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[REDACTED]', data['ip'])
            sensitive_fields = ['hostname', 'city', 'region', 'country', 'loc', 'org', 'postal', 'timezone']
            for field in sensitive_fields:
                data[field] = '[REDACTED]'
        with open('../data/redacted_dcpd_cache_location.json', 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, indent=4)

        logger_info.info("Successfully redacted sensitive data from dcpd_cache_location.json")
        if args.verbose:
            print("Sensitive data redaction from dcpd_cache_location.json completed.")

    except (FileNotFoundError, PermissionError, IOError) as file_error:
        logger_info.error("File operation error during redaction: %s", file_error)
        logger_debug.exception("File operation error during redaction with detailed traceback")
        if args.verbose:
            print(f"File operation error during redaction: {file_error}")

    except json.JSONDecodeError as json_error:
        logger_info.error("JSON parsing error during redaction: %s", json_error)
        logger_debug.exception("JSON parsing error with detailed traceback")
        if args.verbose:
            print(f"JSON parsing error during redaction: {json_error}")

    except re.error as regex_error:
        logger_info.error("Regex substitution error during redaction: %s", regex_error)
        logger_debug.exception("Regex substitution error with detailed traceback")
        if args.verbose:
            print(f"Regex substitution error during redaction: {regex_error}")

    # Logging the conclusion of the function. If verbosity is enabled,
    # a print statement notifies the user of the end of the redaction process.
    logger_info.info("Exiting redact_dcpd_cache_location()")
    if args.verbose:
        print("Sensitive data redaction process from dcpd_cache_location.json ended.")

# -------------------------------------------------------------------------
def redact_username_from_debug_file(args):
    """
    Redact the username from paths in the dcpd_debug.txt file.

    Paths that potentially expose usernames (such as Linux home directory paths) are redacted.
    The redacted content is written to a new file named redacted_dcpd_debug.txt.

    Args:
    None

    Returns:
    None
    """

    # Logging the initiation of the function.
    logger_info.info("Entered redact_username_from_debug_file()")
    if args.verbose:
        print("Starting username redaction from dcpd_debug.txt...")

    try:
        with open('../data/dcpd_debug.txt', 'r', encoding='utf-8') as file:
            content = file.read()

            redacted_content = re.sub(r'(/home/)([^/]+)', r'\1[REDACTED]', content)
            redacted_content = re.sub(r'(/home/[^/]+/Documents/Docker/)[^/]+', r'\1[REDACTED]', redacted_content)

        with open('../data/redacted_dcpd_debug.txt', 'w', encoding='utf-8') as file:
            file.write(redacted_content)

        logger_info.info("Successfully redacted dcpd_debug.txt")
        if args.verbose:
            print("Username redaction from dcpd_debug.txt completed.")

    except (FileNotFoundError, PermissionError, IOError) as file_error:
        logger_info.error("File operation error during redaction: %s", file_error)
        logger_debug.exception("File operation error during redaction with detailed traceback")
        if args.verbose:
            print(f"File operation error during redaction: {file_error}")

    except re.error as regex_error:
        logger_info.error("Regex substitution error during redaction: %s", regex_error)
        logger_debug.exception("Regex substitution error with detailed traceback")
        if args.verbose:
            print(f"Regex substitution error during redaction: {regex_error}")

    logger_info.info("Exiting redact_username_from_debug_file()")
    if args.verbose:
        print("Username redaction process from dcpd_debug.txt ended.")


# -------------------------------------------------------------------------
def create_compressed_files(args):
    """
    Create a .zip file of the redacted files and password protect it using AES encryption.

    This function compresses redacted files and protects them with AES encryption.
    It will log the entry and exit of the function and any errors encountered during compression.
    If the verbose argument is provided, it will also print relevant information to the console.
    """

    # Logging the initiation of the function.
    logger_info.info("Entered create_compressed_files()")
    if args.verbose:
        print("Starting compression of redacted files...")

    # List of files to be compressed
    redacted_files = [
        '../data/dcpd.csv',
        '../data/dcpd.db',
        '../data/dcpd_bootstrap.log',
        '../data/dcpd_caddy.log',
        '../data/dcpd_cron.log',
        '../data/dcpd_debug.txt',
        '../data/dcpd_docker_inspect.csv',
        '../data/dcpd_docker_ps.csv',
        '../data/dcpd_docker_stats.txt',
        '../data/dcpd_flask.log',
        '../data/dcpd_gunicorn.log',
        '../data/dcpd_gunicorn_access.log',
        '../data/dcpd_gunicorn_error.log',
        '../data/dcpd_host_networking.csv',
        '../data/dcpd_stats.txt',
        '../data/redacted_dcpd_debug.txt',
        '../data/redacted_dcpd_cache_location.json',
        '../data/redacted_dcpd_html.json'
    ]

    try:
        with pyzipper.AESZipFile('../data/redacted_dcpd_files.zip', 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zipf:
            zipf.setpassword(redacted_zip_file_password.encode('utf-8'))

            for file in redacted_files:
                if os.path.exists(file):
                    file_name = os.path.basename(file)
                    zipf.write(file, file_name)
                    if args.verbose:
                        print(f"Added {file_name} to compressed file.")
                else:
                    logger_info.warning("File %s not found. Skipping.", file)
                    if args.verbose:
                        print(f"Warning: File {file} not found. Skipping.")

        logger_info.info("Successfully compressed and password protected redacted files using AES encryption.")
        if args.verbose:
            print("Compression and encryption of redacted files successful.")

    except (FileNotFoundError, PermissionError, IOError) as file_error:
        logger_info.error("File operation error during compression: %s", file_error)
        logger_debug.exception("File operation error during compression with detailed traceback")
        if args.verbose:
            print(f"File operation error during compression: {file_error}")

    except pyzipper.zipfile.BadZipFile as zip_error:
        logger_info.error("Error with zip operation: %s", zip_error)
        logger_debug.exception("Zip operation error with detailed traceback")
        if args.verbose:
            print(f"Zip operation error: {zip_error}")

    logger_info.info("Exiting create_compressed_files()")
    if args.verbose:
        print("Exiting compression of redacted files.")

# -------------------------------------------------------------------------
def execute_redaction(args):
    """
    Execute the redaction process for all relevant files.

    This function will initiate the redaction for various files, log the entry and exit of the function,
    and any errors encountered during the redaction. If the verbose argument is provided, it will also
    print relevant information to the console.
    """

    # Logging the start of the function.
    logger_info.info("Entered execute_redaction()")
    if args.verbose:
        print("Starting the redaction process...")

    try:
        redact_dcpd_html_location(args)
        if args.verbose:
            print("Redaction for dcpd_html_location completed.")

        redact_dcpd_cache_location(args)
        if args.verbose:
            print("Redaction for dcpd_cache_location completed.")

        redact_username_from_debug_file(args)
        if args.verbose:
            print("Username redaction from debug file completed.")

        create_compressed_files(args)
        if args.verbose:
            print("Compression of redacted files completed.")

        logger_info.info("Redaction process completed successfully.")
        if args.verbose:
            print("Redaction process successfully completed.")

    except (FileNotFoundError, PermissionError, IOError, json.JSONDecodeError, re.error) as specific_error:
        # Handle specific errors raised by the functions
        logger_info.error("Specific error during redaction process: %s", specific_error)
        logger_debug.exception("Specific error with detailed traceback")
        if args.verbose:
            print(f"Specific error during redaction process: {specific_error}")

    except pyzipper.zipfile.BadZipFile as zip_error:
        # Handle error specific to zip operation
        logger_info.error("Zip operation error: %s", zip_error)
        logger_debug.exception("Zip operation error with detailed traceback")
        if args.verbose:
            print(f"Zip operation error: {zip_error}")

    logger_info.info("Exiting execute_redaction()")
    if args.verbose:
        print("Redaction process ended.")
