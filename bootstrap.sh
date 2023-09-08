#!/bin/bash
# bootstrap.sh

# -------------------------------------------------------------------------
#*** Setup scrit environment ***#

# Enable debugging mode
# set -x

exec > >(tee -a /app/data/dcpd_bootstrap.log) 2>&1

trap 'echo "Script exited with code: $?"' EXIT

# ecgo branding to container logs
cat /app/branding
# -------------------------------------------------------------------------
#*** Copy example config file to config directory on first run only ***#

if [ -f "/app/config/dcpd_config_example.py" ]; then
    mv /app/config/dcpd_config_example.py /app/config/dcpd_config.py
    echo "Renamed /app/dcpd_config_example.py to /app/config/dcpd_config.py"
else
    echo "/app/dcpd_config_example.py does not exist, skipping rename"
fi

# -------------------------------------------------------------------------
#*** Update config.py with values from DOCKER_COMPOSE_FILE_PATHS ***#

# Check if DOCKER_COMPOSE_FILE_PATHS environment variable is set
if [ -n "$DOCKER_COMPOSE_FILE_PATHS" ]; then
	# Remove the surrounding quotes from the environment variable
	DOCKER_COMPOSE_FILE_PATHS=$(echo "$DOCKER_COMPOSE_FILE_PATHS" | tr -d '"')

	# Debugging line: Print the DOCKER_COMPOSE_FILE_PATHS variable
	echo "DOCKER_COMPOSE_FILE_PATHS: $DOCKER_COMPOSE_FILE_PATHS"

	# Convert the paths from the environment variable into the desired format
	FORMATTED_PATHS=$(echo "$DOCKER_COMPOSE_FILE_PATHS" | awk 'BEGIN{FS=","; OFS="\",\n    \""} {for (i=1; i<=NF; i++) print "    \"" $i "\", "}')

	# Debugging line: Print the FORMATTED_PATHS variable
	echo "FORMATTED_PATHS: $FORMATTED_PATHS"

	# Save the formatted paths into a temporary file
	echo "$FORMATTED_PATHS" > /tmp/formatted_paths.tmp

	# Remove the placeholder lines from the config file
	sed -i "/\"\/path\/to\/your\/docker-compose/d" /app/config/dcpd_config.py

	# Insert the new paths into the config file
	sed -i "/DEFAULT_DOCKER_COMPOSE_FILE = \[/r /tmp/formatted_paths.tmp" /app/config/dcpd_config.py

	# Clean up the temporary file
	rm /tmp/formatted_paths.tmp
	
	echo "Updated dcpd_config.py with value(s) from DEFAULT_DOCKER_COMPOSE_FILE"
fi

# -------------------------------------------------------------------------
#*** Update config.py with value from DEFAULT_VPN_CONTAINER_NAME ***#

# Check if DEFAULT_VPN_CONTAINER_NAME environment variable is set
if [ -n "$DEFAULT_VPN_CONTAINER_NAME" ]; then
    # Remove the surrounding quotes from the environment variable
    DEFAULT_VPN_CONTAINER_NAME=$(echo "$DEFAULT_VPN_CONTAINER_NAME" | tr -d '"')

    # Debugging line: Print the DEFAULT_VPN_CONTAINER_NAME variable
    echo "DEFAULT_VPN_CONTAINER_NAME: $DEFAULT_VPN_CONTAINER_NAME"

    # Update the value in the config file
    sed -i "s/DEFAULT_VPN_CONTAINER_NAME = .*/DEFAULT_VPN_CONTAINER_NAME = \"$DEFAULT_VPN_CONTAINER_NAME\"/" /app/config/dcpd_config.py
    echo "Updated DEFAULT_VPN_CONTAINER_NAME in dcpd_config.py"
else
    echo "DEFAULT_VPN_CONTAINER_NAME environment variable is not set or empty"
fi

# -------------------------------------------------------------------------
#*** Update config.py with value from API_KEY ***#


# Check if API_KEY is set or not
if [ -z "$API_KEY" ]; then
    echo "API_KEY environment variable is not set or empty. Skipping replacement."
else
    # Escape special characters to make them compatible with sed's substitution
    escaped_api_key=$(echo "$API_KEY" | sed -e 's/[]\/$*.^[]/\\&/g')

    # Use sed to replace the value in dcpd_config.py
    sed -i "s/API_KEY = \"[^\"]*\"/API_KEY = \"$escaped_api_key\"/" /app/config/dcpd_config.py

    if [ $? -eq 0 ]; then
        echo "API_KEY updated successfully"
    else
        echo "Error updating API_KEY"
    fi
fi

# -------------------------------------------------------------------------
#*** Update config.py with value from API_PORT ***#

# Check if API_PORT environment variable is set
if [ -n "$API_PORT" ]; then
    # Use sed to replace the value in dcpd_config.py
    sed -i "s/API_PORT = [0-9]\+/API_PORT = $API_PORT/g" /app/config/dcpd_config.py
    echo "API_PORT updated in dcpd_config.py to $API_PORT"
else
    echo "API_PORT environment variable is not set or empty"
fi

# -------------------------------------------------------------------------
#*** Update config.py with values for Web Page Colors ***#

# Check if DEFAULT_WEB_PAGE_BACKGROUND_COLOR environment variable is set
if [ -n "$DEFAULT_WEB_PAGE_BACKGROUND_COLOR" ]; then
    # Use sed to replace the value in dcpd_config.py
    sed -i "s/DEFAULT_WEB_PAGE_BACKGROUND_COLOR = .*/DEFAULT_WEB_PAGE_BACKGROUND_COLOR = \"$DEFAULT_WEB_PAGE_BACKGROUND_COLOR\"/" /app/config/dcpd_config.py
    echo "Updated DEFAULT_WEB_PAGE_BACKGROUND_COLOR in dcpd_config.py to $DEFAULT_WEB_PAGE_BACKGROUND_COLOR"
else
    echo "DEFAULT_WEB_PAGE_BACKGROUND_COLOR environment variable is not set or empty"
fi

# Check if DEFAULT_WEB_PAGE_ACCENT_COLOR environment variable is set
if [ -n "$DEFAULT_WEB_PAGE_ACCENT_COLOR" ]; then
    # Use sed to replace the value in dcpd_config.py
    sed -i "s/DEFAULT_WEB_PAGE_ACCENT_COLOR = .*/DEFAULT_WEB_PAGE_ACCENT_COLOR = \"$DEFAULT_WEB_PAGE_ACCENT_COLOR\"/" /app/config/dcpd_config.py
    echo "Updated DEFAULT_WEB_PAGE_ACCENT_COLOR in dcpd_config.py to $DEFAULT_WEB_PAGE_ACCENT_COLOR"
else
    echo "DEFAULT_WEB_PAGE_ACCENT_COLOR environment variable is not set or empty"
fi

# Check if DEFAULT_WEB_PAGE_TEXT_COLOR environment variable is set
if [ -n "$DEFAULT_WEB_PAGE_TEXT_COLOR" ]; then
    # Use sed to replace the value in dcpd_config.py
    sed -i "s/DEFAULT_WEB_PAGE_TEXT_COLOR = .*/DEFAULT_WEB_PAGE_TEXT_COLOR = \"$DEFAULT_WEB_PAGE_TEXT_COLOR\"/" /app/config/dcpd_config.py
    echo "Updated DEFAULT_WEB_PAGE_TEXT_COLOR in dcpd_config.py to $DEFAULT_WEB_PAGE_TEXT_COLOR"
else
    echo "DEFAULT_WEB_PAGE_TEXT_COLOR environment variable is not set or empty"
fi

# Check if DEFAULT_WEB_PAGE_FONT_NAME environment variable is set
if [ -n "$DEFAULT_WEB_PAGE_FONT_NAME" ]; then
    # Use sed to replace the value in dcpd_config.py
    sed -i "s/DEFAULT_WEB_PAGE_FONT_NAME = .*/DEFAULT_WEB_PAGE_FONT_NAME = \"$DEFAULT_WEB_PAGE_FONT_NAME\"/" /app/config/dcpd_config.py
    echo "Updated DEFAULT_WEB_PAGE_FONT_NAME in dcpd_config.py to $DEFAULT_WEB_PAGE_FONT_NAME"
else
    echo "DEFAULT_WEB_PAGE_FONT_NAME environment variable is not set or empty"
fi

# Check if DEFAULT_WEB_PAGE_FONT_SIZE environment variable is set
if [ -n "$DEFAULT_WEB_PAGE_FONT_SIZE" ]; then
    # Use sed to replace the value in dcpd_config.py
    sed -i "s/DEFAULT_WEB_PAGE_FONT_SIZE = .*/DEFAULT_WEB_PAGE_FONT_SIZE = \"$DEFAULT_WEB_PAGE_FONT_SIZE\"/" /app/config/dcpd_config.py
    echo "Updated DEFAULT_WEB_PAGE_FONT_SIZE in dcpd_config.py to $DEFAULT_WEB_PAGE_FONT_SIZE"
else
    echo "DEFAULT_WEB_PAGE_FONT_SIZE environment variable is not set or empty"
fi

# -------------------------------------------------------------------------
#*** Update dcpd_js_apidocs.js with value from API_PORT ***#

if [ -z "$API_PORT" ]; then
    echo "API_PORT environment variable is not set or empty. Skipping replacement."
else
    # Use sed to replace the value in dcpd_js_apidocs.js
    sed -i "s/:51763'/:$API_PORT'/g" /app/web/dcpd_js_constants.js

    if [ $? -eq 0 ]; then
        echo "API_PORT updated successfully"
    else
        echo "Error updating API_PORT"
    fi
fi

# -------------------------------------------------------------------------
#*** Setup ownership and permissions on /app ***#

# Check if REDACTED_ZIP_FILE_PASSWORD environment variable is set
if [ -n "$REDACTED_ZIP_FILE_PASSWORD" ]; then
    # Remove the surrounding quotes from the environment variable
    REDACTED_ZIP_FILE_PASSWORD=$(echo "$REDACTED_ZIP_FILE_PASSWORD" | tr -d '"')
    
    # Update the value in the config file
    sed -i "s/REDACTED_ZIP_FILE_PASSWORD = .*/REDACTED_ZIP_FILE_PASSWORD = \"$REDACTED_ZIP_FILE_PASSWORD\"/" /app/config/dcpd_config.py
    echo "Updated REDACTED_ZIP_FILE_PASSWORD in dcpd_config.py"
else
    echo "REDACTED_ZIP_FILE_PASSWORD environment variable is not set or empty"
fi

# -------------------------------------------------------------------------
#*** Setup caddy ***#

# Create /etc/caddy directory and move the Caddyfile only if they exist
if [ ! -d "/etc/caddy" ]; then
    mkdir /etc/caddy
    echo "/etc/caddy directory created"
fi

if [ -f "Caddyfile" ]; then
    mv /app/Caddyfile /etc/caddy/Caddyfile || { echo "Failed to move Caddyfile"; exit 1; }
    echo "Caddyfile moved from root to /etc/caddy/"
fi

# Format the Caddyfile
caddy fmt --overwrite /etc/caddy/Caddyfile

# Check if the password seems to be in hashed format (bcrypt usually starts with $2a$)
if [[ $BASIC_AUTH_PASS != \$2a\$* ]]; then
    # If not hashed, then hash it
    BASIC_AUTH_HASHED_PASS=$(caddy hash-password --plaintext "$BASIC_AUTH_PASS")
	sed -i "s|{BASIC_AUTH_USER}|$BASIC_AUTH_USER|g" /etc/caddy/Caddyfile
	sed -i "s|{BASIC_AUTH_HASHED_PASS}|$BASIC_AUTH_HASHED_PASS|g" /etc/caddy/Caddyfile

else
    # If already hashed, use as it is
    BASIC_AUTH_HASHED_PASS=$BASIC_AUTH_PASS
	echo $BASIC_AUTH_USER
	echo $BASIC_AUTH_HASHED_PASS
fi

# Create /app/data/dcpd_caddy.log and set ownership and permissions
touch /app/data/dcpd_caddy.log
chown 1000:1000 /app/data/dcpd_caddy.log
chmod 777 /app/data/dcpd_caddy.log
echo "/app/data/dcpd_caddy.log created and ownership and permissions set"

# -------------------------------------------------------------------------
#*** Setup ownership and permissions on /app ***#

chown -R 1000:1000 /app
chmod -R 777 /app
echo "Ownership and permissions set on /app"

# -------------------------------------------------------------------------
#*** Setup aliases for use with bash -l ***#

# Setup array for aliases
declare -A aliases
aliases=(
	["caddy_log"]='tail /app/data/caddy.log -n 25'
	["caddy_reload"]='caddy reload --config /etc/caddy/Caddyfile'
	["caddy_fmt"]='caddy fmt --overwrite /etc/caddy/Caddyfile'
    # ... add more aliases as needed
)
echo "alias arrary created"

# Echoing the keys and values of the array
for key in "${!aliases[@]}"; do
    echo "$key=${aliases[$key]}"
done

# Create the aliases
for key in "${!aliases[@]}"; do
    echo "alias $key='${aliases[$key]}'" >> /etc/bash.bashrc
done
echo "aliases created"

alias

# Source alaises for all users
echo 'source /etc/bash.bashrc' > /etc/profile.d/aliases.sh
chmod +x /etc/profile.d/aliases.sh
echo "aliases sourced for all users"

# -------------------------------------------------------------------------
#*** Start Gunicorn server in the background ***#

touch /app/data/dcpd_gunicorn_access.log
touch /app/data/dcpd_gunicorn_error.log
chown 1000:1000 /app/data/*.log
chmod 777 /app/data/*.log

cd /app/src
echo "Starting Gunicorn..."
nohup gunicorn dcpd_api:dcpd_api \
    --bind 0.0.0.0:$API_PORT \
    --workers 4 \
    --access-logfile '/app/data/dcpd_gunicorn_access.log' \
    --error-logfile '/app/data/dcpd_gunicorn_error.log' \
	--log-file '/app/data/dcpd_gunicorn.log' \
    > /app/data/dcpd_gunicorn.log 2>&1 &
echo "Gunicorn started with PID $!"

# -------------------------------------------------------------------------
#*** Run the main script to generate the data files and web page ***#

cd /app/src && python3 -B ./dcpd.py -o
echo "Initial run of dcpd_main.py to generate data files and web page completed"

# -------------------------------------------------------------------------
# Start caddy in the background
caddy run --config /etc/caddy/Caddyfile --adapter caddyfile &
echo "started caddy in the background"

# -------------------------------------------------------------------------
#*** Setup and start cron ***#

# Create the /etc/cron.d directory only if it doesn't exist
if [ ! -d "/etc/cron.d" ]; then
    mkdir -p /etc/cron.d/
    echo "/etc/cron.d directory created"
fi

# Create /app/data/dcpd_cron.log and set ownership and permissions
touch /app/data/dcpd_cron.log
chown 1000:1000 /app/data/dcpd_cron.log
chmod 777 /app/data/dcpd_cron.log
echo "/app/data/dcpd_cron.log created and ownership and permissions set"

# Check if the job already exists in the crontab
if ! crontab -l | grep -q "dcpd_main.py"; then
    # Write the cron schedule to crontab if not already present
    (crontab -l; echo -e "$CRON_SCHEDULE cd /app/src && python3 -B ./dcpd_main.py -o >> /app/data/dcpd_cron.log 2>&1\n$CRON_SCHEDULE sh -c \"echo ' \$(date)'\" >> /app/data/dcpd_cron.log 2>&1") | crontab -
    echo "Wrote CRON_SCHEDULE to crontab"
else
    echo "Cron job for dcpd_main.py already exists. Skipping addition."
fi

# Check the operating system to decide between cron and crond
if [ -f /etc/alpine-release ]; then
    # Alpine Linux
    CRON_CMD="crond -f"
else
    # Ubuntu or other Linux distributions
    CRON_CMD="cron -f"
fi

# Start cron in the foreground (to keep the container running)
echo "started cron"
$CRON_CMD