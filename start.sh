#!/bin/bash
# y2wav starter script

echo "Y2Wav Audio Downloader"
echo "======================"

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Warning: No virtual environment detected."
    echo "Looking for venv directory..."
    
    if [ -d "venv" ]; then
        echo "Found venv directory. Activating..."
        source venv/bin/activate
        echo "Virtual environment activated."
    else
        echo "No venv directory found in current location."
        echo "Please activate your virtual environment manually:"
        echo "  source venv/bin/activate"
        echo "Then run this script again."
        exit 1
    fi
else
    echo "Virtual environment already active: $VIRTUAL_ENV"
fi

echo ""
echo "Python executable: $(which python)"
echo "yt-dlp location: $(which yt-dlp 2>/dev/null || echo 'NOT FOUND')"
echo "ffmpeg location: $(which ffmpeg 2>/dev/null || echo 'NOT FOUND')"
echo ""

# Check dependencies
MISSING_DEPS=0
if ! command -v yt-dlp &> /dev/null; then
    echo "❌ yt-dlp not found. Please install with: pip install -r requirements.txt"
    MISSING_DEPS=1
fi

if ! command -v ffmpeg &> /dev/null; then
    echo "❌ ffmpeg not found. Please install ffmpeg system package."
    echo "  Fedora/RHEL: sudo dnf install ffmpeg"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg" 
    echo "  macOS: brew install ffmpeg"
    MISSING_DEPS=1
fi

if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    echo "Please install missing dependencies before continuing."
    exit 1
fi

echo "✅ All dependencies available!"

echo ""
echo "Available options:"
echo "1) Launch GUI: python y2wav.py --gui"
echo "2) Download from command line: python y2wav.py [URL or file]"
echo "3) Show config: python y2wav.py --show-config"
echo ""
echo "Example usage:"
echo "  python y2wav.py --gui"
echo "  python y2wav.py 'https://youtube.com/watch?v=...'"
echo "  python y2wav.py urls.txt"
echo ""

# If arguments are provided, run y2wav with them
if [ $# -gt 0 ]; then
    echo "Running: python y2wav.py $*"
    python y2wav.py "$@"
else
    echo "To launch the GUI, run: python y2wav.py --gui"
fi