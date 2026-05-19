#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能选择性去噪测试
解决问题：大颗粒椒盐噪声vs信号模糊

策略：
1. 检测噪声点（基于局部统计）
2. 只修复噪声点（使用中值）
3. 保留信号点（不处理）
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import median_filter, grey_opening, grey_closing
from scipy.ndimage import uniform_filter
import time

print("="*70)
print("智能选择性去噪测试")
print("="*70)

# 创建测试图像：包含强信号峰值和大颗粒椒盐噪声
def create_test_image_with_noise(size=512):
    """
    创建测试图像：
    - 慢变背景
    - 强信号峰（模拟真实数据）
    - 大颗粒椒盐噪声（成簇）
    """
    print("\n创建测试图像...")

    # 1. 慢变背景
    x = np.linspace(0, 1, size)
    y = np.linspace(0, 1, size)
    X, Y = np.meshgrid(x, y)
    background = 1000 + 500 * X + 300 * Y

    # 2. 添加信号峰（模拟真实数据）
    img = background.copy()
    peaks = [
        (size//4, size//4, 15, 3000),
        (size//2, size//2, 20, 5000),
        (3*size//4, 3*size//4, 18, 4000),
    ]

    for px, py, sigma, amp in peaks:
        gaussian = amp * np.exp(-((X*size - px)**2 + (Y*size - py)**2) / (2 * sigma**2))
        img += gaussian

    # 3. 添加椒盐噪声（大颗粒）
    noise_ratio = 0.02  # 2%的像素是噪声
    noise_cluster_size = 3  # 噪声簇大小

    n_noise = int(img.size * noise_ratio)

    # 随机选择噪声位置
    noise_positions = []
    for _ in range(n_noise // (noise_cluster_size**2)):
        cx = np.random.randint(0, size)
        cy = np.random.randint(0, size)
        # 创建噪声簇
        for dx in range(-noise_cluster_size//2, noise_cluster_size//2 + 1):
            for dy in range(-noise_cluster_size//2, noise_cluster_size//2 + 1):
                nx = cx + dx
                ny = cy + dy
                if 0 <= nx < size and 0 <= ny < size:
                    noise_positions.append((nx, ny))

    # 应用椒盐噪声
    for x, y in noise_positions:
        if np.random.random() < 0.5:
            img[x, y] = np.max(img) + 10000  # 盐噪声（白点）
        else:
            img[x, y] = np.min(img) - 1000   # 椒噪声（黑点）

    img = img.astype(np.float64)

    print(f"  图像尺寸: {img.shape}")
    print(f"  噪声点数: {len(noise_positions)}")
    print(f"  噪声比例: {len(noise_positions)/img.size*100:.2f}%")
    print(f"  最小值: {np.min(img):.1f}")
    print(f"  最大值: {np.max(img):.1f}")
    print()

    return img, background, noise_positions


def detect_salt_pepper_noise(img, method='hybrid', threshold_factor=2.0, window_size=7):
    """
    检测椒盐噪声点（改进版）

    原理：结合全局极值和局部差异检测

    Parameters:
    -----------
    img : ndarray
        输入图像
    method : str
        检测方法：'percentile', 'local', 'hybrid'
    threshold_factor : float
        阈值因子（倍数×局部标准差）
    window_size : int
        检测窗口大小

    Returns:
    --------
    noise_mask : ndarray (bool)
        噪声掩码（True=噪声点）
    """
    print(f"[检测噪声] 方法={method}, 窗口={window_size}, 阈值因子={threshold_factor}")

    if method == 'percentile':
        # 方法1：基于百分位数（极值检测）
        # 椒盐噪声通常是极端值
        lower = np.percentile(img, 0.1)
        upper = np.percentile(img, 99.9)
        noise_mask = (img < lower) | (img > upper)

    elif method == 'local':
        # 方法2：基于局部统计
        local_mean = uniform_filter(img, size=window_size)
        local_var = uniform_filter(img**2, size=window_size) - local_mean**2
        local_std = np.sqrt(np.maximum(local_var, 0))

        deviation = np.abs(img - local_mean)
        threshold = threshold_factor * (local_std + 1e-10)  # 避免除零
        noise_mask = deviation > threshold

    elif method == 'hybrid':
        # 方法3：混合检测（全局极值 + 局部异常）
        # 步骤1：全局极值检测
        lower = np.percentile(img, 0.5)
        upper = np.percentile(img, 99.5)
        extreme_mask = (img < lower) | (img > upper)

        # 步骤2：局部异常检测
        local_mean = uniform_filter(img, size=window_size)
        local_std = uniform_filter(np.abs(img - local_mean), size=window_size)

        deviation = np.abs(img - local_mean)
        threshold = threshold_factor * (local_std + 1e-10)
        local_mask = deviation > threshold

        # 合并两种检测结果
        noise_mask = extreme_mask | local_mask

    else:
        raise ValueError(f"Unknown method: {method}")

    # 排除边缘（统计不准确）
    border = window_size // 2
    noise_mask[:border, :] = False
    noise_mask[-border:, :] = False
    noise_mask[:, :border] = False
    noise_mask[:, -border:] = False

    n_detected = np.sum(noise_mask)
    print(f"[检测噪声] 检测到噪声点: {n_detected} ({n_detected/img.size*100:.2f}%)")

    return noise_mask


def selective_median_repair(img, noise_mask, window_size=7):
    """
    选择性中值修复

    只对检测出的噪声点应用中值滤波
    其他点保持原值

    Parameters:
    -----------
    img : ndarray
        输入图像
    noise_mask : ndarray (bool)
        噪声掩码
    window_size : int
        修复窗口大小

    Returns:
    --------
    repaired : ndarray
        修复后的图像
    """
    print(f"[选择性修复] 使用中值窗口={window_size}")

    # 对整个图像应用中值滤波
    img_median = median_filter(img, size=window_size)

    # 只在噪声位置使用滤波结果，其他位置保持原值
    repaired = img.copy()
    repaired[noise_mask] = img_median[noise_mask]

    n_repaired = np.sum(noise_mask)
    print(f"[选择性修复] 修复像素数: {n_repaired}")

    return repaired


def morphological_denoise(img):
    """
    形态学去噪（针对椒盐噪声）

    先闭运算（去黑点），后开运算（去白点）
    """
    print("[形态学去噪] 开闭运算...")

    # 闭运算：填补黑色噪声（椒噪声）
    img_closed = grey_closing(img, size=3)

    # 开运算：去除白色噪声（盐噪声）
    img_opened = grey_opening(img_closed, size=3)

    return img_opened


def iterative_median(img, size=7, iterations=3):
    """
    迭代中值滤波（对比用）
    """
    print(f"[迭代中值] 窗口={size}, 迭代={iterations}")
    filtered = img
    for i in range(iterations):
        filtered = median_filter(filtered, size=size)
    return filtered


# 生成测试图像
img_test, true_background, true_noise_pos = create_test_image_with_noise(size=512)

print("="*70)
print("开始测试不同去噪方法")
print("="*70)

# 方法1：迭代中值滤波（对比基准）
print("\n[方法1] 迭代中值滤波（当前方法）")
start = time.time()
img_iterative = iterative_median(img_test, size=7, iterations=3)
time_iterative = time.time() - start
print(f"耗时: {time_iterative:.3f}秒")

# 方法2：形态学去噪
print("\n[方法2] 形态学去噪")
start = time.time()
img_morphological = morphological_denoise(img_test)
time_morphological = time.time() - start
print(f"耗时: {time_morphological:.3f}秒")

# 方法3：智能选择性去噪（新方法）
print("\n[方法3] 智能选择性去噪（新方法）")
start = time.time()

# 步骤1：检测噪声（使用混合方法）
noise_mask = detect_salt_pepper_noise(img_test, method='hybrid', threshold_factor=2.0, window_size=7)

# 步骤2：选择性修复
img_selective = selective_median_repair(img_test, noise_mask, window_size=7)

time_selective = time.time() - start
print(f"总耗时: {time_selective:.3f}秒")

# 方法4：混合策略（形态学+选择性）
print("\n[方法4] 混合策略（形态学+选择性）")
start = time.time()

# 先形态学粗去噪
img_hybrid = morphological_denoise(img_test)

# 再选择性精修复（降低阈值，更激进去除残留噪声）
noise_mask_hybrid = detect_salt_pepper_noise(img_hybrid, method='local', threshold_factor=1.5, window_size=7)
img_hybrid = selective_median_repair(img_hybrid, noise_mask_hybrid, window_size=5)

time_hybrid = time.time() - start
print(f"总耗时: {time_hybrid:.3f}秒")

# 评估效果
print("\n" + "="*70)
print("效果评估")
print("="*70)

# 提取中心信号峰区域
center = img_test.shape[0] // 2
roi_size = 50
roi = (slice(center-roi_size//2, center+roi_size//2),
       slice(center-roi_size//2, center+roi_size//2))

# 计算信号保留率
signal_original = np.max(img_test[roi])
signal_iterative = np.max(img_iterative[roi])
signal_morphological = np.max(img_morphological[roi])
signal_selective = np.max(img_selective[roi])
signal_hybrid = np.max(img_hybrid[roi])

retention_iterative = signal_iterative / signal_original * 100
retention_morphological = signal_morphological / signal_original * 100
retention_selective = signal_selective / signal_original * 100
retention_hybrid = signal_hybrid / signal_original * 100

# 估计残留噪声
def estimate_noise_residual(img):
    """估计残留噪声（检测异常值）"""
    local_mean = uniform_filter(img, size=5)
    local_std = uniform_filter(np.abs(img - local_mean), size=5)
    outliers = np.abs(img - local_mean) > 5 * local_std
    return np.sum(outliers)

noise_iterative = estimate_noise_residual(img_iterative)
noise_morphological = estimate_noise_residual(img_morphological)
noise_selective = estimate_noise_residual(img_selective)
noise_hybrid = estimate_noise_residual(img_hybrid)

print(f"\n{'方法':<25} {'耗时(秒)':<12} {'信号保留率(%)':<18} {'残留噪声点':<12}")
print("-"*70)
print(f"{'原始图像':<25} {0.0:<12} {100.0:<18.1f} {len(true_noise_pos):<12}")
print(f"{'迭代中值(7×7×3)':<25} {time_iterative:<12.3f} {retention_iterative:<18.1f} {noise_iterative:<12}")
print(f"{'形态学开闭':<25} {time_morphological:<12.3f} {retention_morphological:<18.1f} {noise_morphological:<12}")
print(f"{'智能选择性':<25} {time_selective:<12.3f} {retention_selective:<18.1f} {noise_selective:<12}")
print(f"{'混合策略':<25} {time_hybrid:<12.3f} {retention_hybrid:<18.1f} {noise_hybrid:<12}")
print("="*70)

# 分析最佳方案
print("\n分析：")
if retention_selective > retention_iterative and noise_selective < noise_iterative:
    print("  ✅ 智能选择性去噪：信号保留更好，噪声去除更彻底")
if retention_hybrid > retention_iterative:
    print("  ✅ 混合策略：最佳平衡")
if time_selective < time_iterative * 1.5:
    print("  ✅ 处理速度可接受")

# 可视化对比
print("\n生成可视化对比图...")

fig, axes = plt.subplots(3, 4, figsize=(18, 12))
fig.suptitle('智能选择性去噪对比测试', fontsize=16, fontweight='bold')

methods = [
    ("原始图像（含噪声）", img_test, 0, 100.0),
    ("迭代中值(7×7×3)", img_iterative, time_iterative, retention_iterative),
    ("形态学开闭", img_morphological, time_morphological, retention_morphological),
    ("智能选择性", img_selective, time_selective, retention_selective),
    ("混合策略", img_hybrid, time_hybrid, retention_hybrid),
]

# 第一行：原始图像和噪声掩码
axes[0, 0].imshow(img_test, cmap='jet')
axes[0, 0].set_title('原始图像（含噪声）', fontsize=12, fontweight='bold')
axes[0, 0].axis('off')

axes[0, 1].imshow(noise_mask, cmap='gray')
axes[0, 1].set_title(f'检测的噪声掩码\n({np.sum(noise_mask)}个点)', fontsize=11)
axes[0, 1].axis('off')

# 显示ROI位置
axes[0, 2].imshow(img_test, cmap='jet')
roi_rect = plt.Rectangle((roi[1].start, roi[0].start), roi_size, roi_size,
                          fill=False, edgecolor='red', linewidth=2)
axes[0, 2].add_patch(roi_rect)
axes[0, 2].set_title('ROI区域（信号峰）', fontsize=11)
axes[0, 2].axis('off')

# 中心剖面（原始）
center_line = img_test.shape[0] // 2
axes[0, 3].plot(img_test[center_line, :], label='原始', alpha=0.8, linewidth=1.5)
axes[0, 3].set_title('中心剖面（原始）', fontsize=11)
axes[0, 3].legend(fontsize=9)
axes[0, 3].grid(True, alpha=0.3)

# 第二行：去噪结果
for idx, (name, img, t, retention) in enumerate(methods[1:], start=0):
    axes[1, idx].imshow(img, cmap='jet')
    info = f'{name}\n耗时:{t:.3f}s 保留:{retention:.1f}%'
    axes[1, idx].set_title(info, fontsize=10)
    axes[1, idx].axis('off')

# 第三行：中心剖面对比
for idx, (name, img, t, retention) in enumerate(methods[1:], start=0):
    axes[2, idx].plot(img_test[center_line, :], label='原始', alpha=0.4, linewidth=1)
    axes[2, idx].plot(img[center_line, :], label=name, linewidth=1.5)
    axes[2, idx].set_title(f'剖面对比: {name}', fontsize=9)
    axes[2, idx].legend(fontsize=8)
    axes[2, idx].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('selective_denoise_comparison.png', dpi=150, bbox_inches='tight')
print("✅ 可视化结果已保存: selective_denoise_comparison.png")

print("\n" + "="*70)
print("📊 结论")
print("="*70)

# 找出最佳方法
best_idx = np.argmax([retention_iterative, retention_morphological, retention_selective, retention_hybrid])
best_names = ["迭代中值", "形态学", "智能选择性", "混合策略"]
best_name = best_names[best_idx]

print(f"\n最佳方法: {best_name}")
print(f"  • 信号保留率: {[retention_iterative, retention_morphological, retention_selective, retention_hybrid][best_idx]:.1f}%")
print(f"  • 残留噪声: {[noise_iterative, noise_morphological, noise_selective, noise_hybrid][best_idx]}点")
print(f"  • 处理速度: {[time_iterative, time_morphological, time_selective, time_hybrid][best_idx]:.3f}秒")

print("\n推荐配置:")
print("  1. 中等噪声: 智能选择性去噪（threshold_factor=3.0）")
print("  2. 强噪声:   混合策略（形态学+选择性）")
print("  3. 追求速度: 形态学开闭运算")

print("\n" + "="*70)
