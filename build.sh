#!/bin/bash
echo "🚀 Starting AI Assistant Build Process..."
echo "========================================"

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Install PyTorch separately for stability
echo "⚡ Installing PyTorch..."
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Download NLTK data
echo "📚 Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)"

echo "✅ Build completed successfully!"
echo "========================================"
