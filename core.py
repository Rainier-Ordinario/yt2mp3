"""
Shared core logic for the YouTube to MP3 Converter.

Imported by both the desktop GUI (app.py) and the Flask API (api/app.py)
so URL validation, the ffmpeg check, yt-dlp options, and the quality
table live in exactly one place.
"""

import os
import subprocess
from urllib.parse import urlparse

# Where finished MP3s are written (no hardcoded usernames)
DOWNLOAD_FOLDER = os.path.expanduser("~/Downloads/YouTube MP3s")

# Audio settings
AUDIO_CODEC = "mp3"
DEFAULT_BITRATE = "320"  # kbps (highest MP3 quality)

# Reject videos longer than this to avoid huge downloads/conversions
MAX_DURATION_SECONDS = 2 * 60 * 60  # 2 hours

# yt-dlp socket timeout
SOCKET_TIMEOUT = 30

# Canonical audio quality table. `label` is what the API/web UI shows;
# `size` is the rough estimate shown next to the desktop dropdown.
QUALITY_OPTIONS = [
    {"value": "128", "label": "128 kbps (4-5 MB/min)", "size": "(~4-5 MB/min)"},
    {"value": "192", "label": "192 kbps (6-7 MB/min)", "size": "(~6-7 MB/min)"},
    {"value": "256", "label": "256 kbps (8-9 MB/min)", "size": "(~8-9 MB/min)"},
    {"value": "320", "label": "320 kbps (10-12 MB/min) - Best", "size": "(~10-12 MB/min)"},
]
BITRATE_VALUES = [opt["value"] for opt in QUALITY_OPTIONS]
SIZE_BY_BITRATE = {opt["value"]: opt["size"] for opt in QUALITY_OPTIONS}

# Exact hosts we accept. A substring check ("youtube.com" in url) is
# bypassable with URLs like https://evil.com/?x=youtube.com, so match the
# parsed hostname against this allowlist instead.
ALLOWED_YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
}


def is_valid_youtube_url(url: str) -> bool:
    """Return True only if url is an http(s) URL on a known YouTube host."""
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if parsed.scheme not in ("http", "https"):
        return False
    host = (parsed.hostname or "").lower()
    return host in ALLOWED_YOUTUBE_HOSTS


def check_ffmpeg() -> bool:
    """Check if ffmpeg is installed and runnable."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def build_ydl_opts(download_folder: str, bitrate: str, progress_hooks=None) -> dict:
    """Build the yt-dlp options dict shared by both front ends.

    The output filename includes the video id and restrictfilenames is on
    so a crafted title can't collide with or overwrite another file.
    """
    opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": AUDIO_CODEC,
            "preferredquality": bitrate,
        }],
        "outtmpl": os.path.join(download_folder, "%(title)s [%(id)s].%(ext)s"),
        "restrictfilenames": True,
        "quiet": False,
        "no_warnings": False,
        "noplaylist": True,  # Single video only, reject playlists
        "socket_timeout": SOCKET_TIMEOUT,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (compatible; YouTube-MP3-Converter)"
        },
    }
    if progress_hooks:
        opts["progress_hooks"] = progress_hooks
    return opts
