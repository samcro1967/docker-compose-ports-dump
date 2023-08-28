# dcpd_pip.py

import os
import ast
import pkg_resources
import pprint
import sys
from stdlib_list import stdlib_list
from typing import List, Dict
import dcpd_arguments_parser as dcpd_ap
import dcpd_log_debug as dcpd_log_debug
import dcpd_log_info as dcpd_log_info

# Create an alias for convenience
logger_info = dcpd_log_info.logger
logger_debug = dcpd_log_debug.logger

# Add this at the top of your script
ALWAYS_INCLUDE_PACKAGES = ["gunicorn"]

# Modify the path for files
requirements_txt = os.path.join("..", "requirements.txt")

# Global map for special cases where module name and pip package name differ
module_to_package_map = {
    "yaml": "PyYAML",
    "markdown_it": "markdown-it-py",
}

# Reverse mapping for special cases
package_to_module_map = {v: k for k, v in module_to_package_map.items()}

# -------------------------------------------------------------------------
def get_required_pip_modules(args) -> Dict[str, str]:
    """
    List the pip modules required by the scripts in the current directory.

    This function inspects all Python files in the current directory, identifies 
    their imports, and determines which pip modules are required. It then checks 
    if the identified modules are installed and retrieves their versions.

    Args:
        args (object): An argument object with a 'verbose' attribute for controlling verbosity.

    Returns:
        Dict[str, str]: A dictionary mapping required pip modules to their versions.
    """

    # Logging entry message
    logger_info.info("Entering get_required_pip_modules function.")
    if args.verbose:
        print("Starting to retrieve required pip modules.")

    # Set up data: standard libraries, custom prefixes, and excluded modules
    standard_libs = set(stdlib_list())
    custom_prefixes = ["dcpd_"]
    excluded_modules = ["pkg_resources"]
    required_modules = set()
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # Loop through all Python files in the current directory
    for filename in os.listdir(current_dir):
        if filename.endswith(".py"):
            script_filename = os.path.join(current_dir, filename)

            # Log the scanned file name in verbose mode
            if args.verbose:
                print(f"Scanning the file: {script_filename} for pip modules...")

            with open(script_filename, 'r') as file:
                tree = ast.parse(file.read(), filename=script_filename)

            # Check imports in the file
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    module_name = (node.names[0].name if isinstance(node, ast.Import) else node.module).split(".")[0]
                    if module_name not in standard_libs and not any([module_name.startswith(prefix) for prefix in custom_prefixes]) and module_name not in excluded_modules:
                        required_modules.add(module_name)

    # Map the modules to their packages, and retrieve version info if installed
    required_modules_with_versions = {}
    for package in required_modules:
        module_to_import = package_to_module_map.get(package, package)
        if args.verbose:
            print(f"Checking if package '{package}' (mapped from module '{module_to_import}') is installed...")

        try:
            __import__(module_to_import)
            module_version = pkg_resources.get_distribution(module_to_import).version
            if args.verbose:
                print(f"Package '{package}' (mapped from module '{module_to_import}') is installed with version: {module_version}.")
            required_modules_with_versions[module_to_import] = module_version
        except ImportError:
            logger_debug.debug(f"ImportError for package '{package}'. It might not be installed.")
        except pkg_resources.DistributionNotFound:
            logger_debug.debug(f"Version not found for module '{module_to_import}'. It might not be a pip package.")

    for module, package in module_to_package_map.items():
        if module not in required_modules_with_versions:
            try:
                version = pkg_resources.get_distribution(package).version
                required_modules_with_versions[module] = version
            except pkg_resources.DistributionNotFound:
                logger_debug.debug(f"Version not found for module '{module}' mapped to package '{package}'.")

    sorted_modules_with_versions = dict(sorted(required_modules_with_versions.items(), key=lambda item: item[0].lower()))

    # Logging exit message
    logger_info.info("Exiting get_required_pip_modules function.")
    if args.verbose:
        print("Finished retrieving required pip modules.")

    return sorted_modules_with_versions

# -------------------------------------------------------------------------
def generate_requirements_txt(args):
    """
    Generate a requirements.txt file based on the required pip modules.
    
    This function identifies the required pip modules by analyzing the scripts
    in the current directory. It then creates a requirements.txt file listing
    the names and versions of the required modules for easy installation.
    
    Args:
        args (object): An argument object with a 'verbose' attribute for controlling verbosity.

    Returns:
        None
    """

    logger_info.info("Entering generate_requirements_txt function.")
    if args.verbose:
        print("Starting to generate requirements.txt file.")

    # Get the required pip modules
    try:
        required_pip_modules = get_required_pip_modules(args)
    except Exception as e:
        logger_debug.error(f"An error occurred while getting required pip modules: {e}")
        return

    all_packages = set()

    # Translate module names to package names, including versions
    for module, version in required_pip_modules.items():
        package_name = module_to_package_map.get(module, module)
        all_packages.add(f"{package_name}=={version}")

    # Add the "always include" packages if any (this assumes ALWAYS_INCLUDE_PACKAGES is defined elsewhere)
    all_packages.update(ALWAYS_INCLUDE_PACKAGES)

    # Sort the list of packages alphabetically
    sorted_packages = sorted(all_packages, key=lambda s: s.lower())

    # Write the sorted list to the requirements.txt file
    try:
        if args.verbose:
            print("Final list of packages to be written to requirements.txt:")
            for pkg in sorted_packages:
                print(pkg)
        with open('requirements.txt', 'w') as req_file:
            req_file.write("\n".join(sorted_packages))
            req_file.write("\n")  # end with a newline

        if args.verbose:
            print("requirements.txt file generated successfully.")
        logger_info.info("requirements.txt file generated successfully.")
    except Exception as e:
        logger_debug.error(f"An error occurred while writing to requirements.txt: {e}")

    logger_info.info("Exiting generate_requirements_txt function.")

# -------------------------------------------------------------------------
def are_required_modules_installed(args) -> bool:
    """
    Check if all the required modules are installed.
    
    This function reads the requirements.txt file and checks if all the listed
    packages are installed. If any required packages are missing, they are 
    listed out and False is returned. Otherwise, it returns True.

    Args:
        args (object): An argument object with a 'verbose' attribute for controlling verbosity.

    Returns:
        bool: True if all required modules are installed, False otherwise.
    """

    logger_info.info("Entering are_required_modules_installed function.")
    if args.verbose:
        print("Checking if all required modules are installed.")

    # Try reading the requirements.txt file
    try:
        with open('requirements.txt', "r") as f:
            required_packages = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        msg = f"requirements.txt not found."
        logger_debug.error(msg)
        if args.verbose:
            print(msg)
        return False
    except Exception as e:
        logger_debug.error(f"An error occurred while reading requirements.txt: {e}")
        return False

    missing_packages = []

    for package in required_packages:
        # Split the package name from its version, if provided
        package_name = package.split("==")[0]
        module_to_import = package_to_module_map.get(package_name, package_name)

        # Verbose logging for package checks
        if args.verbose:
            print(f"Checking if package '{package}' (mapped from module '{module_to_import}') is installed...")

        # Try importing the package/module
        try:
            __import__(module_to_import)
            
            # Check the installed version
            dist_package_name = module_to_package_map.get(module_to_import, module_to_import)
            module_version = pkg_resources.get_distribution(dist_package_name).version

            # Verbose logging for installed packages
            if args.verbose:
                print(f"Package '{package}' (mapped from module '{module_to_import}') is installed with version: {module_version}.")

        except ImportError as e:
            logger_debug.warning(f"Package '{package}' not found. Error: {e}")
            if args.verbose:
                print(f"Error importing '{module_to_import}': {e}")
            missing_packages.append(package)

    # Check and handle missing packages
    if missing_packages:
        missing_modules_msg = f"Missing modules: {', '.join(missing_packages)}"
        logger_debug.warning(missing_modules_msg)
        if args.verbose:
            print(missing_modules_msg)
        logger_info.info("Exiting are_required_modules_installed function with status: False.")
        return False

    logger_info.info("All required modules are installed.")
    logger_info.info("Exiting are_required_modules_installed function with status: True.")

    return True