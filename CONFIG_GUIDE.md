# PyTPS 配置指南

PyTPS 是用于 Thomson Parabola Spectrometer (TPS) 图像解谱的 Python 程序。仓库已包含一组样例 TPS 图像，可用于验证程序能否正常读图、滤波和解谱。

## 1. 环境准备

建议使用 Python 3.9 或更新版本。

安装常用依赖：

```bash
pip install numpy scipy matplotlib imageio PySide6 scikit-image
```

如果需要运行 Windows 自动触发相关功能，再安装：

```bash
pip install pywin32
```

在 Linux/WSL 中，`pywin32` 不可用，自动操作 Andor/Mosaic 窗口的功能不能运行，但离线解谱不受影响。

## 2. 运行程序

在仓库根目录执行：

```bash
python PyTPS.py
```

程序启动后，主要配置来自：

- `PyTPS_init.ini`：图像路径、保存路径、解谱范围、滤波参数。
- `TPS_Settings.ini`：TPS 磁场、电压、几何尺寸、相机增益等仪器参数。
- `mcp-proton.txt`：MCP 对质子的能量响应或效率修正表。

## 3. 样例数据

仓库内置样例数据：

```text
sample_data/PW-TPS-stability/
```

包含：

```text
Shot41.tif
Shot42.tif
Shot43.tif
Shot44.tif
Shot45.tif
Shot46.tif
Shot47.tif
Shot48.tif
Shot49.tif
```

这些文件来自本地实验数据目录：

```text
D:\software\PW-TPS稳定性
```

从 GitHub clone 后，如果想直接使用仓库内样例数据，可把 `PyTPS_init.ini` 中的 `imagepath` 改成：

```text
imagepath=	./sample_data/PW-TPS-stability
```

保存路径可改成仓库内或任意本地目录，例如：

```text
savepath=	./output
```

如果 `output` 目录不存在，需要先创建：

```bash
mkdir -p output
```

## 4. 核心解谱参数

`PyTPS_init.ini` 中常用参数：

```text
X0=	81
Y0=	465
±dY=	3
Emin=	0.0
Emax=	100.0
specEmin=	0.0
specEmax=	100.0
specWindow=	0.5
filterMode=	median3
```

含义：

- `X0`, `Y0`：TPS 原点位置，程序内部使用左下角为原点的物理坐标。
- `±dY`：沿理论谱线中心上下积分的像素半宽。
- `Emin`, `Emax`：解谱能量范围，单位 $\mathrm{MeV}$。
- `specEmin`, `specEmax`：能谱图显示范围。
- `specWindow`：自动截止能量搜索窗口宽度，单位 $\mathrm{MeV}$。
- `filterMode`：显示滤波模式。当前常用值为 `none`、`median3`、`median5`。显示滤波不改变定量能谱。

## 5. TPS 仪器参数

`TPS_Settings.ini` 中参数会直接进入能量和强度计算：

```text
B=	0.56
U=	20000
EMGain=	200
S1=	0.3
Res=	0.0979
L=	100
D=	484
L0=	1500
QE=	0.8
```

其中：

- `B`：磁场强度。
- `U`：电场偏转电压。
- `EMGain`：相机 EM 增益。
- `QE`：相机量子效率或等效探测效率。
- `Res`：图像空间分辨率，单位 $\mathrm{mm}/\mathrm{pixel}$。
- `S1`, `L0`：用于计算接收立体角。

能谱强度计算会除以 `EMGain * QE`、MCP 响应、能量 bin 宽度和接收立体角。因此这些参数会影响纵轴绝对数值。只有探测链路完成绝对标定时，纵轴才能严格解释为粒子数谱强度。

## 6. MCP 效率文件

默认 MCP 文件：

```text
mcp-proton.txt
```

文件为两列 tab 分隔数据：

```text
Energy(MeV)	MCP_efficiency_or_response
```

当前代码直接使用第二列作为效率修正分母，不会自动除以 100。若第二列实际是百分比，需要确认是否应先转换为小数，否则绝对强度会差约 100 倍。

## 7. GitHub 使用建议

克隆仓库：

```bash
git clone git@github.com:zxc123aa/Pytps.git
cd Pytps
```

更新代码或数据后提交：

```bash
git add .
git commit -m "Update configuration or sample data"
git push
```

如果新增大量原始实验数据，建议只提交少量代表性样例。大批量数据更适合放在外部数据盘、GitHub Release、云盘或 Git LFS 中。
