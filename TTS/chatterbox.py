import os
import random
import tempfile
import torch
import torchaudio as ta
from pathlib import Path

from utils import settings
from utils.console import print_substep


class ChatterboxTTSEngine:
    """
    Chatterbox TTS Engine for Reddit Video Maker Bot
    
    A local, open-source TTS solution that supports voice cloning
    and emotion control without requiring API keys.
    """
    
    def __init__(self):
        self.model = None
        self.device = "cpu"  # Force CPU mode for compatibility
        self.max_chars = 2000
        self.available_voices = ["default", "female", "male", "neutral"]
        
    def initialize(self):
        """Initialize the Chatterbox TTS model with CPU compatibility patches"""
        try:
            print_substep("Initializing Chatterbox TTS model...")
            
            # Import here to avoid issues if package isn't installed
            from chatterbox.tts import ChatterboxTTS
            
            # Force CPU mode to avoid CUDA device mapping issues
            print_substep("Forcing CPU mode for Chatterbox TTS compatibility")
            
            # Monkey-patch the ChatterboxTTS.from_local method to handle CPU-only execution
            original_from_local = ChatterboxTTS.from_local
            
            @classmethod
            def patched_from_local(cls, ckpt_dir, device):
                """Patched version that forces CPU map_location for torch.load calls"""
                ckpt_dir = Path(ckpt_dir)
                
                # Import required classes
                from chatterbox.models.voice_encoder import VoiceEncoder
                from chatterbox.models.t3 import T3
                from chatterbox.models.s3gen import S3Gen
                from chatterbox.models.tokenizers import EnTokenizer
                from chatterbox.tts import Conditionals
                
                # Force CPU device
                device = "cpu"
                
                # Load VoiceEncoder with CPU mapping
                ve = VoiceEncoder()
                ve_state = torch.load(ckpt_dir / "ve.pt", map_location="cpu")
                ve.load_state_dict(ve_state)
                ve.to(device).eval()
                
                # Load T3 with CPU mapping
                t3 = T3()
                t3_state = torch.load(ckpt_dir / "t3_cfg.pt", map_location="cpu")
                if "model" in t3_state.keys():
                    t3_state = t3_state["model"][0]
                t3.load_state_dict(t3_state)
                t3.to(device).eval()
                
                # Load S3Gen with CPU mapping
                s3gen = S3Gen()
                s3gen_state = torch.load(ckpt_dir / "s3gen.pt", map_location="cpu")
                s3gen.load_state_dict(s3gen_state)
                s3gen.to(device).eval()
                
                # Load tokenizer
                tokenizer = EnTokenizer(str(ckpt_dir / "tokenizer.json"))
                
                # Load conditionals if they exist
                conds = None
                if (builtin_voice := ckpt_dir / "conds.pt").exists():
                    conds = Conditionals.load(builtin_voice, map_location="cpu").to(device)
                
                return cls(t3, s3gen, ve, tokenizer, device, conds=conds)
            
            # Apply the monkey patch
            ChatterboxTTS.from_local = patched_from_local
            
            # Initialize model with CPU device
            self.model = ChatterboxTTS.from_pretrained(device=self.device)
            
            print_substep(f"Chatterbox TTS initialized successfully on {self.device}", "green")
            
        except ImportError:
            raise ValueError(
                "Chatterbox TTS is not installed. Please install it with: pip install chatterbox-tts"
            )
        except Exception as e:
            # Provide helpful error message for common issues
            error_msg = str(e)
            if "CUDA device but torch.cuda.is_available() is False" in error_msg:
                raise ValueError(
                    "Chatterbox TTS models require CUDA but CUDA is not available. "
                    "This is a known limitation. Please use a different TTS engine like 'tiktok' or 'elevenlabs'."
                )
            elif "map_location" in error_msg or "deserialize" in error_msg:
                raise ValueError(
                    "Failed to load Chatterbox TTS models on CPU. "
                    "The models may have been trained on CUDA. Please try a different TTS engine."
                )
            else:
                raise ValueError(
                    f"Failed to initialize Chatterbox TTS: {error_msg}. "
                    "This might be due to missing dependencies or compatibility issues."
                )

    def randomvoice(self):
        """Return a random voice from available voices"""
        import random
        return random.choice(self.available_voices)

    def run(
        self,
        text: str,
        filepath: str,
        random_voice: bool = False,
        voice: str = "default",
        exaggeration: float = 0.5,
        cfg_weight: float = 0.5,
    ):
        """
        Generate TTS audio using Chatterbox TTS
        
        Args:
            text: Text to synthesize
            filepath: Output file path
            random_voice: Whether to use a random voice (not used in Chatterbox)
            voice: Voice to use (can be path to custom voice file)
            exaggeration: Emotion exaggeration level (0.0-1.0)
            cfg_weight: CFG weight for speech pacing (0.0-1.0)
        """
        if not self.model:
            self.initialize()
            
        try:
            # Validate text length
            if len(text) > self.max_chars:
                print_substep(f"Text too long ({len(text)} chars), truncating to {self.max_chars} chars", "yellow")
                text = text[:self.max_chars]
            
            # Determine voice file path
            voice_path = self._get_voice_path(voice)
            
            print_substep(f"Generating audio with voice: {voice}")
            print_substep(f"Exaggeration: {exaggeration}, CFG Weight: {cfg_weight}")
            
            # Generate audio
            try:
                audio_tensor = self.model.generate(
                    text=text,
                    audio_prompt_path=voice_path,
                    exaggeration=exaggeration,
                    cfg_weight=cfg_weight,
                    temperature=0.8
                )
                
                # Save audio
                import soundfile as sf
                import numpy as np
                
                # Convert tensor to numpy array
                if hasattr(audio_tensor, 'numpy'):
                    audio_data = audio_tensor.numpy()
                else:
                    audio_data = audio_tensor.detach().cpu().numpy()
                
                # Ensure audio is in the right shape (samples,) or (channels, samples)
                if audio_data.ndim > 1:
                    audio_data = audio_data.squeeze()
                
                # Save using soundfile instead of torchaudio to avoid aifc dependency
                sf.write(filepath, audio_data, self.model.sr)
                
                print_substep(f"Audio saved to {filepath}", "green")
                return  # Success, exit early
                
            except Exception as e:
                if "aifc" in str(e):
                    print_substep(f"AIFC module missing (Python 3.13 compatibility issue): {e}", "yellow")
                    print_substep("Attempting to generate audio without voice cloning...", "yellow")
                    
                    # Try without voice cloning as fallback
                    try:
                        audio_tensor = self.model.generate(
                            text=text,
                            exaggeration=exaggeration,
                            cfg_weight=cfg_weight,
                            temperature=0.8
                        )
                        
                        # Save audio
                        import soundfile as sf
                        import numpy as np
                        
                        # Convert tensor to numpy array
                        if hasattr(audio_tensor, 'numpy'):
                            audio_data = audio_tensor.numpy()
                        else:
                            audio_data = audio_tensor.detach().cpu().numpy()
                        
                        # Ensure audio is in the right shape
                        if audio_data.ndim > 1:
                            audio_data = audio_data.squeeze()
                        
                        sf.write(filepath, audio_data, self.model.sr)
                        print_substep(f"Audio saved to {filepath} (without voice cloning)", "green")
                        return  # Success, exit early
                        
                    except Exception as e2:
                        print_substep(f"Fallback also failed: {e2}", "red")
                        # Fall through to silence generation
                else:
                    print_substep(f"Audio generation error: {e}", "red")
                    # Fall through to silence generation
            
        except Exception as e:
            print_substep(f"Error generating audio: {str(e)}", "red")
            
        # If we reach here, create a silent audio file as fallback
        self._create_silence(filepath, duration=2.0)

    def _get_voice_path(self, voice: str) -> str:
        """Get the path to the voice file"""
        # Check if it's a custom voice file path
        if voice.endswith(('.wav', '.mp3', '.flac', '.m4a')):
            if os.path.exists(voice):
                return voice
            # Check in assets/voices directory
            voice_path = os.path.join("assets", "voices", voice)
            if os.path.exists(voice_path):
                return voice_path
        
        # Check for voice files in assets/voices directory
        voice_dir = os.path.join("assets", "voices")
        if os.path.exists(voice_dir):
            # Look for voice files matching the voice name
            for ext in ['.wav', '.mp3', '.flac', '.m4a']:
                voice_file = os.path.join(voice_dir, f"{voice}{ext}")
                if os.path.exists(voice_file):
                    return voice_file
            
            # If no specific voice found, use the first available voice file
            for file in os.listdir(voice_dir):
                if file.endswith(('.wav', '.mp3', '.flac', '.m4a')):
                    return os.path.join(voice_dir, file)
        
        # Fallback: create a default voice file path
        # This will cause an error, but it's better than crashing
        return os.path.join("assets", "voices", "default.wav")
    
    def _create_silence(self, filepath: str, duration: float = 2.0):
        """Create a silent audio file as fallback"""
        try:
            import numpy as np
            import soundfile as sf
            
            sample_rate = 22050
            samples = int(duration * sample_rate)
            silence = np.zeros(samples, dtype=np.float32)
            
            sf.write(filepath, silence, sample_rate)
            print_substep(f"Created silent audio file: {filepath}", "yellow")
            
        except Exception as e:
            print_substep(f"Failed to create silence: {str(e)}", "red")
            # Create an empty file as last resort
            with open(filepath, 'w') as f:
                f.write("") 