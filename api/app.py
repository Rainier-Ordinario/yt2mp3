"""
YouTube to MP3 Converter - Flask Backend API
Handles video downloading and MP3 conversion using yt-dlp and ffmpeg
"""

import os
import sys
import json
import threading
import traceback
from queue import Queue
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from pathlib import Path

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
    """Kick off a download and stream NDJSON progress events back.

    Synchronous validation errors come back as a single JSON body (so the
    client can read them with res.json()). Otherwise the response is a
    chunked stream of newline-delimited JSON events, one per line:

        {"type":"progress","percent":"45.3%","speed":"2.1MiB/s","eta":"00:08"}
        {"type":"converting"}
        {"type":"done","title":"...","duration":123,"bitrate":"320"}
        {"type":"error","message":"..."}
    """
    print(f"📥 Download request received from {request.remote_addr}")
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    bitrate = data.get("bitrate") or "320"
    print(f"   URL: {url}, Bitrate: {bitrate}")

    if not url:
        return jsonify({"error": "URL is required"}), 400
    if not core.is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL"}), 400
    if not core.check_ffmpeg():
        return jsonify({
            "error": "FFmpeg is not installed. Install it with: brew install ffmpeg"
        }), 500

    return Response(
        stream_with_context(_download_event_stream(url, bitrate)),
        mimetype="application/x-ndjson",
    )


def _download_event_stream(url: str, bitrate: str):
    """Run the download in a background thread; yield NDJSON events as they happen."""
    events: "Queue[dict | None]" = Queue()

    def on_progress(d):
        status = d.get("status")
        if status == "downloading":
            events.put({
                "type": "progress",
                "percent": (d.get("_percent_str") or "").strip(),
                "speed": (d.get("_speed_str") or "").strip(),
                "eta": (d.get("_eta_str") or "").strip(),
            })
        elif status == "finished":
            events.put({"type": "converting"})

    def run():
        try:
            info = core.download_audio(
                url, bitrate, DOWNLOAD_FOLDER, progress_hooks=[on_progress]
            )
            events.put({
                "type": "done",
                "title": info.get("title", "Unknown"),
                "duration": info.get("duration", 0),
                "bitrate": bitrate,
            })
        except core.AudioDownloadError as e:
            if e.detail:
                print(f"❌ DownloadError: {e.detail}")
            events.put({"type": "error", "message": str(e)})
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print(traceback.format_exc())
            events.put({
                "type": "error",
                "message": "An internal error occurred. Please try again.",
            })
        finally:
            events.put(None)  # sentinel: tells the generator to stop

    threading.Thread(target=run, daemon=True).start()
    while True:
        event = events.get()
        if event is None:
            return
        yield json.dumps(event) + "\n"


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
