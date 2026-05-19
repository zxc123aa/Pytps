import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.sin(x) * np.cos(x)

# 创建子图
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 6),
                                     sharex=True)

ax1.plot(x, y1)
ax1.set_ylabel('sin(x)')

ax2.plot(x, y2)
ax2.set_ylabel('cos(x)')

ax3.plot(x, y3)
ax3.set_ylabel('sin(x)cos(x)')
ax3.set_xlabel('x')

# 关键设置：消除子图间距，实现共享边界
plt.subplots_adjust(hspace=0)  # 设置为0，边界重合

# 可选：移除中间子图的x轴刻度标签（更整洁）
ax1.tick_params(labelbottom=False)
ax2.tick_params(labelbottom=False)

plt.show()