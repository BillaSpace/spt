#!/bin/bash

# -----------------------------
# Self-executable .env generator for DX-SPT
# Creates a .env file with all variable names empty
# -----------------------------

ENV_FILE=".env"

# Warn if .env already exists
if [ -f "$ENV_FILE" ]; then
  echo "⚠️  $ENV_FILE already exists. Overwriting..."
  sleep 1
  rm -f "$ENV_FILE"
fi

# Create new .env with all variables
cat <<EOF > "$ENV_FILE"
# Auto-generated .env file for DX-SPT

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

# Make sure it's readable/writable
chmod 600 "$ENV_FILE"

# Done
echo "✅ .env file created successfully with empty values."
echo "➡️  Edit the file to add your values: vi .env"
