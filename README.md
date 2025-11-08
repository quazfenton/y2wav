# Y2Wav - Advanced Audio Downloader & Processor

Y2Wav is a versatile audio/video downloader with advanced metadata embedding and batch processing capabilities. Supports YouTube, SoundCloud, playlists, direct links, and more with extensive customization options.

## Features

### Core Features
- **Multiple Source Support**: YouTube, SoundCloud, Spotify, direct audio/video links
- **Multiple Audio Formats**: FLAC (default), MP3, WAV, OPUS, AAC, M4A
- **Advanced Metadata Embedding**: Full metadata, thumbnails, and source tracking
- **Batch Processing**: Download from text files, JSON, CSV, or M3U playlists
- **Smart Organization**: Organize downloads by source, artist, album, etc.

### GUI Features
- **Intuitive Interface**: Simple tabbed interface for downloads and processing
- **Quality Selection**: Choose from Best, High, Medium, Low quality levels
- **Progress Tracking**: Real-time progress bar and status updates
- **Example URLs**: Quick sample links to test functionality
- **Settings Panel**: Configure metadata, organization, and archive options

### Processing Features
- **Colab Integration**: Process audio with MelBandRoformer in Google Colab
- **Advanced Naming**: Title, numbered, artist-title, date-title, and more
- **Archive Tracking**: Avoid duplicate downloads with archive files
- **Rate Limiting**: Control download speed to avoid throttling
- **Date Filtering**: Download only videos within specific date ranges

## Installation

### System Dependencies
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Fedora/RHEL
sudo dnf install ffmpeg

# macOS
brew install ffmpeg
```

### Python Dependencies
```bash
# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
source venv\Scripts\activate  # On Windows

# Install Python dependencies
pip install -r requirements.txt
```

### Quick Start Script
A start script is provided to help manage the environment:
```bash
# Make it executable
chmod +x start.sh

# Run with automatic environment management
./start.sh --gui
```

## CLI Usage

### Environment Setup
Before running y2wav, make sure you have:
1. Activated your virtual environment (if using one)
2. Installed all dependencies
3. Installed ffmpeg system package

```bash
# Activate virtual environment
source venv/bin/activate

# Or use the start script which handles this automatically
./start.sh [options]
```

### Basic Usage
```bash
# Download from a single URL (FLAC format by default)
python y2wav.py "https://youtube.com/watch?v=..."

# Download from text file (one URL per line)
python y2wav.py urls.txt

# Download multiple URLs
python y2wav.py url1 url2 url3
```

### Format & Quality Options
```bash
# MP3 format
python y2wav.py -f mp3 urls.txt

# WAV format
python y2wav.py -f wav urls.txt

# Best quality audio
python y2wav.py --quality best urls.txt
```

### Naming Schemes
```bash
# Numbered files: 001 - Title.flac
python y2wav.py --naming numbered urls.txt

# Artist - Title.flac
python y2wav.py --naming artist-title urls.txt

# Album/Track - Title.flac
python y2wav.py --naming album-track urls.txt
```

### Organization & Metadata
```bash
# Organize by source in subdirectories
python y2wav.py --organize urls.txt

# Disable thumbnail embedding
python y2wav.py --no-thumbnail urls.txt

# Track downloads to avoid duplicates
python y2wav.py --archive downloads.txt urls.txt
```

### Advanced Options
```bash
# Limit download speed to 1MB/s
python y2wav.py --rate-limit 1M urls.txt

# Use proxy server (e.g., for bypassing restrictions)
python y2wav.py --proxy http://proxy:8080 urls.txt

# Download entire playlist (detected automatically if URL contains &list= parameter)
python y2wav.py -p urls.txt  # or --playlist

# High-quality settings
python y2wav.py --hi-res urls.txt  # or --24bit for high-resolution audio
python y2wav.py --sample-rate 96000 urls.txt  # or -sr 96000
python y2wav.py --bitrate 0 urls.txt  # 0 for best quality

# Only download videos after a specific date
python y2wav.py --date-after 20231201 urls.txt

# Process with Google Colab MelBandRoformer
python y2wav.py --colab-process ./audio_folder
```

### Default GUI Mode
The application now opens the GUI by default when no URLs are provided:
```bash
python y2wav.py  # Opens GUI automatically
python y2wav.py --gui  # Explicit GUI mode
python y2wav.py [URLs or files]  # Command-line mode
```

### High-Quality Audio Settings
The application defaults to the highest quality settings:
- **Format**: FLAC (lossless) by default
- **Bit depth**: Up to 32-bit internal processing for maximum quality
- **Sample rate**: Configurable up to 192kHz
- **Quality**: "best" setting with maximum quality parameters

Use the `--hi-res` or `--24bit` option to enable high-resolution audio processing with 32-bit internal format.

### Proxy Support
To bypass geo-restrictions or anti-bot measures, you can use proxy servers:
```bash
# HTTP proxy
python y2wav.py --proxy http://proxy-server:8080 "https://youtube.com/..."

# SOCKS proxy  
python y2wav.py --proxy socks5://127.0.0.1:1080 "https://youtube.com/..."
```

### Playlist Downloads
To download entire YouTube playlists, simply use the playlist URL or a video URL that contains a playlist parameter (&list=):
```bash
# Downloads all videos in the playlist
python y2wav.py "https://youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID"
```

### Configuration Persistence
Settings are saved to `~/.audio_downloader_config.json` and persist between sessions. Use `python y2wav.py --show-config` to view current settings. The GUI also has a "Save Default Settings" option to permanently store your preferences.

## GUI Usage

Launch the graphical interface with:
```bash
python y2wav.py --gui
```

### Download Tab
1. **URL Input**: Enter URLs one per line, or load from a file
2. **Format Options**: Choose audio format (FLAC, MP3, WAV, etc.) and naming scheme
3. **Quality Options**: Select quality level (Best, High, Medium, Low)
4. **Output Directory**: Set where files will be saved
5. **Download**: Click "Download Audio" to start the process

### Colab Processing Tab
1. **Select Audio Folder**: Choose directory containing audio files to process
2. **Set Output Directory**: Where processed files will be saved
3. **Model Parameters**: Adjust MelBandRoformer settings
4. **Process**: Click "Process with Colab" to prepare files

### Settings Tab
- Enable/disable metadata embedding
- Enable/disable thumbnail embedding
- Organize by source
- Set archive file for duplicate tracking
- Configure rate limiting

## Supported Inputs

### Text Files (.txt)
```
# This is a comment
https://youtube.com/watch?v=...
https://soundcloud.com/artist/track
```

### JSON Files (.json)
```json
[
  "https://youtube.com/watch?v=...",
  {
    "url": "https://soundcloud.com/artist/track",
    "title": "Example Track"
  }
]
```

### CSV Files (.csv)
```
url, title, artist
https://youtube.com/watch?v=..., "Video Title", "Artist Name"
```

### M3U Playlists (.m3u/.m3u8)
```
#EXTM3U
#EXTINF:245,Artist - Title
https://example.com/audio.mp3
```

## Supported Naming Schemes

- `title`: Title.flac (default)
- `numbered`: 001 - Title.flac
- `artist-title`: Artist - Title.flac
- `album-track`: Album/01 - Title.flac
- `date-title`: 20231225 - Title.flac
- `id-title`: VideoID - Title.flac
- `uploader-title`: Uploader - Title.flac

## Colab Integration

Y2Wav includes seamless Google Colab integration for advanced audio processing:

1. Prepare audio files using the Colab tab
2. Upload the generated zip file to your Colab notebook
3. Run the generated code to process with MelBandRoformer
4. Download the processed results

The integration supports:
- MelBandRoformer for source separation
- Configurable segment size and overlap
- GPU acceleration
- Automatic code generation

## Configuration

Settings are saved in `~/.audio_downloader_config.json` and persist between sessions. Use `python y2wav.py --show-config` to view current settings.

## Troubleshooting

### Dependencies
If you encounter "Missing dependencies" errors:
1. Ensure yt-dlp is installed: `pip install yt-dlp`
2. Ensure ffmpeg is installed via your system package manager
3. Check that both are accessible from your command line

### YouTube Download Issues
YouTube frequently updates their anti-bot measures which can temporarily break downloads. y2wav includes multiple strategies to handle these issues:

1. **Retry Logic**: The application automatically tries different approaches if the first one fails
2. **Multiple Player Clients**: Uses different YouTube client types to bypass restrictions  
3. **User-Agent Spoofing**: Uses browser-like headers to appear less like a bot
4. **Rate Limiting**: Includes sleep intervals to reduce detection

If downloads consistently fail:
- Try using the `--rate-limit` option to slow down requests
- Use a VPN if access is geo-restricted  
- Update yt-dlp to the latest version: `yt-dlp -U`
- Some videos may have additional restrictions that prevent downloading

### Rate Limiting
If downloads fail due to rate limiting, use `--rate-limit` with a limit like `1M` for 1MB/s.

### Geoblocking
For region-restricted content, use `--geo-bypass` to attempt to bypass geographic restrictions.

## Contributing

Pull requests are welcome! Please ensure tests pass and follow the existing code style.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is intended for downloading audio from sources where you have the right to do so. Please respect copyright laws and the terms of service of the platforms you are downloading from.