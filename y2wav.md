# 🎵 Versatile Audio Downloader

A powerful, feature-rich command-line tool for downloading audio from YouTube, playlists, and countless other sources with intelligent defaults and extensive customization.

Versatile bulk Youtube downloader or external link audio/video downloader

Smart inputs- can handle everything from CLI  input 
[ ex. pasting n individual video you want, easily,  terminal, even able to retrieve ALL from a SINGLE playlist link ]  

to ENTIRE bulks of media given a txt file or curation of link data
and MORE!
Smart retrieval with NO extra info required by the script


Defaults and persistent configuration. This will use `yt-dlp` for downloading and `ffmpeg` for audio processing.I've created a comprehensive audio downloader script with all the features you requested. Here's what it does:
## ✨ Key Features

### 🎯 Smart Defaults
- **FLAC lossless** audio at highest available bitrate
- **Automatic metadata embedding** including source URLs and playlist info
- **Title-based naming** using original video/page titles
- **Persistent preferences** that remember your settings
- **Video mode is temporary** - always reverts to audio after use

### 🔄 Versatile Input
- Direct URLs (YouTube, SoundCloud, Spotify, etc.)
- Text files (`.txt`) with line-separated URLs
- JSON files (`.json`) with flexible structures
- CSV files (`.csv`) with URLs in any column
- M3U playlists (`.m3u`, `.m3u8`)
- Mixed text with space/comma-separated URLs
- URLs without `https://` prefix (auto-adds)

### 🎬 Source Support
- **YouTube** videos and playlists (auto-detects)
- **SoundCloud** tracks and playlists
- **Spotify** (with appropriate yt-dlp extractors)
- **Direct audio links** (`.mp3`, `.flac`, `.wav`, etc.)
- **Generic web pages** (auto-extracts media)
- **1000+ sites** supported by yt-dlp

### 📋 Naming Schemes
- `title` - Song Title.flac *(default)*
- `numbered` - 001 - Song Title.flac
- `artist-title` - Artist Name - Song Title.flac
- `album-track` - Album/01 - Song Title.flac
- `date-title` - 20231225 - Song Title.flac
- `id-title` - VideoID - Song Title.flac
- `uploader-title` - Channel Name - Song Title.flac

### 📦 Audio Formats
- **FLAC** - Lossless, compression level 0 *(default)*
- **WAV** - Uncompressed PCM 24-bit
- **MP3** - VBR quality 0 (~245 kbps)
- **Opus** - Excellent quality/size ratio
- **AAC** - High-quality lossy
- **M4A** - Apple audio format
- **Vorbis** - Open-source codec

### 🛡️ Advanced Features
- **Download archive** - Skip previously downloaded URLs
- **Rate limiting** - Control bandwidth usage
- **Date filtering** - Download only from specific time periods
- **Geo-bypass** - Automatic geographic restriction bypass
- **Retry logic** - Configurable retry attempts
- **Batch processing** - Handle thousands of URLs
- **Resume capability** - Skip existing files
- **Error recovery** - Continue on individual failures

---

## 🚀 Quick Start

### Installation

```bash
# 1. Install yt-dlp
pip install yt-dlp

# 2. Install ffmpeg
# Ubuntu/Debian:
sudo apt install ffmpeg

# macOS (with Homebrew):
brew install ffmpeg

# Windows:
# Download from https://ffmpeg.org/ and add to PATH

# 3. Verify installation
yt-dlp --version
ffmpeg -version
```

### Basic Usage

```bash
# Download from a text file (one URL per line)
python downloader.py urls.txt

# Download a single YouTube video
python downloader.py "https://youtube.com/watch?v=dQw4w9WgXcQ"

# Download entire playlist (auto-detects)
python downloader.py "https://youtube.com/playlist?list=PLxxxxxx"

# Download multiple URLs
python downloader.py "url1" "url2" "url3"
```

---

## 📖 Comprehensive Examples

### Format Selection

```bash
# Download as MP3 (becomes new default)
python downloader.py -f mp3 urls.txt

# High-quality WAV (24-bit PCM)
python downloader.py -f wav urls.txt

# Space-efficient Opus
python downloader.py -f opus urls.txt

# Download video (temporary, doesn't persist)
python downloader.py --video urls.txt
```

### Naming & Organization

```bash
# Numbered files for playlists
python downloader.py --naming numbered playlist.txt
# Output: 001 - First Song.flac, 002 - Second Song.flac

# Artist - Title format
python downloader.py --naming artist-title urls.txt
# Output: The Beatles - Hey Jude.flac

# Date-based naming
python downloader.py --naming date-title urls.txt
# Output: 20231225 - Song Title.flac

# Organize by source platform
python downloader.py -o ~/Music --organize urls.txt
# Output: ~/Music/YouTube/song1.flac, ~/Music/SoundCloud/song2.flac

# Custom template (advanced)
python downloader.py -t "%(artist)s/%(album)s/%(title)s.%(ext)s" urls.txt
# Output: Artist/Album/Title.flac
```

### Download Management

```bash
# Track downloads to avoid duplicates
python downloader.py --archive ~/downloads.txt urls.txt
# Run again - skips already downloaded URLs

# Limit speed to 1 MB/s
python downloader.py --rate-limit 1M urls.txt

# Download only recent videos
python downloader.py --date-after 20231201 urls.txt

# Date range (entire year 2023)
python downloader.py --date-after 20230101 --date-before 20231231 urls.txt

# More retries for unreliable connections
python downloader.py --retries 10 urls.txt
```

### Metadata Control

```bash
# Disable all metadata
python downloader.py --no-metadata urls.txt

# Disable only thumbnails
python downloader.py --no-thumbnail urls.txt

# Don't embed source URLs
python downloader.py --no-source-url urls.txt

# Minimal files (no metadata, no thumbnails)
python downloader.py --no-metadata --no-thumbnail urls.txt
```

### Advanced Workflows

```bash
# Complete archival setup
python downloader.py \
  -f flac \
  -o ~/Music/Archive \
  --naming date-title \
  --organize \
  --archive ~/.audio_archive.txt \
  --rate-limit 2M \
  urls.txt

# Fast MP3 batch download
python downloader.py \
  -f mp3 \
  --no-thumbnail \
  --rate-limit 5M \
  --archive ~/mp3_downloads.txt \
  huge_list.txt

# Numbered playlist with custom padding
python downloader.py \
  --naming numbered \
  --padding 4 \
  -o ./Playlists/MyPlaylist \
  "https://youtube.com/playlist?list=PLxxxxxx"
# Output: 0001 - Song.flac, 0002 - Song.flac, etc.
```

---

## 📁 Input File Formats

### Text File (`urls.txt`)
```
https://youtube.com/watch?v=abc123
https://youtube.com/watch?v=def456
# Lines starting with # are comments
https://youtube.com/watch?v=ghi789  # Inline comments work too

# Multiple URLs per line (space-separated)
url1 url2 url3
```

### JSON File (`playlist.json`)

**Array format:**
```json
[
  "https://youtube.com/watch?v=abc",
  "https://youtube.com/watch?v=def",
  "https://youtube.com/watch?v=ghi"
]
```

**Object format:**
```json
{
  "playlist_name": "My Favorites",
  "urls": [
    "https://youtube.com/watch?v=abc",
    "https://youtube.com/watch?v=def"
  ]
}
```

**Detailed object format:**
```json
[
  {
    "url": "https://youtube.com/watch?v=abc",
    "title": "Song 1",
    "artist": "Artist A"
  },
  {
    "url": "https://youtube.com/watch?v=def",
    "title": "Song 2",
    "artist": "Artist B"
  }
]
```

### CSV File (`songs.csv`)
```csv
title,artist,url,year
"Song 1","Artist A","https://youtube.com/watch?v=abc",2023
"Song 2","Artist B","https://youtube.com/watch?v=def",2024
```
*URLs are automatically extracted from any column*

### M3U Playlist (`playlist.m3u`)
```
#EXTM3U
#EXTINF:123,Artist - Song Title
https://youtube.com/watch?v=abc123
#EXTINF:234,Artist 2 - Song Title 2
https://youtube.com/watch?v=def456
```

---

## ⚙️ Configuration

### View Current Settings
```bash
python downloader.py --show-config
```

Output:
```
==============================================================
CURRENT CONFIGURATION
==============================================================
  archive_file             : None
  embed_metadata           : True
  embed_playlist_url       : True
  embed_source_url         : True
  embed_thumbnail          : True
  format                   : flac
  geo_bypass               : True
  naming_scheme            : title
  number_padding           : 3
  organize_by_source       : False
  output_dir               : ./downloads
  output_template          : %(title)s.%(ext)s
  prefer_free_formats      : False
  quality                  : best
  rate_limit               : None
  retries                  : 3
==============================================================
```

### Reset to Defaults
```bash
python downloader.py --reset
```

### Configuration Persistence
Settings are automatically saved in `~/.audio_downloader_config.json`:
- Format preferences
- Output directories
- Naming schemes
- Metadata options
- Download settings

**Exception:** Video format (`--video`) never persists - always reverts to audio.

---

## 🎯 Use Cases & Workflows

### Personal Music Library
```bash
# Setup
python downloader.py \
  -f flac \
  -o ~/Music \
  --naming artist-title \
  --organize \
  --archive ~/.music_downloads.txt

# Daily use - just add URLs to favorites.txt
python downloader.py favorites.txt
```

### Podcast/Educational Content
```bash
python downloader.py \
  -f mp3 \
  -o ~/Podcasts \
  --naming date-title \
  --organize \
  podcast_episodes.txt
```

### Playlist Archival
```bash
# Download entire channel's uploads
python downloader.py \
  --naming numbered \
  --padding 4 \
  -o "./Archive/[Channel Name]" \
  "https://youtube.com/c/ChannelName/videos"

# Download curated playlist
python downloader.py \
  --naming numbered \
  "https://youtube.com/playlist?list=PLxxxxxx"
```

### Batch Conversion
```bash
# Convert existing URLs to different format
python downloader.py -f opus existing_urls.txt
```

### Quick Downloads (No Metadata)
```bash
# Fast downloads without extras
python downloader.py \
  -f mp3 \
  --no-metadata \
  --no-thumbnail \
  --rate-limit 10M \
  quick_list.txt
```

---

## 🔍 URL Format Examples

The script intelligently handles various URL formats:

```bash
# Full URLs
https://youtube.com/watch?v=abc123
https://www.youtube.com/watch?v=abc123
https://youtu.be/abc123

# Without protocol (auto-added)
youtube.com/watch?v=abc123
www.youtube.com/watch?v=abc123
youtu.be/abc123

# Playlists (auto-detected)
https://youtube.com/playlist?list=PLxxxxxx
https://youtube.com/watch?v=abc&list=PLxxxxxx

# Direct audio files
https://example.com/audio/song.mp3
https://example.com/music/track.flac
https://cdn.example.com/files/audio.wav

# Generic web pages (extracts media)
https://soundcloud.com/artist/track
https://example.com/music/song-page
https://bandcamp.com/track/song-title

# Other platforms
https://vimeo.com/123456789
https://dailymotion.com/video/x7xxxxx
https://twitter.com/user/status/123456789
```

---

## 📊 Quality Settings by Format

| Format | Quality Setting | Bitrate/Details |
|--------|----------------|-----------------|
| **FLAC** | Compression 0 | Lossless, fastest compression |
| **WAV** | PCM 24-bit | Uncompressed lossless |
| **MP3** | VBR Quality 0 | ~245 kbps average (highest) |
| **Opus** | VBR Quality 0 | ~128-256 kbps (excellent) |
| **AAC** | VBR Quality 0 | ~192-256 kbps |
| **M4A** | VBR Quality 0 | ~192-256 kbps |
| **Vorbis** | VBR Quality 0 | ~160-320 kbps |

*All formats use "best available" source quality*

---

## 🛠️ Troubleshooting

### "ERROR: Missing dependencies"
```bash
# Update yt-dlp
pip install --upgrade yt-dlp

# Verify ffmpeg installation
ffmpeg -version

# Install ffmpeg if missing (see Installation section)
```

### "No valid URLs found"
- Check file encoding (should be UTF-8)
- Verify URLs are complete (include `https://`)
- Remove any special characters or formatting
- Try testing with a single URL first

### Download Failures
```bash
# Try with more retries
python downloader.py --retries 10 urls.txt

# Check verbose output
yt-dlp --verbose "URL"

# Update yt-dlp (fixes most issues)
pip install --upgrade yt-dlp
```

### Geographic Restrictions
```bash
# Geo-bypass is enabled by default
# If still blocked, yt-dlp will show specific error

# Some platforms may require cookies
# Check yt-dlp documentation for cookie extraction
```

### Metadata Not Embedding
```bash
# Ensure ffmpeg is installed properly
ffmpeg -version

# Check if metadata option is enabled
python downloader.py --show-config

# Try re-enabling if disabled
python downloader.py --reset
```

---

## 🤝 Tips & Best Practices

1. **Use Archive Files**: Always use `--archive` for large collections to avoid re-downloading
2. **Rate Limiting**: Be respectful - use `--rate-limit` for bulk downloads
3. **Organize Early**: Set up organization structure before downloading thousands of files
4. **Backup Configs**: Your settings are in `~/.audio_downloader_config.json` - back it up
5. **Test First**: Try a single URL before processing large batches
6. **Check Quality**: Use `ffprobe` to verify audio quality after download
7. **Update Regularly**: Keep yt-dlp updated: `pip install --upgrade yt-dlp`
8. **Use Comments**: Add comments to URL lists for organization (lines starting with `#`)

---

## 📜 License & Credits

This tool is a wrapper around:
- **yt-dlp** - Universal video/audio downloader
- **ffmpeg** - Multimedia framework for conversion

Both are required dependencies and are subject to their respective licenses.

---

## 🆘 Support & Updates

For issues with:
- **This script**: Check error messages, verify dependencies, try `--reset`
- **yt-dlp**: Update with `pip install --upgrade yt-dlp`
- **Specific sites**: Visit yt-dlp GitHub for site-specific issues
- **ffmpeg**: Check ffmpeg.org documentation

---

## 🎓 Advanced Topics

### Custom Output Templates

yt-dlp supports extensive template options:

```bash
# By uploader and upload date
python downloader.py -t "%(uploader)s/%(upload_date)s - %(title)s.%(ext)s" urls.txt

# With video ID for reference
python downloader.py -t "%(title)s [%(id)s].%(ext)s" urls.txt

# Organized by year/month
python downloader.py -t "%(upload_date>%Y)s/%(upload_date>%m)s/%(title)s.%(ext)s" urls.txt
```

### Playlist-Specific Downloads

```bash
# Only first 10 videos
python downloader.py --playlist-end 10 "playlist_url"

# Videos 5-15
python downloader.py --playlist-start 5 --playlist-end 15 "playlist_url"

# Every other video
python downloader.py --playlist-items "1,3,5,7,9" "playlist_url"
```

### Automation Examples

```bash
# Cron job for daily playlist sync
0 2 * * * cd ~/Music && python /path/to/downloader.py --archive .archive.txt daily_playlist.txt

# Watch a file and download new additions
while inotifywait -e modify urls.txt; do
    python downloader.py --archive .archive.txt urls.txt
done
```

---

**Happy Downloading! 🎵**## ✨ Key Features

### 🎯 Smart Defaults
- **FLAC lossless** audio at highest available bitrate
- **Automatic metadata embedding** including source URLs and playlist info
- **Title-based naming** using original video/page titles
- **Persistent preferences** that remember your settings
- **Video mode is temporary** - always reverts to audio after use

### 🔄 Versatile Input
- Direct URLs (YouTube, SoundCloud, Spotify, etc.)
- Text files (`.txt`) with line-separated URLs
- JSON files (`.json`) with flexible structures
- CSV files (`.csv`) with URLs in any column
- M3U playlists (`.m3u`, `.m3u8`)
- Mixed text with space/comma-separated URLs
- URLs without `https://` prefix (auto-adds)

### 🎬 Source Support
- **YouTube** videos and playlists (auto-detects)
- **SoundCloud** tracks and playlists
- **Spotify** (with appropriate yt-dlp extractors)
- **Direct audio links** (`.mp3`, `.flac`, `.wav`, etc.)
- **Generic web pages** (auto-extracts media)
- **1000+ sites** supported by yt-dlp

### 📋 Naming Schemes
- `title` - Song Title.flac *(default)*
- `numbered` - 001 - Song Title.flac
- `artist-title` - Artist Name - Song Title.flac
- `album-track` - Album/01 - Song Title.flac
- `date-title` - 20231225 - Song Title.flac
- `id-title` - VideoID - Song Title.flac
- `uploader-title` - Channel Name - Song Title.flac

### 📦 Audio Formats
- **FLAC** - Lossless, compression level 0 *(default)*
- **WAV** - Uncompressed PCM 24-bit
- **MP3** - VBR quality 0 (~245 kbps)
- **Opus** - Excellent quality/size ratio
- **AAC** - High-quality lossy
- **M4A** - Apple audio format
- **Vorbis** - Open-source codec

### 🛡️ Advanced Features
- **Download archive** - Skip previously downloaded URLs
- **Rate limiting** - Control bandwidth usage
- **Date filtering** - Download only from specific time periods
- **Geo-bypass** - Automatic geographic restriction bypass
- **Retry logic** - Configurable retry attempts
- **Batch processing** - Handle thousands of URLs
- **Resume capability** - Skip existing files
- **Error recovery** - Continue on individual failures

---

## 🚀 Quick Start

### Installation

```bash
# 1. Install yt-dlp
pip install yt-dlp

# 2. Install ffmpeg
# Ubuntu/Debian:
sudo apt install ffmpeg

# macOS (with Homebrew):
brew install ffmpeg

# Windows:
# Download from https://ffmpeg.org/ and add to PATH

# 3. Verify installation
yt-dlp --version
ffmpeg -version
```

### Basic Usage

```bash
# Download from a text file (one URL per line)
python downloader.py urls.txt

# Download a single YouTube video
python downloader.py "https://youtube.com/watch?v=dQw4w9WgXcQ"

# Download entire playlist (auto-detects)
python downloader.py "https://youtube.com/playlist?list=PLxxxxxx"

# Download multiple URLs
python downloader.py "url1" "url2" "url3"
```

---

## 📖 Comprehensive Examples

### Format Selection

```bash
# Download as MP3 (becomes new default)
python downloader.py -f mp3 urls.txt

# High-quality WAV (24-bit PCM)
python downloader.py -f wav urls.txt

# Space-efficient Opus
python downloader.py -f opus urls.txt

# Download video (temporary, doesn't persist)
python downloader.py --video urls.txt
```

### Naming & Organization

```bash
# Numbered files for playlists
python downloader.py --naming numbered playlist.txt
# Output: 001 - First Song.flac, 002 - Second Song.flac

# Artist - Title format
python downloader.py --naming artist-title urls.txt
# Output: The Beatles - Hey Jude.flac

# Date-based naming
python downloader.py --naming date-title urls.txt
# Output: 20231225 - Song Title.flac

# Organize by source platform
python downloader.py -o ~/Music --organize urls.txt
# Output: ~/Music/YouTube/song1.flac, ~/Music/SoundCloud/song2.flac

# Custom template (advanced)
python downloader.py -t "%(artist)s/%(album)s/%(title)s.%(ext)s" urls.txt
# Output: Artist/Album/Title.flac
```

### Download Management

```bash
# Track downloads to avoid duplicates
python downloader.py --archive ~/downloads.txt urls.txt
# Run again - skips already downloaded URLs

# Limit speed to 1 MB/s
python downloader.py --rate-limit 1M urls.txt

# Download only recent videos
python downloader.py --date-after 20231201 urls.txt

# Date range (entire year 2023)
python downloader.py --date-after 20230101 --date-before 20231231 urls.txt

# More retries for unreliable connections
python downloader.py --retries 10 urls.txt
```

### Metadata Control

```bash
# Disable all metadata
python downloader.py --no-metadata urls.txt

# Disable only thumbnails
python downloader.py --no-thumbnail urls.txt

# Don't embed source URLs
python downloader.py --no-source-url urls.txt

# Minimal files (no metadata, no thumbnails)
python downloader.py --no-metadata --no-thumbnail urls.txt
```

### Advanced Workflows

```bash
# Complete archival setup
python downloader.py \
  -f flac \
  -o ~/Music/Archive \
  --naming date-title \
  --organize \
  --archive ~/.audio_archive.txt \
  --rate-limit 2M \
  urls.txt

# Fast MP3 batch download
python downloader.py \
  -f mp3 \
  --no-thumbnail \
  --rate-limit 5M \
  --archive ~/mp3_downloads.txt \
  huge_list.txt

# Numbered playlist with custom padding
python downloader.py \
  --naming numbered \
  --padding 4 \
  -o ./Playlists/MyPlaylist \
  "https://youtube.com/playlist?list=PLxxxxxx"
# Output: 0001 - Song.flac, 0002 - Song.flac, etc.
```

---

## 📁 Input File Formats

### Text File (`urls.txt`)
```
https://youtube.com/watch?v=abc123
https://youtube.com/watch?v=def456
# Lines starting with # are comments
https://youtube.com/watch?v=ghi789  # Inline comments work too

# Multiple URLs per line (space-separated)
url1 url2 url3
```

### JSON File (`playlist.json`)

**Array format:**
```json
[
  "https://youtube.com/watch?v=abc",
  "https://youtube.com/watch?v=def",
  "https://youtube.com/watch?v=ghi"
]
```

**Object format:**
```json
{
  "playlist_name": "My Favorites",
  "urls": [
    "https://youtube.com/watch?v=abc",
    "https://youtube.com/watch?v=def"
  ]
}
```

**Detailed object format:**
```json
[
  {
    "url": "https://youtube.com/watch?v=abc",
    "title": "Song 1",
    "artist": "Artist A"
  },
  {
    "url": "https://youtube.com/watch?v=def",
    "title": "Song 2",
    "artist": "Artist B"
  }
]
```

### CSV File (`songs.csv`)
```csv
title,artist,url,year
"Song 1","Artist A","https://youtube.com/watch?v=abc",2023
"Song 2","Artist B","https://youtube.com/watch?v=def",2024
```
*URLs are automatically extracted from any column*

### M3U Playlist (`playlist.m3u`)
```
#EXTM3U
#EXTINF:123,Artist - Song Title
https://youtube.com/watch?v=abc123
#EXTINF:234,Artist 2 - Song Title 2
https://youtube.com/watch?v=def456
```

---

## ⚙️ Configuration

### View Current Settings
```bash
python downloader.py --show-config
```

Output:
```
==============================================================
CURRENT CONFIGURATION
==============================================================
  archive_file             : None
  embed_metadata           : True
  embed_playlist_url       : True
  embed_source_url         : True
  embed_thumbnail          : True
  format                   : flac
  geo_bypass               : True
  naming_scheme            : title
  number_padding           : 3
  organize_by_source       : False
  output_dir               : ./downloads
  output_template          : %(title)s.%(ext)s
  prefer_free_formats      : False
  quality                  : best
  rate_limit               : None
  retries                  : 3
==============================================================
```

### Reset to Defaults
```bash
python downloader.py --reset
```

### Configuration Persistence
Settings are automatically saved in `~/.audio_downloader_config.json`:
- Format preferences
- Output directories
- Naming schemes
- Metadata options
- Download settings

**Exception:** Video format (`--video`) never persists - always reverts to audio.

---

## 🎯 Use Cases & Workflows

### Personal Music Library
```bash
# Setup
python downloader.py \
  -f flac \
  -o ~/Music \
  --naming artist-title \
  --organize \
  --archive ~/.music_downloads.txt

# Daily use - just add URLs to favorites.txt
python downloader.py favorites.txt
```

### Podcast/Educational Content
```bash
python downloader.py \
  -f mp3 \
  -o ~/Podcasts \
  --naming date-title \
  --organize \
  podcast_episodes.txt
```

### Playlist Archival
```bash
# Download entire channel's uploads
python downloader.py \
  --naming numbered \
  --padding 4 \
  -o "./Archive/[Channel Name]" \
  "https://youtube.com/c/ChannelName/videos"

# Download curated playlist
python downloader.py \
  --naming numbered \
  "https://youtube.com/playlist?list=PLxxxxxx"
```

### Batch Conversion
```bash
# Convert existing URLs to different format
python downloader.py -f opus existing_urls.txt
```

### Quick Downloads (No Metadata)
```bash
# Fast downloads without extras
python downloader.py \
  -f mp3 \
  --no-metadata \
  --no-thumbnail \
  --rate-limit 10M \
  quick_list.txt
```

---

## 🔍 URL Format Examples

The script intelligently handles various URL formats:

```bash
# Full URLs
https://youtube.com/watch?v=abc123
https://www.youtube.com/watch?v=abc123
https://youtu.be/abc123

# Without protocol (auto-added)
youtube.com/watch?v=abc123
www.youtube.com/watch?v=abc123
youtu.be/abc123

# Playlists (auto-detected)
https://youtube.com/playlist?list=PLxxxxxx
https://youtube.com/watch?v=abc&list=PLxxxxxx

# Direct audio files
https://example.com/audio/song.mp3
https://example.com/music/track.flac
https://cdn.example.com/files/audio.wav

# Generic web pages (extracts media)
https://soundcloud.com/artist/track
https://example.com/music/song-page
https://bandcamp.com/track/song-title

# Other platforms
https://vimeo.com/123456789
https://dailymotion.com/video/x7xxxxx
https://twitter.com/user/status/123456789
```

---

## 📊 Quality Settings by Format

| Format | Quality Setting | Bitrate/Details |
|--------|----------------|-----------------|
| **FLAC** | Compression 0 | Lossless, fastest compression |
| **WAV** | PCM 24-bit | Uncompressed lossless |
| **MP3** | VBR Quality 0 | ~245 kbps average (highest) |
| **Opus** | VBR Quality 0 | ~128-256 kbps (excellent) |
| **AAC** | VBR Quality 0 | ~192-256 kbps |
| **M4A** | VBR Quality 0 | ~192-256 kbps |
| **Vorbis** | VBR Quality 0 | ~160-320 kbps |

*All formats use "best available" source quality*

---

## 🛠️ Troubleshooting

### "ERROR: Missing dependencies"
```bash
# Update yt-dlp
pip install --upgrade yt-dlp

# Verify ffmpeg installation
ffmpeg -version

# Install ffmpeg if missing (see Installation section)
```

### "No valid URLs found"
- Check file encoding (should be UTF-8)
- Verify URLs are complete (include `https://`)
- Remove any special characters or formatting
- Try testing with a single URL first

### Download Failures
```bash
# Try with more retries
python downloader.py --retries 10 urls.txt

# Check verbose output
yt-dlp --verbose "URL"

# Update yt-dlp (fixes most issues)
pip install --upgrade yt-dlp
```

### Geographic Restrictions
```bash
# Geo-bypass is enabled by default
# If still blocked, yt-dlp will show specific error

# Some platforms may require cookies
# Check yt-dlp documentation for cookie extraction
```

### Metadata Not Embedding
```bash
# Ensure ffmpeg is installed properly
ffmpeg -version

# Check if metadata option is enabled
python downloader.py --show-config

# Try re-enabling if disabled
python downloader.py --reset
```

---

## 🤝 Tips & Best Practices

1. **Use Archive Files**: Always use `--archive` for large collections to avoid re-downloading
2. **Rate Limiting**: Be respectful - use `--rate-limit` for bulk downloads
3. **Organize Early**: Set up organization structure before downloading thousands of files
4. **Backup Configs**: Your settings are in `~/.audio_downloader_config.json` - back it up
5. **Test First**: Try a single URL before processing large batches
6. **Check Quality**: Use `ffprobe` to verify audio quality after download
7. **Update Regularly**: Keep yt-dlp updated: `pip install --upgrade yt-dlp`
8. **Use Comments**: Add comments to URL lists for organization (lines starting with `#`)

---

## 📜 License & Credits

This tool is a wrapper around:
- **yt-dlp** - Universal video/audio downloader
- **ffmpeg** - Multimedia framework for conversion

Both are required dependencies and are subject to their respective licenses.

---

## 🆘 Support & Updates

For issues with:
- **This script**: Check error messages, verify dependencies, try `--reset`
- **yt-dlp**: Update with `pip install --upgrade yt-dlp`
- **Specific sites**: Visit yt-dlp GitHub for site-specific issues
- **ffmpeg**: Check ffmpeg.org documentation

---

## 🎓 Advanced Topics

### Custom Output Templates

yt-dlp supports extensive template options:

```bash
# By uploader and upload date
python downloader.py -t "%(uploader)s/%(upload_date)s - %(title)s.%(ext)s" urls.txt

# With video ID for reference
python downloader.py -t "%(title)s [%(id)s].%(ext)s" urls.txt

# Organized by year/month
python downloader.py -t "%(upload_date>%Y)s/%(upload_date>%m)s/%(title)s.%(ext)s" urls.txt
```

### Playlist-Specific Downloads

```bash
# Only first 10 videos
python downloader.py --playlist-end 10 "playlist_url"

# Videos 5-15
python downloader.py --playlist-start 5 --playlist-end 15 "playlist_url"

# Every other video
python downloader.py --playlist-items "1,3,5,7,9" "playlist_url"
```

### Automation Examples

```bash
# Cron job for daily playlist sync
0 2 * * * cd ~/Music && python /path/to/downloader.py --archive .archive.txt daily_playlist.txt

# Watch a file and download new additions
while inotifywait -e modify urls.txt; do
    python downloader.py --archive .archive.txt urls.txt
done
```

---

**Happy Downloading! 🎵**
