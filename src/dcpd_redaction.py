# dcpd_redaction.py
import json
import re
import dcpd_config
import dcpd_log_info
import dcpd_log_debug
import zipfile
import shutil
import os
import pyzipper

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
        # Open the original JSON file in read mode
        with open('../data/dcpd_html.json', 'r') as file:
            # Parse the JSON data
            data = json.load(file)
            
            # Replace the 'location' field's value with '[REDACTED]'
            data['location'] = '[REDACTED]'  

        # Open a new JSON file in write mode to save the redacted content
        with open('../data/redacted_dcpd_html.json', 'w') as outfile:
            # Save the redacted data with an indentation of 4 spaces for better readability
            json.dump(data, outfile, indent=4)

        # Logging the successful redaction and, if verbosity is enabled, 
        # notifying the user of the completion.
        logger_info.info("Successfully redacted location information from dcpd_html.json")
        if args.verbose:
            print("Redaction of location information from dcpd_html.json completed.")
    
    # Handle any exceptions that might arise during the file reading, 
    # JSON parsing, or file writing processes
    except Exception as e:
        # Log an error indicating the failure of the redaction process
        logger_info.error(f"Failed to redact location information from dcpd_html.json: {e}")
        
        # Log a detailed traceback of the exception for debugging purposes
        logger_debug.exception("Redaction error for dcpd_html.json with detailed traceback")
        
        # If verbosity is enabled, inform the user about the error that was encountered
        if args.verbose:
            print(f"Error encountered during redaction of location information from dcpd_html.json: {e}")

    # Logging the conclusion of the function and, if verbosity is enabled, 
    # notifying the user of the end of the redaction process.
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
        # Open the original JSON file in read mode
        with open('../data/dcpd_cache_location.json', 'r') as file:
            # Parse the JSON data
            data = json.load(file)
            
            # Redact the IP address using a regular expression
            data['ip'] = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[REDACTED]', data['ip'])
            
            # List of fields considered as sensitive and to be redacted
            sensitive_fields = ['hostname', 'city', 'region', 'country', 'loc', 'org', 'postal', 'timezone']
            
            # Iterating over each sensitive field and replacing its content with '[REDACTED]'
            for field in sensitive_fields:
                data[field] = '[REDACTED]'

        # Open a new JSON file in write mode to save the redacted content
        with open('../data/redacted_dcpd_cache_location.json', 'w') as outfile:
            # Save the redacted data with an indentation of 4 spaces for better readability
            json.dump(data, outfile, indent=4)

        # Logging the successful redaction of data. If verbosity is enabled, 
        # a print statement notifies the user of the completion.
        logger_info.info("Successfully redacted sensitive data from dcpd_cache_location.json")
        if args.verbose:
            print("Sensitive data redaction from dcpd_cache_location.json completed.")
    
    # Handle any exceptions that might arise during the file reading, 
    # JSON parsing, or file writing processes
    except Exception as e:
        # Log an error indicating the failure of the redaction process
        logger_info.error(f"Failed to redact sensitive data from dcpd_cache_location.json: {e}")
        
        # Log a detailed traceback of the exception for debugging purposes
        logger_debug.exception("Redaction error for dcpd_cache_location.json with detailed traceback")
        
        # If verbosity is enabled, inform the user about the error that was encountered
        if args.verbose:
            print(f"Error encountered during sensitive data redaction from dcpd_cache_location.json: {e}")

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
    
    # Logging the initiation of the function. If verbosity is enabled through `args`, 
    # a print statement notifies the user of the redaction's start.
    logger_info.info("Entered redact_username_from_debug_file()")
    if args.verbose:
        print("Starting username redaction from dcpd_debug.txt...")
    
    try:
        # Open the original debug file in read mode to access its content
        with open('../data/dcpd_debug.txt', 'r') as file:
            content = file.read()

            # Use regular expressions (regex) to identify and redact paths that potentially expose usernames. 
            # The first regex identifies typical Linux home directory paths and replaces the username segment with '[REDACTED]'.
            # The second regex further ensures paths specific to this application's structure are redacted.
            redacted_content = re.sub(r'(/home/)([^/]+)', r'\1[REDACTED]', content)
            redacted_content = re.sub(r'(/home/[^/]+/Documents/Docker/)[^/]+', r'\1[REDACTED]', redacted_content)

        # Open a new file in write mode to save the redacted content.
        with open('../data/redacted_dcpd_debug.txt', 'w') as file:
            file.write(redacted_content)

        # Log the successful redaction of data. If verbosity is enabled, 
        # a print statement notifies the user of the completion.
        logger_info.info("Successfully redacted dcpd_debug.txt")
        if args.verbose:
            print("Username redaction from dcpd_debug.txt completed.")
    
    # Handle any exceptions that might arise during the file reading, regex processing, or file writing processes.
    except Exception as e:
        # Log an error indicating the failure of the redaction process.
        logger_info.error(f"Failed to redact usernames from dcpd_debug.txt: {e}")
        
        # Log a detailed traceback of the exception for debugging purposes.
        logger_debug.exception("Redaction error for dcpd_debug.txt with detailed traceback")
        
        # If verbosity is enabled, inform the user about the error that was encountered.
        if args.verbose:
            print(f"Error encountered during username redaction from dcpd_debug.txt: {e}")

    # Logging the conclusion of the function. If verbosity is enabled, 
    # a print statement notifies the user of the end of the redaction process.
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
    
    # Logging the initiation of the function. If verbosity is enabled through `args`, 
    # a print statement notifies the user of the compression's start.
    logger_info.info("Entered create_compressed_files()")
    if args.verbose:
        print("Starting compression of redacted files...")
    
    # This is the list of files that will be compressed and added to the encrypted `.zip` file.
    redacted_files = [
        '../data/redacted_dcpd_cache_location.json',
        '../data/dcpd.csv',
        '../data/redacted_dcpd_debug.txt',
        '../data/dcpd_host_networking.csv',
        '../data/redacted_dcpd_html.json',
        '../data/dcpd_stats.txt'
    ]
    
    try:
        # Start creating an encrypted `.zip` file using the `pyzipper` library.
        # Compression is done using the `ZIP_DEFLATED` method, and encryption is AES-based.
        with pyzipper.AESZipFile('../data/redacted_dcpd_files.zip', 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zipf:
            
            # Set the password for the `.zip` file.
            zipf.setpassword(redacted_zip_file_password.encode('utf-8'))
            
            # Iterate over the list of files and add them to the encrypted `.zip` archive.
            for file in redacted_files:
                file_name = os.path.basename(file)  # Extract the filename from the path
                zipf.write(file, file_name)
                
                # If verbosity is enabled, notify the user which file has been added to the archive.
                if args.verbose:
                    print(f"Added {file_name} to compressed file.")
        
        # Logging the successful compression and encryption of the files.
        logger_info.info("Successfully compressed and password protected redacted files using AES encryption.")
        if args.verbose:
            print("Compression and encryption of redacted files successful.")
        
    # Handle any exceptions that might arise during the compression or encryption processes.
    except Exception as e:
        # Log an error message about the failure.
        logger_info.error(f"Error during file compression: {e}")
        
        # Provide a detailed traceback for debugging purposes.
        logger_debug.exception("File compression error with detailed traceback")
        
        # If verbosity is enabled, inform the user about the encountered error.
        if args.verbose:
            print(f"Error encountered during compression: {e}")

    # Log the conclusion of the function. If verbosity is enabled, 
    # a print statement notifies the user of the end of the compression process.
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
    
    # Logging the start of the function. If verbosity is enabled using `args`, 
    # a message is printed to inform the user about the start of the redaction process.
    logger_info.info("Entered execute_redaction()")
    if args.verbose:
        print("Starting the redaction process...")
    
    try:
        # Begin the redaction of the `dcpd_html.json` file's location.
        redact_dcpd_html_location(args)
        if args.verbose:
            print("Redaction for dcpd_html_location completed.")
        
        # Redact sensitive information from the `dcpd_cache_location.json` file.
        redact_dcpd_cache_location(args)
        if args.verbose:
            print("Redaction for dcpd_cache_location completed.")
        
        # Redact usernames from paths in the `dcpd_debug.txt` file.
        redact_username_from_debug_file(args)
        if args.verbose:
            print("Username redaction from debug file completed.")
        
        # Compress the redacted files and protect them with encryption.
        create_compressed_files(args)
        if args.verbose:
            print("Compression of redacted files completed.")
        
        # Log the successful completion of the entire redaction process.
        logger_info.info("Redaction process completed successfully.")
        if args.verbose:
            print("Redaction process successfully completed.")
    
    # Handle any exceptions that might occur during the redaction, logging, or compression.
    except Exception as e:
        # Log an error message about the overall redaction process's failure.
        logger_info.error(f"Overall redaction process encountered an error: {e}")
        
        # Provide a detailed traceback for debugging purposes.
        logger_debug.exception("Redaction process error with detailed traceback")
        
        # If verbosity is enabled, notify the user about the encountered error.
        if args.verbose:
            print(f"Error encountered during redaction process: {e}")

    # Log the function's conclusion. If verbosity is enabled, a message notifies the user of the redaction's end.
    logger_info.info("Exiting execute_redaction()")
    if args.verbose:
        print("Redaction process ended.")
