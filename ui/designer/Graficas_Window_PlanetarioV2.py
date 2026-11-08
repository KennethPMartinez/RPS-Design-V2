# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Graficas_Window_PlanetarioV2.ui'
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
from PySide6.QtWidgets import (QApplication, QDial, QDoubleSpinBox, QFrame,
    QGraphicsView, QGridLayout, QGroupBox, QHeaderView,
    QLabel, QMainWindow, QMenuBar, QSizePolicy,
    QSpacerItem, QStatusBar, QTableWidget, QTableWidgetItem,
    QWidget)

class Ui_Graficas_Window(object):
    def setupUi(self, Graficas_Window):
        if not Graficas_Window.objectName():
            Graficas_Window.setObjectName(u"Graficas_Window")
        Graficas_Window.resize(1308, 727)
        self.centralwidget = QWidget(Graficas_Window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line, 0, 2, 5, 1)

        self.table_coordinates_sun = QTableWidget(self.centralwidget)
        self.table_coordinates_sun.setObjectName(u"table_coordinates_sun")
        self.table_coordinates_sun.setMinimumSize(QSize(200, 0))
        self.table_coordinates_sun.setMaximumSize(QSize(250, 16777215))

        self.gridLayout.addWidget(self.table_coordinates_sun, 1, 0, 4, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 1, 6, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 4, 6, 1, 1)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setFamilies([u"Bahnschrift"])
        font.setPointSize(24)
        self.label.setFont(font)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)

        self.graphicsView_anular = QGraphicsView(self.centralwidget)
        self.graphicsView_anular.setObjectName(u"graphicsView_anular")
        self.graphicsView_anular.setMinimumSize(QSize(300, 0))
        self.graphicsView_anular.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout.addWidget(self.graphicsView_anular, 1, 4, 2, 1)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)

        self.gridLayout.addWidget(self.label_2, 0, 3, 1, 2)

        self.table_coordinates_anular = QTableWidget(self.centralwidget)
        self.table_coordinates_anular.setObjectName(u"table_coordinates_anular")
        self.table_coordinates_anular.setMinimumSize(QSize(200, 0))
        self.table_coordinates_anular.setMaximumSize(QSize(250, 16777215))

        self.gridLayout.addWidget(self.table_coordinates_anular, 1, 3, 4, 1)

        self.graphicsView_sun = QGraphicsView(self.centralwidget)
        self.graphicsView_sun.setObjectName(u"graphicsView_sun")
        self.graphicsView_sun.setMinimumSize(QSize(300, 0))
        self.graphicsView_sun.setMaximumSize(QSize(16777215, 400))

        self.gridLayout.addWidget(self.graphicsView_sun, 1, 1, 2, 1)

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
        self.doubleSpinBox_posicion_theta = QDoubleSpinBox(self.groupBox_5)
        self.doubleSpinBox_posicion_theta.setObjectName(u"doubleSpinBox_posicion_theta")
        self.doubleSpinBox_posicion_theta.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.doubleSpinBox_posicion_theta.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_posicion_theta.setSizePolicy(sizePolicy1)
        self.doubleSpinBox_posicion_theta.setMinimumSize(QSize(0, 40))
        self.doubleSpinBox_posicion_theta.setMaximumSize(QSize(16777215, 35))
        self.doubleSpinBox_posicion_theta.setDecimals(6)
        self.doubleSpinBox_posicion_theta.setMaximum(360.000000000000000)
        self.doubleSpinBox_posicion_theta.setSingleStep(0.500000000000000)

        self.gridLayout_9.addWidget(self.doubleSpinBox_posicion_theta, 1, 1, 1, 2)

        self.dial_posicion_theta = QDial(self.groupBox_5)
        self.dial_posicion_theta.setObjectName(u"dial_posicion_theta")
        self.dial_posicion_theta.setEnabled(True)
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.dial_posicion_theta.sizePolicy().hasHeightForWidth())
        self.dial_posicion_theta.setSizePolicy(sizePolicy2)
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

        self.label_5 = QLabel(self.groupBox_5)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy2)
        self.label_5.setMinimumSize(QSize(0, 30))
        font1 = QFont()
        font1.setFamilies([u"Bahnschrift"])
        font1.setPointSize(12)
        self.label_5.setFont(font1)
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_9.addWidget(self.label_5, 0, 1, 1, 2)


        self.gridLayout.addWidget(self.groupBox_5, 2, 6, 2, 1)

        self.table_Rodillos_anular = QTableWidget(self.centralwidget)
        self.table_Rodillos_anular.setObjectName(u"table_Rodillos_anular")
        self.table_Rodillos_anular.setMinimumSize(QSize(300, 0))
        self.table_Rodillos_anular.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout.addWidget(self.table_Rodillos_anular, 3, 4, 2, 1)

        self.table_Rodillos_sun = QTableWidget(self.centralwidget)
        self.table_Rodillos_sun.setObjectName(u"table_Rodillos_sun")
        self.table_Rodillos_sun.setMinimumSize(QSize(300, 0))
        self.table_Rodillos_sun.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout.addWidget(self.table_Rodillos_sun, 3, 1, 2, 1)

        self.line_2 = QFrame(self.centralwidget)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_2, 0, 5, 5, 1)

        Graficas_Window.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(Graficas_Window)
        self.statusbar.setObjectName(u"statusbar")
        Graficas_Window.setStatusBar(self.statusbar)
        self.menuBar = QMenuBar(Graficas_Window)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1308, 33))
        Graficas_Window.setMenuBar(self.menuBar)

        self.retranslateUi(Graficas_Window)

        QMetaObject.connectSlotsByName(Graficas_Window)
    # setupUi

    def retranslateUi(self, Graficas_Window):
        Graficas_Window.setWindowTitle(QCoreApplication.translate("Graficas_Window", u"Titulo_Provisional", None))
        self.label.setText(QCoreApplication.translate("Graficas_Window", u"Engranaje solar", None))
        self.label_2.setText(QCoreApplication.translate("Graficas_Window", u"Engranaje anular", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("Graficas_Window", u"Control Manual", None))
        self.label_5.setText(QCoreApplication.translate("Graficas_Window", u"Posici\u00f3n Angular del Pi\u00f1on \u03b8 (\u00b0)", None))
    # retranslateUi

