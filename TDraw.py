import TImageRead
import numpy as np
import os


def DrawImage(app):
    if os.path.isfile(app.imageFileName):
        app.imageFig.clf()
        # 修复：使用已经滤波过的imageData，而不是重新读取文件
        # 原代码会绕过滤波，直接显示原始图片！
        # pic, app.is8bitImage = TImageRead.readImage(app.imageFileName)
        # pic = np.flipud(pic)

        # 正确做法：使用TSolve.py中已经滤波并翻转的imageData
        pic = app.imageData

        app.ax_image = app.imageFig.subplots()
        if app.zoomed == False:
            img = app.ax_image.imshow(pic, cmap=app.cmap, vmin=app.colormin, vmax=app.colormax)
        else:
            img = app.ax_image.imshow(app.zoomPic, cmap=app.cmap, vmin=app.colormin, vmax=app.colormax)
        app.ax_image.invert_yaxis()
        app.imageFig.colorbar(img, ax=app.ax_image)
        if app.imageCursor == None:
            pass
        else:
            if app.zoomed == False:
                app.ax_image.axvline(app.imageCursor, linewidth=1, color='black')
            else:
                app.ax_image.axvline(app.zoomImageCursor, linewidth=1, color='black')

        app.imageCanvas.draw()
        print(f"[TDraw] 绘制图像完成，使用滤波后的imageData，形状: {pic.shape}")


def DrawSpec(app):
    if os.path.isfile(app.imageFileName):
        app.specFig.clf()
        app.ax_spec = app.specFig.subplots()
        app.ax_spec.set_xlim(app.specEmin, app.specEmax)
        app.ax_spec.set_ylim(app.specdNdEmin, app.specdNdEmax)
        app.ax_spec.set_xlabel("E(MeV)")
        app.ax_spec.set_ylabel("dNdE")
        app.ax_spec.semilogy(app.specData[0], app.specData[1])
        app.ax_spec.semilogy(app.noiseSpec[0], app.noiseSpec[1])
        # app.ax_spec.plot(app.specData[0], app.specData[1])
        # app.ax_spec.plot(app.noiseSpec[0], app.noiseSpec[1])

        if isinstance(app.specCursor, str):
            pass
        else:
            app.ax_spec.axvline(app.specCursor, linewidth=1, color='black')
            app.ui.lineEdit_cursor.setText(str(np.round(app.specCursor, 2)))
            # app.pv.put(np.round(app.specCursor,2))
        app.specCanvas.draw()


def DrawParabola(app):
    if app.zoomed == False:
        app.ax_image.plot(app.TPSParabola[0], app.TPSParabola[1], alpha=0.5, linewidth=2, color='red')
    else:
        app.ax_image.plot(app.zoomPara[0], app.zoomPara[1], alpha=0.5, linewidth=2, color='red')
    app.imageCanvas.draw()


def DrawOrigin(app):
    if app.zoomed == False:
        hLine = np.array([np.arange(app.X0 - 50, app.X0 + 51), np.linspace(app.Y0, app.Y0, 101, dtype=int)])
        vLine = np.array([np.linspace(app.X0, app.X0, 101, dtype=int), np.arange(app.Y0 - 50, app.Y0 + 51)])
        app.ax_image.plot(hLine[0], hLine[1], linewidth=1, color='black')
        app.ax_image.plot(vLine[0], vLine[1], linewidth=1, color='black')
        app.imageCanvas.draw()
    else:
        pass


def DrawAnalysingSpec(app):
    app.specFig.clf()
    app.ax_spec = app.specFig.subplots()
    app.ax_spec.set_xlim(app.specEmin, app.specEmax)
    app.ax_spec.set_ylim(app.specdNdEmin, app.specdNdEmax)
    app.ax_spec.set_xlabel("E(MeV)")
    app.ax_spec.set_ylabel("dNdE")
    if app.analysingDataList == []:
        pass
    else:
        for i in range(len(app.analysingDataList)):
            if isinstance(app.cutoffEnergyList[i], str):
                app.ax_spec.semilogy(app.analysingDataList[i][0], app.analysingDataList[i][1], label=str(
                    os.path.splitext(os.path.basename(app.analysingFileList[i]))[0]) + '--NaN')
            else:
                app.ax_spec.semilogy(app.analysingDataList[i][0], app.analysingDataList[i][1], label=str(
                    os.path.splitext(os.path.basename(app.analysingFileList[i]))[0]) + '--' + str(
                    app.cutoffEnergyList[i]) + 'MeV')
        app.ax_spec.legend()
        app.ax_spec.axvline(app.specCursor, linewidth=1, color='black')
        app.ui.lineEdit_cursor.setText(str(np.round(app.specCursor, 2)))
    app.specCanvas.draw()
