#!/bin/bash
# Setup script for FOMC Sentiment Analysis project

echo "=========================================="
echo "FOMC Sentiment Analysis - Setup"
echo "=========================================="

# Check Python version
echo ""
echo "[1/4] Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo ""
echo "[2/4] Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

echo "✓ Virtual environment created"

# Activate virtual environment
echo ""
echo "[3/4] Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo ""
echo "[4/4] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"

# Download NLTK data
echo ""
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run the quick start example:"
echo "  python example.py"
echo ""
echo "To run the full analysis:"
echo "  python src/main.py"
echo ""
echo "To launch Jupyter notebook:"
echo "  jupyter notebook notebooks/analysis.ipynb"
echo ""
