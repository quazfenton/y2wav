#!/usr/bin/env python3
"""
GUI for y2wav Audio Downloader with Colab Integration
Simple and intuitive interface for audio downloading and processing
"""

# First check if tkinter is available
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
except ImportError:
    print("Error: GUI module not available")
    print("Details: No module named '_tkinter'")
    print("\nTo fix this issue:")
    print("  On Ubuntu/Debian: sudo apt-get install python3-tk")
    print("  On Fedora/RHEL:   sudo dnf install python3-tkinter")
    print("  On macOS:         brew install python-tk")
    print("\nAlternatively, ensure your Python installation includes tkinter support.")
    import sys
    sys.exit(1)

import threading
import queue
import sys
from pathlib import Path

# Import our modules
try:
    from colab_integration import ColabIntegration
    COLAB_AVAILABLE = True
except ImportError:
    COLAB_AVAILABLE = False
    print("Warning: Colab integration not available")


class Y2WavGUI:
    """Main GUI application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Y2Wav - Audio Downloader & Processor")
        self.root.geometry("900x700")
        
        # Queue for thread-safe logging
        self.log_queue = queue.Queue()
        
        # Setup GUI
        self.create_widgets()
        self.load_default_settings()  # Load default settings on startup
        self.check_log_queue()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Create notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Download
        download_frame = ttk.Frame(notebook)
        notebook.add(download_frame, text="Download Audio")
        self.create_download_tab(download_frame)
        
        # Tab 2: Colab Processing
        colab_frame = ttk.Frame(notebook)
        notebook.add(colab_frame, text="Colab Processing")
        self.create_colab_tab(colab_frame)
        
        # Tab 3: Settings
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Settings")
        self.create_settings_tab(settings_frame)
        
        # Log area (bottom)
        log_frame = ttk.LabelFrame(self.root, text="Log Output", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def create_download_tab(self, parent):
        """Create download tab widgets"""
        
        # URL Input Section
        url_frame = ttk.LabelFrame(parent, text="Input URLs", padding=10)
        url_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(url_frame, text="Enter URLs (one per line) or load from file:").pack(anchor=tk.W)
        
        self.url_text = scrolledtext.ScrolledText(url_frame, height=8, wrap=tk.WORD)
        self.url_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        url_buttons = ttk.Frame(url_frame)
        url_buttons.pack(fill=tk.X, pady=5)
        
        ttk.Button(url_buttons, text="Load File", command=self.load_url_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(url_buttons, text="Clear", command=lambda: self.url_text.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)
        ttk.Button(url_buttons, text="Example", command=self.load_example_urls).pack(side=tk.LEFT, padx=5)
        
        # Format Options
        format_frame = ttk.LabelFrame(parent, text="Format Options", padding=10)
        format_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(format_frame, text="Audio Format:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.format_var = tk.StringVar(value="flac")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var, 
                                     values=["flac", "mp3", "wav", "opus", "aac", "m4a"], 
                                     state="readonly", width=15)
        format_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(format_frame, text="Naming:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.naming_var = tk.StringVar(value="title")
        naming_combo = ttk.Combobox(format_frame, textvariable=self.naming_var,
                                     values=["title", "numbered", "artist-title", "date-title", "id-title"],
                                     state="readonly", width=15)
        naming_combo.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Quality Options
        quality_frame = ttk.LabelFrame(parent, text="Quality Options", padding=10)
        quality_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add quality selection
        ttk.Label(quality_frame, text="Quality:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.quality_var = tk.StringVar(value="best")
        quality_combo = ttk.Combobox(quality_frame, textvariable=self.quality_var,
                                      values=["best", "high", "medium", "low"],
                                      state="readonly", width=15)
        quality_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Additional options
        options_frame = ttk.Frame(quality_frame)
        options_frame.grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        
        self.no_overwrites_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="No Overwrites", variable=self.no_overwrites_var).pack(anchor=tk.W)
        
        # Add proxy setting
        proxy_frame = ttk.LabelFrame(parent, text="Proxy Settings", padding=10)
        proxy_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(proxy_frame, text="Proxy URL (optional, e.g., http://proxy:8080):").pack(anchor=tk.W, pady=(0, 5))
        self.proxy_var = tk.StringVar()
        proxy_entry = ttk.Entry(proxy_frame, textvariable=self.proxy_var, width=50)
        proxy_entry.pack(fill=tk.X, pady=(0, 5))
        
        # Playlist handling
        playlist_frame = ttk.Frame(proxy_frame)
        playlist_frame.pack(fill=tk.X, pady=5)
        
        self.download_playlist_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(playlist_frame, text="Download entire playlist if URL contains playlist", 
                       variable=self.download_playlist_var).pack(anchor=tk.W)
        
        # Output Directory
        output_frame = ttk.Frame(parent)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(output_frame, text="Output Directory:").pack(side=tk.LEFT, padx=5)
        self.output_dir_var = tk.StringVar(value="./downloads")
        ttk.Entry(output_frame, textvariable=self.output_dir_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(output_frame, text="Browse", command=self.browse_output_dir).pack(side=tk.LEFT)
        
        # Download Button and Progress
        download_btn_frame = ttk.Frame(parent)
        download_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        button_progress_frame = ttk.Frame(download_btn_frame)
        button_progress_frame.pack(fill=tk.X)
        
        self.download_btn = ttk.Button(button_progress_frame, text="⬇️ Download Audio", 
                                       command=self.start_download, style="Accent.TButton")
        self.download_btn.pack(side=tk.LEFT, pady=10)
        
        # Progress bar for downloads
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(button_progress_frame, variable=self.progress_var, 
                                           maximum=100, length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=(10, 0), pady=10, fill=tk.X, expand=True)
        
        # Status label
        self.status_label = ttk.Label(download_btn_frame, text="Ready to download", 
                                     foreground="gray")
        self.status_label.pack(pady=(0, 10))
        
    def create_colab_tab(self, parent):
        """Create Colab processing tab"""
        
        # Input Directory
        input_frame = ttk.LabelFrame(parent, text="Audio Files", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(input_frame, text="Select folder with audio files to process:").pack(anchor=tk.W, pady=5)
        
        dir_frame = ttk.Frame(input_frame)
        dir_frame.pack(fill=tk.X)
        
        self.colab_input_dir = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.colab_input_dir, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(dir_frame, text="Browse", command=self.browse_colab_input).pack(side=tk.LEFT)
        
        # Output Directory
        output_frame = ttk.Frame(input_frame)
        output_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(output_frame, text="Processed files will be saved to:").pack(side=tk.LEFT, padx=5)
        self.colab_output_dir = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.colab_output_dir, width=30).pack(side=tk.LEFT, padx=5)
        ttk.Button(output_frame, text="Browse", command=self.browse_colab_output).pack(side=tk.LEFT)
        
        # Model Parameters
        params_frame = ttk.LabelFrame(parent, text="MelBandRoformer Parameters", padding=10)
        params_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(params_frame, text="Segment Size:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.segment_size = tk.IntVar(value=256)
        ttk.Entry(params_frame, textvariable=self.segment_size, width=10).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(params_frame, text="Overlap:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.overlap = tk.DoubleVar(value=0.25)
        ttk.Entry(params_frame, textvariable=self.overlap, width=10).grid(row=0, column=3, sticky=tk.W, pady=5)
        
        self.use_gpu = tk.BooleanVar(value=True)
        ttk.Checkbutton(params_frame, text="Use GPU", variable=self.use_gpu).grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Notebook URL
        notebook_frame = ttk.Frame(parent)
        notebook_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(notebook_frame, text="Colab Notebook URL:").pack(side=tk.LEFT, padx=5)
        self.notebook_url = tk.StringVar(value="https://colab.research.google.com/drive/1tyP3ZgcD443d4Q3ly7LcS3toJroLO5o1")
        ttk.Entry(notebook_frame, textvariable=self.notebook_url, width=60).pack(side=tk.LEFT, padx=5)
        
        # Process Button
        process_btn_frame = ttk.Frame(parent)
        process_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.process_btn = ttk.Button(process_btn_frame, text="🚀 Process with Colab", 
                                      command=self.start_colab_processing, style="Accent.TButton")
        self.process_btn.pack(pady=10)
        
        # Instructions
        info_frame = ttk.LabelFrame(parent, text="Instructions", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        instructions = """
1. Select a folder containing audio files (WAV, MP3, FLAC, etc.)
2. Click 'Process with Colab' to prepare files and open the notebook
3. Upload the generated audio_files.zip to Colab when prompted
4. Run the generated code in Colab to process your audio
5. Download the processed_audio.zip from Colab
6. Extract the files to your specified output directory
        """
        
        ttk.Label(info_frame, text=instructions.strip(), justify=tk.LEFT).pack(anchor=tk.W)
        
    def create_settings_tab(self, parent):
        """Create settings tab"""
        
        settings_frame = ttk.LabelFrame(parent, text="Download Settings", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Format and quality options
        format_frame = ttk.Frame(settings_frame)
        format_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(format_frame, text="Default Format:").pack(side=tk.LEFT)
        self.default_format_var = tk.StringVar(value="flac")
        format_combo = ttk.Combobox(format_frame, textvariable=self.default_format_var, 
                                     values=["flac", "mp3", "wav", "opus", "aac", "m4a"], 
                                     state="readonly", width=10)
        format_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(format_frame, text="Default Quality:").pack(side=tk.LEFT, padx=(20, 0))
        self.default_quality_var = tk.StringVar(value="best")
        quality_combo = ttk.Combobox(format_frame, textvariable=self.default_quality_var,
                                      values=["best", "high", "medium", "low"],
                                      state="readonly", width=10)
        quality_combo.pack(side=tk.LEFT, padx=5)
        
        # Metadata options
        metadata_frame = ttk.Frame(settings_frame)
        metadata_frame.pack(fill=tk.X, pady=5)
        
        self.embed_metadata = tk.BooleanVar(value=True)
        ttk.Checkbutton(metadata_frame, text="Embed metadata", variable=self.embed_metadata).pack(side=tk.LEFT)
        
        self.embed_thumbnail = tk.BooleanVar(value=True)
        ttk.Checkbutton(metadata_frame, text="Embed thumbnail", variable=self.embed_thumbnail).pack(side=tk.LEFT, padx=(10, 0))
        
        self.organize = tk.BooleanVar(value=False)
        ttk.Checkbutton(metadata_frame, text="Organize by source", variable=self.organize).pack(side=tk.LEFT, padx=(10, 0))
        
        # Archive and rate limit options
        other_frame = ttk.Frame(settings_frame)
        other_frame.pack(fill=tk.X, pady=5)
        
        self.no_overwrites = tk.BooleanVar(value=True)
        ttk.Checkbutton(other_frame, text="No Overwrites", variable=self.no_overwrites).pack(side=tk.LEFT)
        
        # Archive file
        archive_frame = ttk.Frame(settings_frame)
        archive_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(archive_frame, text="Archive file (track downloads):").pack(side=tk.LEFT)
        self.archive_file = tk.StringVar()
        ttk.Entry(archive_frame, textvariable=self.archive_file, width=30).pack(side=tk.LEFT, padx=5)
        ttk.Button(archive_frame, text="Browse", command=self.browse_archive).pack(side=tk.LEFT)
        
        # Rate limit
        rate_frame = ttk.Frame(settings_frame)
        rate_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(rate_frame, text="Rate limit (e.g., 1M):").pack(side=tk.LEFT)
        self.rate_limit = tk.StringVar()
        ttk.Entry(rate_frame, textvariable=self.rate_limit, width=10).pack(side=tk.LEFT, padx=5)
        
        # Proxy settings
        proxy_frame = ttk.Frame(settings_frame)
        proxy_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(proxy_frame, text="Proxy URL (e.g., http://proxy:8080):").pack(side=tk.LEFT)
        self.default_proxy = tk.StringVar()
        ttk.Entry(proxy_frame, textvariable=self.default_proxy, width=30).pack(side=tk.LEFT, padx=5)
        
        # High quality settings
        quality_frame = ttk.LabelFrame(settings_frame, text="High-Quality Settings", padding=5)
        quality_frame.pack(fill=tk.X, pady=5)
        
        # Bit depth and sample rate options
        quality_settings_frame = ttk.Frame(quality_frame)
        quality_settings_frame.pack(fill=tk.X)
        
        self.use_high_res = tk.BooleanVar(value=False)
        ttk.Checkbutton(quality_settings_frame, text="High-Res (24-bit)", variable=self.use_high_res).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(quality_settings_frame, text="Sample Rate:").pack(side=tk.LEFT)
        self.sample_rate_var = tk.StringVar(value="48000")
        sample_rate_combo = ttk.Combobox(quality_settings_frame, textvariable=self.sample_rate_var,
                                        values=["44100", "48000", "96000", "192000"],
                                        state="readonly", width=8)
        sample_rate_combo.pack(side=tk.LEFT, padx=5)
        
        # Save settings button
        save_frame = ttk.Frame(settings_frame)
        save_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(save_frame, text="💾 Save Default Settings", 
                  command=self.save_default_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(save_frame, text="🔄 Load Saved Settings", 
                  command=self.load_default_settings).pack(side=tk.LEFT, padx=5)
        
    def load_url_file(self):
        """Load URLs from file"""
        filename = filedialog.askopenfilename(
            title="Select URL file",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                self.url_text.delete(1.0, tk.END)
                self.url_text.insert(1.0, content)
                self.log(f"Loaded URLs from: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")
    
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.output_dir_var.set(directory)
    
    def save_default_settings(self):
        """Save default settings from Settings tab to persistent config"""
        try:
            import y2wav
            config = y2wav.Config()
            
            # Update config with default settings from Settings tab
            config.settings['format'] = self.default_format_var.get()
            config.settings['quality'] = self.default_quality_var.get()
            config.settings['embed_metadata'] = self.embed_metadata.get()
            config.settings['embed_thumbnail'] = self.embed_thumbnail.get()
            config.settings['organize_by_source'] = self.organize.get()
            config.settings['no_overwrites'] = self.no_overwrites.get()
            
            if self.archive_file.get():
                config.settings['archive_file'] = self.archive_file.get()
            if self.rate_limit.get():
                config.settings['rate_limit'] = self.rate_limit.get()
            if self.default_proxy.get():
                config.settings['proxy'] = self.default_proxy.get()
            
            # High-quality settings
            if self.use_high_res.get():
                config.settings['postprocessor_args'] = 'ffmpeg:-sample_fmt s32'
                config.settings['sample_rate'] = self.sample_rate_var.get()
            else:
                config.settings['postprocessor_args'] = None
                config.settings['sample_rate'] = None
            
            # Save the configuration
            config.save()
            
            messagebox.showinfo("Settings Saved", "Default settings have been saved successfully!")
            self.log("Default settings saved to config")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            self.log(f"Error saving default settings: {e}")
    
    def load_default_settings(self):
        """Load default settings from config to Settings tab"""
        try:
            import y2wav
            config = y2wav.Config()
            
            # Load settings into GUI variables
            self.default_format_var.set(config.settings.get('format', 'flac'))
            self.default_quality_var.set(config.settings.get('quality', 'best'))
            self.embed_metadata.set(config.settings.get('embed_metadata', True))
            self.embed_thumbnail.set(config.settings.get('embed_thumbnail', True))
            self.organize.set(config.settings.get('organize_by_source', False))
            self.no_overwrites.set(config.settings.get('no_overwrites', True))
            
            if config.settings.get('archive_file'):
                self.archive_file.set(config.settings['archive_file'])
            if config.settings.get('rate_limit'):
                self.rate_limit.set(config.settings['rate_limit'])
            if config.settings.get('proxy'):
                self.default_proxy.set(config.settings['proxy'])
            
            # High-quality settings
            if config.settings.get('postprocessor_args'):
                self.use_high_res.set(True)
                sample_rate = config.settings.get('sample_rate', '48000')
                self.sample_rate_var.set(sample_rate)
            else:
                self.use_high_res.set(False)
                self.sample_rate_var.set('48000')  # Default
            
            self.log("Default settings loaded from config")
            
        except Exception as e:
            self.log(f"Error loading default settings: {e}")
    
    def browse_colab_input(self):
        """Browse for Colab input directory"""
        directory = filedialog.askdirectory(title="Select audio files directory")
        if directory:
            self.colab_input_dir.set(directory)
            # Auto-set output directory
            if not self.colab_output_dir.get():
                parent = Path(directory).parent
                self.colab_output_dir.set(str(parent / "processed_audio"))
    
    def browse_colab_output(self):
        """Browse for Colab output directory"""
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.colab_output_dir.set(directory)
    
    def browse_archive(self):
        """Browse for archive file"""
        filename = filedialog.asksaveasfilename(
            title="Select archive file",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.archive_file.set(filename)
    
    def load_example_urls(self):
        """Load example URLs for testing"""
        example_urls = """https://www.youtube.com/watch?v=dQw4w9WgXcQ  # Never Gonna Give You Up
https://music.youtube.com/watch?v=J---aiyznGQ  # Keyboard Cat
https://soundcloud.com/nocopyrightsounds/laxidasical-catchme"""
        self.url_text.delete(1.0, tk.END)
        self.url_text.insert(1.0, example_urls)
        self.log("Loaded example URLs")
    
    def log(self, message):
        """Add message to log (thread-safe)"""
        self.log_queue.put(message)
    
    def check_log_queue(self):
        """Check log queue and update GUI"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
                self.log_text.update()
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_log_queue)
    
    def start_download(self):
        """Start download in background thread"""
        urls = self.url_text.get(1.0, tk.END).strip()
        
        if not urls:
            messagebox.showwarning("No URLs", "Please enter URLs to download")
            return
        
        self.download_btn.config(state=tk.DISABLED, text="Downloading...")
        self.progress_var.set(0)
        self.status_label.config(text="Starting download...")
        self.log("="*70)
        self.log("Starting download...")
        self.log("="*70)
        
        def download_thread():
            try:
                # Import our y2wav module and use its Downloader class
                try:
                    import y2wav
                except ImportError as e:
                    raise Exception(f"Failed to import y2wav module: {e}")
                
                # Check dependencies before creating config
                config = y2wav.Config()
                
                # Update config with GUI settings (prioritizing the download tab settings)
                config.settings['format'] = self.format_var.get()
                config.settings['output_dir'] = self.output_dir_var.get()
                config.settings['naming_scheme'] = self.naming_var.get()
                config.settings['embed_metadata'] = self.embed_metadata.get()
                config.settings['embed_thumbnail'] = self.embed_thumbnail.get()
                config.settings['organize_by_source'] = self.organize.get()
                
                # Apply quality settings
                quality = self.quality_var.get()
                if quality == "best":
                    config.settings['quality'] = "best"
                elif quality == "high":
                    config.settings['quality'] = "high"
                elif quality == "medium":
                    config.settings['quality'] = "medium"
                elif quality == "low":
                    config.settings['quality'] = "low"
                
                # Additional settings
                config.settings['no_overwrites'] = self.no_overwrites_var.get()
                
                if self.archive_file.get():
                    config.settings['archive_file'] = self.archive_file.get()
                if self.rate_limit.get():
                    config.settings['rate_limit'] = self.rate_limit.get()
                if self.proxy_var.get():
                    config.settings['proxy'] = self.proxy_var.get()
                
                # High-quality settings (from Settings tab)
                if self.use_high_res.get():
                    config.settings['postprocessor_args'] = 'ffmpeg:-sample_fmt s32'
                    config.settings['sample_rate'] = self.sample_rate_var.get()
                else:
                    # If not using high-res, check if the config has these settings and clear them
                    config.settings['postprocessor_args'] = None
                    config.settings['sample_rate'] = None
                # The playlist detection is handled by the URL type detection in y2wav
                
                # Parse URLs from text input
                url_list = urls.split('\n')
                url_list = [url.strip() for url in url_list if url.strip() and not url.strip().startswith('#')]
                
                if not url_list:
                    self.log("No valid URLs to process")
                    return
                
                # Update status
                self.root.after(0, lambda: self.status_label.config(text=f"Processing {len(url_list)} URLs..."))
                
                # Create downloader instance - this will check for dependencies
                try:
                    downloader = y2wav.Downloader(config)
                except SystemExit as e:
                    # Handle the SystemExit that happens when dependencies are missing
                    error_msg = ("Required dependencies (yt-dlp, ffmpeg) are not available. "
                               "Make sure you're running in the correct environment.\n\n"
                               "If you installed dependencies in a virtual environment, "
                               "ensure you've activated it first:\n"
                               "  source venv/bin/activate\n\n"
                               "Then run the GUI again.")
                    self.log(f"✗ Dependency error: {error_msg}")
                    self.root.after(0, lambda: messagebox.showerror("Dependency Error", error_msg))
                    return
                except Exception as e:
                    error_msg = f"Failed to create downloader: {e}"
                    self.log(f"✗ Error creating downloader: {error_msg}")
                    self.root.after(0, lambda: messagebox.showerror("Downloader Error", str(e)))
                    return
                
                # Log the settings
                self.log(f"Format: {config.settings['format']}")
                self.log(f"Output: {config.settings['output_dir']}")
                self.log(f"Naming: {config.settings['naming_scheme']}")
                self.log(f"Quality: {config.settings['quality']}")
                self.log(f"URLs to process: {len(url_list)}")
                self.log(f"Proxy: {config.settings['proxy'] if config.settings['proxy'] else 'None'}")
                self.log("\nProcessing URLs...")
                
                # Perform actual download (modified to update progress)
                success_count = 0
                fail_count = 0
                
                for i, url in enumerate(url_list, 1):
                    self.root.after(0, lambda i=i, total=len(url_list): self.update_progress(i, total))
                    self.root.after(0, lambda i=i, total=len(url_list): self.status_label.config(
                        text=f"Downloading {i}/{total}..."))
                    
                    try:
                        # Process single URL to allow progress updates
                        downloader.download(
                            urls=[url],
                            fmt=config.settings['format'],
                            output_dir=config.settings['output_dir'],
                            naming_scheme=config.settings['naming_scheme'],
                            organize=config.settings['organize_by_source']
                        )
                        success_count += 1
                    except Exception as e:
                        fail_count += 1
                        self.log(f"  ✗ Failed to download {url}: {e}")
                
                self.log(f"✓ Download complete! Success: {success_count}, Failed: {fail_count}")
                
            except Exception as e:
                import traceback
                self.log(f"✗ Error: {e}")
                self.log(f"Traceback: {traceback.format_exc()}")
                # Show error to user in the GUI thread
                self.root.after(0, lambda: messagebox.showerror("Download Error", str(e)))
            finally:
                self.root.after(0, lambda: self.download_btn.config(state=tk.NORMAL, text="⬇️ Download Audio"))
                self.root.after(0, lambda: self.progress_var.set(0))
                self.root.after(0, lambda: self.status_label.config(text="Download complete!"))
        
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
    
    def update_progress(self, current, total):
        """Update the progress bar"""
        progress = (current / total) * 100
        self.progress_var.set(progress)
    
    def start_colab_processing(self):
        """Start Colab processing"""
        input_dir = self.colab_input_dir.get()
        
        if not input_dir:
            messagebox.showwarning("No Input", "Please select an input directory")
            return
        
        if not Path(input_dir).exists():
            messagebox.showerror("Error", "Input directory does not exist")
            return
        
        self.process_btn.config(state=tk.DISABLED, text="Processing...")
        self.log("="*70)
        self.log("Starting Colab processing workflow...")
        self.log("="*70)
        
        def process_thread():
            try:
                if not COLAB_AVAILABLE:
                    self.log("Warning: Colab integration module not available")
                    return
                
                # Get parameters
                model_params = {
                    "model_type": "mel_band_roformer",
                    "segment_size": self.segment_size.get(),
                    "overlap": self.overlap.get(),
                    "use_gpu": self.use_gpu.get()
                }
                
                output_dir = self.colab_output_dir.get() or None
                
                # Process
                colab = ColabIntegration(self.notebook_url.get())
                result = colab.process_audio_folder(
                    input_dir=input_dir,
                    output_dir=output_dir,
                    model_params=model_params,
                    open_browser=True
                )
                
                self.log(f"\n✓ Preparation complete!")
                self.log(f"  Zip file: {result['zip_path']}")
                self.log(f"  Code saved: {result['code_path']}")
                self.log(f"  Audio files: {result['audio_files_count']}")
                self.log(f"\nNext steps:")
                for instruction in result['instructions']:
                    self.log(f"  {instruction}")
                
            except Exception as e:
                self.log(f"✗ Error: {e}")
                import traceback
                self.log(traceback.format_exc())
            finally:
                self.root.after(0, lambda: self.process_btn.config(state=tk.NORMAL, text="🚀 Process with Colab"))
        
        thread = threading.Thread(target=process_thread, daemon=True)
        thread.start()


def main():
    """Launch GUI application"""
    root = tk.Tk()
    app = Y2WavGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
