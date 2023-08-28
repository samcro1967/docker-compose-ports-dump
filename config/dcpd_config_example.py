# dcpd_config.py
# This file contains variables for use in all scripts.

# Replace with the  path(s) to one or more files.  Each row must end in a comma.
DEFAULT_DOCKER_COMPOSE_FILE = [
    "/path/to/your/docker-compose1.yml",
    "/path/to/your/docker-compose1.yml",
    # ... add more if necessary
]

# Set the version
VERSION = "v1.0.0"

# Replace with desired file name for the output html file
DEFAULT_OUTPUT_HTML_FILE_NAME = "dcpd_output.html"

# Replace with the name of your VPN container if you have one. Otherwise, set it to "".
DEFAULT_VPN_CONTAINER_NAME = "your_vpn_container_name"

# Number of lines per page for pagination (set to zero to disable pagination)
LINES_PER_PAGE = 0

# Number of characters to print for log separator
LOG_SEPARATOR_LENGTH = 55

# Path to docker.db (relative to the folder where the script is being ran)
DB_PATH = "docker.db"

# Default background color for the report
DEFAULT_WEB_PAGE_BACKGROUND_COLOR = "scarlet"

# Default text color for the web page
DEFAULT_WEB_PAGE_TEXT_COLOR = "white"

WEB_COLOR_MAP = {
    "black": "#000000",
    "white": "#FFFFFF",
    "bright_black": "#808080",
    "bright_red": "#FF0000",
    "bright_green": "#00FF00",
    "bright_yellow": "#FFFF00",
    "bright_blue": "#0000FF",
    "bright_magenta": "#FF00FF",
    "bright_cyan": "#00FFFF",
    "bright_white": "#C0C0C0",
    "hotpink": "#FF69B4",
    "cyan": "#00FFFF",
    "teal": "#008080",
    "orange": "#FFA500",
    "purple": "#800080",
    "lime": "#00FF00",
    "magenta": "#FF00FF",
    "navy": "#000080",
    "olive": "#808000",
    "steelblue": "#4682B4",
    "scarlet": "#BB0000",
    "grey": "#666666"
}

# Colors ANSI escape code can be found here:
# https://en.wikipedia.org/wiki/ANSI_escape_code

# Also, you can run 256-colors.sh to see them in the terminal from this link:
# https://misc.flogisoft.com/bash/tip_colors_and_formatting

# Pagination Hightlighting Color
PAGINATION_HIGHLIGHTING_COLOR = "\033[1;33;40m" #bold yellow text on a black background

# Debug Report Header Color
DEBUG_REPORT_HEADER_COLOR = "\033[1;97m" #bold bright white

# Restet the color of the terminal back to its defaults
TERMINAL_COLOR_RESET = "\033[m"

# Set default sort order with no argument provided to the command line
# Choice are none, service_name, or external_port
# none sorts by order defined in docker-sompose.yml file
DEFAULT_SORT_ORDER = "none"

# Default log file size
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB

# Default numer of logs to keep
LOG_RETENTION_COUNT = 5  # Keep the latest 5 log files.

# Preferred Time Format
LOG_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Specify the default directory to save log files to
DEFAULT_LOG_DIRECTORY = "../config/logs"

# Enable debug mode by default:  True or False
DEFAULT_DEBUG_MODE = False

# Console logging level (INFO OR ERROR, ERROR is the default)
CONSOLE_LOGGING_LEVEL = "ERROR"

# Location cache expiration (hours)
LOCATION_CACHE_HOURS = 24

# Location cache expiration (hours)
REDACTED_ZIP_FILE_PASSWORD = "P@55w0rd"

# API KEY
API_KEY = "123456789"

# Flask Cache Type
CACHE_TYPE = 'simple'

# Github repo URL
GITHUB_REPO_URL = "https://api.github.com/repos/samcro1967/docker-compose-ports-dump/releases/latest"