#!/usr/bin/env python3
"""
YouTube to MP3 Converter
A simple GUI application to download and convert YouTube videos to MP3
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
from pathlib import Path
import core

# ============================================================================
# Configuration Constants - Easy to modify
# ============================================================================

# Shared values (folder, bitrates, limits, host allowlist) live in core.py
DOWNLOAD_FOLDER = core.DOWNLOAD_FOLDER
AUDIO_BITRATE_DEFAULT = core.DEFAULT_BITRATE
AUDIO_BITRATE_OPTIONS = core.BITRATE_VALUES

# GUI styling - Professional color scheme with better contrast
BG_PRIMARY = "#1a1f2e"  # Very dark navy background
BG_SECONDARY = "#252d3d"  # Slightly lighter secondary
BG_TERTIARY = "#2d3748"  # Tertiary background for sections
ACCENT_COLOR = "#4f46e5"  # Deep indigo blue
ACCENT_HOVER = "#4338ca"  # Darker indigo for hover
TEXT_PRIMARY = "#ffffff"  # Pure white for maximum contrast
TEXT_SECONDARY = "#e5e7eb"  # Very light gray
TEXT_MUTED = "#9ca3af"  # Medium gray for secondary info
BORDER_COLOR = "#374151"  # Border/separator color
SUCCESS_COLOR = "#22c55e"  # Bright green
ERROR_COLOR = "#ef4444"  # Bright red
STATUS_BGCOLOR = "#252d3d"  # Status area background

# Window dimensions
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500


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
        self._setup_text_tags()
        self._setup_styles()
        self.is_downloading = False
        self.selected_bitrate = AUDIO_BITRATE_DEFAULT  # Default to highest quality

    def _check_ffmpeg(self) -> bool:
        """Check if ffmpeg is installed"""
        return core.check_ffmpeg()

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
        # Set window background color
        self.root.config(bg=BG_PRIMARY)

        # ===== TITLE SECTION with gradient effect =====
        title_frame = tk.Frame(self.root, bg=BG_SECONDARY, height=85)
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        title_frame.pack_propagate(False)

        # Main title
        title_label = tk.Label(
            title_frame,
            text="YouTube to MP3 Converter",
            font=("Helvetica", 26, "bold"),
            bg=BG_SECONDARY,
            fg=TEXT_PRIMARY
        )
        title_label.pack(pady=(20, 5))

        # Subtitle with better contrast
        subtitle_label = tk.Label(
            title_frame,
            text="Download and convert videos to high-quality MP3 audio",
            font=("Helvetica", 10),
            bg=BG_SECONDARY,
            fg=TEXT_SECONDARY
        )
        subtitle_label.pack(pady=(0, 10))

        # ===== MAIN CONTENT SECTION =====
        content_frame = tk.Frame(self.root, bg=BG_PRIMARY)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        # URL input section with label
        url_label = tk.Label(
            content_frame,
            text="YouTube URL",
            font=("Helvetica", 12, "bold"),
            bg=BG_PRIMARY,
            fg=TEXT_PRIMARY
        )
        url_label.pack(anchor=tk.W, pady=(0, 8))

        # URL entry field with improved styling and contrast
        self.url_entry = tk.Entry(
            content_frame,
            font=("Helvetica", 12),
            width=50,
            bg=BG_TERTIARY,
            fg=TEXT_PRIMARY,
            insertbackground=ACCENT_COLOR,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=2,
            highlightcolor=ACCENT_COLOR,
            highlightbackground=BORDER_COLOR
        )
        self.url_entry.pack(fill=tk.X, pady=(0, 25), ipady=12)
        # Allow pressing Enter to trigger download
        self.url_entry.bind("<Return>", lambda e: self._on_download_click())

        # Audio quality selector section
        quality_frame = tk.Frame(content_frame, bg=BG_PRIMARY)
        quality_frame.pack(fill=tk.X, pady=(0, 25))

        quality_label = tk.Label(
            quality_frame,
            text="Audio Quality",
            font=("Helvetica", 12, "bold"),
            bg=BG_PRIMARY,
            fg=TEXT_PRIMARY
        )
        quality_label.pack(anchor=tk.W, pady=(0, 10))

        # Quality selector row with better styling
        quality_selector_frame = tk.Frame(quality_frame, bg=BG_PRIMARY)
        quality_selector_frame.pack(fill=tk.X)

        self.quality_var = tk.StringVar(value=AUDIO_BITRATE_DEFAULT)
        quality_dropdown = tk.OptionMenu(
            quality_selector_frame,
            self.quality_var,
            *AUDIO_BITRATE_OPTIONS,
            command=self._on_quality_change
        )
        quality_dropdown.config(
            font=("Helvetica", 11),
            bg=BG_TERTIARY,
            fg=TEXT_PRIMARY,
            activebackground=ACCENT_COLOR,
            activeforeground=TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            padx=12,
            pady=6
        )
        quality_dropdown.pack(side=tk.LEFT, padx=(0, 20))

        # Display file size estimate for selected quality with better contrast
        self.quality_info_label = tk.Label(
            quality_selector_frame,
            text="(~10-12 MB/min)",
            font=("Helvetica", 11),
            bg=BG_PRIMARY,
            fg=TEXT_SECONDARY
        )
        self.quality_info_label.pack(side=tk.LEFT)

        # Download button with improved styling
        button_frame = tk.Frame(content_frame, bg=BG_PRIMARY)
        button_frame.pack(fill=tk.X, pady=(0, 30))

        self.download_btn = tk.Button(
            button_frame,
            text="Download as MP3",
            command=self._on_download_click,
            font=("Helvetica", 13, "bold"),
            bg=ACCENT_COLOR,
            fg=TEXT_PRIMARY,
            activebackground=ACCENT_HOVER,
            activeforeground=TEXT_PRIMARY,
            padx=40,
            pady=14,
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0
        )
        self.download_btn.pack(fill=tk.X)

        # Progress bar section
        self.progress_frame = tk.Frame(content_frame, bg=BG_PRIMARY)
        self.progress_frame.pack(fill=tk.X, pady=(0, 20))

        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode="indeterminate",
            length=400
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 8))

        # Status display area with scrollbar for long output
        status_label = tk.Label(
            content_frame,
            text="Status & Messages",
            font=("Helvetica", 12, "bold"),
            bg=BG_PRIMARY,
            fg=TEXT_PRIMARY
        )
        status_label.pack(anchor=tk.W, pady=(0, 10))

        self.status_text = scrolledtext.ScrolledText(
            content_frame,
            height=10,
            width=60,
            font=("Courier", 10),
            bg=BG_TERTIARY,
            fg=TEXT_SECONDARY,
            insertbackground=ACCENT_COLOR,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=2,
            highlightcolor=BORDER_COLOR,
            highlightbackground=BORDER_COLOR,
            state=tk.DISABLED
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)

        # ===== FOOTER SECTION =====
        footer_frame = tk.Frame(self.root, bg=BG_SECONDARY, height=60)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)

        # Display the download folder path for user reference
        footer_label = tk.Label(
            footer_frame,
            text=f"Saves to:  {self.download_folder}",
            font=("Helvetica", 10),
            bg=BG_SECONDARY,
            fg=TEXT_SECONDARY
        )
        footer_label.pack(padx=25, pady=18, anchor=tk.W)

    def _setup_text_tags(self):
        """Configure text tags for color coding status messages with high contrast"""
        self.status_text.tag_config("success", foreground=SUCCESS_COLOR)  # Bright green
        self.status_text.tag_config("error", foreground=ERROR_COLOR)  # Bright red
        self.status_text.tag_config("download", foreground=ACCENT_COLOR)  # Indigo blue
        self.status_text.tag_config("info", foreground=TEXT_SECONDARY)  # Light gray

    def _setup_styles(self):
        """Configure ttk widget styles"""
        style = ttk.Style()
        style.theme_use("clam")  # Use clam theme for better customization

        # Configure progress bar style
        style.configure(
            "TProgressbar",
            background=ACCENT_COLOR,
            troughcolor=BG_SECONDARY,
            bordercolor=BORDER_COLOR,
            lightcolor=ACCENT_COLOR,
            darkcolor=ACCENT_COLOR
        )

    def _log(self, message: str):
        """Append message to status text area with color coding"""
        self.status_text.config(state=tk.NORMAL)

        # Color code messages based on content
        if "✅" in message or "Success" in message:
            tag = "success"
        elif "❌" in message or "Error" in message:
            tag = "error"
        elif "⬇️" in message or "downloading" in message.lower():
            tag = "download"
        else:
            tag = "info"

        self.status_text.insert(tk.END, message + "\n", tag)
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update()

    def _clear_log(self):
        """Clear the status text area"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)

    def _on_quality_change(self, selected_quality: str):
        """Update UI when user changes audio quality"""
        self.selected_bitrate = selected_quality

        # Update file size estimate based on bitrate
        self.quality_info_label.config(
            text=core.SIZE_BY_BITRATE.get(selected_quality, "")
        )

    def _validate_url(self, url: str) -> bool:
        """Validate if URL is a YouTube URL"""
        if not url.strip():
            messagebox.showwarning("Empty URL", "Please enter a YouTube URL")
            return False

        # Check the parsed hostname against the allowlist
        if not core.is_valid_youtube_url(url):
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

        # Show progress bar during download
        self.progress_bar.start()

    def _download_video(self, url: str):
        """Download and convert YouTube video to MP3"""
        self.is_downloading = True
        self.download_btn.config(state=tk.DISABLED)

        try:
            self._clear_log()
            self._log("🔍 Fetching video information...")
            self._log("📝 Video title: Fetching...")

            # Download and convert (shared orchestration with the Flask API)
            info = core.download_audio(
                url,
                self.selected_bitrate,
                self.download_folder,
                progress_hooks=[self._progress_hook],
            )
            video_title = info.get("title", "Unknown")
            self._log(f"✅ Successfully downloaded: {video_title}")
            self._log(f"💾 Saved to: {self.download_folder}")
            messagebox.showinfo("Success", f"Downloaded: {video_title}\n\nSaved to Downloads folder")

        except core.AudioDownloadError as e:
            # Expected failure: show the user-safe message, log the raw cause
            self._log(f"❌ Error: {e.detail or e}")
            messagebox.showerror("Download Failed", str(e))

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
            # Stop the progress bar animation
            self.progress_bar.stop()

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
