# YouTube to MP3 Converter

A beautiful, modern web application to download and convert YouTube videos to high-quality MP3 audio.

## Quick Start

### Option 1: Modern Web App (Recommended) ⭐

Beautiful Next.js web interface with animations and professional design.

```bash
# One-time setup
bash setup.sh

# Terminal 1: Start backend
cd api && source venv/bin/activate && python app.py

# Terminal 2: Start frontend
cd web && npm run dev

# Open http://localhost:3000
```

📖 **Full guide:** See [README_WEB.md](README_WEB.md)

### Option 2: Desktop App (Python)

Traditional desktop app using Python and tkinter.

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

## Features

✨ **Modern Web UI** - React, Next.js, shadcn/ui  
🎨 **Beautiful Animations** - Infinite grid background with framer-motion  
📥 **Easy Downloads** - Simple, intuitive interface  
🎵 **High Quality** - 128, 192, 256, 320 kbps MP3 conversion  
💻 **Local & Private** - Runs on your machine, no uploads  
🚀 **Fast & Responsive** - Real-time status updates  

## Requirements

### For Web App
- Node.js 18+
- Python 3.8+
- FFmpeg (`brew install ffmpeg` on macOS)

### For Desktop App
- Python 3.8+
- FFmpeg (`brew install ffmpeg` on macOS)

## Project Structure

```
yt2mp3/
├── web/                    # Next.js web app (recommended)
├── api/                    # Python Flask backend
├── app.py                  # Old tkinter desktop app
├── setup.sh               # Automated setup script
└── README_WEB.md          # Full web app documentation
```

## Legal Notice

⚠️ **For Personal Use Only**

This tool is for downloading content you have rights to. Respect copyright and content creators' rights. Do not use for:
- Copyrighted content without permission
- Commercial purposes
- Violating YouTube's Terms of Service

## Support

Having issues? Check [README_WEB.md](README_WEB.md) for troubleshooting.

---

**Built with Next.js, React, Tailwind CSS, Python, and yt-dlp**
