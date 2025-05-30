from PIL.ImageFont import FreeTypeFont, ImageFont


def getsize(font: ImageFont | FreeTypeFont, text: str):
    # Ensure text is a string
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    left, top, right, bottom = font.getbbox(text)
    width = right - left
    height = bottom - top
    return width, height


def getheight(font: ImageFont | FreeTypeFont, text: str):
    # Ensure text is a string  
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    _, height = getsize(font, text)
    return height
