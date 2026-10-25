# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Perfildevelocidad_simulador_Window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFrame, QGraphicsView, QGridLayout, QGroupBox,
    QHeaderView, QLabel, QListWidget, QListWidgetItem,
    QMainWindow, QMenu, QMenuBar, QProgressBar,
    QPushButton, QSizePolicy, QSpacerItem, QSpinBox,
    QStackedWidget, QStatusBar, QTableWidget, QTableWidgetItem,
    QWidget)

class Ui_GiroImpuesto_window(object):
    def setupUi(self, GiroImpuesto_window):
        if not GiroImpuesto_window.objectName():
            GiroImpuesto_window.setObjectName(u"GiroImpuesto_window")
        GiroImpuesto_window.resize(1251, 887)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(GiroImpuesto_window.sizePolicy().hasHeightForWidth())
        GiroImpuesto_window.setSizePolicy(sizePolicy)
        GiroImpuesto_window.setMinimumSize(QSize(0, 0))
        self.actionAbrid = QAction(GiroImpuesto_window)
        self.actionAbrid.setObjectName(u"actionAbrid")
        self.actionGuardar = QAction(GiroImpuesto_window)
        self.actionGuardar.setObjectName(u"actionGuardar")
        self.actionExportar_CSV = QAction(GiroImpuesto_window)
        self.actionExportar_CSV.setObjectName(u"actionExportar_CSV")
        self.actionCerra = QAction(GiroImpuesto_window)
        self.actionCerra.setObjectName(u"actionCerra")
        self.actionGu_a_Tecnica = QAction(GiroImpuesto_window)
        self.actionGu_a_Tecnica.setObjectName(u"actionGu_a_Tecnica")
        self.centralwidget = QWidget(GiroImpuesto_window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_6 = QGridLayout(self.centralwidget)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.pushButton_10 = QPushButton(self.centralwidget)
        self.pushButton_10.setObjectName(u"pushButton_10")

        self.gridLayout_6.addWidget(self.pushButton_10, 2, 3, 1, 1)

        self.pushButton_9 = QPushButton(self.centralwidget)
        self.pushButton_9.setObjectName(u"pushButton_9")

        self.gridLayout_6.addWidget(self.pushButton_9, 2, 2, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_6.addItem(self.horizontalSpacer, 2, 1, 1, 1)

        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_4 = QGridLayout(self.groupBox_2)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.groupBox_7 = QGroupBox(self.groupBox_2)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.gridLayout_10 = QGridLayout(self.groupBox_7)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.stackedWidget = QStackedWidget(self.groupBox_7)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.gridLayout_12 = QGridLayout(self.page)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.label_10 = QLabel(self.page)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_12.addWidget(self.label_10, 0, 0, 1, 1)

        self.doubleSpinBox_pendientegen = QDoubleSpinBox(self.page)
        self.doubleSpinBox_pendientegen.setObjectName(u"doubleSpinBox_pendientegen")

        self.gridLayout_12.addWidget(self.doubleSpinBox_pendientegen, 0, 1, 1, 1)

        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.gridLayout_13 = QGridLayout(self.page_2)
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.label_11 = QLabel(self.page_2)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout_13.addWidget(self.label_11, 1, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_13.addItem(self.verticalSpacer, 0, 0, 1, 2)

        self.label_12 = QLabel(self.page_2)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_13.addWidget(self.label_12, 2, 0, 1, 1)

        self.doubleSpinBox_Fase = QDoubleSpinBox(self.page_2)
        self.doubleSpinBox_Fase.setObjectName(u"doubleSpinBox_Fase")

        self.gridLayout_13.addWidget(self.doubleSpinBox_Fase, 3, 1, 1, 1)

        self.label_13 = QLabel(self.page_2)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_13.addWidget(self.label_13, 3, 0, 1, 1)

        self.doubleSpinBox_frecuencia = QDoubleSpinBox(self.page_2)
        self.doubleSpinBox_frecuencia.setObjectName(u"doubleSpinBox_frecuencia")

        self.gridLayout_13.addWidget(self.doubleSpinBox_frecuencia, 2, 1, 1, 1)

        self.doubleSpinBox_amplitud = QDoubleSpinBox(self.page_2)
        self.doubleSpinBox_amplitud.setObjectName(u"doubleSpinBox_amplitud")

        self.gridLayout_13.addWidget(self.doubleSpinBox_amplitud, 1, 1, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_13.addItem(self.verticalSpacer_2, 4, 0, 1, 2)

        self.stackedWidget.addWidget(self.page_2)
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.gridLayout_14 = QGridLayout(self.page_3)
        self.gridLayout_14.setObjectName(u"gridLayout_14")
        self.tableWidget_coeficientes = QTableWidget(self.page_3)
        self.tableWidget_coeficientes.setObjectName(u"tableWidget_coeficientes")

        self.gridLayout_14.addWidget(self.tableWidget_coeficientes, 0, 0, 1, 2)

        self.pushButton_ponercoeficiente = QPushButton(self.page_3)
        self.pushButton_ponercoeficiente.setObjectName(u"pushButton_ponercoeficiente")

        self.gridLayout_14.addWidget(self.pushButton_ponercoeficiente, 1, 0, 1, 1)

        self.pushButton_quitarcoeficiente = QPushButton(self.page_3)
        self.pushButton_quitarcoeficiente.setObjectName(u"pushButton_quitarcoeficiente")

        self.gridLayout_14.addWidget(self.pushButton_quitarcoeficiente, 1, 1, 1, 1)

        self.stackedWidget.addWidget(self.page_3)
        self.page_4 = QWidget()
        self.page_4.setObjectName(u"page_4")
        self.gridLayout_15 = QGridLayout(self.page_4)
        self.gridLayout_15.setObjectName(u"gridLayout_15")
        self.spinBox_gradocurva = QSpinBox(self.page_4)
        self.spinBox_gradocurva.setObjectName(u"spinBox_gradocurva")

        self.gridLayout_15.addWidget(self.spinBox_gradocurva, 1, 1, 1, 1)

        self.label_19 = QLabel(self.page_4)
        self.label_19.setObjectName(u"label_19")

        self.gridLayout_15.addWidget(self.label_19, 1, 0, 1, 1)

        self.tableWidget_listapuntos = QTableWidget(self.page_4)
        self.tableWidget_listapuntos.setObjectName(u"tableWidget_listapuntos")

        self.gridLayout_15.addWidget(self.tableWidget_listapuntos, 2, 0, 1, 2)

        self.pushButton_ponerpunto = QPushButton(self.page_4)
        self.pushButton_ponerpunto.setObjectName(u"pushButton_ponerpunto")

        self.gridLayout_15.addWidget(self.pushButton_ponerpunto, 3, 0, 1, 1)

        self.pushButton_quitarpunto = QPushButton(self.page_4)
        self.pushButton_quitarpunto.setObjectName(u"pushButton_quitarpunto")

        self.gridLayout_15.addWidget(self.pushButton_quitarpunto, 3, 1, 1, 1)

        self.stackedWidget.addWidget(self.page_4)
        self.page_5 = QWidget()
        self.page_5.setObjectName(u"page_5")
        self.gridLayout_16 = QGridLayout(self.page_5)
        self.gridLayout_16.setObjectName(u"gridLayout_16")
        self.doubleSpinBox_pendientefin = QDoubleSpinBox(self.page_5)
        self.doubleSpinBox_pendientefin.setObjectName(u"doubleSpinBox_pendientefin")

        self.gridLayout_16.addWidget(self.doubleSpinBox_pendientefin, 1, 1, 1, 1)

        self.tableWidget_Listapuntosspline = QTableWidget(self.page_5)
        self.tableWidget_Listapuntosspline.setObjectName(u"tableWidget_Listapuntosspline")

        self.gridLayout_16.addWidget(self.tableWidget_Listapuntosspline, 2, 0, 1, 2)

        self.doubleSpinBox_pendienteini = QDoubleSpinBox(self.page_5)
        self.doubleSpinBox_pendienteini.setObjectName(u"doubleSpinBox_pendienteini")

        self.gridLayout_16.addWidget(self.doubleSpinBox_pendienteini, 0, 1, 1, 1)

        self.label_14 = QLabel(self.page_5)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout_16.addWidget(self.label_14, 0, 0, 1, 1)

        self.pushButton_ponerpuntospline = QPushButton(self.page_5)
        self.pushButton_ponerpuntospline.setObjectName(u"pushButton_ponerpuntospline")

        self.gridLayout_16.addWidget(self.pushButton_ponerpuntospline, 3, 0, 1, 1)

        self.pushButton_quitarpuntospline = QPushButton(self.page_5)
        self.pushButton_quitarpuntospline.setObjectName(u"pushButton_quitarpuntospline")

        self.gridLayout_16.addWidget(self.pushButton_quitarpuntospline, 3, 1, 1, 1)

        self.label_15 = QLabel(self.page_5)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_16.addWidget(self.label_15, 1, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_5)

        self.gridLayout_10.addWidget(self.stackedWidget, 2, 0, 1, 3)


        self.gridLayout_4.addWidget(self.groupBox_7, 0, 4, 2, 1)

        self.groupBox_6 = QGroupBox(self.groupBox_2)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.gridLayout_9 = QGridLayout(self.groupBox_6)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.pushButton_reemplazarfuncion = QPushButton(self.groupBox_6)
        self.pushButton_reemplazarfuncion.setObjectName(u"pushButton_reemplazarfuncion")

        self.gridLayout_9.addWidget(self.pushButton_reemplazarfuncion, 4, 0, 1, 2)

        self.comboBox_tipodefuncion = QComboBox(self.groupBox_6)
        self.comboBox_tipodefuncion.addItem("")
        self.comboBox_tipodefuncion.addItem("")
        self.comboBox_tipodefuncion.addItem("")
        self.comboBox_tipodefuncion.addItem("")
        self.comboBox_tipodefuncion.addItem("")
        self.comboBox_tipodefuncion.addItem("")
        self.comboBox_tipodefuncion.addItem("")
        self.comboBox_tipodefuncion.addItem("")
        self.comboBox_tipodefuncion.addItem("")
        self.comboBox_tipodefuncion.addItem("")
        self.comboBox_tipodefuncion.setObjectName(u"comboBox_tipodefuncion")

        self.gridLayout_9.addWidget(self.comboBox_tipodefuncion, 3, 1, 1, 1)

        self.pushButton_ponerfuncion = QPushButton(self.groupBox_6)
        self.pushButton_ponerfuncion.setObjectName(u"pushButton_ponerfuncion")

        self.gridLayout_9.addWidget(self.pushButton_ponerfuncion, 1, 0, 1, 1)

        self.line_2 = QFrame(self.groupBox_6)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_9.addWidget(self.line_2, 2, 0, 1, 2)

        self.label_7 = QLabel(self.groupBox_6)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_9.addWidget(self.label_7, 3, 0, 1, 1)

        self.pushButton_quitarfuncion = QPushButton(self.groupBox_6)
        self.pushButton_quitarfuncion.setObjectName(u"pushButton_quitarfuncion")

        self.gridLayout_9.addWidget(self.pushButton_quitarfuncion, 1, 1, 1, 1)

        self.listWidget_Ley = QListWidget(self.groupBox_6)
        self.listWidget_Ley.setObjectName(u"listWidget_Ley")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.listWidget_Ley.sizePolicy().hasHeightForWidth())
        self.listWidget_Ley.setSizePolicy(sizePolicy1)
        self.listWidget_Ley.setMinimumSize(QSize(0, 150))
        self.listWidget_Ley.setMaximumSize(QSize(16777215, 150))

        self.gridLayout_9.addWidget(self.listWidget_Ley, 0, 0, 1, 2)


        self.gridLayout_4.addWidget(self.groupBox_6, 0, 3, 2, 1)

        self.groupBox_5 = QGroupBox(self.groupBox_2)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.gridLayout_8 = QGridLayout(self.groupBox_5)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.label_6 = QLabel(self.groupBox_5)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_8.addWidget(self.label_6, 3, 2, 1, 1)

        self.label_4 = QLabel(self.groupBox_5)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_8.addWidget(self.label_4, 0, 2, 1, 1)

        self.label_5 = QLabel(self.groupBox_5)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_8.addWidget(self.label_5, 3, 0, 1, 1)

        self.doubleSpinBox_yfin = QDoubleSpinBox(self.groupBox_5)
        self.doubleSpinBox_yfin.setObjectName(u"doubleSpinBox_yfin")

        self.gridLayout_8.addWidget(self.doubleSpinBox_yfin, 3, 3, 1, 1)

        self.doubleSpinBox_tiempofin = QDoubleSpinBox(self.groupBox_5)
        self.doubleSpinBox_tiempofin.setObjectName(u"doubleSpinBox_tiempofin")

        self.gridLayout_8.addWidget(self.doubleSpinBox_tiempofin, 3, 1, 1, 1)

        self.doubleSpinBox_yini = QDoubleSpinBox(self.groupBox_5)
        self.doubleSpinBox_yini.setObjectName(u"doubleSpinBox_yini")

        self.gridLayout_8.addWidget(self.doubleSpinBox_yini, 0, 3, 1, 1)

        self.doubleSpinBox_tiempoini = QDoubleSpinBox(self.groupBox_5)
        self.doubleSpinBox_tiempoini.setObjectName(u"doubleSpinBox_tiempoini")

        self.gridLayout_8.addWidget(self.doubleSpinBox_tiempoini, 0, 1, 1, 1)

        self.label_3 = QLabel(self.groupBox_5)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_8.addWidget(self.label_3, 0, 0, 1, 1)

        self.line = QFrame(self.groupBox_5)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_8.addWidget(self.line, 1, 0, 1, 4)


        self.gridLayout_4.addWidget(self.groupBox_5, 1, 0, 1, 1)

        self.groupBox_4 = QGroupBox(self.groupBox_2)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.gridLayout_7 = QGridLayout(self.groupBox_4)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.listWidget_tramo = QListWidget(self.groupBox_4)
        self.listWidget_tramo.setObjectName(u"listWidget_tramo")
        sizePolicy1.setHeightForWidth(self.listWidget_tramo.sizePolicy().hasHeightForWidth())
        self.listWidget_tramo.setSizePolicy(sizePolicy1)
        self.listWidget_tramo.setMinimumSize(QSize(0, 150))
        self.listWidget_tramo.setMaximumSize(QSize(16777215, 150))

        self.gridLayout_7.addWidget(self.listWidget_tramo, 0, 0, 1, 2)

        self.pushButton_quitartramo = QPushButton(self.groupBox_4)
        self.pushButton_quitartramo.setObjectName(u"pushButton_quitartramo")

        self.gridLayout_7.addWidget(self.pushButton_quitartramo, 1, 1, 1, 1)

        self.pushButton_ponertramo = QPushButton(self.groupBox_4)
        self.pushButton_ponertramo.setObjectName(u"pushButton_ponertramo")

        self.gridLayout_7.addWidget(self.pushButton_ponertramo, 1, 0, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox_4, 0, 0, 1, 1)


        self.gridLayout_6.addWidget(self.groupBox_2, 1, 0, 1, 4)

        self.groupBox_3 = QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout_5 = QGridLayout(self.groupBox_3)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.label = QLabel(self.groupBox_3)
        self.label.setObjectName(u"label")

        self.gridLayout_5.addWidget(self.label, 1, 0, 1, 1)

        self.comboBox_preset = QComboBox(self.groupBox_3)
        self.comboBox_preset.addItem("")
        self.comboBox_preset.addItem("")
        self.comboBox_preset.addItem("")
        self.comboBox_preset.addItem("")
        self.comboBox_preset.addItem("")
        self.comboBox_preset.addItem("")
        self.comboBox_preset.addItem("")
        self.comboBox_preset.addItem("")
        self.comboBox_preset.setObjectName(u"comboBox_preset")

        self.gridLayout_5.addWidget(self.comboBox_preset, 1, 1, 1, 1)

        self.frame = QFrame(self.groupBox_3)
        self.frame.setObjectName(u"frame")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy2)
        self.frame.setMinimumSize(QSize(0, 370))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout = QGridLayout(self.frame)
        self.gridLayout.setObjectName(u"gridLayout")
        self.widget_grafica = QWidget(self.frame)
        self.widget_grafica.setObjectName(u"widget_grafica")
        self.widget_grafica.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.gridLayout.addWidget(self.widget_grafica, 0, 0, 1, 2)

        self.groupBox = QGroupBox(self.frame)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy3)
        self.gridLayout_3 = QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.checkBox_Velocidad = QCheckBox(self.groupBox)
        self.checkBox_Velocidad.setObjectName(u"checkBox_Velocidad")

        self.gridLayout_3.addWidget(self.checkBox_Velocidad, 0, 1, 1, 1)

        self.checkBox_Posicion = QCheckBox(self.groupBox)
        self.checkBox_Posicion.setObjectName(u"checkBox_Posicion")

        self.gridLayout_3.addWidget(self.checkBox_Posicion, 0, 0, 1, 1)

        self.checkBox_Aceleracion = QCheckBox(self.groupBox)
        self.checkBox_Aceleracion.setObjectName(u"checkBox_Aceleracion")

        self.gridLayout_3.addWidget(self.checkBox_Aceleracion, 0, 2, 1, 1)


        self.gridLayout.addWidget(self.groupBox, 1, 0, 1, 1)


        self.gridLayout_5.addWidget(self.frame, 1, 5, 2, 1)

        self.frame_2 = QFrame(self.groupBox_3)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.frame_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.graphicsView_ruedamovil = QGraphicsView(self.frame_2)
        self.graphicsView_ruedamovil.setObjectName(u"graphicsView_ruedamovil")

        self.gridLayout_2.addWidget(self.graphicsView_ruedamovil, 1, 0, 1, 1)

        self.frame_3 = QFrame(self.frame_2)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_11 = QGridLayout(self.frame_3)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.doubleSpinBox_5 = QDoubleSpinBox(self.frame_3)
        self.doubleSpinBox_5.setObjectName(u"doubleSpinBox_5")

        self.gridLayout_11.addWidget(self.doubleSpinBox_5, 0, 4, 1, 1)

        self.pushButton_pausar = QPushButton(self.frame_3)
        self.pushButton_pausar.setObjectName(u"pushButton_pausar")
        self.pushButton_pausar.setMinimumSize(QSize(0, 50))
        self.pushButton_pausar.setMaximumSize(QSize(50, 16777215))
        font = QFont()
        font.setPointSize(22)
        font.setBold(True)
        self.pushButton_pausar.setFont(font)

        self.gridLayout_11.addWidget(self.pushButton_pausar, 0, 1, 1, 1)

        self.comboBox_4 = QComboBox(self.frame_3)
        self.comboBox_4.setObjectName(u"comboBox_4")

        self.gridLayout_11.addWidget(self.comboBox_4, 0, 6, 1, 1)

        self.progressBar = QProgressBar(self.frame_3)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)

        self.gridLayout_11.addWidget(self.progressBar, 1, 0, 1, 7)

        self.label_9 = QLabel(self.frame_3)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_11.addWidget(self.label_9, 0, 5, 1, 1)

        self.pushButton_reproducir = QPushButton(self.frame_3)
        self.pushButton_reproducir.setObjectName(u"pushButton_reproducir")
        self.pushButton_reproducir.setMinimumSize(QSize(0, 50))
        self.pushButton_reproducir.setMaximumSize(QSize(50, 16777215))
        font1 = QFont()
        font1.setFamilies([u"Bahnschrift"])
        font1.setPointSize(22)
        self.pushButton_reproducir.setFont(font1)

        self.gridLayout_11.addWidget(self.pushButton_reproducir, 0, 0, 1, 1)

        self.pushButton_Reiniciar = QPushButton(self.frame_3)
        self.pushButton_Reiniciar.setObjectName(u"pushButton_Reiniciar")
        self.pushButton_Reiniciar.setMinimumSize(QSize(0, 50))
        self.pushButton_Reiniciar.setMaximumSize(QSize(50, 16777215))
        font2 = QFont()
        font2.setPointSize(22)
        self.pushButton_Reiniciar.setFont(font2)

        self.gridLayout_11.addWidget(self.pushButton_Reiniciar, 0, 2, 1, 1)

        self.label_8 = QLabel(self.frame_3)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_11.addWidget(self.label_8, 0, 3, 1, 1)


        self.gridLayout_2.addWidget(self.frame_3, 2, 0, 1, 1)


        self.gridLayout_5.addWidget(self.frame_2, 2, 0, 1, 3)

        self.pushButton_Aplicar_preset = QPushButton(self.groupBox_3)
        self.pushButton_Aplicar_preset.setObjectName(u"pushButton_Aplicar_preset")

        self.gridLayout_5.addWidget(self.pushButton_Aplicar_preset, 1, 2, 1, 1)


        self.gridLayout_6.addWidget(self.groupBox_3, 0, 0, 1, 4)

        GiroImpuesto_window.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(GiroImpuesto_window)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1251, 33))
        self.menuArchivo = QMenu(self.menubar)
        self.menuArchivo.setObjectName(u"menuArchivo")
        self.menuAyuda = QMenu(self.menubar)
        self.menuAyuda.setObjectName(u"menuAyuda")
        GiroImpuesto_window.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(GiroImpuesto_window)
        self.statusbar.setObjectName(u"statusbar")
        GiroImpuesto_window.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuArchivo.menuAction())
        self.menubar.addAction(self.menuAyuda.menuAction())
        self.menuArchivo.addAction(self.actionAbrid)
        self.menuArchivo.addAction(self.actionGuardar)
        self.menuArchivo.addAction(self.actionExportar_CSV)
        self.menuArchivo.addAction(self.actionCerra)
        self.menuAyuda.addAction(self.actionGu_a_Tecnica)

        self.retranslateUi(GiroImpuesto_window)

        self.stackedWidget.setCurrentIndex(4)


        QMetaObject.connectSlotsByName(GiroImpuesto_window)
    # setupUi

    def retranslateUi(self, GiroImpuesto_window):
        GiroImpuesto_window.setWindowTitle(QCoreApplication.translate("GiroImpuesto_window", u"Giro Impuesto", None))
        self.actionAbrid.setText(QCoreApplication.translate("GiroImpuesto_window", u"Abrir", None))
        self.actionGuardar.setText(QCoreApplication.translate("GiroImpuesto_window", u"Guardar", None))
        self.actionExportar_CSV.setText(QCoreApplication.translate("GiroImpuesto_window", u"Exportar CSV", None))
        self.actionCerra.setText(QCoreApplication.translate("GiroImpuesto_window", u"Cerrar", None))
        self.actionGu_a_Tecnica.setText(QCoreApplication.translate("GiroImpuesto_window", u"Gu\u00eda Tecnica", None))
        self.pushButton_10.setText(QCoreApplication.translate("GiroImpuesto_window", u"Cancelar", None))
        self.pushButton_9.setText(QCoreApplication.translate("GiroImpuesto_window", u"Aceptar", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("GiroImpuesto_window", u"Setup", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("GiroImpuesto_window", u"Par\u00e1metros de funci\u00f3n", None))
        self.label_10.setText(QCoreApplication.translate("GiroImpuesto_window", u"Pendiente", None))
        self.label_11.setText(QCoreApplication.translate("GiroImpuesto_window", u"Amplitud", None))
        self.label_12.setText(QCoreApplication.translate("GiroImpuesto_window", u"Frecuencia (Hz)", None))
        self.label_13.setText(QCoreApplication.translate("GiroImpuesto_window", u"Fase (\u00b0)", None))
        self.pushButton_ponercoeficiente.setText(QCoreApplication.translate("GiroImpuesto_window", u"+ Coeficiente", None))
        self.pushButton_quitarcoeficiente.setText(QCoreApplication.translate("GiroImpuesto_window", u"- Coeficiente", None))
        self.label_19.setText(QCoreApplication.translate("GiroImpuesto_window", u"Grado de la curva", None))
        self.pushButton_ponerpunto.setText(QCoreApplication.translate("GiroImpuesto_window", u"+ Punto", None))
        self.pushButton_quitarpunto.setText(QCoreApplication.translate("GiroImpuesto_window", u"- Punto", None))
        self.label_14.setText(QCoreApplication.translate("GiroImpuesto_window", u"Pendiente incial", None))
        self.pushButton_ponerpuntospline.setText(QCoreApplication.translate("GiroImpuesto_window", u"+ Punto", None))
        self.pushButton_quitarpuntospline.setText(QCoreApplication.translate("GiroImpuesto_window", u"- Punto", None))
        self.label_15.setText(QCoreApplication.translate("GiroImpuesto_window", u"Pendiente final", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("GiroImpuesto_window", u"Funciones de Movimiento", None))
        self.pushButton_reemplazarfuncion.setText(QCoreApplication.translate("GiroImpuesto_window", u"Reemplazar", None))
        self.comboBox_tipodefuncion.setItemText(0, QCoreApplication.translate("GiroImpuesto_window", u"Rampa lineal", None))
        self.comboBox_tipodefuncion.setItemText(1, QCoreApplication.translate("GiroImpuesto_window", u"Rampa c\u00fabica", None))
        self.comboBox_tipodefuncion.setItemText(2, QCoreApplication.translate("GiroImpuesto_window", u"Cicloidal", None))
        self.comboBox_tipodefuncion.setItemText(3, QCoreApplication.translate("GiroImpuesto_window", u"Arm\u00f3nica", None))
        self.comboBox_tipodefuncion.setItemText(4, QCoreApplication.translate("GiroImpuesto_window", u"Sinusoidal", None))
        self.comboBox_tipodefuncion.setItemText(5, QCoreApplication.translate("GiroImpuesto_window", u"Sinusoidal modificada", None))
        self.comboBox_tipodefuncion.setItemText(6, QCoreApplication.translate("GiroImpuesto_window", u"Polin\u00f3mica", None))
        self.comboBox_tipodefuncion.setItemText(7, QCoreApplication.translate("GiroImpuesto_window", u"Lista de puntos", None))
        self.comboBox_tipodefuncion.setItemText(8, QCoreApplication.translate("GiroImpuesto_window", u"Spline", None))
        self.comboBox_tipodefuncion.setItemText(9, QCoreApplication.translate("GiroImpuesto_window", u"Trapezoidal modificada", None))

        self.pushButton_ponerfuncion.setText(QCoreApplication.translate("GiroImpuesto_window", u"+ Funcion", None))
        self.label_7.setText(QCoreApplication.translate("GiroImpuesto_window", u"Tipo de funcion", None))
        self.pushButton_quitarfuncion.setText(QCoreApplication.translate("GiroImpuesto_window", u"- Funcion", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("GiroImpuesto_window", u"Intervalo", None))
        self.label_6.setText(QCoreApplication.translate("GiroImpuesto_window", u"Y\u2082", None))
        self.label_4.setText(QCoreApplication.translate("GiroImpuesto_window", u"Y\u2081", None))
        self.label_5.setText(QCoreApplication.translate("GiroImpuesto_window", u"t\u2082", None))
        self.label_3.setText(QCoreApplication.translate("GiroImpuesto_window", u"t\u2081", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("GiroImpuesto_window", u"Tramos", None))
        self.pushButton_quitartramo.setText(QCoreApplication.translate("GiroImpuesto_window", u"- Tramo", None))
        self.pushButton_ponertramo.setText(QCoreApplication.translate("GiroImpuesto_window", u"+ Tramo", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("GiroImpuesto_window", u"Gr\u00e1fica", None))
        self.label.setText(QCoreApplication.translate("GiroImpuesto_window", u"Presets", None))
        self.comboBox_preset.setItemText(0, QCoreApplication.translate("GiroImpuesto_window", u"Arranque y parada suaves", None))
        self.comboBox_preset.setItemText(1, QCoreApplication.translate("GiroImpuesto_window", u"Oscilador 100Hz", None))
        self.comboBox_preset.setItemText(2, QCoreApplication.translate("GiroImpuesto_window", u"Backlash", None))
        self.comboBox_preset.setItemText(3, QCoreApplication.translate("GiroImpuesto_window", u"Giro de 90\u00b0", None))
        self.comboBox_preset.setItemText(4, QCoreApplication.translate("GiroImpuesto_window", u"Giro de 180\u00b0", None))
        self.comboBox_preset.setItemText(5, QCoreApplication.translate("GiroImpuesto_window", u"Indexer", None))
        self.comboBox_preset.setItemText(6, QCoreApplication.translate("GiroImpuesto_window", u"Lavadora", None))
        self.comboBox_preset.setItemText(7, QCoreApplication.translate("GiroImpuesto_window", u"Vibrador", None))

        self.groupBox.setTitle(QCoreApplication.translate("GiroImpuesto_window", u"Mostrar curvas", None))
        self.checkBox_Velocidad.setText(QCoreApplication.translate("GiroImpuesto_window", u"Velocidad Angular", None))
        self.checkBox_Posicion.setText(QCoreApplication.translate("GiroImpuesto_window", u"Posici\u00f3n Angular", None))
        self.checkBox_Aceleracion.setText(QCoreApplication.translate("GiroImpuesto_window", u"Aceleraci\u00f3n Angular", None))
        self.pushButton_pausar.setText(QCoreApplication.translate("GiroImpuesto_window", u"\u23f8", None))
        self.label_9.setText(QCoreApplication.translate("GiroImpuesto_window", u"Velocidad:", None))
        self.pushButton_reproducir.setText(QCoreApplication.translate("GiroImpuesto_window", u"\u25b6\ufe0f", None))
        self.pushButton_Reiniciar.setText(QCoreApplication.translate("GiroImpuesto_window", u"\U0001f504", None))
        self.label_8.setText(QCoreApplication.translate("GiroImpuesto_window", u"Tiempo:", None))
        self.pushButton_Aplicar_preset.setText(QCoreApplication.translate("GiroImpuesto_window", u"Aplicar", None))
        self.menuArchivo.setTitle(QCoreApplication.translate("GiroImpuesto_window", u"Archivo", None))
        self.menuAyuda.setTitle(QCoreApplication.translate("GiroImpuesto_window", u"Ayuda", None))
    # retranslateUi

