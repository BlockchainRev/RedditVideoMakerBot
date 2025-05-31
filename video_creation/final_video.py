import multiprocessing
import os
import re
import subprocess
import json
import tempfile
import textwrap
import threading
import time
from os.path import exists  # Needs to be imported specifically
from pathlib import Path
from typing import Dict, Final, Tuple

import ffmpeg
import translators
from PIL import Image, ImageDraw, ImageFont
from rich.console import Console
from rich.progress import track

from utils import settings
from utils.cleanup import cleanup
from utils.console import print_step, print_substep
from utils.fonts import getheight
from utils.thumbnail import create_thumbnail
from utils.videos import save_data

console = Console()


class ProgressFfmpeg(threading.Thread):
    def __init__(self, vid_duration_seconds, progress_update_callback):
        threading.Thread.__init__(self, name="ProgressFfmpeg")
        self.stop_event = threading.Event()
        self.output_file = tempfile.NamedTemporaryFile(mode="w+", delete=False)
        self.vid_duration_seconds = vid_duration_seconds
        self.progress_update_callback = progress_update_callback

    def run(self):
        while not self.stop_event.is_set():
            latest_progress = self.get_latest_ms_progress()
            if latest_progress is not None:
                completed_percent = latest_progress / self.vid_duration_seconds
                self.progress_update_callback(completed_percent)
            time.sleep(1)

    def get_latest_ms_progress(self):
        lines = self.output_file.readlines()

        if lines:
            for line in lines:
                if "out_time_ms" in line:
                    out_time_ms_str = line.split("=")[1].strip()
                    if out_time_ms_str.isnumeric():
                        return float(out_time_ms_str) / 1000000.0
                    else:
                        # Handle the case when "N/A" is encountered
                        return None
        return None

    def stop(self):
        self.stop_event.set()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args, **kwargs):
        self.stop()


def name_normalize(name: str) -> str:
    name = re.sub(r'[?\\"%*:|<>]', "", name)
    name = re.sub(r"( [w,W]\s?\/\s?[o,O,0])", r" without", name)
    name = re.sub(r"( [w,W]\s?\/)", r" with", name)
    name = re.sub(r"(\d+)\s?\/\s?(\d+)", r"\1 of \2", name)
    name = re.sub(r"(\w+)\s?\/\s?(\w+)", r"\1 or \2", name)
    name = re.sub(r"\/", r"", name)

    lang = settings.config["reddit"]["thread"]["post_lang"]
    if lang:
        print_substep("Translating filename...")
        translated_name = translators.translate_text(name, translator="google", to_language=lang)
        return translated_name
    else:
        return name


def prepare_background(reddit_id: str, W: int, H: int) -> str:
    # For now, just return the background video as-is
    # The final composition will handle scaling and overlays
    background_path = f"assets/temp/{reddit_id}/background.mp4"
    return background_path


def create_fancy_thumbnail(image, text, text_color, padding, wrap=35):
    print_step(f"Creating fancy thumbnail for: {text}")
    font_title_size = 47
    font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), font_title_size)
    image_width, image_height = image.size
    lines = textwrap.wrap(text, width=wrap)
    y = (
        (image_height / 2)
        - (((getheight(font, text) + (len(lines) * padding) / len(lines)) * len(lines)) / 2)
        + 30
    )
    draw = ImageDraw.Draw(image)

    username_font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), 30)
    draw.text(
        (205, 825),
        settings.config["settings"]["channel_name"],
        font=username_font,
        fill=text_color,
        align="left",
    )

    if len(lines) == 3:
        lines = textwrap.wrap(text, width=wrap + 10)
        font_title_size = 40
        font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), font_title_size)
        y = (
            (image_height / 2)
            - (((getheight(font, text) + (len(lines) * padding) / len(lines)) * len(lines)) / 2)
            + 35
        )
    elif len(lines) == 4:
        lines = textwrap.wrap(text, width=wrap + 10)
        font_title_size = 35
        font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), font_title_size)
        y = (
            (image_height / 2)
            - (((getheight(font, text) + (len(lines) * padding) / len(lines)) * len(lines)) / 2)
            + 40
        )
    elif len(lines) > 4:
        lines = textwrap.wrap(text, width=wrap + 10)
        font_title_size = 30
        font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), font_title_size)
        y = (
            (image_height / 2)
            - (((getheight(font, text) + (len(lines) * padding) / len(lines)) * len(lines)) / 2)
            + 30
        )

    for line in lines:
        draw.text((120, y), line, font=font, fill=text_color, align="left")
        y += getheight(font, line) + padding

    return image


def merge_background_audio(audio: ffmpeg, reddit_id: str):
    """Gather an audio and merge with assets/backgrounds/background.mp3
    Args:
        audio (ffmpeg): The TTS final audio but without background.
        reddit_id (str): The ID of subreddit
    """
    background_audio_volume = settings.config["settings"]["background"]["background_audio_volume"]
    if background_audio_volume == 0:
        return audio  # Return the original audio
    else:
        # sets volume to config
        bg_audio = ffmpeg.input(f"assets/temp/{reddit_id}/background.mp3").filter(
            "volume",
            background_audio_volume,
        )
        # Merges audio and background_audio
        merged_audio = ffmpeg.filter([audio, bg_audio], "amix", duration="longest")
        return merged_audio  # Return merged audio


def make_final_video(
    number_of_clips: int,
    length: int,
    reddit_obj: dict,
    background_config: Dict[str, Tuple],
):
    """Gathers audio clips, gathers all screenshots, stitches them together and saves the final video to assets/temp
    Args:
        number_of_clips (int): Index to end at when going through the screenshots'
        length (int): Length of the video
        reddit_obj (dict): The reddit object that contains the posts to read.
        background_config (Tuple[str, str, str, Any]): The background config to use.
    """
    # settings values
    W: Final[int] = int(settings.config["settings"]["resolution_w"])
    H: Final[int] = int(settings.config["settings"]["resolution_h"])

    opacity = settings.config["settings"]["opacity"]

    reddit_id = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])

    allowOnlyTTSFolder: bool = (
        settings.config["settings"]["background"]["enable_extra_audio"]
        and settings.config["settings"]["background"]["background_audio_volume"] != 0
    )

    print_step("Creating the final video 🎥")

    # Get the background video path
    background_video_path = prepare_background(reddit_id, W=W, H=H)
    
    # Create properly cropped background instead of stretching
    
    # Probe the background video to get its dimensions
    try:
        probe_cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams',
            background_video_path
        ]
        
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            video_info = json.loads(result.stdout)
            video_stream = next(s for s in video_info['streams'] if s['codec_type'] == 'video')
            orig_width = int(video_stream['width'])
            orig_height = int(video_stream['height'])
            
            # Calculate proper scaling to maintain aspect ratio while filling target resolution
            scale_factor = max(W / orig_width, H / orig_height)  # Use max to ensure full coverage
            new_width = int(orig_width * scale_factor)
            new_height = int(orig_height * scale_factor)
            
            # Calculate crop offsets to center the image
            crop_x = (new_width - W) // 2 if new_width > W else 0
            crop_y = (new_height - H) // 2 if new_height > H else 0
            
            print_substep(f"📐 Background scaling: {orig_width}x{orig_height} → {new_width}x{new_height} → crop to {W}x{H}")
            
            # Apply the scale and crop filter to the background
            background_clip = ffmpeg.input(background_video_path).filter(
                'scale', new_width, new_height
            ).filter(
                'crop', W, H, crop_x, crop_y
            )
        else:
            print_substep("⚠️ Could not probe background video, using simple scale", "yellow")
            # Fallback to simple scaling if probe fails
            background_clip = ffmpeg.input(background_video_path).filter("scale", W, H)
    except Exception as e:
        print_substep(f"⚠️ Error with background cropping ({str(e)}), using simple scale", "yellow")
        # Fallback to simple scaling if anything goes wrong
        background_clip = ffmpeg.input(background_video_path).filter("scale", W, H)

    # Gather all audio clips
    audio_clips = list()
    
    # Calculate actual number of content clips based on images, not all audio files
    actual_content_clips = 0
    if settings.config["settings"]["storymode"] and settings.config["settings"]["storymodemethod"] == 1:
        i = 0
        while os.path.exists(f"assets/temp/{reddit_id}/png/content_{i}.png"):
            actual_content_clips += 1
            i += 1
    
    if actual_content_clips == 0 and settings.config["settings"]["storymode"] == "false":
        print(
            "No audio clips to gather. Please use a different TTS or post."
        )  # This is to fix the TypeError: unsupported operand type(s) for +: 'int' and 'NoneType'
        exit()

    if settings.config["settings"]["storymode"]:
        if settings.config["settings"]["storymodemethod"] == 0:
            audio_clips = [ffmpeg.input(f"assets/temp/{reddit_id}/mp3/title.mp3")]
            audio_clips.insert(1, ffmpeg.input(f"assets/temp/{reddit_id}/mp3/postaudio.mp3"))
        elif settings.config["settings"]["storymodemethod"] == 1:
            # Only collect audio clips for title + the content images we have
            audio_clips = [ffmpeg.input(f"assets/temp/{reddit_id}/mp3/title.mp3")]
            for i in range(actual_content_clips):
                audio_clips.append(ffmpeg.input(f"assets/temp/{reddit_id}/mp3/postaudio-{i}.mp3"))
                
        # 🌙 ADD DREAM ANALYSIS AUDIO CLIPS
        if reddit_obj.get("dream_analysis"):
            print_substep("Adding dream analysis audio to final video...", "blue")
            analysis_audio_files = []
            
            # Check for chunked analysis audio files
            chunk_idx = 0
            while True:
                chunk_name = f"analysis_chunk_{chunk_idx}"
                analysis_file = f"assets/temp/{reddit_id}/mp3/{chunk_name}.mp3"
                
                if os.path.exists(analysis_file):
                    audio_clips.append(ffmpeg.input(analysis_file))
                    analysis_audio_files.append(chunk_name)
                    chunk_idx += 1
                else:
                    break  # No more chunks found
                    
            if analysis_audio_files:
                print_substep(f"✅ Added {len(analysis_audio_files)} analysis audio chunks: {', '.join(analysis_audio_files)}", "green")
            else:
                print_substep("⚠️ No analysis audio files found", "yellow")

    else:
        audio_clips = [
            ffmpeg.input(f"assets/temp/{reddit_id}/mp3/{i}.mp3") for i in range(number_of_clips)
        ]
        audio_clips.insert(0, ffmpeg.input(f"assets/temp/{reddit_id}/mp3/title.mp3"))

        audio_clips_durations = [
            float(ffmpeg.probe(f"assets/temp/{reddit_id}/mp3/{i}.mp3")["format"]["duration"])
            for i in range(number_of_clips)
        ]
        audio_clips_durations.insert(
            0,
            float(ffmpeg.probe(f"assets/temp/{reddit_id}/mp3/title.mp3")["format"]["duration"]),
        )

        for i in range(actual_content_clips):
            audio_clips_durations.append(
                float(ffmpeg.probe(f"assets/temp/{reddit_id}/mp3/postaudio-{i}.mp3")["format"]["duration"])
            )
        
        console.log(f"[bold green] Video Will Be: {sum(audio_clips_durations)} Seconds Long")

    audio_concat = ffmpeg.concat(*audio_clips, a=1, v=0)
    ffmpeg.output(
        audio_concat, f"assets/temp/{reddit_id}/audio.mp3", **{"b:a": "192k"}
    ).overwrite_output().run(quiet=True)

    screenshot_width = int((W * 45) // 100)
    audio = ffmpeg.input(f"assets/temp/{reddit_id}/audio.mp3")
    final_audio = merge_background_audio(audio, reddit_id)

    image_clips = list()

    Path(f"assets/temp/{reddit_id}/png").mkdir(parents=True, exist_ok=True)

    # Use the title image already created by our dream generator
    image_clips.insert(
        0,
        ffmpeg.input(f"assets/temp/{reddit_id}/png/title.png")["v"].filter(
            "scale", W, H
        ),
    )

    current_time = 0
    if settings.config["settings"]["storymode"]:
        # Only get audio durations for the images we actually have (title + content images)
        audio_clips_durations = [
            float(ffmpeg.probe(f"assets/temp/{reddit_id}/mp3/title.mp3")["format"]["duration"])
        ]
        for i in range(actual_content_clips):
            audio_clips_durations.append(
                float(ffmpeg.probe(f"assets/temp/{reddit_id}/mp3/postaudio-{i}.mp3")["format"]["duration"])
            )
        
        if settings.config["settings"]["storymodemethod"] == 0:
            image_clips.insert(
                1,
                ffmpeg.input(f"assets/temp/{reddit_id}/png/story_content.png").filter(
                    "scale", W*.5, H*.5
                ),
            )
            background_clip = background_clip.overlay(
                image_clips[0],
                enable=f"between(t,{current_time},{current_time + audio_clips_durations[0]})",
                x="(main_w-overlay_w)/2",
                y="(main_h-overlay_h)/2",
            )
            current_time += audio_clips_durations[0]
        elif settings.config["settings"]["storymodemethod"] == 1:
            # Show title image first
            background_clip = background_clip.overlay(
                image_clips[0],  # Title image
                enable=f"between(t,{current_time},{current_time + audio_clips_durations[0]})",
                x="(main_w-overlay_w)/2",
                y="(main_h-overlay_h)/2",
            )
            current_time += audio_clips_durations[0]
            
            for i in track(range(actual_content_clips), "Collecting the image files..."):
                image_clips.append(
                    ffmpeg.input(f"assets/temp/{reddit_id}/png/content_{i}.png")["v"].filter(
                        "scale", W*.75, H*.5
                    )
                )
                background_clip = background_clip.overlay(
                    image_clips[i + 1],  # +1 because index 0 is title
                    enable=f"between(t,{current_time},{current_time + audio_clips_durations[i + 1]})",
                    x="(main_w-overlay_w)/2",
                    y="(main_h-overlay_h)/2",
                )
                current_time += audio_clips_durations[i + 1]
                
            # 🌙 ADD DREAM ANALYSIS IMAGES TO VIDEO TIMELINE
            if reddit_obj.get("dream_analysis"):
                print_substep("Adding dream analysis images to video timeline...", "blue")
                analysis_image_count = 0
                
                # Add analysis images with their corresponding audio using chunked structure
                chunk_idx = 0
                while True:
                    chunk_name = f"analysis_chunk_{chunk_idx}"
                    image_file = f"assets/temp/{reddit_id}/png/{chunk_name}.png"
                    audio_file = f"assets/temp/{reddit_id}/mp3/{chunk_name}.mp3"
                    
                    if os.path.exists(image_file) and os.path.exists(audio_file):
                        # Get audio duration for this analysis chunk
                        analysis_duration = float(ffmpeg.probe(audio_file)["format"]["duration"])
                        
                        # Add image clip
                        analysis_image_clip = ffmpeg.input(image_file)["v"].filter(
                            "scale", W*.5, H*.5
                        )
                        
                        # Overlay the analysis image during its audio duration
                        background_clip = background_clip.overlay(
                            analysis_image_clip,
                            enable=f"between(t,{current_time},{current_time + analysis_duration})",
                            x="(main_w-overlay_w)/2",
                            y="(main_h-overlay_h)/2",
                        )
                        
                        current_time += analysis_duration
                        analysis_image_count += 1
                        chunk_idx += 1
                    else:
                        break  # No more chunks found
                        
                if analysis_image_count > 0:
                    print_substep(f"✅ Added {analysis_image_count} analysis images to video timeline", "green")
                else:
                    print_substep("⚠️ No analysis images found for video timeline", "yellow")
    else:
        for i in range(0, number_of_clips + 1):
            image_clips.append(
                ffmpeg.input(f"assets/temp/{reddit_id}/png/comment_{i}.png")["v"].filter(
                    "scale", W*.5, H*.5
                )
            )
            image_overlay = image_clips[i].filter("colorchannelmixer", aa=opacity)
            assert (
                audio_clips_durations is not None
            ), "Please make a GitHub issue if you see this. Ping @JasonLovesDoggo on GitHub."
            background_clip = background_clip.overlay(
                image_overlay,
                enable=f"between(t,{current_time},{current_time + audio_clips_durations[i]})",
                x="(main_w-overlay_w)/2",
                y="(main_h-overlay_h)/2",
            )
            current_time += audio_clips_durations[i]

    title = re.sub(r"[^\w\s-]", "", reddit_obj["thread_title"])
    idx = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])
    title_thumb = reddit_obj["thread_title"]

    filename = f"{name_normalize(title)[:251]}"
    subreddit = settings.config["reddit"]["thread"]["subreddit"]

    if not exists(f"./results/{subreddit}"):
        print_substep("The 'results' folder could not be found so it was automatically created.")
        os.makedirs(f"./results/{subreddit}")

    if not exists(f"./results/{subreddit}/OnlyTTS") and allowOnlyTTSFolder:
        print_substep("The 'OnlyTTS' folder could not be found so it was automatically created.")
        os.makedirs(f"./results/{subreddit}/OnlyTTS")

    # create a thumbnail for the video
    settingsbackground = settings.config["settings"]["background"]

    if settingsbackground["background_thumbnail"]:
        if not exists(f"./results/{subreddit}/thumbnails"):
            print_substep(
                "The 'results/thumbnails' folder could not be found so it was automatically created."
            )
            os.makedirs(f"./results/{subreddit}/thumbnails")
        # get the first file with the .png extension from assets/backgrounds and use it as a background for the thumbnail
        first_image = next(
            (file for file in os.listdir("assets/backgrounds") if file.endswith(".png")),
            None,
        )
        if first_image is None:
            print_substep("No png files found in assets/backgrounds", "red")

        else:
            font_family = settingsbackground["background_thumbnail_font_family"]
            font_size = settingsbackground["background_thumbnail_font_size"]
            font_color = settingsbackground["background_thumbnail_font_color"]
            thumbnail = Image.open(f"assets/backgrounds/{first_image}")
            width, height = thumbnail.size
            thumbnailSave = create_thumbnail(
                thumbnail,
                font_family,
                font_size,
                font_color,
                width,
                height,
                title_thumb,
            )
            thumbnailSave.save(f"./assets/temp/{reddit_id}/thumbnail.png")
            print_substep(f"Thumbnail - Building Thumbnail in assets/temp/{reddit_id}/thumbnail.png")

    text = f"Background by {background_config['video'][2]}"
    background_clip = ffmpeg.drawtext(
        background_clip,
        text=text,
        x=f"(w-text_w)",
        y=f"(h-text_h)",
        fontsize=5,
        fontcolor="White",
        fontfile=os.path.join("fonts", "Roboto-Regular.ttf"),
    )
    print_step("Rendering the video 🎥")
    from tqdm import tqdm

    pbar = tqdm(total=100, desc="Progress: ", bar_format="{l_bar}{bar}", unit=" %")

    def on_update_example(progress) -> None:
        status = round(progress * 100, 2)
        old_percentage = pbar.n
        pbar.update(status - old_percentage)

    defaultPath = f"results/{subreddit}"
    actual_length = sum(audio_clips_durations)
    
    # Simplified approach: create video step by step instead of complex filter chain
    print_substep("🎬 Creating simplified video composition...")
    
    # Step 1: Create a simple video with just background and audio
    try:
        # Get the total audio duration
        audio_duration = sum(audio_clips_durations)
        
        # Create background video with proper duration
        background_video = ffmpeg.input(f"assets/temp/{reddit_id}/background.mp4").video
        background_audio_input = ffmpeg.input(f"assets/temp/{reddit_id}/background.mp3").audio
        main_audio = ffmpeg.input(f"assets/temp/{reddit_id}/audio.mp3").audio
        
        # Mix the audio
        if settings.config["settings"]["background"]["background_audio_volume"] > 0:
            bg_audio_volume = settings.config["settings"]["background"]["background_audio_volume"]
            mixed_audio = ffmpeg.filter([main_audio, background_audio_input.filter("volume", bg_audio_volume)], "amix", duration="longest")
        else:
            mixed_audio = main_audio
        
        # Apply proper scaling and cropping to background like above
        try:
            probe_cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams',
                f"assets/temp/{reddit_id}/background.mp4"
            ]
            
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                video_info = json.loads(result.stdout)
                video_stream = next(s for s in video_info['streams'] if s['codec_type'] == 'video')
                orig_width = int(video_stream['width'])
                orig_height = int(video_stream['height'])
                
                # Calculate proper scaling to maintain aspect ratio while filling target resolution
                scale_factor = max(W / orig_width, H / orig_height)  # Use max to ensure full coverage
                new_width = int(orig_width * scale_factor)
                new_height = int(orig_height * scale_factor)
                
                # Calculate crop offsets to center the image
                crop_x = (new_width - W) // 2 if new_width > W else 0
                crop_y = (new_height - H) // 2 if new_height > H else 0
                
                # Apply the scale and crop filter then loop for duration
                scaled_background = background_video.filter(
                    'scale', new_width, new_height
                ).filter(
                    'crop', W, H, crop_x, crop_y
                ).filter("loop", loop=-1, size=int(audio_duration * 25), start=0)
            else:
                # Fallback to simple scaling if probe fails
                scaled_background = background_video.filter("scale", W, H).filter("loop", loop=-1, size=int(audio_duration * 25), start=0)
        except Exception as e:
            # Fallback to simple scaling if anything goes wrong
            scaled_background = background_video.filter("scale", W, H).filter("loop", loop=-1, size=int(audio_duration * 25), start=0)
        
        # Add text overlay for credit
        credit_text = f"Background by {background_config['video'][2]}"
        final_video = scaled_background.drawtext(
            text=credit_text,
            x=f"(w-text_w)",
            y=f"(h-text_h)", 
            fontsize=5,
            fontcolor="White",
            fontfile=os.path.join("fonts", "Roboto-Regular.ttf")
        )
        
        # Create final output
        path = defaultPath + f"/{filename}"
        path = (path[:251] + ".mp4")
        
        print_substep(f"🎥 Rendering final video: {filename}")
        
        output = ffmpeg.output(
            final_video,
            mixed_audio, 
            path,
            vcodec="libx264",
            acodec="aac",
            pix_fmt="yuv420p",
            t=audio_duration,
            **{"b:v": "2M", "b:a": "128k"}
        ).overwrite_output()
        
        output.run(quiet=True)
        print_substep("✅ Basic video created successfully!")
        
        # Now let's try to add the images as overlays in a simpler way
        if os.path.exists(path):
            print_substep("🖼️ Adding image overlays...")
            
            # Create a version with image overlays
            path_with_images = defaultPath + f"/{filename.replace('.mp4', '_with_images.mp4')}"
            
            # Input the basic video we just created
            base_video = ffmpeg.input(path).video
            base_audio = ffmpeg.input(path).audio
            
            current_time = 0
            result_video = base_video
            
            # Add title image
            if os.path.exists(f"assets/temp/{reddit_id}/png/title.png"):
                title_img = ffmpeg.input(f"assets/temp/{reddit_id}/png/title.png").video.filter("scale", W, H)
                result_video = result_video.overlay(
                    title_img,
                    x="(main_w-overlay_w)/2",
                    y="(main_h-overlay_h)/2",
                    enable=f"between(t,{current_time},{current_time + audio_clips_durations[0]})"
                )
                current_time += audio_clips_durations[0]
            
            # Add content images
            for i in range(actual_content_clips):
                if os.path.exists(f"assets/temp/{reddit_id}/png/content_{i}.png"):
                    content_img = ffmpeg.input(f"assets/temp/{reddit_id}/png/content_{i}.png").video.filter("scale", W, H)
                    result_video = result_video.overlay(
                        content_img,
                        x="(main_w-overlay_w)/2", 
                        y="(main_h-overlay_h)/2",
                        enable=f"between(t,{current_time},{current_time + audio_clips_durations[i + 1]})"
                    )
                    current_time += audio_clips_durations[i + 1]
            
            # Output final video with images
            final_output = ffmpeg.output(
                result_video,
                base_audio,
                path_with_images,
                vcodec="libx264", 
                acodec="aac",
                pix_fmt="yuv420p",
                **{"b:v": "2M", "b:a": "128k"}
            ).overwrite_output()
            
            final_output.run(quiet=True)
            print_substep("✅ Final video with images created successfully!")
            
    except Exception as e:
        print_substep(f"❌ Simplified approach failed: {str(e)}")
        print_substep("🔄 Trying basic audio-only approach...")
        
        # Absolute fallback: just create audio file
        try:
            basic_path = defaultPath + f"/audio_only_{filename.replace('.mp4', '.mp3')}"
            ffmpeg.output(final_audio, basic_path).overwrite_output().run(quiet=True)
            print_substep("✅ Audio-only version created!")
        except Exception as audio_e:
            print_substep(f"❌ Audio creation failed: {str(audio_e)}")

    # Continue with the original complex approach as backup
    with ProgressFfmpeg(actual_length, on_update_example) as progress:
        path = defaultPath + f"/{filename}"
        path = (
            path[:251] + ".mp4"
        )  # Prevent a error by limiting the path length, do not change this.
        try:
            ffmpeg.output(
                background_clip,
                final_audio,
                path,
                f="mp4",
                **{
                    "c:v": "h264",
                    "b:v": "20M",
                    "b:a": "192k",
                    "threads": multiprocessing.cpu_count(),
                },
            ).overwrite_output().global_args("-progress", progress.output_file.name).run(
                quiet=True,
                overwrite_output=True,
                capture_stdout=False,
                capture_stderr=False,
            )
        except ffmpeg.Error as e:
            print(e.stderr.decode("utf8"))
            exit(1)
    old_percentage = pbar.n
    pbar.update(100 - old_percentage)
    if allowOnlyTTSFolder:
        path = defaultPath + f"/OnlyTTS/{filename}"
        path = (
            path[:251] + ".mp4"
        )  # Prevent a error by limiting the path length, do not change this.
        print_step("Rendering the Only TTS Video 🎥")
        with ProgressFfmpeg(actual_length, on_update_example) as progress:
            try:
                ffmpeg.output(
                    background_clip,
                    audio,
                    path,
                    f="mp4",
                    **{
                        "c:v": "h264",
                        "b:v": "20M",
                        "b:a": "192k",
                        "threads": multiprocessing.cpu_count(),
                    },
                ).overwrite_output().global_args("-progress", progress.output_file.name).run(
                    quiet=True,
                    overwrite_output=True,
                    capture_stdout=False,
                    capture_stderr=False,
                )
            except ffmpeg.Error as e:
                print(e.stderr.decode("utf8"))
                exit(1)

        old_percentage = pbar.n
        pbar.update(100 - old_percentage)
    pbar.close()
    save_data(subreddit, filename + ".mp4", title, idx, background_config["video"][2])
    print_step("Removing temporary files 🗑")
    cleanups = cleanup(reddit_id)
    print_substep(f"Removed {cleanups} temporary files 🗑")
    print_step("Done! 🎉 The video is in the results folder 📁")
