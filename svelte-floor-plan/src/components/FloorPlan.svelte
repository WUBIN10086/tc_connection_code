<script>
  let aps = [];
  let hosts = [];

  function onDragStart(event, item) {
    event.dataTransfer.setData('text/plain', JSON.stringify(item));
  }

  function onDragOver(event) {
    event.preventDefault();
  }

  function onDrop(event, type) {
    event.preventDefault();
    const data = JSON.parse(event.dataTransfer.getData('text/plain'));
    if (type === 'ap') {
      aps = [...aps, { ...data, x: event.clientX, y: event.clientY }];
    } else {
      hosts = [...hosts, { ...data, x: event.clientX, y: event.clientY }];
    }
  }
</script>

<svg width="800" height="400" on:dragover={onDragOver} on:drop={event => onDrop(event, 'floor')}>
  <!-- Rooms -->
  <!-- D308 -->
  <rect x="0" y="0" width="89" height="158" fill="none" stroke="black" />
  <text x="40" y="80">D308</text>

  <!-- D307 -->
  <rect x="89" y="0" width="178" height="158" fill="none" stroke="black" />
  <text x="150" y="80">D307</text>

  <!-- D306 -->
  <rect x="267" y="0" width="178" height="158" fill="none" stroke="black" />
  <text x="330" y="80">D306</text>

  <!-- D305 -->
  <rect x="445" y="0" width="178" height="158" fill="none" stroke="black" />
  <text x="510" y="80">D305</text>

  <!-- D303 -->
  <rect x="623" y="0" width="89" height="158" fill="none" stroke="black" />
  <text x="650" y="80">D303</text>

  <!-- D301 -->
  <rect x="712" y="0" width="89" height="158" fill="none" stroke="black" />
  <text x="740" y="80">D301</text>

  <!-- Stairwell -->
  <rect x="0" y="158" width="89" height="158" fill="none" stroke="black" />
  <text x="10" y="240">Stairs</text>

  <!-- Corridor -->
  <rect x="89" y="158" width="62" height="158" fill="none" stroke="black" />
  <text x="100" y="240">Corridor</text>

  <!-- Rest Area -->
  <rect x="151" y="158" width="178" height="158" fill="none" stroke="black" />
  <text x="210" y="240">Rest</text>

  <!-- Toilet -->
  <rect x="329" y="158" width="178" height="158" fill="none" stroke="black" />
  <text x="390" y="240">Toilet</text>

  <!-- D304 -->
  <rect x="507" y="158" width="178" height="158" fill="none" stroke="black" />
  <text x="570" y="240">D304</text>

  <!-- D302 -->
  <rect x="685" y="158" width="115" height="158" fill="none" stroke="black" />
  <text x="720" y="240">D302</text>

  <!-- Draggable APs -->
  {#each aps as ap (ap.id)}
    <circle
      cx={ap.x}
      cy={ap.y}
      r="20"
      fill="blue"
      draggable="true"
      on:dragstart={event => onDragStart(event, ap)}
    />
  {/each}

  <!-- Draggable Hosts -->
  {#each hosts as host (host.id)}
    <circle
      cx={host.x}
      cy={host.y}
      r="20"
      fill="red"
      draggable="true"
      on:dragstart={event => onDragStart(event, host)}
    />
  {/each}
</svg>

<style>
  circle {
    cursor: pointer;
  }
  text {
    fill: black;
    font-size: 12px;
    pointer-events: none;
  }
</style>
