# Using LinuxServer.io's baseimage
FROM lsiobase/alpine:3.18

LABEL org.opencontainers.image.source https://github.com/samcro1967/docker-compose-ports-dump

# Update & install required packages and set up Docker Compose V2
RUN apk update && apk upgrade && \
    apk add --no-cache bash busybox grep lsof nano python3 py3-pip tree jq curl linux-headers docker gcc musl-dev python3-dev && \
    # Setup Docker Compose V2 plugin
    mkdir -p /root/.docker/cli-plugins/ && \
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" -o /root/.docker/cli-plugins/docker-compose && \
    chmod +x /root/.docker/cli-plugins/docker-compose && \
    # Fetch latest Caddy release version and install
    LATEST_CADDY_VERSION=$(curl -s https://api.github.com/repos/caddyserver/caddy/releases/latest | jq -r .tag_name) && \
    echo "Latest Caddy Version: ${LATEST_CADDY_VERSION}" && \
    curl -L "https://github.com/caddyserver/caddy/releases/download/${LATEST_CADDY_VERSION}/caddy_${LATEST_CADDY_VERSION#v}_linux_amd64.tar.gz" -o caddy.tar.gz && \
    tar xvf caddy.tar.gz && \
    mv caddy /usr/bin/ && \
    rm caddy.tar.gz

# Environment variables
ENV PUID=1000 \
    PGID=1000 \
    CRON_SCHEDULE="* * * * *" \
    EDITOR=nano \
    DOCKER_COMPOSE_FILE_PATHS="/path/to/docker-compose1.yml,/path/to/docker-compose2.yml"\
    DEFAULT_VPN_CONTAINER_NAME="your_vpn_container_name" \
    REDACTED_ZIP_FILE_PASSWORD="your_zip_file_password" \
    API_KEY="your_api_key" \
    BASIC_AUTH_USER=dcpd_admin \ 
    BASIC_AUTH_PASS=P@55word \
	API_PORT=51763 \
	DEFAULT_WEB_PAGE_BACKGROUND_COLOR=scarlet \
	DEFAULT_WEB_PAGE_ACCENT_COLOR=gray \
	DEFAULT_WEB_PAGE_TEXT_COLOR=white \
	DEFAULT_WEB_PAGE_FONT_NAME=roboto \
	DEFAULT_WEB_PAGE_FONT_SIZE=15px

# Expose the necessary port (app and api)
EXPOSE 8080

# Create required volumes
VOLUME ["/compose-files"]

# Set working directory
WORKDIR /app

# Copy files into the image
COPY . .

# Install pip packages
RUN pip3 install -U -r /app/requirements.txt

RUN chmod +x /app/bootstrap.sh

# Make bootstrap.sh the entrypoint
ENTRYPOINT ["bash", "/app/bootstrap.sh"]
