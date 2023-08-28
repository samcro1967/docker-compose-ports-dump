#!/usr/bin/env python3

"""
dcpd.py - Dependency Checker and Python Dependencies Manager.

This module, `dcpd.py`, is designed to manage and verify dependencies for Python projects. It offers functionalities
like checking for the availability of critical Python packages, prompting users to install missing ones,
and generating a `requirements.txt` file with necessary dependencies. It also provides integrations with
logging utilities and argument parsing for increased user interactivity and diagnostics.

Key functionalities:
- Verifying the installation of the `stdlib_list` module, which is critical for dependency checking.
- Generating a `requirements.txt` file based on discovered dependencies.
- Prompting users to install missing packages based on the generated `requirements.txt`.
- Handling process interruptions gracefully and logging any unexpected exits.

Usage:
Execute the script using the Python interpreter. On invocation, the script will check dependencies,
prompt the user for any necessary actions, and manage Python dependencies as needed.

Author:
samcro1967
Date:
07/24/2023
"""

import subprocess
import sys
from dcpd_pip import get_required_pip_modules, generate_requirements_txt, are_required_modules_installed
import dcpd_arguments_parser as dcpd_ap
import dcpd_log_debug
import dcpd_log_info

# Create an alias for convenience
logger_info = dcpd_log_info.logger
logger_debug = dcpd_log_debug.logger

# Parsing command-line arguments early on to determine the verbosity.
args = dcpd_ap.parse_arguments()

# -------------------------------------------------------------------------
def check_and_install_stdlib_list():
    """
    Checks for the availability of the 'stdlib_list' module and prompts the user for installation if not found.

    If the user agrees to install, the function attempts to use 'pip' to install the 'stdlib_list' module.
    If the installation is successful or if the module is already installed, the function returns True.
    In case of installation failure or if the user opts out of installation, the function returns False.

    Returns:
        bool: True if 'stdlib_list' is available or successfully installed, otherwise False.

    Raises:
        subprocess.CalledProcessError: If there's an error during the installation of 'stdlib_list' using pip.
    """
    # pylint: disable=import-outside-toplevel
    try:
        # Attempt to import the 'stdlib_list' module
        import stdlib_list  # pylint: disable=unused-import
        return True  # Indicate that stdlib_list is already installed
    except ImportError:
        print("The 'stdlib_list' module is required but not installed.")
        response = input("Do you want to install it now? (yes/no): ").strip().lower()
        if response == "yes":
            try:
                # Try to install 'stdlib_list' using pip
                subprocess.check_call([sys.executable, "-m", "pip", "install", "stdlib-list"])
                return True  # Indicate that stdlib_list was installed
            except subprocess.CalledProcessError:
                print("Error installing 'stdlib_list'. Please install it manually and rerun the script.")
                sys.exit(1)  # Exit the script due to installation error
        else:
            print("Please install 'stdlib_list' manually and rerun the script.")
            return False  # Indicate that user decided not to install stdlib_list

# -------------------------------------------------------------------------
def main():
    """
    Main execution function for dcpd.

    - Ensures the 'stdlib_list' module is installed, and prompts the user for installation if not found.
    - Retrieves required pip modules using the `get_required_pip_modules` function.
    - Generates a 'requirements.txt' file with necessary dependencies using the `generate_requirements_txt` function.
    - Checks if the required pip modules are installed. If any are missing, the user is prompted to install them using the generated 'requirements.txt' file.

    Note:
        The script will exit early if required modules are found missing after the check.
    """

    # Verify stdlib_list is installed
    if check_and_install_stdlib_list():
        logger_info.info("stdlib_list was installed. Continuing with the script...")

    # Call get_required_pip_modules
    get_required_pip_modules(args)

    # Generate the requirements.txt file
    generate_requirements_txt(args)

    # Check if required modules are installed
    if not are_required_modules_installed(args):
        print("Some required dependencies are missing.")
        print("Please run 'pip install -r requirements.txt' to install the required packages.")
        return  # Exit the script

# -------------------------------------------------------------------------
if __name__ == '__main__':
    # Attempt to execute the main function of the script and additional operations from dcpd_main.
    # Handle interruptions gracefully, logging any unexpected exits.
    try:
        # Call the primary function in the calling script
        main()

        # Call the primary function in dcpd_main.py
        from dcpd_main import execute_dcpd
        execute_dcpd()
    except (KeyboardInterrupt, EOFError):
        logger_info.error("Process interrupted. Exiting gracefully.")
        # Optionally, you can exit the script with a status code.
        sys.exit(1)
