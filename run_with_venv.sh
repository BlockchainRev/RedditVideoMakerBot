#!/bin/bash

# Dream Tales Video Creator - Virtual Environment Launcher
# This script activates the virtual environment and runs the dream video creator

echo "🌙 Activating Dream Tales Video Creator..."
echo "========================================="

# Check if virtual environment exists
if [ ! -d "dream_venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run the setup first: python3 -m venv dream_venv && source dream_venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment and run the main script
./dream_venv/bin/python main.py 