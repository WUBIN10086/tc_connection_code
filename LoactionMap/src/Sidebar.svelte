<script>
    let wallTypes = ['standard', 'firewall', 'concrete'];
    let selectedWallType = 'standard'; // 声明并初始化 selectedWallType 变量
  </script>
  
  <div>
    <h2>工具栏</h2>
    <label for="wallType">墙壁类型:</label>
    <select id="wallType" bind:value={selectedWallType}>
      {#each wallTypes as type (type)}
        <option value={type}>{type}</option>
      {/each}
    </select>
  </div>
  