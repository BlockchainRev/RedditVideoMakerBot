# ─── text_overlay.py ──────────────────────────────────────────────────────────
from pathlib import Path
from typing    import List, Tuple
from PIL       import Image, ImageDraw, ImageFont


# ── Public helper #1 ──────────────────────────────────────────────────────────
def chunk_text_for_tts(text: str, max_words: int = 28) -> List[str]:
    """
    Split `text` into word-chunks (default ≈2-seconds of speech) that you can
    hand both to your TTS engine *and* to `render_chunks_to_images`.
    """
    words = text.replace('\n', ' ').split()
    chunks, current = [], []

    for w in words:
        current.append(w)
        if len(current) >= max_words:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks


# ── Public helper #2 ──────────────────────────────────────────────────────────
def render_chunks_to_images(chunks       : List[str],
                            out_dir      : Path,
                            font_path    : str = "fonts/Roboto-Regular.ttf",
                            base_size    : int = 120,
                            shadow       : bool = True,
                            text_color   : Tuple[int, int, int, int]=(255, 255, 255, 255),
                            margin_px    : int = 48,
                            canvas_size  : Tuple[int, int]=(1080, 1920)
                            ) -> List[Path]:
    """
    Turn each `chunk` into a centred 1080×1920 PNG.  
    Returns the list of saved file paths (in the same order as `chunks`).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []

    for idx, chunk in enumerate(chunks):
        img   = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        draw  = ImageDraw.Draw(img)
        font  = ImageFont.truetype(font_path, base_size)
        lines = _wrap_text_by_pixels(chunk, font, canvas_size[0] - 2*margin_px)

        # If a line is STILL too wide (rare URL case) → shrink font until fits
        while _line_too_wide(lines, font, canvas_size[0] - 2*margin_px) and font.size > 14:
            font  = ImageFont.truetype(font_path, font.size - 2)
            lines = _wrap_text_by_pixels(chunk, font, canvas_size[0] - 2*margin_px)

        _draw_lines_centered(draw, lines, font, text_color, shadow,
                             canvas_size, margin_px)

        path = out_dir / f"{idx:03d}.png"
        img.save(path, "PNG")
        paths.append(path)

    return paths


# ── Public helper #3 ──────────────────────────────────────────────────────────
def render_dream_analysis_images(analysis_data: dict,
                                out_dir: Path,
                                font_path: str = "fonts/Roboto-Regular.ttf",
                                ) -> List[Path]:
    """
    Generate styled images for dream analysis chunks.
    
    Args:
        analysis_data: Dictionary containing dream analysis data with full_text
        out_dir: Output directory for images
        font_path: Path to font file
        
    Returns:
        List of generated image paths
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    
    # Get the analysis content for chunking
    analysis_content = analysis_data.get("full_text", "")
    
    if not analysis_content.strip():
        return paths  # No content to generate images for
    
    # Chunk the analysis content like other Reddit content
    analysis_chunks = chunk_text_for_tts(analysis_content)
    
    # Define color for analysis (use dream analysis gold)
    analysis_color = (255, 215, 0, 255)  # Gold
    
    # Generate images for each chunk
    for idx, chunk in enumerate(analysis_chunks):
        if not chunk.strip():
            continue  # Skip empty chunks
        
        # Add dream analysis prefix to first chunk only
        if idx == 0:
            text = f"🌙 Dream Analysis\n\n{chunk}"
        else:
            text = chunk
        
        img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Use standard font size for analysis chunks
        font = ImageFont.truetype(font_path, 100)
        lines = _wrap_text_by_pixels(text, font, 1080 - 96)  # 48px margin on each side
        
        # If text is still too wide, reduce font size
        while _line_too_wide(lines, font, 1080 - 96) and font.size > 50:
            font = ImageFont.truetype(font_path, font.size - 5)
            lines = _wrap_text_by_pixels(text, font, 1080 - 96)
        
        # Draw with analysis styling
        _draw_lines_centered(draw, lines, font, analysis_color, shadow=True, 
                           canvas_size=(1080, 1920), margin_px=48)
        
        # Save with chunk-based filename
        path = out_dir / f"analysis_chunk_{idx}.png"
        img.save(path, "PNG")
        paths.append(path)
    
    return paths


# ── Internal utils ────────────────────────────────────────────────────────────
def _line_too_wide(lines: List[str], font, max_px: int) -> bool:
    return any(font.getlength(l) > max_px for l in lines)


def _soft_hyphen_split(word: str, font, max_px: int) -> List[str]:
    """
    Hyphenate a single gigantic word so each part ≤ max_px.
    """
    pieces, current = [], ""
    for ch in word:
        if font.getlength(current + ch) <= max_px:
            current += ch
        else:
            # add a soft hyphen (U+00AD) so browsers/players can break nicely
            pieces.append(current + "\u00AD")
            current = ch
    if current:
        pieces.append(current)
    return pieces


def _wrap_text_by_pixels(text: str, font, max_px: int) -> List[str]:
    """
    True pixel-perfect wrapper: produces lines whose rendered width ≤ max_px.
    """
    words   = text.split()
    lines   = []
    current = []

    for w in words:
        w_px = font.getlength(w)
        if w_px > max_px:                      # monster token → hyphen split
            if current:
                lines.append(" ".join(current))
                current = []
            for part in _soft_hyphen_split(w, font, max_px):
                lines.append(part)
            continue

        test_line = " ".join(current + [w])
        if font.getlength(test_line) <= max_px:
            current.append(w)
        else:
            lines.append(" ".join(current))
            current = [w]

    if current:
        lines.append(" ".join(current))
    return lines


def _draw_lines_centered(draw, lines, font, fill, shadow,
                         canvas_size, margin_px):
    W, H   = canvas_size
    lh     = font.size + 12                 # line height
    total  = lh * len(lines)
    y      = (H - total) // 2

    for line in lines:
        w_px = font.getlength(line)
        x    = (W - w_px) // 2
        if shadow:
            # Create a light black outline by drawing text in 8 directions around the main position
            outline_width = 1  # Width of the outline
            outline_color = (0, 0, 0, 100)  # Light black with alpha for subtle effect
            
            # Draw outline in 8 directions (top, bottom, left, right, and 4 diagonals)
            for dx in [-outline_width, 0, outline_width]:
                for dy in [-outline_width, 0, outline_width]:
                    if dx != 0 or dy != 0:  # Skip the center position (main text)
                        draw.text((x + dx, y + dy), line, font=font, fill=outline_color)
        
        # Draw the main text on top
        draw.text((x, y), line, font=font, fill=fill)
        y += lh
# ──────────────────────────────────────────────────────────────────────────────