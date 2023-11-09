<script>
    let selectedAP = null;
    let selectedHost = null;
    let wallCount = 0;
    let wallType = 'standard';
  
    function calculateDistanceAndWallType() {
      if (selectedAP && selectedHost) {
        // 计算距离和墙面种类的逻辑
        wallCount = walls.filter(wall => wall.type === selectedWallType).length;
      }
    }
  </script>
  
  <div>
    <h2>信息面板</h2>
    {#if selectedAP && selectedHost}
      <p>AP坐标: ({selectedAP.x}, {selectedAP.y})</p>
      <p>Host坐标: ({selectedHost.x}, {selectedHost.y})</p>
      <button on:click={calculateDistanceAndWallType}>计算距离和墙面种类</button>
      {#if wallCount > 0}
        <p>墙面种类: {wallType}</p>
        <p>墙面数量: {wallCount}</p>
      {/if}
    {/if}
  </div>
  