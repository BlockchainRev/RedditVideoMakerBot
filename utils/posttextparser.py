import os
import re
import time
from typing import List

# Make spacy optional
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from utils.console import print_step
from utils.voice import sanitize_text


# working good
def posttextparser(obj, *, tried: bool = False) -> List[str]:
    text: str = re.sub("\n", " ", obj)
    
    if not SPACY_AVAILABLE:
        # Fallback: simple sentence splitting without spacy
        sentences = re.split(r'[.!?]+', text)
        newtext = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sanitize_text(sentence):
                newtext.append(sentence + '.')
        return newtext
    
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError as e:
        if not tried:
            print_step("Spacy model not found. Using fallback sentence splitter.")
            # Use fallback instead of trying to download
            sentences = re.split(r'[.!?]+', text)
            newtext = []
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and sanitize_text(sentence):
                    newtext.append(sentence + '.')
            return newtext
        print_step(
            "The spacy model can't load. Using simple text splitting as fallback."
        )
        # Use fallback instead of raising error
        sentences = re.split(r'[.!?]+', text)
        newtext = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sanitize_text(sentence):
                newtext.append(sentence + '.')
        return newtext

    doc = nlp(text)

    newtext: list = []

    for line in doc.sents:
        if sanitize_text(line.text):
            newtext.append(line.text)

    return newtext
