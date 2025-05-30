import random

from elevenlabs import save
from elevenlabs.client import ElevenLabs

from utils import settings


class elevenlabs:
    def __init__(self):
        self.max_chars = 2500
        self.client: ElevenLabs = None

    def run(self, text, filepath, random_voice: bool = False):
        if self.client is None:
            self.initialize()
        if random_voice:
            voice_id = self.randomvoice()
        else:
            # Use the voice name from config to find the voice ID, or use a default
            voice_name = str(settings.config["settings"]["tts"]["elevenlabs_voice_name"]).capitalize()
            voice_id = self.get_voice_id_by_name(voice_name)

        # Updated for ElevenLabs 2.1.0 API
        audio = self.client.text_to_speech.convert(
            text=text, 
            voice_id=voice_id, 
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        
        # Save the audio to file
        with open(filepath, "wb") as f:
            for chunk in audio:
                if isinstance(chunk, bytes):
                    f.write(chunk)

    def get_voice_id_by_name(self, voice_name):
        """Get voice ID by name, fallback to default voice if not found"""
        try:
            voices = self.client.voices.get_all()
            for voice in voices.voices:
                if voice.name.lower() == voice_name.lower():
                    return voice.voice_id
            # If voice not found, use the first available voice
            if voices.voices:
                return voices.voices[0].voice_id
            # Fallback to a known default voice ID (Rachel - a popular ElevenLabs voice)
            return "21m00Tcm4TlvDq8ikWAM"
        except Exception:
            # Ultimate fallback
            return "21m00Tcm4TlvDq8ikWAM"

    def initialize(self):
        if settings.config["settings"]["tts"]["elevenlabs_api_key"]:
            api_key = settings.config["settings"]["tts"]["elevenlabs_api_key"]
        else:
            raise ValueError(
                "You didn't set an Elevenlabs API key! Please set the config variable ELEVENLABS_API_KEY to a valid API key."
            )

        self.client = ElevenLabs(api_key=api_key)

    def randomvoice(self):
        if self.client is None:
            self.initialize()
        try:
            voices = self.client.voices.get_all()
            return random.choice(voices.voices).voice_id
        except Exception:
            # Fallback to default voice
            return "21m00Tcm4TlvDq8ikWAM"
