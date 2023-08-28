# dcpd_pip.py

"""
This module provides utilities to manage, check, and generate pip requirements for the project.
"""

import os
import ast
from functools import lru_cache
from typing import Dict
from stdlib_list import stdlib_list
import pkg_resources

import dcpd_log_debug
import dcpd_log_info


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
@lru_cache(maxsize=None)  # Unbounded cache
def get_package_version(package_name: str) -> str:
    """
    Retrieve the version of a specified package if installed.

    This function uses `pkg_resources.get_distribution` to obtain the version
    information of the given package. If the package is not found, it returns None.
    Results are cached to optimize repeated calls with the same package name.

    Args:
        package_name (str): The name of the package for which the version is required.

    Returns:
        str: Version of the specified package if found, else None.

    Raises:
        pkg_resources.DistributionNotFound: If the package is not found.
    """
    try:
        version = pkg_resources.get_distribution(package_name).version
        return version
    except pkg_resources.DistributionNotFound:
        return None

# -------------------------------------------------------------------------
def get_required_pip_modules(args) -> Dict[str, str]:
    """
    List the pip modules required by the scripts in the current directory.
    ...  # Rest of the docstring remains unchanged
    """

    # Logging entry message
    logger_info.info("Entering get_required_pip_modules function.")
    if args.verbose:
        print("Starting to retrieve required pip modules.")

    # Set up data
    standard_libs = set(stdlib_list())
    custom_prefixes = ["dcpd_"]
    excluded_modules = ["pkg_resources"]
    required_modules = set()
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # Loop through Python files and analyze imports
    for filename in os.listdir(current_dir):
        if filename.endswith(".py"):
            script_filename = os.path.join(current_dir, filename)
            process_script_file(args, script_filename, standard_libs, custom_prefixes, excluded_modules, required_modules)

    # Map modules to packages, retrieve versions, and sort
    required_modules_with_versions = get_required_modules_with_versions(args, required_modules)

    # Logging exit message
    logger_info.info("Exiting get_required_pip_modules function.")
    if args.verbose:
        print("Finished retrieving required pip modules.")

    return required_modules_with_versions

# -------------------------------------------------------------------------
def process_script_file(args, script_filename, standard_libs, custom_prefixes, excluded_modules, required_modules):
    """
    Process a Python script file and analyze its imports to identify required modules.

    This function reads a Python script file, analyzes its import statements, and determines
    which modules are required for the script. It considers standard libraries, custom prefixes,
    and excluded modules to identify required modules.

    Args:
        args (object): An argument object with a 'verbose' attribute for controlling verbosity.
        script_filename (str): The path of the script file to be processed.
        standard_libs (set): A set of standard library module names.
        custom_prefixes (list): A list of custom module prefixes to consider.
        excluded_modules (list): A list of module names to exclude from consideration.
        required_modules (set): A set to store the identified required module names.

    Returns:
        None
    """
    # pylint: disable=too-many-arguments
    if args.verbose:
        print(f"Scanning the file: {script_filename} for pip modules...")

    with open(script_filename, 'r', encoding='utf-8') as file:
        tree = ast.parse(file.read(), filename=script_filename)

    # Check imports in the file
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module_name = (node.names[0].name if isinstance(node, ast.Import) else node.module).split(".")[0]
            if module_name not in standard_libs and not any(module_name.startswith(prefix) for prefix in custom_prefixes) and module_name not in excluded_modules:
                required_modules.add(module_name)

# -------------------------------------------------------------------------
def get_required_modules_with_versions(args, required_modules):
    """
    Retrieve versions of required modules and return a dictionary with module-version pairs.

    This function takes a set of required module names, retrieves their versions using the
    get_package_version function, and returns a dictionary containing module names as keys
    and their corresponding versions as values.

    Args:
        args (object): An argument object with a 'verbose' attribute for controlling verbosity.
        required_modules (set): A set of required module names.

    Returns:
        dict: A dictionary mapping required module names to their versions.
    """
    required_modules_with_versions = {}
    for module in required_modules:
        package_name = module_to_package_map.get(module, module)
        try:
            version = get_package_version(package_name)
            required_modules_with_versions[module] = version

            if args.verbose:
                print(f"Package '{package_name}' is installed with version: {version}.")

        except pkg_resources.DistributionNotFound:
            logger_info.debug("Package '%s' not found.", package_name)
            required_modules_with_versions[module] = None

    for module, package in module_to_package_map.items():
        if module not in required_modules_with_versions:
            try:
                version = pkg_resources.get_distribution(package).version
                required_modules_with_versions[module] = version
            except pkg_resources.DistributionNotFound:
                logger_info.debug("Version not found for module '%s' mapped to package '%s'.", module, package)

    return dict(sorted(required_modules_with_versions.items(), key=lambda item: item[0].lower()))

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
    except (OSError, SyntaxError, pkg_resources.DistributionNotFound) as error:
        logger_info.error("An error occurred while getting required pip modules: %s", error)
        return

    all_packages = set()

    # Translate module names to package names, including versions
    for module, _ in required_pip_modules.items():
        package_name = module_to_package_map.get(module, module)
        all_packages.add(package_name)

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
        with open(requirements_txt, 'w', encoding='utf-8') as req_file:
            req_file.write("\n".join(sorted_packages))
            req_file.write("\n")  # end with a newline

        if args.verbose:
            print("requirements.txt file generated successfully.")
        logger_info.info("requirements.txt file generated successfully.")
    except (FileNotFoundError, IOError, PermissionError) as error:
        logger_info.error("An error occurred while writing to requirements.txt: %s", error)

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

    # Try reading the requirements.txt file
    try:
        with open(requirements_txt, "r", encoding='utf-8') as file:
            required_packages = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        msg = "requirements.txt not found."
        logger_info.error(msg)
        if args.verbose:
            print(msg)
        return False
    except (IOError, PermissionError) as error:
        logger_info.error("An error occurred while reading requirements.txt: %s", error)
        return False

    missing_packages = []
    installed_packages = []

    for package in required_packages:
        package_name = package.split("==")[0]
        module_to_import = package_to_module_map.get(package_name, package_name)
        try:
            __import__(module_to_import)
            dist_package_name = module_to_package_map.get(module_to_import, module_to_import)
            module_version = pkg_resources.get_distribution(dist_package_name).version
            installed_packages.append((package, module_to_import, module_version))
        except ImportError as import_error:
            missing_packages.append(package)
            logger_debug.warning("Package '%s' not found. Error: %s", package, import_error)

    # Display verbose output in consolidated form
    if args.verbose:
        if installed_packages:
            print("\n".join(
                f"Package '{pkg}' (mapped from module '{mod}') is installed with version: {ver}."
                for pkg, mod, ver in installed_packages
            ))
        if missing_packages:
            print(f"Missing modules: {', '.join(missing_packages)}")

    if missing_packages:
        logger_debug.warning("Missing modules: %s", ', '.join(missing_packages))
        logger_info.info("Exiting are_required_modules_installed function with status: False.")
        return False

    logger_info.info("All required modules are installed.")
    logger_info.info("Exiting are_required_modules_installed function with status: True.")

    return True
