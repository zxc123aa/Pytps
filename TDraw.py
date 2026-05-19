import TImageRead
import numpy as np
import os


def _spectrum_particle_label(app):
    try:
        if int(getattr(app, "A", 0)) == 1 and int(getattr(app, "Z", 0)) == 1:
            return "protons"
    except (TypeError, ValueError):
        pass
    return "ions"


def _set_spectrum_axes(app):
    particle = _spectrum_particle_label(app)
    app.ax_spec.set_xlabel("Energy (MeV)", fontsize=14, labelpad=6)
    app.ax_spec.set_ylabel(
        rf"$d^2N/(dE\,d\Omega)$ ({particle} MeV$^{{-1}}$ sr$^{{-1}}$)",
        fontsize=14,
        labelpad=8
    )
    app.ax_spec.minorticks_on()
    app.ax_spec.tick_params(direction="in", which="both", top=True, right=True, labelsize=12)


def _finish_spectrum_layout(app):
    app.ax_spec.legend(frameon=False, fontsize=10)
    app.specFig.subplots_adjust(left=0.20, bottom=0.18, right=0.97, top=0.96)


def DrawImage(app):
    if os.path.isfile(app.imageFileName):
        app.imageFig.clf()
        pic = getattr(app, "displayImage", app.imageData)

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

        if hasattr(app, "drawManualMaskOverlay"):
            app.drawManualMaskOverlay()

        view = app.zoomPic if app.zoomed else pic
        app.ax_image.set_xlim(-0.5, view.shape[1] - 0.5)
        app.ax_image.set_ylim(view.shape[0] - 0.5, -0.5)

        app.imageCanvas.draw()
        print(f"[TDraw] 绘制图像完成，使用displayImage，形状: {pic.shape}")


def DrawSpec(app):
    if os.path.isfile(app.imageFileName):
        app.specFig.clf()
        app.ax_spec = app.specFig.subplots()
        app.ax_spec.set_xlim(app.specEmin, app.specEmax)
        app.ax_spec.set_ylim(app.specdNdEmin, app.specdNdEmax)
        _set_spectrum_axes(app)
        if hasattr(app, "specDataRaw"):
            app.ax_spec.semilogy(app.specDataRaw[0], app.specDataRaw[1], alpha=0.45, linewidth=1.0,
                                 label="Raw center-band")
        if hasattr(app, "noiseSpec"):
            app.ax_spec.semilogy(app.noiseSpec[0], app.noiseSpec[1], alpha=0.55, linewidth=1.0,
                                 linestyle='--', label="Raw background")
        if hasattr(app, "specDataNet"):
            app.ax_spec.semilogy(app.specDataNet[0], app.specDataNet[1], alpha=0.65, linewidth=1.1,
                                 label="Background-subtracted")
        app.ax_spec.semilogy(app.specData[0], app.specData[1], linewidth=2.0,
                             label="Smoothed background-subtracted")
        _finish_spectrum_layout(app)
        # app.ax_spec.plot(app.specData[0], app.specData[1])
        # app.ax_spec.plot(app.noiseSpec[0], app.noiseSpec[1])

        if isinstance(app.specCursor, str):
            pass
        else:
            app.ax_spec.axvline(app.specCursor, linewidth=1.2, color='black')
            app.ui.lineEdit_cursor.setText(str(np.round(app.specCursor, 2)))
            # app.pv.put(np.round(app.specCursor,2))
        app.specCanvas.draw()


def DrawParabola(app):
    if app.zoomed == False:
        app.ax_image.plot(app.TPSParabola[0], app.TPSParabola[1], alpha=0.5, linewidth=2, color='red')
        if getattr(app, 'backgroundMode', None) == "offset" and hasattr(app, 'backgroundParabola'):
            app.ax_image.plot(app.backgroundParabola[0], app.backgroundParabola[1], alpha=0.7,
                              linewidth=1.5, color='lime', linestyle='--')
    else:
        app.ax_image.plot(app.zoomPara[0], app.zoomPara[1], alpha=0.5, linewidth=2, color='red')
        if getattr(app, 'backgroundMode', None) == "offset" and hasattr(app, 'zoomBackgroundPara'):
            app.ax_image.plot(app.zoomBackgroundPara[0], app.zoomBackgroundPara[1], alpha=0.7,
                              linewidth=1.5, color='lime', linestyle='--')
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
    _set_spectrum_axes(app)
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
        _finish_spectrum_layout(app)
        app.ax_spec.axvline(app.specCursor, linewidth=1.2, color='black')
        app.ui.lineEdit_cursor.setText(str(np.round(app.specCursor, 2)))
    app.specCanvas.draw()
