# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyTPS is a Python-based Thomson Parabola Spectrometer (TPS) data analysis application. It processes raw detector images from laser-plasma ion acceleration experiments to extract energy spectra. The application is built with PySide6 (Qt) and provides both real-time (online) and batch (offline) analysis modes.

## Key Concepts

### Thomson Parabola Spectrometer Physics
- The TPS uses electromagnetic fields to disperse charged particles by energy and charge-to-mass ratio
- Particles trace parabolic trajectories on a detector (typically an MCP + EMCCD camera)
- The software converts 2D image coordinates (X, Y) to energy spectra (E, dN/dE)
- Core physics parameters are stored in `TPS_Settings.ini` (magnetic field B, electric field U, geometry, etc.)

### Analysis Pipeline Flow
1. **Image Loading** (`TImageRead.py`): Reads TIFF/PNG/JPG images (supports 8-bit and 16-bit)
2. **Filtering** (`TFilter.py`): Removes salt-and-pepper noise and background
3. **Spectrum Solving** (`SolveSpectrum.py`): Integrates signal along parabolic trajectory, converts to energy spectrum
4. **Visualization** (`TDraw.py`): Displays image with pseudocolor + energy spectrum plot
5. **Auto-processing** (`TWatchDog.py`): File watcher for online mode (Windows-specific, uses pywin32)

## Architecture

### Main Application (`PyTPS.py`)
- Entry point: `MainWindow` class (PySide6 QMainWindow)
- Manages UI state and coordinates all modules
- Key attributes stored on `self`:
  - `imageData`: Current processed image (numpy array, flipped vertically)
  - `specData`, `noiseSpec`: Processed spectrum and noise background
  - `TPS`: Instance of TPS parameter class
  - Filter parameters: `filterMode`, `medianSize`, `medianIterations`, `morphologicalSize`, `rollingBallRadius`
  - Analysis parameters: `X0`, `Y0` (origin position), `dY` (integration window), `A`, `Z` (particle mass/charge)

### Module Responsibilities

**TSettings.py**: Configuration and initialization
- `TPS` class: Loads TPS parameters from `TPS_Settings.ini`
- `TPSinit()`: Loads application parameters from `PyTPS_init.ini`
- `LoadMCPData()`: Loads MCP efficiency curves from text files

**TSolve.py**: Analysis coordinator
- `Solve()`: Main analysis function called when parameters change
- Applies filtering, solves spectrum, updates plots
- Handles both single-image mode and batch analysis mode

**TFilter.py**: Image preprocessing
- `applyFilter()`: Dispatcher for filter modes
- Filter modes:
  - `"none"`: No filtering
  - `"median"`: Iterative median filter (removes salt-and-pepper noise)
  - `"morphological"`: Grey opening (preserves signal better, recommended)
  - `"rolling_ball"`: Rolling ball background subtraction + median filter
- Uses Numba JIT compilation when available for performance

**SolveSpectrum.py**: Core physics calculations
- `SolveSpectrum()`: Converts 2D image to energy spectrum
- Translated from MATLAB (MATTPS v3.0 by 徐诗睿)
- Accounts for: magnetic/electric field deflection, MCP efficiency, detector geometry, receiving angle

**TDraw.py**: Visualization
- `DrawImage()`: Renders pseudocolor image with optional parabola overlay
- `DrawSpec()`: Plots energy spectrum (log scale)
- `DrawParabola()`: Overlays theoretical parabola trajectory
- `DrawOrigin()`: Marks coordinate origin
- **Critical bug fix**: Uses pre-filtered `app.imageData` instead of re-reading raw file

**TCompare.py**: Proton spectrum comparison (Added/Updated 2025-11-13)
- `compensateElectricField()`: Hybrid approach for electric field compensation
  - Uses theoretical formula + local contour refinement (within ±dY*1.2 range)
  - Dynamic search radius: larger for low-energy regions where theory is less accurate
  - Weighted centroid calculation using squared intensity (focuses on peak center)
  - Extracts large range (`extract_range=150px`) from original image to support adjustable display
- `CompareWindow`: Qt window for multi-image comparison
- Architecture: **Single axes + vertical image stacking** (avoids subplot layout conflicts with aspect='equal')
- Physics: Removes electric field (Y-direction) deflection to show magnetic-only trajectories
- Display:
  - All images vertically stacked in one axes (separated by black divider lines)
  - X-axis inverted, showing non-linear energy scale (high energy left, low energy right)
  - Y-axis shows filenames at center of each image strip
  - Adjustable Y display range (default 80px, range 20-300px) controls background visibility
  - Custom energy tick marks supported (e.g., "20, 40, 60, 70")
  - Red dashed line marks Y0 (compensated proton line position)
  - Automatic cropping of blank columns
- Key Implementation Details:
  - Uses `make_axes_locatable` for proper colorbar alignment
  - `ax.set_xlim(max, min)` to reverse X-axis (instead of flipping image)
  - Energy-to-position mapping: `x_pixel = X0 + TB/sqrt(2*A*E)/Res`
  - **Critical**: Must extract large data range in compensation stage to support user-adjustable display range
- Use case: Compare proton spectra from different shots by aligning them in magnetic deflection coordinates

**TWatchDog.py**: Real-time monitoring (Windows only)
- Uses `watchdog` library to monitor image directory
- Triggers analysis on new files
- Uses `pywin32` for window manipulation and auto-triggering external software

## Development Commands

### Running the Application
```bash
python PyTPS.py
```

### Testing
Test files are in the root directory:
```bash
python test_rolling_ball_comparison.py    # Compare rolling ball implementations
python test_selective_denoise.py          # Test selective denoising
python test_enhanced_denoise.py          # Test enhanced denoising
python test_performance_numba.py         # Benchmark Numba acceleration
```

### Building Executable
```bash
pyinstaller PyTPS.spec
```

The spec file is configured to:
- Use `icon.png` as the application icon
- Bundle all dependencies into a single executable
- Run without console window (GUI mode)

### Dependencies
Install required packages (no requirements.txt provided, infer from imports):
```bash
pip install PySide6 numpy matplotlib scipy scikit-image watchdog pywin32 numba pyautogui
```

## Configuration Files

### PyTPS_init.ini
Application initialization parameters (tab-delimited):
- Image/save/MCP data paths
- Coordinate origin (X0, Y0), integration window (dY)
- Energy range (Emin, Emax), color scale (colormin, colormax)
- Spectrum plot limits (specEmin, specEmax, specdNdEmin, specdNdEmax)
- Filter configuration (filterMode, medianSize, medianIterations, morphologicalSize, rollingBallRadius)

### TPS_Settings.ini
TPS hardware parameters (tab-delimited):
- B: Magnetic field strength (Tesla)
- U: Electric field voltage (Volts)
- EMGain: EMCCD gain
- S1, L, D, L0, etc.: Geometric dimensions (mm)
- Res: Detector pixel resolution (mm/pixel)
- QE: Quantum efficiency

### MCP Efficiency Files
Tab-delimited text files (e.g., `mcp-proton.txt`):
- Column 1: Energy (MeV)
- Column 2: Detection efficiency (0-1)

## Important Implementation Details

### Data Flow Critical Path
1. Image is loaded and filtered in `TSolve.Solve()`
2. Result is stored in `app.imageData` (already flipped vertically)
3. `TDraw.DrawImage()` MUST use `app.imageData`, NOT re-read the file (to preserve filtering)
4. This was a bug fixed on 2025-10-23 - see comments in `TDraw.py:9-14`

### Filter Parameter Tuning
- **Median filter**: Good for salt-and-pepper noise, but can blur edges
  - `medianSize`: 5-7 recommended (must be odd)
  - `medianIterations`: 1-2 (more iterations = more smoothing)
- **Morphological**: Best signal preservation, recommended for TPS data
  - `morphologicalSize`: 3-5 (small SE preserves peaks)
- **Rolling ball**: Best for uneven background, but slower
  - `rollingBallRadius`: 15-30 (match background feature size)

### Coordinate System
- Images are loaded and flipped vertically (`np.flipud()`) to match TPS coordinates
- Origin (X0, Y0) is in flipped coordinates (bottom-left origin, like physics convention)
- Parabola opens upward in energy (higher Y = higher E)

### Performance Optimization
- Numba JIT compilation is optional but recommended for rolling ball filter
- Falls back to pure NumPy if Numba unavailable
- Check imports in `TFilter.py:16-27` for Numba availability detection

### Platform-Specific Code
- `TWatchDog.py` uses Windows-specific `pywin32` APIs for:
  - Window handle manipulation (`win32gui`, `win32api`)
  - Blocking user input during automation (`windll.user32.BlockInput`)
  - Auto-triggering external software (`pyautogui`)
- This module will not work on Linux/macOS

## Common Tasks

### Adding a New Filter Method
1. Implement filter function in `TFilter.py` (follow existing signatures)
2. Add new mode string to `applyFilter()` dispatcher (line 30)
3. Add UI controls in `PyTPS.createFilterUI()` method
4. Add parameter to `PyTPS_init.ini` and `TSettings.TPSinit()`

### Modifying TPS Physics
- Edit `SolveSpectrum.py` carefully - this is translated MATLAB code
- Key equations are around lines 22-28 (field deflections) and 63-98 (spectrum calculation)
- Test with known reference data before deploying

### Adding New Particle Types
- Edit `TSettings.particalList()` to add entries to dropdown
- Follow pattern: `"Symbol-Z"` format
- Add corresponding A, Z values in `PyTPS.chooseParticle()` method (around line 200)

### Using Proton Spectrum Comparison
The comparison window allows side-by-side analysis of multiple TPS images:

1. **Open Comparison Window**: Click "质子谱线对比" button in main window
2. **Select Images**: In the file list, select multiple images to compare (hold Ctrl/Shift)
3. **Adjust Parameters** (optional):
   - **Custom Energy Ticks**: Enter energy values like "5, 10, 15, 20, 30" or leave blank for auto
   - **Y Display Range**: Adjust pixel range (20-300px, default 80px) to show more/less background
4. **Generate Comparison**: Click "生成对比图" button
5. **Understanding the Display**:
   - All images stacked vertically in one plot (single axes)
   - Black horizontal lines separate different images
   - Red dashed lines mark Y0 (compensated proton line position) for each image
   - Filenames displayed on Y-axis at center of each image strip
   - X-axis shows proton energy (MeV): high energy on left, low energy on right
   - Non-linear energy scale accounts for magnetic deflection formula
6. **Physics**:
   - Electric field causes Y-deflection: ΔY = TE/(E·Res) pixels
   - Each column is shifted vertically to compensate for this deflection
   - After compensation, proton trajectories align at Y=0 (magnetic-only)
   - Theory-based compensation refined by local contour detection (search radius adapts with energy)
   - This allows direct comparison of magnetic deflection (X-direction) across shots
7. **Clear**: Click "清除" to reset and select different images

### Proton Spectrum Comparison: Implementation Pitfalls

When modifying `TCompare.py`, be aware of these common pitfalls:

#### Pitfall 1: Subplot Layout Hell
**Problem**: Using `plt.subplots()` with `aspect='equal'` causes layout conflicts. No combination of `hspace`, `constrained_layout`, `GridSpec`, or `height_ratios` works reliably.

**Solution**: Use single axes with `np.vstack()` to vertically stack images. This completely avoids subplot layout issues.

#### Pitfall 2: Qt-Matplotlib Integration
**Problem**: Creating new `fig = plt.figure()` each time breaks Qt's size management.

**Solution**: Reuse `self.figure` and update with `set_size_inches()`. Use `draw_idle()` instead of `draw()`.

#### Pitfall 3: Curved Proton Lines After Compensation
**Problem**: Pure theoretical formula leaves residual curvature, especially at low energies. Pure contour detection makes proton lines disappear.

**Solution**: Hybrid approach - use theory for initial position, then local search within small radius. Key code:
```python
# Dynamic search radius - larger for low energy
energy_factor = max(1.0, Emax / E) if E > 0.1 else 3.0
search_radius = int(dY * 1.2 * min(energy_factor, 3.0))

# Weighted centroid with squared intensity
weights = (signal - background) ** 2
centroid = np.sum(indices * weights) / np.sum(weights)
```

#### Pitfall 4: Blank Areas in Display
**Problem**: Adjusting Y display range shows only black regions (no data).

**Root Cause**: The `compensateElectricField()` function only extracts a small range (`3*dY ≈ 150px`) from original image. The compensated image has lots of zeros outside this range.

**Solution**: Set `extract_range = 150` (pixels) to extract ±150px from original image, supporting up to 300px display range. This is **independent** of the dY parameter used for contour tracking.

**Critical Code**:
```python
# In compensateElectricField():
extract_range = 150  # Must be ≥ max_display_range/2

# In drawComparison():
strip_height_px = self.yRangeSpinBox.value()  # User setting
strip_y_min = max(0, newY0 - strip_height_px // 2)
strip_y_max = min(data['image'].shape[0], newY0 + strip_height_px // 2)
imageRegion = data['image'][strip_y_min:strip_y_max, :]
# DO NOT auto-crop blank rows here!
```

#### Pitfall 5: Colorbar Height Mismatch
**Problem**: Standard `fig.colorbar()` doesn't align properly with axes height.

**Solution**: Use `make_axes_locatable` from `mpl_toolkits.axes_grid1`:
```python
from mpl_toolkits.axes_grid1 import make_axes_locatable
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="2%", pad=0.1)
fig.colorbar(im, cax=cax)
```

#### Pitfall 6: X-Axis Direction Confusion
**Problem**: Wanting "high energy on left" - should I flip the image with `np.fliplr()`?

**Solution**: NO. Keep image as-is, just reverse the axis limits: `ax.set_xlim(x_max, x_min)`. Flipping the image causes coordinate mapping errors.

#### Data Flow Summary
```
Original Image (bent parabola)
    ↓
compensateElectricField():
  - Extract large range (extract_range=150px) around theory+refined position
  - Shift to Y0 → straight line in compensated image
  - Compensated image has real data ±150px around Y0, zeros elsewhere
    ↓
drawComparison():
  - Extract user-specified range (strip_height_px, default 80px) from compensated image
  - Stack vertically without auto-cropping blanks
  - Display with energy axis
```

**Key Lesson**: The compensation stage and display stage must extract data at different scales. Compensation needs small dY for accurate tracking but large extract_range for flexible display.

