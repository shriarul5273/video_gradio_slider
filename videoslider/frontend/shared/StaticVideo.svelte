<svelte:options accessors={true} />

<script lang="ts">
	import type { Gradio, SelectData, ShareData } from "@gradio/utils";
	import VideoSliderPreview from "./VideoSliderPreview.svelte";

	import { Block, IconButton } from "@gradio/atoms";
	import { StatusTracker } from "@gradio/statustracker";
	import type { LoadingStatus } from "@gradio/statustracker";
	import type { FileData } from "@gradio/client";
	import { DownloadLink } from "@gradio/wasm/svelte";
	import { Download } from "@gradio/icons";
	import type { I18nFormatter } from "@gradio/utils";

	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible = true;
	export let value: [null | FileData, null | FileData] = null;
	export let label: string;
	export let show_label: boolean;
	export let upload_count: number = 2;
	export let show_download_button = true;
	export let height: number;
	export let width: number | undefined;
	export let i18n: I18nFormatter;
	export let slider_color: string;
	export let show_fullscreen_button: boolean;
	export let max_height: number;

	export let container = true;
	export let scale: number | null = null;
	export let min_width: number | undefined = undefined;
	export let loading_status: LoadingStatus;
	export let gradio: Gradio<{
		change: never;
		error: string;
		select: SelectData;
		share: ShareData;
	}>;
	export let position: number;

	let el_width: number;
	let dragging: boolean;
	let fullscreen = false;

	$: value, gradio.dispatch("change");
	$: value = !value ? null : value;
	$: is_half = upload_count === 1 && value && value[0] != null && value[1] == null;

	$: normalised_position = Math.max(0, Math.min(100, position)) / 100;
</script>

<Block
	{visible}
	variant={"solid"}
	border_mode={dragging ? "focus" : "base"}
	padding={false}
	{elem_id}
	{elem_classes}
	{height}
	{width}
	allow_overflow={false}
	{container}
	{scale}
	{min_width}
	bind:fullscreen
>
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-noninteractive-element-interactions-->
	<div class="icon-buttons">
		{#if show_download_button && value && value[1]}
			<DownloadLink href={value[1].url} download={value[1].orig_name || "video"}>
				<IconButton Icon={Download} label={i18n("common.download")} />
			</DownloadLink>
		{/if}
	</div>
	<div
		class="status-wrap"
		class:half={is_half}
		style:width="{is_half ? el_width * (1 - normalised_position) : el_width}px"
		style:transform="translateX({is_half ? el_width * normalised_position : 0}px)"
	>
		<StatusTracker
			autoscroll={gradio.autoscroll}
			{i18n}
			{...loading_status}
		/>
	</div>
	<VideoSliderPreview
		bind:el_width
		on:select={({ detail }) => gradio.dispatch("select", detail)}
		on:share={({ detail }) => gradio.dispatch("share", detail)}
		on:error={({ detail }) => gradio.dispatch("error", detail)}
		on:clear={() => gradio.dispatch("clear")}
		on:fullscreen={({ detail }) => {
			fullscreen = detail;
		}}
		{fullscreen}
		interactive={false}
		bind:value
		{label}
		{show_label}
		{show_download_button}
		{i18n}
		{show_fullscreen_button}
		position={normalised_position}
		{slider_color}
		{max_height}
	/>
</Block>

<style>
	.status-wrap {
		position: absolute;
		height: 100%;
		width: 100%;
		--anim-block-background-fill: 255, 255, 255;
		z-index: 1;
		pointer-events: none;
	}

	@media (prefers-color-scheme: dark) {
		.status-wrap {
			--anim-block-background-fill: 31, 41, 55;
		}
	}

	@keyframes pulse {
		0% {
			background-color: rgba(var(--anim-block-background-fill), 0.7);
		}
		50% {
			background-color: rgba(var(--anim-block-background-fill), 0.4);
		}
		100% {
			background-color: rgba(var(--anim-block-background-fill), 0.7);
		}
	}

	.status-wrap.half :global(.wrap) {
		border-radius: 0;
		animation: pulse 1.4s infinite ease-in-out;
	}

	.status-wrap.half :global(.progress-text) {
		background: none !important;
	}

	.status-wrap.half :global(.eta-bar) {
		opacity: 0;
	}
	.icon-buttons {
		display: flex;
		position: absolute;
		right: 6px;
		z-index: var(--layer-1);
		top: 6px;
	}
</style>
