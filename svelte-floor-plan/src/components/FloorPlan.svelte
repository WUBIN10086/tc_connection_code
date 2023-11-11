<script>
    // 假设这些是从图片中提取的房间的墙体坐标
    let walls = [
    // 房间 D308
    { x1: 10, y1: 30, x2: 190, y2: 30 },   // 上墙
    { x1: 10, y1: 30, x2: 10, y2: 350 },   // 左墙
    { x1: 190, y1: 30, x2: 190, y2: 350 }, // 右墙
    { x1: 10, y1: 350, x2: 190, y2: 350 }, // 下墙
        
    // D307
    { x1: 190, y1: 30, x2: 550, y2: 30 },   // 上墙
    { x1: 550, y1: 30, x2: 550, y2: 350 }, // 右墙
    { x1: 190, y1: 350, x2: 550, y2: 350 }, // 下墙
    
    // D306
    { x1: 550, y1: 30, x2: 910, y2: 30 },   // 上墙
    { x1: 910, y1: 30, x2: 910, y2: 350 }, // 右墙
    { x1: 550, y1: 350, x2: 910, y2: 350 },   // 下墙

    // D305
    { x1: 910, y1: 30, x2: 1270, y2: 30 },   // 上墙
    { x1: 1270, y1: 30, x2: 1270, y2: 350 }, // 右墙
    { x1: 910, y1: 350, x2: 1270, y2: 350 },   // 下墙

    // D303
    { x1: 1270, y1: 30, x2: 1450, y2: 30 },   // 上墙
    { x1: 1450, y1: 30, x2: 1450, y2: 350 }, // 右墙
    { x1: 1270, y1: 350, x2: 1450, y2: 350 },   // 下墙

    // D301
    { x1: 1450, y1: 30, x2: 1630, y2: 30 },   // 上墙
    { x1: 1630, y1: 30, x2: 1630, y2: 350 }, // 右墙
    { x1: 1450, y1: 350, x2: 1630, y2: 350 },   // 下墙
			
	];

    // 这些是从图中提取的房间标签位置和文本
    let roomLabels = [
    { x: 95, y: 180, text: 'D308', fontSize: 20 },
    { x: 370, y: 180, text: 'D307', fontSize: 20 },
	{ x: 730, y: 180, text: 'D306', fontSize: 20 },
	{ x: 1090, y: 180, text: 'D305', fontSize: 20 },
	{ x: 1370, y: 180, text: 'D303', fontSize: 20 },
    { x: 1550, y: 180, text: 'D301', fontSize: 20 },
    ];
    

    // dimensions 数据结构，包含起始点、结束点和线的Y位置
    // 添加更多尺寸标注 
    let dimensions = [
     { x1: 10, y1: 15, x2: 1630, y2: 15, text: '32.4m', fontSize: 18 },
    ];

    // AP 和 Host
    let elements = [];
    let nextId = 1; // 开始编号
    let selectedElementId = null; // 跟踪选中的元素ID
    export function placeElement(elementData) {
        // 为新元素分配一个编号
        const elementWithId = {
        ...elementData,
        id: nextId++
        };
        elements = [...elements, elementWithId];
    }

    // 设置选中的元素
    function selectElement(id) {
        selectedElementId = id;
    }  

    // 删除选中的元素
    export function removeSelectedElement() {
        if (selectedElementId !== null) {
        elements = elements.filter(e => e.id !== selectedElementId);
        selectedElementId = null;
        }
    }

    // 点击元素时触发的函数
    function handleClick(event, id) {
        event.stopPropagation(); // 阻止冒泡
        selectElement(id);
    }


  </script>
  
<svg width="100%" height="100%" viewBox="0 0 1640 600">
  <!-- 绘制墙体 -->
  {#each walls as wall}
    <line x1={wall.x1} y1={wall.y1} x2={wall.x2} y2={wall.y2} stroke="black" />
  {/each}

  <!-- 绘制房间标签 -->
  {#each roomLabels as label}
    <text x={label.x} y={label.y} font-size={label.fontSize} text-anchor="middle" fill="black">{label.text}</text>
  {/each}

  <!-- 绘制尺寸标注 -->
  {#each dimensions as dimension}
    <line x1={dimension.x1} y1={dimension.y1} x2={dimension.x2} y2={dimension.y2} stroke="magenta" stroke-dasharray="5,5" />
    <text x={(dimension.x1 + dimension.x2) / 2} y={dimension.y1 - 5} font-size={dimension.fontSize} text-anchor="middle" fill="magenta">{dimension.text}</text>
  {/each}

  <!-- 绘制现有元素... -->
  {#each elements as element}
    {#if element.type === 'AP'}
      <!-- 绘制 AP - 红色三角形 -->
      <polygon points={`${element.x},${element.y - 10} ${element.x - 10},${element.y + 10} ${element.x + 10},${element.y + 10}`} fill="red" />
    {:else if element.type === 'Host'}
      <!-- 绘制 Host - 蓝色圆圈 -->
      <circle cx={element.x} cy={element.y} r="10" fill="blue" />
    {/if}
    <!-- 显示编号 -->
    <text x={element.x} y={element.y + 20} font-size="10" text-anchor="middle" fill="black">{element.id}</text>
    <!-- 选中时高亮显示 -->
    <circle cx={element.x} cy={element.y} r="15" fill={element.id === selectedElementId ? 'yellow' : 'none'} />
  {/each}


</svg>

<style>
  /* 为 SVG 容器设置一个具体的大小，例如 */
  :global(body) {
    margin: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh; /* 设置最小高度，而不是固定高度 */
  }

  svg {
    border: 1px solid #ccc; /* For visibility */
    /* 移除最大宽高限制 */
    /* 确保 SVG 在容器内居中 */
    margin: auto;
    display: block; /* 防止滚动条 */
  }
  line {
    stroke-width: 2;
  }
  text {
    dominant-baseline: middle;
    text-anchor: middle;
    font-family: 'Arial', sans-serif;
  }
</style>
  