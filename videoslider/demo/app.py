import gradio as gr
from gradio_videoslider import VideoSlider
import os
import tempfile
import subprocess

def invert_video(input_video_path):
    """
    Inverts the colors of a video using FFmpeg and returns the path to the inverted video
    """
    print(f"invert_video called with: {input_video_path}")
    
    if not input_video_path:
        print("No input video path provided")
        return None
    
    # Create a temporary file for the output
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "inverted_video.mp4")
    print(f"Output path will be: {output_path}")
    
    try:
        # FFmpeg command to invert video colors and encode in H.264
        cmd = [
            'ffmpeg',
            '-i', input_video_path,
            '-vf', 'negate',  # Video filter to invert colors
            '-c:v', 'libx264',  # H.264 codec
            '-preset', 'fast',  # Encoding preset for speed
            '-crf', '23',  # Quality setting (lower = better quality)
            '-c:a', 'aac',  # Audio codec
            '-y',  # Overwrite output file
            output_path
        ]
        
        print(f"Running FFmpeg command: {' '.join(cmd)}")
        
        # Run FFmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        print(f"FFmpeg return code: {result.returncode}")
        if result.stdout:
            print(f"FFmpeg stdout: {result.stdout}")
        if result.stderr:
            print(f"FFmpeg stderr: {result.stderr}")
        
        if result.returncode == 0 and os.path.exists(output_path):
            print(f"Video inversion successful! Output: {output_path}")
            return output_path
        else:
            print(f"FFmpeg failed or output file doesn't exist")
            return None
            
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        return None

def fn(video_tuple):
    print(f"fn called with: {video_tuple}")
    print(f"Type of video_tuple: {type(video_tuple)}")
    
    if not video_tuple:
        print("No video_tuple provided")
        return video_tuple
    
    # Handle different input formats
    original_video = None
    if isinstance(video_tuple, (list, tuple)) and len(video_tuple) > 0:
        original_video = video_tuple[0]
    elif isinstance(video_tuple, str):
        original_video = video_tuple
    
    print(f"Original video path: {original_video}")
    
    if not original_video:
        print("No original video found")
        return video_tuple
    
    print("Starting video inversion...")
    inverted_video = invert_video(original_video)
    print(f"Inverted video result: {inverted_video}")
    
    if inverted_video:
        result = (original_video, inverted_video)
        print(f"Returning result: {result}")
        return result
    else:
        # If inversion fails, return original for both sides
        result = (original_video, original_video)
        print(f"Inversion failed, returning: {result}")
        return result

with gr.Blocks() as demo:
    with gr.Group():
        video_slider = VideoSlider(
            label="Invert video", 
            height=400,
            max_height=400
        )
        video_slider.upload(fn, inputs=video_slider, outputs=video_slider)

if __name__ == "__main__":
    demo.launch()
