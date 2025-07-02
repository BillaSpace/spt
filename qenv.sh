#!/bin/bash

# -----------------------------
# Self-executable .env generator for DX-SPT
# Creates a .env file with all variable names empty
# -----------------------------

# Set output file
ENV_FILE=".env"

# Remove old file if exists
rm -f "$ENV_FILE"

# Create .env with empty variables
cat <<EOF > "$ENV_FILE"
API_ID=
API_HASH=
BOT_TOKEN=
DB_URL=
DB_NAME=
OWNER_ID=
SUDO_USERS=
ADMIN=
AUTH_CHATS=
START_PIC=
LOG_GROUP=
DUMP_GROUP=
BUG=
GENIUS_API=
MAINTENANCE=
EOF

# Confirm
echo ".env file created with empty values. Please edit it to add your credentials."
