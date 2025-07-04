
import os
from random import randint 
from yt_dlp import YoutubeDL
from config import LOGGER, LOG_GROUP, BUG
from requests import get
from asyncio import sleep 
from asgiref.sync import sync_to_async

COOKIES_PATH = os.path.join("cookies", "cookies.txt")

@sync_to_async
def parse_deezer_url(url):
    url = get(url).url
    parsed_url = url.replace("https://www.deezer.com/", "")
    item_type = parsed_url.split("/")[1]
    item_id = parsed_url.split("/")[2].split("?")[0]
    return item_type, item_id

@sync_to_async
def parse_spotify_url(url):
    if url.startswith("spotify"):
        return url.split(":")[1]
    url = get(url).url
    parsed_url = url.replace("https://open.spotify.com/", "").split("/")
    return parsed_url[0], parsed_url[1].split("?")[0]

@sync_to_async
def thumb_down(link, deezer_id):
    thumb_path = f"/tmp/thumbnails/{deezer_id}.jpg"
    os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
    with open(thumb_path, "wb") as file:
        file.write(get(link).content)
    return thumb_path

@sync_to_async
def fetch_tracks(dz, item_type, item_id):
    songs_list = []
    offset = 0
    if item_type == 'playlist':
        get_play = dz.get_playlist(item_id)
        items = get_play.tracks
        for item in items:
            track_name = item.title
            track_artist = item.artist.name
            track_album = item.album.title
            cover = item.album.cover_xl
            thumb = item.album.cover_small
            deezer_id = item.id
            songs_list.append({
                "name": track_name,
                "artist": track_artist,
                "album": track_album,
                "playlist_num": offset + 1,
                "cover": cover,
                "deezer_id": deezer_id,
                "thumb": thumb,
                "duration": item.duration
            })
            offset += 1
            if len(items) == offset:
                break
    elif item_type == 'album':
        get_al = dz.get_album(item_id)
        track_album = get_al.title
        cover = get_al.cover_xl
        thumb = get_al.cover_small
        items = get_al.tracks
        for item in items:
            track_name = item.title
            track_artist = item.artist.name
            deezer_id = item.id
            songs_list.append({
                "name": track_name,
                "artist": track_artist,
                "album": track_album,
                "playlist_num": offset + 1,
                "cover": cover,
                "deezer_id": deezer_id,
                "thumb": thumb,
                "duration": item.duration
            })
            offset += 1
            if len(items) == offset:
                break
    elif item_type == 'track':
        get_track = dz.get_track(item_id)
        songs_list.append({
            "name": get_track.title,
            "artist": get_track.artist.name,
            "album": get_track.album.title,
            "playlist_num": offset + 1,
            "cover": get_track.album.cover_xl,
            "deezer_id": get_track.id,
            "thumb": get_track.album.cover_small,
            "duration": get_track.duration
        })
    return songs_list

@sync_to_async
def fetch_spotify_track(client, item_id):
    item = client.track(track_id=item_id)
    track_name = item.get("name")
    album_info = item.get("album")
    track_artist = ", ".join([artist['name'] for artist in item['artists']])
    if album_info:
        track_album = album_info.get('name')
        track_year = album_info.get('release_date')[:4] if album_info.get('release_date') else ''
        album_total = album_info.get('total_tracks')
    track_num = item['track_number']
    deezer_id = item_id
    cover = item['album']['images'][0]['url'] if len(item['album']['images']) > 0 else None
    genre = client.artist(artist_id=item['artists'][0]['uri'])['genres'][0] if len(client.artist(artist_id=item['artists'][0]['uri'])['genres']) > 0 else ""
    offset = 0
    return {
        "name": track_name,
        "artist": track_artist,
        "album": track_album,
        "year": track_year,
        "num_tracks": album_total,
        "num": track_num,
        "playlist_num": offset + 1,
        "cover": cover,
        "genre": genre,
        "deezer_id": deezer_id,
    }

@sync_to_async
def download_songs(item, download_directory='.'):
    file = f"{download_directory}/{item['name']} - {item['artists'][0]['name']}"
    query = f"{item['name']} {item['artists'][0]['name']} audio".replace(":", "").replace("\"", "")
    ydl_opts = {
        'format': "bestaudio/best",
        'default_search': 'ytsearch',
        'noplaylist': True,
        "nocheckcertificate": True,
        "outtmpl": f"{file}.%(ext)s",
        "quiet": True,
        "addmetadata": True,
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "postprocessors": [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        "embedthumbnail": True,
        "writethumbnail": False,
    }
    if os.path.isfile(COOKIES_PATH):
        ydl_opts["cookiefile"] = COOKIES_PATH
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)
            filename = ydl.prepare_filename(info)
            if not filename.endswith('.mp3'):
                filename = f"{os.path.splitext(filename)[0]}.mp3"
            if not os.path.isfile(filename):
                raise FileNotFoundError(f"File {filename} was not created")
            return filename
        except IndexError:
            # Retry with lyrics query
            query = f"{item['name']} lyrics audio".replace(":", "").replace("\"", "")
            try:
                info = ydl.extract_info(f"ytsearch:{query}", download=True)
                filename = ydl.prepare_filename(info)
                if not filename.endswith('.mp3'):
                    filename = f"{os.path.splitext(filename)[0]}.mp3"
                if not os.path.isfile(filename):
                    raise FileNotFoundError(f"File {filename} was not created")
                return filename
            except IndexError:
                # Fallback to broader search
                query = f"{item['name']} {item['artists'][0]['name']}".replace(":", "").replace("\"", "")
                info = ydl.extract_info(f"ytsearch:{query}", download=True)
                filename = ydl.prepare_filename(info)
                if not filename.endswith('.mp3'):
                    filename = f"{os.path.splitext(filename)[0]}.mp3"
                if not os.path.isfile(filename):
                    raise FileNotFoundError(f"File {filename} was not created")
                return filename
        except Exception as e:
            LOGGER.error(f"Download failed for {query}: {e}")
            raise FileNotFoundError(f"Download failed for {query}: {e}")

@sync_to_async
def download_dez(song, download_directory='.'):
    file = f"{download_directory}/{song['name']} - {song['artist']}"
    query = f"{song.get('name')} {song.get('artist')} audio".replace(":", "").replace("\"", "")
    ydl_opts = {
        'format': "bestaudio/best",
        'default_search': 'ytsearch',
        'noplaylist': True,
        "nocheckcertificate": True,
        "outtmpl": f"{file}.%(ext)s",
        "quiet": True,
        "addmetadata": True,
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "postprocessors": [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        "embedthumbnail": True,
        "writethumbnail": False,
    }
    if os.path.isfile(COOKIES_PATH):
        ydl_opts["cookiefile"] = COOKIES_PATH
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)
            filename = ydl.prepare_filename(info)
            if not filename.endswith('.mp3'):
                filename = f"{os.path.splitext(filename)[0]}.mp3"
            if not os.path.isfile(filename):
                raise FileNotFoundError(f"File {filename} was not created")
            return filename
        except IndexError:
            query = f"{song['name']} lyrics audio".replace(":", "").replace("\"", "")
            try:
                info = ydl.extract_info(f"ytsearch:{query}", download=True)
                filename = ydl.prepare_filename(info)
                if not filename.endswith('.mp3'):
                    filename = f"{os.path.splitext(filename)[0]}.mp3"
                if not os.path.isfile(filename):
                    raise FileNotFoundError(f"File {filename} was not created")
                return filename
            except IndexError:
                query = f"{song['name']} {song['artist']}".replace(":", "").replace("\"", "")
                info = ydl.extract_info(f"ytsearch:{query}", download=True)
                filename = ydl.prepare_filename(info)
                if not filename.endswith('.mp3'):
                    filename = f"{os.path.splitext(filename)[0]}.mp3"
                if not os.path.isfile(filename):
                    raise FileNotFoundError(f"File {filename} was not created")
                return filename
        except Exception as e:
            LOGGER.error(f"Download failed for {query}: {e}")
            raise FileNotFoundError(f"Download failed for {query}: {e}")

@sync_to_async
def copy(P, A):
    P.copy(LOG_GROUP)
    A.copy(LOG_GROUP)

@sync_to_async
def forward(A, P):
    A.copy(LOG_GROUP)
    P.copy(LOG_GROUP)
