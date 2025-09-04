<script lang="ts">
	import { createEventDispatcher } from "svelte";
	import { BlockLabel, Empty, IconButton } from "@gradio/atoms";
	import { Download, Video } from "@gradio/icons";
	import { type I18nFormatter } from "@gradio/utils";
	import { Upload } from "@gradio/upload";
	import { DownloadLink } from "@gradio/wasm/svelte";
	import { type FileData, type Client } from "@gradio/client";

	export let value: [FileData | null, FileData | null];
	export let label: string | undefined = undefined;
	export let show_label: boolean;
	export let root: string;
	export const position: number = 0.5; // For compatibility with ImageSlider API
	export const upload_count = 2; // For compatibility with ImageSlider API
	export let show_download_button = true;
	export const slider_color: string = "var(--border-color-primary)"; // For compatibility
	export let upload: Client["upload"];
	export let stream_handler: Client["stream"];
	export let max_file_size: number | null = null;
	export const i18n: I18nFormatter | undefined = undefined; // For compatibility
	export let max_height: number;
	export let dragging: boolean;

	const dispatch = createEventDispatcher<{
		change: [FileData | null, FileData | null];
		clear: void;
		drag: boolean;
		upload: FileData[];
		select: { index: number; value: any };
		share: { description: string; title: string };
		edit: void;
		stream: void;
	}>();

	let value_: [FileData | null, FileData | null] = value || [null, null];

	$: value_ = value;
	$: dispatch("change", value);
	$: console.log('VideoUploadComponent value changed:', value);
</script>

<BlockLabel {show_label} Icon={Video} label={label || "VideoSlider"} />

<div class="video-upload-container" style="max-height: {max_height}px;">
	{#if value_[0] && value_[1]}
		<!-- Both videos uploaded - show preview -->
		<div class="video-pair-preview">
			<div class="video-preview">
				<video controls muted>
					<source src={value_[0].url} />
					Your browser does not support the video tag.
				</video>
				<div class="video-label">Video 1</div>
				{#if show_download_button && value_[0]?.url}
					<DownloadLink href={value_[0].url} download={value_[0].orig_name || "video1"}>
						<IconButton Icon={Download} label="Download Video 1" />
					</DownloadLink>
				{/if}
			</div>
			
			<div class="video-preview">
				<video controls muted>
					<source src={value_[1].url} />
					Your browser does not support the video tag.
				</video>
				<div class="video-label">Video 2</div>
				{#if show_download_button && value_[1]?.url}
					<DownloadLink href={value_[1].url} download={value_[1].orig_name || "video2"}>
						<IconButton Icon={Download} label="Download Video 2" />
					</DownloadLink>
				{/if}
			</div>
			
			<div class="clear-all">
				<IconButton
					Icon={Video}
					label="Clear All Videos"
					on:click={() => {
						value = [null, null];
						value_ = [null, null];
						dispatch("change", value);
						dispatch("clear");
					}}
				/>
			</div>
		</div>
	{:else}
		<!-- Upload area for video pair -->
		<div class="upload-section">
			<div class="upload-label">Upload Video Pair</div>
			<div class="upload-instructions">Upload two videos to compare side by side</div>
			
			<Upload
				filetype="video/mp4,video/avi,video/mov,video/mkv,video/webm,video/*"
				file_count="multiple"
				on:load={(e) => {
					console.log('Upload component load event:', e);
					console.log('Event detail:', e.detail);
					
					if (e.detail && e.detail.length >= 2) {
						// Two videos uploaded at once
						value = [e.detail[0], e.detail[1]];
						value_ = [e.detail[0], e.detail[1]];
						console.log('Set both videos:', value);
					} else if (e.detail && e.detail.length === 1) {
						// One video uploaded - set as first or second based on current state
						if (!value_[0]) {
							value = [e.detail[0], value_[1]];
							value_ = [e.detail[0], value_[1]];
							console.log('Set first video:', value);
						} else if (!value_[1]) {
							value = [value_[0], e.detail[0]];
							value_ = [value_[0], e.detail[0]];
							console.log('Set second video:', value);
						}
					}
					
					dispatch("change", value);
					dispatch("upload", e.detail);
				}}
				on:error={(e) => {
					console.error('Upload error:', e);
					console.error('Error detail:', e.detail);
					dispatch('error', e.detail);
				}}
				on:drag={({ detail }) => {
					console.log('Drag event:', detail);
					dragging = detail;
				}}
				{upload}
				{stream_handler}
				{root}
				max_file_size={max_file_size}
				disable_click={false}
			>
				<div class="upload-placeholder">
					<slot />
					<div class="upload-hint">
						Drop two video files here or click to browse<br/>
						<small>You can upload files one at a time or select multiple files</small>
					</div>
				</div>
			</Upload>
			
			{#if value_[0] && !value_[1]}
				<div class="partial-upload">
					<div class="uploaded-video">
						<video controls muted>
							<source src={value_[0].url} />
						</video>
						<div>First video uploaded. Upload second video to continue.</div>
					</div>
				</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	.video-upload-container {
		width: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 16px;
		padding: 1rem;
	}

	.video-pair-preview {
		display: flex;
		gap: 1rem;
		align-items: flex-start;
		justify-content: center;
		flex-wrap: wrap;
		width: 100%;
	}

	.video-preview {
		flex: 1;
		min-width: 200px;
		max-width: 300px;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		align-items: center;
	}

	.video-preview video {
		width: 100%;
		max-height: 200px;
		border-radius: 4px;
		background: var(--color-border-subtle);
	}

	.video-label {
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text-secondary);
	}

	.clear-all {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 100%;
		margin-top: 1rem;
	}

	.upload-section {
		display: flex;
		flex-direction: column;
		align-items: center;
		border: 2px dashed var(--border-color-primary);
		border-radius: 8px;
		padding: 20px;
		min-height: 200px;
		width: 100%;
		max-width: 600px;
	}

	.upload-label {
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--color-text-primary);
		text-align: center;
		margin-bottom: 0.5rem;
	}

	.upload-instructions {
		font-size: 0.875rem;
		color: var(--color-text-secondary);
		text-align: center;
		margin-bottom: 1rem;
	}

	.upload-placeholder {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 150px;
		width: 100%;
		text-align: center;
		gap: 0.5rem;
	}

	.upload-hint {
		font-size: 0.875rem;
		color: var(--color-text-secondary);
		line-height: 1.4;
	}

	.upload-hint small {
		font-size: 0.75rem;
		opacity: 0.8;
	}

	.partial-upload {
		margin-top: 1rem;
		padding: 1rem;
		border: 1px solid var(--color-border);
		border-radius: 4px;
		background: var(--color-background-secondary);
		text-align: center;
		width: 100%;
	}

	.uploaded-video {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
	}

	.uploaded-video video {
		width: 100%;
		max-width: 200px;
		max-height: 150px;
		border-radius: 4px;
	}

	.uploaded-video div {
		font-size: 0.875rem;
		color: var(--color-text-secondary);
		text-align: center;
	}
</style>
