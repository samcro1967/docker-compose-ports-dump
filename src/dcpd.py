#!/usr/bin/env python3

# File: dcpd.py
# Created by samcro1967 on 07/24/2023

from dcpd_pip import get_required_pip_modules, generate_requirements_txt, are_required_modules_installed
import dcpd_arguments_parser as dcpd_ap
import subprocess
import sys

# Parsing command-line arguments early on to determine the verbosity.
args = dcpd_ap.parse_arguments()

# -------------------------------------------------------------------------
def check_and_install_stdlib_list():
    """
    Check if the 'stdlib_list' module is installed and install it if prompted by the user.
    Returns True if the module is installed successfully, otherwise exits the script.
    """
    try:
        import stdlib_list  # Attempt to import the 'stdlib_list' module
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
            sys.exit(1)  # Exit the script because 'stdlib_list' is required but not installed


# -------------------------------------------------------------------------
def main():
    """
    Entry function to execute required operations for dcpd.
    """

    # Verify stdlib_list is installed
    if check_and_install_stdlib_list():
        print("stdlib_list was installed. Continuing with the script...")

    # Call get_required_pip_modules (though we don't do anything with its result directly here)
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
    try:
        # Call the primary function in the calling script
        main() 

        # Call the primary function in dcpd_main.py
        from dcpd_main import execute_dcpd
        execute_dcpd(args)
    except (KeyboardInterrupt, EOFError):
        logger_info.error("Process interrupted. Exiting gracefully.")
        # Optionally, you can exit the script with a status code.
        sys.exit(1)