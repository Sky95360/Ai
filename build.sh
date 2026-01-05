#!/bin/bash
echo "🚀 Starting AI Assistant Build Process..."

# Install basic packages first
pip install --upgrade pip
pip install flask==2.3.3 flask-cors==4.0.0 gunicorn==21.2.0
pip install requests==2.31.0 python-dotenv==1.0.0
pip install numpy==1.24.3 pandas==1.5.3

# Install PyTorch with CPU-only version (compatible with Render)
echo "Installing PyTorch..."
pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cpu

# Install transformers
pip install transformers==4.35.2 sentencepiece==0.1.99 protobuf==3.20.3

echo "✅ Build completed!"
