# PyTPS 技术说明：图像处理、Mask 与能谱计算

本文档说明 PyTPS 当前版本的主要功能、数据流、能谱计算公式、背景提取方法、平滑算法和能谱保存格式。重点是让同一张 TPS 图像从相机 count 到最终能谱文件的处理过程可追踪、可复现。

## 1. 总体数据流

当前程序把一张 TPS 图像分成三类数据使用：

```text
rawImage
原始读入图像，仅做坐标方向统一。

analysisImage
定量解谱图像。当前固定使用保守 3x3 中值滤波去除孤立热像素。

displayImage
界面显示图像。显示滤波、理论轨迹显示清理、手工 Mask 只作用于显示图。
```

核心原则：

```text
能谱计算只使用 analysisImage
界面预览使用 displayImage
手工 Mask 主要用于显示清理和标签保存
显示滤波不改变能谱计算结果
```

当前代码路径：

```text
TImageRead.readImage()
-> TFilter.makeAnalysisImage()
-> SolveSpectrum.SolveSpectrumSideband()
-> SolveSpectrum.SmoothSpectrumDisplayRaw()
-> TDraw.DrawSpec()
-> PyTPS.saveSpec()
```

## 2. 图像读取与坐标

图像由 `TImageRead.readImage()` 读取。

如果图像最大值小于 256，程序认为它是 8-bit 图像，并把像素值乘以 256：

```text
if max(image) < 256:
    image = image * 256
    is8bit = True
else:
    is8bit = False
```

随后图像转为 `uint16`。

TPS 解谱公式使用左下角为原点的坐标，因此主流程会执行：

```python
np.flipud(img)
```

在界面上看到的图像和解谱使用的图像方向已经统一。

## 3. 显示滤波与定量滤波

### 3.1 显示滤波

UI 中的 `显示滤波` 目前有：

```text
原图
中值3x3
中值5x5
```

这些只影响 `displayImage`，不改变能谱。

真实数据 `Shot41-49.tif` 测试结果表明：切换这三个显示滤波选项后，能谱数组保持一致。

### 3.2 定量预处理

定量解谱固定使用：

```text
3x3 中值滤波
```

目的只是去掉孤立热像素，不做大尺度背景扣除，不做形态学分割，不做轨迹外抹平。

真实数据 `Shot41-49.tif` 对比结果：

```text
none 相对 3x3 中值：平滑谱积分通常偏高约 1%-3%
5x5 相对 3x3 中值：平滑谱积分通常偏低约 2%-3%
```

因此当前默认采用 3x3 作为保守折中。

## 4. TPS 能量刻度

核心实现位于 `SolveSpectrum._spectrum_geometry()`。

### 4.1 磁场偏转常数

$$
L_B = \left(\frac{L}{2} + D\right)L
$$

$$
T_B = Z B L_B \times 0.00998115
$$

其中：

```text
B: 磁场强度
Z: 离子电荷数
L, D: TPS 几何长度参数
```

### 4.2 能量与 X 坐标关系

对每个像素列 `X`：

$$
E(X) = \frac{1}{2A}\left[\frac{T_B}{(X-X_0)\,\mathrm{Res}}\right]^2
$$

其中：

```text
E: 能量，MeV
A: 质量数
X0: TPS 原点 X 像素
Res: 空间分辨率，mm/pixel
```

因此 TPS 能量 bin 不是等间隔的。程序用相邻像素边界计算每个 bin 的能量宽度：

$$
\Delta E_i = E(X_i-0.5)-E(X_i+0.5)
$$

### 4.3 电场偏转与 Y 坐标

电场等效偏转常数：

$$
L_{E1}=\frac{L_1D_1+L_1L_2+L_1^2/2}{d}
$$

$$
L_{E2}=\frac{\ln\left(\frac{L_2+L_3}{L_3}\right)(L_2+L_3+D_1)-L_2}{\theta}
$$

$$
L_E=\frac{L_{E1}+L_{E2}}{2}
$$

$$
T_E=\frac{U Z L_E}{10^6}
$$

理论轨迹中心：

$$
Y_\mathrm{center}(E)=Y_0+\frac{T_E}{E\,\mathrm{Res}}
$$

积分带：

$$
Y_{\min}=\left\lfloor Y_{\mathrm{center}}-dY\right\rfloor
$$

$$
Y_{\max}=\left\lceil Y_{\mathrm{center}}+dY\right\rceil
$$

`dY` 是 UI 中的 `±dY`，单位为像素。

## 5. 接收立体角

程序使用准直孔几何估计接收立体角：

$$
\Omega_0=\frac{\pi(S_1/2)^2}{L_0^2}
$$

考虑 `dY` 积分宽度可能小于理论接收宽度，程序再乘以修正因子：

$$
dY_{\max}=\left\lceil\frac{S_1/2}{L_0}\frac{L_0+D+L}{\mathrm{Res}}\right\rceil
$$

$$
\Omega=\Omega_0\min\left(1,\frac{2dY}{2dY_{\max}}\right)
$$

最终能谱纵轴按当前代码是“相机 count 经 EMGain、QE、MCP 响应、能量 bin 宽度和接收立体角归一化后的谱强度”：

```text
corrected counts MeV^-1 sr^-1
```

只有当 `EMGain`、`QE` 和 MCP 文件第二列都已经完成绝对粒子数标定时，才可进一步解释为：

```text
particles MeV^-1 sr^-1
```

## 6. 背景提取

当前主流程使用 `SolveSpectrumSideband()`。它支持两种背景模式：

```text
同形偏移 offset
上下旁带 sideband
```

### 6.1 中心带

对每个能量 bin，也就是每个 X 列：

$$
C_{\mathrm{center}}=\sum_{y=Y_{\min}}^{Y_{\max}} I(y,X)
$$

$$
N_{\mathrm{center}}=\mathrm{number\ of\ pixels\ in\ center\ band}
$$

`center_sum` 是中心带原始积分，包含信号和背景。

### 6.2 同形偏移背景

当前默认背景模式是 `同形偏移`。

背景采样区域沿同一条理论抛物线形状整体平移：

$$
y_\mathrm{bg}=y_\mathrm{center}+\Delta y_\mathrm{bg}
$$

$$
y_{\mathrm{bg},\min}=y_\mathrm{bg}-\frac{w_\mathrm{bg}}{2},\qquad
y_{\mathrm{bg},\max}=y_\mathrm{bg}+\frac{w_\mathrm{bg}}{2}
$$

UI 参数：

```text
偏移(px): background_offset
宽度(px): background_width
```

这种方式适合背景云团也跟随轨迹附近形态变化的情况。

### 6.3 上下旁带背景

如果选择 `上下旁带`，程序在中心带上下两侧采样：

```text
lower sideband: center_ymin - gap - width 到 center_ymin - gap
upper sideband: center_ymax + gap 到 center_ymax + gap + width
```

当前默认：

```text
gap = max(2, dY)
width = max(4, 2*dY)
```

### 6.4 背景水平估计

不论使用哪种背景模式，程序把采样到的背景像素合并为 `sideband`，并用中位数估计背景水平：

$$
B_\mathrm{level}=\mathrm{median}(\mathrm{sideband})
$$

背景涨落估计：

$$
\sigma_B = 1.4826\,\mathrm{median}\left(|\mathrm{sideband}-B_\mathrm{level}|\right)
$$

如果 MAD 为 0，则退化为标准差：

$$
\sigma_B=\mathrm{std}(\mathrm{sideband})
$$

## 7. 能谱强度计算

MCP 效率文件由 `mcp-proton.txt` 提供，两列为：

```text
Energy(MeV)    efficiency_or_response
```

程序对当前能量 `E_i` 进行线性插值，得到：

$$
\eta_\mathrm{MCP}(E_i)
$$

相机 count 先除以：

$$
\mathrm{EMGain}\times QE
$$

然后除以 MCP 效率、能量 bin 宽度和接收立体角：

$$
I_i=\frac{C_i}{\mathrm{EMGain}\,QE\,\eta_\mathrm{MCP}(E_i)\,\Delta E_i\,\Omega}
$$

这里 `I_i` 的代码单位更严格地说是：

```text
corrected counts MeV^-1 sr^-1
```

如果 MCP 文件、EMGain 和 QE 已经被标定到绝对粒子数，则可写成：

```text
particles MeV^-1 sr^-1
```

注意：当前代码直接使用 MCP 文件第二列作为分母。如果第二列是百分比、相对响应或未归一化响应，需要在实验标定中统一定义，否则绝对强度会有比例误差。

## 8. 当前保存的四类能谱

点击 `保存当前能谱` 后，程序保存 PNG 图和 TXT 数据。

TXT 表头为：

```text
Energy_MeV
d2N_dE_dOmega_raw_center
d2N_dE_dOmega_background_subtracted
d2N_dE_dOmega_smoothed
d2N_dE_dOmega_background
```

### 8.1 `Energy_MeV`

能量轴：

$$
E_i=\frac{1}{2A}\left[\frac{T_B}{(X_i-X_0)\,\mathrm{Res}}\right]^2
$$

单位：

```text
MeV
```

### 8.2 `d2N_dE_dOmega_raw_center`

中心带原始积分谱：

$$
C_\mathrm{raw}=\sum(\mathrm{center})
$$

$$
I_\mathrm{raw}=\frac{C_\mathrm{raw}}{\mathrm{EMGain}\,QE\,\eta_\mathrm{MCP}\,\Delta E\,\Omega}
$$

特点：

```text
包含轨迹信号
包含中心带背景
最接近“原始很抖”的能谱曲线
```

单位：

```text
corrected counts MeV^-1 sr^-1
```

若探测链路已绝对标定，可解释为 `particles MeV^-1 sr^-1`。

### 8.3 `d2N_dE_dOmega_background_subtracted`

扣背景后的净谱：

$$
C_\mathrm{net}=\sum(\mathrm{center})-B_\mathrm{level}N_\mathrm{center}
$$

$$
I_\mathrm{net}=\frac{C_\mathrm{net}}{\mathrm{EMGain}\,QE\,\eta_\mathrm{MCP}\,\Delta E\,\Omega}
$$

当前实现中，如果 `C_net <= 0`，校准函数会用一个极小正数 `1e-30` 代替，以便在对数坐标中绘图。因此高能端可能出现非常接近 0 的数值。

单位：

```text
corrected counts MeV^-1 sr^-1
```

若探测链路已绝对标定，可解释为 `particles MeV^-1 sr^-1`。

### 8.4 `d2N_dE_dOmega_smoothed`

对扣背景净谱做平滑后的曲线。

当前算法：

```text
1. 只取 y > 0 的有效点
2. 按能量升序排序
3. 在 log10(y) 空间中设置 floor
4. 做窗口为 spectrumSmoothWindow 的中值滤波
5. 再做同窗口移动平均
6. 平滑结果限制在局部原始范围内，避免 Savitzky-Golay 式过冲
7. 插值回原始能量顺序
```

核心目的：

```text
去掉高频抖动
不生成超过局部原始范围的虚假尖峰
在高能端接近背景时自动压低
```

单位：

```text
corrected counts MeV^-1 sr^-1
```

若探测链路已绝对标定，可解释为 `particles MeV^-1 sr^-1`。

### 8.5 `d2N_dE_dOmega_background`

背景水平谱：

$$
I_{B,\mathrm{level}}=\frac{B_\mathrm{level}}{\mathrm{EMGain}\,QE\,\eta_\mathrm{MCP}\,\Delta E\,\Omega}
$$

重要说明：

```text
当前保存的 background 是背景水平，不是中心带等效背景积分。
```

也就是说它不是：

$$
B_\mathrm{level}N_\mathrm{center}
$$

因此它适合观察背景趋势和噪声水平，但如果要和 `raw_center` 做严格逐点相减，应使用：

$$
B_\mathrm{equiv}=B_\mathrm{level}N_\mathrm{center}
$$

当前 TXT 尚未单独保存 `background_equivalent_center_band`。如需更严格的数据产品，建议后续增加该列。

## 9. 能谱图显示

当前能谱图显示：

```text
Raw center-band
Raw background
Background-subtracted
Smoothed background-subtracted
```

纵轴标签当前写成：

$$
\frac{d^2N}{dE\,d\Omega}\quad(\mathrm{protons/ions}\;\mathrm{MeV}^{-1}\,\mathrm{sr}^{-1})
$$

这是实验解释标签。严格性取决于 MCP、EMGain、QE 是否完成绝对标定；代码实际做的是 corrected-count 归一化。

如果解谱粒子是 `A=1, Z=1`，图上显示为 `protons`；否则显示为 `ions`。

## 10. 截止能量

当前自动截止能量主要基于平滑后的扣背景谱和背景曲线比较。

逻辑上要求：

```text
signal > background
signal / background >= threshold
连续若干 bin 满足条件
```

当前 UI 中仍保留手动 cursor 选择截止能量。手动选择不会被禁用。

建议论文或正式报告中说明：

```text
自动截止能量仅作为参考
最终截止能量应结合图像轨迹末端、背景曲线和人工判断
```

## 11. 手工 Mask

手工 Mask 功能用于人工勾选轨迹区域，主要目标是：

```text
清理轨迹外“陨石带”杂散信号
保存分割标签，供未来训练视觉分割网络使用
改善显示图和导出图
```

当前 Mask 不直接改变能谱计算。

Mask 工作流：

```text
开始绘制
在图像上逐点点击多边形
闭合
应用显示
保存
读取
清除
```

保存内容包括：

```text
二值 mask png
overlay png
json 元数据
```

多次保存同一 shot 的不同粒子区域时，程序会合并已有 polygon/mask，适合先画质子，再画 C/O 离子。

## 12. Mask 外背景清理

应用 Mask 后：

```text
Mask 内保持原图
Mask 外作为背景区域处理
```

当前显示清理逻辑：

```text
1. 统计 Mask 外像素
2. 取指定背景分位数 bg_percentile
3. Mask 外高亮点先被截断到该背景水平
4. 对背景做中值滤波和高斯平滑
5. Mask 内像素替换回原始值
```

UI 参数：

```text
Mask背景半径
背景分位
```

这两个参数只影响显示图，不影响定量能谱。

## 13. 理论轨迹显示清理

`理论轨迹显示清理` 使用 TPS 理论抛物线保护常见粒子轨迹，然后清理轨迹外背景。

相关参数：

```text
轨迹保护宽度
羽化半径
```

含义：

```text
轨迹保护宽度: 理论轨迹中心线上下各保护多少像素
羽化半径: 保护区边缘向外柔和过渡的像素距离
```

该功能只更新显示图，不改变能谱。

有手工 Mask 后，推荐优先使用手工 Mask。理论轨迹显示清理适合快速预览，但如果理论线和真实轨迹有偏差，可能造成显示上的误清理。

## 14. 视觉分割网络标签

如果后续训练 U-Net 或其他分割网络，推荐标签定义为：

```text
1: 真实粒子轨迹区域
0: 背景和杂散信号区域
```

当前手工 Mask 保存的二值图即可作为初始训练标签。

建议标注策略：

```text
轨迹主体必须覆盖
轨迹边缘可稍微外扩
明显的陨石带不要标为轨迹
不同粒子可以先合并为同一前景类
如果要区分 H/C/O，需要未来扩展多类别 mask
```

## 15. 当前实现限制与建议

### 15.1 背景列的定义

当前保存的 `background` 是背景水平谱，不是中心带等效背景积分。为了严格复现：

```text
raw_center - background_equivalent = background_subtracted
```

建议后续在保存文件中增加：

```text
d2N_dE_dOmega_background_equivalent_center_band
```

### 15.2 高能端低计数

TPS 高能端通常计数低，容易出现：

```text
单 bin 偶然偏高
扣背景后接近 0
平滑线依赖窗口参数
```

因此高能截止不应只看平滑曲线，应同时查看：

```text
原始中心带
背景曲线
扣背景曲线
图像轨迹末端
手动 cursor 位置
```

### 15.3 绝对强度标定

绝对强度依赖：

```text
EMGain
QE
MCP 效率文件
接收立体角
dE
```

这些参数中任意一个定义不一致，都会导致整体强度比例变化。

## 16. 实际数据验证摘要

使用 `D:\software\PW-TPS稳定性\Shot41.tif` 保存能谱测试：

```text
输出 TXT: 728 行 x 5 列
Energy: 约 100.68 MeV 到 5.28 MeV
raw_center: 约 2.37e8 到 1.25e11
background_subtracted: 可接近 0，到约 1.13e11
smoothed: 约 6.03e6 到 9.40e10
background: 约 3.23e7 到 4.90e9
```

使用 `Shot41-49.tif` 对定量预处理做对比：

```text
none 相对 3x3 中值：平滑谱积分通常偏高约 1%-3%
5x5 相对 3x3 中值：平滑谱积分通常偏低约 2%-3%
```

因此当前推荐：

```text
定量解谱: 固定 3x3 热像素中值
显示预览: 原图 / 中值3x3 / 中值5x5 按需要切换
背景清理: 优先使用手工 Mask
```
