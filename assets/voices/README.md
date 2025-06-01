# Custom Voice Files for Chatterbox TTS

This directory is where you can place custom voice files to use with Chatterbox TTS for voice cloning.

## Supported Formats

Chatterbox TTS supports the following audio formats for voice prompts:
- `.wav` (recommended)
- `.mp3`
- `.flac`
- `.m4a`

## How to Use Custom Voices

1. **Add voice files**: Place your audio files in this directory (`assets/voices/`)
2. **Configure**: Set the `chatterbox_voice` setting in your config to the filename (without extension)
3. **Example**: If you have `female_narrator.wav`, set `chatterbox_voice = "female_narrator"`

## Voice File Requirements

For best results, your voice files should:
- Be 3-10 seconds long
- Contain clear, high-quality speech
- Have minimal background noise
- Be in a supported audio format
- Represent the voice you want to clone

## Default Voices

If no custom voice files are found, Chatterbox will use these built-in options:
- `default` - Chatterbox's default voice
- `female` - Built-in female voice option
- `male` - Built-in male voice option  
- `neutral` - Built-in neutral voice option

## Configuration Examples

In your `config.toml`:

```toml
[settings.tts]
voice_choice = "chatterbox"
chatterbox_voice = "default"  # or "female", "male", "neutral", or your custom voice name
chatterbox_exaggeration = 0.5  # 0.0-1.0, higher = more expressive
chatterbox_cfg_weight = 0.5    # 0.0-1.0, lower = slower/more deliberate
```

## Tips for Voice Cloning

- Use high-quality recordings for better results
- Consistent audio quality across files works best
- Test different `exaggeration` and `cfg_weight` values for your voice
- For dramatic content, try higher `exaggeration` (0.7+) and lower `cfg_weight` (0.3)
- For calm narration, use moderate settings (both around 0.5) 