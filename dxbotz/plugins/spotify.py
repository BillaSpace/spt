from pyrogram.errors import FloodWait, Forbidden, UserIsBlocked, MessageNotModified, ChatWriteForbidden, SlowmodeWait 
from asyncio import sleep
import time
from config import AUTH_CHATS, LOGGER, LOG_GROUP, BUG
from dxbotz import Dxbotz
from pyrogram import filters, enums
from dxbotz.utils.mainhelper import parse_spotify_url, fetch_spotify_track, download_songs, thumb_down, copy, forward 
from dxbotz.utils.ytdl import getIds, ytdl_down, audio_opt
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from os import mkdir, environ, path
from shutil import rmtree
from random import randint
from mutagen import File
from mutagen.flac import FLAC, Picture
from lyricsgenius import Genius 
from pyrogram.types import Message
from pyrogram.errors.rpc_error import RPCError
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from pyrogram.errors import ChatAdminRequired
from requests import head
from requests.exceptions import MissingSchema

ADMINS = 5960968099
client = Spotify(auth_manager=SpotifyClientCredentials())
PICS = ("dxbotz/1162775.jpg dxbotz/danny-howe-bn-D2bCvpik-unsplash.jpg dxbotz/saurabh-gill-38RthwbB3nE-unsplash.jpg").split()
MAIN = bool(environ.get('MAIN', None))
genius = Genius("ChS_Qz9KzZi-g95xGpYOT6lZhg4Ky9ciZoFFGTY-hatB5Pk7HvPhir3SQInE90k7")

LOG_TEXT_P = """
ID - <code>{}</code>
Name - {}
"""

@Dxbotz.on_message(filters.incoming & filters.regex(r'https?://open.spotify.com[^\s]+') | filters.incoming & filters.regex(r'https?://spotify.link[^\s]+'), group=-2)
async def spotify_dl(Dxbotz, message: Message):
    if MAIN:
        await message.reply_text(f"Bot Is Under Maintenance ⚠️")
        return
    link = message.matches[0].group(0)
    if "https://spotify.link" in link:
        link = head(link).headers['location']
    if "https://www.deezer.com" in link:
        return
    if "https://youtu.be" in link:
        return await message.reply("301: Use @billamusic2_bot Instead Of Me 🚫")
    try:
        parsed_item = await parse_spotify_url(link)
        item_type, item_id = parsed_item[0], parsed_item[1]
    except Exception as e:
        cr = await message.reply("417: Not Critical, Retrying Again 🚫")
        await Dxbotz.send_message(BUG, f"Private r: Unsupported [URI]({link}) Not critical {message.chat.id} {message.from_user.id} {message.from_user.mention}")
        try:
            link = head(link).headers['location']
            parsed_item = await parse_spotify_url(link)
            item_type, item_id = parsed_item[0], parsed_item[1]
        except Exception:
            await Dxbotz.send_message(BUG, f"Private r: Unsupported [URI]({link}) Failed twice {message.chat.id} {message.from_user.id} {message.from_user.mention}")
            return await cr.edit(f"501: This URI Is Not Supported ⚠")
    if message.text.startswith("/thumb"):
        try:
            await Dxbotz.send_message(BUG, f"Thumb download requested from {message.from_user.mention}")
            if item_type == "track":
                item = client.track(track_id=item_id)
                alb = client.album(album_id=item['album']['id'])
                await message.reply_document(alb['images'][0]['url'])
            elif item_type == "playlist":
                play = client.playlist(playlist_id=item_id)
                await message.reply_document(play['images'][0]['url'])
            elif item_type == "album":
                alb = client.album(album_id=item_id)
                await message.reply_document(alb['images'][0]['url'])
            elif item_type == "artist":
                art = client.artist(item_id)
                await message.reply_document(art['images'][0]['url'])
        except Exception as e:
            await message.reply("404: sorry, thumbnail download is not available for this track 😔")
            await Dxbotz.send_message(BUG, f"thumb 400 {e}")
        return 
    if message.text.startswith("/preview"):
        if item_type == "track":
            try:
                await Dxbotz.send_message(BUG, f"Preview download requested from {message.from_user.mention}")
                item = client.track(track_id=item_id)
                await message.reply_audio(f"{item.get('preview_url')}")
            except Exception as e:
                await message.reply("404: sorry, audio preview is not available for this track 😔")
                await Dxbotz.send_message(BUG, e)
            return 
    try: 
        if item_type in ["https:", "http:"]:
            cr = await message.reply("417: Not Critical, Retrying Again 🚫")
            await sleep(1)
            return await cr.edit(f"501: This URI Is Not Supported ⚠")
    except Exception as e:
        await Dxbotz.send_message(BUG, f"Private r: Unsupported http [URI]({link}) Failed twice {message.chat.id} {message.from_user.id} {message.from_user.mention}")
    u = message.from_user.id
    randomdir = f"/tmp/{str(randint(1, 100000000))}"
    mkdir(randomdir)
    try:
        m = await message.reply_text(f"⏳")
        await message.reply_chat_action(enums.ChatAction.TYPING)
    except ChatWriteForbidden:
        chat = message.chat.id
        await Dxbotz.leave_chat(chat)
        k = await Dxbotz.send_message(-1002030443562, f"{chat} {message.chat.username or message.from_user.id}")
        await k.pin()
        sp = f"I have left from {chat} reason: I Am Not Admin "
        await Dxbotz.send_message(message.from_user.id, f"{sp}")
    try:
        if item_type in ["show", "episode"]:
            items = await getIds(link)
            for item in items:
                await message.reply_chat_action(enums.ChatAction.UPLOAD_PHOTO)
                await sleep(0.9)
                await message.reply_photo(item[5], caption=f"✔️ Episode Name: `{item[3]}`\n🕔 Duration: {item[4]//60}:{item[4]%60}")
                await message.reply_text(f"sorry we removed support of episode 😔 pls send other types album/playlist/track")
       
        elif item_type == "track":
            song = await fetch_spotify_track(client, item_id)
            try:
                item = client.track(track_id=item_id)
                await message.reply_photo(item['album']['images'][0]['url'], caption=f"🎧 Title: `{song['name']}`\n🎤 Artist: `{song['artist']}`\n💽 Album: `{song['album']}`\n🗓 Release Year: `{song['year']}`\n� neighbour️Is Local: `{item['is_local']}`\n🌐 ISRC: `{item['external_ids']['isrc']}`\n\n[IMAGE]({item['album']['images'][0]['url']})\nTrack id: `{song['deezer_id']}`")
            except Exception:
                await message.reply_photo(song.get('cover'), caption=f"🎧 Title: `{song['name']}`\n🎤 Artist: `{song['artist']}`\n💽 Album: `{song['album']}`\n🗓 Release Year: `{song['year']}`\n\n[IMAGE]({song.get('cover')})\nTrack id: `{song['deezer_id']}`")
            try:
                path = await download_songs(item, randomdir)
            except Exception as e:
                await Dxbotz.send_message(BUG, f"Download failed for {song.get('name')} - {song.get('artist')}: {e}")
                await message.reply_text(f"[{song.get('name')} - {song.get('artist')}](https://open.spotify.com/track/{song.get('deezer_id')}) Track Not Found ⚠️")
                return
            thumbnail = await thumb_down(item['album']['images'][0]['url'], song.get('deezer_id'))
            try:
                audio = FLAC(path)
                audio["TITLE"] = f"{song.get('name')}"
                audio["ORIGINALYEAR"] = song.get('year')
                audio["YEAR_OF_RELEASE"] = song.get('year')
                audio["SOURCE"] = "https://t.me/BillaDLbot"
                audio["GEEK_SCORE"] = "9"
                audio["ARTIST"] = song.get('artist')
                audio["ALBUM"] = song.get('album')
                audio["DATE"] = song.get('year')
                audio["DISCNUMBER"] = f"{item['disc_number']}"
                audio["TRACKNUMBER"] = f"{item['track_number']}"
                try:
                    audio["ISRC"] = item['external_ids']['isrc']
                except:
                    pass
                try:
                    songGenius = genius.search_song(song.get('name'), song.get('artist'))
                    audio["LYRICS"] = songGenius.lyrics
                except:
                    pass
                audio.save()
                audi = File(path)
                image = Picture()
                image.type = 3
                mime = 'image/jpeg' if thumbnail.endswith('jpg') else 'image/png'
                image.desc = 'front cover'
                with open(thumbnail, 'rb') as f:
                    image.data = f.read()
                audi.add_picture(image)
                audi.save()
            except:
                pass
            try:
                await message.reply_chat_action(enums.ChatAction.UPLOAD_AUDIO)
                AForCopy = await message.reply_audio(path, performer=song.get('artist'), title=f"{song.get('name')} - {song.get('artist')}", caption=f"[{song.get('name')}](https://open.spotify.com/track/{song.get('deezer_id')}) | {song.get('album')} - {song.get('artist')}", thumb=thumbnail, parse_mode=enums.ParseMode.MARKDOWN, quote=True)
                if LOG_GROUP:
                    await forward(AForCopy, AForCopy)
            except Exception as e:
                await Dxbotz.send_message(BUG, f"Upload failed for {song.get('name')} - {song.get('artist')}: {e}")
                await message.reply_text(f"[{song.get('name')} - {song.get('artist')}](https://open.spotify.com/track/{song.get('deezer_id')}) Track Not Found ⚠️")
            await m.delete()

        elif item_type == "playlist":
            play = client.playlist(playlist_id=item_id)
            tracks = client.playlist_items(playlist_id=item_id, additional_types=['track'], offset=0, market=None)
            total_tracks = tracks.get('total')
            track_no = 1
            try:
                PForCopy = await message.reply_photo(play['images'][0]['url'], caption=f"▶️ Playlist: {play['name']}\n📝 Description: {play['description']}\n👤 Owner: {play['owner']['display_name']}\n❤️ Followers: {play['followers']['total']}\n🔢 Total Tracks: {play['tracks']['total']}\n\n[IMAGE]({play['images'][0]['url']})\n{play['uri']}")
            except Exception as e:
                PForCopy = await message.reply(f"▶️ Playlist: {play['name']}\n📝 Description: {play['description']}\n👤 Owner: {play['owner']['display_name']}\n❤️ Followers: {play['followers']['total']}\n🔢 Total Tracks: {play['tracks']['total']}\n\n[IMAGE]({play['images'][0]['url']})\n{play['uri']}")
                await message.reply("are you sure it's a valid playlist 🤨?")
            for track in tracks['items']:
                song = await fetch_spotify_track(client, track.get('track').get('id'))
                item = client.track(track_id=track['track']['id'])
                try:
                    path = await download_songs(item, randomdir)
                except Exception as e:
                    await Dxbotz.send_message(BUG, f"Download failed for {song.get('name')} - {song.get('artist')}: {e}")
                    await message.reply_text(f"[{song.get('name')} - {song.get('artist')}](https://open.spotify.com/track/{song.get('deezer_id')}) Track Not Found ⚠️")
                    continue
                thumbnail = await thumb_down(song.get('cover'), song.get('deezer_id'))
                try:
                    audio = FLAC(path)
                    audio["TITLE"] = f"{song.get('name')}"
                    audio["ORIGINALYEAR"] = song.get('year')
                    audio["YEAR_OF_RELEASE"] = song.get('year')
                    audio["SOURCE"] = "https://t.me/BillaDLbot"
                    audio["GEEK_SCORE"] = "9"
                    audio["ARTIST"] = song.get('artist')
                    audio["ALBUM"] = song.get('album')
                    audio["DATE"] = song.get('year')
                    audio["discnumber"] = f"{item['disc_number']}"
                    audio["tracknumber"] = f"{item['track_number']}"
                    try:
                        audio["ISRC"] = item['external_ids']['isrc']
                    except:
                        pass
                    try:
                        songGenius = genius.search_song(song.get('name'), song.get('artist'))
                        audio["LYRICS"] = songGenius.lyrics
                    except:
                        pass
                    audio.save()
                    audi = File(path)
                    image = Picture()
                    image.type = 3
                    mime = 'image/jpeg' if thumbnail.endswith('jpg') else 'image/png'
                    image.desc = 'front cover'
                    with open(thumbnail, 'rb') as f:
                        image.data = f.read()
                    audi.add_picture(image)
                    audi.save()
                except:
                    pass
                try:
                    await message.reply_chat_action(enums.ChatAction.UPLOAD_AUDIO)
                    AForCopy = await message.reply_audio(path, performer=song.get('artist'), title=f"{song.get('name')} - {song.get('artist')}", caption=f"[{song.get('name')}](https://open.spotify.com/track/{song.get('deezer_id')}) | {song.get('album')} - {song.get('artist')}", thumb=thumbnail, parse_mode=enums.ParseMode.MARKDOWN, quote=True)
                    if LOG_GROUP:
                        await forward(AForCopy, AForCopy)
                except Exception as e:
                    await Dxbotz.send_message(BUG, f"Upload failed for {song.get('name')} - {song.get('artist')}: {e}")
                    await message.reply_text(f"[{song.get('name')} - {song.get('artist')}](https://open.spotify.com/track/{song.get('deezer_id')}) Track Not Found ⚠️")
                track_no += 1
            await m.delete()

        elif item_type == "album":
            alb = client.album(album_id=item_id)
            try:
                PForCopy = await message.reply_photo(alb['images'][0]['url'], caption=f"💽 Album: {alb['name']}\n👥 Artists: {alb['artists'][0]['name']}\n🎧 Total tracks: {alb['total_tracks']}\n🗂 Category: {alb['album_type']}\n📆 Published on: {alb['release_date']}\n\n[IMAGE]({alb['images'][0]['url']})\n{alb['uri']}")
            except Exception as e:
                PForCopy = await message.reply(f"💽 Album: {alb['name']}\n👥 Artists: {alb['artists'][0]['name']}\n🎧 Total tracks: {alb['total_tracks']}\n🗂 Category: {alb['album_type']}\n📆 Published on: {alb['release_date']}\n\n[IMAGE]({alb['images'][0]['url']})\n{alb['uri']}")
            for track in alb['tracks']['items']:
                item = client.track(track_id=track['id'])
                song = await fetch_spotify_track(client, track.get('id'))
                try:
                    path = await download_songs(item, randomdir)
                except Exception as e:
                    await Dxbotz.send_message(BUG, f"Download failed for {song.get('name')} - {song.get('artist')}: {e}")
                    await message.reply_text(f"[{song.get('name')} - {song.get('artist')}](https://open.spotify.com/track/{song.get('deezer_id')}) Track Not Found ⚠️")
                    continue
                thumbnail = await thumb_down(song.get('cover'), song.get('deezer_id'))
                try:
                    audio = FLAC(path)
                    audio["TITLE"] = f"{song.get('name')}"
                    audio["ORIGINALYEAR"] = song.get('year')
                    audio["YEAR_OF_RELEASE"] = song.get('year')
                    audio["SOURCE"] = "https://t.me/BillaDLbot"
                    audio["GEEK_SCORE"] = "9"
                    audio["ARTIST"] = song.get('artist')
                    audio["ALBUM"] = song.get('album')
                    audio["DATE"] = song.get('year')
                    audio["discnumber"] = f"{track['disc_number']}"
                    audio["tracknumber"] = f"{track['track_number']}"
                    try:
                        audio["ISRC"] = track['external_ids']['isrc']
                    except:
                        pass
                    try:
                        songGenius = genius.search_song(song.get('name'), song.get('artist'))
                        audio["LYRICS"] = songGenius.lyrics
                    except:
                        pass
                    audio.save()
                    audi = File(path)
                    image = Picture()
                    image.type = 3
                    mime = 'image/jpeg' if thumbnail.endswith('jpg') else 'image/png'
                    image.desc = 'front cover'
                    with open(thumbnail, 'rb') as f:
                        image.data = f.read()
                    audi.add_picture(image)
                    audi.save()
                except:
                    pass
                try:
                    await message.reply_chat_action(enums.ChatAction.UPLOAD_AUDIO)
                    AForCopy = await message.reply_audio(path, performer=song.get('artist'), title=f"{song.get('name')} - {song.get('artist')}", caption=f"[{song.get('name')}](https://open.spotify.com/track/{song.get('deezer_id')}) | {song.get('album')} - {song.get('artist')}", thumb=thumbnail, parse_mode=enums.ParseMode.MARKDOWN, quote=True)
                    if LOG_GROUP:
                        await forward(AForCopy, AForCopy)
                except Exception as e:
                    await Dxbotz.send_message(BUG, f"Upload failed for {song.get('name')} - {song.get('artist')}: {e}")
                    await message.reply_text(f"[{song.get('name')} - {song.get('artist')}](https://open.spotify.com/track/{song.get('deezer_id')}) Track Not Found ⚠️")
            await m.delete()

    except MissingSchema:
        await message.reply("400: Are You Sure It's valid URL🤨?")
    except RPCError:
        await message.reply(f"500: telegram says 500 error, so please try again later.❣️")
    except ChatWriteForbidden:
        chat = message.chat.id
        try:
            await Dxbotz.leave_chat(chat)
            k = await Dxbotz.send_message(-1002030443562, f"{chat} {message.chat.username or message.from_user.id}")
            await k.pin()
            sp = f"I have left from {chat} reason: I Am Not Admin "
            await Dxbotz.send_message(message.from_user.id, f"{sp}")
        except:
            pass
    except UserIsBlocked:
        K = await Dxbotz.send_message(BUG, f"private {message.chat.id} {message.from_user.id} {message.from_user.mention}")
        await K.pin()
    except IOError:
        K = await Dxbotz.send_message(BUG, f"Private r: socket {message.chat.id} {message.from_user.id} {message.from_user.mention}")
        await K.pin()
    except (FileNotFoundError, OSError):
        await message.reply('Sorry, We Are Unable To Procced It 🤕❣️')
    except BrokenPipeError:
        K = await Dxbotz.send_message(BUG, f"private r: broken {message.chat.id} {message.from_user.id} {message.from_user.mention}")
    except Forbidden:
        await message.reply_text(f"Dude check whether I have enough rights😎⚠️")
    except FloodofuodWait as e:
        await sleep(e.value)
        await message.reply_text(f"420: Telegram says: [420 FLOOD_WAIT_X] - A wait of {e.value} seconds is required !")
    except SlowmodeWait as e:
        await sleep(e.value)
    except Exception as e:
        await Dxbotz.send_message(BUG, f"Final pv {e}")
        await message.reply('503: Sorry, We Are Unable To Procced It 🤕❣️')
    finally:
        try:
            rmtree(randomdir)
        except:
            pass
