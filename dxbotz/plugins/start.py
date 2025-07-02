# Copyright (C) 2024 DX-MODS
# Licensed under the AGPL-3.0 License;
# Author: ZIYAN
# Donate: https://www.buymeacoffee.com/ziyankp

from asyncio import sleep
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from dxbotz.utils.txt import dx
from dxbotz.utils.database import db
from config import START_PIC


def to_smallcaps(text: str) -> str:
    # Convert basic ASCII to small caps Unicode where possible
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    small = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ" + "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
    return ''.join(small[normal.index(c)] if c in normal else c for c in text)


@Client.on_message(filters.private & filters.command(["start"]))
async def start(client, message):
    user = message.from_user
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id)

    txt = (
        f"<b>👋 ᴡʜᴀᴛ'ꜱ ᴜᴘ {user.mention}</b>\n\n"
        "<blockquote>"
        + to_smallcaps(
            "I'm a super advanced music downloader Pro-bot that supports multiple streaming platforms like "
            "Spotify, YouTube, SoundCloud, Shazam, Deezer and social platforms like Facebook, Instagram Reels/IGTV, and TikTok!"
        )
        + "</blockquote>"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🍃 𝙳𝙴𝚅𝚂", callback_data='dev')],
        [
            InlineKeyboardButton("📢 𝚄𝙿𝙳𝙰𝚃𝙴𝚂", url="https://t.me/BillaSpace"),
            InlineKeyboardButton("🍂 𝚂𝚄𝙿𝙿𝙾𝚁𝚃", url="https://t.me/BillaCore")
        ],
        [
            InlineKeyboardButton("🍃 𝙰𝙱𝙾𝚄𝚃", callback_data='about'),
            InlineKeyboardButton("ℹ️ 𝙷𝙴𝙻𝙿", callback_data='help')
        ]
    ])

    if START_PIC:
        await message.reply_photo(START_PIC, caption=txt, reply_markup=buttons)
    else:
        await message.reply_text(txt, reply_markup=buttons, disable_web_page_preview=True)


@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data

    if data == "start":
        txt = (
            f"<b>👋 ʜᴇʏ {query.from_user.mention}!</b>\n\n"
            "<blockquote>"
            + to_smallcaps(
                "I'm a super advanced music downloader that supports Spotify, Deezer, YouTube, JioSaavn, SoundCloud, "
                "and even Instagram, TikTok, Facebook, and more!"
            )
            + "</blockquote>\n"
            + to_smallcaps("Stay tuned on @BillaSpace for more SuperBots like me!")
        )

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("💌 𝙳𝙴𝚅𝚂", callback_data='dev')],
            [
                InlineKeyboardButton("📢 𝚄𝙿𝙳𝙰𝚃𝙴𝚂", url="https://t.me/BillaSpace"),
                InlineKeyboardButton("🍂 𝚂𝚄𝙿𝙿𝙾𝚁𝚃", url="https://t.me/BillaCore")
            ],
            [
                InlineKeyboardButton("🍃 𝙰𝙱𝙾𝚄𝚃", callback_data='about'),
                InlineKeyboardButton("ℹ️ 𝙷𝙴𝙻𝙿", callback_data='help')
            ]
        ])
        await query.message.edit_text(txt, reply_markup=buttons)

    elif data == "help":
        await query.message.edit_text(
            text=dx.HELP_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("𝚂𝙾𝚄𝚁𝙲𝙴", url="https://github.com/Billa/spotidl")],
                [InlineKeyboardButton("❤ ᴄʜᴀᴛ ɢʀᴏᴜᴘ", url="https://t.me/chat_space2")],
                [
                    InlineKeyboardButton("🔒 𝙲𝙻𝙾𝚂𝙴", callback_data="close"),
                    InlineKeyboardButton("◀️ 𝙱𝙰𝙲𝙺", callback_data="start")
                ]
            ])
        )

    elif data == "about":
        await query.message.edit_text(
            text=dx.ABOUT_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("𝚂𝙾𝚄𝚁𝙲𝙴", url="https://github.com/Billa/spotidl")],
                [InlineKeyboardButton("ᴄʜᴀᴛ ɢʀᴏᴜᴘ", url="https://t.me/chat_space2")],
                [
                    InlineKeyboardButton("🔒 𝙲𝙻𝙾𝚂𝙴", callback_data="close"),
                    InlineKeyboardButton("◀️ 𝙱𝙰𝙲𝙺", callback_data="start")
                ]
            ])
        )

    elif data == "dev":
        await query.message.edit_text(
            text=dx.DEV_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("𝚂𝙾𝚄𝚁𝙲𝙴", url="https://github.com/Billa/spotidl")],
                [InlineKeyboardButton("ᴄʜᴀᴛ ɢʀᴏᴜᴘ", url="https://t.me/chat_space2")],
                [
                    InlineKeyboardButton("🔒 𝙲𝙻𝙾𝚂𝙴", callback_data="close"),
                    InlineKeyboardButton("◀️ 𝙱𝙰𝙲𝙺", callback_data="start")
                ]
            ])
        )

    elif data == "close":
        try:
            await query.message.delete()
            if query.message.reply_to_message:
                await query.message.reply_to_message.delete()
        except:
            await query.message.delete()
