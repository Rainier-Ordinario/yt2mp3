# YouTube to MP3 Converter

A simple, lightweight desktop application to download YouTube videos and convert them to MP3 format on macOS.

## Features

✨ **Simple GUI** - Clean, intuitive tkinter interface  
📥 **Single Video Downloads** - Download one video at a time (no playlists)  
🎵 **MP3 Conversion** - Automatically converts to 192kbps MP3  
📊 **Progress Tracking** - Real-time download progress and status messages  
✅ **FFmpeg Check** - Detects missing dependencies with clear error messages  

## Requirements

- **macOS** (tested on recent versions)
- **Python 3.7+**
- **FFmpeg** (for audio conversion)

## Installation & Setup

### 1. Install FFmpeg (if not already installed)

```bash
brew install ffmpeg
```

If you don't have Homebrew, install it first from https://brew.sh

### 2. Clone or download this repository

```bash
cd ~/Documents/yt2mp3
```

### 3. Create a Python virtual environment

```bash
python3 -m venv venv
```

### 4. Activate the virtual environment

```bash
source venv/bin/activate
```

### 5. Install Python dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
python3 app.py
```

The GUI will open. Simply:

1. **Paste a YouTube URL** in the text field
2. **Click "Download as MP3"** or press Enter
3. **Wait for the download to complete**
4. **Find your MP3** in `~/Downloads/YouTube MP3s/`

### Command-line shortcuts (optional)

Make the script executable:
```bash
chmod +x app.py
```

Then run directly:
```bash
./app.py
```

## File Structure

```
yt2mp3/
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── .gitignore            # Git ignore rules
```

## Troubleshooting

### "FFmpeg is not installed" error

Run: `brew install ffmpeg`

Then restart the application.

### "This video is not available" error

- The video might be private, age-restricted, or unavailable in your region
- Check if you can access the video in your browser first

### "Playlists are not supported" error

This application downloads single videos only. Please provide a direct video URL, not a playlist URL.

### Downloaded file is empty or incomplete

- Check your internet connection
- Try downloading a different video
- Make sure you have enough disk space in `~/Downloads/`

## Legal Notice

⚠️ **For Personal Use Only**

This tool is intended for personal, non-commercial use only. You are responsible for ensuring:

- You have the right to download the content
- The content is not protected by copyright
- You comply with YouTube's Terms of Service
- You respect the rights of content creators

**Do not use this tool to:**
- Download copyrighted content without permission
- Infringe on intellectual property rights
- Violate YouTube's Terms of Service
- For commercial purposes

## Dependencies

- **yt-dlp** - YouTube video downloader and metadata extractor
- **FFmpeg** - Audio/video processing (installed via Homebrew)
- **tkinter** - GUI toolkit (included with Python)

## License

Use responsibly and respect content creators' rights.

---

**Last updated:** 2026  
**Platform:** macOS only
