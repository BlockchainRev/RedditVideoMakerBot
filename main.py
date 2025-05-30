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
from video_creation.background import (
    chop_background,
    download_background_audio,
    download_background_video,
    get_background_config,
)
from video_creation.final_video import make_final_video
from video_creation.text_image_generator import render_chunks_to_images, chunk_text_for_tts
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
    reddit_object = get_subreddit_threads(POST_ID)
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
    thread_post_text = reddit_object['thread_post']
    if isinstance(thread_post_text, list):
        thread_post_text = " ".join(thread_post_text)
    
    post_chunks = chunk_text_for_tts(thread_post_text)
    if post_chunks:
        # Save current files in dir to avoid renaming them
        # existing_files_before_render = set(os.listdir(image_dir)) # No longer needed with direct paths
        post_image_paths = render_chunks_to_images(chunks=post_chunks, out_dir=image_dir) # Render post content
        
        # Rename post content images to content_0.png, content_1.png, etc.
        for idx, source_path in enumerate(post_image_paths):
            target_path = image_dir / f"content_{idx}.png"
            if source_path.exists() and source_path != target_path and source_path.name != "title.png":
                # If target_path (e.g. content_0.png) exists from a previous run or title processing, remove it
                if target_path.exists():
                    target_path.unlink()
                source_path.rename(target_path)
    
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
