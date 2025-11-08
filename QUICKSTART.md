# 🚀 Y2Wav + Colab Integration - Quick Start

## 30-Second Overview

**Y2Wav** is now a complete audio production tool:
1. **Download** audio from YouTube and 1000+ sites
2. **Process** with AI-powered MelBandRoformer in Google Colab
3. **Export** professional-quality separated audio

## 🎯 Choose Your Interface

### Option 1: Graphical Interface (Easiest)
```bash
python3 y2wav.py --gui
```
- Point and click interface
- Visual feedback
- Perfect for beginners

### Option 2: Command Line (Most Powerful)
```bash
# Download
python3 y2wav.py -f flac -o ./audio urls.txt

# Process with Colab
python3 y2wav.py --colab-process ./audio
```
- Full automation
- Script-friendly
- Advanced options

## 📋 Installation (One-Time)

```bash
# Install Python dependencies
pip install yt-dlp

# Install ffmpeg (system package)
# Ubuntu/Debian:
sudo apt install ffmpeg

# macOS:
brew install ffmpeg

# Windows: Download from https://ffmpeg.org/
```

## ⚡ Common Workflows

### Workflow 1: Download + Process Single Video

```bash
# Step 1: Download
python3 y2wav.py -f flac -o ./mysong "https://youtube.com/watch?v=..."

# Step 2: Process
python3 y2wav.py --colab-process ./mysong

# Step 3: Upload audio_files.zip to Colab (opens automatically)
# Step 4: Run code in Colab
# Step 5: Download processed_audio.zip
```

### Workflow 2: Download + Process Playlist

```bash
# Step 1: Download entire playlist
python3 y2wav.py -f flac \
  --naming numbered \
  -o ./playlist \
  "https://youtube.com/playlist?list=PLxxxxxx"

# Step 2: Process all songs
python3 y2wav.py --colab-process ./playlist \
  --colab-segment-size 512
```

### Workflow 3: Use GUI

```bash
# Launch GUI
python3 y2wav.py --gui
```

Then:
1. **Download Tab**: Paste URLs → Click "Download Audio"
2. **Colab Tab**: Select folder → Click "Process with Colab"
3. Follow browser instructions

## 🎛️ Essential Options

### Download Options
```bash
-f FORMAT           # Audio format (flac, mp3, wav, opus, aac)
-o DIR              # Output directory
--naming SCHEME     # File naming (title, numbered, artist-title)
--archive FILE      # Track downloads (avoid duplicates)
```

### Colab Options
```bash
--colab-process DIR          # Process audio folder
--colab-segment-size NUM     # Quality (256=fast, 512=balanced, 1024=best)
--colab-overlap FLOAT        # Overlap ratio (0.25=fast, 0.5=better)
--colab-output DIR           # Where to save processed files
--no-browser                 # Don't open browser
```

### GUI Option
```bash
--gui               # Launch graphical interface
```

## 🔥 Real-World Examples

### Example 1: Music Producer
```bash
# Download stems for remixing
python3 y2wav.py -f flac -o ./remix \
  "https://youtube.com/watch?v=..."

python3 y2wav.py --colab-process ./remix \
  --colab-segment-size 512
```
**Result**: Separated vocals, drums, bass, other

### Example 2: Podcast Editor
```bash
# Batch download episodes
python3 y2wav.py -f mp3 \
  --naming numbered \
  -o ./podcast \
  episodes.txt

python3 y2wav.py --colab-process ./podcast
```
**Result**: Enhanced, cleaned audio

### Example 3: DJ/Mashup Artist
```bash
# Download multiple tracks
python3 y2wav.py -f wav -o ./tracks urls.txt

# Separate all sources
python3 y2wav.py --colab-process ./tracks \
  --colab-segment-size 1024
```
**Result**: Acapellas and instrumentals ready to mix

## 📊 Format Recommendations

| Use Case | Format | Why |
|----------|--------|-----|
| **Colab Processing** | FLAC or WAV | Lossless = best results |
| **Portable Music** | MP3 or Opus | Small size, compatible |
| **Production/DAW** | WAV | Universal DAW support |
| **Archival** | FLAC | Lossless + metadata |

## 🎓 Understanding Parameters

### Segment Size (--colab-segment-size)
- **256**: Fast, lower quality (default)
- **512**: Balanced (recommended)
- **1024**: Best quality, slower

### Overlap (--colab-overlap)
- **0.25**: Fast processing (default)
- **0.5**: Better results (recommended)
- **0.75**: Maximum quality

## 🐛 Troubleshooting

### "yt-dlp not found"
```bash
pip install yt-dlp
# or
pip install --upgrade yt-dlp
```

### "ffmpeg not found"
```bash
# Ubuntu/Debian:
sudo apt install ffmpeg

# macOS:
brew install ffmpeg

# Verify:
ffmpeg -version
```

### GUI doesn't launch
```bash
# Install tkinter
# Ubuntu/Debian:
sudo apt install python3-tk

# Test:
python3 -c "import tkinter"
```

### "No audio files found"
Make sure your folder contains supported formats:
- `.wav`, `.mp3`, `.flac`, `.ogg`, `.m4a`, `.aac`, `.opus`

## 💡 Pro Tips

1. **Use FLAC for processing**: Best quality input = best output
2. **Archive downloads**: `--archive downloads.txt` avoids re-downloading
3. **Start with defaults**: Then adjust based on results
4. **Process in batches**: Don't upload 100+ files at once
5. **Save generated code**: Reuse for similar processing tasks

## 📚 Learn More

- **Full Documentation**: See `README_COLAB.md`
- **Technical Details**: See `FEATURE_SUMMARY.md`
- **Original Features**: See `y2wav.md`
- **Demo Script**: Run `./demo.sh`

## 🎉 You're Ready!

Start with the simplest command:
```bash
python3 y2wav.py --gui
```

Or dive into the CLI:
```bash
python3 y2wav.py "https://youtube.com/watch?v=..." -f flac
python3 y2wav.py --colab-process ./downloads
```

**Happy audio processing! 🎵**

---

Need help? Check the full documentation in `README_COLAB.md`
