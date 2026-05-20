# PyTPS

PyTPS 是一个用于 Thomson Parabola Spectrometer (TPS) 图像分析的 Python/PySide6 程序。它从 TPS 相机图像中提取离子轨迹、计算能量刻度、估计背景并输出能谱曲线。

当前版本重点支持：

- 离线 TPS 图像浏览与解谱。
- 质子/离子理论抛物线显示。
- 中心带原始谱、背景谱、扣背景谱和平滑谱显示。
- 手工 Mask 绘制、保存、读取和显示清理。
- 能谱图和能谱 txt 数据保存。
- 多 shot 质子谱线对比窗口。

## 快速开始

建议使用 Python 3.10 或兼容版本。

```bash
pip install numpy scipy matplotlib imageio PySide6 scikit-image watchdog
python PyTPS.py
```

Windows 在线模式相关功能可能还需要：

```bash
pip install pywin32 pyautogui
```

## 主要配置文件

- `PyTPS_init.ini`：图像路径、保存路径、解谱窗口、显示滤波等程序配置。
- `TPS_Settings.ini`：TPS 磁场、电压、几何尺寸、相机增益、QE 等仪器参数。
- `mcp-proton.txt`：MCP 响应/效率表。

更详细的配置说明见 [CONFIG_GUIDE.md](CONFIG_GUIDE.md)。

## 当前能谱数据流

程序内部区分三类图像：

```text
rawImage      原始读入图像
analysisImage 定量解谱图像，固定使用保守 3x3 热像素中值预处理
displayImage  界面显示图像，显示滤波和 Mask 只影响它
```

能谱计算只使用 `analysisImage`。显示滤波、理论轨迹显示清理、手工 Mask 不改变定量能谱。

## 保存的能谱列

点击 `保存当前能谱` 后，程序保存一张 PNG 和一个 txt 文件。txt 当前包含：

```text
Energy_MeV
d2N_dE_dOmega_raw_center
d2N_dE_dOmega_background_subtracted
d2N_dE_dOmega_smoothed
d2N_dE_dOmega_background
```

这些列分别对应：

- `raw_center`：中心带原始积分谱。
- `background_subtracted`：中心带扣背景后的净谱。
- `smoothed`：对扣背景净谱做平滑后的曲线。
- `background`：背景水平谱。注意它不是中心带等效背景积分。

单位和公式细节见 [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md)。

## 技术文档

核心算法、公式和当前实现限制集中写在：

- [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md)：能量刻度、背景提取、谱强度归一化、平滑、Mask、保存格式。
- [CONFIG_GUIDE.md](CONFIG_GUIDE.md)：运行环境、配置文件、样例数据和 GitHub 使用。
- [COMPARE_USAGE.md](COMPARE_USAGE.md)：多 shot 谱线对比窗口说明。

## 重要说明

当前纵轴计算会除以：

$$
\mathrm{EMGain}\times QE\times \mathrm{MCP\_response}(E)\times \Delta E\times \Omega
$$

因此更严格地说，代码输出是经探测链路响应修正后的单位能量单位立体角谱强度。只有当 `EMGain`、`QE` 和 MCP 文件已经完成绝对粒子数标定时，纵轴才能严格解释为 $\mathrm{particles}\,\mathrm{MeV}^{-1}\,\mathrm{sr}^{-1}$。

## 样例数据

仓库可放置少量代表性 TPS 图像用于测试。大批量原始实验数据不建议直接提交到 Git，建议使用外部数据盘、Git LFS、Release 或云存储。

## 开发状态

该项目来源于 MATTPS V3.0 思路并进行了 PySide6 UI、显示清理、Mask、背景采样和平滑输出等扩展。当前仍以实验分析工具为目标，自动截止能量和绝对强度标定结果应结合图像轨迹和实验标定人工复核。
