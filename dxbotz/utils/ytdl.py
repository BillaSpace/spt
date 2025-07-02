from asgiref.sync import sync_to_async
from yt_dlp import YoutubeDL
from requests import get
import os

COOKIES_PATH = os.path.join("cookies", "cookies.txt")

def get_common_opts():
    opts = {
        "quiet": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "extract_flat": True,
        "format": "bestaudio/best",
        "noplaylist": True,
    }
    if os.path.isfile(COOKIES_PATH):
        opts["cookiefile"] = COOKIES_PATH
    return opts

@sync_to_async
def getIds(video):
    ids = []
    ydl_opts = get_common_opts()
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(video, download=False)
            if 'entries' in info_dict:
                ids.extend([x.get('id'), x.get('playlist_index'), x.get('creator') or x.get('uploader'),
                           x.get('title'), x.get('duration'), x.get('thumbnail')] for x in info_dict['entries'])
            else:
                ids.append([info_dict.get('id'), info_dict.get('playlist_index'), info_dict.get('creator') or info_dict.get('uploader'),
                           info_dict.get('title'), info_dict.get('duration'), info_dict.get('thumbnail')])
        except Exception as e:
            raise e
    return ids

def audio_opt(path, uploader="@BillaDLbot"):
    opts = get_common_opts()
    opts.update({
        "format": "bestaudio/best",
        "addmetadata": True,
        "noplaylist": True,
        "outtmpl": f"{path}/%(title)s - {uploader}.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "embedthumbnail": True,
        "writethumbnail": False,
    })
    return opts

@sync_to_async
def ytdl_down(opts, url):
    cookie_opts = get_common_opts()
    opts.update(cookie_opts)
    with YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
        except Exception as e:
            raise e

@sync_to_async
def thumb_down(url, videoId):
    thumb_path = f"/tmp/thumbnails/{videoId}.jpg"
    os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
    with open(thumb_path, "wb") as file:
        file.write(get(url).content)
    return thumb_path
