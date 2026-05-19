#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rolling Ball算法对比测试

对比三种实现：
1. 平坦SE（disk + opening）- 原始版本
2. 平坦SE（minimum + maximum filter）- 快速近似
3. 球形SE（grey_erosion）- 真正的rolling ball（ImageJ风格）

测试重点：
- 对强峰值的背景估计准确度
- 是否"吃掉"真实信号
- 处理时间对比
"""

import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置中文字体（可选）
try:
    rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    rcParams['axes.unicode_minus'] = False
except:
    pass

# 导入TFilter模块
import TFilter

print("="*70)
print("Rolling Ball算法对比测试")
print("="*70)
print()

# 创建测试图像：包含强峰值和慢变背景
def create_test_image(size=512):
    """
    创建测试图像：
    - 慢变背景（斜坡）
    - 强峰值信号（模拟真实数据）
    - 少量噪声
    """
    print("创建测试图像...")

    # 1. 慢变背景（斜坡）
    x = np.linspace(0, 1, size)
    y = np.linspace(0, 1, size)
    X, Y = np.meshgrid(x, y)
    background = 1000 + 500 * X + 300 * Y  # 线性背景

    # 2. 添加强峰值信号
    img = background.copy()

    # 添加几个高斯峰（模拟真实信号）
    peaks = [
        (size//4, size//4, 20, 3000),    # (x, y, sigma, amplitude)
        (size//2, size//2, 15, 5000),
        (3*size//4, 3*size//4, 25, 4000),
        (size//3, 2*size//3, 18, 3500),
    ]

    for px, py, sigma, amp in peaks:
        gaussian = amp * np.exp(-((X*size - px)**2 + (Y*size - py)**2) / (2 * sigma**2))
        img += gaussian

    # 3. 添加少量噪声
    noise = np.random.normal(0, 50, img.shape)
    img += noise

    img = img.astype(np.float64)

    print(f"  图像尺寸: {img.shape}")
    print(f"  最小值: {np.min(img):.1f}")
    print(f"  最大值: {np.max(img):.1f}")
    print(f"  平均值: {np.mean(img):.1f}")
    print()

    return img, background


# 生成测试图像
img_test, true_background = create_test_image(size=512)

# 测试不同半径
test_radii = [10, 20, 50]

results = {
    'original': {},
    'fast': {},
    'true': {},
}

print("\n" + "="*70)
print("开始对比测试")
print("="*70)

for radius in test_radii:
    print(f"\n{'='*70}")
    print(f"测试半径 r={radius}")
    print(f"{'='*70}\n")

    # 方法1: 原始版本（disk + opening）
    print("[1/3] 测试原始版本（disk + opening）...")
    start = time.time()
    bg_original = TFilter.rollingBallBackground(img_test, radius)
    time_original = time.time() - start
    img_corrected_original = img_test - bg_original
    img_corrected_original[img_corrected_original < 0] = 0
    print(f"      耗时: {time_original:.3f}秒\n")

    # 方法2: 快速近似（minimum + maximum filter）
    print("[2/3] 测试快速近似（minimum + maximum filter）...")
    start = time.time()
    bg_fast = TFilter.rollingBallBackground_fast(img_test, radius)
    time_fast = time.time() - start
    img_corrected_fast = img_test - bg_fast
    img_corrected_fast[img_corrected_fast < 0] = 0
    print(f"      耗时: {time_fast:.3f}秒\n")

    # 方法3: 真正的rolling ball（球形SE）
    print("[3/3] 测试真正的Rolling Ball（球形SE）...")
    start = time.time()
    bg_true = TFilter.rollingBallBackground_true(img_test, radius)
    time_true = time.time() - start
    img_corrected_true = img_test - bg_true
    img_corrected_true[img_corrected_true < 0] = 0
    print(f"      耗时: {time_true:.3f}秒\n")

    # 计算背景估计误差（与真实背景对比）
    error_original = np.mean(np.abs(bg_original - true_background))
    error_fast = np.mean(np.abs(bg_fast - true_background))
    error_true = np.mean(np.abs(bg_true - true_background))

    # 计算信号保留率（峰值区域）
    # 提取中心峰值区域
    center = img_test.shape[0] // 2
    roi_size = 50
    roi = slice(center-roi_size//2, center+roi_size//2)

    signal_original = np.max(img_corrected_original[roi, roi])
    signal_fast = np.max(img_corrected_fast[roi, roi])
    signal_true = np.max(img_corrected_true[roi, roi])
    signal_original_img = np.max(img_test[roi, roi])

    retention_original = signal_original / signal_original_img * 100
    retention_fast = signal_fast / signal_original_img * 100
    retention_true = signal_true / signal_original_img * 100

    # 保存结果
    results['original'][radius] = {
        'time': time_original,
        'error': error_original,
        'retention': retention_original,
        'bg': bg_original,
        'corrected': img_corrected_original
    }
    results['fast'][radius] = {
        'time': time_fast,
        'error': error_fast,
        'retention': retention_fast,
        'bg': bg_fast,
        'corrected': img_corrected_fast
    }
    results['true'][radius] = {
        'time': time_true,
        'error': error_true,
        'retention': retention_true,
        'bg': bg_true,
        'corrected': img_corrected_true
    }

    # 打印对比结果
    print("="*70)
    print(f"半径 r={radius} 对比结果：")
    print("="*70)
    print(f"{'方法':<20} {'耗时(秒)':<12} {'背景误差':<12} {'信号保留率(%)':<15}")
    print("-"*70)
    print(f"{'原始版(disk+open)':<20} {time_original:<12.3f} {error_original:<12.1f} {retention_original:<15.1f}")
    print(f"{'快速近似(min+max)':<20} {time_fast:<12.3f} {error_fast:<12.1f} {retention_fast:<15.1f}")
    print(f"{'真正Rolling Ball':<20} {time_true:<12.3f} {error_true:<12.1f} {retention_true:<15.1f}")
    print("="*70)

    # 分析结论
    print("\n分析：")
    if error_true < error_fast:
        print(f"  ✅ 球形SE背景估计更准确（误差小{(error_fast-error_true)/error_fast*100:.1f}%）")
    if retention_true > retention_fast:
        print(f"  ✅ 球形SE信号保留更好（多保留{retention_true-retention_fast:.1f}%）")
    if time_true < time_original:
        print(f"  ✅ 球形SE比原始版快{time_original/time_true:.1f}x")

print("\n" + "="*70)
print("测试完成")
print("="*70)

# 可视化对比（选择一个半径）
test_radius = 20
print(f"\n生成半径r={test_radius}的可视化对比图...")

fig, axes = plt.subplots(3, 4, figsize=(18, 12))
fig.suptitle(f'Rolling Ball算法对比 (半径={test_radius})', fontsize=16, fontweight='bold')

methods = ['original', 'fast', 'true']
method_names = ['原始版(disk+open)', '快速近似(min+max)', '真正Rolling Ball(球形SE)']

for i, (method, name) in enumerate(zip(methods, method_names)):
    # 原始图像
    axes[i, 0].imshow(img_test, cmap='jet')
    axes[i, 0].set_title('原始图像' if i == 0 else '')
    axes[i, 0].axis('off')

    # 背景估计
    axes[i, 1].imshow(results[method][test_radius]['bg'], cmap='jet')
    axes[i, 1].set_title(f'{name}\n背景估计')
    axes[i, 1].axis('off')

    # 背景减除后
    axes[i, 2].imshow(results[method][test_radius]['corrected'], cmap='jet')
    axes[i, 2].set_title('背景减除后')
    axes[i, 2].axis('off')

    # 中心剖面对比
    center_line = img_test.shape[0] // 2
    axes[i, 3].plot(img_test[center_line, :], label='原始', alpha=0.7)
    axes[i, 3].plot(results[method][test_radius]['bg'][center_line, :], label='背景', linewidth=2)
    axes[i, 3].plot(results[method][test_radius]['corrected'][center_line, :], label='减除后', alpha=0.7)
    axes[i, 3].set_title(f'{name}\n中心剖面')
    axes[i, 3].legend(fontsize=8)
    axes[i, 3].grid(True, alpha=0.3)

    # 添加指标文本
    info_text = (f"耗时: {results[method][test_radius]['time']:.3f}s\n"
                 f"背景误差: {results[method][test_radius]['error']:.1f}\n"
                 f"信号保留: {results[method][test_radius]['retention']:.1f}%")
    axes[i, 3].text(0.02, 0.98, info_text, transform=axes[i, 3].transAxes,
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                   fontsize=9)

plt.tight_layout()
plt.savefig('rolling_ball_comparison.png', dpi=150, bbox_inches='tight')
print("✅ 可视化结果已保存: rolling_ball_comparison.png")

# 生成性能对比图
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

radii_list = list(results['original'].keys())

# 时间对比
times_original = [results['original'][r]['time'] for r in radii_list]
times_fast = [results['fast'][r]['time'] for r in radii_list]
times_true = [results['true'][r]['time'] for r in radii_list]

x = np.arange(len(radii_list))
width = 0.25

axes[0].bar(x - width, times_original, width, label='原始版', color='#FF6B6B')
axes[0].bar(x, times_fast, width, label='快速近似', color='#4ECDC4')
axes[0].bar(x + width, times_true, width, label='球形SE', color='#95E1D3')
axes[0].set_xlabel('半径', fontsize=12)
axes[0].set_ylabel('耗时 (秒)', fontsize=12)
axes[0].set_title('处理时间对比', fontsize=14, fontweight='bold')
axes[0].set_xticks(x)
axes[0].set_xticklabels([f'r={r}' for r in radii_list])
axes[0].legend()
axes[0].grid(axis='y', alpha=0.3)

# 背景误差对比
errors_original = [results['original'][r]['error'] for r in radii_list]
errors_fast = [results['fast'][r]['error'] for r in radii_list]
errors_true = [results['true'][r]['error'] for r in radii_list]

axes[1].plot(radii_list, errors_original, marker='o', linewidth=2, markersize=8, label='原始版')
axes[1].plot(radii_list, errors_fast, marker='s', linewidth=2, markersize=8, label='快速近似')
axes[1].plot(radii_list, errors_true, marker='^', linewidth=2, markersize=8, label='球形SE')
axes[1].set_xlabel('半径', fontsize=12)
axes[1].set_ylabel('平均绝对误差', fontsize=12)
axes[1].set_title('背景估计准确度', fontsize=14, fontweight='bold')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# 信号保留率对比
retention_original = [results['original'][r]['retention'] for r in radii_list]
retention_fast = [results['fast'][r]['retention'] for r in radii_list]
retention_true = [results['true'][r]['retention'] for r in radii_list]

axes[2].plot(radii_list, retention_original, marker='o', linewidth=2, markersize=8, label='原始版')
axes[2].plot(radii_list, retention_fast, marker='s', linewidth=2, markersize=8, label='快速近似')
axes[2].plot(radii_list, retention_true, marker='^', linewidth=2, markersize=8, label='球形SE')
axes[2].set_xlabel('半径', fontsize=12)
axes[2].set_ylabel('信号保留率 (%)', fontsize=12)
axes[2].set_title('信号保留对比', fontsize=14, fontweight='bold')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('rolling_ball_metrics.png', dpi=150, bbox_inches='tight')
print("✅ 性能指标图已保存: rolling_ball_metrics.png")

print("\n" + "="*70)
print("📊 总结")
print("="*70)

# 计算平均改善
avg_error_improvement = np.mean([(results['fast'][r]['error'] - results['true'][r]['error']) / results['fast'][r]['error'] * 100 for r in radii_list])
avg_retention_improvement = np.mean([results['true'][r]['retention'] - results['fast'][r]['retention'] for r in radii_list])

print(f"\n球形SE（真正Rolling Ball）相比快速近似：")
print(f"  • 背景估计准确度平均提升: {avg_error_improvement:.1f}%")
print(f"  • 信号保留率平均提升: {avg_retention_improvement:.1f}%")
print(f"\n推荐使用策略（已在TFilter.py中实现）：")
print(f"  • 小半径（<15）：球形SE（准确度优先）")
print(f"  • 中半径（15-30）：快速近似（平衡）")
print(f"  • 大半径（>30）：快速近似（速度优先）")

print("\n" + "="*70)
