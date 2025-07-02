# Copyright (C) 2024 DX-MODS
# Licensed under the AGPL-3.0 License;
# Author: ZIYAN
# Donate: https://www.buymeacoffee.com/ziyankp

import os
import sys
import re
import json
import asyncio
from collections import defaultdict
from typing import List, Dict, Union
import logging

from dotenv import load_dotenv
from pyrogram import Client

# Load environment variables from .env
load_dotenv()

# Logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

# Required ENV variables
try:
    API_ID = int(os.environ["API_ID"])
    API_HASH = os.environ["API_HASH"]
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    DB_URL = os.environ["DB_URL"]
    DB_NAME = os.environ["DB_NAME"]
    OWNER_ID = int(os.environ["OWNER_ID"])
    ADMIN = int(os.environ["ADMIN"])
    START_PIC = os.environ["START_PIC"]
except KeyError as e:
    LOGGER.error(f"❌ Missing required environment variable: {e}")
    sys.exit(1)

# Optional: SUDO_USERS
SUDO_USERS = os.environ.get("SUDO_USERS", str(OWNER_ID)).split()
SUDO_USERS = [int(x) for x in SUDO_USERS if x.strip().isdigit()]
if OWNER_ID not in SUDO_USERS:
    SUDO_USERS.append(OWNER_ID)

# Optional: AUTH_CHATS
AUTH_CHATS = os.environ.get("AUTH_CHATS", "").split()
AUTH_CHATS = [int(x) for x in AUTH_CHATS if x.strip().lstrip("-").isdigit()]

# Optional: LOG_GROUP
LOG_GROUP = os.environ.get("LOG_GROUP")
LOG_GROUP = int(LOG_GROUP) if LOG_GROUP and LOG_GROUP.lstrip("-").isdigit() else None

# Optional: DUMP_GROUP
DUMP_GROUP = os.environ.get("DUMP_GROUP")
DUMP_GROUP = int(DUMP_GROUP) if DUMP_GROUP and DUMP_GROUP.lstrip("-").isdigit() else None

# Optional: BUG
BUG = os.environ.get("BUG")
BUG = int(BUG) if BUG and BUG.lstrip("-").isdigit() else None

# Optional: Genius API
GENIUS_API = os.environ.get("GENIUS_API", None)

# Optional: Maintenance mode
MAINTENANCE = os.environ.get("MAINTENANCE", "false").lower() == "true"
