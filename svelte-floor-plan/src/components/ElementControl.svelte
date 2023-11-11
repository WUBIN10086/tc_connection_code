<!-- ElementControl.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  function placeElement(type) {
    // 暂时用固定的位置，你可以根据需求来获取实际的位置
    const elementData = {
      type: type,
      x: Math.random() * 800, // 例如随机位置
      y: Math.random() * 600
    };

    dispatch('elementPlaced', elementData);
  }
</script>

<div>
  <button on:click={() => placeElement('AP')}>放置 AP</button>
  <button on:click={() => placeElement('Host')}>放置 Host</button>
</div>
