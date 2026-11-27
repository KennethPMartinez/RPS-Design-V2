# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Mostrar_Ocultar_Planetario.ui'
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
        Opciones_epitrocoidal_sim.resize(281, 255)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Opciones_epitrocoidal_sim.sizePolicy().hasHeightForWidth())
        Opciones_epitrocoidal_sim.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(Opciones_epitrocoidal_sim)
        self.gridLayout.setObjectName(u"gridLayout")
        self.buttonBox = QDialogButtonBox(Opciones_epitrocoidal_sim)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox, 1, 1, 1, 1)

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
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 228, 201))
        self.gridLayout_2 = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.checkBox_circulos_de_paso = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_circulos_de_paso.setObjectName(u"checkBox_circulos_de_paso")

        self.gridLayout_2.addWidget(self.checkBox_circulos_de_paso, 0, 0, 1, 1)

        self.checkBox_lineas_de_accion = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_lineas_de_accion.setObjectName(u"checkBox_lineas_de_accion")
        self.checkBox_lineas_de_accion.setEnabled(True)
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.checkBox_lineas_de_accion.sizePolicy().hasHeightForWidth())
        self.checkBox_lineas_de_accion.setSizePolicy(sizePolicy2)
        self.checkBox_lineas_de_accion.setTristate(False)

        self.gridLayout_2.addWidget(self.checkBox_lineas_de_accion, 1, 0, 1, 1)

        self.checkBox_puntos_de_contacto = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_puntos_de_contacto.setObjectName(u"checkBox_puntos_de_contacto")
        self.checkBox_puntos_de_contacto.setEnabled(True)

        self.gridLayout_2.addWidget(self.checkBox_puntos_de_contacto, 2, 0, 1, 1)

        self.checkBox_etiquetas_de_rodillo = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_etiquetas_de_rodillo.setObjectName(u"checkBox_etiquetas_de_rodillo")
        self.checkBox_etiquetas_de_rodillo.setEnabled(True)

        self.gridLayout_2.addWidget(self.checkBox_etiquetas_de_rodillo, 3, 0, 1, 1)

        self.line_3 = QFrame(self.scrollAreaWidgetContents)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_2.addWidget(self.line_3, 4, 0, 1, 1)

        self.label_3 = QLabel(self.scrollAreaWidgetContents)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setEnabled(False)
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy3)

        self.gridLayout_2.addWidget(self.label_3, 5, 0, 1, 1)

        self.checkBox_vectoresfuerza = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_vectoresfuerza.setObjectName(u"checkBox_vectoresfuerza")
        self.checkBox_vectoresfuerza.setEnabled(False)

        self.gridLayout_2.addWidget(self.checkBox_vectoresfuerza, 6, 0, 1, 1)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 0, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 2, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 0, 0, 1, 1)


        self.retranslateUi(Opciones_epitrocoidal_sim)
        self.buttonBox.accepted.connect(Opciones_epitrocoidal_sim.accept)
        self.buttonBox.rejected.connect(Opciones_epitrocoidal_sim.reject)

        QMetaObject.connectSlotsByName(Opciones_epitrocoidal_sim)
    # setupUi

    def retranslateUi(self, Opciones_epitrocoidal_sim):
        Opciones_epitrocoidal_sim.setWindowTitle(QCoreApplication.translate("Opciones_epitrocoidal_sim", u"Mostrar/Ocultar", None))
        self.checkBox_circulos_de_paso.setText(QCoreApplication.translate("Opciones_epitrocoidal_sim", u"C\u00edrculos de paso", None))
        self.checkBox_lineas_de_accion.setText(QCoreApplication.translate("Opciones_epitrocoidal_sim", u"Lineas de acci\u00f3n de las fuerzas de \n"
"contacto", None))
        self.checkBox_puntos_de_contacto.setText(QCoreApplication.translate("Opciones_epitrocoidal_sim", u"Puntos de contacto", None))
        self.checkBox_etiquetas_de_rodillo.setText(QCoreApplication.translate("Opciones_epitrocoidal_sim", u"Etiquetas de rodillo", None))
        self.label_3.setText(QCoreApplication.translate("Opciones_epitrocoidal_sim", u"Solo Simulaci\u00f3n por Contactos", None))
        self.checkBox_vectoresfuerza.setText(QCoreApplication.translate("Opciones_epitrocoidal_sim", u"Vectores de fuerza", None))
    # retranslateUi

