from asgiref.sync import sync_to_async
from yt_dlp import YoutubeDL
from requests import get
import os

# Path to cookies file relative to repo root
COOKIES_PATH = os.path.join("cookies", "cookies.txt")

def get_common_opts():
    opts = {
        "quiet": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
    }
    if os.path.isfile(COOKIES_PATH):
        opts["cookiefile"] = COOKIES_PATH
    return opts

@sync_to_async
def getIds(video):
    ids = []
    ydl_opts = get_common_opts()
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video, download=False)
        try:
            info_dict = info_dict['entries']
            ids.extend([x.get('id'), x.get('playlist_index'), x.get('creator') or x.get('uploader'),
                        x.get('title'), x.get('duration'), x.get('thumbnail')] for x in info_dict)
        except:
            ids.append([info_dict.get('id'), info_dict.get('playlist_index'), info_dict.get('creator') or info_dict.get('uploader'),
                        info_dict.get('title'), info_dict.get('duration'), info_dict.get('thumbnail')])
    return ids

def audio_opt(path, uploader="@BillaDLbot"):
    opts = get_common_opts()
    opts.update({
        "format": "bestaudio",
        "addmetadata": True,
        'noplaylist': True,
        "outtmpl": f"{path}/%(title)s - {uploader}.mp3",
    })
    return opts

@sync_to_async
def ytdl_down(opts, url):
    # Merge opts with cookie option if cookies file exists
    cookie_opts = get_common_opts()
    opts.update(cookie_opts)
    
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url)
        return ydl.prepare_filename(info)

@sync_to_async
def thumb_down(videoId):
    thumb_path = f"/tmp/thumbnails/{videoId}.jpg"
    os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
    with open(thumb_path, "wb") as file:
        file.write(get(f"https://img.youtube.com/vi/{videoId}/default.jpg").content)
    return thumb_path
