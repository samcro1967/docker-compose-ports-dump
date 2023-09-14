"""
dcpd_utils.py

This script provides utility functions for interacting with the DCPD (Dynamic Configurable Port Detection) system.
It includes functions for caching data, checking cache validity, fetching software versions, and paginating output.

"""

# pylint: disable=E0401,C0415,R0915, R0912, R0914, C0103, W0612, W0603
import sys
import os
import platform

# Add config to the sys path
# pylint: disable=wrong-import-position
sys.path.extend(['.', '../config'])

# Third-party imports (if any)
import dcpd_config
import dcpd_log_info
import dcpd_log_debug

# Using the variables from config.py
default_docker_compose_file = dcpd_config.DEFAULT_DOCKER_COMPOSE_FILE
default_vpn_container_name = dcpd_config.DEFAULT_VPN_CONTAINER_NAME
lines_per_page = dcpd_config.LINES_PER_PAGE
pagination_highlight_color = dcpd_config.PAGINATION_HIGHLIGHTING_COLOR
terminal_color_reset = dcpd_config.TERMINAL_COLOR_RESET

# Create an alias for convenience
logger_info = dcpd_log_info.logger
logger_debug = dcpd_log_debug.logger

# Set length of log file separator
log_separator_length = dcpd_config.LOG_SEPARATOR_LENGTH

# Initialize the last viewed page to 1
last_viewed_page = 1

# Check what OS we are running on
IS_WINDOWS = platform.system() == "Windows"
IS_UNIX = not IS_WINDOWS  # Assuming all non-Windows systems are considered Unix-like
# print(f"Is UNIX:  {IS_UNIX}")
# print(f"Is Windows:  {IS_WINDOWS}")

# Conditionally import termios only on Unix-like systems
if IS_UNIX:
    import termios

# Check if the system is Windows and import msvcrt for key input handling
if IS_WINDOWS:
    import msvcrt

# -------------------------------------------------------------------------
def set_permissions_and_ownership(args):
    """
    Set permissions and ownership for files and directories.

    Modifies permissions and ownership of all files and directories starting one level up from where the script resides.
    Logs relevant operations and any errors encountered.

    Note:
        Verbose mode provides detailed console output for better user interaction.
    """

    # Entry messages
    logger_info.info("Starting the permission and ownership modification process.")
    if args.verbose:
        print("Starting the permission and ownership modification process.")

    # Determine the directory path one level up from where the script resides.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)

    # Provide separators in logs for better clarity.
    log_separator_info(logger_info)
    log_separator_debug(logger_debug)

    # Logging the OS context can be beneficial for debugging platform-specific issues.
    logger_info.info("Running on: %s", platform.platform())


    try:
        for root, dirs, files in os.walk(parent_dir):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                os.chmod(dir_path, 0o755)
                os.chown(dir_path, 1000, 1000)

            for file_name in files:
                file_path = os.path.join(root, file_name)
                os.chmod(file_path, 0o755)
                os.chown(file_path, 1000, 1000)

    except OSError as os_error:
        # Catch specific OS-related errors
        logger_info.error("Encountered an OS-related error during permission and ownership modification: %s", str(os_error))
        if args.verbose:
            print(f"OS-related error encountered: {str(os_error)}")

    # Exit messages
    logger_info.info("Permission and ownership modification finished.")
    logger_debug.debug("Permission and ownership modification finished.")

    if args.verbose:
        print("Finished the permission and ownership modification process.")

# -------------------------------------------------------------------------
def get_keypress() -> str:
    """
    Get single keypress on both Windows and UNIX systems.

    Returns:
        str: Detected keypress in lowercase or 'ARROW_UP' if the up arrow key is pressed.
    """
    logger_info.info("Determining single keypress.")

    if IS_WINDOWS:
        keypress = msvcrt.getch().decode('utf-8')  # Use msvcrt for Windows
    else:
        file_descriptor = sys.stdin.fileno()
        old_settings = termios.tcgetattr(file_descriptor)
        try:
            if IS_UNIX:  # Only set raw mode on Unix-like systems
                import tty
                tty.setraw(sys.stdin.fileno())
            keypress = sys.stdin.read(1)
            if keypress == '\x1b':  # escape character, might be an arrow key
                next_char = sys.stdin.read(1)  # read the next character
                if next_char == '[':  # checking for arrow key sequence
                    arrow_char = sys.stdin.read(1)
                    if arrow_char == 'A':
                        logger_info.info("Single keypress determined.")
                        return 'ARROW_UP'
        finally:
            if IS_UNIX:  # Only restore terminal settings on Unix-like systems
                termios.tcsetattr(file_descriptor, termios.TCSADRAIN, old_settings)

    logger_info.info("Single keypress determined.")
    return keypress.lower()

# -------------------------------------------------------------------------
def is_interactive_terminal():
    """
    Checks if the script is running in an interactive terminal.

    Returns:
        bool: True if the script is running in an interactive terminal, False otherwise.
    """
    logger_info.info("Checking to see if the terminal is interactive.")
    try:
        # Check if sys.stdin has the attribute isatty to determine if it's an interactive terminal
        logger_info.info("Terminal is interactive.")
        return sys.stdin.isatty()
    except AttributeError:
        # If the attribute is not present, it's not an interactive terminal
        logger_info.info("Terminal is not interactive.")
        return False

# -------------------------------------------------------------------------
def reset_highlights(lines, term):
    """
    Removes highlights from the specified term in all lines.

    Args:
        lines (List[str]): The list of lines to process.
        term (str): The term for which highlights need to be removed.

    Returns:
        List[str]: The list of lines with highlights removed.
    """
    logger_info.info("Beginning removal of highlighting from the terminal.")

    # Assuming your highlight format is consistent
    normal = term

    # Remove the highlights for the specified term in each line
    processed_lines = [line.replace(highlight_term(term, term), normal) for line in lines]

    logger_info.info("Finished removing highlighting from the terminal.")
    return processed_lines


# -------------------------------------------------------------------------
def highlight_term(line: str, term: str) -> str:
    """
    Highlights the specified term in the given line.

    Args:
        line (str): The line of text to highlight.
        term (str): The term to be highlighted.

    Returns:
        str: The line with the term highlighted.
    """
    logger_info.info("Beginning to highlight lines in the terminal.")

    if not term:  # Check for None or empty terms
        return line

    # Find the index of the term (case-insensitive) in the line
    term_index = line.lower().find(term.lower())

    if term_index == -1:
        logger_info.info("Finished highlighting lines in the terminal.")
        return line

    # Calculate the start and end positions of the term in the line
    start = term_index
    end = term_index + len(term)

    # Construct the highlighted version of the line
    highlighted = (
        line[:start]
        + f"{pagination_highlight_color}{line[start:end]}{terminal_color_reset}"
        + line[end:]
    )

    logger_info.info("Finished highlighting the terminal.")
    return highlighted

# -------------------------------------------------------------------------
def paginate_output(text: str):
    """
    Paginates the given text for interactive display in the terminal.

    Args:
        text (str): The text to be paginated and displayed.
    """

    logger_info.info("Beginning to paginate the output.")

    global lines_per_page, last_viewed_page

    # Check if pagination is disabled
    if lines_per_page == 0:
        print(text)
        logger_info.info("dcpd_utils.paginate_output completed.  Pagination is diabled.")
        return

    original_lines = text.split('\n')
    lines = original_lines.copy()
    total_lines = len(lines)

    total_lines = len(lines)
    total_pages = (total_lines + lines_per_page - 1) // lines_per_page
    current_page = last_viewed_page  # Use the last viewed page as the starting page
    start_line = (current_page - 1) * lines_per_page

    in_search_mode = False
    search_term = None
    search_positions = []
    search_index = 0  # Index in search_positions
    # -------------------------------------------------------------------------
    def print_page(start: int, page_number: int):
        """
        Prints a page of lines starting from the specified index.

        Args:
            start (int): The starting index of the lines to print.
            page_number (int): The current page number.

        Returns:
            int: The ending index of the lines that were printed.
        """
        # Log the start of the print_page process
        logger_info.info("dcpd_utils.print_page started.")

        # Clear the terminal screen to show the new page
        clear_terminal()

        # If it's not the first page, print the header
        if page_number != 1:
            custom_header = "+-----------------------+-----------------+-----------------+----------------+---------------+"
            print(custom_header)
            print("|     Service Name      |  External Port  |  Internal Port  |  Port Mapping  |  Mapped App   |")
            print("+=======================+=================+=================+================+===============+")

        # Calculate the ending line index for the current page
        end = min(start + lines_per_page, total_lines)

        # Extract the lines for the current page
        page_lines = lines[start:end]

        # Print the lines for the current page
        print('\n'.join(page_lines))

        # Return the index of the last line displayed on this page
        return end
    # -------------------------------------------------------------------------

    # Print each page until all lines are covered
    while start_line < total_lines:
        # Print the current page using the print_page function
        end_line = print_page(start_line, current_page)


        # ANSI color codes
        RESET = "\033[0m"
        HEADER = "\033[1m\033[96m"  # Bold Cyan
        INFO = "\033[93m"  # Yellow
        COMMAND = "\033[91m"  # Red
        TEXT = "\033[92m"  # Green

        # Define pagination options
        options = [
            ("n", "next"),
            ("p", "prev"),
            ("+", "scroll down"),
            ("-", "scroll up"),
            ("t", "top"),
            ("b", "bottom"),
            ("j", "jump to page"),
            ("r", "return to prev page"),
            ("s", "search"),
            ("l", "set lines/page"),
            ("q", "quit")
        ]

        # Print pagination options
        print(f"\n{HEADER}--- Pagination Options ---{RESET}")
        print(f"{INFO}Page: {current_page}/{total_pages} | Lines/Page: {lines_per_page} | Previous Page: {last_viewed_page}{RESET}")

        # Set number of options per line for pagination help
        options_per_line = 4

        # Print each pagination option
        for i, (option, description) in enumerate(options, start=1):
            print(f"{COMMAND}{option}{RESET}: {TEXT}{description}{RESET}", end=" | " if i % options_per_line != 0 and i != len(options) else "\n")

        if in_search_mode or search_term:  # display search navigation options if in search mode or if a term was searched previously
            print("[: first occurrence | ]: last occurrence | >: next occurrence | <: prev occurrence")

        temp_current_page = current_page

        try:
            print("Enter your choice: ", end='', flush=True)
            choice = get_keypress()

            if choice == 'j':
                page_num_str = input("Enter page number and press enter: ")
                try:
                    page_num = int(page_num_str)
                    if 1 <= page_num <= total_pages:
                        # print(f"'j' option last_viewed_page at entry: {last_viewed_page}")
                        # print(f"'j' option current_page at entry: {current_page}")
                        # print(f"'j' option start_line at entry: {start_line}")
                        start_line = (page_num - 1) * lines_per_page
                        current_page = page_num
                        # last_viewed_page = current_page
                        # print(f"'j' option last_viewed_page at exit: {last_viewed_page}")
                        # print(f"'j' option current_page at exit: {current_page}")
                        # print(f"'j' option start_line at exit: {start_line}")
                    else:
                        print(f"Page number out of range. Valid pages: 1-{total_pages}")
                except ValueError:
                    print("Invalid page number.")
            elif choice == 'ARROW_UP':
                continue  # Just ignore for now, but can be used for navigation in the future
            elif choice == 'n' and temp_current_page < total_pages:
                last_viewed_page = current_page
                current_page += 1
                start_line += lines_per_page
            elif choice == 'p' and temp_current_page > 1:
                last_viewed_page = current_page
                current_page -= 1
                start_line -= lines_per_page
            elif choice == '+':
                start_line = min(start_line + 1, total_lines - lines_per_page)
            elif choice == '-':
                start_line = max(0, start_line - 1)
            elif choice == 'a':
                logger_info.info("dcpd_utils.print_page completed.")
                print('\n'.join(lines[start_line:]))
                return
            elif choice == 't':
                last_viewed_page = current_page
                current_page = 1
                start_line = 0
                print("\nJumped to the top page.\n")
            elif choice == 'b':
                last_viewed_page = current_page
                current_page = total_pages
                start_line = (total_pages - 1) * lines_per_page
                print("\nJumped to the last page.\n")
            elif choice == 's':
                term = input("Enter term to search for: ")
                if term:
                    search_term = term
                    search_positions = [i for i, line in enumerate(original_lines) if term.lower() in line.lower()]
                if search_positions:
                    search_position = search_positions[search_index]
                    start_line = (search_position // lines_per_page) * lines_per_page  # This ensures start_line is at the start of the page
                    current_page = (start_line // lines_per_page) + 1
                    print(f"\n\033[91mTerm found on page {current_page}\033[0m\n")
                    lines = [highlight_term(line, term) for line in original_lines]
                    in_search_mode = True
                else:
                    print("\n\033[91mSearch term not found.\033[0m\n")
                    in_search_mode = False
            elif choice == '>' and in_search_mode:
                search_index += 1
                if search_index < len(search_positions):
                    search_position = search_positions[search_index]
                    start_line = (search_position // lines_per_page) * lines_per_page  # This ensures start_line is at the start of the page
                    current_page = (start_line // lines_per_page) + 1
                else:
                    print("\nReached the last occurrence of the search term.\n")
                    in_search_mode = False  # Exiting search mode
            elif choice == '<' and in_search_mode:
                search_index -= 1
                if search_index >= 0:
                    search_position = search_positions[search_index]
                    start_line = (search_position // lines_per_page) * lines_per_page  # This ensures start_line is at the start of the page
                    current_page = (start_line // lines_per_page) + 1
                else:
                    print("\nReached the first occurrence of the search term.\n")
                    in_search_mode = False  # Exiting search mode
            elif choice == 'l':
                new_lpp = input(f"Enter new lines-per-page setting (current {lines_per_page}): ")
                try:
                    lines_per_page = int(new_lpp)
                except ValueError:
                    print("Invalid lines-per-page setting. Using the previous setting.")
            elif choice == 'r':
                current_page = last_viewed_page
                start_line = (current_page - 1) * lines_per_page
                print("\nReturned to the previously viewed page.\n")
                print(f"current_page: {current_page}")
            elif choice == 'q':
                break
            elif choice == '[':
                # Jump to the first occurrence
                if search_positions:
                    search_index = 0
                    search_position = search_positions[search_index]
                    start_line = (search_position // lines_per_page) * lines_per_page  # This ensures start_line is at the start of the page
                    current_page = (start_line // lines_per_page) + 1
                else:
                    print("\n\033[91mSearch term not found.\033[0m\n")

            elif choice == ']':
                # Jump to the last occurrence
                if search_positions:
                    search_index = len(search_positions) - 1
                    search_position = search_positions[search_index]
                    start_line = (search_position // lines_per_page) * lines_per_page  # This ensures start_line is at the start of the page
                    current_page = (start_line // lines_per_page) + 1
                else:
                    print("\n\033[91mSearch term not found.\033[0m\n")
        except (KeyboardInterrupt, EOFError):
            # Handle Ctrl+C or Ctrl+D gracefully
            print("\nPagination interrupted.")
            break

    # Resetting search mode at the end
    if in_search_mode:
        lines = reset_highlights(lines, search_term)
    logger_info.info("Finished paginating the output.")

# -------------------------------------------------------------------------
def log_separator_info(logger):
    """
    Log a separator line of "=" for visual separation in log files at INFO level.

    Args:
        logger (logging.Logger): Logger object to which the separator should be logged.
    """
    # Create a separator line of "=" characters with the specified length
    separator = "=" * log_separator_length

    # Log the separator line at the INFO level
    logger.info(separator)

    # Log a debug message indicating that the INFO separator has been logged
    logger_debug.debug("Logged INFO separator.")

# -------------------------------------------------------------------------
def log_separator_debug(logger):
    """
    Log a separator line of "=" for visual separation in log files at DEBUG level.

    Args:
        logger (logging.Logger): Logger object to which the separator should be logged.
    """
    # Create a separator line of "=" characters with the specified length
    separator = "=" * log_separator_length

    # Log the separator line at the DEBUG level
    logger.debug(separator)

    # Log a debug message indicating that the DEBUG separator has been logged
    logger_debug.debug("Logged DEBUG separator.")


# -------------------------------------------------------------------------
def log_separator_data(logger):
    """
    Log a separator line of "-" for visual separation in log files, usually for data entries.

    Args:
        logger (logging.Logger): Logger object to which the separator should be logged.
    """
    # Create a separator line of "-" characters with the specified length
    separator = "-" * log_separator_length

    # Log the separator line at the DEBUG level
    logger.debug(separator)

    # Log a debug message indicating that the data separator has been logged
    logger_debug.debug("Logged data separator.")

# -------------------------------------------------------------------------
def clear_terminal():
    """
    Clears the terminal screen by executing system-specific commands.

    This function checks if the script is running on a Windows system or a non-Windows system
    and then uses the appropriate command to clear the terminal screen.

    Note:
        The behavior of this function might vary based on the operating system.

    """
    logger_info.info("dcpd_utils.clear_terminal started.")

    if IS_WINDOWS:
        # If running on a Windows system, use 'cls' command to clear the terminal screen
        os.system('cls')
        logger_info.info("dcpd_utils.clear_terminal completed.")
    else:
        # If running on a non-Windows system, use 'clear' command to clear the terminal screen
        os.system('clear')
        logger_info.info("dcpd_utils.clear_terminal completed.")
