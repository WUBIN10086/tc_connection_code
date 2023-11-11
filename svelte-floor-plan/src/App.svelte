<!-- App.svelte -->
<script>
	import { onMount } from 'svelte';
	import FloorPlan from './components/FloorPlan.svelte';
	import WallControlPanel from './components/WallControlPanel.svelte';
	import ElementControl from './components/ElementControl.svelte';
  
	let floorPlanComponent;
  
	function handleElementPlaced(event) {
	  floorPlanComponent.placeElement(event.detail);
	}
  
	onMount(() => {
	  // 这里你可以执行组件挂载后的逻辑
	});

	// 处理删除选中元素的事件
	function handleRemoveElement() {
		floorPlanComponent.removeSelectedElement();
    }
</script>
  
<main>
	<h1>Location Map</h1>
	<FloorPlan bind:this={floorPlanComponent} />
	<!-- <WallControlPanel /> -->
	<ElementControl on:elementPlaced={handleElementPlaced} />
	<!-- 添加一个按钮来删除选中的元素 -->
	<button on:click={handleRemoveElement}>Delete</button>
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
	}
</style>