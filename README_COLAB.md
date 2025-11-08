# 🎵 Y2Wav with Google Colab Integration

Enhanced audio downloader with **Google Colab MelBandRoformer** integration for professional audio source separation and processing.

## 🆕 New Features

### 1. **Google Colab Integration**
Process your downloaded audio files with MelBandRoformer AI model for:
- Audio source separation (vocals, drums, bass, other)
- High-quality audio processing
- GPU-accelerated processing in the cloud
- Professional-grade results

### 2. **Graphical User Interface (GUI)**
User-friendly interface for:
- Easy URL input and file management
- Visual configuration of settings
- Real-time log output
- Integrated Colab workflow

### 3. **Seamless Workflow**
Download → Process → Export in one integrated tool

---

## 📦 Installation

### Basic Requirements
```bash
# Install Python dependencies
pip install yt-dlp

# Install ffmpeg (if not already installed)
# Ubuntu/Debian:
sudo apt install ffmpeg

# macOS:
brew install ffmpeg
```

### GUI Requirements (Optional)
```bash
# GUI uses tkinter (usually pre-installed with Python)
# If not available:
# Ubuntu/Debian:
sudo apt install python3-tk

# macOS: Already included with Python
```

---

## 🚀 Quick Start

### Method 1: Command Line Interface (CLI)

#### Download Audio
```bash
# Basic download
python y2wav.py "https://youtube.com/watch?v=..."

# Download from file
python y2wav.py urls.txt

# Download as MP3
python y2wav.py -f mp3 urls.txt
```

#### Process with Colab
```bash
# Process audio folder with MelBandRoformer
python y2wav.py --colab-process ./downloads

# With custom output directory
python y2wav.py --colab-process ./my_audio --colab-output ./processed

# Custom model parameters
python y2wav.py --colab-process ./audio \
  --colab-segment-size 512 \
  --colab-overlap 0.5

# Don't open browser automatically
python y2wav.py --colab-process ./audio --no-browser
```

### Method 2: Graphical User Interface (GUI)

```bash
# Launch GUI
python y2wav.py --gui

# Or directly:
python gui.py
```

The GUI provides:
- **Download Tab**: Input URLs, configure format, start downloads
- **Colab Processing Tab**: Select audio folder, configure MelBandRoformer, process
- **Settings Tab**: Configure metadata, archive, rate limiting
- **Log Output**: Real-time status updates

---

## 📖 Complete Workflow Examples

### Example 1: Download and Process Playlist

```bash
# Step 1: Download playlist as FLAC
python y2wav.py -f flac -o ./my_playlist \
  "https://youtube.com/playlist?list=PLxxxxxx"

# Step 2: Process with Colab
python y2wav.py --colab-process ./my_playlist \
  --colab-output ./my_playlist_processed
```

### Example 2: Batch Download and Process

```bash
# Step 1: Create URL list (urls.txt)
echo "https://youtube.com/watch?v=abc123" > urls.txt
echo "https://youtube.com/watch?v=def456" >> urls.txt

# Step 2: Download all as WAV
python y2wav.py -f wav -o ./batch_downloads urls.txt

# Step 3: Process with custom settings
python y2wav.py --colab-process ./batch_downloads \
  --colab-segment-size 512 \
  --colab-overlap 0.25
```

### Example 3: Using GUI Workflow

1. Launch GUI: `python y2wav.py --gui`
2. **Download Tab**:
   - Paste URLs or load from file
   - Select format (FLAC recommended for processing)
   - Set output directory
   - Click "Download Audio"
3. **Colab Processing Tab**:
   - Browse to select downloaded audio folder
   - Configure MelBandRoformer parameters
   - Click "Process with Colab"
4. **In Google Colab**:
   - Upload the generated `audio_files.zip`
   - Run the auto-generated code
   - Download `processed_audio.zip`

---

## 🎛️ Colab Processing Parameters

### Model Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--colab-segment-size` | 256 | Segment size for processing (higher = more VRAM, better quality) |
| `--colab-overlap` | 0.25 | Overlap between segments (0.0 - 1.0) |
| GPU | Auto | Automatically uses GPU if available in Colab |

### Recommended Settings

**High Quality (Recommended)**
```bash
python y2wav.py --colab-process ./audio \
  --colab-segment-size 512 \
  --colab-overlap 0.5
```

**Fast Processing**
```bash
python y2wav.py --colab-process ./audio \
  --colab-segment-size 256 \
  --colab-overlap 0.25
```

**Maximum Quality (Requires more time)**
```bash
python y2wav.py --colab-process ./audio \
  --colab-segment-size 1024 \
  --colab-overlap 0.75
```

---

## 📁 File Structure

After running, you'll find:

```
your_project/
├── downloads/              # Downloaded audio files
│   ├── song1.flac
│   ├── song2.flac
│   └── ...
├── processed_audio/        # Processed output (after Colab)
│   ├── processed_song1.wav
│   ├── processed_song2.wav
│   ├── colab_processing_code.py  # Generated Colab code
│   └── ...
└── /tmp/
    └── audio_files.zip     # Temporary zip for upload
```

---

## 🔧 Advanced Usage

### Custom Colab Notebook

Use your own Colab notebook:
```bash
python y2wav.py --colab-process ./audio \
  --colab-notebook "https://colab.research.google.com/drive/YOUR_NOTEBOOK_ID"
```

### Programmatic Usage

```python
from colab_integration import ColabIntegration

# Initialize
colab = ColabIntegration()

# Process audio folder
result = colab.process_audio_folder(
    input_dir="./my_audio",
    output_dir="./processed",
    model_params={
        "segment_size": 512,
        "overlap": 0.5,
        "use_gpu": True
    },
    open_browser=True
)

print(f"Status: {result['status']}")
print(f"Zip file: {result['zip_path']}")
print(f"Audio files: {result['audio_files_count']}")
```

---

## 🎯 Use Cases

### 1. Music Production
```bash
# Download stems from YouTube
python y2wav.py -f flac -o ./stems urls.txt

# Separate sources with MelBandRoformer
python y2wav.py --colab-process ./stems
```

### 2. Podcast Processing
```bash
# Download podcast episodes
python y2wav.py -f mp3 -o ./podcasts podcast_urls.txt

# Enhance audio quality
python y2wav.py --colab-process ./podcasts
```

### 3. Audio Research
```bash
# Download high-quality audio
python y2wav.py -f wav -o ./research research_urls.txt

# Process for analysis
python y2wav.py --colab-process ./research \
  --colab-segment-size 1024
```

### 4. Remix/Mashup Creation
```bash
# Download songs
python y2wav.py -f flac -o ./remix songs.txt

# Separate vocals and instrumentals
python y2wav.py --colab-process ./remix
```

---

## 🐛 Troubleshooting

### GUI doesn't launch
```bash
# Check if tkinter is installed
python -c "import tkinter"

# If error, install tkinter:
# Ubuntu/Debian:
sudo apt install python3-tk

# macOS: Reinstall Python from python.org
```

### Colab integration not working
```bash
# Verify files are in same directory
ls audi0z/y2wav/
# Should see: y2wav.py, colab_integration.py, gui.py

# Test colab module directly
python colab_integration.py ./test_audio
```

### Browser doesn't open
```bash
# Use --no-browser flag and open manually
python y2wav.py --colab-process ./audio --no-browser

# Then manually open the notebook URL shown in output
```

### Upload fails in Colab
- Check zip file size (Colab has upload limits)
- Try processing in smaller batches
- Ensure stable internet connection

---

## 📊 Comparison: Before vs After

### Before (Basic y2wav)
```bash
python y2wav.py urls.txt
# Output: Downloaded audio files
```

### After (With Colab Integration)
```bash
# Download
python y2wav.py -f flac -o ./audio urls.txt

# Process with AI
python y2wav.py --colab-process ./audio

# Result: Professional-grade processed audio with source separation
```

---

## 🎓 MelBandRoformer Background

**MelBandRoformer** is a state-of-the-art AI model for audio source separation:
- Separates vocals, drums, bass, and other instruments
- Uses transformer architecture with mel-spectrogram bands
- Trained on large datasets of music
- Achieves professional-quality results
- GPU-accelerated for fast processing

**Colab Notebook**: [MelBandRoformer Colab](https://colab.research.google.com/drive/1tyP3ZgcD443d4Q3ly7LcS3toJroLO5o1)

---

## 📝 Tips & Best Practices

1. **Use FLAC or WAV for processing**: Lossless formats preserve quality
2. **Start with default parameters**: Then adjust based on results
3. **Process in batches**: Avoid overwhelming Colab with too many files
4. **Save your settings**: GUI remembers your preferences
5. **Archive downloads**: Use `--archive` to track processed files
6. **Check file sizes**: Large files take longer to upload/process

---

## 🤝 Integration with Other Tools

### Export to DAW
```bash
# Download and process
python y2wav.py --colab-process ./tracks

# Processed files are ready for:
# - Ableton Live
# - FL Studio
# - Logic Pro
# - Pro Tools
# - Reaper
```

### Batch Processing Script
```bash
#!/bin/bash
# batch_process.sh

# Download
python y2wav.py -f flac -o ./batch "$@"

# Process
python y2wav.py --colab-process ./batch \
  --colab-output ./batch_processed

echo "Complete! Check ./batch_processed/"
```

Usage:
```bash
./batch_process.sh urls.txt
```

---

## 📚 Additional Resources

- **Original y2wav**: See `y2wav.md` for download options
- **Colab Notebook**: [MelBandRoformer](https://colab.research.google.com/drive/1tyP3ZgcD443d4Q3ly7LcS3toJroLO5o1)
- **yt-dlp**: [Documentation](https://github.com/yt-dlp/yt-dlp)
- **FFmpeg**: [Official Site](https://ffmpeg.org/)

---

## 🆘 Support

For issues related to:
- **Downloading**: Check yt-dlp documentation
- **Colab Processing**: Check Colab notebook comments
- **GUI**: Ensure tkinter is installed
- **Integration**: Verify all modules are in same directory

---

## 📄 License

This tool extends y2wav with Google Colab integration. All original licenses apply.

---

**Happy downloading and processing! 🎵**
