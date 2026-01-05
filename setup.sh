#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════╗"
echo "║    AI Assistant Setup Script         ║"
echo "║    For Termux & Local Development    ║"
echo "╚══════════════════════════════════════╝"
echo -e "${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if running in Termux
if [[ -d "/data/data/com.termux/files/usr" ]]; then
    echo -e "${GREEN}✓ Running in Termux${NC}"
    IS_TERMUX=true
else
    echo -e "${YELLOW}⚠ Running on regular Linux/Mac${NC}"
    IS_TERMUX=false
fi

# Update and install system packages
echo -e "\n${BLUE}[1/6] Updating system packages...${NC}"
if [ "$IS_TERMUX" = true ]; then
    pkg update -y && pkg upgrade -y
    echo -e "${GREEN}✓ Termux updated${NC}"
else
    if command_exists apt; then
        sudo apt update && sudo apt upgrade -y
    elif command_exists yum; then
        sudo yum update -y
    elif command_exists brew; then
        brew update
    fi
    echo -e "${GREEN}✓ System updated${NC}"
fi

# Install Python and git
echo -e "\n${BLUE}[2/6] Installing Python and Git...${NC}"
if [ "$IS_TERMUX" = true ]; then
    pkg install python -y
    pkg install git -y
    pkg install wget -y
    pkg install termux-api -y
else
    if command_exists apt; then
        sudo apt install python3 python3-pip git wget -y
    elif command_exists yum; then
        sudo yum install python3 python3-pip git wget -y
    elif command_exists brew; then
        brew install python git wget
    fi
fi
echo -e "${GREEN}✓ Python & Git installed${NC}"

# Upgrade pip
echo -e "\n${BLUE}[3/6] Setting up Python environment...${NC}"
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✓ Pip upgraded${NC}"

# Install Python requirements
echo -e "\n${BLUE}[4/6] Installing Python packages...${NC}"
if [ -f "requirements.txt" ]; then
    echo "Installing from requirements.txt..."
    pip install -r requirements.txt
else
    echo -e "${YELLOW}⚠ requirements.txt not found, installing basic packages...${NC}"
    pip install flask flask-cors gunicorn requests
fi

# Install PyTorch for Termux
if [ "$IS_TERMUX" = true ]; then
    echo -e "\n${BLUE}[5/6] Installing PyTorch for Termux...${NC}"
    pip install torch --index-url https://download.pytorch.org/whl/cpu
    echo -e "${GREEN}✓ PyTorch installed${NC}"
fi

# Download NLTK data
echo -e "\n${BLUE}[6/6] Setting up NLTK data...${NC}"
python3 -c "
import nltk
import os

print('Downloading NLTK data...')
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
print('NLTK setup complete!')
"

# Make scripts executable
chmod +x build.sh 2>/dev/null || true
chmod +x setup.sh 2>/dev/null || true

# Display completion message
echo -e "\n${GREEN}"
echo "╔══════════════════════════════════════╗"
echo "║       SETUP COMPLETED!              ║"
echo "╚══════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}📦 Installed Packages:${NC}"
echo "• Flask Web Framework"
echo "• AI/ML Libraries"
echo "• Production Server (Gunicorn)"
echo "• NLTK for Natural Language"

echo -e "\n${YELLOW}🚀 To start the application:${NC}"
echo "1. Run: ${GREEN}python app.py${NC}"
echo "2. Open browser: ${GREEN}http://localhost:5000${NC}"

echo -e "\n${YELLOW}🔧 Additional Commands:${NC}"
echo "• Test API: ${GREEN}curl http://localhost:5000/api/status${NC}"
echo "• Install dev tools: ${GREEN}pkg install nano vim${NC}"

if [ "$IS_TERMUX" = true ]; then
    echo -e "\n${YELLOW}📱 Termux Tips:${NC}"
    echo "• Keep screen on: ${GREEN}termux-wake-lock${NC}"
    echo "• Allow storage: ${GREEN}termux-setup-storage${NC}"
    echo "• Run in background: ${GREEN}tmux${NC}"
fi

echo -e "\n${BLUE}Need help? Check README.md for more details.${NC}"
