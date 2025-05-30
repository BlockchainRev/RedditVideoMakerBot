#!/usr/bin/env python3
"""
Test script to verify Dream Tales Video Creator setup
"""

import sys

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import praw
        print("✅ praw (Reddit API)")
    except ImportError as e:
        print(f"❌ praw: {e}")
        return False
    
    try:
        import prawcore
        print("✅ prawcore")
    except ImportError as e:
        print(f"❌ prawcore: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow (Image processing)")
    except ImportError as e:
        print(f"❌ Pillow: {e}")
        return False
    
    try:
        import moviepy
        print("✅ moviepy (Video creation)")
    except ImportError as e:
        print(f"❌ moviepy: {e}")
        return False
    
    try:
        from gtts import gTTS
        print("✅ gTTS (Text-to-speech)")
    except ImportError as e:
        print(f"❌ gTTS: {e}")
        return False
    
    try:
        import rich
        print("✅ rich (Console output)")
    except ImportError as e:
        print(f"❌ rich: {e}")
        return False
    
    try:
        import requests
        print("✅ requests")
    except ImportError as e:
        print(f"❌ requests: {e}")
        return False
    
    try:
        import toml
        print("✅ toml")
    except ImportError as e:
        print(f"❌ toml: {e}")
        return False
    
    return True

def test_reddit_connection():
    """Test Reddit API connection"""
    print("\n🔗 Testing Reddit connection...")
    
    try:
        import praw
        from utils import settings
        
        # Load config
        config = settings.check_toml("utils/.config.template.toml", "config.toml")
        if not config:
            print("❌ Could not load configuration")
            return False
        
        # Test Reddit connection
        reddit = praw.Reddit(
            client_id=settings.config["reddit"]["creds"]["client_id"],
            client_secret=settings.config["reddit"]["creds"]["client_secret"],
            user_agent="Dream Tales Video Creator - Test",
            username=settings.config["reddit"]["creds"]["username"],
            password=settings.config["reddit"]["creds"]["password"],
            check_for_async=False,
        )
        
        # Test by trying to access a subreddit
        subreddit = reddit.subreddit("Dreams")
        subreddit.title  # This will trigger the connection
        
        print("✅ Reddit API connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Reddit connection failed: {e}")
        return False

def test_dream_modules():
    """Test our custom dream modules"""
    print("\n🌙 Testing dream-specific modules...")
    
    try:
        from video_creation.text_image_generator import generate_dream_images
        print("✅ Dream text image generator")
    except ImportError as e:
        print(f"❌ Dream text generator: {e}")
        return False
    
    try:
        from reddit.subreddit import get_subreddit_threads
        print("✅ Dream subreddit fetcher")
    except ImportError as e:
        print(f"❌ Dream subreddit fetcher: {e}")
        return False
    
    return True

def main():
    print("🌙 Dream Tales Video Creator - Setup Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Some imports failed. Please install missing dependencies.")
        return False
    
    # Test custom modules
    if not test_dream_modules():
        print("\n❌ Dream-specific modules failed to load.")
        return False
    
    # Test Reddit connection
    if not test_reddit_connection():
        print("\n⚠️  Reddit connection failed. Please check your credentials in config.toml")
        print("   You can still use the tool, but you'll need to fix the credentials.")
    
    print("\n🎉 Setup test completed!")
    print("✨ Your Dream Tales Video Creator is ready to use!")
    print("\nNext steps:")
    print("1. Run: python main.py")
    print("2. Or use the launcher: python run_dream.py")
    
    return True

if __name__ == "__main__":
    main() 