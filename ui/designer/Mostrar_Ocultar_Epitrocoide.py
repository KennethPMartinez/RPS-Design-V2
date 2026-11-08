# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Mostrar_Ocultar_Epitrocoidal.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QFrame, QGridLayout, QLabel,
    QScrollArea, QSizePolicy, QSpacerItem, QWidget)

class Ui_Opciones_epitrocoidal_sim(object):
    def setupUi(self, Opciones_epitrocoidal_sim):
        if not Opciones_epitrocoidal_sim.objectName():
            Opciones_epitrocoidal_sim.setObjectName(u"Opciones_epitrocoidal_sim")
        Opciones_epitrocoidal_sim.setWindowModality(Qt.WindowModality.NonModal)
        Opciones_epitrocoidal_sim.resize(283, 338)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Opciones_epitrocoidal_sim.sizePolicy().hasHeightForWidth())
        Opciones_epitrocoidal_sim.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(Opciones_epitrocoidal_sim)
        self.gridLayout.setObjectName(u"gridLayout")
        self.scrollArea = QScrollArea(Opciones_epitrocoidal_sim)
        self.scrollArea.setObjectName(u"scrollArea")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy1)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 249, 284))
        self.gridLayout_7 = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.line_2 = QFrame(self.scrollAreaWidgetContents)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_7.addWidget(self.line_2, 11, 0, 1, 1)

        self.checkBox_etiquetas_de_rodillo = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_etiquetas_de_rodillo.setObjectName(u"checkBox_etiquetas_de_rodillo")
        self.checkBox_etiquetas_de_rodillo.setEnabled(True)
        self.checkBox_etiquetas_de_rodillo.setChecked(False)

        self.gridLayout_7.addWidget(self.checkBox_etiquetas_de_rodillo, 4, 0, 1, 1)

        self.line = QFrame(self.scrollAreaWidgetContents)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_7.addWidget(self.line, 8, 0, 1, 1)

        self.label_2 = QLabel(self.scrollAreaWidgetContents)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setEnabled(False)
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy2)

        self.gridLayout_7.addWidget(self.label_2, 12, 0, 1, 1)

        self.checkBox_circulos_de_paso = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_circulos_de_paso.setObjectName(u"checkBox_circulos_de_paso")
        self.checkBox_circulos_de_paso.setChecked(False)

        self.gridLayout_7.addWidget(self.checkBox_circulos_de_paso, 1, 0, 1, 1)

        self.label = QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName(u"label")
        sizePolicy2.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy2)

        self.gridLayout_7.addWidget(self.label, 9, 0, 1, 1)

        self.checkBox_epitrocoide_base = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_epitrocoide_base.setObjectName(u"checkBox_epitrocoide_base")
        self.checkBox_epitrocoide_base.setEnabled(False)

        self.gridLayout_7.addWidget(self.checkBox_epitrocoide_base, 13, 0, 1, 1)

        self.checkBox_camino_de_contacto = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_camino_de_contacto.setObjectName(u"checkBox_camino_de_contacto")
        self.checkBox_camino_de_contacto.setEnabled(True)

        self.gridLayout_7.addWidget(self.checkBox_camino_de_contacto, 10, 0, 1, 1)

        self.checkBox_lineas_de_accion = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_lineas_de_accion.setObjectName(u"checkBox_lineas_de_accion")
        self.checkBox_lineas_de_accion.setEnabled(True)
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.checkBox_lineas_de_accion.sizePolicy().hasHeightForWidth())
        self.checkBox_lineas_de_accion.setSizePolicy(sizePolicy3)
        self.checkBox_lineas_de_accion.setChecked(False)
        self.checkBox_lineas_de_accion.setTristate(False)

        self.gridLayout_7.addWidget(self.checkBox_lineas_de_accion, 2, 0, 1, 1)

        self.checkBox_puntos_de_contacto = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_puntos_de_contacto.setObjectName(u"checkBox_puntos_de_contacto")
        self.checkBox_puntos_de_contacto.setEnabled(True)
        self.checkBox_puntos_de_contacto.setChecked(False)

        self.gridLayout_7.addWidget(self.checkBox_puntos_de_contacto, 3, 0, 1, 1)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 0, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 2, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 0, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(Opciones_epitrocoidal_sim)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 3)


        self.retranslateUi(Opciones_epitrocoidal_sim)
        self.buttonBox.accepted.connect(Opciones_epitrocoidal_sim.accept)
        self.buttonBox.rejected.connect(Opciones_epitrocoidal_sim.reject)

        QMetaObject.connectSlotsByName(Opciones_epitrocoidal_sim)
    # setupUi

    def retranslateUi(self, Opciones_epitrocoidal_sim):
        Opciones_epitrocoidal_sim.setWindowTitle(QCoreApplication.translate("Opciones_epitrocoidal_sim", u"Mostrar/Ocultar", None))
        self.checkBox_etiquetas_de_rodillo.setText(QCoreApplication.translate("Opciones_epitrocoidal_sim", u"Etiquetas de rodillo", None))
        self.label_2.setText(QCoreApplication.translate("Opciones_epitrocoidal_sim", u"Solo Modo Orbitar", None))
        self.checkBox_circulos_de_paso.setText(QCoreApplication.translate("Opciones_epitrocoidal_sim", u"C\u00edrculos de paso", None))
        self.label.setText(QCoreApplication.translate("Opciones_epitrocoidal_sim", u"Solo modo Fijo en X+", None))
        self.checkBox_epitrocoide_base.setText(QCoreApplication.translate("Opciones_epitrocoidal_sim", u"Epitrocoide base", None))
        self.checkBox_camino_de_contacto.setText(QCoreApplication.translate("Opciones_epitrocoidal_sim", u"Camino de contacto", None))
        self.checkBox_lineas_de_accion.setText(QCoreApplication.translate("Opciones_epitrocoidal_sim", u"Lineas de acci\u00f3n de las fuerzas de \n"
"contacto", None))
        self.checkBox_puntos_de_contacto.setText(QCoreApplication.translate("Opciones_epitrocoidal_sim", u"Puntos de contacto", None))
    # retranslateUi

