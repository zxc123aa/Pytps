#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的16位TIFF图像处理：Rolling Ball + 去噪 + 自定义Jet伪彩色
处理椒盐噪声的科研数据图像
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from scipy.ndimage import median_filter
from skimage import io, morphology, restoration
from skimage.morphology import disk, ball, opening, closing
from skimage.filters import median
import warnings

warnings.filterwarnings('ignore')

# ========================================================================
# 参数设置
# ========================================================================
filename = 'your_image.tif'  # 修改为您的文件名
ball_radius = 50  # Rolling Ball半径
median_size = 5  # 中值滤波窗口大小
white_ratio = 0.05  # colormap中白色占比
transition_ratio = 0.10  # 白色到jet的过渡区域占比


# ========================================================================
# 自定义函数
# ========================================================================

def custom_jet_white_smooth(n=256, white_ratio=0.05, transition_ratio=0.10):
    """
    创建自定义colormap：最低值白色 + jet

    Parameters:
    -----------
    n : int
        colormap的颜色数量
    white_ratio : float
        白色区域占比
    transition_ratio : float
        白色到jet的过渡区域占比

    Returns:
    --------
    cmap : matplotlib.colors.ListedColormap
        自定义colormap
    """
    from matplotlib.colors import ListedColormap

    white_n = int(n * white_ratio)
    transition_n = int(n * transition_ratio)
    jet_n = n - white_n - transition_n

    # 纯白色部分
    white_part = np.ones((white_n, 3))

    # jet部分
    jet_cmap = plt.cm.jet
    jet_colors = jet_cmap(np.linspace(0, 1, max(jet_n, 1)))[:, :3]
    first_jet_color = jet_colors[0]

    # 过渡部分：白色渐变到jet的起始色
    transition_part = np.zeros((transition_n, 3))
    for i in range(transition_n):
        ratio = i / transition_n
        transition_part[i] = (1 - ratio) * np.array([1, 1, 1]) + ratio * first_jet_color

    # 合并
    colors = np.vstack([white_part, transition_part, jet_colors])
    cmap = ListedColormap(colors)

    return cmap


def rolling_ball_background(img, radius):
    """
    Rolling Ball 背景减除算法

    Parameters:
    -----------
    img : ndarray
        输入图像
    radius : int
        滚球半径

    Returns:
    --------
    background : ndarray
        估计的背景
    """
    # 使用形态学开运算近似Rolling Ball
    selem = disk(radius)
    background = opening(img, selem)
    return background


def adaptive_median_filter(img, max_size=7):
    """
    自适应中值滤波

    Parameters:
    -----------
    img : ndarray
        输入图像
    max_size : int
        最大窗口大小

    Returns:
    --------
    output : ndarray
        滤波后的图像
    """
    rows, cols = img.shape
    output = img.copy()

    for i in range(rows):
        for j in range(cols):
            window_size = 3
            while window_size <= max_size:
                half = window_size // 2
                rmin = max(0, i - half)
                rmax = min(rows, i + half + 1)
                cmin = max(0, j - half)
                cmax = min(cols, j + half + 1)

                window = img[rmin:rmax, cmin:cmax]
                zmin = np.min(window)
                zmax = np.max(window)
                zmed = np.median(window)
                zxy = img[i, j]

                A1 = zmed - zmin
                A2 = zmed - zmax

                if A1 > 0 and A2 < 0:
                    B1 = zxy - zmin
                    B2 = zxy - zmax
                    if B1 > 0 and B2 < 0:
                        output[i, j] = zxy
                    else:
                        output[i, j] = zmed
                    break
                else:
                    window_size += 2

                if window_size > max_size:
                    output[i, j] = zmed

    return output


def switching_median_filter(img, window_size=3):
    """
    开关中值滤波：仅对噪声点进行滤波

    Parameters:
    -----------
    img : ndarray
        输入图像
    window_size : int
        窗口大小

    Returns:
    --------
    output : ndarray
        滤波后的图像
    """
    rows, cols = img.shape
    output = img.copy()
    half = window_size // 2

    for i in range(half, rows - half):
        for j in range(half, cols - half):
            window = img[i - half:i + half + 1, j - half:j + half + 1]
            center = img[i, j]
            zmin = np.min(window)
            zmax = np.max(window)

            # 如果是极值点，认为是噪声
            if center == zmin or center == zmax:
                output[i, j] = np.median(window)

    return output


def iterative_median_filter(img, iterations=3, size=3):
    """
    迭代中值滤波（"滚雪球"方式）

    Parameters:
    -----------
    img : ndarray
        输入图像
    iterations : int
        迭代次数
    size : int
        窗口大小

    Returns:
    --------
    output : ndarray
        滤波后的图像
    """
    output = img.copy()
    for _ in range(iterations):
        output = median_filter(output, size=size)
    return output


# ========================================================================
# 主处理流程
# ========================================================================

def main():
    print("=" * 70)
    print("16位TIFF图像处理：Rolling Ball + 去噪 + 自定义Jet伪彩色")
    print("=" * 70)

    # 读取16位TIFF图像
    print(f"\n正在读取图像: {filename}")
    img = io.imread(filename)

    if img.dtype == np.uint16:
        print(f"图像信息: {img.shape[1]} x {img.shape[0]}, 16位")
    else:
        print(f"图像信息: {img.shape[1]} x {img.shape[0]}, {img.dtype}")

    img = img.astype(np.float64)

    # ====================================================================
    # 第一步：Rolling Ball 背景减除
    # ====================================================================
    print(f"\n正在进行Rolling Ball背景减除 (半径={ball_radius})...")
    background = rolling_ball_background(img, ball_radius)
    img_bg_removed = img - background
    img_bg_removed[img_bg_removed < 0] = 0

    # ====================================================================
    # 第二步：椒盐噪声去除
    # ====================================================================
    print("正在进行噪声去除...")

    # 方法1: 标准中值滤波
    img_median3 = median_filter(img_bg_removed, size=3)
    img_median5 = median_filter(img_bg_removed, size=median_size)

    # 方法2: 自适应中值滤波
    print("  - 自适应中值滤波...")
    img_adaptive = adaptive_median_filter(img_bg_removed, max_size=7)

    # 方法3: 开关中值滤波
    print("  - 开关中值滤波...")
    img_switching = switching_median_filter(img_bg_removed, window_size=3)

    # 方法4: 形态学滤波
    selem = disk(2)
    img_morph = closing(opening(img_bg_removed, selem), selem)

    # 方法5: 双边滤波
    from skimage.restoration import denoise_bilateral
    img_bilateral = denoise_bilateral(img_bg_removed, sigma_color=0.05, sigma_spatial=15)

    # 方法6: 迭代中值滤波
    img_iter = iterative_median_filter(img_bg_removed, iterations=3, size=3)

    # ====================================================================
    # 第三步：创建自定义Colormap
    # ====================================================================
    custom_cmap = custom_jet_white_smooth(256, white_ratio, transition_ratio)

    # ====================================================================
    # 可视化：完整处理流程
    # ====================================================================
    print("\n正在生成可视化图像...")

    fig1 = plt.figure(figsize=(18, 10))
    fig1.suptitle('Rolling Ball + 去噪完整流程', fontsize=16, fontweight='bold')

    images = [
        (img, '1. 原始图像'),
        (background, '2. Rolling Ball背景'),
        (img_bg_removed, '3. 背景减除后'),
        (img_median3, '4. 中值滤波 3×3'),
        (img_median5, '5. 中值滤波 5×5 ★推荐'),
        (img_adaptive, '6. 自适应中值滤波'),
        (img_morph, '7. 形态学滤波'),
        (img_bilateral, '8. 双边滤波'),
        (img_iter, '9. 迭代中值×3')
    ]

    for idx, (image, title) in enumerate(images, 1):
        ax = plt.subplot(3, 3, idx)
        im = ax.imshow(image, cmap=custom_cmap)
        ax.set_title(title, fontsize=10, fontweight='bold' if '★' in title else 'normal')
        ax.axis('off')
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    plt.tight_layout()
    plt.savefig('processing_flow.png', dpi=150, bbox_inches='tight')
    print("  已保存: processing_flow.png")

    # ====================================================================
    # 高质量对比图
    # ====================================================================
    fig2 = plt.figure(figsize=(14, 6))
    fig2.suptitle('处理前后对比', fontsize=16, fontweight='bold')

    # 原始图像
    ax1 = plt.subplot(1, 3, 1)
    im1 = ax1.imshow(img, cmap=custom_cmap)
    ax1.set_title('原始图像', fontsize=14, fontweight='bold')
    ax1.set_xlabel('X (像素)')
    ax1.set_ylabel('Y (像素)')
    cbar1 = plt.colorbar(im1, ax=ax1)
    cbar1.set_label('强度值', fontsize=10)

    # Rolling Ball背景
    ax2 = plt.subplot(1, 3, 2)
    im2 = ax2.imshow(background, cmap=custom_cmap)
    ax2.set_title(f'Rolling Ball背景 (r={ball_radius})', fontsize=14, fontweight='bold')
    ax2.set_xlabel('X (像素)')
    ax2.set_ylabel('Y (像素)')
    cbar2 = plt.colorbar(im2, ax=ax2)
    cbar2.set_label('强度值', fontsize=10)

    # 最终结果
    ax3 = plt.subplot(1, 3, 3)
    im3 = ax3.imshow(img_median5, cmap=custom_cmap)
    ax3.set_title('最终结果 (背景去除+去噪)', fontsize=14, fontweight='bold')
    ax3.set_xlabel('X (像素)')
    ax3.set_ylabel('Y (像素)')
    cbar3 = plt.colorbar(im3, ax=ax3)
    cbar3.set_label('强度值', fontsize=10)

    plt.tight_layout()
    plt.savefig('comparison.png', dpi=300, bbox_inches='tight')
    print("  已保存: comparison.png")

    # ====================================================================
    # Rolling Ball 半径对比
    # ====================================================================
    fig3 = plt.figure(figsize=(16, 8))
    fig3.suptitle('Rolling Ball 半径对比', fontsize=16, fontweight='bold')

    radii = [20, 50, 100, 150]
    for i, r in enumerate(radii):
        # 计算背景
        bg_temp = rolling_ball_background(img, r)
        img_corrected = img - bg_temp
        img_corrected[img_corrected < 0] = 0

        # 去噪
        img_final = median_filter(img_corrected, size=5)

        # 显示背景
        ax1 = plt.subplot(2, 4, i + 1)
        im1 = ax1.imshow(bg_temp, cmap=custom_cmap)
        ax1.set_title(f'背景 (r={r})')
        ax1.axis('off')
        plt.colorbar(im1, ax=ax1, fraction=0.046)

        # 显示处理结果
        ax2 = plt.subplot(2, 4, i + 5)
        im2 = ax2.imshow(img_final, cmap=custom_cmap)
        ax2.set_title(f'处理后 (r={r})')
        ax2.axis('off')
        plt.colorbar(im2, ax=ax2, fraction=0.046)

    plt.tight_layout()
    plt.savefig('radius_comparison.png', dpi=150, bbox_inches='tight')
    print("  已保存: radius_comparison.png")

    # ====================================================================
    # 保存结果
    # ====================================================================
    print("\n正在保存处理结果...")

    # 保存16位TIFF
    img_result_16bit = np.clip(img_median5, 0, 65535).astype(np.uint16)
    io.imsave('result_16bit.tif', img_result_16bit)
    print("  已保存: result_16bit.tif (16位TIFF)")

    # 保存伪彩色PNG
    fig_save = plt.figure(figsize=(10, 8))
    ax = plt.subplot(1, 1, 1)
    im = ax.imshow(img_median5, cmap=custom_cmap)
    ax.set_title('处理后的科研数据', fontsize=14, fontweight='bold')
    ax.axis('off')
    plt.colorbar(im, ax=ax, fraction=0.046)
    plt.tight_layout()
    plt.savefig('result_pseudocolor.png', dpi=300, bbox_inches='tight')
    plt.close(fig_save)
    print("  已保存: result_pseudocolor.png (伪彩色)")

    # ====================================================================
    # 输出统计信息
    # ====================================================================
    print("\n" + "=" * 70)
    print("处理完成")
    print("=" * 70)
    print("\n原始图像统计:")
    print(f"  最小值: {np.min(img):.2f}")
    print(f"  最大值: {np.max(img):.2f}")
    print(f"  平均值: {np.mean(img):.2f}")
    print(f"  标准差: {np.std(img):.2f}")

    print("\n处理后图像统计:")
    print(f"  最小值: {np.min(img_median5):.2f}")
    print(f"  最大值: {np.max(img_median5):.2f}")
    print(f"  平均值: {np.mean(img_median5):.2f}")
    print(f"  标准差: {np.std(img_median5):.2f}")

    print("\n保存的文件:")
    print("  - result_16bit.tif (16位TIFF格式)")
    print("  - result_pseudocolor.png (伪彩色可视化)")
    print("  - processing_flow.png (完整处理流程)")
    print("  - comparison.png (高分辨率对比图)")
    print("  - radius_comparison.png (Rolling Ball半径对比)")
    print("=" * 70)

    # 显示所有图形
    plt.show()


# ========================================================================
# 运行主程序
# ========================================================================
if __name__ == "__main__":
    main()