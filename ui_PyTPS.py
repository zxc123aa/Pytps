# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PyTPS.ui'
##
## Created by: Qt User Interface Compiler version 6.3.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLayout, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1280, 720)
        MainWindow.setMinimumSize(QSize(0, 0))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_8 = QGridLayout(self.centralwidget)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_4)

        self.label_title = QLabel(self.centralwidget)
        self.label_title.setObjectName(u"label_title")

        self.horizontalLayout_10.addWidget(self.label_title)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_2)

        self.radioButton_online = QRadioButton(self.centralwidget)
        self.radioButton_online.setObjectName(u"radioButton_online")

        self.horizontalLayout_10.addWidget(self.radioButton_online)

        self.radioButton_offline = QRadioButton(self.centralwidget)
        self.radioButton_offline.setObjectName(u"radioButton_offline")
        self.radioButton_offline.setChecked(True)

        self.horizontalLayout_10.addWidget(self.radioButton_offline)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_5)

        self.checkBox_analyse = QCheckBox(self.centralwidget)
        self.checkBox_analyse.setObjectName(u"checkBox_analyse")

        self.horizontalLayout_10.addWidget(self.checkBox_analyse)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_3)

        self.pushButton_help = QPushButton(self.centralwidget)
        self.pushButton_help.setObjectName(u"pushButton_help")

        self.horizontalLayout_10.addWidget(self.pushButton_help)

        self.pushButton_about = QPushButton(self.centralwidget)
        self.pushButton_about.setObjectName(u"pushButton_about")

        self.horizontalLayout_10.addWidget(self.pushButton_about)


        self.gridLayout_8.addLayout(self.horizontalLayout_10, 0, 0, 1, 3)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMaximumSize(QSize(300, 16777215))
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(2)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)
        self.label_2.setMinimumSize(QSize(80, 24))

        self.horizontalLayout.addWidget(self.label_2)

        self.lineEdit_imagePath = QLineEdit(self.groupBox)
        self.lineEdit_imagePath.setObjectName(u"lineEdit_imagePath")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(10)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.lineEdit_imagePath.sizePolicy().hasHeightForWidth())
        self.lineEdit_imagePath.setSizePolicy(sizePolicy2)
        self.lineEdit_imagePath.setMinimumSize(QSize(0, 0))
        self.lineEdit_imagePath.setReadOnly(True)

        self.horizontalLayout.addWidget(self.lineEdit_imagePath)

        self.pushButton_browseImagePath = QPushButton(self.groupBox)
        self.pushButton_browseImagePath.setObjectName(u"pushButton_browseImagePath")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(2)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.pushButton_browseImagePath.sizePolicy().hasHeightForWidth())
        self.pushButton_browseImagePath.setSizePolicy(sizePolicy3)
        self.pushButton_browseImagePath.setMaximumSize(QSize(50, 50))

        self.horizontalLayout.addWidget(self.pushButton_browseImagePath)

        self.pushButton_refreshImagePath = QPushButton(self.groupBox)
        self.pushButton_refreshImagePath.setObjectName(u"pushButton_refreshImagePath")
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(1)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.pushButton_refreshImagePath.sizePolicy().hasHeightForWidth())
        self.pushButton_refreshImagePath.setSizePolicy(sizePolicy4)
        self.pushButton_refreshImagePath.setMaximumSize(QSize(40, 50))

        self.horizontalLayout.addWidget(self.pushButton_refreshImagePath)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.listWidget = QListWidget(self.groupBox)
        self.listWidget.setObjectName(u"listWidget")
        self.listWidget.setEnabled(True)
        self.listWidget.setMaximumSize(QSize(16777215, 16777215))
        self.listWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.verticalLayout.addWidget(self.listWidget)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.groupBox_2 = QGroupBox(self.groupBox)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_2.addWidget(self.label_3)

        self.pushButton_openTPS = QPushButton(self.groupBox_2)
        self.pushButton_openTPS.setObjectName(u"pushButton_openTPS")

        self.horizontalLayout_2.addWidget(self.pushButton_openTPS)

        self.pushButton_refreshTPS = QPushButton(self.groupBox_2)
        self.pushButton_refreshTPS.setObjectName(u"pushButton_refreshTPS")

        self.horizontalLayout_2.addWidget(self.pushButton_refreshTPS)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_3.addWidget(self.label_4)

        self.lineEdit_MCPPath = QLineEdit(self.groupBox_2)
        self.lineEdit_MCPPath.setObjectName(u"lineEdit_MCPPath")
        self.lineEdit_MCPPath.setReadOnly(True)

        self.horizontalLayout_3.addWidget(self.lineEdit_MCPPath)

        self.pushButton_browseMCPPath = QPushButton(self.groupBox_2)
        self.pushButton_browseMCPPath.setObjectName(u"pushButton_browseMCPPath")

        self.horizontalLayout_3.addWidget(self.pushButton_browseMCPPath)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.groupBox_3 = QGroupBox(self.groupBox_2)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_5 = QLabel(self.groupBox_3)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_4.addWidget(self.label_5)

        self.comboBox_particals = QComboBox(self.groupBox_3)
        self.comboBox_particals.setObjectName(u"comboBox_particals")

        self.horizontalLayout_4.addWidget(self.comboBox_particals)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_6 = QLabel(self.groupBox_3)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_5.addWidget(self.label_6)

        self.lineEdit_A = QLineEdit(self.groupBox_3)
        self.lineEdit_A.setObjectName(u"lineEdit_A")

        self.horizontalLayout_5.addWidget(self.lineEdit_A)

        self.label_7 = QLabel(self.groupBox_3)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_5.addWidget(self.label_7)

        self.lineEdit_Z = QLineEdit(self.groupBox_3)
        self.lineEdit_Z.setObjectName(u"lineEdit_Z")

        self.horizontalLayout_5.addWidget(self.lineEdit_Z)


        self.verticalLayout_2.addLayout(self.horizontalLayout_5)


        self.verticalLayout_3.addWidget(self.groupBox_3)


        self.gridLayout.addWidget(self.groupBox_2, 2, 0, 1, 1)


        self.verticalLayout_6.addWidget(self.groupBox)


        self.gridLayout_8.addLayout(self.verticalLayout_6, 1, 0, 1, 1)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.groupBox_4 = QGroupBox(self.centralwidget)
        self.groupBox_4.setObjectName(u"groupBox_4")
        sizePolicy5 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy5.setHorizontalStretch(2)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy5)
        self.groupBox_4.setMinimumSize(QSize(0, 0))
        self.gridLayout_image = QGridLayout(self.groupBox_4)
        self.gridLayout_image.setObjectName(u"gridLayout_image")

        self.verticalLayout_7.addWidget(self.groupBox_4)

        self.groupBox_5 = QGroupBox(self.centralwidget)
        self.groupBox_5.setObjectName(u"groupBox_5")
        sizePolicy.setHeightForWidth(self.groupBox_5.sizePolicy().hasHeightForWidth())
        self.groupBox_5.setSizePolicy(sizePolicy)
        self.horizontalLayout_6 = QHBoxLayout(self.groupBox_5)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_8 = QLabel(self.groupBox_5)
        self.label_8.setObjectName(u"label_8")
        sizePolicy6 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy6.setHorizontalStretch(1)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy6)

        self.gridLayout_2.addWidget(self.label_8, 0, 0, 1, 1)

        self.label_9 = QLabel(self.groupBox_5)
        self.label_9.setObjectName(u"label_9")
        sizePolicy6.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy6)

        self.gridLayout_2.addWidget(self.label_9, 1, 0, 1, 1)

        self.label_10 = QLabel(self.groupBox_5)
        self.label_10.setObjectName(u"label_10")
        sizePolicy6.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy6)

        self.gridLayout_2.addWidget(self.label_10, 2, 0, 1, 1)

        self.lineEdit_dY = QLineEdit(self.groupBox_5)
        self.lineEdit_dY.setObjectName(u"lineEdit_dY")
        sizePolicy3.setHeightForWidth(self.lineEdit_dY.sizePolicy().hasHeightForWidth())
        self.lineEdit_dY.setSizePolicy(sizePolicy3)

        self.gridLayout_2.addWidget(self.lineEdit_dY, 2, 1, 1, 3)

        self.label_11 = QLabel(self.groupBox_5)
        self.label_11.setObjectName(u"label_11")
        sizePolicy6.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy6)
        self.label_11.setMinimumSize(QSize(0, 0))

        self.gridLayout_2.addWidget(self.label_11, 3, 0, 1, 1)

        self.lineEdit_Emin = QLineEdit(self.groupBox_5)
        self.lineEdit_Emin.setObjectName(u"lineEdit_Emin")
        sizePolicy3.setHeightForWidth(self.lineEdit_Emin.sizePolicy().hasHeightForWidth())
        self.lineEdit_Emin.setSizePolicy(sizePolicy3)

        self.gridLayout_2.addWidget(self.lineEdit_Emin, 3, 1, 1, 3)

        self.label_12 = QLabel(self.groupBox_5)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_2.addWidget(self.label_12, 4, 0, 1, 1)

        self.lineEdit_Emax = QLineEdit(self.groupBox_5)
        self.lineEdit_Emax.setObjectName(u"lineEdit_Emax")
        sizePolicy3.setHeightForWidth(self.lineEdit_Emax.sizePolicy().hasHeightForWidth())
        self.lineEdit_Emax.setSizePolicy(sizePolicy3)

        self.gridLayout_2.addWidget(self.lineEdit_Emax, 4, 1, 1, 3)

        self.lineEdit_X0 = QLineEdit(self.groupBox_5)
        self.lineEdit_X0.setObjectName(u"lineEdit_X0")
        sizePolicy3.setHeightForWidth(self.lineEdit_X0.sizePolicy().hasHeightForWidth())
        self.lineEdit_X0.setSizePolicy(sizePolicy3)

        self.gridLayout_2.addWidget(self.lineEdit_X0, 0, 1, 1, 3)

        self.lineEdit_Y0 = QLineEdit(self.groupBox_5)
        self.lineEdit_Y0.setObjectName(u"lineEdit_Y0")
        sizePolicy3.setHeightForWidth(self.lineEdit_Y0.sizePolicy().hasHeightForWidth())
        self.lineEdit_Y0.setSizePolicy(sizePolicy3)

        self.gridLayout_2.addWidget(self.lineEdit_Y0, 1, 1, 1, 3)


        self.horizontalLayout_6.addLayout(self.gridLayout_2)

        self.line = QFrame(self.groupBox_5)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_6.addWidget(self.line)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.pushButton_zoom = QPushButton(self.groupBox_5)
        self.pushButton_zoom.setObjectName(u"pushButton_zoom")
        self.pushButton_zoom.setCheckable(True)

        self.verticalLayout_4.addWidget(self.pushButton_zoom)

        self.pushButton_origin = QPushButton(self.groupBox_5)
        self.pushButton_origin.setObjectName(u"pushButton_origin")

        self.verticalLayout_4.addWidget(self.pushButton_origin)

        self.checkBox_parabola = QCheckBox(self.groupBox_5)
        self.checkBox_parabola.setObjectName(u"checkBox_parabola")

        self.verticalLayout_4.addWidget(self.checkBox_parabola)


        self.horizontalLayout_6.addLayout(self.verticalLayout_4)

        self.groupBox_6 = QGroupBox(self.groupBox_5)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.gridLayout_3 = QGridLayout(self.groupBox_6)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_13 = QLabel(self.groupBox_6)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_3.addWidget(self.label_13, 0, 0, 1, 1)

        self.comboBox_colormap = QComboBox(self.groupBox_6)
        self.comboBox_colormap.setObjectName(u"comboBox_colormap")

        self.gridLayout_3.addWidget(self.comboBox_colormap, 0, 1, 1, 1)

        self.label_14 = QLabel(self.groupBox_6)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout_3.addWidget(self.label_14, 1, 0, 1, 1)

        self.lineEdit_colormin = QLineEdit(self.groupBox_6)
        self.lineEdit_colormin.setObjectName(u"lineEdit_colormin")

        self.gridLayout_3.addWidget(self.lineEdit_colormin, 1, 1, 1, 1)

        self.label_15 = QLabel(self.groupBox_6)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_3.addWidget(self.label_15, 2, 0, 1, 1)

        self.lineEdit_colormax = QLineEdit(self.groupBox_6)
        self.lineEdit_colormax.setObjectName(u"lineEdit_colormax")

        self.gridLayout_3.addWidget(self.lineEdit_colormax, 2, 1, 1, 1)


        self.horizontalLayout_6.addWidget(self.groupBox_6)


        self.verticalLayout_7.addWidget(self.groupBox_5)


        self.gridLayout_8.addLayout(self.verticalLayout_7, 1, 1, 1, 1)

        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.groupBox_7 = QGroupBox(self.centralwidget)
        self.groupBox_7.setObjectName(u"groupBox_7")
        sizePolicy7 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy7.setHorizontalStretch(1)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.groupBox_7.sizePolicy().hasHeightForWidth())
        self.groupBox_7.setSizePolicy(sizePolicy7)
        self.groupBox_7.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_spec = QVBoxLayout(self.groupBox_7)
        self.verticalLayout_spec.setObjectName(u"verticalLayout_spec")
        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_16 = QLabel(self.groupBox_7)
        self.label_16.setObjectName(u"label_16")
        sizePolicy8 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.label_16.sizePolicy().hasHeightForWidth())
        self.label_16.setSizePolicy(sizePolicy8)

        self.horizontalLayout_11.addWidget(self.label_16)

        self.lineEdit_cutoff = QLineEdit(self.groupBox_7)
        self.lineEdit_cutoff.setObjectName(u"lineEdit_cutoff")
        self.lineEdit_cutoff.setEnabled(True)
        self.lineEdit_cutoff.setAlignment(Qt.AlignCenter)
        self.lineEdit_cutoff.setReadOnly(True)

        self.horizontalLayout_11.addWidget(self.lineEdit_cutoff)

        self.label_17 = QLabel(self.groupBox_7)
        self.label_17.setObjectName(u"label_17")
        sizePolicy8.setHeightForWidth(self.label_17.sizePolicy().hasHeightForWidth())
        self.label_17.setSizePolicy(sizePolicy8)

        self.horizontalLayout_11.addWidget(self.label_17)


        self.verticalLayout_spec.addLayout(self.horizontalLayout_11)


        self.verticalLayout_8.addWidget(self.groupBox_7)

        self.groupBox_8 = QGroupBox(self.centralwidget)
        self.groupBox_8.setObjectName(u"groupBox_8")
        self.horizontalLayout_8 = QHBoxLayout(self.groupBox_8)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.label_18 = QLabel(self.groupBox_8)
        self.label_18.setObjectName(u"label_18")

        self.gridLayout_6.addWidget(self.label_18, 0, 0, 1, 1)

        self.lineEdit_specEmin = QLineEdit(self.groupBox_8)
        self.lineEdit_specEmin.setObjectName(u"lineEdit_specEmin")

        self.gridLayout_6.addWidget(self.lineEdit_specEmin, 0, 1, 1, 1)

        self.label_19 = QLabel(self.groupBox_8)
        self.label_19.setObjectName(u"label_19")

        self.gridLayout_6.addWidget(self.label_19, 1, 0, 1, 1)

        self.lineEdit_specEmax = QLineEdit(self.groupBox_8)
        self.lineEdit_specEmax.setObjectName(u"lineEdit_specEmax")

        self.gridLayout_6.addWidget(self.lineEdit_specEmax, 1, 1, 1, 1)

        self.label_20 = QLabel(self.groupBox_8)
        self.label_20.setObjectName(u"label_20")

        self.gridLayout_6.addWidget(self.label_20, 2, 0, 1, 1)

        self.lineEdit_specdNdEmin = QLineEdit(self.groupBox_8)
        self.lineEdit_specdNdEmin.setObjectName(u"lineEdit_specdNdEmin")

        self.gridLayout_6.addWidget(self.lineEdit_specdNdEmin, 2, 1, 1, 1)

        self.label_21 = QLabel(self.groupBox_8)
        self.label_21.setObjectName(u"label_21")

        self.gridLayout_6.addWidget(self.label_21, 3, 0, 1, 1)

        self.lineEdit_specdNdEmax = QLineEdit(self.groupBox_8)
        self.lineEdit_specdNdEmax.setObjectName(u"lineEdit_specdNdEmax")

        self.gridLayout_6.addWidget(self.lineEdit_specdNdEmax, 3, 1, 1, 1)


        self.horizontalLayout_8.addLayout(self.gridLayout_6)

        self.line_2 = QFrame(self.groupBox_8)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.VLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_8.addWidget(self.line_2)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.label = QLabel(self.groupBox_8)
        self.label.setObjectName(u"label")

        self.horizontalLayout_12.addWidget(self.label)

        self.lineEdit_specWindow = QLineEdit(self.groupBox_8)
        self.lineEdit_specWindow.setObjectName(u"lineEdit_specWindow")
        sizePolicy9 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy9.setHorizontalStretch(0)
        sizePolicy9.setVerticalStretch(0)
        sizePolicy9.setHeightForWidth(self.lineEdit_specWindow.sizePolicy().hasHeightForWidth())
        self.lineEdit_specWindow.setSizePolicy(sizePolicy9)

        self.horizontalLayout_12.addWidget(self.lineEdit_specWindow)

        self.label_25 = QLabel(self.groupBox_8)
        self.label_25.setObjectName(u"label_25")

        self.horizontalLayout_12.addWidget(self.label_25)


        self.verticalLayout_5.addLayout(self.horizontalLayout_12)

        self.label_22 = QLabel(self.groupBox_8)
        self.label_22.setObjectName(u"label_22")

        self.verticalLayout_5.addWidget(self.label_22)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.lineEdit_cursor = QLineEdit(self.groupBox_8)
        self.lineEdit_cursor.setObjectName(u"lineEdit_cursor")
        self.lineEdit_cursor.setReadOnly(True)

        self.horizontalLayout_7.addWidget(self.lineEdit_cursor)

        self.label_23 = QLabel(self.groupBox_8)
        self.label_23.setObjectName(u"label_23")

        self.horizontalLayout_7.addWidget(self.label_23)


        self.verticalLayout_5.addLayout(self.horizontalLayout_7)


        self.horizontalLayout_8.addLayout(self.verticalLayout_5)


        self.verticalLayout_8.addWidget(self.groupBox_8)

        self.groupBox_9 = QGroupBox(self.centralwidget)
        self.groupBox_9.setObjectName(u"groupBox_9")
        self.gridLayout_7 = QGridLayout(self.groupBox_9)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.pushButton_saveImage = QPushButton(self.groupBox_9)
        self.pushButton_saveImage.setObjectName(u"pushButton_saveImage")

        self.gridLayout_7.addWidget(self.pushButton_saveImage, 1, 3, 1, 1)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_24 = QLabel(self.groupBox_9)
        self.label_24.setObjectName(u"label_24")

        self.horizontalLayout_9.addWidget(self.label_24)

        self.lineEdit_savePath = QLineEdit(self.groupBox_9)
        self.lineEdit_savePath.setObjectName(u"lineEdit_savePath")
        self.lineEdit_savePath.setReadOnly(True)

        self.horizontalLayout_9.addWidget(self.lineEdit_savePath)

        self.pushButton_browseSavePath = QPushButton(self.groupBox_9)
        self.pushButton_browseSavePath.setObjectName(u"pushButton_browseSavePath")

        self.horizontalLayout_9.addWidget(self.pushButton_browseSavePath)


        self.gridLayout_7.addLayout(self.horizontalLayout_9, 0, 2, 1, 4)

        self.horizontalSpacer = QSpacerItem(129, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer, 1, 4, 1, 1)

        self.checkBox_autoSave = QCheckBox(self.groupBox_9)
        self.checkBox_autoSave.setObjectName(u"checkBox_autoSave")

        self.gridLayout_7.addWidget(self.checkBox_autoSave, 1, 5, 1, 1)

        self.pushButton_saveSpec = QPushButton(self.groupBox_9)
        self.pushButton_saveSpec.setObjectName(u"pushButton_saveSpec")

        self.gridLayout_7.addWidget(self.pushButton_saveSpec, 1, 2, 1, 1)


        self.verticalLayout_8.addWidget(self.groupBox_9)


        self.gridLayout_8.addLayout(self.verticalLayout_8, 1, 2, 1, 1)

        self.gridLayout_8.setColumnStretch(0, 1)
        self.gridLayout_8.setColumnStretch(1, 6)
        self.gridLayout_8.setColumnStretch(2, 5)
        self.gridLayout_8.setColumnMinimumWidth(0, 300)
        self.gridLayout_8.setColumnMinimumWidth(1, 256)
        self.gridLayout_8.setColumnMinimumWidth(2, 300)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"PyTPS", None))
        self.label_title.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:26pt; font-weight:700;\">PyTPS \u6c64\u59c6\u900a\u8c31\u4eea\u5168\u81ea\u52a8\u89e3\u8c31\u7a0b\u5e8f</span></p></body></html>", None))
        self.radioButton_online.setText(QCoreApplication.translate("MainWindow", u"\u5728\u7ebf\u6a21\u5f0f", None))
        self.radioButton_offline.setText(QCoreApplication.translate("MainWindow", u"\u79bb\u7ebf\u6a21\u5f0f", None))
        self.checkBox_analyse.setText(QCoreApplication.translate("MainWindow", u"\u80fd\u8c31\u5206\u6790\u6a21\u5f0f", None))
        self.pushButton_help.setText(QCoreApplication.translate("MainWindow", u"\u5e2e\u52a9...", None))
        self.pushButton_about.setText(QCoreApplication.translate("MainWindow", u"\u5173\u4e8e...", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"\u8def\u5f84\u8bbe\u7f6e", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u6587\u4ef6\u8def\u5f84\uff1a", None))
        self.pushButton_browseImagePath.setText(QCoreApplication.translate("MainWindow", u"\u6d4f\u89c8...", None))
        self.pushButton_refreshImagePath.setText(QCoreApplication.translate("MainWindow", u"\u5237\u65b0", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"\u6c64\u59c6\u900a\u8c31\u4eea\u8bbe\u7f6e", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u8c31\u4eea\u53c2\u6570", None))
        self.pushButton_openTPS.setText(QCoreApplication.translate("MainWindow", u"\u6253\u5f00\u914d\u7f6e\u6587\u4ef6...", None))
        self.pushButton_refreshTPS.setText(QCoreApplication.translate("MainWindow", u"\u5237\u65b0\u914d\u7f6e\u6587\u4ef6", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"MCP\u6548\u7387\u6587\u4ef6", None))
        self.pushButton_browseMCPPath.setText(QCoreApplication.translate("MainWindow", u"\u6d4f\u89c8...", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"\u89e3\u8c31\u79bb\u5b50\u8bbe\u7f6e", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"\u79bb\u5b50\u79cd\u7c7b\uff1a", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"\u8d28\u91cf\u6570(A)", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"\u7535\u8377\u6570(Z)", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"\u56fe\u7247\u9884\u89c8", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("MainWindow", u"\u89e3\u8c31\u8bbe\u7f6e/\u56fe\u7247\u9884\u89c8\u8bbe\u7f6e", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"X0", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Y0", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"\u00b1dY", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"E min", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"E max", None))
        self.pushButton_zoom.setText(QCoreApplication.translate("MainWindow", u"\u56fe\u7247\u7f29\u653e", None))
        self.pushButton_origin.setText(QCoreApplication.translate("MainWindow", u"\u539f\u59cb\u5927\u5c0f", None))
        self.checkBox_parabola.setText(QCoreApplication.translate("MainWindow", u"\u663e\u793a\u53c2\u8003\u629b\u7269\u7ebf", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("MainWindow", u"\u4f2a\u5f69\u56fe\u8bbe\u7f6e", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"\u540d\u79f0", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"\u8303\u56f4\u4e0b\u9650", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"\u8303\u56f4\u4e0a\u9650", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("MainWindow", u"\u89e3\u8c31\u7ed3\u679c", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"\u622a\u6b62\u80fd\u91cf(\u4ec5\u4f9b\u53c2\u8003)\uff1a", None))
        self.lineEdit_cutoff.setText("")
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"MeV", None))
        self.groupBox_8.setTitle(QCoreApplication.translate("MainWindow", u"\u80fd\u8c31\u56fe\u8bbe\u7f6e", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"Emin", None))
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"Emax", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"dNdEmin", None))
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"dNdEmax", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u81ea\u52a8\u89e3\u8c31\u7a97\u53e3", None))
        self.label_25.setText(QCoreApplication.translate("MainWindow", u"MeV", None))
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"\u5149\u6807\u5904\u5bf9\u5e94\u80fd\u91cf\uff1a", None))
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"MeV", None))
        self.groupBox_9.setTitle(QCoreApplication.translate("MainWindow", u"\u80fd\u8c31\u4fdd\u5b58\u8bbe\u7f6e", None))
        self.pushButton_saveImage.setText(QCoreApplication.translate("MainWindow", u"\u4fdd\u5b58\u5f53\u524d\u56fe\u7247", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"\u4fdd\u5b58\u8def\u5f84\uff1a", None))
        self.pushButton_browseSavePath.setText(QCoreApplication.translate("MainWindow", u"\u6d4f\u89c8...", None))
        self.checkBox_autoSave.setText(QCoreApplication.translate("MainWindow", u"\u81ea\u52a8\u4fdd\u5b58", None))
        self.pushButton_saveSpec.setText(QCoreApplication.translate("MainWindow", u"\u4fdd\u5b58\u5f53\u524d\u80fd\u8c31", None))
    # retranslateUi

