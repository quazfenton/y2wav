#!/bin/bash
# Demo script for y2wav with Colab integration

echo "=================================="
echo "Y2Wav + Colab Integration Demo"
echo "=================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

echo "✓ Python 3 found"

# Check dependencies
echo ""
echo "Checking dependencies..."

# Check yt-dlp
if python3 -c "import yt_dlp" 2>/dev/null; then
    echo "✓ yt-dlp installed"
else
    echo "⚠ yt-dlp not installed"
    echo "  Install with: pip install yt-dlp"
fi

# Check ffmpeg
if command -v ffmpeg &> /dev/null; then
    echo "✓ ffmpeg installed"
else
    echo "⚠ ffmpeg not installed"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS: brew install ffmpeg"
fi

# Check tkinter for GUI
if python3 -c "import tkinter" 2>/dev/null; then
    echo "✓ tkinter installed (GUI available)"
else
    echo "⚠ tkinter not installed (GUI unavailable)"
    echo "  Ubuntu/Debian: sudo apt install python3-tk"
fi

echo ""
echo "=================================="
echo "Available Commands:"
echo "=================================="
echo ""

echo "1. Show help:"
echo "   python3 y2wav.py --help"
echo ""

echo "2. Download audio:"
echo "   python3 y2wav.py 'https://youtube.com/watch?v=...'"
echo "   python3 y2wav.py -f mp3 urls.txt"
echo ""

echo "3. Process with Colab:"
echo "   python3 y2wav.py --colab-process ./audio_folder"
echo ""

echo "4. Launch GUI:"
echo "   python3 y2wav.py --gui"
echo ""

echo "5. Complete workflow:"
echo "   # Download"
echo "   python3 y2wav.py -f flac -o ./downloads urls.txt"
echo "   # Process"
echo "   python3 y2wav.py --colab-process ./downloads"
echo ""

echo "=================================="
echo "Quick Test (with dummy files):"
echo "=================================="
echo ""

# Create test directory
TEST_DIR="demo_audio"
if [ -d "$TEST_DIR" ]; then
    echo "Cleaning up old test directory..."
    rm -rf "$TEST_DIR"
fi

echo "Creating test audio files..."
mkdir -p "$TEST_DIR"
for i in {1..3}; do
    echo "Test audio file $i" > "$TEST_DIR/test_song_$i.mp3"
done

echo "✓ Created 3 test files in ./$TEST_DIR/"
echo ""

echo "Running Colab integration test..."
python3 y2wav.py --colab-process "./$TEST_DIR" --no-browser --colab-output "./demo_output"

echo ""
echo "=================================="
echo "Test Complete!"
echo "=================================="
echo ""
echo "Check the following:"
echo "  - Zip file: /tmp/audio_files.zip"
echo "  - Generated code: ./demo_output/colab_processing_code.py"
echo ""
echo "To clean up test files:"
echo "  rm -rf $TEST_DIR demo_output /tmp/audio_files.zip"
echo ""
echo "=================================="
echo "For more information:"
echo "  - See README_COLAB.md"
echo "  - See FEATURE_SUMMARY.md"
echo "=================================="
