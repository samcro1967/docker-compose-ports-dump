# Table of Contents
- [Summary](#summary)
- [Features](#features)
- [Current Known Issues](#current-known-issues)
- [Installation](#installation)
- [Local Usage Instructions](#local-usage-instructions)
- [To DO](#to-do)
- [License](#license)
- [Acknowledgements](#acknowledgements)

# **Summary**
This script parses a docker-compose.yml file(s) and dumps all assigned ports into a table and displays them in a terminal.  It defaults to sort by the order services are defined in docker-compose.yml.  It also has options to sort by external ports or by container names.  If you have containers that are attached to a VPN container, you can also have those mapped as well.

It can also generate a web page.  The web page must be run from a web server and viewed via http ot https as it includes JavaScript.  The web page also contains view of all services mapped to host networking as well as the info and debug logs.

The script does not change the existing file and only needs read access to your docker-compose.yml file.

This was developed on Ubuntu 22.04 running Python 3.10.6.  Use at your own risk.  This comes with no warranty or guarantees.

# **Features**

[Table of Contents](#table-of-contents)

* Collect and display the following either in the terminal or on a web page
	* All external and internal port definitons for services in docker-compose.yml
	* Ports mapped to a VPN container
* Additionally display the following on the web page
	* Containers attached to host networking
	* info and debug logs
	* dcpd debug information
	* dcpd configuration file
	* Stastics page
* Export of all data from the web page
* Export all support files into redacted and password protected zip file
* Supports one or more docker-compose files

# **Current Known Issues**

[Table of Contents](#table-of-contents)

* Global search and column filters - Searching external and internal port for 80 will return 80 and 7801 as expected.  However, it will also return 8405.
* Does not work behind an https proxy

# **Installation**

[Table of Contents](#table-of-contents)

## **Docker**

### Run this command to generate your own random API_KEY

```
cat /dev/urandom | tr -dc 'a-zA-Z0-9' | head -c 24 ; echo
```

### **Docker Compose**
```
  dcpd:
    hostname: dcpd
    image: ghcr.io/samcro1967/docker_compose_ports_dump:latest
    container_name: dcpd
    environment:
      - TZ=${TZ}
      - PUID=1000
      - PGID=1000
      - CRON_SCHEDULE=*/15 * * * *
      - DOCKER_COMPOSE_FILE_PATHS="/compose-files/docker-compose.yml,/app/compose-files/docker-compose_test.yml"
      - DEFAULT_VPN_CONTAINER_NAME=your_vpn_container_name #Optional
      - DEFAULT_DCPD_USERNAME=your_user_name #Optional
      - DEFAULT_DCPD_PASSWORD=your_user_password #Optional
      - REDACTED_ZIP_FILE_PASSWORD=P@55w0rd #Optional
      - API_KEY=your_random_api_key
    ports:
      - "80:80"
      - "81:81"
    volumes:
      # root of folder where all docker compose folder reside
      - /path/to/compose/files:/compose-files
    healthcheck:
      test: /app/healthcheck.sh
      interval: 60s
      timeout: 10s
      retries: 3
      start_period: 10s
```
### **Docker Run**
```
docker run \
  --hostname dcpd \
  --name dcpd \
  -e TZ=${TZ} \
  -e PUID=1000 \
  -e PGID=1000 \
  -e CRON_SCHEDULE='*/15 * * * *' \
  -e DOCKER_COMPOSE_FILE_PATHS="/compose-files/docker-compose.yml,/compose-files/docker-compose_test.yml" \
  -e DEFAULT_VPN_CONTAINER_NAME=your_vpn_container_name \
  -e DEFAULT_DCPD_USERNAME=your_user_name \
  -e DEFAULT_DCPD_PASSWORD=your_user_password \
  -e REDACTED_ZIP_FILE_PASSWORD=P@55w0rd \
  -e API_KEY=your_random_api_key \
  -p 80:80 \
  -p 81:81 \
  -v /path/to/compose/files:/compose-files \
  --health-cmd="/app/healthcheck.sh" \
  --health-interval=60s \
  --health-timeout=10s \
  --health-retries=3 \
  --health-start-period=10s \
  ghcr.io/samcro1967/docker_compose_ports_dump:latest
```
Launch your browser and go to http://ipaddress:80/dcpd
```
If you did not change the user name and password, here are the defaults:
Default user name: dcpd_admin
Default user password: P@55w0rd
```

# **Local Usage Instructions**

[Table of Contents](#table-of-contents)

## **For help:**

docker exec -it dcpd bash -c 'cd /app/src && ./dcpd.py -h'

[help.md](./docs/help.md)

## **port.mapping(s) example config**

docker exec -it dcpd bash -c 'cd /app/src && ./dcpd.py -s'

[examples.md](./docs/examples.md)

## **Terminal output example:**

docker exec -it dcpd bash -c 'cd /app/src && ./dcpd.py'

![server_info_table](./docs/server_info_table.png)

## **Web Page Output Example:** 

docker exec -it dcpd bash -c 'cd /app/src && ./dcpd.py -o'

Launch your browser and go to http://ipaddress:80/dcpd
```
Default user name: dcpd_admin
Default user password: P@55w0rd
```
![service_info_web](./docs/service_info_web.png)

# To Do

[Table of Contents](#table-of-contents)

- ✅ Support multiple docker-compose.yml files.
- ❌ Auto scan a directory and subdirectories for docker-compose.yml files.
- 🔲 Investigate arm64 image.
- 🔲 Investigate supporting behind an https proxy.

Legend
- ✅ This task is complete.
- ❌ This task is not being pursued.
- 🔲 This task is yet to be done.
- 🔜 This task is in progress.

# **License**

[Table of Contents](#table-of-contents)

This project is licensed under the terms of the MIT license. See the [LICENSE](LICENSE) file for details.

# **Acknowledgements**

[Table of Contents](#table-of-contents)

This project makes use of the following third-party software:

- **Caddy**: An open-source web server with automatic HTTPS. Licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). More information can be found at the [Caddy Official Website](https://caddyserver.com/) or the [Caddy GitHub Repository](https://github.com/caddyserver/caddy).

- **jQuery**: A fast, small, and feature-rich JavaScript library. Licensed under the [MIT License](https://opensource.org/licenses/MIT). More information and source code can be found on the [jQuery Official Website](https://jquery.com/).

- **jquery.tablesorter**: A jQuery plugin for turning a standard HTML table with THEAD and TBODY tags into a sortable table without refreshing the page. Licensed under the [MIT License](https://opensource.org/licenses/MIT). More details and source code are available at the [jquery.tablesorter GitHub Repository](https://mottie.github.io/tablesorter/docs/).

- **delete-untagged-ghcr-action**: This action deletes untagged images from the GitHub Container Registry. Used under [MIT License](https://github.com/Chizkiyahu/delete-untagged-ghcr-action/blob/main/LICENSE) (link to the license might change based on the repository structure). More details and source code are available at the [delete-untagged-ghcr-action GitHub Repository](https://github.com/Chizkiyahu/delete-untagged-ghcr-action).