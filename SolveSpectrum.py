# 输入： data-照片对应的ndarray，以左下角为坐标原点，开口向上的抛物线。
#       X0,Y0,Emin,Emax,dY-打靶位置参数；A,Z-解谱粒子的质量数和电荷数：具体可参考MATTPS程序
#       MCPFileName：MCP效率信息，传入MCP效率数据的txt文档路径，默认效率数据尚未录入
#       TPS：在main中创建一个TPS类的实例即可，默认不输入参数即为MATTPS程序中提供的默认TPS参数，可传入一个txt文档路径
#           txt文档的格式见TSettings.py中TPS类的定义
# 
# 返回值：ndarray，2行n列的数组，第一行为横坐标E，第二行为纵坐标dNdE，可直接绘图


# 全文翻译自 徐诗睿：MATTPS V3.0
# 由MATLAB r2017翻译至Python 3.9
# 因为我也不太懂，所以没有注释，感谢NumPy和MATLAB相近的语法结构：）
# 感谢徐诗睿师兄
# 张予嘉，2022.8.3


import numpy as np
import TSettings


def _spectrum_geometry(data, X0, Y0, A, Z, Emin, Emax, dY, TPS):
    LB = (TPS.L / 2 + TPS.D) * TPS.L
    TB = Z * TPS.B * LB * 0.00998115
    LE1 = (TPS.L1 * TPS.D1 + TPS.L1 * TPS.L2 + TPS.L1 ** 2 / 2) / TPS.d
    LE2 = (np.log((TPS.L2 + TPS.L3) / TPS.L3) * (TPS.L2 + TPS.L3 + TPS.D1) - TPS.L2) / TPS.theta
    LE = (LE1 + LE2) / 2
    TE = TPS.U * Z * LE / 1000000
    received_angle = (TPS.S1 / 2) ** 2 * np.pi / TPS.L0 ** 2
    dYmax_theoretical = np.ceil((TPS.S1 / 2) / TPS.L0 * (TPS.L0 + TPS.D + TPS.L) / TPS.Res)
    received_angle = received_angle * min(1, (2 * dY) / (2 * dYmax_theoretical))

    if Emin == 0:
        Xmax = data.shape[1]
    else:
        Xmax = np.ceil(X0 + TB / np.sqrt(2 * A * Emin) / TPS.Res)
        Xmax = min(Xmax, data.shape[1])

    Xmin = max(1, np.floor(X0 + TB / np.sqrt(2 * A * Emax) / TPS.Res))
    X = np.arange(Xmin, Xmax + 1, dtype=int)
    X = X[X != X0]
    E = (TB / ((X - X0) * TPS.Res)) ** 2 / (2 * A)
    Ymax = np.ceil(Y0 + TE / (E * TPS.Res) + dY)
    Ymax = np.clip(Ymax, 0, data.shape[0])
    Ymin = np.floor(Y0 + TE / (E * TPS.Res) - dY)
    Ymin = np.clip(Ymin, 0, data.shape[0])

    X_temp = X - 0.5
    X_temp = np.append(X_temp, X_temp[-1] + 1)
    E_temp = (TB / ((X_temp - X0) * TPS.Res)) ** 2 / (2 * A)
    dE = E_temp[0:-1] - E_temp[1:]

    return X, E, Ymin, Ymax, dE, received_angle, dYmax_theoretical


def _mcp_efficiency(E_value, MCP_Energy, MCP_Efficiency):
    if E_value > np.max(MCP_Energy):
        return MCP_Efficiency[MCP_Energy.argmax()]
    if E_value < np.min(MCP_Energy):
        return MCP_Efficiency[MCP_Energy.argmin()]

    index = np.argsort(abs(MCP_Energy - E_value))
    n1 = index[0]
    n2 = index[1]
    E1 = MCP_Energy[n1]
    E2 = MCP_Energy[n2]
    MCPEff1 = MCP_Efficiency[n1]
    MCPEff2 = MCP_Efficiency[n2]
    return MCPEff1 + (MCPEff2 - MCPEff1) / (E2 - E1) * (E_value - E1)


def _calibrated_spectrum_value(count_value, E_value, dE_value, received_angle,
                               MCP_Energy, MCP_Efficiency, TPS, is8bit):
    if is8bit == False:
        count_value = max(count_value, 1e-30) / (TPS.EMGain * TPS.QE)
    else:
        count_value = max(count_value, 1e-30) / (TPS.EMGain * TPS.QE)

    MCPEff = _mcp_efficiency(E_value, MCP_Energy, MCP_Efficiency)
    dnde = count_value / (MCPEff * dE_value * received_angle)
    return dnde


def _camera_correct_count(value, TPS, is8bit):
    if is8bit == False:
        return value / (TPS.EMGain * TPS.QE)
    return (value / 3) / (TPS.EMGain * TPS.QE)


def SolveSpectrum(data, X0, Y0, A, Z, Emin, Emax, dY, MCPFileName, TPS, is8bit):
    X, E, Ymin, Ymax, dE, Received_angle, dYmax_theoretical = _spectrum_geometry(
        data, X0, Y0, A, Z, Emin, Emax, dY, TPS
    )
    dNdE = np.zeros(E.shape[0])
    dNdE_noise = np.zeros(E.shape[0])

    MCPData = TSettings.LoadMCPData(MCPFileName)
    MCP_Energy = MCPData[..., 0]
    MCP_Efficiency = MCPData[..., 1]

    for i in np.nditer(np.arange(X.shape[0])):
        if A == 1 and Z == 1:
            Noise = np.mean(
                data[int(Ymin[i] - 2 * dYmax_theoretical - 1):int(Ymin[i] - 1 * dYmax_theoretical), X[i] - 1].astype(
                    float))
        else:
            Noise = np.mean(data[Y0 - 2 * dY - 1:Y0 - 1 * dY, X[i] - 1].astype(float))

        Count_net = np.sum(data[int(Ymin[i] - 1):int(Ymax[i]), X[i] - 1].astype(float) - Noise)

        dNdE[i] = _calibrated_spectrum_value(
            Count_net, E[i], dE[i], Received_angle,
            MCP_Energy, MCP_Efficiency, TPS, is8bit
        )
        dNdE_noise[i] = _calibrated_spectrum_value(
            Noise, E[i], dE[i], Received_angle,
            MCP_Energy, MCP_Efficiency, TPS, is8bit
        )

    spectrum = np.array([E, dNdE])
    specnoise = np.array([E, dNdE_noise])
    return spectrum, specnoise


def SolveSpectrumSideband(data, X0, Y0, A, Z, Emin, Emax, dY, MCPFileName, TPS, is8bit,
                          sideband_gap=None, sideband_width=None, background_mode="sideband",
                          background_offset=None, background_width=None, return_stats=False):
    X, E, Ymin, Ymax, dE, Received_angle, _ = _spectrum_geometry(
        data, X0, Y0, A, Z, Emin, Emax, dY, TPS
    )
    dNdE = np.zeros(E.shape[0])
    dNdE_noise = np.zeros(E.shape[0])
    dNdE_net = np.zeros(E.shape[0])
    center_counts = np.zeros(E.shape[0])
    bg_counts = np.zeros(E.shape[0])
    alpha_values = np.zeros(E.shape[0])
    net_counts = np.zeros(E.shape[0])
    var_counts = np.zeros(E.shape[0])
    denom_values = np.zeros(E.shape[0])

    MCPData = TSettings.LoadMCPData(MCPFileName)
    MCP_Energy = MCPData[..., 0]
    MCP_Efficiency = MCPData[..., 1]

    if sideband_gap is None:
        sideband_gap = max(2, int(dY))
    if sideband_width is None:
        sideband_width = max(4, int(2 * dY))
    if background_offset is None:
        background_offset = -max(8, int(4 * dY))
    if background_width is None:
        background_width = max(3, int(2 * dY))

    height = data.shape[0]
    for i in np.nditer(np.arange(X.shape[0])):
        x = X[i] - 1
        center_ymin = int(max(0, Ymin[i] - 1))
        center_ymax = int(min(height, Ymax[i]))
        if center_ymax <= center_ymin:
            continue

        sideband_parts = []
        if background_mode == "offset":
            center = 0.5 * (center_ymin + center_ymax)
            bg_center = center + background_offset
            bg_ymin = int(max(0, np.floor(bg_center - background_width / 2)))
            bg_ymax = int(min(height, np.ceil(bg_center + background_width / 2)))
            if bg_ymax > bg_ymin:
                sideband_parts.append(data[bg_ymin:bg_ymax, x].astype(float))
        else:
            lower_ymax = max(0, center_ymin - sideband_gap)
            lower_ymin = max(0, lower_ymax - sideband_width)
            upper_ymin = min(height, center_ymax + sideband_gap)
            upper_ymax = min(height, upper_ymin + sideband_width)
            if lower_ymax > lower_ymin:
                sideband_parts.append(data[lower_ymin:lower_ymax, x].astype(float))
            if upper_ymax > upper_ymin:
                sideband_parts.append(data[upper_ymin:upper_ymax, x].astype(float))

        center = data[center_ymin:center_ymax, x].astype(float)
        center_sum = float(np.sum(center))
        center_size = max(center.size, 1)
        if sideband_parts:
            sideband = np.concatenate(sideband_parts)
            bg_level = np.median(sideband)
            bg_sigma = 1.4826 * np.median(np.abs(sideband - bg_level))
            if bg_sigma == 0:
                bg_sigma = np.std(sideband)
            bg_sum = float(np.sum(sideband))
            bg_size = max(sideband.size, 1)
        else:
            bg_level = np.median(center)
            bg_sigma = np.std(center)
            bg_sum = float(bg_level * center_size)
            bg_size = center_size

        alpha = center_size / bg_size
        stat_scale = TPS.EMGain * TPS.QE * (3 if is8bit else 1)
        center_stat = center_sum / stat_scale
        bg_stat = bg_sum / stat_scale
        net_stat = center_stat - alpha * bg_stat
        count_var = max(center_stat + alpha * alpha * bg_stat, 1.0)
        MCPEff = _mcp_efficiency(E[i], MCP_Energy, MCP_Efficiency)
        denom = MCPEff * dE[i] * Received_angle

        center_counts[i] = center_sum
        bg_counts[i] = bg_sum
        alpha_values[i] = alpha
        net_counts[i] = net_stat
        var_counts[i] = count_var
        denom_values[i] = denom

        dNdE[i] = _calibrated_spectrum_value(center_sum, E[i], dE[i], Received_angle,
                                             MCP_Energy, MCP_Efficiency, TPS, is8bit)
        net_sum = center_sum - bg_level * center_size
        dNdE_net[i] = _calibrated_spectrum_value(net_sum, E[i], dE[i], Received_angle,
                                                 MCP_Energy, MCP_Efficiency, TPS, is8bit)
        # Background curve keeps the same convention as the earlier code path:
        # plot the background level, not the full sideband integral.
        dNdE_noise[i] = _calibrated_spectrum_value(bg_level, E[i], dE[i], Received_angle,
                                                   MCP_Energy, MCP_Efficiency, TPS, is8bit)

    spectrum = np.array([E, dNdE])
    noise = np.array([E, dNdE_noise])
    if not return_stats:
        return spectrum, noise

    stats = {
        "E": E,
        "dE": dE,
        "center_counts": center_counts,
        "bg_counts": bg_counts,
        "alpha": alpha_values,
        "net_counts": net_counts,
        "var_counts": var_counts,
        "denom": denom_values,
        "sigma_dNdE": np.sqrt(var_counts) / np.maximum(denom_values, 1e-30),
        "snr": net_counts / np.sqrt(np.maximum(var_counts, 1e-30)),
        "net_spectrum": np.array([E, dNdE_net]),
    }
    return spectrum, noise, stats


def SmoothSpectrum(spectrum, window=31, median_window=None):
    E = spectrum[0].copy()
    values = spectrum[1].astype(float).copy()
    if values.size < 3:
        return np.array([E, values])

    window = int(window)
    if window < 3:
        return np.array([E, values])
    if window % 2 == 0:
        window += 1
    window = min(window, values.size if values.size % 2 == 1 else values.size - 1)
    if window < 3:
        return np.array([E, values])

    positive = values > 0
    if not np.any(positive):
        return np.array([E, values])

    floor = np.min(values[positive]) * 0.1
    log_values = np.log10(np.maximum(values, floor))
    if median_window is None:
        median_window = max(3, window // 3)
    median_window = int(median_window)
    if median_window % 2 == 0:
        median_window += 1

    try:
        from scipy.ndimage import median_filter
        from scipy.signal import savgol_filter
        log_values = median_filter(log_values, size=median_window, mode='nearest')
        polyorder = min(3, window - 1)
        smoothed_log = savgol_filter(log_values, window_length=window, polyorder=polyorder, mode='interp')
    except Exception:
        kernel = np.ones(window) / window
        padded = np.pad(log_values, window // 2, mode='edge')
        smoothed_log = np.convolve(padded, kernel, mode='valid')

    return np.array([E, 10 ** smoothed_log])


def AdaptiveRebinSpectrum(stats, snr_min=3.0, min_counts=30):
    E = np.asarray(stats["E"], dtype=float)
    net = np.asarray(stats["net_counts"], dtype=float)
    var = np.asarray(stats["var_counts"], dtype=float)
    denom = np.asarray(stats["denom"], dtype=float)

    E_new = []
    y_new = []
    sigma_new = []
    snr_new = []

    i = 0
    n = len(E)
    while i < n:
        sum_net = 0.0
        sum_var = 0.0
        sum_denom = 0.0
        sum_weight_E = 0.0
        sum_weight = 0.0
        j = i

        while j < n:
            sum_net += net[j]
            sum_var += max(var[j], 1.0)
            sum_denom += max(denom[j], 1e-30)
            weight = max(net[j], 0.0) + 1e-12
            sum_weight_E += E[j] * weight
            sum_weight += weight
            snr = sum_net / np.sqrt(max(sum_var, 1e-30))
            if (snr >= snr_min and sum_net >= min_counts) or j == n - 1:
                break
            j += 1

        E_bin = sum_weight_E / sum_weight if sum_weight > 0 else np.mean(E[i:j + 1])
        y_bin = sum_net / max(sum_denom, 1e-30)
        sigma_bin = np.sqrt(max(sum_var, 1.0)) / max(sum_denom, 1e-30)

        E_new.append(E_bin)
        y_new.append(max(y_bin, 1e-30))
        sigma_new.append(max(sigma_bin, 1e-30))
        snr_new.append(sum_net / np.sqrt(max(sum_var, 1e-30)))
        i = j + 1

    return {
        "E": np.array(E_new),
        "dNdE": np.array(y_new),
        "sigma_dNdE": np.array(sigma_new),
        "snr": np.array(snr_new),
    }


def SmoothSpectrumWeightedLog(binned, smooth_factor=1.5, E_out=None):
    E = np.asarray(binned["E"], dtype=float)
    y = np.asarray(binned["dNdE"], dtype=float)
    sigma = np.asarray(binned["sigma_dNdE"], dtype=float)
    if E_out is None:
        E_out = E

    valid = np.isfinite(E) & np.isfinite(y) & np.isfinite(sigma) & (y > 0) & (sigma > 0)
    if np.sum(valid) < 4:
        return np.array([E_out, np.interp(E_out, E[valid], y[valid])]) if np.any(valid) else np.array([E_out, np.zeros_like(E_out)])

    E_fit = E[valid]
    y_fit = y[valid]
    sigma_fit = sigma[valid]
    order = np.argsort(E_fit)
    E_fit = E_fit[order]
    y_fit = y_fit[order]
    sigma_fit = sigma_fit[order]

    logy = np.log(y_fit)
    sigma_logy = np.clip(sigma_fit / y_fit, 0.05, 2.0)
    weights = 1.0 / sigma_logy

    try:
        from scipy.interpolate import UnivariateSpline
        spline = UnivariateSpline(E_fit, logy, w=weights, s=smooth_factor * len(E_fit))
        y_smooth = np.exp(spline(E_out))
    except Exception:
        y_smooth = SmoothSpectrum(np.array([E_fit, y_fit]), window=31)[1]
        y_smooth = np.interp(E_out, E_fit, y_smooth)

    return np.array([E_out, y_smooth])


def SmoothSpectrumAdaptiveRobust(binned, smooth_window=3, E_out=None):
    E = np.asarray(binned["E"], dtype=float)
    y = np.asarray(binned["dNdE"], dtype=float)
    if E_out is None:
        E_out = E
    E_out = np.asarray(E_out, dtype=float)

    valid = np.isfinite(E) & np.isfinite(y) & (y > 0)
    if np.sum(valid) == 0:
        return np.array([E_out, np.zeros_like(E_out)])

    E_fit = E[valid]
    y_fit = y[valid]
    order = np.argsort(E_fit)
    E_fit = E_fit[order]
    y_fit = y_fit[order]

    if E_fit.size == 1:
        return np.array([E_out, np.full_like(E_out, y_fit[0], dtype=float)])

    logy = np.log10(np.maximum(y_fit, np.min(y_fit[y_fit > 0]) * 0.1))

    window = int(smooth_window)
    if window % 2 == 0:
        window += 1
    max_window = E_fit.size if E_fit.size % 2 == 1 else E_fit.size - 1
    window = max(3, min(window, max_window))

    if window >= 3 and E_fit.size >= 3:
        try:
            from scipy.ndimage import median_filter
            logy = median_filter(logy, size=window, mode='nearest')
        except Exception:
            half = window // 2
            padded = np.pad(logy, half, mode='edge')
            logy = np.array([np.median(padded[i:i + window]) for i in range(logy.size)])

    logy_out = np.interp(E_out, E_fit, logy, left=logy[0], right=logy[-1])
    return np.array([E_out, 10 ** logy_out])


def SmoothSpectrumDisplayRaw(spectrum, smooth_window=9):
    E = np.asarray(spectrum[0], dtype=float)
    y = np.asarray(spectrum[1], dtype=float)
    E_out = E.copy()
    valid = np.isfinite(E) & np.isfinite(y) & (y > 0)
    if np.sum(valid) < 3:
        return np.array([E, np.maximum(y, 0)])

    E_fit = E[valid]
    y_fit = y[valid]
    order = np.argsort(E_fit)
    E_fit = E_fit[order]
    y_fit = y_fit[order]

    positive = y_fit[y_fit > 0]
    robust_positive = positive[positive > np.max(positive) * 1e-8]
    if robust_positive.size == 0:
        robust_positive = positive
    floor = max(np.percentile(robust_positive, 5) * 0.1, 1e-30)
    logy = np.log10(np.maximum(y_fit, floor))
    window = int(smooth_window)
    if window % 2 == 0:
        window += 1
    window = max(3, min(window, E_fit.size if E_fit.size % 2 == 1 else E_fit.size - 1))

    try:
        from scipy.ndimage import median_filter
        logy = median_filter(logy, size=window, mode='nearest')
    except Exception:
        half = window // 2
        padded = np.pad(logy, half, mode='edge')
        logy = np.array([np.median(padded[i:i + window]) for i in range(logy.size)])

    kernel = np.ones(window, dtype=float) / window
    padded = np.pad(logy, window // 2, mode='edge')
    logy = np.convolve(padded, kernel, mode='valid')

    y_smooth = 10 ** logy
    half = window // 2
    y_padded = np.pad(y_fit, half, mode='edge')
    local_min = np.array([np.min(y_padded[i:i + window]) for i in range(y_fit.size)])
    local_max = np.array([np.max(y_padded[i:i + window]) for i in range(y_fit.size)])
    y_smooth = np.clip(y_smooth, np.maximum(local_min, floor), np.maximum(local_max, floor))

    y_out = np.interp(E_out, E_fit, y_smooth, left=y_smooth[0], right=y_smooth[-1])
    return np.array([E_out, y_out])


def SmoothSpectrumPoissonWeighted(stats, snr_min=3.0, min_counts=30, smooth_factor=1.5,
                                  E_out=None, smooth_window=5):
    binned = AdaptiveRebinSpectrum(stats, snr_min=snr_min, min_counts=min_counts)
    smooth = SmoothSpectrumAdaptiveRobust(binned, smooth_window=smooth_window, E_out=E_out)
    return smooth, binned


def CutoffEnergySNR(spectrum, noise, Emin, Emax, snr_threshold=3.0, consecutive=3, smooth_window=9):
    smooth = SmoothSpectrum(spectrum, window=smooth_window)
    E = smooth[0]
    signal = smooth[1]
    noise_values = np.maximum(noise[1], 1e-30)
    valid_range = (E >= Emin) & (E <= Emax)
    significant = valid_range & (signal > noise[1]) & ((signal / noise_values) >= snr_threshold)

    if consecutive < 1:
        consecutive = 1

    order = np.argsort(E)[::-1]
    for start in range(0, len(order) - consecutive + 1):
        idxs = order[start:start + consecutive]
        if np.all(significant[idxs]):
            return np.round(np.max(E[idxs]), 2)

    return "寻找截止能量失败"
