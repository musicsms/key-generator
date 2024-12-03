#!/bin/sh
set -e

# Set default values for required paths if not provided
: "${KEY_STORAGE_PATH:=/app/keys}"
: "${GNUPGHOME:=/app/keys/.gnupg}"

# Export the variables so they are available to the application
export KEY_STORAGE_PATH
export GNUPGHOME

# Execute the main command
exec "$@"
