#!/usr/bin/env python3
"""
Versatile Audio/Video Downloader with Advanced Metadata & Batch Processing
Supports YouTube, playlists, direct links, web scraping, and extensive customization
Defaults to FLAC lossless at highest quality with full metadata embedding
"""

import argparse
import json
import os
import sys
import re
import subprocess
import urllib.parse
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from datetime import datetime

CONFIG_FILE = Path.home() / ".audio_downloader_config.json"

DEFAULT_CONFIG = {
    "format": "flac",  # Lossless format
    "quality": "best",
    "output_dir": "./downloads",
    "output_template": "%(title)s.%(ext)s",
    "organize_by_source": False,
    "embed_metadata": True,
    "embed_thumbnail": True,
    "embed_source_url": True,
    "embed_playlist_url": True,
    "naming_scheme": "title",  # title, numbered, artist-title, custom
    "number_padding": 3,
    "archive_file": None,  # Track downloaded URLs to avoid duplicates
    "rate_limit": None,  # Speed limit (e.g., "1M" for 1MB/s)
    "retries": 3,
    "geo_bypass": True,
    "prefer_free_formats": False,
    "no_overwrites": True,  # Don't overwrite existing files by default
    "proxy": None,  # Proxy support
    "bitrate": "0",  # Highest quality (0 means best for most formats)
    "sample_rate": None,  # Let yt-dlp decide best sample rate
    "postprocessor_args": None  # Additional FFmpeg args for highest quality
}


class Config:
    """Manages persistent configuration with extensive options"""
    
    def __init__(self):
        self.settings = self.load()
    
    def load(self) -> dict:
        """Load config from file or return defaults"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    return {**DEFAULT_CONFIG, **config}
            except:
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()
    
    def save(self):
        """Save current settings to file"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def update(self, **kwargs):
        """Update settings and save (except video format which is transient)"""
        for key, value in kwargs.items():
            if value is not None:
                self.settings[key] = value
        # Don't persist video format - always revert to audio
        if 'format' in kwargs and kwargs['format'] in ['mp4', 'mkv', 'webm', 'avi']:
            # For video formats, don't save to persist the original audio format
            pass  # Temporary - don't save
        else:
            # Save all other settings including proxy, etc.
            self.save()
    
    def display(self):
        """Display current configuration"""
        print("\n" + "="*60)
        print("CURRENT CONFIGURATION")
        print("="*60)
        for key, value in sorted(self.settings.items()):
            print(f"  {key:25s}: {value}")
        print("="*60 + "\n")


class Downloader:
    """Handles downloading from various sources with advanced features"""
    
    def __init__(self, config: Config):
        self.config = config
        self.check_dependencies()
        self.download_archive = set()
        self.load_archive()
    
    def check_dependencies(self):
        """Verify yt-dlp and ffmpeg are installed"""
        deps = {'yt-dlp': 'yt-dlp'}
        missing = []
        
        # Check yt-dlp first
        for name, cmd in deps.items():
            timeout_val = 10
            try:
                # Try with shell=True to ensure PATH is properly inherited
                subprocess.run([cmd, '--version'], 
                             capture_output=True, 
                             check=True,
                             timeout=timeout_val)
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                # If direct call fails, try using shutil.which to find the executable
                import shutil
                cmd_path = shutil.which(cmd)
                if cmd_path:
                    try:
                        subprocess.run([cmd_path, '--version'], 
                                     capture_output=True, 
                                     check=True,
                                     timeout=timeout_val)
                    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                        missing.append(name)
                else:
                    missing.append(name)
        
        # Check ffmpeg separately since it may return different exit codes
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                 capture_output=True, 
                                 timeout=15)
            # ffmpeg might return 0 for success or 8 for version command, both indicate it works
            if result.returncode not in [0, 8]:
                # If version check fails, try a simple info command
                result2 = subprocess.run(['ffmpeg', '-h'], 
                                       capture_output=True, 
                                       timeout=15)
                if result2.returncode not in [0, 1]:  # 1 is normal for help command
                    # Try to find ffmpeg with shutil.which
                    import shutil
                    ffmpeg_path = shutil.which('ffmpeg')
                    if ffmpeg_path:
                        result3 = subprocess.run([ffmpeg_path, '-version'], 
                                               capture_output=True, 
                                               timeout=15)
                        if result3.returncode not in [0, 8]:
                            missing.append('ffmpeg')
                    else:
                        missing.append('ffmpeg')
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # Try to find ffmpeg with shutil.which
            import shutil
            ffmpeg_path = shutil.which('ffmpeg')
            if ffmpeg_path:
                try:
                    result = subprocess.run([ffmpeg_path, '-version'], 
                                         capture_output=True, 
                                         timeout=15)
                    if result.returncode not in [0, 8]:
                        missing.append('ffmpeg')
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    missing.append('ffmpeg')
            else:
                missing.append('ffmpeg')
        
        if missing:
            print(f"ERROR: Missing dependencies: {', '.join(missing)}")
            print("\nInstall with:")
            if 'yt-dlp' in missing:
                print("  pip install yt-dlp")
                print("  # or: pip install --upgrade yt-dlp")
            if 'ffmpeg' in missing:
                print("  # Install ffmpeg:")
                print("  # - Ubuntu/Debian: sudo apt install ffmpeg")
                print("  # - Fedora/RHEL: sudo dnf install ffmpeg")
                print("  # - macOS: brew install ffmpeg")
                print("  # - Windows: Download from https://ffmpeg.org/")
            sys.exit(1)
    
    def load_archive(self):
        """Load previously downloaded URLs from archive file"""
        archive_file = self.config.settings.get('archive_file')
        if archive_file and os.path.exists(archive_file):
            try:
                with open(archive_file, 'r') as f:
                    self.download_archive = set(line.strip() for line in f if line.strip())
            except:
                pass
    
    def save_to_archive(self, url: str):
        """Save URL to archive to prevent re-downloading"""
        archive_file = self.config.settings.get('archive_file')
        if archive_file:
            self.download_archive.add(url)
            try:
                Path(archive_file).parent.mkdir(parents=True, exist_ok=True)
                with open(archive_file, 'a') as f:
                    f.write(f"{url}\n")
            except:
                pass
    
    def parse_urls(self, sources: List[str]) -> List[str]:
        """Parse URLs from various input formats"""
        urls = []
        
        for source in sources:
            # Check if it's a file
            if os.path.isfile(source):
                urls.extend(self.parse_file(source))
            # Check if it's a direct URL
            elif re.match(r'https?://', source):
                urls.append(source)
            # Check if it's a URL without protocol
            elif re.match(r'www\.', source) or '.' in source and '/' in source:
                urls.append('https://' + source.lstrip('/'))
            # Try to find URLs in text
            else:
                urls.extend(self.parse_text(source))
        
        return list(dict.fromkeys(urls))  # Remove duplicates while preserving order
    
    def parse_file(self, filepath: str) -> List[str]:
        """Parse URLs from various file formats"""
        urls = []
        ext = Path(filepath).suffix.lower()
        
        try:
            if ext == '.json':
                urls.extend(self.parse_json_file(filepath))
            elif ext == '.csv':
                urls.extend(self.parse_csv_file(filepath))
            elif ext in ['.m3u', '.m3u8']:
                urls.extend(self.parse_m3u_file(filepath))
            else:
                urls.extend(self.parse_text_file(filepath))
        except Exception as e:
            print(f"Warning: Error parsing {filepath}: {e}")
        
        return urls
    
    def parse_text_file(self, filepath: str) -> List[str]:
        """Parse URLs from text file (line or space separated)"""
        urls = []
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Try line-separated first
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('//'):
                # Extract all URLs from line
                found_urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', line)
                urls.extend(found_urls)
        
        return urls
    
    def parse_json_file(self, filepath: str) -> List[str]:
        """Parse URLs from JSON file (supports various structures)"""
        urls = []
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    urls.append(item)
                elif isinstance(item, dict):
                    # Try common URL field names
                    for key in ['url', 'link', 'href', 'source', 'video_url']:
                        if key in item:
                            urls.append(item[key])
                            break
        elif isinstance(data, dict):
            # Try to find URL lists in dict
            for value in data.values():
                if isinstance(value, list):
                    urls.extend([v for v in value if isinstance(v, str) and re.match(r'https?://', v)])
                elif isinstance(value, str) and re.match(r'https?://', value):
                    urls.append(value)
        
        return urls
    
    def parse_csv_file(self, filepath: str) -> List[str]:
        """Parse URLs from CSV file"""
        urls = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                # Find all URLs in each CSV row
                found_urls = re.findall(r'https?://[^\s,;"]+', line)
                urls.extend(found_urls)
        return urls
    
    def parse_m3u_file(self, filepath: str) -> List[str]:
        """Parse URLs from M3U/M3U8 playlist file"""
        urls = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)
        return urls
    
    def parse_text(self, text: str) -> List[str]:
        """Parse URLs from text (space, comma, or line separated)"""
        # Find all URLs in the text
        urls = re.findall(r'https?://[^\s,;"]+|www\.[^\s,;"]+', text)
        # Add protocol to www URLs
        urls = ['https://' + url if url.startswith('www.') else url for url in urls]
        return urls
    
    def detect_url_type(self, url: str) -> str:
        """Detect type of URL (youtube, playlist, direct audio, etc.)"""
        url_lower = url.lower()
        
        if 'youtube.com/playlist' in url_lower or 'youtu.be/playlist' in url_lower or '&list=' in url_lower:
            return 'youtube_playlist'
        elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube_video'
        elif 'soundcloud.com' in url_lower:
            return 'soundcloud'
        elif 'spotify.com' in url_lower:
            return 'spotify'
        elif url_lower.endswith(('.mp3', '.flac', '.wav', '.m4a', '.ogg', '.opus', '.aac')):
            return 'direct_audio'
        elif url_lower.endswith(('.mp4', '.mkv', '.webm', '.avi', '.mov')):
            return 'direct_video'
        else:
            return 'generic'
    
    def get_output_template(self, naming_scheme: str, number_padding: int) -> str:
        """Generate output template based on naming scheme"""
        templates = {
            'title': '%(title)s.%(ext)s',
            'numbered': f'%(playlist_index)0{number_padding}d - %(title)s.%(ext)s',
            'artist-title': '%(artist)s - %(title)s.%(ext)s',
            'album-track': '%(album)s/%(track_number)s - %(title)s.%(ext)s',
            'date-title': '%(upload_date)s - %(title)s.%(ext)s',
            'id-title': '%(id)s - %(title)s.%(ext)s',
            'uploader-title': '%(uploader)s - %(title)s.%(ext)s'
        }
        return templates.get(naming_scheme, '%(title)s.%(ext)s')
    
    def build_metadata_args(self, url: str, playlist_url: Optional[str] = None) -> List[str]:
        """Build metadata arguments for embedding source information"""
        args = []
        
        if self.config.settings.get('embed_source_url'):
            # Embed source URL in metadata
            args.extend([
                '--add-metadata',
                '--parse-metadata', f'url:{url}',
                '--parse-metadata', 'webpage_url:%(meta_url)s',
            ])
        
        if playlist_url and self.config.settings.get('embed_playlist_url'):
            # Embed playlist URL in metadata
            args.extend([
                '--parse-metadata', f'playlist_url:{playlist_url}',
            ])
        
        return args
    
    def download(self, urls: List[str], 
                 fmt: Optional[str] = None,
                 output_dir: Optional[str] = None,
                 output_template: Optional[str] = None,
                 organize: Optional[bool] = None,
                 video: bool = False,
                 naming_scheme: Optional[str] = None,
                 batch_size: Optional[int] = None,
                 date_range: Optional[Tuple[str, str]] = None,
                 skip_archive: bool = False):
        """Download URLs with specified settings and advanced features"""
        
        # Use provided settings or fall back to config
        fmt = fmt or self.config.settings['format']
        output_dir = output_dir or self.config.settings['output_dir']
        naming_scheme = naming_scheme or self.config.settings['naming_scheme']
        
        if output_template:
            template = output_template
        else:
            template = self.get_output_template(
                naming_scheme, 
                self.config.settings['number_padding']
            )
        
        organize = organize if organize is not None else self.config.settings['organize_by_source']
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Filter already downloaded URLs
        if not skip_archive and self.config.settings.get('archive_file'):
            original_count = len(urls)
            urls = [u for u in urls if u not in self.download_archive]
            if len(urls) < original_count:
                print(f"Skipping {original_count - len(urls)} already downloaded URL(s)")
        
        if not urls:
            print("No new URLs to download!")
            return
        
        # Determine quality level
        quality_level = self.config.settings.get('quality', 'best')
        
        print(f"\n{'='*70}")
        print(f"DOWNLOAD SESSION STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        print(f"URLs to process: {len(urls)}")
        print(f"Format: {fmt.upper() if not video else 'VIDEO (MP4)'}")
        print(f"Quality: {quality_level}")
        print(f"Output directory: {output_dir}")
        print(f"Naming scheme: {naming_scheme}")
        print(f"Metadata embedding: {'Enabled' if self.config.settings['embed_metadata'] else 'Disabled'}")
        if self.config.settings.get('rate_limit'):
            print(f"Rate limit: {self.config.settings['rate_limit']}")
        print(f"{'='*70}\n")
        
        success_count = 0
        fail_count = 0
        
        for i, url in enumerate(urls, 1):
            url_type = self.detect_url_type(url)
            print(f"\n[{i}/{len(urls)}] Processing ({url_type}): {url[:80]}{'...' if len(url) > 80 else ''}")
            
            try:
                # Build yt-dlp command
                cmd = ['yt-dlp']
                
                # Playlist handling - update to properly detect playlists
                playlist_url = None
                if url_type == 'youtube_playlist' or '&list=' in url:
                    cmd.append('--yes-playlist')
                    playlist_url = url
                else:
                    cmd.append('--no-playlist')
                
                # Format selection
                if video:
                    cmd.extend(['-f', 'bestvideo+bestaudio/best'])
                else:
                    # Set quality based on setting
                    if quality_level == "best":
                        cmd.extend(['-f', 'bestaudio/best'])
                        audio_quality = '0'  # Best quality
                    elif quality_level == "high":
                        cmd.extend(['-f', 'bestaudio/best'])
                        audio_quality = '0'  # Still best but may be limited differently
                    elif quality_level == "medium":
                        cmd.extend(['-f', 'bestaudio/best'])
                        audio_quality = '3'  # Medium quality
                    elif quality_level == "low":
                        cmd.extend(['-f', 'bestaudio/best'])
                        audio_quality = '9'  # Lower quality
                    else:
                        cmd.extend(['-f', 'bestaudio/best'])
                        audio_quality = '0'  # Default to best if unknown quality
                    
                    # Audio extraction and conversion
                    cmd.extend([
                        '--extract-audio',
                        '--audio-format', fmt,
                        '--audio-quality', audio_quality,
                    ])
                
                # Additional options to handle YouTube restrictions (only for YouTube)
                if 'youtube.com' in url or 'youtu.be' in url:
                    # Enhanced options to bypass YouTube restrictions
                    cmd.extend([
                        '--extractor-args', 'youtube:player-client=web',
                        '--no-check-certificate',
                        # Playlist handling based on URL
                        '--yes-playlist' if ('playlist' in url or '&list=' in url) else '--no-playlist',
                        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        '--add-header', 'Referer: https://www.youtube.com/',
                        '--add-header', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        '--sleep-interval', '1',
                        '--max-sleep-interval', '3'
                    ])
                
                # Add proxy support if configured
                if self.config.settings.get('proxy'):
                    cmd.extend(['--proxy', self.config.settings['proxy']])
                
                # Output template
                if organize:
                    output_path = os.path.join(output_dir, '%(extractor)s', template)
                else:
                    output_path = os.path.join(output_dir, template)
                
                cmd.extend(['-o', output_path])
                
                # Metadata embedding
                if self.config.settings.get('embed_metadata') and not video:
                    cmd.append('--embed-metadata')
                    cmd.extend(self.build_metadata_args(url, playlist_url))
                
                # Thumbnail embedding
                if self.config.settings.get('embed_thumbnail') and not video:
                    cmd.extend([
                        '--embed-thumbnail',
                        '--convert-thumbnails', 'jpg',
                    ])
                
                # Additional options
                cmd.extend([
                    '--no-warnings',
                    '--ignore-errors',
                ])
                
                # Handle overwrites setting (if it's False, don't add --no-overwrites)
                if self.config.settings.get('no_overwrites', True):
                    cmd.append('--no-overwrites')
                
                cmd.extend([
                    '--retries', str(self.config.settings['retries']),
                ])
                
                if self.config.settings.get('rate_limit'):
                    cmd.extend(['--limit-rate', self.config.settings['rate_limit']])
                
                if self.config.settings.get('geo_bypass'):
                    cmd.append('--geo-bypass')
                
                if self.config.settings.get('prefer_free_formats'):
                    cmd.append('--prefer-free-formats')
                
                # Date range filtering
                if date_range:
                    cmd.extend(['--dateafter', date_range[0]])
                    if date_range[1]:
                        cmd.extend(['--datebefore', date_range[1]])
                
                # FFmpeg postprocessor args for maximum quality
                if not video:
                    # Use custom postprocessor args if specified in config, otherwise defaults
                    if self.config.settings.get('postprocessor_args'):
                        cmd.extend(['--postprocessor-args', self.config.settings['postprocessor_args']])
                    else:
                        if fmt == 'flac':
                            # Highest quality FLAC: compression level 0 (fastest) or 12 (most compressed)
                            # For quality, use compression level 0 or 8 for best quality
                            cmd.extend(['--postprocessor-args', 'ffmpeg:-compression_level 0 -sample_fmt s32'])  # 32-bit for highest quality
                        elif fmt == 'wav':
                            # 24-bit WAV for highest quality
                            cmd.extend(['--postprocessor-args', 'ffmpeg:-c:a pcm_s24le'])
                        else:
                            # Adjust quality based on setting for non-FLAC formats, with 24-bit sample format
                            cmd.extend([f'--postprocessor-args', f'ffmpeg:-q:a {audio_quality} -sample_fmt s32'])
                
                cmd.append(url)
                
                # Execute download with retry logic for YouTube
                print(f"  Downloading...")
                
                # Try multiple approaches for YouTube if the first one fails
                retry_strategies = [cmd]  # Default command
                
                # If it's a YouTube URL, add alternative strategies
                if 'youtube.com' in url or 'youtu.be' in url:
                    # Strategy 2: Different player client
                    cmd_alt1 = cmd.copy()
                    for i, arg in enumerate(cmd_alt1):
                        if arg == '--extractor-args':
                            # Replace existing extractor args
                            cmd_alt1[i+1] = 'youtube:player-client=android'
                            break
                    else:
                        # If no extractor args were found, add them
                        cmd_alt1.extend(['--extractor-args', 'youtube:player-client=android'])
                    
                    # Strategy 3: Direct video download then audio extraction (fallback)
                    cmd_alt2 = ['yt-dlp']
                    cmd_alt2.extend(['--no-playlist', '-f', 'best', '--extract-audio', '--audio-format', fmt, '--audio-quality', audio_quality])
                    cmd_alt2.extend(['-o', output_path])
                    if self.config.settings.get('embed_metadata') and not video:
                        cmd_alt2.append('--embed-metadata')
                        cmd_alt2.extend(self.build_metadata_args(url, playlist_url))
                    if self.config.settings.get('embed_thumbnail') and not video:
                        cmd_alt2.extend(['--embed-thumbnail', '--convert-thumbnails', 'jpg'])
                    cmd_alt2.extend(['--no-warnings', '--ignore-errors'])
                    if self.config.settings.get('no_overwrites', True):
                        cmd_alt2.append('--no-overwrites')
                    cmd_alt2.extend(['--retries', str(self.config.settings['retries'])])
                    if self.config.settings.get('rate_limit'):
                        cmd_alt2.extend(['--limit-rate', self.config.settings['rate_limit']])
                    if self.config.settings.get('geo_bypass'):
                        cmd_alt2.append('--geo-bypass')
                    cmd_alt2.extend(['--user-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'])
                    cmd_alt2.append(url)
                    
                    retry_strategies = [cmd, cmd_alt1, cmd_alt2]
                
                download_success = False
                for i, attempt_cmd in enumerate(retry_strategies):
                    try:
                        print(f"    Attempt {i+1}/{len(retry_strategies)}...")
                        result = subprocess.run(attempt_cmd, capture_output=True, text=True, timeout=120)  # 2 minute timeout per download
                        
                        if result.returncode == 0:
                            print(f"  ✓ Successfully downloaded")
                            success_count += 1
                            self.save_to_archive(url)
                            download_success = True
                            break  # Success, exit retry loop
                        else:
                            print(f"    Attempt {i+1} failed (return code: {result.returncode})")
                            if i == len(retry_strategies) - 1:  # Last attempt
                                if result.stderr:
                                    error_lines = result.stderr.split('\n')
                                    relevant_errors = [line for line in error_lines if 'ERROR' in line]
                                    if relevant_errors:
                                        print(f"     Error: {relevant_errors[0][:100]}")
                                fail_count += 1
                    except subprocess.TimeoutExpired:
                        print(f"    Attempt {i+1} timed out (2 minutes)")
                        if i == len(retry_strategies) - 1:  # Last attempt
                            fail_count += 1
                    except Exception as e:
                        print(f"    Attempt {i+1} error: {str(e)[:100]}")
                        if i == len(retry_strategies) - 1:  # Last attempt
                            fail_count += 1
                
                if not download_success and len(retry_strategies) > 1:
                    print(f"  ✗ All {len(retry_strategies)} download attempts failed")
                    
            except KeyboardInterrupt:
                print("\n\nDownload interrupted by user")
                break
            except Exception as e:
                print(f"  ✗ Error: {str(e)[:100]}")
                fail_count += 1
        
        # Summary
        print(f"\n{'='*70}")
        print(f"DOWNLOAD SESSION COMPLETE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        print(f"  Successful: {success_count}/{len(urls)}")
        print(f"  Failed: {fail_count}/{len(urls)}")
        print(f"  Output location: {output_dir}")
        print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Advanced audio/video downloader with extensive customization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  Basic usage:
    %(prog)s urls.txt                           # Download from text file
    %(prog)s "https://youtube.com/watch?v=..."  # Single URL
    %(prog)s url1 url2 url3                     # Multiple URLs
  
  Format & quality:
    %(prog)s -f mp3 urls.txt                    # Convert to MP3
    %(prog)s -f wav --no-thumbnail urls.txt     # WAV without thumbnails
    %(prog)s --video urls.txt                   # Download as video (temporary)
  
  Naming schemes:
    %(prog)s --naming numbered urls.txt         # 001 - Title.flac
    %(prog)s --naming artist-title urls.txt     # Artist - Title.flac
    %(prog)s --naming date-title urls.txt       # 20231225 - Title.flac
  
  Organization:
    %(prog)s -o ./music --organize urls.txt     # Organize by source
    %(prog)s -t "<artist>/<album>/<title>.<ext>" urls.txt
  
  Advanced features:
    %(prog)s --archive downloads.txt urls.txt   # Track & skip duplicates
    %(prog)s --rate-limit 1M urls.txt           # Limit to 1MB/s
    %(prog)s --date-after 20231201 urls.txt     # Only recent videos
    %(prog)s --no-metadata urls.txt             # Skip metadata embedding
  
  Colab Integration:
    %(prog)s --colab-process ./audio_folder     # Process audio with MelBandRoformer
    %(prog)s --colab-notebook URL --input-dir ./music  # Custom notebook
  
  File formats supported:
    Text files (.txt) - One URL per line, # for comments
    JSON files (.json) - Lists or objects with URL fields
    CSV files (.csv) - URLs in any column
    M3U playlists (.m3u, .m3u8) - Standard playlist format
  
  Configuration:
    %(prog)s --show-config                      # Display current settings
    %(prog)s --reset                            # Reset to defaults
    %(prog)s -f flac -o ~/Music                 # Settings saved for next time

SUPPORTED FORMATS:
  Audio: flac, mp3, wav, aac, opus, m4a, vorbis
  Video: mp4, mkv, webm (temporary, reverts to audio default)

NAMING SCHEMES:
  title        : Title.flac (default)
  numbered     : 001 - Title.flac
  artist-title : Artist - Title.flac
  album-track  : Album/01 - Title.flac
  date-title   : 20231225 - Title.flac
  id-title     : VideoID - Title.flac
  uploader-title: Uploader - Title.flac
        """
    )
    
    parser.add_argument('sources', nargs='*', 
                       help='URLs, file paths, or text with URLs')
    
    # Format options
    format_group = parser.add_argument_group('format options')
    format_group.add_argument('-f', '--format', 
                             choices=['flac', 'mp3', 'wav', 'aac', 'opus', 'm4a', 'vorbis'],
                             help='Audio format (default: flac or last used)')
    format_group.add_argument('--video', action='store_true',
                             help='Download video instead of audio (does not persist)')
    
    # Output options
    output_group = parser.add_argument_group('output options')
    output_group.add_argument('-o', '--output-dir',
                             help='Output directory')
    output_group.add_argument('-t', '--template',
                             help='Output filename template (yt-dlp format)')
    output_group.add_argument('--naming', 
                             choices=['title', 'numbered', 'artist-title', 'album-track', 
                                    'date-title', 'id-title', 'uploader-title'],
                             help='Naming scheme for output files')
    output_group.add_argument('--organize', action='store_true',
                             help='Organize downloads by source in subdirectories')
    output_group.add_argument('--padding', type=int,
                             help='Number padding for numbered naming (default: 3)')
    
    # Metadata options
    metadata_group = parser.add_argument_group('metadata options')
    metadata_group.add_argument('--no-metadata', action='store_true',
                               help='Disable metadata embedding')
    metadata_group.add_argument('--no-thumbnail', action='store_true',
                               help='Disable thumbnail embedding')
    metadata_group.add_argument('--no-source-url', action='store_true',
                               help='Do not embed source URL in metadata')
    metadata_group.add_argument('--no-playlist-url', action='store_true',
                               help='Do not embed playlist URL in metadata')
    
    # Download options
    download_group = parser.add_argument_group('download options')
    download_group.add_argument('--archive',
                               help='File to track downloaded URLs (avoid duplicates)')
    download_group.add_argument('--skip-archive', action='store_true',
                               help='Skip archive check for this session')
    download_group.add_argument('--rate-limit',
                               help='Download speed limit (e.g., 1M, 500K)')
    download_group.add_argument('--retries', type=int,
                               help='Number of retries for failed downloads')
    download_group.add_argument('--date-after',
                               help='Download only videos after this date (YYYYMMDD)')
    download_group.add_argument('--date-before',
                               help='Download only videos before this date (YYYYMMDD)')
    download_group.add_argument('--batch-size', type=int,
                               help='Process URLs in batches of N')
    download_group.add_argument('--no-geo-bypass', action='store_true',
                               help='Disable geographic restriction bypass')
    download_group.add_argument('--prefer-free-formats', action='store_true',
                               help='Prefer free formats over proprietary ones')
    download_group.add_argument('--proxy',
                               help='Proxy URL (e.g., http://proxy:8080 or socks5://127.0.0.1:1080)')
    download_group.add_argument('-p', '--playlist',  # Short option added
                               help='Download entire playlist when URL includes playlist parameter',
                               action='store_true')
    download_group.add_argument('--bitrate',
                               help='Audio bitrate (e.g., 320 for 320kbps, 0 for best)')
    download_group.add_argument('--sample-rate', '--sr',
                               help='Audio sample rate (e.g., 44100, 48000, 96000)')
    download_group.add_argument('--24bit', '--hi-res', dest='hi_res', action='store_true',
                               help='Use high-resolution settings for highest quality')
    
    # Colab integration options
    colab_group = parser.add_argument_group('colab integration options')
    colab_group.add_argument('--colab-process', metavar='DIR',
                            help='Process audio folder with Google Colab MelBandRoformer')
    colab_group.add_argument('--colab-notebook',
                            help='Custom Colab notebook URL (default: MelBandRoformer)')
    colab_group.add_argument('--colab-segment-size', type=int, default=256,
                            help='MelBandRoformer segment size (default: 256)')
    colab_group.add_argument('--colab-overlap', type=float, default=0.25,
                            help='MelBandRoformer overlap (default: 0.25)')
    colab_group.add_argument('--colab-output',
                            help='Output directory for processed audio')
    colab_group.add_argument('--no-browser', action='store_true',
                            help='Do not open browser automatically')
    colab_group.add_argument('--gui', action='store_true',
                            help='Launch GUI interface')
    
    # Config options
    config_group = parser.add_argument_group('configuration options')
    config_group.add_argument('--show-config', action='store_true',
                             help='Display current configuration and exit')
    config_group.add_argument('--reset', action='store_true',
                             help='Reset to default settings')
    
    args = parser.parse_args()
    
    # Handle GUI mode - if no sources provided, launch GUI by default
    if args.gui or (not args.sources and not args.show_config and not args.reset and not args.colab_process):
        try:
            import tkinter
        except ImportError:
            print("Error: GUI module not available")
            print("Details: No module named '_tkinter'")
            print("\nTo fix this issue:")
            print("  On Ubuntu/Debian: sudo apt-get install python3-tk")
            print("  On Fedora/RHEL:   sudo dnf install python3-tkinter")
            print("  On macOS:         brew install python-tk")
            print("\nAlternatively, ensure your Python installation includes tkinter support.")
            sys.exit(1)
        
        try:
            import gui
            gui.main()
            return
        except ImportError as e:
            print("Error: GUI module not available")
            print(f"Details: {e}")
            print("\nMake sure gui.py is in the same directory as y2wav.py")
            sys.exit(1)
    
    # Handle Colab processing mode
    if args.colab_process:
        try:
            from colab_integration import ColabIntegration
            
            model_params = {
                "model_type": "mel_band_roformer",
                "segment_size": args.colab_segment_size,
                "overlap": args.colab_overlap,
                "use_gpu": True
            }
            
            notebook_url = args.colab_notebook if args.colab_notebook else None
            colab = ColabIntegration(notebook_url)
            
            result = colab.process_audio_folder(
                input_dir=args.colab_process,
                output_dir=args.colab_output,
                model_params=model_params,
                open_browser=not args.no_browser
            )
            
            if result['status'] == 'ready':
                print("\n✓ Colab processing workflow prepared successfully!")
                print(f"\nZip file created: {result['zip_path']}")
                print(f"Processing code saved: {result['code_path']}")
                print(f"Audio files to process: {result['audio_files_count']}")
                print(f"\nColab notebook: {result['notebook_url']}")
            else:
                print(f"\n✗ Error: {result.get('message', 'Unknown error')}")
                sys.exit(1)
            
            return
            
        except ImportError as e:
            print("Error: Colab integration module not available")
            print(f"Details: {e}")
            print("\nMake sure colab_integration.py is in the same directory as y2wav.py")
            sys.exit(1)
        except Exception as e:
            print(f"Error during Colab processing: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    # Load config
    config = Config()
    
    # Show config
    if args.show_config:
        config.display()
        return
    
    # Reset if requested
    if args.reset:
        config.settings = DEFAULT_CONFIG.copy()
        config.save()
        print("✓ Settings reset to defaults")
        config.display()
        return
    
    # Require sources unless showing config or resetting
    if not args.sources:
        parser.print_help()
        sys.exit(0)
    
    # Update config with provided arguments
    update_dict = {}
    if args.format and not args.video:
        update_dict['format'] = args.format
    if args.output_dir:
        update_dict['output_dir'] = args.output_dir
    if args.naming:
        update_dict['naming_scheme'] = args.naming
    if args.organize:
        update_dict['organize_by_source'] = args.organize
    if args.padding:
        update_dict['number_padding'] = args.padding
    if args.no_metadata:
        update_dict['embed_metadata'] = False
    if args.no_thumbnail:
        update_dict['embed_thumbnail'] = False
    if args.no_source_url:
        update_dict['embed_source_url'] = False
    if args.no_playlist_url:
        update_dict['embed_playlist_url'] = False
    if args.archive:
        update_dict['archive_file'] = args.archive
    if args.rate_limit:
        update_dict['rate_limit'] = args.rate_limit
    if args.retries:
        update_dict['retries'] = args.retries
    if args.no_geo_bypass:
        update_dict['geo_bypass'] = False
    if args.prefer_free_formats:
        update_dict['prefer_free_formats'] = True
    if args.proxy:
        update_dict['proxy'] = args.proxy
    if args.playlist:
        # When playlist flag is used, force playlist download
        # This affects how URLs are processed
        pass  # The playlist detection happens in the download method
    if args.bitrate:
        update_dict['bitrate'] = args.bitrate
    if args.sample_rate:
        update_dict['sample_rate'] = args.sample_rate
    if args.hi_res:
        # When high-res flag is used, set high quality settings
        update_dict['postprocessor_args'] = 'ffmpeg:-sample_fmt s32'  # Use 32-bit internal for highest quality
        if not args.sample_rate:  # Only set sample rate if not already specified
            update_dict['sample_rate'] = '48000'  # Standard high quality sample rate
    
    config.update(**update_dict)
    
    # Initialize downloader
    downloader = Downloader(config)
    
    # Parse URLs from sources
    urls = downloader.parse_urls(args.sources)
    
    if not urls:
        print("ERROR: No valid URLs found in input")
        print("\nSupported inputs:")
        print("  - Direct URLs (with or without https://)")
        print("  - Text files (.txt) with one URL per line")
        print("  - JSON files (.json) with URL arrays or objects")
        print("  - CSV files (.csv) with URLs in any column")
        print("  - M3U playlist files (.m3u, .m3u8)")
        sys.exit(1)
    
    # Determine format
    if args.video:
        fmt = 'mp4'
        video = True
    else:
        fmt = args.format
        video = False
    
    # Date range
    date_range = None
    if args.date_after:
        date_range = (args.date_after, args.date_before)
    
    # Download
    downloader.download(
        urls=urls,
        fmt=fmt,
        output_dir=args.output_dir,
        output_template=args.template,
        organize=args.organize,
        video=video,
        naming_scheme=args.naming,
        batch_size=args.batch_size,
        date_range=date_range,
        skip_archive=args.skip_archive
    )


if __name__ == '__main__':
    main()
