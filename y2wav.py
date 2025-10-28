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
    "format": "flac",
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
    "prefer_free_formats": False
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
            pass  # Temporary
        else:
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
        deps = {'yt-dlp': 'yt-dlp', 'ffmpeg': 'ffmpeg'}
        missing = []
        
        for name, cmd in deps.items():
            try:
                subprocess.run([cmd, '--version'], 
                             capture_output=True, 
                             check=True,
                             timeout=5)
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                missing.append(name)
        
        if missing:
            print(f"ERROR: Missing dependencies: {', '.join(missing)}")
            print("\nInstall with:")
            if 'yt-dlp' in missing:
                print("  pip install yt-dlp")
                print("  # or: pip install --upgrade yt-dlp")
            if 'ffmpeg' in missing:
                print("  # Install ffmpeg:")
                print("  # - Ubuntu/Debian: sudo apt install ffmpeg")
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
        
        print(f"\n{'='*70}")
        print(f"DOWNLOAD SESSION STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        print(f"URLs to process: {len(urls)}")
        print(f"Format: {fmt.upper() if not video else 'VIDEO (MP4)'}")
        print(f"Quality: Best available (lossless for audio)")
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
                
                # Playlist handling
                playlist_url = None
                if 'playlist' in url_type or '&list=' in url:
                    cmd.append('--yes-playlist')
                    playlist_url = url
                else:
                    cmd.append('--no-playlist')
                
                # Format selection
                if video:
                    cmd.extend(['-f', 'bestvideo+bestaudio/best'])
                else:
                    cmd.extend(['-f', 'bestaudio/best'])
                    
                    # Audio extraction and conversion
                    cmd.extend([
                        '--extract-audio',
                        '--audio-format', fmt,
                        '--audio-quality', '0',  # Best quality
                    ])
                
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
                    '--no-overwrites',
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
                    if fmt == 'flac':
                        cmd.extend(['--postprocessor-args', 'ffmpeg:-compression_level 0'])
                    elif fmt == 'wav':
                        cmd.extend(['--postprocessor-args', 'ffmpeg:-c:a pcm_s24le'])
                    else:
                        cmd.extend(['--postprocessor-args', 'ffmpeg:-q:a 0'])
                
                cmd.append(url)
                
                # Execute download
                print(f"  Downloading...")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"  ✓ Successfully downloaded")
                    success_count += 1
                    self.save_to_archive(url)
                else:
                    print(f"  ✗ Failed to download")
                    if result.stderr:
                        error_lines = result.stderr.split('\n')
                        relevant_errors = [line for line in error_lines if 'ERROR' in line]
                        if relevant_errors:
                            print(f"     Error: {relevant_errors[0][:100]}")
                    fail_count += 1
                    
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
    %(prog)s -t "%(artist)s/%(album)s/%(title)s.%(ext)s" urls.txt
  
  Advanced features:
    %(prog)s --archive downloads.txt urls.txt   # Track & skip duplicates
    %(prog)s --rate-limit 1M urls.txt           # Limit to 1MB/s
    %(prog)s --date-after 20231201 urls.txt     # Only recent videos
    %(prog)s --no-metadata urls.txt             # Skip metadata embedding
  
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
    
    # Config options
    config_group = parser.add_argument_group('configuration options')
    config_group.add_argument('--show-config', action='store_true',
                             help='Display current configuration and exit')
    config_group.add_argument('--reset', action='store_true',
                             help='Reset to default settings')
    
    args = parser.parse_args()
    
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
