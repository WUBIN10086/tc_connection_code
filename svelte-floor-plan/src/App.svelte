<script>
	// 导入组件
	import FloorPlan from './components/FloorPlan.svelte';
	import WallControlPanel from './components/WallControlPanel.svelte';
	import ElementControl from './components/ElementControl.svelte';
</script>

<main>
	<h1>平面图设计</h1>
	<FloorPlan />
	<WallControlPanel />
	<ElementControl />
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: none; /* 你可以根据需要修改这里，以适应你的设计 */
	}

	/* 根据需要添加更多样式 */
</style>
  