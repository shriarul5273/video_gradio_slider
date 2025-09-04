import gradio as gr
from gradio_videoslider import VideoSlider
import os

def simple_demo(video_file):
    """Simple demo that just returns the same video for both sides"""
    if video_file:
        return (video_file, video_file)
    return None

with gr.Blocks(title="Simple VideoSlider Test") as demo:
    gr.Markdown("# Simple VideoSlider Test")
    gr.Markdown("Upload a video to test the VideoSlider component.")
    
    with gr.Row():
        with gr.Column():
            video_input = gr.Video(label="Upload Video")
            
        with gr.Column():
            output_slider = VideoSlider(
                label="Video Comparison",
                interactive=True
            )
    
    video_input.change(
        simple_demo,
        inputs=video_input,
        outputs=output_slider
    )
    
    gr.Markdown("Upload a video to see it displayed in the VideoSlider component.")

if __name__ == "__main__":
    demo.launch()
