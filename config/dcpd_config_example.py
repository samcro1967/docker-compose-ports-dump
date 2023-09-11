# dcpd_config.py
# This file contains variables for use in all scripts.

# Replace with the  path(s) to one or more files.  Each row must end in a comma.
DEFAULT_DOCKER_COMPOSE_FILE = [
    "/path/to/your/docker-compose1.yml",
    "/path/to/your/docker-compose1.yml",
    # ... add more if necessary
]

# Set the version
VERSION = "v1.2.0"

# Replace with desired file name for the output html file
DEFAULT_OUTPUT_HTML_FILE_NAME = "dcpd_output.html"

# Replace with the name of your VPN container if you have one. Otherwise, set it to "".
DEFAULT_VPN_CONTAINER_NAME = "your_vpn_container_name"

# Number of lines per page for pagination (set to zero to disable pagination)
LINES_PER_PAGE = 0

# Number of characters to print for log separator
LOG_SEPARATOR_LENGTH = 55

# Default background color for the web page
DEFAULT_WEB_PAGE_BACKGROUND_COLOR = "scarlet"

# Default accent color for the web page
DEFAULT_WEB_PAGE_ACCENT_COLOR = "gray"

# Default text color for the web page
DEFAULT_WEB_PAGE_TEXT_COLOR = "white"

# Default font name for the web page
DEFAULT_WEB_PAGE_FONT_NAME = "roboto"

# Default font sizze for the web page
DEFAULT_WEB_PAGE_FONT_SIZE = "medium"

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
    "purple": "#5C2D91",
    "lime": "#00FF00",
    "magenta": "#FF00FF",
    "navy": "#000080",
    "olive": "#808000",
    "maroon": "#800000",
    "green": "#008000",
    "blue": "#0000FF",
    "chocolate": "#D2691E",
    "turquoise": "#40E0D0",
    "silver": "#C0C0C0",
    "royalblue": "#4169E1",
    "coral": "#FF7F50",
    "tomato": "#FF6347",
    "goldenrod": "#DAA520",
    "darkgreen": "#006400",
    "plum": "#DDA0DD",
    "tan": "#D2B48C",
    "lightcoral": "#F08080",
    "orchid": "#DA70D6",
    "sienna": "#A0522D",
    "beige": "#F5F5DC",
    "indigo": "#4B0082",
    "khaki": "#F0E68C",
    "darkkhaki": "#BDB76B",
    "steelblue": "#4682B4",
    "scarlet": "#BB0000",
    "gray": "#666666",
    "gold": "#FFD700"
}

# Available font sizes for the web page
FONT_SIZE_MAP = {
    "tiny": "10px",
    "small": "12px",
    "normal": "14px",
    "medium": "15px",
    "large": "18px",
    "extra_large": "20px",
    "huge": "24px",
    "gigantic": "28px"
}

# https://fonts.google.com/
FONT_CHOICES = {
    "default": "Arial, sans-serif",             # Web-safe font
    "roboto": "'Roboto', sans-serif",           # Google Font
    "lato": "'Lato', sans-serif",               # Google Font
    "open_sans": "'Open Sans', sans-serif",     # Google Font
    "merriweather": "'Merriweather', serif",    # Google Font
    "raleway": "'Raleway', sans-serif",         # Google Font
    "oswald": "'Oswald', sans-serif",           # Google Font
    "josefin_sans": "'Josefin Sans', sans-serif", # Google Font
    "playfair_display": "'Playfair Display', serif", # Google Font
    "ubuntu": "'Ubuntu', sans-serif",           # Google Font
    "muli": "'Muli', sans-serif",               # Google Font
    "zcool_xiao_wei": "'ZCOOL XiaoWei', serif", # Google Font
    "fjalla_one": "'Fjalla One', sans-serif",   # Google Font
    "arvo": "'Arvo', serif",                    # Google Font
    "poppins": "'Poppins', sans-serif",         # Google Font
    "montserrat": "'Montserrat', sans-serif",   # Google Font
    "pacifico": "'Pacifico', cursive",          # Google Font
    "dancing_script": "'Dancing Script', cursive", # Google Font
    "lobster": "'Lobster', cursive"              # Google Font
}

FONT_LINK_MAP = {
    "default": None,  # Web-safe font does not require a link
    "roboto": "https://fonts.googleapis.com/css2?family=Roboto:wght@400&display=swap",
    "lato": "https://fonts.googleapis.com/css2?family=Lato:wght@400&display=swap",
    "open_sans": "https://fonts.googleapis.com/css2?family=Open+Sans:wght@400&display=swap",
    "merriweather": "https://fonts.googleapis.com/css2?family=Merriweather:wght@400&display=swap",
    "raleway": "https://fonts.googleapis.com/css2?family=Raleway:wght@400&display=swap",
    "oswald": "https://fonts.googleapis.com/css2?family=Oswald:wght@400&display=swap",
    "josefin_sans": "https://fonts.googleapis.com/css2?family=Josefin+Sans:wght@400&display=swap",
    "playfair_display": "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400&display=swap",
    "ubuntu": "https://fonts.googleapis.com/css2?family=Ubuntu:wght@400&display=swap",
    "muli": "https://fonts.googleapis.com/css2?family=Muli:wght@400&display=swap",
    "zcool_xiao_wei": "https://fonts.googleapis.com/css2?family=ZCOOL+XiaoWei:wght@400&display=swap",
    "fjalla_one": "https://fonts.googleapis.com/css2?family=Fjalla+One:wght@400&display=swap",
    "arvo": "https://fonts.googleapis.com/css2?family=Arvo:wght@400&display=swap",
    "poppins": "https://fonts.googleapis.com/css2?family=Poppins:wght@400&display=swap",
    "montserrat": "https://fonts.googleapis.com/css2?family=Montserrat:wght@400&display=swap",
    "pacifico": "https://fonts.googleapis.com/css2?family=Pacifico:wght@400&display=swap",
    "dancing_script": "https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400&display=swap",
    "lobster": "https://fonts.googleapis.com/css2?family=Lobster:wght@400&display=swap"
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

# API Port
API_PORT = 51763

# Flask Cache Type
CACHE_TYPE = 'simple'

# Github repo URL
GITHUB_REPO_URL = "https://api.github.com/repos/samcro1967/docker-compose-ports-dump/releases/latest"