import os
import re
import textwrap
from pathlib import Path
from typing import Dict, Final, List

from PIL import Image, ImageDraw, ImageFont
from rich.progress import track

from TTS.engine_wrapper import process_text
from utils import settings
from utils.console import print_step, print_substep
from utils.fonts import getheight, getsize


def draw_multiline_text_with_styling(
    image, text, font, text_color, padding, wrap=50, transparent=False, 
    title_font=None, title_color=None
) -> None:
    """
    Draw multiline text over given image with improved styling for dream content
    """
    # Ensure text is a string
    if isinstance(text, list):
        text = " ".join(str(item) for item in text)
    elif not isinstance(text, str):
        text = str(text) if text is not None else ""
    
    draw = ImageDraw.Draw(image)
    font_height = getheight(font, text)
    image_width, image_height = image.size
    lines = textwrap.wrap(text, width=wrap)
    
    # Calculate total text height
    total_height = (font_height + padding) * len(lines)
    y = (image_height - total_height) / 2
    
    for line in lines:
        line_width, line_height = getsize(font, line)
        x = (image_width - line_width) / 2
        
        if transparent:
            # Add shadow for better readability on transparent backgrounds
            shadow_color = "black"
            for offset in range(1, 4):
                for dx, dy in [(-offset, -offset), (offset, -offset), 
                              (-offset, offset), (offset, offset)]:
                    draw.text((x + dx, y + dy), line, font=font, fill=shadow_color)
        
        # Draw the main text
        draw.text((x, y), line, font=font, fill=text_color)
        y += line_height + padding


def create_dream_title_image(reddit_object: dict, theme, text_color, transparent=False) -> str:
    """
    Create a title image for the dream post
    """
    reddit_id = re.sub(r"[^\w\s-]", "", reddit_object["thread_id"])
    
    # Ensure directory exists
    Path(f"assets/temp/{reddit_id}/png").mkdir(parents=True, exist_ok=True)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), 80)
        subtitle_font = ImageFont.truetype(os.path.join("fonts", "Roboto-Regular.ttf"), 40)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # FIXED: Use correct portrait dimensions (1080x1920)
    size = (1080, 1920)
    image = Image.new("RGBA", size, (0, 0, 0, 0))  # Transparent background
    
    # Process the title
    title_text = reddit_object["thread_title"]
    if len(title_text) > 100:  # Truncate very long titles
        title_text = title_text[:97] + "..."
    
    # Add a dream-themed subtitle
    subtitle = "✨ Dream Story ✨"
    
    # Draw title with clean text (no purple background)
    draw_clean_text(
        image, title_text, title_font, text_color, 
        padding=20, wrap=25
    )
    
    # Add subtitle at the bottom
    draw = ImageDraw.Draw(image)
    subtitle_width, subtitle_height = getsize(subtitle_font, subtitle)
    x = (1080 - subtitle_width) / 2
    y = 1920 - subtitle_height - 150
    
    # Add shadow for readability
    for offset in range(1, 4):
        for dx, dy in [(-offset, -offset), (offset, -offset), 
                      (-offset, offset), (offset, offset)]:
            draw.text((x + dx, y + dy), subtitle, font=subtitle_font, fill=(0, 0, 0, 200))
    
    draw.text((x, y), subtitle, font=subtitle_font, fill=text_color)
    
    # Save the image
    image_path = f"assets/temp/{reddit_id}/png/title.png"
    image.save(image_path)
    return image_path


def create_dream_content_images(reddit_object: dict, theme, text_color, transparent=False) -> List[str]:
    """
    Create images for dream content text, breaking it into readable chunks
    """
    reddit_id = re.sub(r"[^\w\s-]", "", reddit_object["thread_id"])
    
    # Get the main post content (the dream)
    if "thread_post" in reddit_object and reddit_object["thread_post"]:
        dream_text = reddit_object["thread_post"]
        # Handle case where thread_post might be a list
        if isinstance(dream_text, list):
            dream_text = " ".join(str(item) for item in dream_text)
        elif not isinstance(dream_text, str):
            dream_text = str(dream_text)
    elif reddit_object.get("comments") and len(reddit_object["comments"]) > 0:
        # If no post content, use the first comment as the dream
        dream_text = reddit_object["comments"][0]["comment_body"]
    else:
        dream_text = "No dream content found."
    
    # Clean and process the text
    dream_text = process_text(dream_text, False)
    
    # Load fonts
    try:
        content_font = ImageFont.truetype(os.path.join("fonts", "Roboto-Regular.ttf"), 60)
    except:
        content_font = ImageFont.load_default()
    
    # FIXED: Use correct portrait dimensions (1080x1920)
    size = (1080, 1920)
    
    # Split text into chunks that fit nicely on screen
    # Each chunk should be roughly 400-600 characters for good readability
    max_chars_per_image = 500
    text_chunks = []
    
    if len(dream_text) <= max_chars_per_image:
        text_chunks = [dream_text]
    else:
        # Split by sentences first, then group into chunks
        sentences = re.split(r'[.!?]+', dream_text)
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk + sentence) <= max_chars_per_image:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    text_chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            text_chunks.append(current_chunk.strip())
    
    # Create images for each chunk
    image_paths = []
    for idx, chunk in enumerate(track(text_chunks, "Creating dream content images...")):
        image = Image.new("RGBA", size, (0, 0, 0, 0))  # Transparent background
        
        draw_clean_text(
            image, chunk, content_font, text_color, 
            padding=15, wrap=30
        )
        
        image_path = f"assets/temp/{reddit_id}/png/content_{idx}.png"
        image.save(image_path)
        image_paths.append(image_path)
    
    return image_paths


def draw_clean_text(image, text, font, text_color, padding, wrap=50) -> None:
    """
    Draw clean multiline text with shadows but no background boxes
    """
    # Ensure text is a string
    if isinstance(text, list):
        text = " ".join(str(item) for item in text)
    elif not isinstance(text, str):
        text = str(text) if text is not None else ""
    
    draw = ImageDraw.Draw(image)
    font_height = getheight(font, text)
    image_width, image_height = image.size
    lines = textwrap.wrap(text, width=wrap)
    
    # Calculate total text height
    total_height = (font_height + padding) * len(lines)
    y = (image_height - total_height) / 2
    
    for line in lines:
        line_width, line_height = getsize(font, line)
        x = (image_width - line_width) / 2
        
        # Add subtle shadow for readability
        for offset in range(1, 4):
            for dx, dy in [(-offset, -offset), (offset, -offset), 
                          (-offset, offset), (offset, offset)]:
                draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 180))
        
        # Draw the main text
        draw.text((x, y), line, font=font, fill=text_color)
        y += line_height + padding


def create_dream_comment_images(reddit_object: dict, theme, text_color, 
                               max_comments=5, transparent=False) -> List[str]:
    """
    Create images for dream-related comments (analysis, interpretations, etc.)
    """
    reddit_id = re.sub(r"[^\w\s-]", "", reddit_object["thread_id"])
    
    if not reddit_object.get("comments"):
        return []
    
    # Load fonts
    try:
        comment_font = ImageFont.truetype(os.path.join("fonts", "Roboto-Regular.ttf"), 50)
        header_font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), 60)
    except:
        comment_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
    
    # FIXED: Use correct portrait dimensions (1080x1920)
    size = (1080, 1920)
    image_paths = []
    
    # Process comments (limit to max_comments)
    comments_to_process = reddit_object["comments"][:max_comments]
    
    for idx, comment in enumerate(track(comments_to_process, "Creating comment images...")):
        image = Image.new("RGBA", size, (0, 0, 0, 0))  # Transparent background
        
        # Add a header
        header_text = f"💭 Dream Analysis #{idx + 1}"
        
        # Process comment text
        comment_text = process_text(comment["comment_body"], False)
        
        # Truncate very long comments
        if len(comment_text) > 400:
            comment_text = comment_text[:397] + "..."
        
        # Draw header
        draw = ImageDraw.Draw(image)
        header_width, header_height = getsize(header_font, header_text)
        header_x = (1080 - header_width) / 2
        header_y = 400
        
        # Add shadow for readability
        for offset in range(1, 4):
            for dx, dy in [(-offset, -offset), (offset, -offset), 
                          (-offset, offset), (offset, offset)]:
                draw.text((header_x + dx, header_y + dy), header_text, 
                         font=header_font, fill=(0, 0, 0, 200))
        
        draw.text((header_x, header_y), header_text, font=header_font, fill=text_color)
        
        # Draw comment content below header using our clean text function
        content_y_start = header_y + header_height + 100
        content_image = Image.new("RGBA", (1080, 1920 - int(content_y_start)), (0, 0, 0, 0))
        
        draw_clean_text(
            content_image, comment_text, comment_font, text_color, 
            padding=12, wrap=25
        )
        
        # Paste the content image onto the main image
        image.paste(content_image, (0, int(content_y_start)), content_image)
        
        image_path = f"assets/temp/{reddit_id}/png/comment_{idx}.png"
        image.save(image_path)
        image_paths.append(image_path)
    
    return image_paths


def generate_dream_images(reddit_obj: dict):
    """Generate clean text images for dream content"""
    reddit_id = reddit_obj["thread_id"]
    
    # Create output directory
    Path(f"assets/temp/{reddit_id}/png").mkdir(parents=True, exist_ok=True)
    
    # Portrait video dimensions for mobile/TikTok format
    W, H = 1080, 1920
    
    print_substep("Creating clean title image...")
    create_clean_title_image(reddit_obj["thread_title"], reddit_id, W, H)
    
    print_substep("Creating clean content images...")
    
    # Get post content and split into chunks
    story_max_length = settings.config['settings']['storymode_max_length']
    post_content = reddit_obj.get("thread_post", "")
    if isinstance(post_content, list):
        post_content = "\n\n".join(post_content)
    
    if len(post_content) > story_max_length:
        post_content = post_content[:story_max_length] + "..."
    
    if post_content:
        # Create content chunks
        chunks = create_text_chunks(post_content, max_chars_per_chunk=250)
        
        for i, chunk in enumerate(chunks):
            create_clean_content_image(chunk, f"content_{i}", reddit_id, W, H)
            if i >= 5:  # Limit to 5 chunks max
                break
    
    print_substep(f"Generated {min(len(chunks), 5)} clean content images!")

def create_clean_title_image(title: str, reddit_id: str, W: int, H: int):
    """Create a clean title image without purple background"""
    # Create transparent base
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Load font
    try:
        font = ImageFont.truetype("fonts/Roboto-Bold.ttf", 80)
    except:
        font = ImageFont.load_default()
    
    # Add clean text with shadows
    lines = textwrap.wrap(title, width=25)
    line_height = 90
    total_height = len(lines) * line_height
    start_y = (H - total_height) // 2
    
    for i, line in enumerate(lines):
        # Get text dimensions
        text_bbox = draw.textbbox((0, 0), line, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x = (W - text_width) // 2
        y = start_y + (i * line_height)
        
        # Add shadow for readability
        for offset in range(1, 4):
            for dx, dy in [(-offset, -offset), (offset, -offset), 
                          (-offset, offset), (offset, offset)]:
                draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 180))
        
        # Draw main text
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
    
    img.save(f"assets/temp/{reddit_id}/png/title.png", "PNG")

def create_clean_content_image(text: str, filename: str, reddit_id: str, W: int, H: int):
    """Create clean content images without purple background"""
    # Create transparent base
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Load font
    try:
        font = ImageFont.truetype("fonts/Roboto-Regular.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    # Add clean text with shadows
    lines = textwrap.wrap(text, width=30)
    line_height = 70
    total_height = len(lines) * line_height
    start_y = (H - total_height) // 2
    
    for i, line in enumerate(lines):
        # Get text dimensions
        text_bbox = draw.textbbox((0, 0), line, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x = (W - text_width) // 2
        y = start_y + (i * line_height)
        
        # Add shadow for readability
        for offset in range(1, 4):
            for dx, dy in [(-offset, -offset), (offset, -offset), 
                          (-offset, offset), (offset, offset)]:
                draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 180))
        
        # Draw main text
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
    
    img.save(f"assets/temp/{reddit_id}/png/{filename}.png", "PNG")

def create_text_chunks(text: str, max_chars_per_chunk=250):
    """Split text into readable chunks"""
    if len(text) <= max_chars_per_chunk:
        return [text]
    
    chunks = []
    sentences = re.split(r'[.!?]+', text)
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        if len(current_chunk + sentence) <= max_chars_per_chunk:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def create_title_image(title: str, reddit_id: str, W: int, H: int):
    """Create a clean title image without purple background - OVERRIDE"""
    return create_clean_title_image(title, reddit_id, W, H)

def create_content_image(text: str, filename: str, reddit_id: str, W: int, H: int):
    """Create clean content images without purple background - OVERRIDE"""
    return create_clean_content_image(text, filename, reddit_id, W, H)

def create_large_text_image(text: str, filename: str, reddit_id: str, W: int, H: int):
    """Create clean large text images without purple background - OVERRIDE"""
    return create_clean_content_image(text, filename, reddit_id, W, H)

def add_premium_text(draw, text: str, W: int, H: int, is_title: bool = False, text_area_bounds=None):
    """Add premium styled text with beautiful typography"""
    if is_title:
        font_size = 68
        text_color = (255, 255, 255, 255)
        stroke_color = (147, 112, 219, 200)
        y_offset = H // 2.5
        max_width = W - 140
    else:
        font_size = 42
        text_color = (255, 255, 255, 255)
        stroke_color = (199, 21, 133, 180)
        # Use the bounds of the text area
        if text_area_bounds:
            x_start, y_start, area_width, area_height = text_area_bounds
            y_offset = y_start + (area_height // 2)
            max_width = area_width - 40
        else:
            y_offset = H // 2
            max_width = W - 160
    
    # Load premium font
    try:
        if is_title:
            font = ImageFont.truetype("fonts/Roboto-Bold.ttf", font_size)
        else:
            font = ImageFont.truetype("fonts/Roboto-Medium.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Word wrap the text
    wrapped_lines = wrap_text_to_fit(text, font, max_width)
    
    # Calculate total text height
    line_height = font_size + 12
    total_height = len(wrapped_lines) * line_height
    
    # Start drawing from center
    current_y = y_offset - (total_height // 2)
    
    for line in wrapped_lines:
        # Get text dimensions
        text_bbox = draw.textbbox((0, 0), line, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        
        # Center the text
        x = (W - text_width) // 2
        
        # Multiple shadow layers for depth
        shadow_layers = [
            (4, 4, (0, 0, 0, 120)),
            (3, 3, (0, 0, 0, 100)),
            (2, 2, (0, 0, 0, 80)),
            (1, 1, (0, 0, 0, 60))
        ]
        
        # Draw shadow layers
        for dx, dy, shadow_color in shadow_layers:
            draw.text((x + dx, current_y + dy), line, font=font, fill=shadow_color)
        
        # Draw stroke/outline
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx != 0 or dy != 0:
                    draw.text((x + dx, current_y + dy), line, font=font, fill=stroke_color)
        
        # Draw main text with slight glow
        draw.text((x, current_y), line, font=font, fill=text_color)
        
        current_y += line_height

def add_premium_decorations(draw, W: int, H: int):
    """Add premium decorative elements"""
    import random
    random.seed(42)  # Consistent decorations
    
    # Add elegant sparkles and particles
    for _ in range(20):
        x = random.randint(50, W - 50)
        y = random.randint(50, H - 50)
        size = random.randint(2, 6)
        
        # Sparkle colors
        colors = [
            (255, 255, 255, 200),
            (199, 21, 133, 180),
            (147, 112, 219, 160),
            (138, 43, 226, 140)
        ]
        color = random.choice(colors)
        
        # Draw diamond sparkle
        points = [
            (x, y - size),      # top
            (x + size, y),      # right
            (x, y + size),      # bottom
            (x - size, y)       # left
        ]
        draw.polygon(points, fill=color)
        
        # Add small center glow
        draw.ellipse((x-1, y-1, x+1, y+1), fill=(255, 255, 255, 255))
    
    # Add elegant corner decorations
    corner_size = 30
    corner_color = (199, 21, 133, 100)
    
    # Top corners
    for corner_x in [30, W-60]:
        for i in range(3):
            draw.arc((corner_x-corner_size+i*5, 30-corner_size+i*5, 
                     corner_x+corner_size-i*5, 30+corner_size-i*5), 
                    start=0, end=90, fill=corner_color, width=2)
    
    # Bottom corners  
    for corner_x in [30, W-60]:
        for i in range(3):
            draw.arc((corner_x-corner_size+i*5, H-60-corner_size+i*5, 
                     corner_x+corner_size-i*5, H-60+corner_size-i*5), 
                    start=180, end=270, fill=corner_color, width=2)

def wrap_text_to_fit(text: str, font, max_width: int) -> list:
    """Wrap text to fit within specified width"""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = font.getbbox(test_line)
        width = bbox[2] - bbox[0]
        
        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # Single word too long, force it
                lines.append(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def split_text_into_segments(text, max_chars: int = 300) -> list:
    """Split text into readable segments"""
    # Handle case where text might be a list
    if isinstance(text, list):
        text = ' '.join(str(item) for item in text)
    elif not isinstance(text, str):
        text = str(text)
    
    sentences = text.split('. ')
    segments = []
    current_segment = ""
    
    for sentence in sentences:
        if len(current_segment + sentence) < max_chars:
            current_segment += sentence + ". "
        else:
            if current_segment:
                segments.append(current_segment.strip())
            current_segment = sentence + ". "
    
    if current_segment:
        segments.append(current_segment.strip())
    
    return segments

def create_dynamic_word_chunks(text, words_per_chunk=7):
    """Split text into dynamic chunks of 5-10 words, optimized for 2 lines"""
    # Handle case where text might be a list
    if isinstance(text, list):
        text = ' '.join(str(item) for item in text)
    elif not isinstance(text, str):
        text = str(text)
    
    # Clean the text
    words = text.split()
    chunks = []
    
    i = 0
    while i < len(words):
        # Take 5-10 words, but prefer 6-8 for better 2-line split
        chunk_size = min(words_per_chunk, len(words) - i)
        if chunk_size < 3 and chunks:  # If remaining words are too few, add to last chunk
            chunks[-1] += " " + " ".join(words[i:])
            break
        
        chunk_words = words[i:i + chunk_size]
        chunk_text = " ".join(chunk_words)
        
        # Split into 2 lines for better display
        formatted_chunk = split_into_two_lines(chunk_text)
        chunks.append(formatted_chunk)
        
        i += chunk_size
    
    return chunks

def split_into_two_lines(text):
    """Split text optimally into 2 lines"""
    words = text.split()
    if len(words) <= 3:
        return text  # Keep short text on one line
    
    # Split roughly in the middle, but prefer natural breaks
    mid_point = len(words) // 2
    
    # Try to find a good break point (avoid splitting at articles, prepositions)
    break_words = ['and', 'or', 'but', 'so', 'then', 'when', 'where', 'how', 'why']
    
    best_split = mid_point
    for i in range(max(1, mid_point - 2), min(len(words) - 1, mid_point + 2)):
        if i < len(words) and words[i].lower() in break_words:
            best_split = i
            break
    
    line1 = " ".join(words[:best_split])
    line2 = " ".join(words[best_split:])
    
    return f"{line1}\n{line2}"

def create_dynamic_text_image(text: str, filename: str, reddit_id: str, W: int, H: int):
    """Create dynamic text images optimized for 2-line display"""
    # Create transparent base
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Smaller, more elegant text area for dynamic display
    padding = 100
    text_area_width = W - (padding * 2)
    text_area_height = H // 5  # Even smaller for dynamic chunks
    
    # Center the text area
    x_start = padding
    y_start = (H - text_area_height) // 2
    
    # Create compact rounded rectangle with premium styling
    corner_radius = 30
    
    # Multi-layer glow effect (more compact)
    for i in range(6):
        glow_alpha = int(50 * (6 - i) / 6)
        glow_expand = i * 2
        
        # Compact outer glow
        draw.rounded_rectangle([
            (x_start - glow_expand, y_start - glow_expand), 
            (x_start + text_area_width + glow_expand, y_start + text_area_height + glow_expand)
        ], radius=corner_radius + glow_expand, fill=(138, 43, 226, glow_alpha))
    
    # Dynamic gradient background
    for i in range(text_area_height):
        ratio = i / text_area_height
        r = int(40 * (1 - ratio) + 60 * ratio)
        g = int(20 * (1 - ratio) + 30 * ratio)
        b = int(80 * (1 - ratio) + 120 * ratio)
        alpha = 220
        
        draw.rectangle([
            (x_start, y_start + i), 
            (x_start + text_area_width, y_start + i + 1)
        ], fill=(r, g, b, alpha))
    
    # Elegant border with dynamic colors
    border_colors = [(255, 105, 180, 255), (138, 43, 226, 255), (75, 0, 130, 255)]
    for i, color in enumerate(border_colors):
        draw.rounded_rectangle([
            (x_start - i - 1, y_start - i - 1), 
            (x_start + text_area_width + i + 1, y_start + text_area_height + i + 1)
        ], radius=corner_radius + i, outline=color, width=2)
    
    # Add dynamic text content
    add_dynamic_text(draw, text, W, H, text_area_bounds=(x_start, y_start, text_area_width, text_area_height))
    
    img.save(f"assets/temp/{reddit_id}/png/{filename}.png", "PNG")

def add_dynamic_text(draw, text: str, W: int, H: int, text_area_bounds=None):
    """Add dynamic text optimized for 2-line display"""
    font_size = 48  # Good size for dynamic chunks
    text_color = (255, 255, 255, 255)
    stroke_color = (255, 105, 180, 200)
    
    # Load dynamic font
    try:
        font = ImageFont.truetype("fonts/Roboto-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Handle 2-line text
    lines = text.split('\n') if '\n' in text else [text]
    
    # Calculate positioning
    if text_area_bounds:
        x_start, y_start, area_width, area_height = text_area_bounds
        
        line_height = font_size + 8
        total_height = len(lines) * line_height
        
        # Center vertically in the text area
        current_y = y_start + (area_height - total_height) // 2
        
        for line in lines:
            # Get text dimensions
            text_bbox = draw.textbbox((0, 0), line, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            
            # Center the text horizontally
            x = (W - text_width) // 2
            
            # Dynamic shadow layers
            shadow_layers = [
                (3, 3, (0, 0, 0, 150)),
                (2, 2, (0, 0, 0, 120)),
                (1, 1, (0, 0, 0, 100))
            ]
            
            # Draw shadow layers
            for dx, dy, shadow_color in shadow_layers:
                draw.text((x + dx, current_y + dy), line, font=font, fill=shadow_color)
            
            # Draw dynamic stroke/outline
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, current_y + dy), line, font=font, fill=stroke_color)
            
            # Draw main text with glow
            draw.text((x, current_y), line, font=font, fill=text_color)
            
            current_y += line_height

def create_large_text_chunks(text, target_chunks=4):
    """Split text into larger chunks for easier subtitle syncing"""
    # Handle case where text might be a list
    if isinstance(text, list):
        text = ' '.join(str(item) for item in text)
    elif not isinstance(text, str):
        text = str(text)
    
    # Clean the text
    sentences = text.split('. ')
    chunks = []
    
    # Calculate roughly how many sentences per chunk
    sentences_per_chunk = max(1, len(sentences) // target_chunks)
    
    current_chunk = []
    for i, sentence in enumerate(sentences):
        current_chunk.append(sentence.strip())
        
        # Create chunk when we have enough sentences or at the end
        if len(current_chunk) >= sentences_per_chunk or i == len(sentences) - 1:
            if current_chunk:
                chunk_text = '. '.join(current_chunk)
                if chunk_text and not chunk_text.endswith('.'):
                    chunk_text += '.'
                
                # Format for better readability (3-4 lines max)
                formatted_chunk = format_large_chunk(chunk_text)
                chunks.append(formatted_chunk)
                current_chunk = []
    
    return chunks

def format_large_chunk(text):
    """Format large text chunks for optimal readability (3-4 lines)"""
    words = text.split()
    if len(words) <= 8:
        return text  # Keep short text as is
    
    # Target 3-4 lines with roughly equal length
    words_per_line = len(words) // 3 if len(words) > 15 else len(words) // 2
    
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        
        # Break line when we have enough words or hit natural breaks
        if len(current_line) >= words_per_line:
            # Look for good break points
            if word.endswith(('.', ',', '!', '?')) or len(current_line) > words_per_line + 2:
                lines.append(' '.join(current_line))
                current_line = []
    
    # Add remaining words
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines) 