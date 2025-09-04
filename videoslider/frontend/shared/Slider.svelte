<script lang="ts">
	import { onMount } from "svelte";
	import { drag } from "d3-drag";
	import { select } from "d3-selection";

	function clamp(value: number, min: number, max: number): number {
		return Math.min(Math.max(value, min), max);
	}

	export let position = 0.5;
	export let disabled = false;

	export let slider_color = "var(--border-color-primary)";
	export let image_size: {
		top: number;
		left: number;
		width: number;
		height: number;
	} = { top: 0, left: 0, width: 0, height: 0 };
	export let el: HTMLDivElement | undefined = undefined;
	export let parent_el: HTMLDivElement | undefined = undefined;
	let inner: Element;
	let px = 0;
	let active = false;
	let container_width = 0;

	function set_position(width: number): void {
		container_width = parent_el?.getBoundingClientRect().width || 0;
		if (width === 0) {
			image_size.width = el?.getBoundingClientRect().width || 0;
		}

		px = clamp(
			image_size.width * position + image_size.left,
			0,
			container_width
		);
	}

	function round(n: number, points: number): number {
		const mod = Math.pow(10, points);
		return Math.round((n + Number.EPSILON) * mod) / mod;
	}

	function update_position(x: number): void {
		px = clamp(x, 0, container_width);
		position = round((x - image_size.left) / image_size.width, 5);
	}

	function drag_start(event: any): void {
		if (disabled) return;
		active = true;
		update_position(event.x);
	}

	function drag_move(event: any): void {
		if (disabled) return;
		update_position(event.x);
	}

	function drag_end(): void {
		if (disabled) return;
		active = false;
	}

	function update_position_from_pc(pc: number): void {
		px = clamp(image_size.width * pc + image_size.left, 0, container_width);
	}

	$: set_position(image_size.width);
	$: update_position_from_pc(position);

	onMount(() => {
		set_position(image_size.width);
		const drag_handler = drag()
			.on("start", drag_start)
			.on("drag", drag_move)
			.on("end", drag_end);
		select(inner).call(drag_handler);
	});
</script>

<svelte:window on:resize={() => set_position(image_size.width)} />

<div class="wrap" role="none" bind:this={parent_el}>
	<div class="content" bind:this={el}>
		<slot />
	</div>
	<div
		class="outer"
		class:disabled
		bind:this={inner}
		role="none"
		style="transform: translateX({px}px)"
		class:grab={active}
	>
		<div class="inner" style:--color={slider_color}></div>
	</div>
</div>

<style>
	.wrap {
		position: relative;
		width: 100%;
		height: 100%;
		z-index: var(--layer-1);
		overflow: hidden;
	}


	.outer {
		width: 20px;
		height: 100%;
		position: absolute;
		cursor: grab;
		position: absolute;
		top: 0;
		left: -10px;
		pointer-events: auto;
		z-index: var(--layer-2);
	}
	.grab {
		cursor: grabbing;
	}

	.inner {
		width: 1px;
		height: 100%;
		background: var(--color);
		position: absolute;
		left: calc((100% - 2px) / 2);
	}

	.disabled {
		cursor: auto;
	}

	.disabled .inner {
		box-shadow: none;
	}

	.content {
		width: 100%;
		height: 100%;
		display: flex;
		justify-content: center;
		align-items: center;
	}
</style>
