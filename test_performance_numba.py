#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试脚本：对比scipy和Numba实现的滚球法

测试不同半径下的性能差异
"""

import time
import numpy as np

# 导入matplotlib（可选）
try:
    import matplotlib.pyplot as plt
    from matplotlib import rcParams
    MATPLOTLIB_AVAILABLE = True
    # 设置中文字体
    rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    rcParams['axes.unicode_minus'] = False
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️  matplotlib不可用，将跳过可视化")

# 导入TFilter模块
import TFilter

print("="*70)
print("滚球法性能对比测试")
print("="*70)

# 检查Numba是否可用
if TFilter.NUMBA_AVAILABLE:
    print("✅ Numba可用")
else:
    print("⚠️  Numba不可用，请先安装: pip install numba")
    print("    测试将只运行scipy版本")

print()

# 创建测试图像
print("创建测试图像...")
img_sizes = [(512, 512), (1024, 1024)]
test_radii = [10, 20, 30, 50]

results = {
    'scipy': {},
    'numba': {},
    'speedup': {}
}

for img_size in img_sizes:
    print(f"\n{'='*70}")
    print(f"图像尺寸: {img_size[0]}×{img_size[1]}")
    print(f"{'='*70}")

    # 生成测试图像
    img_test = np.random.randint(1000, 2000, img_size, dtype=np.uint16)
    img_float = img_test.astype(np.float64)

    size_key = f"{img_size[0]}x{img_size[1]}"
    results['scipy'][size_key] = []
    results['numba'][size_key] = []
    results['speedup'][size_key] = []

    for radius in test_radii:
        print(f"\n半径 r={radius}")
        print("-"*70)

        # 测试scipy版本
        print(f"[1/2] 测试scipy实现...")
        start = time.time()
        bg_scipy = TFilter.rollingBallBackground_fast(img_float, radius)
        time_scipy = time.time() - start
        print(f"      scipy耗时: {time_scipy:.3f}秒")

        # 测试Numba版本（如果可用）
        if TFilter.NUMBA_AVAILABLE:
            print(f"[2/2] 测试Numba实现...")

            # 第一次运行（包含JIT编译时间）
            start = time.time()
            bg_numba = TFilter.rollingBallBackground_numba(img_float, radius)
            time_first = time.time() - start
            print(f"      Numba首次: {time_first:.3f}秒 (包含JIT编译)")

            # 第二次运行（JIT已编译）
            start = time.time()
            bg_numba = TFilter.rollingBallBackground_numba(img_float, radius)
            time_numba = time.time() - start
            print(f"      Numba二次: {time_numba:.3f}秒")

            # 计算加速比
            speedup = time_scipy / time_numba
            if speedup > 1:
                print(f"      🚀 Numba加速: {speedup:.2f}x 更快")
            elif speedup < 1:
                print(f"      ⚠️  scipy更快: {1/speedup:.2f}x")
            else:
                print(f"      ⚖️  性能相当")

            # 验证结果一致性
            max_diff = np.max(np.abs(bg_scipy - bg_numba))
            mean_diff = np.mean(np.abs(bg_scipy - bg_numba))
            print(f"      结果差异: 最大={max_diff:.2e}, 平均={mean_diff:.2e}")

            results['numba'][size_key].append(time_numba)
            results['speedup'][size_key].append(speedup)
        else:
            results['numba'][size_key].append(None)
            results['speedup'][size_key].append(None)

        results['scipy'][size_key].append(time_scipy)

# 生成汇总报告
print("\n" + "="*70)
print("性能测试汇总报告")
print("="*70)

for img_size in img_sizes:
    size_key = f"{img_size[0]}x{img_size[1]}"
    print(f"\n图像尺寸: {size_key}")
    print(f"{'半径':<10} {'scipy(秒)':<15} {'Numba(秒)':<15} {'加速比':<10}")
    print("-"*70)

    for i, radius in enumerate(test_radii):
        scipy_time = results['scipy'][size_key][i]
        numba_time = results['numba'][size_key][i]
        speedup = results['speedup'][size_key][i]

        if numba_time is not None:
            print(f"r={radius:<8} {scipy_time:<15.3f} {numba_time:<15.3f} {speedup:<10.2f}x")
        else:
            print(f"r={radius:<8} {scipy_time:<15.3f} {'N/A':<15} {'N/A':<10}")

# 可视化结果（如果Numba和matplotlib都可用）
if TFilter.NUMBA_AVAILABLE and MATPLOTLIB_AVAILABLE:
    print("\n生成性能对比图...")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for idx, img_size in enumerate(img_sizes):
        ax = axes[idx]
        size_key = f"{img_size[0]}x{img_size[1]}"

        scipy_times = results['scipy'][size_key]
        numba_times = results['numba'][size_key]

        x = np.arange(len(test_radii))
        width = 0.35

        bars1 = ax.bar(x - width/2, scipy_times, width, label='scipy', color='#2E86AB')
        bars2 = ax.bar(x + width/2, numba_times, width, label='Numba', color='#A23B72')

        ax.set_xlabel('滚球半径', fontsize=12)
        ax.set_ylabel('耗时 (秒)', fontsize=12)
        ax.set_title(f'图像尺寸: {size_key}', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([f'r={r}' for r in test_radii])
        ax.legend(fontsize=11)
        ax.grid(axis='y', alpha=0.3)

        # 在柱子上标注数值
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}s',
                       ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig('performance_comparison_numba.png', dpi=150, bbox_inches='tight')
    print("✅ 性能对比图已保存: performance_comparison_numba.png")

    # 加速比图
    fig, ax = plt.subplots(figsize=(10, 6))

    for idx, img_size in enumerate(img_sizes):
        size_key = f"{img_size[0]}x{img_size[1]}"
        speedups = results['speedup'][size_key]
        ax.plot(test_radii, speedups, marker='o', linewidth=2,
                markersize=8, label=size_key)

    ax.axhline(y=1.0, color='red', linestyle='--', linewidth=1,
               label='无加速线', alpha=0.7)
    ax.set_xlabel('滚球半径', fontsize=12)
    ax.set_ylabel('加速比 (scipy时间 / Numba时间)', fontsize=12)
    ax.set_title('Numba加速比分析', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    # 标注数值
    for idx, img_size in enumerate(img_sizes):
        size_key = f"{img_size[0]}x{img_size[1]}"
        speedups = results['speedup'][size_key]
        for i, (r, s) in enumerate(zip(test_radii, speedups)):
            ax.text(r, s, f'{s:.2f}x', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig('speedup_analysis_numba.png', dpi=150, bbox_inches='tight')
    print("✅ 加速比分析图已保存: speedup_analysis_numba.png")

print("\n" + "="*70)
print("测试完成！")
print("="*70)

# 生成建议
print("\n📊 性能优化建议：")
print("-"*70)

if TFilter.NUMBA_AVAILABLE:
    # 分析哪种实现更优
    for img_size in img_sizes:
        size_key = f"{img_size[0]}x{img_size[1]}"
        speedups = results['speedup'][size_key]

        print(f"\n{size_key}图像:")
        for i, (r, s) in enumerate(zip(test_radii, speedups)):
            if s > 1.2:
                print(f"  • r={r}: 推荐使用Numba ({s:.2f}x加速)")
            elif s < 0.8:
                print(f"  • r={r}: 推荐使用scipy ({1/s:.2f}x更快)")
            else:
                print(f"  • r={r}: 两者性能相当")
else:
    print("  请先安装Numba以启用加速功能:")
    print("  pip install numba")
    print()
    print("  当前使用scipy实现已经过优化，性能良好。")

print("\n" + "="*70)
