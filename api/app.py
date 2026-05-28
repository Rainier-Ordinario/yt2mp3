"""
YouTube to MP3 Converter - Flask Backend API
Handles video downloading and MP3 conversion using yt-dlp and ffmpeg
"""

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
from datetime import datetime

# Import the shared core module from the repo root regardless of cwd.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core  # noqa: E402

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configuration (shared values live in core.py)
DOWNLOAD_FOLDER = core.DOWNLOAD_FOLDER

# Ensure download folder exists
Path(DOWNLOAD_FOLDER).mkdir(parents=True, exist_ok=True)


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    ffmpeg_available = core.check_ffmpeg()
    # Don't expose the server's filesystem path. Callers only need to know
    # whether the service can run.
    return jsonify({
        "status": "ok",
        "ffmpeg": ffmpeg_available,
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
        if not core.is_valid_youtube_url(url):
            return jsonify({"error": "Invalid YouTube URL"}), 400

        # Check ffmpeg
        if not core.check_ffmpeg():
            return jsonify({
                "error": "FFmpeg is not installed. Install it with: brew install ffmpeg"
            }), 500

        # Download and convert (shared orchestration with the desktop app).
        # The file is written to the *server's* DOWNLOAD_FOLDER — this only
        # makes sense as a localhost tool. We deliberately don't echo the
        # server path back to the client.
        info = core.download_audio(url, bitrate, DOWNLOAD_FOLDER)
        return jsonify({
            "success": True,
            "title": info.get("title", "Unknown"),
            "duration": info.get("duration", 0),
            "bitrate": bitrate,
            "timestamp": datetime.now().isoformat()
        })

    except core.AudioDownloadError as e:
        # Expected failure with a user-safe message. Log the raw cause
        # server-side without echoing internals (paths, stack) to the client.
        if e.detail:
            print(f"❌ DownloadError: {e.detail}")
        return jsonify({"error": str(e)}), 400

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
            {"value": opt["value"], "label": opt["label"]}
            for opt in core.QUALITY_OPTIONS
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
    if not core.check_ffmpeg():
        print("⚠️  Warning: FFmpeg is not installed")
        print("Install it with: brew install ffmpeg")

    print(f"✓ Download folder: {DOWNLOAD_FOLDER}")
    print("✓ Starting Flask API server on http://localhost:8000")
    print("✓ Press Ctrl+C to stop")

    # Debug mode exposes the Werkzeug debugger (arbitrary code execution if
    # the port is reachable). Off by default; opt in locally with FLASK_DEBUG=1.
    debug_enabled = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_enabled, port=8000)
