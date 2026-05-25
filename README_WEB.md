# YouTube to MP3 Converter - Web App

A modern, beautiful web application to download and convert YouTube videos to high-quality MP3 audio. Built with Next.js, React, and Python Flask. Created this to use audio from youtube for video editing.

## Features

✨ **Modern Web UI** - Beautiful React interface with Tailwind CSS and shadcn/ui  
🎨 **Infinite Grid Background** - Eye-catching animated background with framer-motion  
📥 **Easy Downloads** - Simple URL input and quality selection  
🎵 **High Quality** - Support for 128, 192, 256, and 320 kbps MP3 conversion  
⚡ **Fast & Responsive** - Real-time status updates and smooth animations  
💻 **Local Processing** - Runs entirely on your machine, no cloud uploads  

## Architecture

```
┌─────────────────────────────┐         ┌──────────────────────────┐
│    Frontend (Next.js)       │         │   Backend (Python)       │
│  ├── React Components       │         │  ├── Flask API           │
│  ├── shadcn/ui Components   │─API───→ │  ├── yt-dlp             │
│  ├── Tailwind CSS           │  calls  │  ├── ffmpeg             │
│  └── Framer Motion          │←Response│  └── CORS handling      │
└─────────────────────────────┘         └──────────────────────────┘
       (localhost:3000)                     (localhost:5000)
```

## Requirements

### Frontend
- Node.js 18+
- npm or yarn

### Backend
- Python 3.8+
- FFmpeg (for audio conversion)

## Installation & Setup

### 1. Install FFmpeg (macOS)

```bash
brew install ffmpeg
```

If you don't have Homebrew, install it from https://brew.sh

### 2. Backend Setup

Navigate to the `api` directory and create a virtual environment:

```bash
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Frontend Setup

Navigate to the `web` directory and install dependencies:

```bash
cd ../web
npm install
```

## Running the App

You need to run **two terminals** - one for the backend API and one for the frontend.

### Terminal 1: Start the Python Backend

```bash
cd api
source venv/bin/activate
python app.py
```

You should see:
```
✓ Download folder: /Users/rainier/Downloads/YouTube MP3s
✓ Starting Flask API server on http://localhost:5000
```

### Terminal 2: Start the Next.js Frontend

```bash
cd web
npm run dev
```

You should see:
```
➜  Local:        http://localhost:3000
```

### 3. Open in Browser

Visit **http://localhost:3000** in your web browser and start downloading!

## Usage

1. **Enter a YouTube URL** - Paste a direct link to a YouTube video
2. **Select Quality** - Choose your desired MP3 bitrate (128-320 kbps)
3. **Click Download** - The app will fetch, convert, and save the MP3
4. **Find Your File** - MP3 is saved to `~/Downloads/YouTube MP3s/`

## Project Structure

```
yt2mp3/
├── web/                          # Next.js Frontend
│   ├── app/
│   │   ├── page.tsx             # Main page
│   │   └── globals.css          # Global styles
│   ├── components/
│   │   ├── ui/
│   │   │   ├── infinite-grid.tsx # Animated background
│   │   │   ├── button.tsx        # shadcn button
│   │   │   ├── input.tsx         # shadcn input
│   │   │   └── select.tsx        # shadcn select
│   │   └── youtube-converter.tsx # Main converter component
│   ├── lib/
│   │   └── utils.ts             # Utility functions
│   ├── tailwind.config.ts        # Tailwind configuration
│   ├── package.json             # Frontend dependencies
│   └── next.config.ts           # Next.js configuration
│
├── api/                          # Python Flask Backend
│   ├── app.py                   # Flask API server
│   ├── requirements.txt          # Python dependencies
│   └── venv/                    # Virtual environment
│
├── README_WEB.md                # This file
└── .gitignore                   # Git ignore rules
```

## API Endpoints

### Health Check
```
GET /api/health
```

Returns API status and FFmpeg availability.

### Download Video
```
POST /api/download
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=...",
  "bitrate": "320"
}
```

Returns downloaded video info and save location.

### Get Available Formats
```
GET /api/formats
```

Returns list of available quality options.

## Troubleshooting

### "FFmpeg is not installed"
```bash
brew install ffmpeg
```

### Backend API not responding
- Check if backend is running on Terminal 1
- Ensure port 5000 is not in use
- Try: `lsof -i :5000` to see what's using the port

### Frontend won't connect to backend
- Check backend is running (should see logs on Terminal 1)
- Verify both are on localhost (frontend 3000, backend 5000)
- Check browser console for CORS errors

### Slow downloads
- Check your internet connection
- Try a shorter/smaller video first
- Ensure enough disk space in ~/Downloads/

## Dependencies

### Frontend
- **next** - React framework
- **react** - UI library
- **tailwindcss** - Styling framework
- **framer-motion** - Animations
- **shadcn/ui** - Component library
- **axios** - HTTP client
- **typescript** - Type safety

### Backend
- **Flask** - Web framework
- **Flask-CORS** - Cross-Origin Resource Sharing
- **yt-dlp** - YouTube downloader
- **ffmpeg** - Audio conversion (system dependency)

## File Size Estimates

MP3 file size depends on video duration and quality:

| Quality | File Size | Duration |
|---------|-----------|----------|
| 128 kbps | 4-5 MB | per minute |
| 192 kbps | 6-7 MB | per minute |
| 256 kbps | 8-9 MB | per minute |
| 320 kbps | 10-12 MB | per minute |

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

## Performance Tips

1. **First download is slowest** - Subsequent downloads are faster
2. **Avoid peak hours** - YouTube may rate-limit during peak times
3. **Shorter videos** - Download faster and use less bandwidth
4. **Higher quality** - Takes more time but produces better audio

## Advanced: Deploy to Cloud

To deploy this app to production (Vercel, Heroku, etc.):

1. **Frontend** - Deploy `web` directory to Vercel (free for Next.js)
2. **Backend** - Deploy `api` directory to Heroku or similar
3. **Update API URL** - Change `API_URL` in `youtube-converter.tsx`

See framework docs for deployment instructions.

## Contributing

To improve the app:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally (run both frontend and backend)
5. Submit a pull request

## License

Use responsibly and respect content creators' rights.

---

**Built with:**
- ⚛️ React & Next.js
- 🎨 Tailwind CSS & shadcn/ui
- 🎬 yt-dlp & FFmpeg
- 🐍 Python & Flask
- ✨ Framer Motion

**Last Updated:** May 2026  
**Platform:** macOS, Linux, Windows (with WSL)
