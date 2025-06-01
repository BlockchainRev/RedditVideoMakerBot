# Reddit Video Maker Bot 🎥

All done WITHOUT video editing or asset compiling. Just pure ✨programming magic✨.

Created by Lewis Menelaws & [TMRRW](https://tmrrwinc.ca)

<a target="_blank" href="https://tmrrwinc.ca">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://user-images.githubusercontent.com/6053155/170528535-e274dc0b-7972-4b27-af22-637f8c370133.png">
  <source media="(prefers-color-scheme: light)" srcset="https://user-images.githubusercontent.com/6053155/170528582-cb6671e7-5a2f-4bd4-a048-0e6cfa54f0f7.png">
  <img src="https://user-images.githubusercontent.com/6053155/170528582-cb6671e7-5a2f-4bd4-a048-0e6cfa54f0f7.png" width="350">
</picture>

</a>

## Video Explainer

[![lewisthumbnail](https://user-images.githubusercontent.com/6053155/173631669-1d1b14ad-c478-4010-b57d-d79592a789f2.png)
](https://www.youtube.com/watch?v=3gjcY_00U1w)

## Motivation 🤔

These videos on TikTok, YouTube and Instagram get MILLIONS of views across all platforms and require very little effort.
The only original thing being done is the editing and gathering of all materials...

... but what if we can automate that process? 🤔

## Disclaimers 🚨

- **At the moment**, this repository won't attempt to upload this content through this bot. It will give you a file that
  you will then have to upload manually. This is for the sake of avoiding any sort of community guideline issues.

## Requirements

- Python 3.10
- Playwright (this should install automatically in installation)

## TTS Options 🎙️

This bot supports multiple Text-to-Speech engines:

### Chatterbox TTS (Recommended) 🆕
- **Local, open-source TTS** - No API keys required!
- **High-quality voice synthesis** - Outperforms ElevenLabs in side-by-side tests
- **Voice cloning support** - Use custom voice files for unique narration
- **Emotion control** - Adjust exaggeration and pacing for different content styles
- **GPU acceleration** - Fast generation with CUDA support

**Quick Setup:**
```bash
python install_chatterbox.py
```

**Configuration:**
```toml
[settings.tts]
voice_choice = "chatterbox"
chatterbox_voice = "default"  # or "female", "male", "neutral", or custom voice name
chatterbox_exaggeration = 0.5  # 0.0-1.0, higher = more expressive
chatterbox_cfg_weight = 0.5    # 0.0-1.0, lower = slower/more deliberate
```

### Other TTS Options
- **ElevenLabs** - High quality but requires API key and costs money
- **TikTok TTS** - Free but requires session ID
- **AWS Polly** - Requires AWS credentials
- **Google Translate** - Free but basic quality
- **pyttsx3** - Local system voices

## Installation 👩‍💻

1. Clone this repository
2. Run `pip install -r requirements.txt`
3. Run `python -m playwright install` and `python -m playwright install-deps`

**EXPERIMENTAL!!!!**

On macOS and Linux (debian, arch, fedora and centos, and based on those), you can run an install script that will automatically install steps 1 to 3. (requires bash)

`bash <(curl -sL https://raw.githubusercontent.com/elebumm/RedditVideoMakerBot/master/install.sh)`

This can also be used to update the installation

4. **For Chatterbox TTS (recommended):** Run `python install_chatterbox.py`
5. Run `python main.py`
6. Visit [the Reddit Apps page.](https://www.reddit.com/prefs/apps), and set up an app that is a "script". Paste any URL in redirect URL. Ex:`https://jasoncameron.dev`
7. The bot will ask you to fill in your details to connect to the Reddit API, and configure the bot to your liking
8. Enjoy 😎
9. If you need to reconfigure the bot, simply open the `config.toml` file and delete the lines that need to be changed. On the next run of the bot, it will help you reconfigure those options.

(Note if you got an error installing or running the bot try first rerunning the command with a three after the name e.g. python3 or pip3)

If you want to read more detailed guide about the bot, please refer to the [documentation](https://reddit-video-maker-bot.netlify.app/)

## Custom Voice Cloning with Chatterbox 🎭

Want to use your own voice or a specific character voice? Chatterbox TTS supports voice cloning!

1. **Prepare voice samples**: Record 3-10 seconds of clear, high-quality speech
2. **Add to voices folder**: Place your audio files (`.wav`, `.mp3`, `.flac`, `.m4a`) in `assets/voices/`
3. **Configure**: Set `chatterbox_voice` to your filename (without extension)
4. **Optimize settings**: 
   - For dramatic content: `exaggeration = 0.7`, `cfg_weight = 0.3`
   - For calm narration: `exaggeration = 0.5`, `cfg_weight = 0.5`

See `assets/voices/README.md` for detailed instructions.

## Video

https://user-images.githubusercontent.com/66544866/173453972-6526e4e6-c6ef-41c5-ab40-5d275e724e7c.mp4

## Contributing & Ways to improve 📈

In its current state, this bot does exactly what it needs to do. However, improvements can always be made!

I have tried to simplify the code so anyone can read it and start contributing at any skill level. Don't be shy :) contribute!

- [ ] Creating better documentation and adding a command line interface.
- [x] Allowing the user to choose background music for their videos.
- [x] Allowing users to choose a reddit thread instead of being randomized.
- [x] Allowing users to choose a background that is picked instead of the Minecraft one.
- [x] Allowing users to choose between any subreddit.
- [x] Allowing users to change voice.
- [x] Checks if a video has already been created
- [x] Light and Dark modes
- [x] NSFW post filter

Please read our [contributing guidelines](CONTRIBUTING.md) for more detailed information.

### For any questions or support join the [Discord](https://discord.gg/qfQSx45xCV) server

## Developers and maintainers.

Elebumm (Lewis#6305) - https://github.com/elebumm (Founder)

Jason Cameron - https://github.com/JasonLovesDoggo (Maintainer)

Simon (OpenSourceSimon) - https://github.com/OpenSourceSimon

CallumIO (c.#6837) - https://github.com/CallumIO

Verq (Verq#2338) - https://github.com/CordlessCoder

LukaHietala (Pix.#0001) - https://github.com/LukaHietala

Freebiell (Freebie#3263) - https://github.com/FreebieII

Aman Raza (electro199#8130) - https://github.com/electro199

Cyteon (cyteon) - https://github.com/cyteon


## LICENSE
[Roboto Fonts](https://fonts.google.com/specimen/Roboto/about) are licensed under [Apache License V2](https://www.apache.org/licenses/LICENSE-2.0)
