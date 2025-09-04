"""gr.VideoSlider() component."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from gradio_client import handle_file
from gradio_client.documentation import document

from gradio.components.base import Component
from gradio.data_classes import GradioRootModel, FileData
from gradio.events import Events


class VideoSliderData(GradioRootModel):
    root: tuple[FileData | None, FileData | None] | None


video_tuple = tuple[
    str | Path | None, str | Path | None
]


if TYPE_CHECKING:
    from gradio.components import Timer


class VideoSlider(Component):
    """
    Creates a video component that can be used to upload video pairs (as an input) or display video comparisons (as an output).
    The component provides a draggable slider to compare two videos side by side with synchronized playback.

    Demos: videoslider
    """

    EVENTS = [
        Events.clear,
        Events.change,
        Events.stream,
        Events.select,
        Events.upload,
        Events.input,
    ]

    data_model = VideoSliderData

    def __init__(
        self,
        value: video_tuple | Callable | None = None,
        *,
        height: int | str | None = None,
        width: int | str | None = None,
        label: str | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        show_download_button: bool = True,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        show_fullscreen_button: bool = True,
        slider_position: float = 50,
        max_height: int = 500,
    ):
        """
        Parameters:
            value: A tuple of video file paths, URLs, or file objects for the default value that VideoSlider component is going to take. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            height: The height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. This will affect the displayed videos.
            width: The width of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. This will affect the displayed videos.
            label: the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            show_download_button: If True, will display button to download videos. Only applies if interactive is False (e.g. if the component is used as an output).
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: if True, will allow users to upload and edit videos; if False, can only be used to display videos. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            show_fullscreen_button: If True, will show a fullscreen icon in the corner of the component that allows user to view the videos in fullscreen mode. If False, icon does not appear.
            slider_position: The position of the slider as a percentage of the width of the video, between 0 and 100.
            max_height: The maximum height of the videos.
        """
        self.slider_position = slider_position
        self.max_height = max_height
        self.height = height
        self.width = width
        self.show_download_button = show_download_button
        self.show_fullscreen_button = show_fullscreen_button

        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )
        self._value_description = "a tuple of filepaths to video files"

    def preprocess(self, payload: VideoSliderData | None) -> video_tuple | None:
        """
        Parameters:
            payload: video data in the form of a VideoSliderData object
        Returns:
            Passes the uploaded videos as a tuple of file paths.
        """
        if payload is None:
            return None
        if payload.root is None:
            raise ValueError("Payload is None.")
        
        video1_path = None
        video2_path = None
        
        if payload.root[0] is not None:
            video1_path = payload.root[0].path
        if payload.root[1] is not None:
            video2_path = payload.root[1].path
            
        return (video1_path, video2_path)

    def postprocess(
        self,
        value: tuple[str | Path | None, str | Path | None] | None,
    ) -> VideoSliderData | None:
        """
        Parameters:
            value: Expects a tuple of file paths to videos which are displayed.
        Returns:
            Returns the videos as a VideoSliderData object.
        """
        if value is None:
            return None
        
        video1_data = None
        video2_data = None
        
        if value[0] is not None:
            video1_data = FileData(path=str(value[0]))
        if value[1] is not None:
            video2_data = FileData(path=str(value[1]))
            
        return VideoSliderData(root=(video1_data, video2_data))

    def api_info_as_output(self) -> dict[str, Any]:
        return self.api_info()

    def example_payload(self) -> Any:
        return (
            handle_file(
                "https://sample-videos.com/zip/10/mp4/SampleVideo_360x240_1mb.mp4"
            ),
            handle_file(
                "https://sample-videos.com/zip/10/mp4/SampleVideo_360x240_1mb.mp4"
            ),
        )

    def example_value(self) -> Any:
        return (
            "https://sample-videos.com/zip/10/mp4/SampleVideo_360x240_1mb.mp4",
            "https://sample-videos.com/zip/10/mp4/SampleVideo_360x240_1mb.mp4",
        )
