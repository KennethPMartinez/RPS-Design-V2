# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Graficas_Window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
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
from PySide6.QtWidgets import (QApplication, QDial, QDoubleSpinBox, QGraphicsView,
    QGridLayout, QGroupBox, QHeaderView, QLabel,
    QMainWindow, QMenuBar, QSizePolicy, QSpacerItem,
    QStatusBar, QTableWidget, QTableWidgetItem, QWidget)

class Ui_Graficas_Window(object):
    def setupUi(self, Graficas_Window):
        if not Graficas_Window.objectName():
            Graficas_Window.setObjectName(u"Graficas_Window")
        Graficas_Window.resize(1034, 0)
        self.centralwidget = QWidget(Graficas_Window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 0, 2, 1, 1)

        self.groupBox_5 = QGroupBox(self.centralwidget)
        self.groupBox_5.setObjectName(u"groupBox_5")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_5.sizePolicy().hasHeightForWidth())
        self.groupBox_5.setSizePolicy(sizePolicy)
        self.groupBox_5.setMinimumSize(QSize(0, 0))
        self.groupBox_5.setMaximumSize(QSize(290, 16777215))
        self.gridLayout_9 = QGridLayout(self.groupBox_5)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.label_5 = QLabel(self.groupBox_5)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy1)
        self.label_5.setMinimumSize(QSize(0, 30))
        font = QFont()
        font.setFamilies([u"Bahnschrift"])
        font.setPointSize(12)
        self.label_5.setFont(font)
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_9.addWidget(self.label_5, 0, 1, 1, 2)

        self.doubleSpinBox_posicion_theta = QDoubleSpinBox(self.groupBox_5)
        self.doubleSpinBox_posicion_theta.setObjectName(u"doubleSpinBox_posicion_theta")
        self.doubleSpinBox_posicion_theta.setEnabled(True)
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.doubleSpinBox_posicion_theta.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_posicion_theta.setSizePolicy(sizePolicy2)
        self.doubleSpinBox_posicion_theta.setMinimumSize(QSize(0, 40))
        self.doubleSpinBox_posicion_theta.setMaximumSize(QSize(16777215, 35))
        self.doubleSpinBox_posicion_theta.setDecimals(6)
        self.doubleSpinBox_posicion_theta.setMaximum(360.000000000000000)
        self.doubleSpinBox_posicion_theta.setSingleStep(0.500000000000000)

        self.gridLayout_9.addWidget(self.doubleSpinBox_posicion_theta, 1, 1, 1, 2)

        self.dial_posicion_theta = QDial(self.groupBox_5)
        self.dial_posicion_theta.setObjectName(u"dial_posicion_theta")
        self.dial_posicion_theta.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.dial_posicion_theta.sizePolicy().hasHeightForWidth())
        self.dial_posicion_theta.setSizePolicy(sizePolicy1)
        self.dial_posicion_theta.setMinimumSize(QSize(225, 225))
        self.dial_posicion_theta.setMinimum(90)
        self.dial_posicion_theta.setMaximum(450)
        self.dial_posicion_theta.setValue(90)
        self.dial_posicion_theta.setTracking(True)
        self.dial_posicion_theta.setOrientation(Qt.Orientation.Horizontal)
        self.dial_posicion_theta.setInvertedAppearance(True)
        self.dial_posicion_theta.setInvertedControls(False)
        self.dial_posicion_theta.setWrapping(True)
        self.dial_posicion_theta.setNotchTarget(1.000000000000000)
        self.dial_posicion_theta.setNotchesVisible(True)

        self.gridLayout_9.addWidget(self.dial_posicion_theta, 4, 1, 1, 2)


        self.gridLayout.addWidget(self.groupBox_5, 1, 2, 2, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 3, 2, 1, 1)

        self.graphicsView = QGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setMinimumSize(QSize(500, 0))

        self.gridLayout.addWidget(self.graphicsView, 0, 1, 4, 1)

        self.table_coordinates = QTableWidget(self.centralwidget)
        self.table_coordinates.setObjectName(u"table_coordinates")
        self.table_coordinates.setMinimumSize(QSize(250, 0))
        self.table_coordinates.setMaximumSize(QSize(400, 16777215))

        self.gridLayout.addWidget(self.table_coordinates, 0, 0, 2, 1)

        self.table_Rodillos = QTableWidget(self.centralwidget)
        self.table_Rodillos.setObjectName(u"table_Rodillos")
        self.table_Rodillos.setMinimumSize(QSize(250, 0))
        self.table_Rodillos.setMaximumSize(QSize(400, 16777215))

        self.gridLayout.addWidget(self.table_Rodillos, 2, 0, 2, 1)

        Graficas_Window.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(Graficas_Window)
        self.statusbar.setObjectName(u"statusbar")
        Graficas_Window.setStatusBar(self.statusbar)
        self.menuBar = QMenuBar(Graficas_Window)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1034, 33))
        Graficas_Window.setMenuBar(self.menuBar)

        self.retranslateUi(Graficas_Window)

        QMetaObject.connectSlotsByName(Graficas_Window)
    # setupUi

    def retranslateUi(self, Graficas_Window):
        Graficas_Window.setWindowTitle(QCoreApplication.translate("Graficas_Window", u"Titulo_Provisional", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("Graficas_Window", u"Control Manual", None))
        self.label_5.setText(QCoreApplication.translate("Graficas_Window", u"Posici\u00f3n Angular del Pi\u00f1on \u03b8 (\u00b0)", None))
    # retranslateUi

