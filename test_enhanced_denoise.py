#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强去噪测试 - 针对椒盐噪声+大颗粒模糊背景

实现方案1：形态学重建 + 导向滤波
- 开运算重建/闭运算重建
- 顶帽/底帽变换
- 导向滤波保边去噪
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import grey_opening, grey_closing, grey_erosion, grey_dilation
from scipy.ndimage import minimum_filter, maximum_filter, median_filter, uniform_filter
import time

print("="*70)
print("增强去噪测试（形态学重建 + 导向滤波）")
print("="*70)


def morphological_reconstruction_erosion(marker, mask, selem_size=3):
    """
    形态学腐蚀重建

    Parameters:
    -----------
    marker : ndarray
        标记图像（被重建的图像）
    mask : ndarray
        掩膜图像（限制重建的上界）
    selem_size : int
        结构元素大小

    Returns:
    --------
    reconstructed : ndarray
        重建后的图像
    """
    h, w = marker.shape
    reconstructed = marker.copy()

    # 迭代膨胀直到收敛
    for iteration in range(1000):  # 最多迭代1000次
        dilated = grey_dilation(reconstructed, size=selem_size)
        # 与mask取最小值（限制重建）
        dilated = np.minimum(dilated, mask)

        # 检查收敛
        if np.array_equal(dilated, reconstructed):
            print(f"[重建] 腐蚀重建收敛于第{iteration+1}次迭代")
            break
        reconstructed = dilated

    return reconstructed


def morphological_reconstruction_dilation(marker, mask, selem_size=3):
    """
    形态学膨胀重建

    Parameters:
    -----------
    marker : ndarray
        标记图像
    mask : ndarray
        掩膜图像（限制重建的下界）
    selem_size : int
        结构元素大小

    Returns:
    --------
    reconstructed : ndarray
        重建后的图像
    """
    h, w = marker.shape
    reconstructed = marker.copy()

    # 迭代腐蚀直到收敛
    for iteration in range(1000):
        eroded = grey_erosion(reconstructed, size=selem_size)
        # 与mask取最大值（限制重建）
        eroded = np.maximum(eroded, mask)

        # 检查收敛
        if np.array_equal(eroded, reconstructed):
            print(f"[重建] 膨胀重建收敛于第{iteration+1}次迭代")
            break
        reconstructed = eroded

    return reconstructed


def opening_by_reconstruction(img, selem_size=3):
    """
    开运算重建
    去除亮小块，保留大结构
    """
    print(f"[开运算重建] size={selem_size}")
    # 腐蚀作为marker
    eroded = grey_erosion(img, size=selem_size)
    # 原图作为mask
    reconstructed = morphological_reconstruction_erosion(eroded, img, selem_size)
    return reconstructed


def closing_by_reconstruction(img, selem_size=3):
    """
    闭运算重建
    去除暗小块，保留大结构
    """
    print(f"[闭运算重建] size={selem_size}")
    # 膨胀作为marker
    dilated = grey_dilation(img, size=selem_size)
    # 原图作为mask
    reconstructed = morphological_reconstruction_dilation(dilated, img, selem_size)
    return reconstructed


def white_tophat(img, selem_size=15):
    """
    白顶帽变换：原图 - 开运算重建
    提取亮异常（比背景亮的小结构）
    """
    print(f"[白顶帽] size={selem_size}")
    opened = opening_by_reconstruction(img, selem_size)
    tophat = img - opened
    tophat[tophat < 0] = 0
    return tophat


def black_tophat(img, selem_size=15):
    """
    黑顶帽（底帽）变换：闭运算重建 - 原图
    提取暗异常（比背景暗的小结构）
    """
    print(f"[黑顶帽] size={selem_size}")
    closed = closing_by_reconstruction(img, selem_size)
    bottomhat = closed - img
    bottomhat[bottomhat < 0] = 0
    return bottomhat


def guided_filter(I, p, r, eps):
    """
    导向滤波（Guided Filter）

    Parameters:
    -----------
    I : ndarray
        导向图像（guide image）
    p : ndarray
        输入图像（要滤波的图像）
    r : int
        窗口半径
    eps : float
        正则化参数（控制边缘保留程度）

    Returns:
    --------
    q : ndarray
        滤波后的图像
    """
    print(f"[导向滤波] radius={r}, epsilon={eps}")

    # 计算局部统计量
    mean_I = uniform_filter(I, size=2*r+1)
    mean_p = uniform_filter(p, size=2*r+1)
    mean_Ip = uniform_filter(I * p, size=2*r+1)
    cov_Ip = mean_Ip - mean_I * mean_p

    mean_II = uniform_filter(I * I, size=2*r+1)
    var_I = mean_II - mean_I * mean_I

    # 计算线性系数
    a = cov_Ip / (var_I + eps)
    b = mean_p - a * mean_I

    # 平均系数（避免块效应）
    mean_a = uniform_filter(a, size=2*r+1)
    mean_b = uniform_filter(b, size=2*r+1)

    # 输出
    q = mean_a * I + mean_b

    return q


def enhanced_denoise_v1(img, morph_size=3, tophat_size=15, guided_r=4, guided_eps=0.01):
    """
    增强去噪 v1：形态学重建 + 导向滤波

    流程：
    1. 闭运算重建 → 去除暗噪声（椒噪声）
    2. 开运算重建 → 去除亮噪声（盐噪声）
    3. 导向滤波 → 保边平滑，去除模糊背景噪声

    Parameters:
    -----------
    img : ndarray
        输入图像
    morph_size : int
        形态学结构元素大小（3-7）
    tophat_size : int
        顶帽变换尺寸（用于检测大颗粒）
    guided_r : int
        导向滤波半径（2-8）
    guided_eps : float
        导向滤波正则参数（0.0001-0.1，值越小边缘越锐利）

    Returns:
    --------
    denoised : ndarray
        去噪后的图像
    """
    print("\n[增强去噪v1] 形态学重建 + 导向滤波")
    print(f"  参数: morph_size={morph_size}, tophat_size={tophat_size}, guided_r={guided_r}, guided_eps={guided_eps}")

    img_float = img.astype(np.float64)

    # 步骤1：闭运算重建（去除暗噪声）
    img_closed = closing_by_reconstruction(img_float, selem_size=morph_size)

    # 步骤2：开运算重建（去除亮噪声）
    img_opened = opening_by_reconstruction(img_closed, selem_size=morph_size)

    # 步骤3：导向滤波（保边平滑，去除模糊背景）
    # 归一化到0-1
    img_min = np.min(img_opened)
    img_max = np.max(img_opened)
    img_norm = (img_opened - img_min) / (img_max - img_min + 1e-10)

    # 应用导向滤波
    img_guided = guided_filter(img_norm, img_norm, r=guided_r, eps=guided_eps)

    # 反归一化
    img_final = img_guided * (img_max - img_min) + img_min

    return img_final


def enhanced_denoise_v2(img, morph_size=3, tophat_size=15):
    """
    增强去噪 v2：形态学重建 + 顶帽掩膜修复

    流程：
    1. 顶帽/底帽检测异常
    2. 创建掩膜
    3. 掩膜内用中值修复，掩膜外保持原样

    Parameters:
    -----------
    img : ndarray
        输入图像
    morph_size : int
        基础形态学size
    tophat_size : int
        顶帽检测size（应大于噪声尺寸）

    Returns:
    --------
    denoised : ndarray
        去噪后的图像
    """
    print("\n[增强去噪v2] 形态学重建 + 顶帽掩膜修复")
    print(f"  参数: morph_size={morph_size}, tophat_size={tophat_size}")

    img_float = img.astype(np.float64)

    # 步骤1：检测异常
    tophat_white = white_tophat(img_float, selem_size=tophat_size)
    tophat_black = black_tophat(img_float, selem_size=tophat_size)

    # 步骤2：创建噪声掩膜
    # 阈值：超过局部标准差的3倍
    threshold_white = np.percentile(tophat_white, 95)
    threshold_black = np.percentile(tophat_black, 95)

    mask_white = tophat_white > threshold_white
    mask_black = tophat_black > threshold_black
    mask_noise = mask_white | mask_black

    print(f"  检测到噪声像素: {np.sum(mask_noise)} ({np.sum(mask_noise)/mask_noise.size*100:.2f}%)")

    # 步骤3：掩膜内修复
    img_repaired = img_float.copy()

    if np.sum(mask_noise) > 0:
        # 膨胀掩膜连接邻近噪声
        from scipy.ndimage import binary_dilation
        mask_dilated = binary_dilation(mask_noise, iterations=2)

        # 掩膜内用中值滤波修复
        img_median = median_filter(img_float, size=5)
        img_repaired[mask_dilated] = img_median[mask_dilated]

    # 步骤4：全局轻度平滑（可选）
    img_final = grey_closing(img_repaired, size=morph_size)
    img_final = grey_opening(img_final, size=morph_size)

    return img_final, mask_noise


# 创建测试图像（模拟实际情况）
def create_test_image_complex(size=512):
    """
    创建复杂测试图像：
    - 慢变背景
    - 强信号峰
    - 椒盐噪声（小颗粒）
    - 大颗粒模糊背景噪声
    """
    print("\n创建复杂测试图像...")

    # 1. 慢变背景
    x = np.linspace(0, 1, size)
    y = np.linspace(0, 1, size)
    X, Y = np.meshgrid(x, y)
    background = 1000 + 500 * X + 300 * Y

    # 2. 信号峰
    img = background.copy()
    peaks = [
        (size//4, size//4, 20, 3000),
        (size//2, size//2, 15, 5000),
        (3*size//4, 3*size//4, 25, 4000),
    ]
    for px, py, sigma, amp in peaks:
        gaussian = amp * np.exp(-((X*size - px)**2 + (Y*size - py)**2) / (2 * sigma**2))
        img += gaussian

    # 3. 椒盐噪声（小颗粒3×3）
    noise_ratio = 0.02
    noise_cluster_size = 3
    n_noise = int(img.size * noise_ratio)

    # 记录干净图像的最大/最小值（修复：避免指数增长）
    clean_max = np.max(img)
    clean_min = np.min(img)

    for _ in range(n_noise // (noise_cluster_size**2)):
        cx = np.random.randint(0, size)
        cy = np.random.randint(0, size)
        for dx in range(-noise_cluster_size//2, noise_cluster_size//2 + 1):
            for dy in range(-noise_cluster_size//2, noise_cluster_size//2 + 1):
                nx = cx + dx
                ny = cy + dy
                if 0 <= nx < size and 0 <= ny < size:
                    if np.random.random() < 0.5:
                        img[nx, ny] = clean_max + 3000  # 盐（固定使用干净图像的最大值）
                    else:
                        img[nx, ny] = clean_min - 500   # 椒（固定使用干净图像的最小值）

    # 4. 大颗粒模糊背景噪声（重点）
    # 模拟不均匀光照或低频噪声
    n_blobs = 20  # 20个大斑块
    for _ in range(n_blobs):
        cx = np.random.randint(0, size)
        cy = np.random.randint(0, size)
        sigma_blob = np.random.randint(30, 80)  # 大斑块
        amp_blob = np.random.uniform(-800, 800)  # 随机亮度

        blob = amp_blob * np.exp(-((X*size - cx)**2 + (Y*size - cy)**2) / (2 * sigma_blob**2))
        img += blob

    # 5. 少量高斯噪声
    noise = np.random.normal(0, 30, img.shape)
    img += noise

    img = img.astype(np.float64)

    print(f"  图像尺寸: {img.shape}")
    print(f"  最小值: {np.min(img):.1f}")
    print(f"  最大值: {np.max(img):.1f}")

    return img, background


# 生成测试图像
img_test, true_background = create_test_image_complex(size=512)

# 测试不同方法
print("\n" + "="*70)
print("开始测试")
print("="*70)

results = {}

# 方法1：简单形态学开闭
print("\n[方法1] 简单形态学开闭（当前方法）")
start = time.time()
img_simple = grey_closing(img_test, size=3)
img_simple = grey_opening(img_simple, size=3)
time_simple = time.time() - start
results['simple'] = {'img': img_simple, 'time': time_simple}
print(f"耗时: {time_simple:.3f}秒")

# 方法2：增强去噪v1（形态学重建 + 导向滤波）
print("\n[方法2] 增强去噪v1（形态学重建 + 导向滤波）")
start = time.time()
img_enhanced_v1 = enhanced_denoise_v1(img_test, morph_size=3, tophat_size=15, guided_r=4, guided_eps=0.0001)
time_v1 = time.time() - start
results['enhanced_v1'] = {'img': img_enhanced_v1, 'time': time_v1}
print(f"总耗时: {time_v1:.3f}秒")

# 方法3：增强去噪v2（顶帽掩膜修复）
print("\n[方法3] 增强去噪v2（顶帽掩膜修复）")
start = time.time()
img_enhanced_v2, mask_v2 = enhanced_denoise_v2(img_test, morph_size=3, tophat_size=15)
time_v2 = time.time() - start
results['enhanced_v2'] = {'img': img_enhanced_v2, 'time': time_v2, 'mask': mask_v2}
print(f"总耗时: {time_v2:.3f}秒")

# 评估效果
print("\n" + "="*70)
print("效果评估")
print("="*70)

center = img_test.shape[0] // 2
roi_size = 50
roi = (slice(center-roi_size//2, center+roi_size//2),
       slice(center-roi_size//2, center+roi_size//2))

signal_original = np.max(img_test[roi])
signal_simple = np.max(results['simple']['img'][roi])
signal_v1 = np.max(results['enhanced_v1']['img'][roi])
signal_v2 = np.max(results['enhanced_v2']['img'][roi])

retention_simple = signal_simple / signal_original * 100
retention_v1 = signal_v1 / signal_original * 100
retention_v2 = signal_v2 / signal_original * 100

print(f"\n{'方法':<30} {'耗时(秒)':<12} {'信号保留率(%)':<15}")
print("-"*70)
print(f"{'原始图像':<30} {0.0:<12} {100.0:<15.1f}")
print(f"{'简单形态学':<30} {time_simple:<12.3f} {retention_simple:<15.1f}")
print(f"{'增强v1(重建+导向)':<30} {time_v1:<12.3f} {retention_v1:<15.1f}")
print(f"{'增强v2(顶帽掩膜)':<30} {time_v2:<12.3f} {retention_v2:<15.1f}")

# 可视化
print("\n生成可视化对比图...")

fig, axes = plt.subplots(3, 4, figsize=(18, 12))
fig.suptitle('增强去噪算法对比', fontsize=16, fontweight='bold')

methods = ['原始图像', '简单形态学', '增强v1(重建+导向)', '增强v2(顶帽掩膜)']
images = [img_test, results['simple']['img'], results['enhanced_v1']['img'], results['enhanced_v2']['img']]

for col, (name, img) in enumerate(zip(methods, images)):
    # 第一行：全图
    axes[0, col].imshow(img, cmap='jet')
    axes[0, col].set_title(name, fontsize=11)
    axes[0, col].axis('off')

    # 第二行：ROI区域放大
    roi_img = img[roi]
    axes[1, col].imshow(roi_img, cmap='jet')
    axes[1, col].set_title(f'ROI放大 ({name})', fontsize=10)
    axes[1, col].axis('off')

    # 第三行：中心剖面
    center_line = img.shape[0] // 2
    axes[2, col].plot(img[center_line, :], linewidth=1.5)
    axes[2, col].set_title(f'中心剖面', fontsize=10)
    axes[2, col].grid(True, alpha=0.3)

    if col > 0:
        # 添加性能指标
        time_info = results[['simple', 'enhanced_v1', 'enhanced_v2'][col-1]]['time']
        retention_info = [retention_simple, retention_v1, retention_v2][col-1]
        info_text = f"耗时: {time_info:.3f}s\n信号保留: {retention_info:.1f}%"
        axes[2, col].text(0.02, 0.98, info_text, transform=axes[2, col].transAxes,
                         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                         fontsize=9)

plt.tight_layout()
plt.savefig('enhanced_denoise_comparison.png', dpi=150, bbox_inches='tight')
print("✅ 可视化结果已保存: enhanced_denoise_comparison.png")

print("\n" + "="*70)
print("📊 结论")
print("="*70)

best_idx = np.argmax([retention_simple, retention_v1, retention_v2])
best_names = ["简单形态学", "增强v1", "增强v2"]
print(f"\n最佳方法: {best_names[best_idx]}")
print(f"  信号保留率: {[retention_simple, retention_v1, retention_v2][best_idx]:.1f}%")
print(f"  处理速度: {[time_simple, time_v1, time_v2][best_idx]:.3f}秒")

print("\n推荐使用：")
print("  1. 简单椒盐噪声: 简单形态学（最快）")
print("  2. 椒盐+模糊背景: 增强v1（重建+导向滤波，效果最好）")
print("  3. 大颗粒异常: 增强v2（顶帽掩膜，针对性强）")

print("\n" + "="*70)
