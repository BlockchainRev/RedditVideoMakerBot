#!/usr/bin/env python3
"""
Dream Tales Video Creator - Quick Launcher
Easy way to run the dream video creator with different options
"""

import os
import sys
from pathlib import Path

def print_banner():
    print("""
    🌙 Dream Tales Video Creator 🌙
    ===============================
    
    Transform Reddit dream stories into engaging videos!
    """)

def check_config():
    """Check if configuration is set up"""
    if not os.path.exists("config.toml"):
        print("❌ No configuration file found!")
        print("Please run 'python setup_dream.py' first to set up the tool.")
        return False
    
    # Check if credentials are configured
    with open("config.toml", "r") as f:
        content = f.read()
        if "YOUR_CLIENT_ID_HERE" in content:
            print("⚠️  Reddit credentials not configured!")
            print("Edit config.toml or run 'python setup_dream.py' to set them up.")
            return False
    
    return True

def run_setup():
    """Run the setup script"""
    print("🔧 Running setup...")
    os.system("python setup_dream.py")

def run_main():
    """Run the main dream video creator"""
    print("🎬 Starting dream video creation...")
    os.system("python main.py")

def show_help():
    """Show help information"""
    print("""
    📖 Dream Tales Video Creator Help
    =================================
    
    Quick Commands:
    - python run_dream.py           # Run this launcher
    - python setup_dream.py         # Set up configuration
    - python main.py                # Run video creator directly
    
    Key Features:
    - Extracts dream stories from Reddit
    - Creates beautiful text-based visuals
    - Auto-generates narrated videos
    - Perfect for marketing dream-related content
    
    Popular Dream Subreddits:
    - r/Dreams - General dream sharing
    - r/DreamAnalysis - Dream interpretation
    - r/LucidDreaming - Conscious dreaming
    - r/DreamInterpretation - Symbolic meanings
    
    For detailed documentation, see README_DREAM.md
    """)

def main():
    print_banner()
    
    while True:
        print("\nWhat would you like to do?")
        print("1. 🎬 Create dream video")
        print("2. 🔧 Setup/configure")
        print("3. 📖 Help")
        print("4. 🚪 Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            if check_config():
                run_main()
                break
            else:
                print("\nPlease set up the configuration first.")
                continue
                
        elif choice == "2":
            run_setup()
            
        elif choice == "3":
            show_help()
            
        elif choice == "4":
            print("Happy dream video creating! 🌙✨")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main() 