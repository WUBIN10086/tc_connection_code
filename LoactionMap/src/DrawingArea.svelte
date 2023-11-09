<script>
	let walls = [];
	let apCoordinates = [];
	let hostCoordinates = [];
	let selectedWallType = 'standard'; // 默认墙面类型
  
	function addWall(x1, y1, x2, y2) {
	  walls = [...walls, { x1, y1, x2, y2, type: selectedWallType }];
	}
  </script>
  
  <style>
	.drawing-area {
	  position: relative;
	  width: 800px;
	  height: 600px;
	  border: 1px solid #000;
	}
  </style>
  
  <div class="drawing-area" on:mousedown={handleMouseDown} on:mouseup={handleMouseUp}>
	{#each walls as wall (wall.x1 + wall.y1 + wall.x2 + wall.y2)}
	  <line x1={wall.x1} y1={wall.y1} x2={wall.x2} y2={wall.y2} stroke={wall.type === 'standard' ? 'black' : 'red'} />
	{/each}
	{#each apCoordinates as ap (ap.x + ap.y)}
	  <circle cx={ap.x} cy={ap.y} r="5" fill="blue" />
	{/each}
	{#each hostCoordinates as host (host.x + host.y)}
	  <circle cx={host.x} cy={host.y} r="5" fill="green" />
	{/each}
  </div>
  