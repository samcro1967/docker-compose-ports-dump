# dcpd_help.py

import sys

# Add config to the sys path
sys.path.append('../config')

from colorama import Fore, Style
import dcpd_config as dcpd_config
import dcpd_log_info as dcpd_log_info
import dcpd_utils as dcpd_utils

# Create an alias for convenience
logger_info = dcpd_log_info.logger

# Configurations
default_docker_compose_file = dcpd_config.DEFAULT_DOCKER_COMPOSE_FILE
default_vpn_container_name = dcpd_config.DEFAULT_VPN_CONTAINER_NAME
lines_per_page = dcpd_config.LINES_PER_PAGE

# -------------------------------------------------------------------------
def print_examples(paginate=True, verbose=False):
    """
    Prints examples of 'port.mapping' configurations in a docker-compose.yml file.

    Args:
        paginate (bool): If True, the output is paginated, otherwise it's printed continuously.
        verbose (bool): If True, provides detailed logging to the console.

    Returns:
        None
    """
    logger_info.info("Beginning to print examples.")
    
    # Get the common help text containing examples
    output_text = common_help_text()

    try:
        if paginate:
            dcpd_utils.paginate_output(output_text)
            logger_info.info("Paginated display of examples completed.")
            if verbose:
                print("Paginated display of examples completed.")
        else:
            # Display the output without pagination
            print(output_text)
            logger_info.info("Finished printing examples without pagination.")
    except Exception as e:
        error_message = f"{Fore.RED}An error occurred while displaying the examples: {e}{Style.RESET_ALL}"
        print(error_message)
        logger_info.error(error_message)

        if verbose:
            print("Error details have been logged.")

# -------------------------------------------------------------------------
def common_help_text():
    """
    Return the common help text containing examples of port.mapping and host.mapping configurations.
    """
    logger_info.info("Beginning to construct examples.")
    help_text = f"""
{Fore.YELLOW}Examples of port.mapping configuration in a docker-compose.yml file:{Style.RESET_ALL}

{Fore.GREEN}1. Service attached to VPN container:{Style.RESET_ALL}
services:
  {Fore.GREEN}my_service1:{Style.RESET_ALL}
    environment:
      - {Fore.GREEN}port.mapping=51820{Style.RESET_ALL}
    network_mode: service:{Fore.GREEN}your_vpn_container_name{Style.RESET_ALL}

{Fore.CYAN}In example 1:{Style.RESET_ALL}
The {Fore.GREEN}'my_service1'{Style.RESET_ALL} is attached to the VPN container {Fore.GREEN}'your_vpn_container_name'{Style.RESET_ALL}.
The {Fore.GREEN}'port.mapping'{Style.RESET_ALL} environment variable is set to {Fore.GREEN}'51820'{Style.RESET_ALL}, which represents the external port that should be mapped to the service {Fore.GREEN}'your_vpn_container_name'{Style.RESET_ALL}.
The {Fore.GREEN}'port.mapping'{Style.RESET_ALL} can be anywhere in the environment block. It does not need to be first or last.

{Fore.GREEN}2. Another service attached to VPN container:{Style.RESET_ALL}
services:
  {Fore.GREEN}my_service2:{Style.RESET_ALL}
    environment:
      - {Fore.GREEN}port.mapping=1194{Style.RESET_ALL}
      - {Fore.GREEN}port.mapping1=1195{Style.RESET_ALL}
      - {Fore.GREEN}port.mapping2=1196{Style.RESET_ALL}
    network_mode: service:{Fore.GREEN}your_vpn_container_name{Style.RESET_ALL}

{Fore.CYAN}In example 2:{Style.RESET_ALL}
{Fore.GREEN}'my_service2'{Style.RESET_ALL} is another service that is attached to the VPN container {Fore.GREEN}'your_vpn_container_name'{Style.RESET_ALL}.
It has three {Fore.GREEN}'port.mappings'{Style.RESET_ALL} environment variables set to {Fore.GREEN}'1194, 1195, & 1196'{Style.RESET_ALL}, representing the external ports mapped to the service {Fore.GREEN}'your_vpn_container_name'{Style.RESET_ALL}.
The {Fore.GREEN}'port.mappings'{Style.RESET_ALL} can be anywhere in the environment block. It does not need to be first or last.

{Fore.GREEN}3. Another service not attached to VPN container:{Style.RESET_ALL}
services:
  {Fore.GREEN}my_service3:{Style.RESET_ALL}
    ports:
     - {Fore.GREEN}8923:8080{Style.RESET_ALL}

{Fore.CYAN}In example 3:{Style.RESET_ALL}
{Fore.GREEN}'my_service3'{Style.RESET_ALL} is another service that is not attached to the VPN container {Fore.GREEN}'your_vpn_container_name'{Style.RESET_ALL}.
It has one external port, {Fore.GREEN}'8923'{Style.RESET_ALL}, mapped to the internal port {Fore.GREEN}'8080'{Style.RESET_ALL}.

{Fore.GREEN}4. Your VPN Container:{Style.RESET_ALL}
services:
  {Fore.GREEN}your_vpn_container_name:{Style.RESET_ALL}
    ports:
      - {Fore.GREEN}1194:1194{Style.RESET_ALL}
      - {Fore.GREEN}1195:1195{Style.RESET_ALL}
      - {Fore.GREEN}1196:1196{Style.RESET_ALL}
      - {Fore.GREEN}51820:51820{Style.RESET_ALL}

{Fore.CYAN}In example 4:{Style.RESET_ALL}
{Fore.GREEN}'your_vpn_container_name'{Style.RESET_ALL} is the name of your VPN container.
It has four ports mapped, {Fore.GREEN}'1194, 1195, 1196, & 51820'{Style.RESET_ALL} for the services that are attaching to its network, 'my_service1' and 'my_service2'.

{Fore.YELLOW}Examples of host.mapping configuration in a docker-compose.yml file:{Style.RESET_ALL}

{Fore.GREEN}1. Service attached to host networking with one port mapping:{Style.RESET_ALL}
services:
  {Fore.GREEN}my_service1:{Style.RESET_ALL}
    environment:
      - {Fore.GREEN}host.mapping=8080{Style.RESET_ALL}
    network_mode: host

{Fore.CYAN}In example 1:{Style.RESET_ALL}
The {Fore.GREEN}'my_service1'{Style.RESET_ALL} is attached to the host network.
The {Fore.GREEN}'host.mapping'{Style.RESET_ALL} environment variable is set to {Fore.GREEN}'8080'{Style.RESET_ALL}, which represents the external port being exposed by the host.
The {Fore.GREEN}'host.mapping'{Style.RESET_ALL} can be anywhere in the environment block. It does not need to be first or last.

{Fore.GREEN}2. Service attached to host networking with multiple port mapping:{Style.RESET_ALL}
services:
  {Fore.GREEN}my_service2:{Style.RESET_ALL}
    environment:
      - {Fore.GREEN}host.mapping=1194{Style.RESET_ALL}
      - {Fore.GREEN}host.mapping1=1195{Style.RESET_ALL}
      - {Fore.GREEN}host.mapping2=1196{Style.RESET_ALL}
    network_mode: host

{Fore.CYAN}In example 2:{Style.RESET_ALL}
The {Fore.GREEN}'my_service2'{Style.RESET_ALL} is attached to the host network.
The {Fore.GREEN}'host.mapping'{Style.RESET_ALL} environment variables are set to {Fore.GREEN}'1194, 1195' & 1196'{Style.RESET_ALL} which represent the external ports being exposed by the host.
The {Fore.GREEN}'host.mappings'{Style.RESET_ALL} can be anywhere in the environment block. They do not need to be first or last.
"""

    logger_info.info("Finished constructing examples.")
    return help_text

# -------------------------------------------------------------------------
def print_help(verbose=False):
    """
    Prints the script's help message.

    Args:
        verbose (bool): If True, provides detailed logging to the console.

    Returns:
        None
    """
    # ANSI color codes
    RESET = "\033[0m"
    RED = "\033[91m"

    if not isinstance(verbose, bool):
        raise ValueError("The verbose argument should be of type bool.")

    try:
        logger_info.info("Beginning to print help message.")
        
        help_message = (
            "usage: docker_ports_dump.py [-h] [-d] [-e] [-n] [-o] [-f FILE] [-v VPN_CONTAINER_NAME] [-s] [-V]\n\n"
            "Parse Docker Compose file and extract ports.\n"
            "\noptions:\n"
            "  -h, --help                   show this help message and exit.\n"
            "  -d, --debug                  Print the debug info. All other arguments ignored.\n"
            "  -e, --sort-by-external-port  Sort the table by External Port.\n"
            "  -n, --sort-by-service-name   Sort the table by Service Name.\n"
            "  -s, --show-examples          Show examples of port.mapping configuration in a docker-compose.yml file.\n"
            "  -V, --version                Show version information and exit.\n"
            "  -o, --output                 Generate a web page with the port mappings.\n\n"
            "All options are mutually exclusive and cannot be used together.\n"
            f"{RED}DEFAULT_DOCKER_COMPOSE_FILE must be configured in dcpd_config.py{RESET}"
        )

        print(help_message)
        logger_info.info("Finished printing help message.")
        
        if verbose:
            print("Help message printed successfully.")

    except UnicodeEncodeError:
        print(f"{RED}Error: Unable to print due to encoding issues. Please check your terminal's character support.{RESET}")
    except Exception as e:
        if verbose:
            print(f"{RED}Error: An unexpected error occurred. Details: {e}{RESET}")
        logger_info.error(f"Unexpected error during print_help execution: {e}")

