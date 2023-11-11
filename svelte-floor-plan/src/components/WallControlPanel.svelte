<script>
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  let selectedWallType = '';

  function selectWallType(type) {
    selectedWallType = type;
    dispatch('walltypechange', { type });
  }
</script>

<div>
  <button on:click={() => selectWallType('W1')}>走廊墙 (W1)</button>
  <button on:click={() => selectWallType('W2')}>隔断墙 (W2)</button>
  <button on:click={() => selectWallType('W3')}>隔间墙 (W3)</button>
  <button on:click={() => selectWallType('W4')}>玻璃墙 (W4)</button>
  <button on:click={() => selectWallType('W5')}>电梯墙 (W5)</button>
  <button on:click={() => selectWallType('W6')}>门 (W6)</button>
</div>

<style>
  button {
    margin: 0.5rem;
    padding: 0.5rem 1rem;
  }
</style>
