import TDraw, SolveSpectrum, AutoCutoffEnergy, TPSParabola, TImageRead, TFilter
import numpy as np
import os


def Solve(app):
    if os.path.isfile(app.imageFileName) and app.isAnalysing == False:
        app.zoomed = False
        img, app.is8bitImage = TImageRead.readImage(app.imageFileName)

        # 应用滤波（新增）
        filterParams = {
            'medianSize': app.medianSize,
            'medianIterations': app.medianIterations,
            'morphologicalSize': app.morphologicalSize,
            'rollingBallRadius': app.rollingBallRadius,  # 恢复滚球法参数
            'fadeRadius': app.fadeRadius if hasattr(app, 'fadeRadius') else 20,  # 软掩膜羽化半径
            # 形态学分割参数（简化版）
            'thresholdValue': getattr(app, 'thresholdValue', 500),
            'morphKernelSize': getattr(app, 'morphKernelSize', 3),
            'showSegmentationMask': getattr(app, 'showSegmentationMask', False),
            # 轨迹保护滤波需要的TPS参数（保留向后兼容）
            'X0': app.X0,
            'Y0': app.Y0,
            'A': app.A,
            'Z': app.Z,
            'Emin': app.Emin,
            'Emax': app.Emax,
            'dY': app.dY,
            'TPS': app.TPS,
            'protectionWidth': app.protectionWidth if hasattr(app, 'protectionWidth') else int(app.dY * 3),
            'aggressiveSize': app.aggressiveSize if hasattr(app, 'aggressiveSize') else 15,
            'gentleSize': app.gentleSize if hasattr(app, 'gentleSize') else 5,
        }
        print(f"[TSolve] 应用滤波: mode={app.filterMode}, params={filterParams}")
        img = TFilter.applyFilter(img, app.filterMode, filterParams)
        print(f"[TSolve] 滤波完成，图像形状: {img.shape}, 数据类型: {img.dtype}")

        app.imageData = np.flipud(img)
        app.zoomPic = app.imageData
        app.specData, app.noiseSpec = SolveSpectrum.SolveSpectrum(app.imageData, app.X0, app.Y0, app.A, app.Z, app.Emin,
                                                                  app.Emax, app.dY, app.MCPPath, app.TPS,
                                                                  app.is8bitImage)
        app.TPSParabola = TPSParabola.Parabola(app.TPS, app.specData[0], app.X0, app.Y0, app.A, app.Z,
                                               app.imageData.shape[1])
        # app.cutoffEnergy = AutoCutoffEnergy.CutoffEnergy(app.specData, app.noiseSpec, app.Emin, app.Emax,
        #                                                  app.specWindow)
        # app.specCursor = AutoCutoffEnergy.CutoffEnergy(app.specData, app.noiseSpec, app.Emin, app.Emax, app.specWindow)
        app.cutoffEnergy = 0
        app.specCursor = 0
        # app.imageCursor = TPSParabola.CutoffLine(app.TPS, app.specCursor, app.X0, app.A, app.Z)
        app.imageCursor = 0
        TDraw.DrawImage(app)
        TDraw.DrawSpec(app)

        if app.isShowParabola:
            TDraw.DrawParabola(app)

        TDraw.DrawOrigin(app)
        app.ui.lineEdit_cutoff.setText(str(app.cutoffEnergy))
        # app.pv.put(app.cutoffEnergy)

        if app.isAutoSave == True:
            app.saveImage()
            app.saveSpec()

    if app.isAnalysing == True:
        app.analysingDataList = []
        app.cutoffEnergyList = []
        if app.analysingFileList == []:
            app.specCursor = 0.0
            TDraw.DrawAnalysingSpec(app)
        else:
            for image in app.analysingFileList:
                img, app.is8bitImage = TImageRead.readImage(image)

                # 应用滤波（新增）
                filterParams = {
                    'medianSize': app.medianSize,
                    'medianIterations': app.medianIterations,
                    'morphologicalSize': app.morphologicalSize,
                    'rollingBallRadius': app.rollingBallRadius,  # 恢复滚球法参数
                    'fadeRadius': app.fadeRadius if hasattr(app, 'fadeRadius') else 20,  # 软掩膜羽化半径
                    # 形态学分割参数（简化版）
                    'thresholdValue': getattr(app, 'thresholdValue', 500),
                    'morphKernelSize': getattr(app, 'morphKernelSize', 3),
                    'showSegmentationMask': getattr(app, 'showSegmentationMask', False),
                    # 轨迹保护滤波需要的TPS参数（保留向后兼容）
                    'X0': app.X0,
                    'Y0': app.Y0,
                    'A': app.A,
                    'Z': app.Z,
                    'Emin': app.Emin,
                    'Emax': app.Emax,
                    'dY': app.dY,
                    'TPS': app.TPS,
                    'protectionWidth': app.protectionWidth if hasattr(app, 'protectionWidth') else int(app.dY * 3),
                    'aggressiveSize': app.aggressiveSize if hasattr(app, 'aggressiveSize') else 15,
                    'gentleSize': app.gentleSize if hasattr(app, 'gentleSize') else 5,
                }
                img = TFilter.applyFilter(img, app.filterMode, filterParams)

                data = np.flipud(img)
                spec, noise = SolveSpectrum.SolveSpectrum(data, app.X0, app.Y0, app.A, app.Z, app.Emin, app.Emax,
                                                          app.dY, app.MCPPath, app.TPS, app.is8bitImage)
                app.analysingDataList.append(spec)
                app.cutoffEnergyList.append(
                    AutoCutoffEnergy.CutoffEnergy(spec, noise, app.Emin, app.Emax, app.specWindow))
            app.specCursor = 0.0
            TDraw.DrawAnalysingSpec(app)
