import cv2
import numpy as np
import subprocess
import shutil
from pathlib import Path

from pathlib import Path

# Check for ffmpeg availability
FFMPEG = shutil.which("ffmpeg")

def run(cmd: list):
    """Run a command and print it for visibility."""
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

def create_solid_color_video(color, output_filename, width=500, height=500, duration=5, fps=30):
    """
    Create a video with a solid color directly in H.264 format.
    
    Args:
        color (tuple): RGB color values (R, G, B) where each value is 0-255
        output_filename (str): Name of the output video file
        width (int): Width of the video in pixels
        height (int): Height of the video in pixels
        duration (int): Duration of the video in seconds
        fps (int): Frames per second
    """
    if FFMPEG is None:
        print("Error: ffmpeg not found. Please install ffmpeg and ensure it's on PATH.")
        print("This script now requires ffmpeg to create H.264 videos directly.")
        return None
    
    print(f"Creating H.264 video with {color} color...")
    print(f"Video size: {width}x{height}")
    print(f"Duration: {duration} seconds")
    
    # Convert RGB to hex format for ffmpeg
    hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
    
    # Calculate inverted color for text (255 - each RGB component)
    inverted_color = (255 - color[0], 255 - color[1], 255 - color[2])
    hex_inverted = f"#{inverted_color[0]:02x}{inverted_color[1]:02x}{inverted_color[2]:02x}"
    
    print(f"Background color: {hex_color}")
    print(f"Text color (inverted): {hex_inverted}")
    
    # Create H.264 video with frame numbers using ffmpeg
    cmd = [
        FFMPEG, '-y',
        '-f', 'lavfi',
        '-i', f'color=c={hex_color}:size={width}x{height}:duration={duration}:rate={fps}',
        '-vf', f'drawtext=text=%{{frame_num}}:fontcolor={hex_inverted}:fontsize=40:x=(w-text_w)/2:y=(h-text_h)/2',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.0',
        '-movflags', '+faststart',
        output_filename
    ]
    
    run(cmd)
    print(f"H.264 video saved as: {output_filename}")
    return output_filename

def parse_color(color_str):
    """
    Parse color string in different formats:
    - RGB: "255,0,0" or "255 0 0"
    - Named colors: "red", "blue", "green", etc.
    """
    # Named colors mapping
    named_colors = {
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'orange': (255, 165, 0),
        'purple': (128, 0, 128),
        'pink': (255, 192, 203),
        'brown': (165, 42, 42),
        'gray': (128, 128, 128),
        'grey': (128, 128, 128)
    }
    
    # Check if it's a named color
    if color_str.lower() in named_colors:
        return named_colors[color_str.lower()]
    
    # Try to parse as RGB values
    try:
        # Replace commas with spaces and split
        rgb_str = color_str.replace(',', ' ')
        rgb_values = [int(x.strip()) for x in rgb_str.split()]
        
        if len(rgb_values) != 3:
            raise ValueError("RGB must have exactly 3 values")
        
        # Validate range
        for val in rgb_values:
            if not 0 <= val <= 255:
                raise ValueError("RGB values must be between 0 and 255")
        
        return tuple(rgb_values)
    
    except ValueError as e:
        raise ValueError(f"Invalid color format: {color_str}. Use named colors (e.g., 'red') or RGB format (e.g., '255,0,0')")

if __name__ == "__main__":
    # Simple example usage - create a red video
    COLOR = "green"  # You can change this to any color
    
    try:
        # Parse the color
        color = parse_color(COLOR)
        
        # Create H.264 video directly
        h264_video = f"{COLOR}.mp4"
        result = create_solid_color_video(
            color=color,
            output_filename=h264_video,
            width=500,
            height=500,
            duration=50,
            fps=30
        )
        
        if result:
            print(f"\n✅ Created browser-compatible H.264 video: {result}")
        
    except ValueError as e:
        print(f"Error: {e}")
        print("\nTo use different colors, modify the COLOR variable in the script.")
        print("Supported colors: red, blue, green, yellow, cyan, magenta, white, black, etc.")
        print("Or use RGB format like: '255,0,0' for red")
    except subprocess.CalledProcessError as e:
        print(f"Error during video creation: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
