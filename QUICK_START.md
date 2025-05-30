# 🌙 Quick Start Guide - Dream Video Creator

*For when you just need the essentials*

## 🚀 Installation & Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup configuration (first time only)
python setup_dream.py

# 3. Create videos
python run_dream.py
```

## 🎬 Creating Videos

### Easy Way (Recommended)
```bash
python run_dream.py
```
Choose option 1 from the menu.

### Direct Way
```bash
python main.py
```

## ⚙️ Quick Configuration

### Reddit Credentials (config.toml)
```toml
[reddit.creds]
client_id = "your_client_id"
client_secret = "your_client_secret"
username = "your_username"
password = "your_password"
```

### Popular Settings
```toml
# Subreddits (mix and match)
subreddit = "Dreams+LucidDreaming+DreamAnalysis"

# Theme
theme = "dark"  # or "light", "transparent"

# Number of videos to create
times_to_run = 1

# Story length
storymode_max_length = 2000
```

## 🎨 Common Customizations

### Change Subreddits
```toml
subreddit = "Dreams"  # Single subreddit
subreddit = "Dreams+Nightmares+LucidDreaming"  # Multiple
```

### Voice Options
```toml
voice_choice = "tiktok"  # Free, good quality
tiktok_voice = "en_us_001"  # Different voices available
```

### Background
```toml
background_video = "minecraft"  # or "motor-gta", "csgo-surf"
background_audio = "lofi"  # Relaxing for dream content
```

## 📁 Output Location
Videos are saved in: `results/final_video.mp4`

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Missing packages | `pip install -r requirements.txt` |
| Reddit login fails | Run `python setup_dream.py` |
| No FFmpeg | Mac: `brew install ffmpeg`<br>Windows: Download from ffmpeg.org |
| No content found | Try different subreddits or times |
| Video creation fails | Check `results/` folder for error files |

## 🎯 Pro Tips

- **First run takes longer** (downloads background videos)
- **Best content**: Evening hours US time
- **Multiple videos**: Change `times_to_run` in config
- **Check output**: Look at `results/` folder images
- **Experiment**: Try different subreddit combinations

## 📚 More Help
- **Detailed guide**: `README_BEGINNER.md`
- **Technical docs**: `README_DREAM.md`
- **Reconfigure**: `python setup_dream.py` 