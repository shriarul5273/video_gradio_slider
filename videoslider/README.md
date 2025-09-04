---
tags: [gradio-custom-component, ImageSlider]
title: gradio_videoslider
short_description: A gradio custom component
colorFrom: blue
colorTo: yellow
sdk: gradio
pinned: false
app_file: space.py
---

# VideoSlider

[![PyPI](https://img.shields.io/pypi/v/gradio_videoslider)](https://pypi.org/project/gradio_videoslider/)

A custom Gradio component for comparing videos side-by-side with a draggable slider interface and synchronized playback.

## Installation

```bash
pip install gradio_videoslider
```

## Usage

```python
import gradio as gr
from gradio_videoslider import VideoSlider

def process_videos(video_tuple):
    # Your video processing logic here
    return video_tuple

with gr.Blocks() as demo:
    input_slider = VideoSlider(label="Input Videos")
    output_slider = VideoSlider(label="Processed Videos", interactive=False)
    
    input_slider.change(process_videos, input_slider, output_slider)

demo.launch()
```

## Features

- **Side-by-side video comparison** with a draggable divider
- **Synchronized playback** - both videos play/pause together and stay in sync
- **Interactive slider** - drag the center handle to reveal more of either video
- **Click-to-play** - click on either video to control playback of both
- **Upload support** - drag and drop or click to upload video files
- **Fullscreen mode** - view videos in fullscreen for detailed comparison
- **Download functionality** - download videos when in output mode

## API

### VideoSlider

The main component for video comparison.

#### Parameters

- `value` (tuple[str | Path | None, str | Path | None], optional): A tuple of video file paths for the default videos
- `height` (int | str | None): Height of the component in pixels or CSS units
- `width` (int | str | None): Width of the component in pixels or CSS units  
- `label` (str | None): Label for the component
- `show_label` (bool): Whether to show the label
- `show_download_button` (bool): Whether to show download buttons (for output mode)
- `show_fullscreen_button` (bool): Whether to show fullscreen button
- `container` (bool): Whether to wrap in a container
- `scale` (int | None): Relative size compared to adjacent components
- `min_width` (int): Minimum width in pixels
- `interactive` (bool | None): Whether users can upload videos
- `visible` (bool): Whether the component is visible
- `elem_id` (str | None): HTML element ID
- `elem_classes` (list[str] | str | None): CSS classes
- `slider_position` (float): Initial slider position (0-100)
- `max_height` (int): Maximum height of videos

#### Events

- `change`: Triggered when videos are uploaded or changed
- `upload`: Triggered when files are uploaded
- `clear`: Triggered when videos are cleared
- `select`: Triggered when component is selected
- `input`: Triggered on user input

## Examples

### Basic Usage

```python
import gradio as gr
from gradio_videoslider import VideoSlider

demo = gr.Interface(
    fn=lambda x: x,  # Echo function
    inputs=VideoSlider(),
    outputs=VideoSlider()
)

demo.launch()
```

### Video Processing Pipeline

```python
import gradio as gr
from gradio_videoslider import VideoSlider

def enhance_video(video_tuple):
    """Process videos and return enhanced versions"""
    if video_tuple is None:
        return None
    
    video1_path, video2_path = video_tuple
    
    # Your video processing logic here
    # For demo purposes, just return the same videos
    enhanced1 = video1_path  # process_video(video1_path)
    enhanced2 = video2_path  # process_video(video2_path)
    
    return (enhanced1, enhanced2)

with gr.Blocks(title="Video Enhancement") as demo:
    gr.Markdown("# Video Enhancement Comparison")
    
    with gr.Row():
        input_videos = VideoSlider(
            label="Original Videos",
            slider_position=50
        )
        
        enhanced_videos = VideoSlider(
            label="Enhanced Videos", 
            interactive=False,
            slider_position=50
        )
    
    input_videos.change(
        enhance_video,
        inputs=input_videos,
        outputs=enhanced_videos
    )

demo.launch()
```

### Preset Video Comparison

```python
import gradio as gr
from gradio_videoslider import VideoSlider

# Load with preset videos
demo = gr.Interface(
    fn=lambda x: x,
    inputs=VideoSlider(
        value=("path/to/video1.mp4", "path/to/video2.mp4"),
        label="Compare Videos"
    ),
    outputs=VideoSlider(interactive=False)
)

demo.launch()
```

## Technical Details

### Synchronization

The VideoSlider component ensures perfect synchronization between videos by:

1. **Shared playback state** - Play/pause commands affect both videos
2. **Time synchronization** - Videos are periodically checked and synchronized
3. **Seek synchronization** - When one video seeks, both videos sync to the same time

### Frontend Implementation

The component uses Svelte for the frontend with:

- HTML5 video elements for playback
- Custom slider implementation for the divider
- Touch and mouse event handling for cross-platform compatibility
- CSS clipping for the overlay effect

### Backend Implementation

The Python backend:

- Handles file uploads and validation
- Manages video metadata
- Provides file serving capabilities
- Integrates with Gradio's component system

## Browser Compatibility

- Chrome/Chromium 88+
- Firefox 85+
- Safari 14+
- Edge 88+

Video format support depends on browser capabilities. MP4 with H.264 encoding is recommended for maximum compatibility.

## Contributing

1. Clone the repository
2. Install development dependencies: `pip install -e .[dev]`
3. Make changes to the component
4. Test with `gradio cc dev`
5. Build with `gradio cc build`
6. Submit a pull request

## License

Apache 2.0

## Changelog

### 0.0.1

- Initial release
- Basic video comparison functionality
- Synchronized playback
- Interactive slider
- Upload support
