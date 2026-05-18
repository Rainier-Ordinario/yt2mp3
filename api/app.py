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

# Ensure download folder exists
Path(DOWNLOAD_FOLDER).mkdir(parents=True, exist_ok=True)


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
        youtube_domains = ["youtube.com", "youtu.be", "youtube.co"]
        if not any(domain in url for domain in youtube_domains):
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
            "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),
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
            return jsonify({"error": error_msg}), 400

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Unexpected error: {error_msg}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            "error": f"An error occurred: {error_msg}"
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
