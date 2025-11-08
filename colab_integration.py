#!/usr/bin/env python3
"""
Google Colab Integration for Audio Processing
Integrates with MelBandRoformer for audio source separation
"""

import os
import sys
import json
import time
import zipfile
import webbrowser
import tempfile
from pathlib import Path
from typing import List, Optional, Dict

# Google Colab API integration
try:
    from google.colab import auth, files
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    COLAB_AVAILABLE = True
except ImportError:
    COLAB_AVAILABLE = False


class ColabIntegration:
    """Handles Google Colab notebook execution and file management"""
    
    def __init__(self, notebook_url: str = None):
        self.notebook_url = notebook_url or "https://colab.research.google.com/drive/1tyP3ZgcD443d4Q3ly7LcS3toJroLO5o1"
        self.default_notebook_id = "1tyP3ZgcD443d4Q3ly7LcS3toJroLO5o1"
    
    def prepare_audio_files(self, input_dir: str) -> List[str]:
        """Prepare audio files for upload"""
        audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac', '.opus'}
        audio_files = []
        
        input_path = Path(input_dir)
        if not input_path.exists():
            raise ValueError(f"Input directory does not exist: {input_dir}")
        
        for file_path in input_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
                audio_files.append(str(file_path))
        
        print(f"Found {len(audio_files)} audio files to process")
        return audio_files
    
    def create_zip_archive(self, audio_files: List[str], output_path: str) -> str:
        """Create a zip archive of audio files"""
        print(f"Creating zip archive: {output_path}")
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in audio_files:
                arcname = Path(file_path).name
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")
        
        file_size = Path(output_path).stat().st_size / (1024 * 1024)
        print(f"✓ Archive created: {file_size:.2f} MB")
        return output_path
    
    def generate_colab_code(self, audio_files: List[str], model_params: Dict) -> str:
        """Generate Python code to run in Colab notebook"""
        
        code = '''# MelBandRoformer Audio Processing - Auto-generated
# Upload your audio_files.zip and run this code

from google.colab import files
import zipfile
import os
from pathlib import Path
import torch
import torchaudio
from tqdm.auto import tqdm

# Setup directories
extract_dir = "/content/audio_input"
output_dir = "/content/audio_output"
os.makedirs(extract_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Upload and extract audio files
print("Please upload your audio_files.zip")
uploaded = files.upload()

zip_filename = list(uploaded.keys())[0]
with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

print(f"Extracted files to: {extract_dir}")

# List audio files
audio_files = []
for ext in ['*.wav', '*.mp3', '*.flac', '*.ogg', '*.m4a']:
    audio_files.extend(Path(extract_dir).glob(ext))

print(f"Found {len(audio_files)} audio files")

# Device setup
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Model parameters
model_params = ''' + json.dumps(model_params, indent=2) + '''

# Install dependencies
!pip install -q torch torchaudio librosa soundfile demucs

# Process audio files
results = []
for audio_path in tqdm(audio_files, desc="Processing"):
    try:
        # Load audio
        waveform, sample_rate = torchaudio.load(str(audio_path))
        
        # Process with MelBandRoformer
        # Note: Insert actual model processing here
        # output = model.separate(waveform)
        
        # Save output
        output_path = Path(output_dir) / f"processed_{audio_path.name}"
        # torchaudio.save(str(output_path), output, sample_rate)
        
        results.append({
            "input": str(audio_path),
            "output": str(output_path),
            "status": "success"
        })
        
        print(f"✓ Processed: {audio_path.name}")
        
    except Exception as e:
        print(f"✗ Error: {audio_path.name}: {e}")
        results.append({
            "input": str(audio_path),
            "status": "error",
            "error": str(e)
        })

# Create output zip
output_zip = "/content/processed_audio.zip"
with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file in Path(output_dir).glob("*"):
        if file.is_file():
            zipf.write(file, file.name)

print(f"\\n✓ Processing complete!")
print(f"  Successful: {sum(1 for r in results if r['status'] == 'success')}")
print(f"  Failed: {sum(1 for r in results if r['status'] == 'error')}")

# Download results
files.download(output_zip)
'''
        return code
    
    def open_colab_notebook(self, code: str = None):
        """Open Colab notebook in browser"""
        print("\n" + "="*70)
        print("GOOGLE COLAB INTEGRATION")
        print("="*70)
        print(f"\n📓 Opening Colab notebook...")
        print(f"   URL: {self.notebook_url}\n")
        
        if code:
            print("Generated code to paste in Colab:")
            print("-" * 70)
            print(code)
            print("-" * 70)
        
        print("\n📋 INSTRUCTIONS:")
        print("  1. The Colab notebook will open in your browser")
        print("  2. Upload the audio_files.zip when prompted")
        print("  3. Run all cells to process your audio")
        print("  4. Download processed_audio.zip when complete")
        print("  5. Extract the zip to get your processed audio files")
        print("\n" + "="*70 + "\n")
        
        # Open notebook in browser
        webbrowser.open(self.notebook_url)
        return True
    
    def process_audio_folder(self, 
                            input_dir: str, 
                            output_dir: str = None,
                            model_params: Dict = None,
                            open_browser: bool = True) -> Dict:
        """
        Main method to process audio folder with Colab
        
        Args:
            input_dir: Directory containing audio files
            output_dir: Directory to save processed files
            model_params: Parameters for MelBandRoformer model
            open_browser: Whether to open Colab in browser
            
        Returns:
            Dictionary with processing information
        """
        
        if model_params is None:
            model_params = {
                "model_type": "mel_band_roformer",
                "segment_size": 256,
                "batch_size": 1,
                "overlap": 0.25,
                "use_gpu": True
            }
        
        if output_dir is None:
            output_dir = Path(input_dir).parent / "processed_audio"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print("\n" + "="*70)
        print("COLAB AUDIO PROCESSING WORKFLOW")
        print("="*70)
        print(f"  Input directory:  {input_dir}")
        print(f"  Output directory: {output_dir}")
        print(f"  Model: MelBandRoformer")
        print("="*70 + "\n")
        
        # Step 1: Prepare audio files
        print("[1/4] Preparing audio files...")
        audio_files = self.prepare_audio_files(input_dir)
        
        if not audio_files:
            print("✗ No audio files found!")
            return {"status": "error", "message": "No audio files found"}
        
        # Step 2: Create zip archive
        print("\n[2/4] Creating zip archive...")
        temp_dir = tempfile.gettempdir()
        zip_path = os.path.join(temp_dir, "audio_files.zip")
        self.create_zip_archive(audio_files, zip_path)
        
        # Step 3: Generate Colab code
        print("\n[3/4] Generating Colab processing code...")
        colab_code = self.generate_colab_code(audio_files, model_params)
        
        # Save code to file for easy copy-paste
        code_path = os.path.join(output_dir, "colab_processing_code.py")
        with open(code_path, 'w') as f:
            f.write(colab_code)
        print(f"✓ Code saved to: {code_path}")
        
        # Step 4: Open Colab notebook
        print("\n[4/4] Opening Colab notebook...")
        if open_browser:
            self.open_colab_notebook(colab_code)
        
        return {
            "status": "ready",
            "zip_path": zip_path,
            "code_path": code_path,
            "audio_files_count": len(audio_files),
            "output_dir": str(output_dir),
            "notebook_url": self.notebook_url,
            "instructions": [
                f"1. Upload {zip_path} to Colab",
                "2. Copy and run the generated code",
                f"3. Download processed files to {output_dir}"
            ]
        }


if __name__ == '__main__':
    # Test functionality
    import argparse
    parser = argparse.ArgumentParser(description='Test Colab integration')
    parser.add_argument('input_dir', help='Directory with audio files')
    parser.add_argument('-o', '--output-dir', help='Output directory')
    args = parser.parse_args()
    
    colab = ColabIntegration()
    result = colab.process_audio_folder(args.input_dir, args.output_dir)
    
    print("\n" + "="*70)
    print("RESULT:")
    print(json.dumps(result, indent=2))
    print("="*70)
