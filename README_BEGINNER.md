# 🌙 Dream Tales Video Creator - Beginner's Guide

**Never used this before? No problem!** This guide will walk you through everything step-by-step to create amazing dream videos from Reddit stories.

## 🤔 What Is This?

This software automatically creates videos from dream stories posted on Reddit. Here's what it does:

1. **Finds dream stories** from Reddit (like r/Dreams, r/LucidDreaming)
2. **Converts text to beautiful visuals** with mystical styling
3. **Adds computer-generated narration** that reads the story aloud
4. **Creates a complete video** with background music and visuals

Perfect for creating content for social media, YouTube, or just for fun!

## 📱 What You'll Get

After running this software, you'll have:
- A complete video (usually 1-3 minutes long)
- Vertical format perfect for TikTok, YouTube Shorts, Instagram Reels
- Professional narration and background music
- Beautiful text overlays with dream-themed styling

## 🛠️ Step 1: Install Required Software

### Python (Required)
1. **Check if you have Python**: Open Terminal/Command Prompt and type:
   ```bash
   python --version
   ```
   If you see version 3.10 or higher, you're good! If not, continue:

2. **Install Python**:
   - **Mac**: Download from [python.org](https://www.python.org/downloads/) or use Homebrew: `brew install python`
   - **Windows**: Download from [python.org](https://www.python.org/downloads/)
   - **Linux**: Usually pre-installed, or use: `sudo apt install python3`

### Git (To download this software)
1. **Check if you have Git**:
   ```bash
   git --version
   ```
2. **Install Git** if needed from [git-scm.com](https://git-scm.com/downloads)

## 📥 Step 2: Download This Software

1. **Open Terminal/Command Prompt**
2. **Navigate to where you want the software** (like Desktop):
   ```bash
   cd ~/Desktop
   ```
3. **Download the software**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/RedditVideoMakerBot.git
   cd RedditVideoMakerBot
   ```

## ⚙️ Step 3: Set Up Reddit Access

You need Reddit API credentials to access Reddit stories. Don't worry, it's free!

### Get Reddit Credentials (5 minutes)
1. **Go to Reddit**: Visit [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. **Log in** to your Reddit account
3. **Create an app**:
   - Click "Create App" or "Create Another App"
   - **Name**: "Dream Video Creator" (or whatever you want)
   - **App type**: Select "script"
   - **Description**: Leave blank
   - **About URL**: Leave blank
   - **Redirect URI**: Type `http://localhost:8080`
4. **Save your credentials**:
   - **Client ID**: The text under your app name (looks like random letters/numbers)
   - **Client Secret**: The "secret" field (longer random text)
   - **Username**: Your Reddit username
   - **Password**: Your Reddit password

**⚠️ Keep these credentials private!**

## 🚀 Step 4: Easy Setup (Recommended)

The easiest way to get started:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(This might take a few minutes)*

2. **Run the setup wizard**:
   ```bash
   python setup_dream.py
   ```

3. **Follow the prompts**:
   - Enter your Reddit credentials from Step 3
   - Choose your preferred subreddits (or stick with defaults)
   - Pick a theme (Dark is recommended for dreams)

## 🎬 Step 5: Create Your First Video

### Method 1: Easy Launcher (Recommended for beginners)
```bash
python run_dream.py
```
This opens a friendly menu where you can:
- Create videos
- Change settings
- Get help

### Method 2: Direct Run
```bash
python main.py
```
This runs the video creator directly.

## ⏱️ What to Expect

- **First run**: 5-10 minutes (downloading background videos, processing)
- **Subsequent runs**: 2-5 minutes
- **Progress**: You'll see status updates in the terminal
- **Output**: Videos are saved in the `results/` folder

## 📁 Understanding the Output

After creating a video, you'll find these files in `results/`:
- `final_video.mp4` - Your completed video
- `audio.mp3` - The narration audio
- `thumbnail.png` - Video thumbnail
- Various image files used in the video

## 🎨 Customization Options

### Change Subreddits
Edit `config.toml` and modify this line:
```toml
subreddit = "Dreams+DreamAnalysis+LucidDreaming"
```

Popular dream subreddits:
- `Dreams` - General dream stories
- `LucidDreaming` - Conscious dreaming experiences  
- `DreamAnalysis` - Dream interpretation
- `Nightmares` - Scary dreams
- `DreamJournal` - Personal dream logs

### Change Theme
In `config.toml`, change:
```toml
theme = "dark"  # or "light" or "transparent"
```

### Change Voice
In `config.toml`, modify:
```toml
tiktok_voice = "en_us_001"  # Different voice options available
```

## 🐛 Troubleshooting

### "No module named..."
**Problem**: Missing Python packages
**Solution**: Run `pip install -r requirements.txt`

### "Reddit credentials invalid"
**Problem**: Wrong Reddit credentials
**Solution**: 
1. Double-check your credentials at [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Run `python setup_dream.py` to re-enter them

### "No content found"
**Problem**: No suitable dream posts found
**Solution**:
- Try different subreddits
- Lower the minimum comments requirement in config.toml
- Try running at different times (Reddit content varies)

### Video creation fails
**Problem**: Missing video processing tools
**Solution**: 
- **Mac**: `brew install ffmpeg`
- **Windows**: Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
- **Linux**: `sudo apt install ffmpeg`

### "Permission denied" or file errors
**Problem**: File permission issues
**Solution**: Make sure you have write permissions in the folder

## 🎯 Tips for Better Videos

1. **Best times to run**: Reddit is most active during US evening hours
2. **Experiment with subreddits**: Different subs have different story styles
3. **Check the results folder**: Look at generated images to see what worked
4. **Adjust story length**: Modify `storymode_max_length` in config for longer/shorter videos
5. **Background matters**: The default Minecraft background is calming for dream content

## 🔄 Running Multiple Videos

Want to create several videos? Easy!

1. **Change the run count** in `config.toml`:
   ```toml
   times_to_run = 5  # Creates 5 videos
   ```

2. **Or run multiple times manually**:
   ```bash
   python main.py  # Run once
   python main.py  # Run again
   ```

Each run creates a new video with different content.

## 📚 Advanced Configuration

Once you're comfortable, you can customize:

- **Video resolution**: Change `resolution_w` and `resolution_h`
- **Background videos**: Add your own to the `assets/backgrounds/` folder
- **Voice settings**: Try ElevenLabs for premium voices
- **AI keywords**: Modify `ai_similarity_keywords` for better content matching

## 🆘 Getting Help

1. **Check existing documentation**: `README_DREAM.md` has technical details
2. **Configuration issues**: Run `python setup_dream.py` again
3. **Video problems**: Check the `results/` folder for partial files
4. **Still stuck?**: Check the error messages in the terminal - they usually explain what's wrong

## 🎉 You're Ready!

You now have everything you need to create amazing dream videos! Start with the easy launcher:

```bash
python run_dream.py
```

And follow the prompts. Your first video will be ready in just a few minutes!

---

**Happy dreaming! 🌙✨**

*Remember: The first video takes longer as it downloads background content. After that, it's much faster!* 