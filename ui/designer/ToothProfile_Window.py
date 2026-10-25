# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ToothProfile_Window.ui'
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
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGridLayout, QHeaderView,
    QMainWindow, QMenuBar, QSizePolicy, QStatusBar,
    QTableWidget, QTableWidgetItem, QWidget)

class Ui_Graficas_Window(object):
    def setupUi(self, Graficas_Window):
        if not Graficas_Window.objectName():
            Graficas_Window.setObjectName(u"Graficas_Window")
        Graficas_Window.resize(1028, 503)
        self.centralwidget = QWidget(Graficas_Window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.table_coordinates = QTableWidget(self.centralwidget)
        self.table_coordinates.setObjectName(u"table_coordinates")
        self.table_coordinates.setMinimumSize(QSize(250, 0))
        self.table_coordinates.setMaximumSize(QSize(400, 16777215))

        self.gridLayout.addWidget(self.table_coordinates, 0, 0, 2, 1)

        self.graphicsView = QGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setMinimumSize(QSize(500, 0))

        self.gridLayout.addWidget(self.graphicsView, 0, 1, 2, 1)

        Graficas_Window.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(Graficas_Window)
        self.statusbar.setObjectName(u"statusbar")
        Graficas_Window.setStatusBar(self.statusbar)
        self.menuBar = QMenuBar(Graficas_Window)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1028, 33))
        Graficas_Window.setMenuBar(self.menuBar)

        self.retranslateUi(Graficas_Window)

        QMetaObject.connectSlotsByName(Graficas_Window)
    # setupUi

    def retranslateUi(self, Graficas_Window):
        Graficas_Window.setWindowTitle(QCoreApplication.translate("Graficas_Window", u"Perfil del diente", None))
    # retranslateUi

