import sys


import ui_PyTPS
from PySide6 import QtWidgets, QtGui, QtCore
import TSettings, CustomColormaps, TDraw, TPSParabola, TWatchDog, TSolve, TSave, TCompare
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import os
from watchdog.observers import Observer
import datetime


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        # 初始化UI
        super().__init__()

        # self.pv = PV("TPS_pv:TPS_cutoff_energy:pv")
        self.ui = ui_PyTPS.Ui_MainWindow()
        self.ui.setupUi(self)
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap("icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(self.icon)

        # 初始化参数，self中新增了TPS,imagePath,imageFileName,savePath,MCPPath,X0,Y0,dY,Emin,Emax,colormin,colormax,specEmin,specEmax,specdNdEmin,specdNdEmax,specWindow变量
        TSettings.TPSinit(self)

        # 初始化新滤波参数（如果配置文件中没有，使用默认值）
        if not hasattr(self, 'thresholdValue'):
            self.thresholdValue = 500
        if not hasattr(self, 'minConnectedArea'):
            self.minConnectedArea = 50
        if not hasattr(self, 'fadeRadius'):
            self.fadeRadius = 20

        self.mode = "offline"
        self.zoomed = False
        self.isShowParabola = False
        self.isAutoSave = False
        self.isAnalysing = False
        self.is8bitImage = False
        self.imageData = []
        self.specData = []
        self.noiseSpec = []
        self.TPSParabola = []
        self.analysingFileList = []
        self.analysingDataList = []
        self.cutoffEnergyList = []

        # 初始化文件列表
        TSettings.getList(self)
        # 初始化离子种类列表和伪彩图类型列表，此处创建了self中的A,Z,cmap变量
        TSettings.particalList(self)
        TSettings.colormapList(self)

        # 初始化参数写入GUI
        self.ui.lineEdit_imagePath.setText(self.imagePath)
        self.ui.lineEdit_savePath.setText(self.savePath)
        self.ui.lineEdit_MCPPath.setText(self.MCPPath)
        self.ui.lineEdit_X0.setText(np.str_(self.X0))
        self.ui.lineEdit_Y0.setText(np.str_(self.Y0))
        self.ui.lineEdit_dY.setText(np.str_(self.dY))
        self.ui.lineEdit_Emin.setText(np.str_(self.Emin))
        self.ui.lineEdit_Emax.setText(np.str_(self.Emax))
        self.ui.lineEdit_colormin.setText(np.str_(self.colormin))
        self.ui.lineEdit_colormax.setText(np.str_(self.colormax))
        self.ui.lineEdit_specEmin.setText(np.str_(self.specEmin))
        self.ui.lineEdit_specEmax.setText(np.str_(self.specEmax))
        self.ui.lineEdit_specdNdEmin.setText(np.format_float_scientific(self.specdNdEmin))
        self.ui.lineEdit_specdNdEmax.setText(np.format_float_scientific(self.specdNdEmax))
        self.ui.lineEdit_specWindow.setText(np.str_(self.specWindow))

        # 设置文本框验证规则
        self.ui.lineEdit_A.setValidator(QtGui.QIntValidator(self.Z, 500))
        self.ui.lineEdit_Z.setValidator(QtGui.QIntValidator(0, self.A))
        self.ui.lineEdit_X0.setValidator(QtGui.QIntValidator(0, 1024))
        self.ui.lineEdit_Y0.setValidator(QtGui.QIntValidator(0, 1024))
        self.ui.lineEdit_dY.setValidator(QtGui.QIntValidator(0, 20))
        self.ui.lineEdit_Emin.setValidator(QtGui.QDoubleValidator(0.0, self.Emax, 5))
        self.ui.lineEdit_Emax.setValidator(QtGui.QDoubleValidator(self.Emin, 1000.0, 5))
        self.ui.lineEdit_colormin.setValidator(QtGui.QIntValidator(0, self.colormax))
        self.ui.lineEdit_colormax.setValidator(QtGui.QIntValidator(self.colormin, 65535))
        self.ui.lineEdit_specEmin.setValidator(QtGui.QDoubleValidator(0.0, self.specEmax, 5))
        self.ui.lineEdit_specEmax.setValidator(QtGui.QDoubleValidator(self.specEmin, 1000.0, 5))
        self.ui.lineEdit_specdNdEmin.setValidator(QtGui.QDoubleValidator(0.0, self.specdNdEmax, 5))
        self.ui.lineEdit_specdNdEmax.setValidator(QtGui.QDoubleValidator(self.specdNdEmin, 1e100, 5))
        self.ui.lineEdit_specWindow.setValidator(QtGui.QDoubleValidator(0.0, self.Emax, 3))

        # 初始化图片画布
        self.imageFig = plt.figure()
        self.imageCanvas = FigureCanvas(self.imageFig)
        self.ui.gridLayout_image.addWidget(self.imageCanvas)

        # 初始化能谱画布
        self.specFig = plt.figure()
        self.specCanvas = FigureCanvas(self.specFig)
        self.ui.verticalLayout_spec.addWidget(self.specCanvas)

        # 动态创建滤波UI（新增）
        self.createFilterUI()

        # 创建对比窗口（新增）
        self.compareWindow = None

        # 信号绑定

        # 各种路径浏览
        self.ui.pushButton_browseImagePath.clicked.connect(self.browseImagePath)
        self.ui.pushButton_browseMCPPath.clicked.connect(self.browseMCPPath)
        self.ui.pushButton_browseSavePath.clicked.connect(self.browseSavePath)
        self.ui.pushButton_refreshImagePath.clicked.connect(self.refreshImagePath)
        self.ui.pushButton_openTPS.clicked.connect(self.openTPS)

        # 各种数值改变
        self.ui.pushButton_refreshTPS.clicked.connect(self.refreshTPS)
        self.ui.lineEdit_A.textChanged.connect(self.setA)
        self.ui.lineEdit_Z.textChanged.connect(self.setZ)
        self.ui.comboBox_particals.currentIndexChanged.connect(self.choosePartical)
        self.ui.comboBox_colormap.currentTextChanged.connect(self.chooseColormap)
        self.ui.lineEdit_X0.editingFinished.connect(self.setX0)
        self.ui.lineEdit_Y0.editingFinished.connect(self.setY0)
        self.ui.lineEdit_dY.editingFinished.connect(self.setdY)
        self.ui.lineEdit_Emin.editingFinished.connect(self.setEmin)
        self.ui.lineEdit_Emax.editingFinished.connect(self.setEmax)
        self.ui.lineEdit_colormin.editingFinished.connect(self.setColormin)
        self.ui.lineEdit_colormax.editingFinished.connect(self.setColormax)
        self.ui.lineEdit_specEmin.editingFinished.connect(self.setSpecEmin)
        self.ui.lineEdit_specEmax.editingFinished.connect(self.setSpecEmax)
        self.ui.lineEdit_specdNdEmin.editingFinished.connect(self.setSpecdNdEmin)
        self.ui.lineEdit_specdNdEmax.editingFinished.connect(self.setSpecdNdEmax)
        self.ui.lineEdit_specWindow.editingFinished.connect(self.setSpecWindow)

        # 离线模式：选择图片绘图解谱
        self.ui.listWidget.itemClicked.connect(self.selectImage)

        # 切换在线/离线/分析模式
        self.ui.radioButton_online.toggled.connect(self.modeSwitch)
        self.ui.radioButton_offline.toggled.connect(self.modeSwitch)
        self.ui.checkBox_analyse.stateChanged.connect(self.analyseMode)

        # 是否显示参考抛物线
        self.ui.checkBox_parabola.stateChanged.connect(self.showParabola)

        # 保存当前结果
        self.ui.pushButton_saveSpec.clicked.connect(self.saveSpec)
        self.ui.pushButton_saveImage.clicked.connect(self.saveImage)

        # 是否自动保存
        self.ui.checkBox_autoSave.stateChanged.connect(self.autoSave)

        # 图片缩放
        self.ui.pushButton_zoom.toggled.connect(self.startZoom)
        self.ui.pushButton_origin.clicked.connect(self.stopZoom)

        # 点击能谱曲线移动光标
        self.specFig.canvas.mpl_connect('button_press_event', self.setSpecCursor)

        # 帮助&关于
        self.ui.pushButton_help.clicked.connect(self.help)
        self.ui.pushButton_about.clicked.connect(self.about)

        # 添加对比窗口按钮（新增）
        self.createCompareButton()

    # 各种槽函数

    def browseImagePath(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "选择文件夹", ".")
        if os.path.exists(path) == False:
            QtWidgets.QMessageBox.critical(self, "错误", "路径不存在，请重新选择！")
            return
        self.imagePath = path
        self.ui.lineEdit_imagePath.setText(self.imagePath)
        if self.mode == "online":
            observer.unschedule_all()
            observer.schedule(event_handler, self.imagePath, recursive=False)

    def browseMCPPath(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, "选择MCP效率文件", ".")
        if os.path.exists(path) == False:
            QtWidgets.QMessageBox.critical(self, "错误", "路径不存在，请重新选择！")
            return
        self.MCPPath, _ = path
        self.ui.lineEdit_MCPPath.setText(self.MCPPath)
        TSolve.Solve(self)

    def browseSavePath(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "选择保存文件夹", ".")
        if os.path.exists(path) == False:
            QtWidgets.QMessageBox.critical(self, "错误", "路径不存在，请重新选择！")
            return
        self.savePath = path
        self.ui.lineEdit_savePath.setText(self.savePath)

    def refreshImagePath(self):
        self.ui.listWidget.clear()
        TSettings.getList(self)

    def openTPS(self):
        os.startfile("TPS_Settings.ini")

    def refreshTPS(self):
        self.TPS = TSettings.TPS()
        TSolve.Solve(self)

    def setA(self):
        self.A = int(self.ui.lineEdit_A.text())

    def setZ(self):
        self.Z = int(self.ui.lineEdit_Z.text())

    def choosePartical(self, index):
        if index == 12:
            self.ui.lineEdit_A.setReadOnly(False)
            self.ui.lineEdit_Z.setReadOnly(False)
        else:
            self.ui.lineEdit_A.setReadOnly(True)
            self.ui.lineEdit_Z.setReadOnly(True)
            if index == 0:
                self.ui.lineEdit_A.setText("1")
                self.ui.lineEdit_Z.setText("1")
            elif index == 1:
                self.ui.lineEdit_A.setText("12")
                self.ui.lineEdit_Z.setText("6")
            elif index == 2:
                self.ui.lineEdit_A.setText("16")
                self.ui.lineEdit_Z.setText("8")
            elif index == 3:
                self.ui.lineEdit_A.setText("16")
                self.ui.lineEdit_Z.setText("7")
            elif index == 4:
                self.ui.lineEdit_A.setText("12")
                self.ui.lineEdit_Z.setText("5")
            elif index == 5:
                self.ui.lineEdit_A.setText("16")
                self.ui.lineEdit_Z.setText("6")
            elif index == 6:
                self.ui.lineEdit_A.setText("12")
                self.ui.lineEdit_Z.setText("4")
            elif index == 7:
                self.ui.lineEdit_A.setText("16")
                self.ui.lineEdit_Z.setText("5")
            elif index == 8:
                self.ui.lineEdit_A.setText("12")
                self.ui.lineEdit_Z.setText("3")
            elif index == 9:
                self.ui.lineEdit_A.setText("16")
                self.ui.lineEdit_Z.setText("4")
            elif index == 10:
                self.ui.lineEdit_A.setText("12")
                self.ui.lineEdit_Z.setText("2")
            elif index == 11:
                self.ui.lineEdit_A.setText("12")
                self.ui.lineEdit_Z.setText("1")
        TSolve.Solve(self)

    def chooseColormap(self, cmap):
        if cmap == "partical":
            self.cmap = CustomColormaps.particals
        elif cmap == "field":
            self.cmap = CustomColormaps.field
        else:
            self.cmap = cmap
        TDraw.DrawImage(self)

    def setX0(self):
        self.X0 = int(self.ui.lineEdit_X0.text())
        TSolve.Solve(self)

    def setY0(self):
        self.Y0 = int(self.ui.lineEdit_Y0.text())
        TSolve.Solve(self)

    def setdY(self):
        self.dY = int(self.ui.lineEdit_dY.text())
        TSolve.Solve(self)

    def setEmin(self):
        self.Emin = float(self.ui.lineEdit_Emin.text())
        TSolve.Solve(self)

    def setEmax(self):
        self.Emax = float(self.ui.lineEdit_Emax.text())
        TSolve.Solve(self)

    def setColormin(self):
        self.colormin = int(self.ui.lineEdit_colormin.text())
        TDraw.DrawImage(self)

    def setColormax(self):
        self.colormax = int(self.ui.lineEdit_colormax.text())
        TDraw.DrawImage(self)

    def setSpecEmin(self):
        self.specEmin = float(self.ui.lineEdit_specEmin.text())
        if self.isAnalysing == False:
            TDraw.DrawSpec(self)
        else:
            TDraw.DrawAnalysingSpec(self)

    def setSpecEmax(self):
        self.specEmax = float(self.ui.lineEdit_specEmax.text())
        if self.isAnalysing == False:
            TDraw.DrawSpec(self)
        else:
            TDraw.DrawAnalysingSpec(self)

    def setSpecdNdEmin(self):
        self.specdNdEmin = float(self.ui.lineEdit_specdNdEmin.text())
        if self.isAnalysing == False:
            TDraw.DrawSpec(self)
        else:
            TDraw.DrawAnalysingSpec(self)

    def setSpecdNdEmax(self):
        self.specdNdEmax = float(self.ui.lineEdit_specdNdEmax.text())
        if self.isAnalysing == False:
            TDraw.DrawSpec(self)
        else:
            TDraw.DrawAnalysingSpec(self)

    def setSpecWindow(self):
        self.specWindow = float(self.ui.lineEdit_specWindow.text())
        TSolve.Solve(self)

    def selectImage(self, item):
        if self.isAnalysing == False:
            self.imageFileName = os.path.join(self.imagePath, item.text())
            TSolve.Solve(self)
        else:
            list = self.ui.listWidget.selectedItems()
            self.analysingFileList = []
            for item in list:
                self.analysingFileList.append(os.path.join(self.imagePath, item.text()))
            TSolve.Solve(self)

    def modeSwitch(self):
        button = self.sender()
        if self.ui.radioButton_online.isChecked() and button.text() == "在线模式":
            self.mode = "online"
            observer.schedule(event_handler, self.imagePath, recursive=False)
            self.ui.listWidget.setEnabled(False)
            timeformat = "%Y%m%d-%H%M%S"
            time = datetime.datetime.now().strftime(timeformat)
            self.onlineCutoffEnergyListName = os.path.normcase(
                os.path.join(self.savePath, "在线模式截止能量汇总_" + time + ".txt"))
            with open(self.onlineCutoffEnergyListName, 'w') as f:
                f.write("开始于" + time + "的在线模式，读取到的图片截止能量如下" + '\n')
        elif self.ui.radioButton_offline.isChecked() and button.text() == "离线模式":
            self.mode = "offline"
            observer.unschedule_all()
            self.ui.listWidget.setEnabled(True)
            timeformat = "%Y%m%d-%H%M%S"
            time = datetime.datetime.now().strftime(timeformat)
            with open(self.onlineCutoffEnergyListName, 'a') as f:
                f.write("结束于" + time + '\n')

    def analyseMode(self):
        if self.ui.checkBox_analyse.isChecked():
            self.ui.radioButton_offline.setChecked(True)
            self.ui.radioButton_offline.setEnabled(False)
            self.ui.radioButton_online.setEnabled(False)
            self.ui.checkBox_autoSave.setChecked(False)
            self.ui.checkBox_autoSave.setEnabled(False)
            self.ui.pushButton_saveImage.setEnabled(False)
            self.ui.groupBox_4.setEnabled(False)
            self.ui.groupBox_5.setEnabled(False)
            self.isAnalysing = True
            self.ui.listWidget.setSelectionMode(QtWidgets.QListWidget.MultiSelection)
        else:
            self.ui.radioButton_offline.setEnabled(True)
            self.ui.radioButton_online.setEnabled(True)
            self.ui.checkBox_autoSave.setEnabled(True)
            self.ui.pushButton_saveImage.setEnabled(True)
            self.ui.groupBox_4.setEnabled(True)
            self.ui.groupBox_5.setEnabled(True)
            self.isAnalysing = False
            self.ui.listWidget.setSelectionMode(QtWidgets.QListWidget.SingleSelection)

    def showParabola(self):
        if self.ui.checkBox_parabola.isChecked():
            self.isShowParabola = True
            TDraw.DrawImage(self)
            TDraw.DrawSpec(self)
            TDraw.DrawParabola(self)
        else:
            self.isShowParabola = False
            TDraw.DrawImage(self)
            TDraw.DrawSpec(self)
        if self.zoomed == False:
            TDraw.DrawOrigin(self)

    def autoSave(self):
        if self.ui.checkBox_autoSave.isChecked():
            self.isAutoSave = True
            self.saveImage()
            self.saveSpec()
        else:
            self.isAutoSave = False

    def saveSpec(self):
        if os.path.isfile(self.imageFileName):
            if self.isAnalysing == False:
                if isinstance(self.cutoffEnergy, str):
                    specPicFileName = os.path.normcase(os.path.join(self.savePath, os.path.splitext(
                        os.path.split(self.imageFileName)[1])[0] + "_" + "NaN.png"))
                    specDataFileName = os.path.normcase(os.path.join(self.savePath, os.path.splitext(
                        os.path.split(self.imageFileName)[1])[0] + "_" + "NaN.txt"))
                else:
                    ene = np.round(self.specCursor, 2)
                    specPicFileName = os.path.normcase(os.path.join(self.savePath, os.path.splitext(
                        os.path.split(self.imageFileName)[1])[0] + "_" + str(ene) + "MeV.png"))
                    specDataFileName = os.path.normcase(os.path.join(self.savePath, os.path.splitext(
                        os.path.split(self.imageFileName)[1])[0] + "_" + str(ene) + "MeV.txt"))
                self.specFig.savefig(specPicFileName)
                np.savetxt(specDataFileName, self.specData.transpose(), delimiter='\t', newline='\n', encoding='utf-8')
            else:
                timeformat = "%Y%m%d-%H%M%S"
                time = datetime.datetime.now().strftime(timeformat)
                specPicFileName = os.path.normcase(os.path.join(self.savePath, "Analysing_" + time + ".png"))
                self.specFig.savefig(specPicFileName)

    def saveImage(self):
        if os.path.isfile(self.imageFileName):
            imagePicFileName = os.path.normcase(
                os.path.join(self.savePath, os.path.splitext(os.path.split(self.imageFileName)[1])[0] + "_color.png"))
            self.imageFig.savefig(imagePicFileName)

    def initZoom(self, event):
        self.zoomStart = [event.xdata, event.ydata]

    def zoom(self, event):
        self.zoomEnd = [event.xdata, event.ydata]
        self.ui.pushButton_zoom.setChecked(False)

        if self.zoomed == False:
            self.zoomToOrigin = [0, 0, self.imageData[1].shape[0] - 1, self.imageData[0].shape[0] - 1]

        self.zoomed = True

        self.zoomArea = np.zeros(4)
        self.zoomArea[1] = np.min([np.ceil(self.zoomStart[0]), np.ceil(self.zoomEnd[0])])
        self.zoomArea[0] = np.min([np.ceil(self.zoomStart[1]), np.ceil(self.zoomEnd[1])])
        self.zoomArea[3] = np.max([np.ceil(self.zoomStart[0]), np.ceil(self.zoomEnd[0])])
        self.zoomArea[2] = np.max([np.ceil(self.zoomStart[1]), np.ceil(self.zoomEnd[1])])
        self.zoomArea = self.zoomArea.astype(int)

        self.zoomToOrigin = [self.zoomArea[0] + self.zoomToOrigin[0], self.zoomArea[1] + self.zoomToOrigin[1],
                             self.zoomToOrigin[2] - (self.zoomPic.shape[0] - 1 - self.zoomArea[2]),
                             self.zoomToOrigin[3] - (self.zoomPic.shape[1] - 1 - self.zoomArea[3])]

        self.zoomPic = self.zoomPic[self.zoomArea[0]:self.zoomArea[2], self.zoomArea[1]:self.zoomArea[3]]
        self.zoomPara = TPSParabola.ZoomPara(self.TPSParabola, self.zoomToOrigin, self.zoomPic.shape[1])
        self.zoomImageCursor = TPSParabola.zoomCutoffLine(self.imageCursor, self.zoomToOrigin)

        TDraw.DrawImage(self)
        TDraw.DrawSpec(self)
        if self.isShowParabola:
            TDraw.DrawParabola(self)

    def closeEvent(self, event):
        self.ui.radioButton_offline.setChecked(True)
        isSaveInit = QtWidgets.QMessageBox.question(self, "退出程序", "是否覆盖保存当前设置？",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                    QtWidgets.QMessageBox.Yes)
        if isSaveInit == QtWidgets.QMessageBox.Yes:
            TSave.save_ini(self)
        self.close()

    def startZoom(self):
        if self.ui.pushButton_zoom.isChecked():
            self.pressId = self.imageFig.canvas.mpl_connect('button_press_event', self.initZoom)
            self.releaseId = self.imageFig.canvas.mpl_connect('button_release_event', self.zoom)
        else:
            self.imageFig.canvas.mpl_disconnect(self.pressId)
            self.imageFig.canvas.mpl_disconnect(self.releaseId)

    def stopZoom(self):
        self.zoomed = False
        self.zoomPic = self.imageData
        TDraw.DrawImage(self)
        TDraw.DrawOrigin(self)
        if self.isShowParabola:
            TDraw.DrawParabola(self)

    def setSpecCursor(self, event):
        if self.isAnalysing == False:
            self.specCursor = event.xdata
            self.imageCursor = TPSParabola.CutoffLine(self.TPS, self.specCursor, self.X0, self.A, self.Z)
            if self.zoomed == True:
                self.zoomImageCursor = TPSParabola.zoomCutoffLine(self.imageCursor, self.zoomToOrigin)
            TDraw.DrawImage(self)
            TDraw.DrawOrigin(self)
            TDraw.DrawSpec(self)
            if self.isShowParabola:
                TDraw.DrawParabola(self)
        else:
            self.specCursor = event.xdata
            TDraw.DrawAnalysingSpec(self)

    def help(self):
        title = "帮助"
        text = ("自动解谱功能的设置：\n“解谱设置-±dY”对应解谱时考虑的谱线范围，对于信号较弱的图片（尤其是8位图），可以考虑调大这个值。 \
        \n“自动解谱窗口”是指自动寻找截止能量时，有多大范围的能谱始终高于本底，就确定此处为截止能量。能谱线的噪声较大时，可以考虑调大这个值。")
        helpWindow = QtWidgets.QMessageBox.about(self, title, text)

    def about(self):
        title = "关于"
        text = ("PyTPS 汤姆逊谱仪全自动解谱程序 v2.1\n作者：张予嘉\n本程序改进自MATTPS V3.0\n特别感谢：MATTPS作者：徐诗睿师兄\n2022.11.8 \
        \n\nv2.1更新：\n保存：新增了保存能谱线原始数据的功能 \
        \n\nv2.0更新：\n自动寻找截止能量：全面重制的自动截止能量功能！直接基于对本底的对比寻找截止能量，更加稳定更加准确\n解谱：优化了对于8位图的去噪算法，使得弱信号更容易被分辨出来\n在线模式：修复了监视进程容易崩溃的bug \
        \n\nv1.1更新：\n自动解谱：优化了对于8位图的自动截止能量处理\n新功能：在线模式下可以自动触发Andor相机")
        aboutWindow = QtWidgets.QMessageBox.about(self, title, text)

    # 滤波功能相关方法（新增）

    def createFilterUI(self):
        """动态创建滤波设置UI（简化版：形态学阈值分割）"""
        # 创建滤波设置GroupBox
        self.groupBox_filter = QtWidgets.QGroupBox(self.ui.groupBox_2)
        self.groupBox_filter.setObjectName("groupBox_filter")
        self.groupBox_filter.setTitle("图像滤波设置")

        # 创建垂直布局
        self.verticalLayout_filter = QtWidgets.QVBoxLayout(self.groupBox_filter)

        # 滤波模式选择（简化：只有两种模式）
        self.horizontalLayout_filterMode = QtWidgets.QHBoxLayout()
        self.label_filterMode = QtWidgets.QLabel(self.groupBox_filter)
        self.label_filterMode.setText("滤波模式：")
        self.comboBox_filterMode = QtWidgets.QComboBox(self.groupBox_filter)
        self.comboBox_filterMode.addItems(["无滤波", "形态学分割"])
        # 根据配置设置初始值
        if self.filterMode == "none":
            self.comboBox_filterMode.setCurrentIndex(0)
        else:
            # 所有其他模式统一为"形态学分割"
            self.comboBox_filterMode.setCurrentIndex(1)
            self.filterMode = "protected"  # 统一设置为protected
        self.horizontalLayout_filterMode.addWidget(self.label_filterMode)
        self.horizontalLayout_filterMode.addWidget(self.comboBox_filterMode)
        self.verticalLayout_filter.addLayout(self.horizontalLayout_filterMode)

        # === 形态学分割参数区域 ===

        # 轨迹坐标背景减除按钮（更名为多轨迹软掩膜）
        self.pushButton_trajectoryBgSubtract = QtWidgets.QPushButton(self.groupBox_filter)
        self.pushButton_trajectoryBgSubtract.setText("多轨迹软掩膜滤波")
        self.pushButton_trajectoryBgSubtract.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; }")
        self.verticalLayout_filter.addWidget(self.pushButton_trajectoryBgSubtract)

        # 轨迹保护宽度（新增）
        self.horizontalLayout_protectionWidth = QtWidgets.QHBoxLayout()
        self.label_protectionWidth = QtWidgets.QLabel(self.groupBox_filter)
        self.label_protectionWidth.setText("轨迹保护宽度：")
        self.lineEdit_protectionWidth = QtWidgets.QLineEdit(self.groupBox_filter)
        self.lineEdit_protectionWidth.setText(str(self.protectionWidth))
        self.lineEdit_protectionWidth.setValidator(QtGui.QIntValidator(0, 30))
        self.lineEdit_protectionWidth.setMaximumWidth(80)
        self.label_protectionWidthUnit = QtWidgets.QLabel(self.groupBox_filter)
        self.label_protectionWidthUnit.setText("像素（从轨迹中心线向上下各保护N像素）")
        self.label_protectionWidthUnit.setStyleSheet("color: #666; font-size: 9pt;")
        self.horizontalLayout_protectionWidth.addWidget(self.label_protectionWidth)
        self.horizontalLayout_protectionWidth.addWidget(self.lineEdit_protectionWidth)
        self.horizontalLayout_protectionWidth.addWidget(self.label_protectionWidthUnit)
        self.horizontalLayout_protectionWidth.addStretch()
        self.verticalLayout_filter.addLayout(self.horizontalLayout_protectionWidth)

        # 羽化半径（原"条带半宽"）
        self.horizontalLayout_fadeRadius = QtWidgets.QHBoxLayout()
        self.label_fadeRadius = QtWidgets.QLabel(self.groupBox_filter)
        self.label_fadeRadius.setText("羽化半径：")
        self.lineEdit_fadeRadius = QtWidgets.QLineEdit(self.groupBox_filter)
        self.lineEdit_fadeRadius.setText(str(getattr(self, 'fadeRadius', 20)))
        self.lineEdit_fadeRadius.setValidator(QtGui.QIntValidator(0, 50))
        self.lineEdit_fadeRadius.setMaximumWidth(80)
        self.label_fadeRadiusUnit = QtWidgets.QLabel(self.groupBox_filter)
        self.label_fadeRadiusUnit.setText("像素（从保护边缘往外柔和过渡距离）")
        self.label_fadeRadiusUnit.setStyleSheet("color: #666; font-size: 9pt;")
        self.horizontalLayout_fadeRadius.addWidget(self.label_fadeRadius)
        self.horizontalLayout_fadeRadius.addWidget(self.lineEdit_fadeRadius)
        self.horizontalLayout_fadeRadius.addWidget(self.label_fadeRadiusUnit)
        self.horizontalLayout_fadeRadius.addStretch()
        self.verticalLayout_filter.addLayout(self.horizontalLayout_fadeRadius)

        # 说明文字（更新）
        self.label_hint = QtWidgets.QLabel(self.groupBox_filter)
        self.label_hint.setText("总影响范围计算：\n·轨迹保护宽度N：从中心线向上下各N像素（总宽度=2N+1）\n·羽化半径R：从保护边缘往外再过渡R像素\n·总影响范围 = 2N+1 + 2R 像素\n·例：保护宽度5 + 羽化半径20 = 轨迹宽11px + 上下各20px羽化 = 总共51px")
        self.label_hint.setStyleSheet("color: #0066cc; font-size: 9pt; padding: 5px; border-left: 3px solid #0066cc; background-color: #f0f8ff;")
        self.label_hint.setWordWrap(True)
        self.verticalLayout_filter.addWidget(self.label_hint)

        # 将滤波GroupBox添加到主布局
        self.ui.verticalLayout_3.addWidget(self.groupBox_filter)

        # 绑定信号
        self.comboBox_filterMode.currentIndexChanged.connect(self.setFilterMode)
        self.pushButton_trajectoryBgSubtract.clicked.connect(self.trajectoryBackgroundSubtraction)
        self.lineEdit_protectionWidth.editingFinished.connect(self.setProtectionWidth)
        self.lineEdit_fadeRadius.editingFinished.connect(self.setFadeRadius)

        # 初始化UI状态
        self.updateFilterUIState()

    def updateFilterUIState(self):
        """根据当前滤波模式更新UI状态"""
        if self.filterMode == "none":
            self.pushButton_trajectoryBgSubtract.setEnabled(False)
            self.lineEdit_protectionWidth.setEnabled(False)
            self.lineEdit_fadeRadius.setEnabled(False)
            # self.lineEdit_rollingBall 始终禁用
        else:  # protected模式
            self.pushButton_trajectoryBgSubtract.setEnabled(True)
            self.lineEdit_protectionWidth.setEnabled(True)
            self.lineEdit_fadeRadius.setEnabled(True)
            # self.lineEdit_rollingBall 始终禁用

    def setProtectionWidth(self):
        """设置轨迹保护宽度"""
        try:
            width = int(self.lineEdit_protectionWidth.text())
            width = max(0, min(30, width))  # 允许设为0
            self.protectionWidth = width
            self.lineEdit_protectionWidth.setText(str(width))
            print(f"[PyTPS] 设置轨迹保护宽度：{width} 像素（从轨迹中心线向上下各保护{width}像素）")
        except ValueError:
            self.lineEdit_protectionWidth.setText(str(self.protectionWidth))

    def setFadeRadius(self):
        """设置羽化半径"""
        try:
            radius = int(self.lineEdit_fadeRadius.text())
            radius = max(0, min(50, radius))  # 允许设为0
            self.fadeRadius = radius
            self.lineEdit_fadeRadius.setText(str(radius))
            print(f"[PyTPS] 设置羽化半径：{radius} 像素")
        except ValueError:
            self.lineEdit_fadeRadius.setText(str(getattr(self, 'fadeRadius', 20)))

    def trajectoryBackgroundSubtraction(self):
        """多轨迹软掩膜滤波：保护所有粒子+原点，软边界羽化"""
        print("[PyTPS] 点击多轨迹软掩膜滤波")

        # 直接读取当前图像
        if self.imageFileName == "." or not os.path.isfile(self.imageFileName):
            print("[PyTPS] 错误：没有加载图像")
            return

        import TImageRead, TFilter
        img, _ = TImageRead.readImage(self.imageFileName)
        img = img.astype(np.float64)

        # 调用新的多轨迹软掩膜滤波函数
        # 保护所有常见粒子（H-1, C-4/5/6, O-6/7/8）+ 原点
        print(f"[PyTPS] 开始多轨迹软掩膜滤波：保护H/C/O所有轨迹+原点")

        fadeRadius = getattr(self, 'fadeRadius', 20)  # 羽化半径
        protectionWidth = self.protectionWidth  # 轨迹保护宽度

        img_cleaned = TFilter.softMaskMultiTrajectory(
            img,
            X0=self.X0,
            Y0=self.Y0,
            Emin=self.Emin,
            Emax=self.Emax,
            dY=self.dY,
            TPS=self.TPS,
            protection_width=protectionWidth,
            fade_radius=fadeRadius,
            rolling_ball_radius=40  # 保留参数兼容性，但不使用
        )

        # 更新显示并重新计算能谱
        self.imageData = np.flipud(img_cleaned)
        self.zoomPic = self.imageData

        # 重新解谱
        import SolveSpectrum, TPSParabola
        self.specData, self.noiseSpec = SolveSpectrum.SolveSpectrum(
            self.imageData, self.X0, self.Y0, self.A, self.Z,
            self.Emin, self.Emax, self.dY, self.MCPPath, self.TPS,
            self.is8bitImage
        )
        self.TPSParabola = TPSParabola.Parabola(
            self.TPS, self.specData[0], self.X0, self.Y0,
            self.A, self.Z, self.imageData.shape[1]
        )

        TDraw.DrawImage(self)
        TDraw.DrawSpec(self)
        if self.isShowParabola:
            TDraw.DrawParabola(self)
        TDraw.DrawOrigin(self)

        print(f"[PyTPS] 多轨迹软掩膜滤波完成，已更新能谱")

    def setFilterMode(self, index):
        """设置滤波模式（简化版）"""
        if index == 0:
            self.filterMode = "none"
        elif index == 1:
            self.filterMode = "protected"  # 形态学分割
        self.updateFilterUIState()
        # 自动应用滤波
        print(f"滤波模式切换为: {self.filterMode}")
        if self.imageFileName != "." and os.path.isfile(self.imageFileName):
            TSolve.Solve(self)

    def createCompareButton(self):
        """创建谱线对比按钮"""
        # 在帮助按钮旁边添加一个对比按钮
        # 找到帮助按钮所在的布局
        # 根据UI文件，帮助和关于按钮应该在某个水平布局中
        # 我们可以在verticalLayout_3中添加一个新的按钮

        self.pushButton_compare = QtWidgets.QPushButton(self.ui.groupBox_2)
        self.pushButton_compare.setText("质子谱线对比")
        self.pushButton_compare.setObjectName("pushButton_compare")
        self.pushButton_compare.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 5px; }")

        # 将按钮添加到verticalLayout_3的底部
        self.ui.verticalLayout_3.addWidget(self.pushButton_compare)

        # 绑定信号
        self.pushButton_compare.clicked.connect(self.openCompareWindow)

    def openCompareWindow(self):
        """打开谱线对比窗口"""
        if self.compareWindow is None:
            self.compareWindow = TCompare.CompareWindow(self)
            self.compareWindow.setParentApp(self)

        # 更新文件列表
        import os
        fileList = []
        if os.path.exists(self.imagePath):
            allFiles = os.listdir(self.imagePath)
            for f in allFiles:
                if f.endswith(".tif") or f.endswith(".tiff") or f.endswith(".jpg") or f.endswith(".png") or f.endswith(".raw"):
                    fileList.append(f)

        self.compareWindow.updateFileList(fileList)
        self.compareWindow.show()
        self.compareWindow.raise_()
        self.compareWindow.activateWindow()

        print("[PyTPS] 已打开谱线对比窗口")

    def applyFilterAndResolve(self):
        """应用滤波并重新解谱"""
        print(f"点击应用滤波按钮 - 当前模式: {self.filterMode}, medianSize: {self.medianSize}, radius: {self.rollingBallRadius}")
        print(f"当前图片文件: {self.imageFileName}")

        if self.imageFileName != "." and os.path.isfile(self.imageFileName):
            print("开始重新解谱...")
            TSolve.Solve(self)
            print("解谱完成")
        else:
            print("警告：未选择图片")
            QtWidgets.QMessageBox.warning(self, "警告", "请先选择一张图片！")


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    mainwindow = MainWindow()

    event_handler = TWatchDog.MyHandler(mainwindow)
    observer = Observer()
    observer.start()

    mainwindow.show()
    sys.exit(app.exec())
