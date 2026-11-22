# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Seleccion_de_sistema.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel,
    QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
    QWidget)
import Logo_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setWindowModality(Qt.WindowModality.WindowModal)
        MainWindow.resize(1008, 475)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line, 3, 1, 1, 4)

        self.pushButton_planetario = QPushButton(self.centralwidget)
        self.pushButton_planetario.setObjectName(u"pushButton_planetario")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_planetario.sizePolicy().hasHeightForWidth())
        self.pushButton_planetario.setSizePolicy(sizePolicy)
        self.pushButton_planetario.setMinimumSize(QSize(240, 240))
        self.pushButton_planetario.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        icon = QIcon()
        icon.addFile(u"Recursos/Planetary.PNG", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_planetario.setIcon(icon)
        self.pushButton_planetario.setIconSize(QSize(230, 230))

        self.gridLayout.addWidget(self.pushButton_planetario, 4, 4, 1, 1)

        self.pushButton_cremallera = QPushButton(self.centralwidget)
        self.pushButton_cremallera.setObjectName(u"pushButton_cremallera")
        sizePolicy.setHeightForWidth(self.pushButton_cremallera.sizePolicy().hasHeightForWidth())
        self.pushButton_cremallera.setSizePolicy(sizePolicy)
        self.pushButton_cremallera.setMinimumSize(QSize(240, 240))
        self.pushButton_cremallera.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        icon1 = QIcon()
        icon1.addFile(u"Recursos/rackandpinion.PNG", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_cremallera.setIcon(icon1)
        self.pushButton_cremallera.setIconSize(QSize(230, 230))

        self.gridLayout.addWidget(self.pushButton_cremallera, 4, 1, 1, 1)

        self.pushButton_epitrocoidal = QPushButton(self.centralwidget)
        self.pushButton_epitrocoidal.setObjectName(u"pushButton_epitrocoidal")
        sizePolicy.setHeightForWidth(self.pushButton_epitrocoidal.sizePolicy().hasHeightForWidth())
        self.pushButton_epitrocoidal.setSizePolicy(sizePolicy)
        self.pushButton_epitrocoidal.setMinimumSize(QSize(240, 240))
        self.pushButton_epitrocoidal.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        icon2 = QIcon()
        icon2.addFile(u"Recursos/epytrochoidal_1.PNG", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_epitrocoidal.setIcon(icon2)
        self.pushButton_epitrocoidal.setIconSize(QSize(230, 230))

        self.gridLayout.addWidget(self.pushButton_epitrocoidal, 4, 2, 1, 1)

        self.horizontalSpacer = QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 4, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 4, 5, 1, 1)

        self.pushButton_hipotrocoidal = QPushButton(self.centralwidget)
        self.pushButton_hipotrocoidal.setObjectName(u"pushButton_hipotrocoidal")
        sizePolicy.setHeightForWidth(self.pushButton_hipotrocoidal.sizePolicy().hasHeightForWidth())
        self.pushButton_hipotrocoidal.setSizePolicy(sizePolicy)
        self.pushButton_hipotrocoidal.setMinimumSize(QSize(240, 240))
        self.pushButton_hipotrocoidal.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        icon3 = QIcon()
        icon3.addFile(u"Recursos/hypotrochoidal.PNG", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_hipotrocoidal.setIcon(icon3)
        self.pushButton_hipotrocoidal.setIconSize(QSize(230, 230))

        self.gridLayout.addWidget(self.pushButton_hipotrocoidal, 4, 3, 1, 1)

        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.gridLayout_2 = QGridLayout(self.widget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(600, 172))
        self.label.setPixmap(QPixmap(u":/newPrefix/RPSDesign_VID.png"))
        self.label.setScaledContents(True)

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)


        self.gridLayout.addWidget(self.widget, 1, 1, 1, 4)

        self.verticalSpacer_3 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_3, 5, 2, 1, 2)

        self.verticalSpacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 0, 2, 1, 2)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.pushButton_planetario.setText("")
        self.pushButton_cremallera.setText("")
        self.pushButton_epitrocoidal.setText("")
        self.pushButton_hipotrocoidal.setText("")
        self.label.setText("")
    # retranslateUi

