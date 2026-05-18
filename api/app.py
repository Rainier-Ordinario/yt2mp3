"""
YouTube to MP3 Converter - Flask Backend API
Handles video downloading and MP3 conversion using yt-dlp and ffmpeg
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os
import subprocess
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configuration
DOWNLOAD_FOLDER = os.path.expanduser("~/Downloads/YouTube MP3s")
AUDIO_CODEC = "mp3"
MAX_DURATION_SECONDS = 2 * 60 * 60  # reject videos longer than 2 hours

# Ensure download folder exists
Path(DOWNLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

# Exact hosts we accept. A substring check (e.g. "youtube.com" in url) is
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


def check_ffmpeg():
    """Check if ffmpeg is installed"""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    ffmpeg_available = check_ffmpeg()
    return jsonify({
        "status": "ok",
        "ffmpeg": ffmpeg_available,
        "download_folder": DOWNLOAD_FOLDER
    })


@app.route("/api/download", methods=["POST"])
def download():
    """Download YouTube video and convert to MP3"""
    print(f"📥 Download request received from {request.remote_addr}")
    print(f"   Headers: {dict(request.headers)}")
    try:
        data = request.json
        url = data.get("url", "").strip()
        bitrate = data.get("bitrate", "320")
        print(f"   URL: {url}, Bitrate: {bitrate}")

        # Validate input
        if not url:
            return jsonify({"error": "URL is required"}), 400

        # Validate YouTube URL
        if not is_valid_youtube_url(url):
            return jsonify({"error": "Invalid YouTube URL"}), 400

        # Check ffmpeg
        if not check_ffmpeg():
            return jsonify({
                "error": "FFmpeg is not installed. Install it with: brew install ffmpeg"
            }), 500

        # Configure yt-dlp options
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": AUDIO_CODEC,
                "preferredquality": bitrate,
            }],
            # Include the video id and restrict to safe ASCII filenames so a
            # crafted title can't collide with or overwrite another file.
            "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title)s [%(id)s].%(ext)s"),
            "restrictfilenames": True,
            "quiet": False,
            "no_warnings": False,
            "noplaylist": True,  # Single video only
            "socket_timeout": 30,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (compatible; YouTube-MP3-Converter)"
            },
        }

        # Download and convert
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Check duration before downloading to avoid resource exhaustion
            # from someone requesting a multi-hour video.
            meta = ydl.extract_info(url, download=False)
            duration = (meta or {}).get("duration") or 0
            if duration > MAX_DURATION_SECONDS:
                return jsonify({
                    "error": (
                        f"Video is too long ({duration // 60} min). "
                        f"Maximum is {MAX_DURATION_SECONDS // 60} minutes."
                    )
                }), 400

            info = ydl.extract_info(url, download=True)
            video_title = info.get("title", "Unknown")
            duration = info.get("duration", 0)

            return jsonify({
                "success": True,
                "title": video_title,
                "duration": duration,
                "bitrate": bitrate,
                "save_location": DOWNLOAD_FOLDER,
                "timestamp": datetime.now().isoformat()
            })

    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "This video is not available" in error_msg or "Private" in error_msg:
            return jsonify({
                "error": "This video is not available or is private"
            }), 400
        elif "playlist" in error_msg.lower():
            return jsonify({
                "error": "Playlists are not supported. Please provide a single video URL"
            }), 400
        else:
            # Log the full yt-dlp error server-side, but don't echo it back
            # to the client (it can contain file paths and internals).
            print(f"❌ DownloadError: {error_msg}")
            return jsonify({
                "error": "Could not download this video. It may be "
                         "unavailable, age-restricted, or region-locked."
            }), 400

    except Exception as e:
        # Log full detail server-side; return a generic message so we don't
        # leak internals (paths, stack frames) to the client.
        print(f"❌ Unexpected error: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            "error": "An internal error occurred. Please try again."
        }), 500


@app.route("/api/formats", methods=["GET"])
def get_formats():
    """Get available audio quality formats"""
    return jsonify({
        "formats": [
            {"value": "128", "label": "128 kbps (4-5 MB/min)" },
            {"value": "192", "label": "192 kbps (6-7 MB/min)" },
            {"value": "256", "label": "256 kbps (8-9 MB/min)" },
            {"value": "320", "label": "320 kbps (10-12 MB/min) - Best" },
        ]
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    # Check dependencies on startup
    if not check_ffmpeg():
        print("⚠️  Warning: FFmpeg is not installed")
        print("Install it with: brew install ffmpeg")

    print(f"✓ Download folder: {DOWNLOAD_FOLDER}")
    print("✓ Starting Flask API server on http://localhost:8000")
    print("✓ Press Ctrl+C to stop")

    # Debug mode exposes the Werkzeug debugger (arbitrary code execution if
    # the port is reachable). Off by default; opt in locally with FLASK_DEBUG=1.
    debug_enabled = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_enabled, port=8000)
