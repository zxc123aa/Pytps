#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TCompare.py - 质子谱线对比模块
用于提取并对比多个TPS图像的质子谱线，消除电场偏移影响

作者：PyTPS团队
日期：2025-11-13
修改：2025-11-13 - 使用subplot方式，紧密堆叠多个子图
"""

import numpy as np
import TSettings
from PySide6 import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm

# 设置matplotlib中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False


def findProtonLineContour(imageData, X0, Y0, dY, Xmin, Xmax):
    """
    追踪质子谱线的实际轮廓（数据驱动方法）

    Parameters:
    -----------
    imageData : ndarray
        图像数据（已翻转）
    X0, Y0 : int
        原点坐标（像素）
    dY : int
        搜索窗口半宽（像素）
    Xmin, Xmax : int
        X范围（像素）

    Returns:
    --------
    contour_y : ndarray
        每一列X对应的质子线Y位置（像素坐标）
    """
    contour_y = np.zeros(imageData.shape[1])

    for x in range(imageData.shape[1]):
        if x < Xmin or x > Xmax:
            contour_y[x] = Y0
            continue

        # 在Y0附近搜索信号最强的位置（实际质子线位置）
        search_range = 4 * dY  # 扩大搜索范围
        y_min = max(0, Y0 - search_range)
        y_max = min(imageData.shape[0], Y0 + search_range + 1)

        # 提取这一列
        column = imageData[y_min:y_max, x]

        if len(column) > 0 and np.max(column) > 0:
            # 找到信号最强的位置（质子线中心）
            # 使用加权平均获得亚像素精度
            threshold = np.max(column) * 0.3  # 30%阈值
            above_threshold = column > threshold

            if np.any(above_threshold):
                # 计算质心位置
                indices = np.arange(len(column))
                weights = column * above_threshold
                if np.sum(weights) > 0:
                    centroid = np.sum(indices * weights) / np.sum(weights)
                    contour_y[x] = y_min + centroid
                else:
                    contour_y[x] = Y0
            else:
                contour_y[x] = Y0
        else:
            contour_y[x] = Y0

    # 平滑轮廓（去除噪声）
    from scipy.ndimage import median_filter
    contour_y[Xmin:Xmax+1] = median_filter(contour_y[Xmin:Xmax+1], size=5)

    return contour_y


def compensateElectricField(imageData, TPS, X0, Y0, A, Z, Emin, Emax, dY):
    """
    补偿电场偏移 - 使用理论公式+局部轮廓微调

    Parameters:
    -----------
    imageData : ndarray
        图像数据（已翻转）
    TPS : TPS对象
        TPS参数
    X0, Y0 : int
        原点坐标（像素）
    A, Z : int
        粒子质量数和电荷数
    Emin, Emax : float
        能量范围（MeV）
    dY : int
        提取窗口半宽（像素）

    Returns:
    --------
    compensatedImage : ndarray
        补偿后的图像（质子谱线在Y0位置）
    yRange : tuple
        显示的Y范围 (ymin, ymax)，像素坐标
    xRange : tuple
        显示的X范围 (xmin, xmax)，像素坐标
    newY0 : int
        补偿后图像中Y0的位置（像素）
    """

    # 计算磁场偏转参数
    LB = (TPS.L / 2 + TPS.D) * TPS.L
    TB = Z * TPS.B * LB * 0.00998115

    # 计算电场偏转参数
    LE1 = (TPS.L1 * TPS.D1 + TPS.L1 * TPS.L2 + TPS.L1 ** 2 / 2) / TPS.d
    LE2 = (np.log((TPS.L2 + TPS.L3) / TPS.L3) * (TPS.L2 + TPS.L3 + TPS.D1) - TPS.L2) / TPS.theta
    LE = (LE1 + LE2) / 2
    TE = TPS.U * Z * LE / 1000000

    # 确定X范围
    if Emin == 0:
        Xmax = imageData.shape[1] - 1
    else:
        Xmax = int(np.ceil(X0 + TB / np.sqrt(2 * A * Emin) / TPS.Res))
        Xmax = min(Xmax, imageData.shape[1] - 1)

    Xmin = max(0, int(np.floor(X0 + TB / np.sqrt(2 * A * Emax) / TPS.Res)))

    # 创建补偿后的图像（足够支持用户调整显示范围）
    compensatedHeight = max(16 * dY + 1, 400)  # 至少400像素高，支持最大300像素显示
    compensatedWidth = imageData.shape[1]
    compensatedImage = np.zeros((compensatedHeight, compensatedWidth), dtype=imageData.dtype)

    # 补偿后的Y0在新图像中的位置（中心）
    newY0 = compensatedHeight // 2

    # 对每一列进行处理
    for x in range(Xmin, Xmax + 1):
        if x <= X0 or x >= imageData.shape[1]:
            continue

        # 1. 先用理论公式计算抛物线位置
        E = (TB / ((x - X0) * TPS.Res)) ** 2 / (2 * A)
        electricDeflection = TE / (E * TPS.Res)
        parabola_y_theory = Y0 + electricDeflection

        # 2. 在理论位置附近搜索实际信号峰值（局部微调）
        # 动态调整搜索范围：低能处（X大）需要更大的搜索范围
        energy_factor = max(1.0, Emax / E) if E > 0.1 else 3.0  # 低能放大搜索范围
        search_radius = int(dY * 1.2 * min(energy_factor, 3.0))  # 最大3倍dY
        search_y_min = max(0, int(parabola_y_theory) - search_radius)
        search_y_max = min(imageData.shape[0], int(parabola_y_theory) + search_radius + 1)

        # 提取搜索区域
        search_column = imageData[search_y_min:search_y_max, x]

        if len(search_column) > 0 and np.max(search_column) > 0:
            # 改进的质心计算：使用强度的平方作为权重（更关注峰值）
            # 先去除背景
            bg_level = np.percentile(search_column, 10)  # 10%分位数作为背景
            signal = search_column - bg_level
            signal[signal < 0] = 0

            if np.sum(signal) > 0:
                # 使用平方权重计算质心（更聚焦于强信号中心）
                indices = np.arange(len(search_column))
                weights = signal ** 2  # 平方权重
                centroid = np.sum(indices * weights) / np.sum(weights)
                actual_parabola_y = search_y_min + centroid
            else:
                actual_parabola_y = parabola_y_theory
        else:
            actual_parabola_y = parabola_y_theory

        # 3. 从实际轮廓位置提取数据
        # 提取足够大的范围，支持用户调整显示区域
        extract_range = 150  # 提取上下各150像素，支持最大300像素显示范围

        src_y_center = int(np.round(actual_parabola_y))
        src_y_min = max(0, src_y_center - extract_range)
        src_y_max = min(imageData.shape[0], src_y_center + extract_range + 1)

        # 提取源数据
        source_data = imageData[src_y_min:src_y_max, x]

        # 4. 放到补偿图像的Y0位置（向下移）
        dst_y_min = newY0 - extract_range
        dst_y_max = newY0 + extract_range + 1

        # 计算实际能复制的数据长度
        copy_length = min(len(source_data), dst_y_max - dst_y_min)

        if copy_length > 0 and dst_y_min >= 0 and dst_y_max <= compensatedHeight:
            # 居中放置
            src_offset = (len(source_data) - copy_length) // 2
            compensatedImage[dst_y_min:dst_y_min + copy_length, x] = \
                source_data[src_offset:src_offset + copy_length]

    # 确定显示的Y范围
    y_extend = 3 * dY + 15
    ymin = max(0, newY0 - y_extend)
    ymax = min(compensatedHeight, newY0 + y_extend)

    return compensatedImage, (ymin, ymax), (Xmin, Xmax), newY0


def compensateElectricField_Original(imageData, TPS, X0, Y0, A, Z, Emin, Emax, dY):
    """
    补偿电场偏移，将沿抛物线的质子谱线"拉直"到Y0位置

    Parameters:
    -----------
    imageData : ndarray
        图像数据（已翻转）
    TPS : TPS对象
        TPS参数
    X0, Y0 : int
        原点坐标（像素）
    A, Z : int
        粒子质量数和电荷数
    Emin, Emax : float
        能量范围（MeV）
    dY : int
        提取窗口半宽（像素）

    Returns:
    --------
    compensatedImage : ndarray
        补偿后的图像（质子谱线在Y0位置）
    yRange : tuple
        显示的Y范围 (ymin, ymax)，像素坐标
    xRange : tuple
        显示的X范围 (xmin, xmax)，像素坐标
    newY0 : int
        补偿后图像中Y0的位置（像素）
    """

    # 计算磁场偏转参数
    LB = (TPS.L / 2 + TPS.D) * TPS.L
    TB = Z * TPS.B * LB * 0.00998115

    # 计算电场偏转参数
    LE1 = (TPS.L1 * TPS.D1 + TPS.L1 * TPS.L2 + TPS.L1 ** 2 / 2) / TPS.d
    LE2 = (np.log((TPS.L2 + TPS.L3) / TPS.L3) * (TPS.L2 + TPS.L3 + TPS.D1) - TPS.L2) / TPS.theta
    LE = (LE1 + LE2) / 2
    TE = TPS.U * Z * LE / 1000000

    # 确定X范围
    if Emin == 0:
        Xmax = imageData.shape[1] - 1
    else:
        Xmax = int(np.ceil(X0 + TB / np.sqrt(2 * A * Emin) / TPS.Res))
        Xmax = min(Xmax, imageData.shape[1] - 1)

    Xmin = max(0, int(np.floor(X0 + TB / np.sqrt(2 * A * Emax) / TPS.Res)))

    # 创建补偿后的图像（增大高度）
    compensatedHeight = 8 * dY + 1
    compensatedWidth = imageData.shape[1]
    compensatedImage = np.zeros((compensatedHeight, compensatedWidth), dtype=imageData.dtype)

    # 补偿后的Y0在新图像中的位置（中心）
    newY0 = compensatedHeight // 2

    # 对每一列进行处理：从抛物线位置提取数据，放到Y0位置
    for x in range(Xmin, Xmax + 1):
        if x <= X0 or x >= imageData.shape[1]:
            continue

        # 计算该X位置对应的能量
        E = (TB / ((x - X0) * TPS.Res)) ** 2 / (2 * A)

        # 计算电场造成的Y偏移（像素）
        electricDeflection = TE / (E * TPS.Res)
        parabola_y = Y0 + electricDeflection

        # 提取更大范围的背景
        extract_range = 3 * dY

        # 从原图的抛物线位置提取数据
        src_y_center = int(np.round(parabola_y))
        src_y_min = max(0, src_y_center - extract_range)
        src_y_max = min(imageData.shape[0], src_y_center + extract_range + 1)

        # 提取源数据
        source_data = imageData[src_y_min:src_y_max, x]

        # 放到补偿图像的Y0位置
        dst_y_min = newY0 - extract_range
        dst_y_max = newY0 + extract_range + 1

        # 计算实际能复制的数据长度
        copy_length = min(len(source_data), dst_y_max - dst_y_min)

        if copy_length > 0 and dst_y_min >= 0 and dst_y_max <= compensatedHeight:
            # 居中放置
            src_offset = (len(source_data) - copy_length) // 2
            compensatedImage[dst_y_min:dst_y_min + copy_length, x] = \
                source_data[src_offset:src_offset + copy_length]

    # 确定显示的Y范围
    y_extend = 3 * dY + 15
    ymin = max(0, newY0 - y_extend)
    ymax = min(compensatedHeight, newY0 + y_extend)

    return compensatedImage, (ymin, ymax), (Xmin, Xmax), newY0


class CompareWindow(QtWidgets.QMainWindow):
    """
    质子谱线对比窗口
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("质子谱线对比 (Proton Spectrum Comparison)")
        self.resize(1200, 650)  # 合理的初始窗口大小

        # Main layout
        centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(centralWidget)
        mainLayout = QtWidgets.QVBoxLayout(centralWidget)

        # Control area
        controlLayout = QtWidgets.QHBoxLayout()

        self.fileList = QtWidgets.QListWidget()
        self.fileList.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.fileList.setMaximumHeight(150)
        controlLayout.addWidget(QtWidgets.QLabel("选择要对比的图像："))
        controlLayout.addWidget(self.fileList)

        # 能量刻度自定义输入
        energyLayout = QtWidgets.QVBoxLayout()
        energyLayout.addWidget(QtWidgets.QLabel("自定义能量刻度 (MeV)："))
        self.energyTicksInput = QtWidgets.QLineEdit()
        self.energyTicksInput.setPlaceholderText("例如：5, 10, 15, 20, 25, 30 或留空自动生成")
        self.energyTicksInput.setMaximumHeight(30)
        energyLayout.addWidget(self.energyTicksInput)

        # Y方向显示范围调整（按像素拓展）
        yRangeLayout = QtWidgets.QHBoxLayout()
        yRangeLayout.addWidget(QtWidgets.QLabel("Y显示范围 (像素)："))
        self.yRangeSpinBox = QtWidgets.QSpinBox()
        self.yRangeSpinBox.setRange(1, 500)  # 范围1-500像素
        self.yRangeSpinBox.setValue(80)  # 默认80像素（上下各40）
        self.yRangeSpinBox.setSingleStep(1)  # 步长1像素
        self.yRangeSpinBox.setSuffix(" px")
        self.yRangeSpinBox.setMaximumWidth(120)
        yRangeLayout.addWidget(self.yRangeSpinBox)
        yRangeLayout.addWidget(QtWidgets.QLabel("(质子线上下各显示一半)"))
        yRangeLayout.addStretch()
        energyLayout.addLayout(yRangeLayout)

        # Gamma校正（非线性colorbar）
        gammaLayout = QtWidgets.QHBoxLayout()
        gammaLayout.addWidget(QtWidgets.QLabel("Gamma校正："))
        self.gammaSpinBox = QtWidgets.QDoubleSpinBox()
        self.gammaSpinBox.setRange(0.01, 10.0)
        self.gammaSpinBox.setValue(1.0)  # 默认线性
        self.gammaSpinBox.setSingleStep(0.01)
        self.gammaSpinBox.setDecimals(2)
        self.gammaSpinBox.setMaximumWidth(80)
        self.gammaSpinBox.setToolTip("gamma<1: 增强低计数区域细节\ngamma=1: 线性\ngamma>1: 压缩低计数区域")
        gammaLayout.addWidget(self.gammaSpinBox)
        gammaLayout.addWidget(QtWidgets.QLabel("(<1 增强弱信号)"))
        gammaLayout.addStretch()
        energyLayout.addLayout(gammaLayout)

        # Colorbar范围调节
        colorbarLayout = QtWidgets.QHBoxLayout()
        colorbarLayout.addWidget(QtWidgets.QLabel("Colorbar范围："))
        colorbarLayout.addWidget(QtWidgets.QLabel("最小值"))
        self.colorMinSpinBox = QtWidgets.QSpinBox()
        self.colorMinSpinBox.setRange(0, 100000)
        self.colorMinSpinBox.setValue(0)
        self.colorMinSpinBox.setSingleStep(1)
        self.colorMinSpinBox.setMaximumWidth(100)
        colorbarLayout.addWidget(self.colorMinSpinBox)
        colorbarLayout.addWidget(QtWidgets.QLabel("最大值"))
        self.colorMaxSpinBox = QtWidgets.QSpinBox()
        self.colorMaxSpinBox.setRange(1, 100000)
        self.colorMaxSpinBox.setValue(65536)
        self.colorMaxSpinBox.setSingleStep(100)
        self.colorMaxSpinBox.setMaximumWidth(100)
        colorbarLayout.addWidget(self.colorMaxSpinBox)
        colorbarLayout.addStretch()
        energyLayout.addLayout(colorbarLayout)

        controlLayout.addLayout(energyLayout)

        buttonLayout = QtWidgets.QVBoxLayout()
        self.btnCompare = QtWidgets.QPushButton("生成对比图")
        self.btnCompare.clicked.connect(self.generateComparison)
        self.btnClear = QtWidgets.QPushButton("清除")
        self.btnClear.clicked.connect(self.clearComparison)
        buttonLayout.addWidget(self.btnCompare)
        buttonLayout.addWidget(self.btnClear)
        buttonLayout.addStretch()
        controlLayout.addLayout(buttonLayout)

        mainLayout.addLayout(controlLayout)

        # Image display area
        self.figure = plt.figure(figsize=(12, 6))  # 合理的初始大小
        self.canvas = FigureCanvas(self.figure)
        mainLayout.addWidget(self.canvas)

        # Data storage
        self.parentApp = None
        self.comparisonData = []

    def setParentApp(self, app):
        """设置父应用程序以访问参数"""
        self.parentApp = app

    def updateFileList(self, fileList):
        """更新文件列表"""
        self.fileList.clear()
        self.fileList.addItems(fileList)

    def _generateAutoEnergyTicks(self, E_min, E_max):
        """自动生成能量刻度"""
        energy_ticks = []
        if E_max >= 10:
            # 高能范围：10, 15, 20, 25, ...
            energy_ticks.extend(np.arange(10, min(E_max, 50) + 1, 5))
        if E_min < 10:
            # 低能范围：1, 2, 3, 4, 5, 6, 7, 8, 9
            energy_ticks.extend(np.arange(max(1, int(E_min)), 10, 1))

        return sorted(set(energy_ticks), reverse=True)  # 去重并降序排序

    def generateComparison(self):
        """生成对比图"""
        if self.parentApp is None:
            print("[TCompare] 错误：未设置父应用程序")
            return

        selectedItems = self.fileList.selectedItems()
        if len(selectedItems) == 0:
            print("[TCompare] 请至少选择一个图像")
            return

        # Import necessary modules
        import TImageRead
        import TFilter
        import os

        # Clear previous data
        self.comparisonData = []

        # Process each selected file
        for item in selectedItems:
            fileName = item.text()
            filePath = os.path.join(self.parentApp.imagePath, fileName)

            if not os.path.isfile(filePath):
                print(f"[TCompare] 文件未找到：{filePath}")
                continue

            # Read and filter image
            img, is8bit = TImageRead.readImage(filePath)
            filterParams = {
                'medianSize': self.parentApp.medianSize,
                'medianIterations': self.parentApp.medianIterations,
                'morphologicalSize': self.parentApp.morphologicalSize,
                'rollingBallRadius': self.parentApp.rollingBallRadius
            }
            img = TFilter.applyFilter(img, self.parentApp.filterMode, filterParams)
            imageData = np.flipud(img)

            # 补偿电场偏移（使用固定的dY保证轮廓追踪准确）
            compensatedImage, yRange, xRange, newY0 = compensateElectricField(
                imageData,
                self.parentApp.TPS,
                self.parentApp.X0,
                self.parentApp.Y0,
                self.parentApp.A,
                self.parentApp.Z,
                self.parentApp.Emin,
                self.parentApp.Emax,
                self.parentApp.dY  # 使用固定dY
            )

            self.comparisonData.append({
                'fileName': fileName,
                'image': compensatedImage,
                'yRange': yRange,
                'xRange': xRange,
                'newY0': newY0
            })

            print(f"[TCompare] 已处理：{fileName}, 图像形状：{compensatedImage.shape}")

        # Draw comparison plot
        self.drawComparison()

    def drawComparison(self):
        """
        绘制对比图 - 单个axes + 垂直拼接 + 人为分割
        """
        if len(self.comparisonData) == 0:
            print("[TCompare] 没有数据可显示")
            return

        self.figure.clf()
        nImages = len(self.comparisonData)

        # 找到所有图像的共同X范围
        all_xmin = min(data['xRange'][0] for data in self.comparisonData)
        all_xmax = max(data['xRange'][1] for data in self.comparisonData)

        X0_orig = self.parentApp.X0
        Res = self.parentApp.TPS.Res

        # 从UI获取Y显示范围（像素）
        strip_height_px = self.yRangeSpinBox.value()
        strip_height_mm = strip_height_px * Res

        print(f"[TCompare] Y显示范围：{strip_height_px} 像素 ({strip_height_mm:.2f} mm)，质子线上下各 {strip_height_px//2} 像素")

        # ===== 垂直拼接所有图像 =====
        imageStrips = []
        y0_positions = []  # 每个图像的Y0位置（物理坐标mm）
        split_positions = []  # 分割线位置（物理坐标mm）
        filenames = []

        current_y_offset = 0  # 当前Y偏移（物理坐标mm）

        for i, data in enumerate(self.comparisonData):
            newY0 = data['newY0']

            # 使用用户设置的Y显示范围（上下拓展）
            strip_y_min = max(0, newY0 - strip_height_px // 2)
            strip_y_max = min(data['image'].shape[0], newY0 + strip_height_px // 2)

            # 提取图像条带（保留完整的用户指定范围，不自动裁剪空白）
            imageRegion = data['image'][strip_y_min:strip_y_max, all_xmin:all_xmax]

            imageStrips.append(imageRegion)

            # 计算Y0在拼接图中的位置
            y0_in_strip = (newY0 - strip_y_min) * Res  # Y0在当前条带中的位置
            y0_in_combined = current_y_offset + y0_in_strip  # Y0在整个拼接图中的位置
            y0_positions.append(y0_in_combined)

            filenames.append(data['fileName'])

            # 更新偏移（使用实际高度）
            strip_height = imageRegion.shape[0] * Res
            current_y_offset += strip_height

            # 记录分割线位置（在两个图像之间）
            if i < nImages - 1:
                split_positions.append(current_y_offset)

        # 垂直拼接
        combinedImage = np.vstack(imageStrips)

        # ===== 不翻转图像，通过X轴反转实现能量从左到右递减 =====
        # （原始图像：X小=高能，X大=低能）

        # ===== 检测并裁剪空白列（X方向）=====
        column_max = np.max(combinedImage, axis=0)
        valid_columns = np.where(column_max > 0)[0]

        if len(valid_columns) > 0:
            actual_xmin = valid_columns[0] + all_xmin  # 像素坐标
            actual_xmax = valid_columns[-1] + all_xmin
            combinedImage = combinedImage[:, valid_columns[0]:valid_columns[-1]+1]
        else:
            actual_xmin = all_xmin
            actual_xmax = all_xmax

        # 计算物理参数（用于能量计算）
        LB = (self.parentApp.TPS.L / 2 + self.parentApp.TPS.D) * self.parentApp.TPS.L
        TB = self.parentApp.Z * self.parentApp.TPS.B * LB * 0.00998115
        A = self.parentApp.A

        # 创建能量到X位置的映射函数
        def x_pixel_to_energy(x_pixel):
            """将X像素坐标转换为能量（MeV）"""
            if x_pixel <= X0_orig:
                return 50  # 默认高能
            return (TB / ((x_pixel - X0_orig) * Res)) ** 2 / (2 * A)

        # 计算边界能量
        E_min_actual = x_pixel_to_energy(actual_xmax)  # X大 = 低能
        E_max_actual = x_pixel_to_energy(actual_xmin)  # X小 = 高能

        # 为了显示，extent使用位置坐标（mm）
        x_physical_min = (actual_xmin - X0_orig) * Res
        x_physical_max = (actual_xmax - X0_orig) * Res
        y_physical_min = 0
        y_physical_max = combinedImage.shape[0] * Res

        # ===== 创建单个axes =====
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # 获取gamma值和colorbar范围
        gamma = self.gammaSpinBox.value()
        colormin = self.colorMinSpinBox.value()
        colormax = self.colorMaxSpinBox.value()

        # 显示拼接图像（使用PowerNorm进行gamma校正）
        if abs(gamma - 1.0) > 0.01:
            # 非线性：使用PowerNorm
            norm = PowerNorm(gamma=gamma, vmin=colormin, vmax=colormax)
            im = ax.imshow(combinedImage,
                           cmap=self.parentApp.cmap,
                           aspect='equal',
                           extent=[x_physical_min, x_physical_max,
                                   y_physical_min, y_physical_max],
                           norm=norm,
                           origin='lower',
                           interpolation='bilinear')
        else:
            # 线性归一化
            im = ax.imshow(combinedImage,
                           cmap=self.parentApp.cmap,
                           aspect='equal',
                           extent=[x_physical_min, x_physical_max,
                                   y_physical_min, y_physical_max],
                           vmin=colormin,
                           vmax=colormax,
                           origin='lower',
                           interpolation='bilinear')

        # 设置显示范围，让图像充满整个axes
        ax.set_xlim(x_physical_max, x_physical_min)  # 反转X轴：右到左（低能到高能）
        ax.set_ylim(y_physical_min, y_physical_max)

        # 关闭自动边距（防止matplotlib添加空白）
        ax.margins(0)
        ax.autoscale(enable=False)  # 禁用自动缩放

        # ===== 画分割线（黑色细线，匹配图框样式）=====
        for split_y in split_positions:
            ax.axhline(y=split_y, color='black', linewidth=0.8, linestyle='-', alpha=0.8, zorder=10)

        # ===== 画每个图像的Y0参考线（红色虚线）=====
        for i, (y0_pos, filename) in enumerate(zip(y0_positions, filenames)):
            ax.axhline(y=y0_pos, color='red', linewidth=0.8, linestyle='--', alpha=0.7, zorder=5)

            # 不再显示文件名标注（已去除）

        # ===== Y轴刻度设置：在分割线位置显示文件名 =====
        # Y刻度位置：每个图像的中心位置
        y_tick_positions = []
        y_tick_labels = []

        # 计算每个图像的中心Y位置（用于显示文件名）
        prev_split = 0
        for i, filename in enumerate(filenames):
            if i < len(split_positions):
                next_split = split_positions[i]
            else:
                next_split = y_physical_max

            # 图像中心位置
            center_y = (prev_split + next_split) / 2
            y_tick_positions.append(center_y)

            # 提取文件名（去掉扩展名）
            import os
            name_only = os.path.splitext(filename)[0]
            # 如果文件名太长，截断
            if len(name_only) > 15:
                name_only = name_only[:15] + "..."
            y_tick_labels.append(name_only)

            prev_split = next_split

        ax.set_yticks(y_tick_positions)
        ax.set_yticklabels(y_tick_labels, fontsize=8)

        # 设置tick线的样式
        ax.tick_params(axis='y', which='major', length=6, width=0.8, direction='out')

        # ===== X轴能量刻度设置（非线性）=====
        # 检查是否有用户自定义的能量刻度
        custom_energy_input = self.energyTicksInput.text().strip()

        if custom_energy_input:
            # 使用用户自定义的能量刻度
            try:
                # 支持逗号或空格分隔
                energy_ticks = []
                for part in custom_energy_input.replace(',', ' ').split():
                    try:
                        energy = float(part)
                        if energy > 0:
                            energy_ticks.append(energy)
                    except ValueError:
                        continue

                energy_ticks = sorted(set(energy_ticks), reverse=True)  # 去重并降序排序

                if len(energy_ticks) == 0:
                    # 如果解析失败，使用自动生成
                    print("[TCompare] 警告：自定义能量刻度解析失败，使用自动生成")
                    energy_ticks = self._generateAutoEnergyTicks(E_min_actual, E_max_actual)
                else:
                    print(f"[TCompare] 使用自定义能量刻度：{energy_ticks}")
            except Exception as e:
                print(f"[TCompare] 错误：自定义能量刻度解析失败 - {e}，使用自动生成")
                energy_ticks = self._generateAutoEnergyTicks(E_min_actual, E_max_actual)
        else:
            # 自动生成能量刻度
            energy_ticks = self._generateAutoEnergyTicks(E_min_actual, E_max_actual)

        # 将能量转换为X坐标位置（mm）
        def energy_to_x_mm(E):
            """能量（MeV）→ X物理坐标（mm，相对X0）"""
            if E <= 0:
                return x_physical_max
            x_pixel = X0_orig + TB / np.sqrt(2 * A * E) / Res
            return (x_pixel - X0_orig) * Res

        x_tick_positions = [energy_to_x_mm(E) for E in energy_ticks]
        x_tick_labels = [f'{E:.0f}' for E in energy_ticks]

        ax.set_xticks(x_tick_positions)
        ax.set_xticklabels(x_tick_labels)

        # 设置标签
        ax.set_xlabel('Proton Energy (MeV)', fontsize=11)
        # 不设置Y轴label（已去除）
        ax.set_title('Proton Spectrum Comparison (Electric field compensated)',
                     fontsize=13, pad=15)

        # 网格
        ax.grid(True, alpha=0.2, linestyle=':', linewidth=0.5)

        # Colorbar（使用axes位置自动匹配）
        # 关键：使用 ax 参数传入单个axes，colorbar会自动匹配其高度
        from mpl_toolkits.axes_grid1 import make_axes_locatable
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="2%", pad=0.1)
        cbar = self.figure.colorbar(im, cax=cax, label='Intensity (a.u.)')
        cbar.ax.tick_params(labelsize=9)

        # 调整布局
        self.figure.tight_layout()

        # 更新canvas
        self.canvas.draw_idle()

        print(f"[TCompare] 对比图已生成：{nImages} 个图像垂直拼接（单axes）")
        print(f"[TCompare] Y显示范围：{strip_height_px} 像素 ({strip_height_mm:.2f} mm)，质子线上下各 {strip_height_px//2} 像素")
        print(f"[TCompare] Gamma校正：{gamma:.2f}" + (" (线性)" if abs(gamma - 1.0) <= 0.01 else ""))
        print(f"[TCompare] Colorbar范围：[{colormin}, {colormax}]")
        print(f"[TCompare] 拼接总高度：{y_physical_max:.2f} mm")
        print(f"[TCompare] 分割线位置：{[f'{y:.2f}' for y in split_positions]} mm")
        print(f"[TCompare] 能量范围：{E_max_actual:.2f} MeV (左) ~ {E_min_actual:.2f} MeV (右)")
        print(f"[TCompare] Y轴显示文件名：{y_tick_labels}")
    def clearComparison(self):
        """清除对比图"""
        self.comparisonData = []
        self.figure.clf()
        self.canvas.draw()
        print("[TCompare] 对比图已清除")