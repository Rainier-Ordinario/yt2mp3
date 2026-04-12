#!/usr/bin/env python3
"""
YouTube to MP3 Converter
A simple GUI application to download and convert YouTube videos to MP3
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import os
import subprocess
from pathlib import Path
import yt_dlp

# ============================================================================
# Configuration Constants - Easy to modify
# ============================================================================

# Download folder location (uses ~ for home directory, no hardcoded usernames)
DOWNLOAD_FOLDER = os.path.expanduser("~/Downloads/YouTube MP3s")

# Audio quality settings
AUDIO_BITRATE = "192"  # kbps
AUDIO_CODEC = "mp3"

# YouTube domains to validate URLs
YOUTUBE_DOMAINS = ["youtube.com", "youtu.be", "youtube.co"]

# GUI styling
TITLE_BGCOLOR = "#2c3e50"
TITLE_HEIGHT = 60
BUTTON_BGCOLOR = "#27ae60"
STATUS_BGCOLOR = "#ecf0f1"
FOOTER_BGCOLOR = "#ecf0f1"
TEXT_COLOR_DARK = "#7f8c8d"

# Window dimensions
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500

# Timeouts and delays
SOCKET_TIMEOUT = 30


class YouTubeMP3Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube to MP3 Converter")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)

        # Check ffmpeg installation first before proceeding
        if not self._check_ffmpeg():
            self._show_ffmpeg_error()
            return

        # Use the configured download folder path
        self.download_folder = DOWNLOAD_FOLDER
        self._create_download_folder()

        self._setup_ui()
        self.is_downloading = False

    def _check_ffmpeg(self) -> bool:
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

    def _show_ffmpeg_error(self):
        """Show error dialog if ffmpeg is not installed"""
        error_msg = (
            "❌ FFmpeg is not installed\n\n"
            "YouTube to MP3 requires ffmpeg to convert audio.\n\n"
            "To install on macOS, run:\n"
            "  brew install ffmpeg\n\n"
            "If you don't have Homebrew, install it first from:\n"
            "  https://brew.sh\n\n"
            "After installing, restart this application."
        )
        messagebox.showerror("FFmpeg Not Found", error_msg)
        self.root.quit()

    def _create_download_folder(self):
        """Create download folder if it doesn't exist"""
        try:
            Path(self.download_folder).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Could not create download folder:\n{e}")

    def _setup_ui(self):
        """Set up the GUI elements"""
        # ===== TITLE SECTION =====
        title_frame = tk.Frame(self.root, bg=TITLE_BGCOLOR, height=TITLE_HEIGHT)
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="YouTube to MP3 Converter",
            font=("Helvetica", 18, "bold"),
            bg=TITLE_BGCOLOR,
            fg="white"
        )
        title_label.pack(pady=15)

        # ===== MAIN CONTENT SECTION =====
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # URL input field for YouTube links
        url_label = tk.Label(content_frame, text="YouTube URL:", font=("Helvetica", 11, "bold"))
        url_label.pack(anchor=tk.W, pady=(0, 5))

        self.url_entry = tk.Entry(content_frame, font=("Helvetica", 10), width=50)
        self.url_entry.pack(fill=tk.X, pady=(0, 15))
        # Allow pressing Enter to trigger download
        self.url_entry.bind("<Return>", lambda e: self._on_download_click())

        # Download button
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(0, 15))

        self.download_btn = tk.Button(
            button_frame,
            text="📥 Download as MP3",
            command=self._on_download_click,
            font=("Helvetica", 11, "bold"),
            bg=BUTTON_BGCOLOR,
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.download_btn.pack(fill=tk.X)

        # Status display area with scrollbar for long output
        status_label = tk.Label(content_frame, text="Status:", font=("Helvetica", 11, "bold"))
        status_label.pack(anchor=tk.W, pady=(0, 5))

        self.status_text = scrolledtext.ScrolledText(
            content_frame,
            height=12,
            width=60,
            font=("Courier", 9),
            bg=STATUS_BGCOLOR,
            state=tk.DISABLED
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)

        # ===== FOOTER SECTION =====
        footer_frame = tk.Frame(self.root, bg=FOOTER_BGCOLOR)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Display the download folder path for user reference
        footer_label = tk.Label(
            footer_frame,
            text=f"Downloads saved to: {self.download_folder}",
            font=("Helvetica", 9),
            bg=FOOTER_BGCOLOR,
            fg=TEXT_COLOR_DARK
        )
        footer_label.pack(padx=15, pady=8, anchor=tk.W)

    def _log(self, message: str):
        """Append message to status text area"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update()

    def _clear_log(self):
        """Clear the status text area"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)

    def _validate_url(self, url: str) -> bool:
        """Validate if URL is a YouTube URL"""
        if not url.strip():
            messagebox.showwarning("Empty URL", "Please enter a YouTube URL")
            return False

        # Check if URL contains any known YouTube domains
        if not any(domain in url for domain in YOUTUBE_DOMAINS):
            messagebox.showwarning("Invalid URL", "Please enter a valid YouTube URL")
            return False

        return True

    def _on_download_click(self):
        """Handle download button click"""
        if self.is_downloading:
            messagebox.showinfo("Already Downloading", "A download is already in progress")
            return

        url = self.url_entry.get().strip()

        if not self._validate_url(url):
            return

        # Run download in a separate thread to not freeze the GUI
        thread = threading.Thread(target=self._download_video, args=(url,))
        thread.daemon = True
        thread.start()

    def _download_video(self, url: str):
        """Download and convert YouTube video to MP3"""
        self.is_downloading = True
        self.download_btn.config(state=tk.DISABLED)

        try:
            self._clear_log()
            self._log("🔍 Fetching video information...")

            # Configure yt-dlp options for audio extraction
            ydl_opts = {
                # Download best available audio quality
                "format": "bestaudio/best",
                # Post-processor: extract audio and convert to MP3
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": AUDIO_CODEC,
                    "preferredquality": AUDIO_BITRATE,
                }],
                # Output filename template (uses video title)
                "outtmpl": os.path.join(self.download_folder, "%(title)s.%(ext)s"),
                "quiet": False,
                "no_warnings": False,
                "noplaylist": True,  # Enforce single video only, reject playlists
                "socket_timeout": SOCKET_TIMEOUT,
                # Standard browser User-Agent (not hardcoded to specific OS version)
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (compatible; YouTube-MP3-Converter)"
                },
                "progress_hooks": [self._progress_hook],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self._log("📝 Video title: Fetching...")
                info = ydl.extract_info(url, download=True)
                video_title = info.get("title", "Unknown")
                self._log(f"✅ Successfully downloaded: {video_title}")
                self._log(f"💾 Saved to: {self.download_folder}")
                messagebox.showinfo("Success", f"Downloaded: {video_title}\n\nSaved to Downloads folder")

        except yt_dlp.utils.DownloadError as e:
            # Handle specific download errors with user-friendly messages
            error_msg = str(e)
            if "This video is not available" in error_msg or "Private" in error_msg:
                self._log("❌ Error: This video is not available or is private")
                messagebox.showerror("Download Failed", "This video is not available or is private")
            elif "playlist" in error_msg.lower():
                self._log("❌ Error: Playlists are not supported. Please provide a single video URL")
                messagebox.showerror("Download Failed", "Playlists are not supported.\nPlease provide a single video URL")
            else:
                self._log(f"❌ Error: {error_msg}")
                messagebox.showerror("Download Failed", error_msg)

        except Exception as e:
            # Catch any other unexpected errors
            error_msg = str(e)
            self._log(f"❌ Error: {error_msg}")
            messagebox.showerror("Error", f"An error occurred:\n{error_msg}")

        finally:
            # Always re-enable the button and clear input field after download (success or failure)
            self.is_downloading = False
            self.download_btn.config(state=tk.NORMAL)
            self.url_entry.delete(0, tk.END)

    def _progress_hook(self, d):
        """Handle download progress updates from yt-dlp"""
        if d["status"] == "downloading":
            # Extract progress information from yt-dlp
            percent = d.get("_percent_str", "N/A")
            speed = d.get("_speed_str", "N/A")
            eta = d.get("_eta_str", "N/A")

            # Display download progress
            self._log(f"⬇️  {percent} | Speed: {speed} | ETA: {eta}")

        elif d["status"] == "finished":
            # Download complete, now converting audio
            self._log("✔️  Download finished, converting to MP3...")


def main():
    root = tk.Tk()
    app = YouTubeMP3Converter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
