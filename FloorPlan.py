import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# 创建一个新窗口
root = tk.Tk()
root.wm_title("Interactive Floor Plan")

# 创建一个 matplotlib 图表
fig, ax = plt.subplots(figsize=(6, 3))
ax.set_xlim(0, 36)
ax.set_ylim(0, 9)

# 在 Tkinter 窗口中嵌入 matplotlib 图表
canvas = FigureCanvasTkAgg(fig, master=root) 
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# 定义点击事件处理函数
def onclick(event):
    # 仅当点击事件发生在坐标轴内时才响应
    if event.inaxes:
        ax.plot(event.xdata, event.ydata, 'ro')  # 在点击的位置添加一个红色的点
        canvas.draw()

# 绑定点击事件
fig.canvas.mpl_connect('button_press_event', onclick)

# 启动 Tkinter 事件循环
tk.mainloop()
