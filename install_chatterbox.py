#!/usr/bin/env python3
"""
Installation script for Chatterbox TTS
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("   Chatterbox TTS requires Python 3.8 or higher")
        return False

def check_torch():
    """Check if PyTorch is installed and compatible"""
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__} is installed")
        
        # Check for CUDA availability
        if torch.cuda.is_available():
            print(f"✅ CUDA is available (GPU acceleration enabled)")
            print(f"   CUDA version: {torch.version.cuda}")
            print(f"   GPU device: {torch.cuda.get_device_name(0)}")
        else:
            print("⚠️  CUDA not available (will use CPU)")
        
        return True
    except ImportError:
        print("❌ PyTorch is not installed")
        return False

def install_chatterbox():
    """Install Chatterbox TTS"""
    commands = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip install chatterbox-tts", "Installing Chatterbox TTS"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True

def verify_installation():
    """Verify that Chatterbox TTS is installed correctly"""
    try:
        from chatterbox.tts import ChatterboxTTS
        print("✅ Chatterbox TTS import successful")
        
        # Try to initialize (this will download the model if needed)
        print("🔧 Initializing Chatterbox TTS model (this may take a while on first run)...")
        device = "cuda" if __import__("torch").cuda.is_available() else "cpu"
        model = ChatterboxTTS.from_pretrained(device=device)
        print("✅ Chatterbox TTS model initialized successfully")
        
        return True
    except Exception as e:
        print(f"❌ Chatterbox TTS verification failed: {e}")
        return False

def update_requirements():
    """Update the requirements.txt file if needed"""
    req_file = Path("requirements.txt")
    if req_file.exists():
        with open(req_file, 'r') as f:
            content = f.read()
        
        if "chatterbox-tts" not in content:
            print("🔧 Adding chatterbox-tts to requirements.txt...")
            with open(req_file, 'a') as f:
                f.write("\nchatterbox-tts\n")
            print("✅ Updated requirements.txt")
        else:
            print("✅ chatterbox-tts already in requirements.txt")
    else:
        print("⚠️  requirements.txt not found")

def main():
    """Main installation process"""
    print("🚀 Chatterbox TTS Installation Script")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        print("\n🚨 Installation aborted due to incompatible Python version")
        return False
    
    if not check_torch():
        print("\n⚠️  PyTorch not found. Installing PyTorch first...")
        if not run_command("pip install torch torchaudio", "Installing PyTorch"):
            print("\n🚨 Failed to install PyTorch")
            return False
    
    # Install Chatterbox TTS
    print("\n🔧 Installing Chatterbox TTS...")
    if not install_chatterbox():
        print("\n🚨 Installation failed")
        return False
    
    # Update requirements file
    update_requirements()
    
    # Verify installation
    print("\n🧪 Verifying installation...")
    if not verify_installation():
        print("\n🚨 Installation verification failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Chatterbox TTS installation completed successfully!")
    print("\n📝 Next steps:")
    print("1. Update your config.toml to use Chatterbox:")
    print("   [settings.tts]")
    print("   voice_choice = \"chatterbox\"")
    print("   chatterbox_voice = \"default\"")
    print("   chatterbox_exaggeration = 0.5")
    print("   chatterbox_cfg_weight = 0.5")
    print("\n2. (Optional) Add custom voice files to assets/voices/")
    print("3. Run your Reddit Video Maker Bot as usual")
    print("\n🧪 You can test the installation by running: python test_chatterbox.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 