#!/usr/bin/env python
import math
import sys
from os import name, listdir
from pathlib import Path
from subprocess import Popen
from typing import NoReturn

from prawcore import ResponseException

from reddit.subreddit import get_subreddit_threads
from utils import settings
from utils.cleanup import cleanup
from utils.console import print_markdown, print_step, print_substep
from utils.ffmpeg_install import ffmpeg_install
from utils.id import id
from utils.version import checkversion
from utils.dream_analysis import is_dream_analysis_enabled
from video_creation.background import (
    chop_background,
    download_background_audio,
    download_background_video,
    get_background_config,
)
from video_creation.final_video import make_final_video
from video_creation.text_image_generator import render_chunks_to_images, chunk_text_for_tts, render_dream_analysis_images
from video_creation.voices import save_text_to_mp3

__VERSION__ = "3.3.0"

print(
    """
██████╗ ██████╗ ███████╗ █████╗ ███╗   ███╗    ████████╗ █████╗ ██╗     ███████╗███████╗
██╔══██╗██╔══██╗██╔════╝██╔══██╗████╗ ████║    ╚══██╔══╝██╔══██╗██║     ██╔════╝██╔════╝
██║  ██║██████╔╝█████╗  ███████║██╔████╔██║       ██║   ███████║██║     █████╗  ███████╗
██║  ██║██╔══██╗██╔══╝  ██╔══██║██║╚██╔╝██║       ██║   ██╔══██║██║     ██╔══╝  ╚════██║
██████╔╝██║  ██║███████╗██║  ██║██║ ╚═╝ ██║       ██║   ██║  ██║███████╗███████╗███████║
╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝       ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝
                        🌙 Dream Journal Video Creator 🌙
"""
)
print_markdown(
    "### Dream Tales Video Creator - Automated dream story videos from Reddit! Perfect for creating engaging dream journal content for marketing. Extract dreams from r/Dreams, r/DreamAnalysis and more!"
)
checkversion(__VERSION__)


def main(POST_ID=None) -> None:
    global redditid, reddit_object
    
    # User prompts for enhanced features
    use_dream_analysis = False
    keep_under_30_seconds = False
    
    # Check if dream analysis is available and prompt user
    if is_dream_analysis_enabled():
        print_step("🌙 Dream Analysis Options")
        analysis_choice = input("Do you want to include professional dream analysis in your video? (y/n): ").strip().lower()
        use_dream_analysis = analysis_choice.startswith('y')
        
        if use_dream_analysis:
            print_substep("✅ Dream analysis will be included", "green")
            
            # Additional prompt for video length optimization
            print_step("⏱️ Video Length Options")
            length_choice = input("Do you want to keep the final video under 30 seconds? (y/n): ").strip().lower()
            keep_under_30_seconds = length_choice.startswith('y')
            
            if keep_under_30_seconds:
                print_substep("✅ Video will be optimized for ~30 seconds", "green")
                print_substep("📝 Note: Content will be summarized to fit time limit", "yellow")
            else:
                print_substep("📹 Video will include full content", "blue")
        else:
            print_substep("📹 Creating video without dream analysis", "blue")
    else:
        print_substep("💭 Dream analysis not configured - skipping", "yellow")
    
    # Get Reddit content with analysis preferences
    reddit_object = get_subreddit_threads(POST_ID, use_dream_analysis, keep_under_30_seconds)
    redditid = id(reddit_object)
    length, number_of_comments = save_text_to_mp3(reddit_object)
    length = math.ceil(length)
    
    # Generate the dream images
    image_dir = Path(f"assets/temp/{redditid}/png")
    image_dir.mkdir(parents=True, exist_ok=True) # Ensure directory exists

    # Render title image
    title_text = reddit_object['thread_title']
    title_chunks = chunk_text_for_tts(title_text)
    if title_chunks: # Ensure there's a title to render
        title_image_paths = render_chunks_to_images(chunks=title_chunks, out_dir=image_dir, font_path="fonts/Roboto-Bold.ttf", base_size=70) # Render title
        # Rename the first generated image for the title to title.png
        if title_image_paths:
            first_title_image_path = title_image_paths[0]
            if first_title_image_path.exists() and first_title_image_path.name != "title.png":
                 # Construct the target path for title.png within the same directory
                target_title_path = image_dir / "title.png"
                # If title.png already exists from a previous chunk, remove it or handle as needed
                if target_title_path.exists():
                    target_title_path.unlink() # Remove existing title.png to avoid error on rename
                first_title_image_path.rename(target_title_path)
            # If more than one image was generated for the title, these are currently ignored.
            # This might need a more sophisticated handling if titles can span multiple images.

    # Render post content images
    thread_post_text_source = reddit_object['thread_post']
    post_images_generated_count = 0

    if settings.config["settings"]["storymode"] and settings.config["settings"]["storymodemethod"] == 1:
        # In storymodemethod 1, thread_post_text_source is already a list of sentences
        if isinstance(thread_post_text_source, list):
            for idx, sentence_text in enumerate(thread_post_text_source):
                if not sentence_text.strip(): # Skip empty sentences
                    continue
                # Each sentence becomes one image
                # render_chunks_to_images expects a list of chunks, so pass [sentence_text]
                # It will save as 000.png in the out_dir for this single chunk
                sentence_image_paths = render_chunks_to_images(chunks=[sentence_text], out_dir=image_dir, font_path="fonts/Roboto-Bold.ttf")
                if sentence_image_paths:
                    source_path = sentence_image_paths[0] # Should be one image per sentence
                    target_path = image_dir / f"content_{post_images_generated_count}.png"
                    if source_path.exists() and source_path != target_path:
                        if target_path.exists():
                            target_path.unlink()
                        source_path.rename(target_path)
                    post_images_generated_count += 1
        else:
            # Fallback for safety, though it should be a list
            if isinstance(thread_post_text_source, str) and thread_post_text_source.strip():
                post_chunks = chunk_text_for_tts(thread_post_text_source)
                if post_chunks:
                    post_image_paths = render_chunks_to_images(chunks=post_chunks, out_dir=image_dir, font_path="fonts/Roboto-Bold.ttf")
                    for i, source_path in enumerate(post_image_paths):
                        target_path = image_dir / f"content_{post_images_generated_count}.png"
                        if source_path.exists() and source_path != target_path and source_path.name != "title.png":
                            if target_path.exists():
                                target_path.unlink()
                            source_path.rename(target_path)
                        post_images_generated_count += 1
    else: # Existing logic for other modes or if storymode is off
        thread_post_text_for_chunking = ""
        if isinstance(thread_post_text_source, list):
            thread_post_text_for_chunking = " ".join(thread_post_text_source)
        elif isinstance(thread_post_text_source, str):
            thread_post_text_for_chunking = thread_post_text_source
        
        if thread_post_text_for_chunking.strip():
            post_chunks = chunk_text_for_tts(thread_post_text_for_chunking)
            if post_chunks:
                post_image_paths = render_chunks_to_images(chunks=post_chunks, out_dir=image_dir, font_path="fonts/Roboto-Bold.ttf")
                for i, source_path in enumerate(post_image_paths): # Changed idx to i to avoid conflict
                    target_path = image_dir / f"content_{post_images_generated_count}.png"
                    # Check source_path.name != "title.png" is important if title image was also saved as 000.png and not yet renamed
                    if source_path.exists() and source_path != target_path and source_path.name != "title.png":
                        if target_path.exists():
                            target_path.unlink() # Make sure we're not trying to rename to an existing file from a previous iteration
                        source_path.rename(target_path)
                    post_images_generated_count += 1
    
    # 🌙 GENERATE DREAM ANALYSIS IMAGES
    if reddit_object.get("dream_analysis"):
        print_step("🎨 Generating dream analysis images...")
        try:
            analysis_image_paths = render_dream_analysis_images(
                reddit_object["dream_analysis"], 
                image_dir,
                font_path="fonts/Roboto-Bold.ttf"
            )
            if analysis_image_paths:
                print_substep(f"✅ Generated {len(analysis_image_paths)} analysis images", "green")
                for path in analysis_image_paths:
                    print_substep(f"   📄 {path.name}", "blue")
            else:
                print_substep("⚠️ No analysis images generated", "yellow")
        except Exception as e:
            print_substep(f"⚠️ Failed to generate analysis images: {str(e)}", "yellow")
    
    bg_config = {
        "video": get_background_config("video"),
        "audio": get_background_config("audio"),
    }
    download_background_video(bg_config["video"])
    download_background_audio(bg_config["audio"])
    chop_background(bg_config, length, reddit_object)
    make_final_video(number_of_comments, length, reddit_object, bg_config)


def run_many(times) -> None:
    for x in range(1, times + 1):
        print_step(
            f'on the {x}{("th", "st", "nd", "rd", "th", "th", "th", "th", "th", "th")[x % 10]} iteration of {times}'
        )  # correct 1st 2nd 3rd 4th 5th....
        main()
        Popen("cls" if name == "nt" else "clear", shell=True).wait()


def shutdown() -> NoReturn:
    if "redditid" in globals():
        print_markdown("## Clearing temp files")
        cleanup(redditid)

    print("Exiting...")
    sys.exit()


if __name__ == "__main__":
    if sys.version_info.major != 3 or sys.version_info.minor < 10:
        print(
            "Hey! This program requires Python 3.10 or newer. You're using Python {}.{}. Please install Python 3.10+ and try again.".format(sys.version_info.major, sys.version_info.minor)
        )
        sys.exit()
    ffmpeg_install()
    directory = Path().absolute()
    config = settings.check_toml(
        f"{directory}/utils/.config.template.toml", f"{directory}/config.toml"
    )
    config is False and sys.exit()

    if (
        not settings.config["settings"]["tts"]["tiktok_sessionid"]
        or settings.config["settings"]["tts"]["tiktok_sessionid"] == ""
    ) and config["settings"]["tts"]["voice_choice"] == "tiktok":
        print_substep(
            "TikTok voice requires a sessionid! Check our documentation on how to obtain one.",
            "bold red",
        )
        sys.exit()
    try:
        if config["reddit"]["thread"]["post_id"]:
            for index, post_id in enumerate(config["reddit"]["thread"]["post_id"].split("+")):
                index += 1
                print_step(
                    f'on the {index}{("st" if index % 10 == 1 else ("nd" if index % 10 == 2 else ("rd" if index % 10 == 3 else "th")))} post of {len(config["reddit"]["thread"]["post_id"].split("+"))}'
                )
                main(post_id)
                Popen("cls" if name == "nt" else "clear", shell=True).wait()
        elif config["settings"]["times_to_run"]:
            run_many(config["settings"]["times_to_run"])
        else:
            main()
    except KeyboardInterrupt:
        shutdown()
    except ResponseException:
        print_markdown("## Invalid credentials")
        print_markdown("Please check your credentials in the config.toml file")
        shutdown()
    except Exception as err:
        config["settings"]["tts"]["tiktok_sessionid"] = "REDACTED"
        config["settings"]["tts"]["elevenlabs_api_key"] = "REDACTED"
        print_step(
            f"Sorry, something went wrong with this version! Try again, and feel free to report this issue at GitHub or the Discord community.\n"
            f"Version: {__VERSION__} \n"
            f"Error: {err} \n"
            f'Config: {config["settings"]}'
        )
        raise err
