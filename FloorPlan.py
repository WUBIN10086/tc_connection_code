import matplotlib.pyplot as plt
import matplotlib.patches as patches
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random  # Import the random module


# 创建一个新窗口
root = tk.Tk()
root.wm_title("Interactive Floor Plan")

# 创建一个 matplotlib 图表
fig, ax = plt.subplots(figsize=(16, 8))  # 根据平面图的实际尺寸调整尺寸
ax.set_xlim(0, 32.4)
ax.set_ylim(0, 15.3)
ax.invert_yaxis()  # Y轴反向，使得0点在左上角

# 绘制房间和其他区域的函数
def draw_room(x, y, width, height, room_label):
    room = patches.Rectangle((x, y), width, height, edgecolor='black', facecolor='none')
    ax.add_patch(room)
    ax.text(x + width/2, y + height/2, room_label, horizontalalignment='center', verticalalignment='center')

# 绘制各个房间
draw_room(0, 8.9, 3.6, 6.4, 'D308')  # D308
draw_room(3.6, 8.9, 7.2, 6.4, 'D307')  # D307
draw_room(10.8, 8.9, 7.2, 6.4, 'D306')  # D306
draw_room(18.0, 8.9, 7.2, 6.4, 'D305')  # D305
draw_room(25.2, 8.9, 3.6, 6.4, 'D303')  # D303
draw_room(28.8, 8.9, 3.6, 6.4, 'D301')  # D301

# 绘制楼梯间、休息区和厕所
draw_room(0, 0, 3.6, 6.4, 'Stairs')  # 楼梯间
draw_room(3.6, 0, 7.2, 6.4, 'Refresh Corner')  # 休息区
draw_room(10.8, 0, 7.2, 6.4, 'Toilets')  # 厕所

# 绘制 D304 和 D302
draw_room(18.0, 0, 7.2, 6.4, 'D304')  # D304
draw_room(25.2, 0, 7.2, 6.4, 'D302')  # D302


# 存储 AP 和 Host 对象的列表
aps = []
hosts = []

# AP 和 Host 的编号
ap_count = 1
host_count = 1

# 添加 AP 的函数
def add_ap():
    global ap_count
    x, y = random.uniform(0, 32.4), random.uniform(0, 15.3)
    ap, = ax.plot(x, y, '^b', markersize=10)  # 蓝色三角形表示 AP
    label = ax.annotate(str(ap_count), xy=(x, y), textcoords="offset points", xytext=(0,10), ha='center')
    ap_count += 1
    aps.append((ap, label))
    canvas.draw()

# 添加 Host 的函数
def add_host():
    global host_count
    x, y = random.uniform(0, 32.4), random.uniform(0, 15.3)
    host, = ax.plot(x, y, 'ro', markersize=10)  # 红色圆圈表示 Host
    label = ax.annotate(str(host_count), xy=(x, y), textcoords="offset points", xytext=(0,10), ha='center')
    host_count += 1
    hosts.append((host, label))
    canvas.draw()

# 更新坐标的函数
def update_annotation(ann, new_x, new_y):
    ann.xy = (new_x, new_y)
    ann.set_position((new_x, new_y + 10))

# 移动 AP 或 Host 的函数
def on_move(event):
    if event.inaxes:
        for ap, label in aps:
            if ap.contains(event)[0]:
                update_annotation(label, event.xdata, event.ydata)
                ap.set_data(event.xdata, event.ydata)
                canvas.draw()
        for host, label in hosts:
            if host.contains(event)[0]:
                update_annotation(label, event.xdata, event.ydata)
                host.set_data(event.xdata, event.ydata)
                canvas.draw()

# 绑定移动事件
fig.canvas.mpl_connect('motion_notify_event', on_move)

# 添加 AP 和 Host 按钮
btn_add_ap = tk.Button(master=root, text="Add AP", command=add_ap)
btn_add_ap.pack(side=tk.LEFT)

btn_add_host = tk.Button(master=root, text="Add Host", command=add_host)
btn_add_host.pack(side=tk.LEFT)

# 在 Tkinter 窗口中嵌入 matplotlib 图表
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# 启动 Tkinter 事件循环
tk.mainloop()