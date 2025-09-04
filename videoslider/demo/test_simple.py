import gradio as gr
from gradio_videoslider import VideoSlider
import os

# Simple test with existing videos
video1_path = "green.mp4" if os.path.exists("green.mp4") else None
video2_path = "red.mp4" if os.path.exists("red.mp4") else None

def simple_fn(video_tuple):
    print(f"simple_fn called with: {video_tuple}")
    print(f"Type: {type(video_tuple)}")
    
    # Just return the same video for both sides for testing
    if video_tuple and video_tuple[0]:
        return (video_tuple[0], video_tuple[0])
    return video_tuple

with gr.Blocks() as demo:
    with gr.Group():
        video_slider = VideoSlider(
            label="Test VideoSlider",
            value=(video1_path, video2_path) if video1_path and video2_path else None
        )
        video_slider.upload(simple_fn, inputs=video_slider, outputs=video_slider)

if __name__ == "__main__":
    demo.launch()
