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
	export const max_height: number = 500;
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
	let videosReady = false;

	let video_width = 0;
	let viewport_width = 0;
	
	$: style = `clip-path: inset(0 0 0 ${position * 100}%)`;

	function handle_video_load(): void {
		// Check if both videos are ready
		if (video1?.readyState >= 2 && video2?.readyState >= 2) {
			videosReady = true;
		}
	}


	function handleClick(): void {
		if (!video1 || !video2 || !videosReady) return;
		
		if (isPlaying) {
			video1.pause();
			video2.pause();
			isPlaying = false;
		} else {
			video1.loop = true;
			video2.loop = true;
			video1.play();
			video2.play();
			isPlaying = true;
		}
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

</script>

<BlockLabel {show_label} Icon={Video} label={label || i18n("video.video")} />
{#if value === null || value[0] === null || value[1] === null}
	<Empty unpadded_box={true} size="large">
		<div class="empty-state">
			<Video size="3rem" />
			<p class="empty-text">Upload two videos to compare</p>
		</div>
	</Empty>
{:else}
	<div class="video-container" bind:this={video_container}>
		<!-- Simple Header -->
		<div class="header">
			<span>Click to play/pause videos</span>
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
		</div>

		<!-- Video Area -->
		<div
			class="slider-wrap"
			bind:this={slider_wrap_parent}
			bind:clientWidth={el_width}
			class:limit_height={!fullscreen}
			role="button"
			tabindex="0"
			aria-label="Video comparison player. Click to play/pause videos."
			on:click={handleClick}
			on:keydown={(e) => {
				if (e.key === ' ' || e.key === 'Enter') {
					e.preventDefault();
					handleClick();
				}
			}}
		>
			{#if !videosReady}
				<div class="loading-overlay">
					<p>Loading videos...</p>
				</div>
			{/if}

			<Slider
				bind:position
				{slider_color}
				bind:el={slider_wrap}
				bind:parent_el
			>
				<video
					bind:this={video1}
					src={value?.[0]?.url}
					class="video-element base-video"
					muted
					preload="metadata"
					on:loadeddata={handle_video_load}
					on:timeupdate={() => sync_videos()}
				>
					<track kind="captions" />
				</video>
				<video
					bind:this={video2}
					src={value?.[1]?.url}
					class="video-element overlay-video"
					muted
					preload="metadata"
					style="{style}"
					on:loadeddata={handle_video_load}
				>
					<track kind="captions" />
				</video>
			</Slider>

		</div>
	</div>
{/if}

<style>
	.video-container {
		height: 100%;
		position: relative;
		min-width: var(--size-20);
		background: #f5f5f5;
		border: 1px solid #ddd;
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 10px;
		background: white;
		border-bottom: 1px solid #ddd;
		font-size: 14px;
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
		outline: none;
	}

	.limit_height .video-element {
		max-height: 500px;
	}

	.video-element {
		width: 100%;
		height: auto;
		display: block;
		object-fit: contain;
		cursor: pointer;
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
		align-items: center;
		justify-content: center;
		z-index: 10;
		color: white;
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
	}

	:global(.slider-wrap .video-element) {
		max-width: 100%;
		height: auto;
	}
</style>
