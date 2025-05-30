#!/usr/bin/env python3
"""
Dream Tales Video Creator - Setup Script
Helps you quickly configure the tool for dream content creation
"""

import os
import shutil
from pathlib import Path

def print_banner():
    print("""
    🌙 Dream Tales Video Creator Setup 🌙
    =====================================
    
    Welcome! This script will help you set up the Dream Tales Video Creator
    for making engaging dream journal videos from Reddit content.
    """)

def setup_config():
    """Set up the configuration file"""
    print("\n📋 Setting up configuration...")
    
    # Copy the dream config template
    if os.path.exists("config.dream.toml"):
        if not os.path.exists("config.toml"):
            shutil.copy("config.dream.toml", "config.toml")
            print("✅ Copied dream configuration template to config.toml")
        else:
            overwrite = input("config.toml already exists. Overwrite with dream template? (y/n): ")
            if overwrite.lower().startswith('y'):
                shutil.copy("config.dream.toml", "config.toml")
                print("✅ Overwrote config.toml with dream template")
    else:
        print("❌ config.dream.toml not found. Please ensure you have the complete project files.")
        return False
    
    return True

def get_reddit_credentials():
    """Interactive Reddit credentials setup"""
    print("\n🔑 Reddit API Setup")
    print("=" * 50)
    print("To use this tool, you need Reddit API credentials.")
    print("1. Go to: https://www.reddit.com/prefs/apps")
    print("2. Click 'Create App' or 'Create Another App'")
    print("3. Choose 'script' as the app type")
    print("4. Copy the credentials below")
    print()
    
    setup_reddit = input("Do you want to set up Reddit credentials now? (y/n): ")
    if not setup_reddit.lower().startswith('y'):
        print("⚠️  You can set up Reddit credentials later by editing config.toml")
        return
    
    print("\nEnter your Reddit app credentials:")
    client_id = input("Client ID (from under the app name): ").strip()
    client_secret = input("Client Secret: ").strip()
    username = input("Reddit Username: ").strip()
    password = input("Reddit Password: ").strip()
    
    if not all([client_id, client_secret, username, password]):
        print("❌ Missing credentials. You can add them later in config.toml")
        return
    
    # Update the config file
    try:
        with open("config.toml", "r") as f:
            config_content = f.read()
        
        config_content = config_content.replace('client_id = "YOUR_CLIENT_ID_HERE"', f'client_id = "{client_id}"')
        config_content = config_content.replace('client_secret = "YOUR_CLIENT_SECRET_HERE"', f'client_secret = "{client_secret}"')
        config_content = config_content.replace('username = "YOUR_REDDIT_USERNAME"', f'username = "{username}"')
        config_content = config_content.replace('password = "YOUR_REDDIT_PASSWORD"', f'password = "{password}"')
        
        with open("config.toml", "w") as f:
            f.write(config_content)
        
        print("✅ Reddit credentials saved to config.toml")
        
    except Exception as e:
        print(f"❌ Error updating config file: {e}")
        print("Please manually edit config.toml with your credentials")

def customize_settings():
    """Customize dream-specific settings"""
    print("\n🎨 Customization Options")
    print("=" * 50)
    
    # Subreddit selection
    print("Popular dream subreddits:")
    subreddits = [
        "Dreams - General dream sharing",
        "DreamAnalysis - Dream interpretation", 
        "LucidDreaming - Conscious dreaming",
        "DreamInterpretation - Symbolic meanings",
        "Nightmares - Scary dreams",
        "DreamJournal - Personal dream logs"
    ]
    
    for i, sub in enumerate(subreddits, 1):
        print(f"  {i}. {sub}")
    
    print("\nCurrent setting: Dreams+DreamAnalysis+LucidDreaming")
    change_subs = input("Want to customize subreddits? (y/n): ")
    
    if change_subs.lower().startswith('y'):
        custom_subs = input("Enter subreddits (separated by +): ").strip()
        if custom_subs:
            try:
                with open("config.toml", "r") as f:
                    config_content = f.read()
                
                config_content = config_content.replace(
                    'subreddit = "Dreams+DreamAnalysis+LucidDreaming"',
                    f'subreddit = "{custom_subs}"'
                )
                
                with open("config.toml", "w") as f:
                    f.write(config_content)
                
                print(f"✅ Updated subreddits to: {custom_subs}")
            except Exception as e:
                print(f"❌ Error updating subreddits: {e}")
    
    # Theme selection
    print("\nTheme options:")
    print("  1. dark - Mystical, night-time feel (recommended)")
    print("  2. light - Clean, minimalist")  
    print("  3. transparent - Overlay on background")
    
    theme_choice = input("Choose theme (1-3, or press Enter for dark): ").strip()
    theme_map = {"1": "dark", "2": "light", "3": "transparent"}
    
    if theme_choice in theme_map:
        try:
            with open("config.toml", "r") as f:
                config_content = f.read()
            
            config_content = config_content.replace(
                'theme = "dark"',
                f'theme = "{theme_map[theme_choice]}"'
            )
            
            with open("config.toml", "w") as f:
                f.write(config_content)
            
            print(f"✅ Updated theme to: {theme_map[theme_choice]}")
        except Exception as e:
            print(f"❌ Error updating theme: {e}")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n📦 Checking Dependencies")
    print("=" * 50)
    
    try:
        import praw
        print("✅ praw (Reddit API) - installed")
    except ImportError:
        print("❌ praw (Reddit API) - not installed")
        print("   Run: pip install praw")
    
    try:
        from PIL import Image
        print("✅ Pillow (Image processing) - installed")
    except ImportError:
        print("❌ Pillow (Image processing) - not installed")
        print("   Run: pip install Pillow")
    
    try:
        import moviepy
        print("✅ moviepy (Video creation) - installed")
    except ImportError:
        print("❌ moviepy (Video creation) - not installed")
        print("   Run: pip install moviepy")
    
    try:
        import rich
        print("✅ rich (Console output) - installed")
    except ImportError:
        print("❌ rich (Console output) - not installed")
        print("   Run: pip install rich")
    
    print("\nTo install all dependencies at once:")
    print("pip install -r requirements.txt")

def main():
    print_banner()
    
    # Setup configuration
    if not setup_config():
        return
    
    # Reddit credentials
    get_reddit_credentials()
    
    # Customization
    customize_settings()
    
    # Check dependencies
    check_dependencies()
    
    print("\n🎉 Setup Complete!")
    print("=" * 50)
    print("Next steps:")
    print("1. Install any missing dependencies: pip install -r requirements.txt")
    print("2. Run the dream video creator: python main.py")
    print("3. Check README_DREAM.md for detailed documentation")
    print("\nHappy dream video creating! 🌙✨")

if __name__ == "__main__":
    main() 