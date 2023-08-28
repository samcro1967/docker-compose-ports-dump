usage: docker_ports_dump.py [-h] [-d] [-e] [-n] [-o] [-f FILE] [-v VPN_CONTAINER_NAME] [-s] [-V]

Parse Docker Compose file and extract ports.

options:
  -h, --help                   show this help message and exit.
  -d, --debug                  Print the debug info. All other arguments ignored.
  -e, --sort-by-external-port  Sort the table by External Port.
  -n, --sort-by-service-name   Sort the table by Service Name.
  -s, --show-examples          Show examples of port.mapping configuration in a docker-compose.yml file.
  -V, --version                Show version information and exit.
  -o, --output                 Generate a web page with the port mappings.

All options are mutually exclusive and cannot be used together.
DEFAULT_DOCKER_COMPOSE_FILE must be configured in dcpd_config.py