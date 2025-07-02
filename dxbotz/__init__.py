# Copyright (C) 2024 DX-MODS
# Licensed under the AGPL-3.0 License;
# Author: ZIYAN

from pyrogram import Client
import os
from os import environ, sys, mkdir, path
import logging
from config import API_ID, API_HASH, BOT_TOKEN, AUTH_CHATS

# Log setup
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)


class Dxbotz(Client):
    def __init__(self):
        name = self.__class__.__name__.lower()
        super().__init__(
            name=":memory:",
            plugins=dict(root=f"{name}/plugins"),
            workdir="./cache/",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            sleep_threshold=30,
        )

    async def start(self, *args, **kwargs):  # 🔧 Accept *args, **kwargs
        global BOT_INFO
        await super().start(*args, **kwargs)  # ✅ Forward them to base class

        BOT_INFO = await self.get_me()

        if not path.exists("/tmp/thumbnails/"):
            mkdir("/tmp/thumbnails/")

        for chat in AUTH_CHATS:
            try:
                await self.send_photo(
                    chat,
                    "https://telegra.ph/file/97bc8a091ac1b119b72e4.jpg",
                    "**SpotifyDl Started**",
                )
            except Exception as e:
                LOGGER.warning(f"Failed to notify chat {chat}: {e}")

        LOGGER.info(f"✅ Bot Started as @{BOT_INFO.username}")

    async def stop(self, *args):  # Optional args for safety
        await super().stop()
        LOGGER.info("🛑 Bot Stopped. Goodbye!")
