<script>
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  function placeElement(type) {
    // 此处应有逻辑来确定元素的位置
    // 暂时我们只发送元素类型
    dispatch('elementplaced', { type });
  }
</script>

<div>
  <button on:click={() => placeElement('AP')}>放置 AP</button>
  <button on:click={() => placeElement('Host')}>放置 Host</button>
</div>

<style>
  button {
    margin: 0.5rem;
    padding: 0.5rem 1rem;
  }
</style>
