# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ToothProfile_Window_PlanetarioV2.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGraphicsView, QGridLayout,
    QHeaderView, QLabel, QMainWindow, QMenuBar,
    QSizePolicy, QStatusBar, QTableWidget, QTableWidgetItem,
    QWidget)

class Ui_Graficas_Window(object):
    def setupUi(self, Graficas_Window):
        if not Graficas_Window.objectName():
            Graficas_Window.setObjectName(u"Graficas_Window")
        Graficas_Window.resize(1351, 759)
        self.centralwidget = QWidget(Graficas_Window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.table_coordinates_anular = QTableWidget(self.centralwidget)
        self.table_coordinates_anular.setObjectName(u"table_coordinates_anular")
        self.table_coordinates_anular.setMinimumSize(QSize(200, 0))
        self.table_coordinates_anular.setMaximumSize(QSize(300, 16777215))

        self.gridLayout.addWidget(self.table_coordinates_anular, 1, 3, 1, 1)

        self.table_coordinates_sun = QTableWidget(self.centralwidget)
        self.table_coordinates_sun.setObjectName(u"table_coordinates_sun")
        self.table_coordinates_sun.setMinimumSize(QSize(200, 0))
        self.table_coordinates_sun.setMaximumSize(QSize(300, 16777215))

        self.gridLayout.addWidget(self.table_coordinates_sun, 1, 0, 1, 1)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        font = QFont()
        font.setFamilies([u"Bahnschrift"])
        font.setPointSize(24)
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_2, 0, 3, 1, 3)

        self.graphicsView_anular = QGraphicsView(self.centralwidget)
        self.graphicsView_anular.setObjectName(u"graphicsView_anular")
        self.graphicsView_anular.setMinimumSize(QSize(450, 0))

        self.gridLayout.addWidget(self.graphicsView_anular, 1, 4, 1, 1)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line, 0, 2, 2, 1)

        self.graphicsView_sun = QGraphicsView(self.centralwidget)
        self.graphicsView_sun.setObjectName(u"graphicsView_sun")
        self.graphicsView_sun.setMinimumSize(QSize(450, 0))

        self.gridLayout.addWidget(self.graphicsView_sun, 1, 1, 1, 1)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)

        Graficas_Window.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(Graficas_Window)
        self.statusbar.setObjectName(u"statusbar")
        Graficas_Window.setStatusBar(self.statusbar)
        self.menuBar = QMenuBar(Graficas_Window)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1351, 33))
        Graficas_Window.setMenuBar(self.menuBar)

        self.retranslateUi(Graficas_Window)

        QMetaObject.connectSlotsByName(Graficas_Window)
    # setupUi

    def retranslateUi(self, Graficas_Window):
        Graficas_Window.setWindowTitle(QCoreApplication.translate("Graficas_Window", u"Perfil del diente", None))
        self.label_2.setText(QCoreApplication.translate("Graficas_Window", u"Engranaje anular", None))
        self.label.setText(QCoreApplication.translate("Graficas_Window", u"Engranaje solar", None))
    # retranslateUi

