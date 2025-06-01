#!/usr/bin/env python3
"""
Test script for Chatterbox TTS integration
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

def test_import():
    """Test if Chatterbox TTS module can be imported"""
    print("🔍 Running Import Test...")
    try:
        from TTS.chatterbox import ChatterboxTTSEngine
        print("✅ Chatterbox TTS module imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import Chatterbox TTS module: {e}")
        return False

def test_initialization():
    """Test if Chatterbox TTS can be initialized"""
    print("\n🔍 Running Initialization Test...")
    try:
        from TTS.chatterbox import ChatterboxTTSEngine
        
        # Initialize the TTS engine
        tts = ChatterboxTTSEngine()
        
        print("✅ Chatterbox TTS class initialized successfully")
        print(f"   Device: {tts.device}")
        print(f"   Max chars: {tts.max_chars}")
        print(f"   Available voices: {tts.available_voices}")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Chatterbox TTS: {e}")
        return False

def test_model_loading():
    """Test if Chatterbox TTS model can be loaded"""
    print("\n🔍 Running Model Loading Test...")
    try:
        from TTS.chatterbox import ChatterboxTTSEngine
        
        # Initialize and load model
        tts = ChatterboxTTSEngine()
        tts.initialize()
        
        print("✅ Chatterbox TTS model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to load Chatterbox TTS model: {e}")
        print("   This might be expected if chatterbox-tts is not installed")
        return False

def test_audio_generation():
    """Test if Chatterbox TTS can generate audio"""
    print("\n🔍 Running Audio Generation Test...")
    try:
        from TTS.chatterbox import ChatterboxTTSEngine
        
        # Initialize TTS
        tts = ChatterboxTTSEngine()
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            # Generate audio
            test_text = "Hello, this is a test of Chatterbox TTS."
            tts.run(
                text=test_text,
                filepath=output_path,
                voice="default",
                exaggeration=0.5,
                cfg_weight=0.5
            )
            
            # Check if file was created
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print("✅ Audio generated successfully")
                print(f"   Output file: {output_path}")
                print(f"   File size: {os.path.getsize(output_path)} bytes")
                return True
            else:
                print("❌ Audio file was not created or is empty")
                return False
                
        finally:
            # Clean up temporary file
            if os.path.exists(output_path):
                os.unlink(output_path)
                
    except Exception as e:
        print(f"❌ Failed to generate audio with Chatterbox TTS: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Chatterbox TTS Integration")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Import Test", test_import),
        ("Initialization Test", test_initialization),
        ("Model Loading Test", test_model_loading),
        ("Audio Generation Test", test_audio_generation),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Chatterbox TTS is working correctly.")
    elif passed >= len(tests) // 2:
        print("⚠️  Basic functionality works. Some advanced features may need setup.")
    else:
        print("🚨 Major issues detected. Please check installation and dependencies.")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 