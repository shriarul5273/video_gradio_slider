<script lang="ts">
	import Slider from "./Slider.svelte";
	import {
		BlockLabel,
		Empty,
		IconButton,
		IconButtonWrapper,
		FullscreenButton
	} from "@gradio/atoms";
	import { Video, Download, Undo, Clear } from "@gradio/icons";
	import { type FileData } from "@gradio/client";
	import type { I18nFormatter } from "@gradio/utils";
	import { DownloadLink } from "@gradio/wasm/svelte";
	import { onMount, createEventDispatcher } from "svelte";
	import { tweened, type Tweened } from "svelte/motion";
	import { fade, slide } from "svelte/transition";

	export let value: [null | FileData, null | FileData] = [null, null];
	export let label: string | undefined = undefined;
	export let show_download_button = true;
	export let show_label: boolean;
	export let i18n: I18nFormatter;
	export let position: number = 0.5;
	export let slider_color: string = "#4285f4";
	export let show_fullscreen_button = true;
	export let fullscreen = false;
	export let el_width = 0;
	export let max_height: number;
	export let interactive = true;
	
	const dispatch = createEventDispatcher<{ 
		clear: void;
		select: any;
		share: any;
		error: any;
		fullscreen: boolean;
	}>();

	let video1: HTMLVideoElement;
	let video2: HTMLVideoElement;
	let slider_wrap: HTMLDivElement;
	let video_container: HTMLDivElement;
	let slider_wrap_parent: HTMLDivElement;
	let parent_el: HTMLDivElement;

	// State variables
	let isPlaying = false;
	let duration = 0;
	let currentTime = 0;
	let isLoaded = false;
	let videosReady = false;
	let showControls = true;
	let controlsTimeout: NodeJS.Timeout;
	let isMousePressed = false;

	let transform: Tweened<{ x: number; y: number; z: number }> = tweened(
		{ x: 0, y: 0, z: 1 },
		{
			duration: 150,
			easing: (t) => t * t * (3 - 2 * t) // smooth easing
		}
	);

	let video_size: { top: number; left: number; width: number; height: number } = 
		{ top: 0, left: 0, width: 0, height: 0 };

	let video_width = 0;
	let viewport_width = 0;
	let observer: ResizeObserver | null = null;

	$: coords_at_viewport = get_coords_at_viewport(
		position,
		viewport_width,
		video_size.width,
		video_size.left,
		$transform.x,
		$transform.z
	);

	$: style = `clip-path: inset(0 0 0 ${coords_at_viewport * 100}%)`;

	function get_coords_at_viewport(
		viewport_percent_x: number, // 0-1
		viewportWidth: number,
		video_width: number,
		video_offset_x: number,
		tx: number, // video translation x (in pixels)
		scale: number // video scale (uniform)
	): number {
		const px_relative_to_video = viewport_percent_x * video_width;
		const pixel_position = px_relative_to_video + video_offset_x;
		const normalised_position = (pixel_position - tx) / scale;
		const percent_position = normalised_position / viewportWidth;
		return percent_position;
	}

	function init_video(video: HTMLVideoElement, slider_wrap: HTMLDivElement): void {
		if (!video || !slider_wrap) return;
		observer?.disconnect();
		video_width = video?.getBoundingClientRect().width || 0;
		viewport_width = slider_wrap?.getBoundingClientRect().width || 0;

		observer = new ResizeObserver((entries) => {
			for (const entry of entries) {
				if (entry.target === slider_wrap) {
					viewport_width = entry.contentRect.width;
				}
				if (entry.target === video) {
					video_width = entry.contentRect.width;
				}
			}
		});
		observer.observe(slider_wrap);
		observer.observe(video);
	}

	$: init_video(video1, slider_wrap);

	function handle_video_load(event: Event): void {
		const video = event.target as HTMLVideoElement;
		const rect = video.getBoundingClientRect();
		video_size = {
			top: rect.top,
			left: rect.left,
			width: rect.width,
			height: rect.height
		};
		
		// Set duration when first video loads
		if (video === video1) {
			duration = video.duration;
			isLoaded = true;
		}
		
		// Check if both videos are ready
		if (video1?.readyState >= 2 && video2?.readyState >= 2) {
			videosReady = true;
		}
	}

	function togglePlayPause(): void {
		if (!video1 || !video2) return;
		
		if (isPlaying) {
			video1.pause();
			video2.pause();
		} else {
			video1.play();
			video2.play();
		}
		isPlaying = !isPlaying;
	}

	function handleMouseDown(): void {
		if (!video1 || !video2 || !videosReady) return;
		isMousePressed = true;
		video1.play();
		video2.play();
		isPlaying = true;
	}

	function handleMouseUp(): void {
		if (!video1 || !video2) return;
		isMousePressed = false;
		video1.pause();
		video2.pause();
		isPlaying = false;
	}

	function handleMouseLeave(): void {
		if (isMousePressed) {
			handleMouseUp();
		}
	}

	function handleTimeSeek(event: Event): void {
		const input = event.target as HTMLInputElement;
		const newTime = parseFloat(input.value);
		if (video1 && video2) {
			video1.currentTime = newTime;
			video2.currentTime = newTime;
			currentTime = newTime;
		}
	}

	function formatTime(seconds: number): string {
		const mins = Math.floor(seconds / 60);
		const secs = Math.floor(seconds % 60);
		return `${mins}:${secs.toString().padStart(2, '0')}`;
	}

	function showControlsTemporarily(): void {
		showControls = true;
		clearTimeout(controlsTimeout);
		controlsTimeout = setTimeout(() => {
			if (isPlaying) showControls = false;
		}, 3000);
	}

	function sync_videos(): void {
		if (video1 && video2) {
			video2.currentTime = video1.currentTime;
			if (video1.paused) {
				video2.pause();
			} else {
				video2.play();
			}
		}
	}

	function handle_video1_timeupdate(): void {
		if (video1) {
			currentTime = video1.currentTime;
		}
		if (video2 && Math.abs(video1.currentTime - video2.currentTime) > 0.1) {
			video2.currentTime = video1.currentTime;
		}
	}

	function handle_video1_play(): void {
		isPlaying = true;
		if (video2 && video2.paused) {
			video2.play();
		}
	}

	function handle_video1_pause(): void {
		isPlaying = false;
		if (video2 && !video2.paused) {
			video2.pause();
		}
	}

	onMount(() => {
		return () => {
			observer?.disconnect();
			clearTimeout(controlsTimeout);
		};
	});
</script>

<BlockLabel {show_label} Icon={Video} label={label || i18n("video.video")} />
{#if value === null || value[0] === null || value[1] === null}
	<Empty unpadded_box={true} size="large">
		<div class="empty-state" in:fade={{ duration: 300 }}>
			<Video size="3rem" />
			<p class="empty-text">Upload two videos to compare</p>
		</div>
	</Empty>
{:else}
	<div class="video-container" bind:this={video_container} in:fade={{ duration: 400 }}>
		<!-- Header Controls -->
		<div class="header-controls">
			<div class="video-info">
				<div class="video-titles">
					<span class="video-title">{value[0]?.orig_name || "Video A"}</span>
					<span class="vs-divider">vs</span>
					<span class="video-title">{value[1]?.orig_name || "Video B"}</span>
				</div>
			</div>
			
			<IconButtonWrapper>
				{#if show_fullscreen_button}
					<FullscreenButton {fullscreen} on:fullscreen />
				{/if}

				{#if show_download_button && value[1]}
					<DownloadLink
						href={value[1]?.url}
						download={value[1]?.orig_name || "video"}
					>
						<IconButton Icon={Download} label={i18n("common.download")} />
					</DownloadLink>
				{/if}
				{#if interactive}
					<IconButton
						Icon={Clear}
						label="Clear Videos"
						on:click={(event) => {
							value = [null, null];
							dispatch("clear");
							event.stopPropagation();
						}}
					/>
				{/if}
			</IconButtonWrapper>
		</div>

		<!-- Main Video Area -->
		<div
			class="slider-wrap"
			bind:this={slider_wrap_parent}
			bind:clientWidth={el_width}
			class:limit_height={!fullscreen}
			class:mouse-pressed={isMousePressed}
			on:mousemove={showControlsTemporarily}
			on:mouseenter={() => showControls = true}
			on:mouseleave={handleMouseLeave}
			on:mousedown={handleMouseDown}
			on:mouseup={handleMouseUp}
		>
			<!-- Loading Overlay -->
			{#if !videosReady}
				<div class="loading-overlay" transition:fade>
					<div class="loading-spinner"></div>
					<p>Loading videos...</p>
				</div>
			{/if}

			<Slider
				bind:position
				{slider_color}
				bind:el={slider_wrap}
				bind:parent_el
				image_size={video_size}
			>
				<video
					bind:this={video1}
					src={value?.[0]?.url}
					class="video-element base-video"
					muted
					preload="metadata"
					style="transform: translate({$transform.x}px, {$transform.y}px) scale({$transform.z})"
					on:loadedmetadata={handle_video_load}
					on:loadeddata={() => videosReady = video1?.readyState >= 2 && video2?.readyState >= 2}
					on:timeupdate={handle_video1_timeupdate}
					on:play={handle_video1_play}
					on:pause={handle_video1_pause}
				>
					<track kind="captions" />
				</video>
				<video
					bind:this={video2}
					src={value?.[1]?.url}
					class="video-element overlay-video"
					muted
					preload="metadata"
					style="{style}; transform: translate({$transform.x}px, {$transform.y}px) scale({$transform.z})"
					on:loadedmetadata={handle_video_load}
					on:loadeddata={() => videosReady = video1?.readyState >= 2 && video2?.readyState >= 2}
				>
					<track kind="captions" />
				</video>
			</Slider>

			<!-- Custom Video Controls -->
			{#if showControls && videosReady}
				<div class="custom-controls" transition:slide={{ duration: 200 }}>
					<div class="controls-content">
						<div class="play-instruction">
							{#if isMousePressed}
								<span class="playing-indicator">▶ Playing...</span>
							{:else}
								<span class="instruction-text">Hold mouse down to play</span>
							{/if}
						</div>
						
						<div class="time-display">
							{formatTime(currentTime)} / {formatTime(duration)}
						</div>
						
						<div class="progress-container">
							<input
								type="range"
								class="progress-bar"
								min="0"
								max={duration}
								bind:value={currentTime}
								on:input={handleTimeSeek}
								step="0.1"
							/>
						</div>
						
						<div class="slider-position-display">
							Split: {Math.round(position * 100)}%
						</div>
					</div>
				</div>
			{/if}
		</div>
	</div>
{/if}

<style>
	.video-container {
		height: 100%;
		position: relative;
		min-width: var(--size-20);
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		border-radius: 12px;
		overflow: hidden;
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
	}

	.header-controls {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 16px 20px;
		background: rgba(255, 255, 255, 0.95);
		backdrop-filter: blur(10px);
		border-bottom: 1px solid rgba(255, 255, 255, 0.2);
	}

	.video-info {
		flex: 1;
	}

	.video-titles {
		display: flex;
		align-items: center;
		gap: 12px;
		font-weight: 500;
	}

	.video-title {
		color: #2d3748;
		font-size: 14px;
		max-width: 150px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.vs-divider {
		background: linear-gradient(45deg, #667eea, #764ba2);
		background-clip: text;
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		font-weight: bold;
		font-size: 16px;
	}

	.slider-wrap {
		user-select: none;
		height: 100%;
		width: 100%;
		position: relative;
		display: flex;
		align-items: center;
		justify-content: center;
		background: #000;
		min-height: 400px;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.slider-wrap:hover {
		background: #111;
	}

	.slider-wrap.mouse-pressed {
		background: #222;
		transform: scale(0.995);
	}

	.limit_height .video-element {
		max-height: 500px;
	}

	.video-element {
		width: 100%;
		height: auto;
		display: block;
		object-fit: contain;
		border-radius: 8px;
		transition: transform 0.3s ease;
	}

	.video-element:hover {
		cursor: pointer;
	}

	.play-instruction {
		display: flex;
		align-items: center;
		min-width: 150px;
	}

	.instruction-text {
		font-size: 14px;
		color: rgba(255, 255, 255, 0.8);
		font-weight: 500;
	}

	.playing-indicator {
		font-size: 14px;
		color: #4ade80;
		font-weight: 600;
		animation: pulse 1.5s ease-in-out infinite;
	}

	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.7; }
	}

	.base-video {
		position: relative;
		z-index: 1;
	}

	.overlay-video {
		position: absolute;
		top: 0;
		left: 0;
		z-index: 2;
		pointer-events: none;
	}

	.loading-overlay {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.8);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		z-index: 10;
		color: white;
		gap: 16px;
	}

	.loading-spinner {
		width: 48px;
		height: 48px;
		border: 4px solid rgba(255, 255, 255, 0.3);
		border-top: 4px solid #667eea;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}

	.custom-controls {
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
		z-index: 5;
		pointer-events: auto;
	}

	.controls-content {
		display: flex;
		align-items: center;
		gap: 16px;
		padding: 20px;
		color: white;
	}

	.time-display {
		font-family: monospace;
		font-size: 14px;
		min-width: 100px;
		color: rgba(255, 255, 255, 0.9);
	}

	.progress-container {
		flex: 1;
		margin: 0 16px;
	}

	.progress-bar {
		width: 100%;
		height: 6px;
		background: rgba(255, 255, 255, 0.3);
		border-radius: 3px;
		outline: none;
		cursor: pointer;
		-webkit-appearance: none;
		appearance: none;
	}

	.progress-bar::-webkit-slider-thumb {
		-webkit-appearance: none;
		appearance: none;
		width: 16px;
		height: 16px;
		background: #667eea;
		border-radius: 50%;
		cursor: pointer;
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
		transition: transform 0.2s ease;
	}

	.progress-bar::-webkit-slider-thumb:hover {
		transform: scale(1.2);
	}

	.progress-bar::-moz-range-thumb {
		width: 16px;
		height: 16px;
		background: #667eea;
		border-radius: 50%;
		cursor: pointer;
		border: none;
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
	}

	.slider-position-display {
		font-size: 12px;
		color: rgba(255, 255, 255, 0.8);
		background: rgba(255, 255, 255, 0.1);
		padding: 4px 8px;
		border-radius: 12px;
		backdrop-filter: blur(10px);
	}

	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 16px;
		padding: 40px;
		color: var(--text-color-subdued);
	}

	.empty-text {
		margin: 0;
		font-size: 16px;
		opacity: 0.8;
	}

	:global(.slider-wrap .video-element) {
		max-width: 100%;
		height: auto;
	}

	/* Responsive design */
	@media (max-width: 768px) {
		.header-controls {
			padding: 12px 16px;
		}
		
		.video-titles {
			gap: 8px;
		}
		
		.video-title {
			max-width: 100px;
			font-size: 12px;
		}
		
		.controls-content {
			padding: 16px;
			gap: 12px;
		}
		
		.time-display {
			font-size: 12px;
			min-width: 80px;
		}
	}

	/* Dark mode support */
	@media (prefers-color-scheme: dark) {
		.video-container {
			background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
		}
		
		.header-controls {
			background: rgba(26, 32, 44, 0.95);
		}
		
		.video-title {
			color: #e2e8f0;
		}
	}
</style>
