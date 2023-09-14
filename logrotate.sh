#!/bin/bash

# Add a timestamp at the beginning
echo "Logrotate script started at: $(date '+%Y-%m-%d %H:%M:%S')"

# Path to the logrotate status file
LOGROTATE_STATUS_FILE="/var/lib/logrotate.status"

# Path to the logrotate lock file (this path may vary)
LOGROTATE_LOCK_FILE="/var/lib/logrotate.status.lock"

# Path to the logrotate configuration
LOGROTATE_CONFIG="/etc/logrotate.d/dcpd_cron_logrotate.conf"

# Check if logrotate is running
if pgrep -x "logrotate" > /dev/null
then
    echo "Logrotate is currently running. Exiting script."
    exit 1
else
    echo "Logrotate is not running."

    # Check if the lock file exists
    if [ -f "$LOGROTATE_LOCK_FILE" ]; then
        echo "Logrotate lock file found."

        # Optionally, you could check the lock file's age and remove it only if it's old enough
        # This prevents removing the lock file if logrotate has just started on another process
        # FIND_OLD_LOCK=$(find "$LOGROTATE_LOCK_FILE" -mmin +5)

        # if [ -n "$FIND_OLD_LOCK" ]; then
        echo "Removing logrotate lock file."
        rm -f "$LOGROTATE_LOCK_FILE"
        # else
        #     echo "Lock file is not old enough to be considered stuck. Exiting script."
        #     exit 1
        # fi
    fi

    # Run logrotate
    /usr/sbin/logrotate "$LOGROTATE_CONFIG" --state "$LOGROTATE_STATUS_FILE" --verbose
    LOGROTATE_EXIT_CODE=$?

    if [ $LOGROTATE_EXIT_CODE -ne 0 ]; then
        echo "Logrotate exited with an error code: $LOGROTATE_EXIT_CODE"
        exit 1
    else
        echo "Logrotate ran successfully."
    fi
fi