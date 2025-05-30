#!/usr/bin/env python3
import subprocess
import os
from pathlib import Path

def create_easy_sync_video():
    """Create a portrait video with larger text chunks for easy subtitle syncing"""
    
    # Set up paths
    reddit_id = '1kyeswh'
    base_path = f'assets/temp/{reddit_id}'
    output_path = 'results/Dreams+DreamAnalysis+LucidDreaming/EASY_SYNC_VIDEO.mp4'
    
    # Portrait dimensions
    W, H = 1080, 1920
    
    # Make sure output directory exists
    os.makedirs('results/Dreams+DreamAnalysis+LucidDreaming', exist_ok=True)
    
    print(f"🎬 Creating EASY SYNC video with larger text chunks...")
    print(f"   Target resolution: {W}x{H} (Portrait)")
    print(f"   Background: Minecraft video")
    print(f"   Voice: Sam (ElevenLabs)")
    print(f"   Text: Large chunks, 3-5 seconds each - EASY TO SYNC!")
    
    try:
        # Step 1: Create perfect background
        print("📐 Step 1: Creating background...")
        
        bg_sync_path = f'{base_path}/bg_sync.mp4'
        
        # Get video dimensions and scale perfectly
        probe_cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams',
            'assets/backgrounds/video/bbswitzer-minecraft.mp4'
        ]
        
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Could not probe video dimensions")
            return False
        
        import json
        video_info = json.loads(result.stdout)
        video_stream = next(s for s in video_info['streams'] if s['codec_type'] == 'video')
        orig_width = int(video_stream['width'])
        orig_height = int(video_stream['height'])
        
        # Perfect scaling math
        scale_factor = H / orig_height
        new_width = int(orig_width * scale_factor)
        
        print(f"   Minecraft video: {orig_width}x{orig_height} → {new_width}x{H} → {W}x{H}")
        
        # Create perfect background
        scale_cmd = [
            'ffmpeg', '-y',
            '-i', 'assets/backgrounds/video/bbswitzer-minecraft.mp4',
            '-vf', f'scale={new_width}:{H},crop={W}:{H}:{(new_width-W)//2}:0',
            '-t', '16.2',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
            bg_sync_path
        ]
        
        result = subprocess.run(scale_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Background failed: {result.stderr}")
            return False
            
        print("✅ Background ready!")
        
        # Step 2: Calculate easy sync timing
        print("⏱️ Step 2: Calculating easy sync timing...")
        
        # Audio duration and segments  
        total_audio_duration = 16.2
        
        # Count large text chunks
        sync_chunks = []
        chunk_index = 0
        while os.path.exists(f'{base_path}/png/content_{chunk_index}.png'):
            sync_chunks.append(f'content_{chunk_index}.png')
            chunk_index += 1
            if chunk_index >= 5:  # Safety limit
                break
        
        print(f"   Found {len(sync_chunks)} large text chunks!")
        
        # Calculate timing for easy syncing - longer durations
        title_duration = 3.5
        content_duration = total_audio_duration - title_duration
        chunk_duration = content_duration / len(sync_chunks) if sync_chunks else 1
        
        print(f"   Title: {title_duration}s, Each chunk: {chunk_duration:.1f}s (EASY TO SYNC!)")
        
        # Step 3: Create video with easy sync overlays
        print("🎨 Step 3: Building video with easy sync timing...")
        
        current_video = bg_sync_path
        step_counter = 0
        
        # Add title first
        if os.path.exists(f'{base_path}/png/title.png'):
            step_counter += 1
            next_video = f'{base_path}/sync_step_{step_counter}.mp4'
            
            print(f"   Adding title (0s - {title_duration}s)")
            
            title_cmd = [
                'ffmpeg', '-y',
                '-i', current_video,
                '-i', f'{base_path}/png/title.png',
                '-filter_complex', f'[0:v][1:v]overlay=0:0:enable=between(t\\,0\\,{title_duration})',
                '-t', '16.2', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
                next_video
            ]
            
            result = subprocess.run(title_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Title overlay failed: {result.stderr}")
                return False
            
            # Clean up
            if current_video != bg_sync_path:
                os.remove(current_video)
            current_video = next_video
            
        # Add large chunks with easy timing
        for i, chunk_file in enumerate(sync_chunks):
            step_counter += 1
            next_video = f'{base_path}/sync_step_{step_counter}.mp4'
            
            # Calculate timing for this chunk - longer durations for easy syncing
            start_time = title_duration + (i * chunk_duration)
            end_time = title_duration + ((i + 1) * chunk_duration)
            
            print(f"   Adding chunk {i+1}/{len(sync_chunks)} ({start_time:.1f}s - {end_time:.1f}s) - {chunk_duration:.1f}s duration")
            
            overlay_cmd = [
                'ffmpeg', '-y',
                '-i', current_video,
                '-i', f'{base_path}/png/{chunk_file}',
                '-filter_complex', f'[0:v][1:v]overlay=0:0:enable=between(t\\,{start_time:.2f}\\,{end_time:.2f})',
                '-t', '16.2', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
                next_video
            ]
            
            result = subprocess.run(overlay_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Chunk {i+1} overlay failed: {result.stderr}")
                return False
            
            # Clean up previous
            if current_video != bg_sync_path:
                os.remove(current_video)
            current_video = next_video
        
        print("✅ All chunks added with easy sync timing!")
        
        # Step 4: Add Sam voice audio
        print("🎵 Step 4: Adding Sam voice...")
        
        final_cmd = [
            'ffmpeg', '-y',
            '-i', current_video,
            '-i', f'{base_path}/audio.mp3',
            '-map', '0:v', '-map', '1:a',
            '-c:v', 'libx264', '-c:a', 'aac',
            '-preset', 'medium', '-crf', '16',  # High quality
            '-pix_fmt', 'yuv420p',
            '-b:a', '256k',
            '-t', '16.2',
            output_path
        ]
        
        result = subprocess.run(final_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Audio failed: {result.stderr}")
            return False
        
        print('🎉 EASY SYNC video created!')
        print(f'📁 Video saved to: {output_path}')
        
        # Easy sync stats
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f'📊 File size: {file_size:.2f} MB')
            print(f'🎥 Resolution: {W}x{H} (Portrait)')
            print(f'⏱️  Duration: 16.2 seconds')
            print(f'🎮 Background: Minecraft')
            print(f'🎤 Voice: Sam (ElevenLabs)')
            print(f'📝 Text: {len(sync_chunks)} large chunks ({chunk_duration:.1f}s each)')
            print(f'✅ EASY TO SYNC IN POST!')
            print(f'💎 Quality: Premium encoding')
        
        # Cleanup
        temp_files = [bg_sync_path] + [f'{base_path}/sync_step_{i}.mp4' for i in range(1, step_counter + 1)]
        for temp_file in temp_files:
            if os.path.exists(temp_file) and temp_file != current_video:
                os.remove(temp_file)
        
        return True
        
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        return False

if __name__ == "__main__":
    create_easy_sync_video() 