#!/usr/bin/env python3
import sys
sys.path.append('.')
from video_creation.text_image_generator import generate_dream_images

# Mock reddit object with sample content  
reddit_obj = {
    'thread_id': '1kyeswh',
    'thread_title': 'How do you increase your sense of touch and detail?',
    'thread_post': 'I have been lucid dreaming for a while now and I have noticed that my sense of touch and detail is not as vivid as I would like it to be. In my dreams I can barely feel textures properly and when I try to read text it is usually blurry or changes constantly. I have been doing reality checks regularly and I can become lucid consistently but once I am lucid I struggle to make the dream more vivid and realistic. What techniques do you use to improve the clarity and detail of your lucid dreams? I have tried spinning and rubbing my hands together but these techniques only work occasionally and the effect does not last very long. Any advice would be greatly appreciated!'
}

print('🎨 Generating large text chunks for easy syncing...')
generate_dream_images(reddit_obj)
print('✅ Done! Generated larger chunks that are easier to sync.') 