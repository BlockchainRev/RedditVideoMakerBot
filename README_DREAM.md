# 🌙 Dream Tales Video Creator

An automated dream journal video creator that extracts dream stories from Reddit and transforms them into engaging, narrated videos perfect for marketing dream-related content.

## ✨ What This Tool Does

This modified version of the Reddit Video Maker Bot is specifically designed for creating dream journal videos:

- **Extracts Dream Stories**: Automatically pulls dream content from subreddits like r/Dreams, r/DreamAnalysis, r/LucidDreaming
- **Text-Based Visuals**: Instead of screenshots, creates beautiful text-based images with dream content
- **Auto-Narration**: Converts dream text to speech for engaging storytelling
- **Marketing Ready**: Perfect for creating content for dream journals, sleep apps, or mystical/spiritual brands

## 🎯 Key Features

### Dream-Focused Content
- Targets dream-related subreddits automatically
- Uses AI similarity matching to find the best dream stories
- Handles both long dream narratives and comment-based analysis
- Optimized for storytelling format

### Beautiful Text Visuals
- No more Reddit UI screenshots
- Clean, readable text displays with customizable themes
- Dream-themed styling with mystical elements
- Multiple text chunks for longer dreams

### Smart Content Processing
- Automatically extracts main dream content from posts
- Falls back to comments if no post content is available
- Filters and processes text for optimal readability
- Handles various dream story formats

## 🚀 Quick Start

1. **Setup Reddit Credentials**
   ```bash
   # Copy the sample config
   cp config.dream.toml config.toml
   
   # Edit config.toml with your Reddit app credentials
   nano config.toml
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Dream Video Creator**
   ```bash
   python main.py
   ```

## 📋 Configuration

### Reddit Setup
1. Go to https://www.reddit.com/prefs/apps
2. Create a new app (select "script" type)
3. Copy the client ID and secret to your config file

### Dream-Optimized Settings

The `config.dream.toml` file comes pre-configured with optimal settings:

```toml
[reddit.thread]
subreddit = "Dreams+DreamAnalysis+LucidDreaming"
min_comments = 3  # Dreams posts might have fewer comments

[ai]
ai_similarity_enabled = true
ai_similarity_keywords = "dream, nightmare, sleep, vision, lucid, subconscious"

[settings]
storymode = true  # Essential for dream narratives
theme = "dark"    # Works well for mystical content
storymode_max_length = 2000  # Longer dreams
```

## 🎨 Customization

### Themes
- **Dark**: Mystical, night-time feel perfect for dreams
- **Light**: Clean, minimalist approach
- **Transparent**: Overlay text on background videos

### Subreddits
Popular dream-related subreddits:
- `Dreams` - General dream sharing
- `DreamAnalysis` - Dream interpretation discussions  
- `LucidDreaming` - Conscious dreaming experiences
- `DreamInterpretation` - Symbolic dream meanings
- `Nightmares` - Scary dream content
- `DreamJournal` - Personal dream logs

### AI Keywords
Customize similarity matching with keywords like:
- `lucid, astral, prophetic, recurring`
- `symbols, meaning, interpretation`
- `nightmare, anxiety, fear`
- `flying, falling, chase`

## 🎬 Output

The tool creates:
1. **Title Image**: Dream story title with mystical styling
2. **Content Images**: Dream narrative broken into readable chunks
3. **Analysis Images**: Community interpretations and discussions
4. **Final Video**: Narrated video with background and music

## 🔧 Advanced Features

### Story Mode
- Enabled by default for dream content
- Creates narrative flow from dream posts
- Handles long-form dream descriptions
- Multiple text display methods

### Background Options
- Minecraft: Calming, meditative gameplay
- Lofi audio: Perfect for dream content
- Customizable opacity and timing

### Voice Options
- TikTok TTS: Free, good quality
- ElevenLabs: Premium, natural voices
- Multiple language support

## 📱 Marketing Applications

Perfect for:
- **Dream Journal Apps**: Content marketing videos
- **Sleep/Wellness Brands**: Engaging social media content  
- **Spiritual/Mystical Content**: YouTube channels, TikTok
- **Podcast Promotion**: Visual content for dream-themed podcasts
- **Blog/Website Content**: Embedded videos for dream-related articles

## 🛠️ Troubleshooting

### Common Issues

**No Dream Content Found**
- Check if the subreddit has recent posts
- Lower `min_comments` setting in config
- Try different subreddits

**Text Too Long/Short**
- Adjust `storymode_max_length` in config
- Modify `max_comment_length` settings
- Use AI similarity for better content selection

**Poor Voice Quality**
- Set up TikTok session ID for better TTS
- Consider ElevenLabs for premium voices
- Adjust `silence_duration` for pacing

## 📄 Requirements

- Python 3.10+
- Reddit API credentials
- Required Python packages (see requirements.txt)
- Optional: TikTok session ID for premium TTS

## 🤝 Contributing

This is a specialized fork focused on dream content. For general Reddit video creation, see the original project.

## 📜 License

Same license as the original Reddit Video Maker Bot project.

---

*Transform dreams into captivating videos for your marketing needs! 🌙✨* 