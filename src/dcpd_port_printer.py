# dcpd_port_printer.py

import sys

# Add config to the sys path
sys.path.append('../config')

import dcpd_config as dcpd_config
import dcpd_log_debug as dcpd_log_debug
import dcpd_log_info as dcpd_log_info
import dcpd_utils as dcpd_utils
import os
from tabulate import tabulate
from typing import Any, List, Tuple, Optional

# Get the number of lines per page from the configuration
lines_per_page = dcpd_config.LINES_PER_PAGE

# Create an alias for convenience
logger_info = dcpd_log_info.logger
logger_debug = dcpd_log_debug.logger

# -------------------------------------------------------------------------
def format_all_ports(cursor: Any, sort_by: Optional[str] = None, args: Optional[object] = None):
    """
    Formats and displays all ports data in a tabulated form.
    
    Fetches service port data from the database, then formats and displays it 
    in a clear, tabulated format. The data can be sorted based on the provided criterion.

    Args:
        cursor (Any): Database cursor object for fetching data.
        sort_by (str, optional): Sorting criteria. 
            "-e" for sorting by external port, 
            "-n" for sorting by service name. 
            Defaults to None.
        args (object, optional): Additional argument object, if needed.

    Raises:
        RuntimeError: If there's any error while formatting and displaying ports.
    """
    
    # Log entry into the function
    logger_info.info("Entering format_all_ports function.")
    if sort_by:
        logger_debug.debug(f"Data will be sorted by: {sort_by}")

    try:
        # Fetch all relevant data from the database's service_info table
        data = fetch_all_data_from_db(cursor, args)

        # Sort the data if a sort criterion is provided
        if sort_by:
            data = sort_data(data, sort_by, args)

        # Prepare the fetched data for display
        headers, table_rows = prepare_data_for_display(data)

        # Use the tabulate library to present the data as a formatted table
        table_str = tabulate(table_rows, headers=headers, tablefmt="grid", numalign="center", stralign="center")

        # If the data is long, paginate the output for better readability
        dcpd_utils.paginate_output(table_str)

    except Exception as e:
        error_msg = f"Error while formatting and displaying ports: {str(e)}"
        logger_debug.exception(error_msg)
        logger_info.error(error_msg)
        # Raise a runtime error to inform the caller about the issue
        raise RuntimeError(error_msg) from e

    # Logging upon successfully displaying the table
    logger_info.info("Successfully completed format_all_ports function.")

# -------------------------------------------------------------------------
def prepare_data_for_display(data: List[Tuple[Any]]) -> Tuple[List[str], List[List[Any]]]:
    """
    Prepares and processes database data for tabulated display.

    This function processes the fetched data from the database, making adjustments 
    such as handling NULL values for ports and converting port mappings to human-readable 
    strings. The result is structured into headers and rows suitable for table display.

    Args:
        data (List[Tuple[Any]]): List of tuples containing database data to be processed.

    Returns:
        Tuple[List[str], List[List[Any]]]: A tuple of headers and table rows for display.
    """
    
    # Define the column headers for the table
    headers = ["Service Name", "External Port", "Internal Port", "Port Mapping", "Mapped App"]
    
    table_rows = []

    # Iterate over each row of the fetched data to process it
    for service_name, external_port, internal_port, port_mapping, mapped_app in data:
        
        # Handle NULL values for external and internal ports by replacing them with "N/A"
        external_port = external_port if external_port is not None else "N/A"
        internal_port = internal_port if internal_port is not None else "N/A"

        # Convert binary port_mapping data into a human-readable format
        if port_mapping == 1:
            port_mapping_str = "True"
        elif port_mapping == 0:
            port_mapping_str = "False"
        else:
            port_mapping_str = "N/A"  # Handle unexpected values

        # Construct and append the processed row to the table rows list
        table_rows.append([service_name, external_port, internal_port, port_mapping_str, mapped_app])

    return headers, table_rows

# -------------------------------------------------------------------------
def fetch_all_data_from_db(cursor: Any, args) -> List[Tuple[str, int, int, int, str]]:
    """
    Fetch all data from the service_info table in the database.
    
    Args:
        cursor (Any): Database cursor object.
    
    Returns:
        List[Tuple[str, int, int, int, str]]: A list of tuples representing the fetched data.
    """
    
    # Start logging the initiation of the data fetching process
    logger_info.info("Initiating data fetch from the service_info table in the database.") 

    try:
        # Execute SQL query to fetch data from the database table
        cursor.execute("SELECT service_name, external_port, internal_port, has_port_mapping, mapped_app FROM service_info")
        
        # Fetch all data returned by the executed query
        fetched_data = cursor.fetchall()
        
        # Log the number of rows fetched for monitoring purposes
        logger_info.info(f"Successfully fetched {len(fetched_data)} rows from the service_info table.")
        
        # Return the fetched data to the caller
        return fetched_data
        
    except Exception as e:
        # Log detailed information if an error occurs during data fetching
        logger_debug.exception("Error encountered during data fetch.")
        
        # Log the error message for higher-level monitoring
        logger_info.error(f"Failed to fetch data from the database: {str(e)}")
        
        # Propagate the error to the caller for further handling or termination
        raise e

# -------------------------------------------------------------------------
def sort_data(data: List[Tuple[str, int, int, int, str]], args, sort_by=None) -> List[Tuple[str, int, int, int, str]]:
    """
    Sorts the provided data based on the specified criteria or uses default sorting.
    
    Args:
        data (List[Tuple[str, int, int, int, str]]): Data to be sorted.
        sort_by (str, optional): Sorting criteria. "-e" for external port, "-n" for service name. Defaults to None.
    
    Returns:
        List[Tuple[str, int, int, int, str]]: The sorted data.
    """
    
    # Log the initiation of the data sorting process
    logger_info.info("Initiating data sorting process.")
    
    # If a sorting criteria is provided, log which criteria will be used
    if sort_by:
        logger_debug.debug(f"Data will be sorted based on the criteria: {sort_by}")

    try:
        # If the sort_by criteria is "-e", sort the data based on the external port.
        # The lambda function used for sorting ensures that rows with None values for the port will appear first.
        if sort_by == "-e":
            sorted_data = sorted(data, key=lambda x: (x[1] is None, int(x[1]) if x[1] is not None else 0))
        
        # If the sort_by criteria is "-n", sort the data based on the service name.
        # Rows with None values for the service name will appear first.
        elif sort_by == "-n":
            sorted_data = sorted(data, key=lambda x: (x[0] is None, x[0]))
        
        # If no sorting criteria is provided, return the data as is without sorting.
        else:
            sorted_data = data
        
        # Log that the sorting process was completed successfully
        logger_info.info("Data sorting completed successfully.")
        
        # Return the sorted data to the caller
        return sorted_data
    
    except Exception as e:
        # If any errors occur during sorting, log detailed information about the error
        logger_debug.exception("Error encountered during data sorting.")
        
        # Log the error message for higher-level monitoring
        logger_info.error(f"Failed to sort data: {str(e)}")
        
        # Propagate the error to the caller for further handling or termination
        raise e

# -------------------------------------------------------------------------
def get_terminal_cols(args) -> int:
    """
    Retrieve the number of terminal columns, defaulting to 80 if detection fails.
    
    Returns:
        int: The number of terminal columns.
    """
    
    # Log the intent to determine the terminal's column count
    logger_info.info("Trying to determine the terminal column count.")

    try:
        # Using the os module to get the terminal size. The function returns a tuple 
        # where the first value is the number of rows and the second is the number of columns.
        _, terminal_cols = os.get_terminal_size()
        
        # If successfully determined, log the detected terminal width
        logger_debug.debug(f"Detected terminal width as: {terminal_cols} columns.")
        
        # Return the detected number of columns
        return terminal_cols
        
    except OSError:
        # If there was an error determining the terminal width, default to 80 columns.
        # This is a common width for many terminals.
        default_cols = 80
        
        # Log a warning message indicating that the terminal width detection failed 
        # and that the default width is being used.
        logger_debug.warning("Failed to detect terminal width. Defaulting to 80 columns.")
        
        # Return the default number of columns
        return default_cols
