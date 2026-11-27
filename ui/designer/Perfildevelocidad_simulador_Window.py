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
    QHBoxLayout, QHeaderView, QLabel, QListWidget,
    QListWidgetItem, QMainWindow, QMenu, QMenuBar,
    QProgressBar, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QSpinBox, QSplitter, QStackedWidget,
    QStatusBar, QTabWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

class Ui_GiroImpuesto_window(object):
    def setupUi(self, GiroImpuesto_window):
        if not GiroImpuesto_window.objectName():
            GiroImpuesto_window.setObjectName(u"GiroImpuesto_window")
        GiroImpuesto_window.resize(1370, 860)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(GiroImpuesto_window.sizePolicy().hasHeightForWidth())
        GiroImpuesto_window.setSizePolicy(sizePolicy)
        GiroImpuesto_window.setMinimumSize(QSize(950, 650))
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
        self.layoutEditorRegimenes = QVBoxLayout(self.centralwidget)
        self.layoutEditorRegimenes.setObjectName(u"layoutEditorRegimenes")
        self.layoutEncabezadoRegimenes = QHBoxLayout()
        self.layoutEncabezadoRegimenes.setObjectName(u"layoutEncabezadoRegimenes")

        self.layoutEditorRegimenes.addLayout(self.layoutEncabezadoRegimenes)

        self.tabRegimenes = QTabWidget(self.centralwidget)
        self.tabRegimenes.setObjectName(u"tabRegimenes")
        self.tabCinematico = QWidget()
        self.tabCinematico.setObjectName(u"tabCinematico")
        self.layoutCinematico = QVBoxLayout(self.tabCinematico)
        self.layoutCinematico.setObjectName(u"layoutCinematico")
        self.scrollRegimenCinematico = QScrollArea(self.tabCinematico)
        self.scrollRegimenCinematico.setObjectName(u"scrollRegimenCinematico")
        self.scrollRegimenCinematico.setWidgetResizable(True)
        self.contenidoCinematico = QWidget()
        self.contenidoCinematico.setObjectName(u"contenidoCinematico")
        self.contenidoCinematico.setGeometry(QRect(0, 0, 1312, 807))
        self.layoutContenidoCinematico = QVBoxLayout(self.contenidoCinematico)
        self.layoutContenidoCinematico.setObjectName(u"layoutContenidoCinematico")
        self.groupBox_3 = QGroupBox(self.contenidoCinematico)
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
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy1)
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
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy2)
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


        self.layoutContenidoCinematico.addWidget(self.groupBox_3)

        self.groupBox_2 = QGroupBox(self.contenidoCinematico)
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
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.listWidget_Ley.sizePolicy().hasHeightForWidth())
        self.listWidget_Ley.setSizePolicy(sizePolicy3)
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
        sizePolicy3.setHeightForWidth(self.listWidget_tramo.sizePolicy().hasHeightForWidth())
        self.listWidget_tramo.setSizePolicy(sizePolicy3)
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


        self.layoutContenidoCinematico.addWidget(self.groupBox_2)

        self.espacioCinematicoFinal = QSpacerItem(20, 24, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layoutContenidoCinematico.addItem(self.espacioCinematicoFinal)

        self.scrollRegimenCinematico.setWidget(self.contenidoCinematico)

        self.layoutCinematico.addWidget(self.scrollRegimenCinematico)

        self.tabRegimenes.addTab(self.tabCinematico, "")
        self.tabDinamico = QWidget()
        self.tabDinamico.setObjectName(u"tabDinamico")
        self.layoutDinamicoPrincipal = QVBoxLayout(self.tabDinamico)
        self.layoutDinamicoPrincipal.setObjectName(u"layoutDinamicoPrincipal")
        self.groupEstudioActivo = QGroupBox(self.tabDinamico)
        self.groupEstudioActivo.setObjectName(u"groupEstudioActivo")
        self.layoutEstudioActivo = QVBoxLayout(self.groupEstudioActivo)
        self.layoutEstudioActivo.setObjectName(u"layoutEstudioActivo")
        self.filaEscenarioPreset = QHBoxLayout()
        self.filaEscenarioPreset.setObjectName(u"filaEscenarioPreset")
        self.lblEscenarioPreset = QLabel(self.groupEstudioActivo)
        self.lblEscenarioPreset.setObjectName(u"lblEscenarioPreset")

        self.filaEscenarioPreset.addWidget(self.lblEscenarioPreset)

        self.comboEscenarioDinamico = QComboBox(self.groupEstudioActivo)
        self.comboEscenarioDinamico.addItem("")
        self.comboEscenarioDinamico.addItem("")
        self.comboEscenarioDinamico.addItem("")
        self.comboEscenarioDinamico.setObjectName(u"comboEscenarioDinamico")
        self.comboEscenarioDinamico.setMinimumSize(QSize(190, 0))

        self.filaEscenarioPreset.addWidget(self.comboEscenarioDinamico)

        self.btnGuardarEscenario = QPushButton(self.groupEstudioActivo)
        self.btnGuardarEscenario.setObjectName(u"btnGuardarEscenario")
        self.btnGuardarEscenario.setEnabled(False)

        self.filaEscenarioPreset.addWidget(self.btnGuardarEscenario)

        self.btnRestaurarEscenario = QPushButton(self.groupEstudioActivo)
        self.btnRestaurarEscenario.setObjectName(u"btnRestaurarEscenario")
        self.btnRestaurarEscenario.setEnabled(False)

        self.filaEscenarioPreset.addWidget(self.btnRestaurarEscenario)


        self.layoutEstudioActivo.addLayout(self.filaEscenarioPreset)


        self.layoutDinamicoPrincipal.addWidget(self.groupEstudioActivo)

        self.splitConfiguracionYResultados = QSplitter(self.tabDinamico)
        self.splitConfiguracionYResultados.setObjectName(u"splitConfiguracionYResultados")
        self.splitConfiguracionYResultados.setOrientation(Qt.Orientation.Horizontal)
        self.panelConfiguracionDinamica = QWidget(self.splitConfiguracionYResultados)
        self.panelConfiguracionDinamica.setObjectName(u"panelConfiguracionDinamica")
        self.layoutPanelConfiguracionDinamica = QVBoxLayout(self.panelConfiguracionDinamica)
        self.layoutPanelConfiguracionDinamica.setObjectName(u"layoutPanelConfiguracionDinamica")
        self.layoutPanelConfiguracionDinamica.setContentsMargins(0, 0, 0, 0)
        self.lblSubtituloConfig = QLabel(self.panelConfiguracionDinamica)
        self.lblSubtituloConfig.setObjectName(u"lblSubtituloConfig")

        self.layoutPanelConfiguracionDinamica.addWidget(self.lblSubtituloConfig)

        self.layoutSelectorParametros = QHBoxLayout()
        self.layoutSelectorParametros.setObjectName(u"layoutSelectorParametros")
        self.listSeccionesEstudio = QListWidget(self.panelConfiguracionDinamica)
        QListWidgetItem(self.listSeccionesEstudio)
        QListWidgetItem(self.listSeccionesEstudio)
        QListWidgetItem(self.listSeccionesEstudio)
        QListWidgetItem(self.listSeccionesEstudio)
        self.listSeccionesEstudio.setObjectName(u"listSeccionesEstudio")
        self.listSeccionesEstudio.setMinimumSize(QSize(140, 280))
        self.listSeccionesEstudio.setMaximumSize(QSize(170, 16777215))

        self.layoutSelectorParametros.addWidget(self.listSeccionesEstudio)

        self.stackConfiguracion = QStackedWidget(self.panelConfiguracionDinamica)
        self.stackConfiguracion.setObjectName(u"stackConfiguracion")
        self.pageAccionamiento = QWidget()
        self.pageAccionamiento.setObjectName(u"pageAccionamiento")
        self.layoutScrollMotor = QVBoxLayout(self.pageAccionamiento)
        self.layoutScrollMotor.setObjectName(u"layoutScrollMotor")
        self.scrollPaginaMotor = QScrollArea(self.pageAccionamiento)
        self.scrollPaginaMotor.setObjectName(u"scrollPaginaMotor")
        self.scrollPaginaMotor.setWidgetResizable(True)
        self.contenidoScrollMotor = QWidget()
        self.contenidoScrollMotor.setObjectName(u"contenidoScrollMotor")
        self.contenidoScrollMotor.setGeometry(QRect(0, 0, 674, 544))
        self.layoutPaginaAccionamiento = QVBoxLayout(self.contenidoScrollMotor)
        self.layoutPaginaAccionamiento.setObjectName(u"layoutPaginaAccionamiento")
        self.comboTipoMotorFila = QHBoxLayout()
        self.comboTipoMotorFila.setObjectName(u"comboTipoMotorFila")
        self.lblComboTipoMotor = QLabel(self.contenidoScrollMotor)
        self.lblComboTipoMotor.setObjectName(u"lblComboTipoMotor")
        self.lblComboTipoMotor.setWordWrap(True)

        self.comboTipoMotorFila.addWidget(self.lblComboTipoMotor)

        self.comboTipoMotor = QComboBox(self.contenidoScrollMotor)
        self.comboTipoMotor.addItem("")
        self.comboTipoMotor.addItem("")
        self.comboTipoMotor.addItem("")
        self.comboTipoMotor.setObjectName(u"comboTipoMotor")

        self.comboTipoMotorFila.addWidget(self.comboTipoMotor)


        self.layoutPaginaAccionamiento.addLayout(self.comboTipoMotorFila)

        self.comboModoAccionamientoFila = QHBoxLayout()
        self.comboModoAccionamientoFila.setObjectName(u"comboModoAccionamientoFila")

        self.layoutPaginaAccionamiento.addLayout(self.comboModoAccionamientoFila)

        self.spinPotenciaNominalFila = QHBoxLayout()
        self.spinPotenciaNominalFila.setObjectName(u"spinPotenciaNominalFila")
        self.lblSpinPotenciaNominal = QLabel(self.contenidoScrollMotor)
        self.lblSpinPotenciaNominal.setObjectName(u"lblSpinPotenciaNominal")
        self.lblSpinPotenciaNominal.setWordWrap(True)

        self.spinPotenciaNominalFila.addWidget(self.lblSpinPotenciaNominal)

        self.spinPotenciaNominal = QDoubleSpinBox(self.contenidoScrollMotor)
        self.spinPotenciaNominal.setObjectName(u"spinPotenciaNominal")
        self.spinPotenciaNominal.setDecimals(3)
        self.spinPotenciaNominal.setMinimum(0.000000000000000)
        self.spinPotenciaNominal.setMaximum(1000000000.000000000000000)
        self.spinPotenciaNominal.setSingleStep(0.001000000000000)

        self.spinPotenciaNominalFila.addWidget(self.spinPotenciaNominal)


        self.layoutPaginaAccionamiento.addLayout(self.spinPotenciaNominalFila)

        self.spinVelocidadNominalFila = QHBoxLayout()
        self.spinVelocidadNominalFila.setObjectName(u"spinVelocidadNominalFila")

        self.layoutPaginaAccionamiento.addLayout(self.spinVelocidadNominalFila)

        self.spinParRetencionFila = QHBoxLayout()
        self.spinParRetencionFila.setObjectName(u"spinParRetencionFila")
        self.lblSpinParRetencion = QLabel(self.contenidoScrollMotor)
        self.lblSpinParRetencion.setObjectName(u"lblSpinParRetencion")
        self.lblSpinParRetencion.setWordWrap(True)

        self.spinParRetencionFila.addWidget(self.lblSpinParRetencion)

        self.spinParRetencion = QDoubleSpinBox(self.contenidoScrollMotor)
        self.spinParRetencion.setObjectName(u"spinParRetencion")
        self.spinParRetencion.setDecimals(3)
        self.spinParRetencion.setMinimum(0.000000000000000)
        self.spinParRetencion.setMaximum(1000000000.000000000000000)
        self.spinParRetencion.setSingleStep(0.001000000000000)

        self.spinParRetencionFila.addWidget(self.spinParRetencion)


        self.layoutPaginaAccionamiento.addLayout(self.spinParRetencionFila)

        self.spinFrecuenciaRedFila = QHBoxLayout()
        self.spinFrecuenciaRedFila.setObjectName(u"spinFrecuenciaRedFila")
        self.lblSpinFrecuenciaRed = QLabel(self.contenidoScrollMotor)
        self.lblSpinFrecuenciaRed.setObjectName(u"lblSpinFrecuenciaRed")
        self.lblSpinFrecuenciaRed.setWordWrap(True)

        self.spinFrecuenciaRedFila.addWidget(self.lblSpinFrecuenciaRed)

        self.spinFrecuenciaRed = QDoubleSpinBox(self.contenidoScrollMotor)
        self.spinFrecuenciaRed.setObjectName(u"spinFrecuenciaRed")
        self.spinFrecuenciaRed.setDecimals(1)
        self.spinFrecuenciaRed.setMinimum(0.000000000000000)
        self.spinFrecuenciaRed.setMaximum(1000.000000000000000)
        self.spinFrecuenciaRed.setSingleStep(0.100000000000000)
        self.spinFrecuenciaRed.setValue(50.000000000000000)

        self.spinFrecuenciaRedFila.addWidget(self.spinFrecuenciaRed)


        self.layoutPaginaAccionamiento.addLayout(self.spinFrecuenciaRedFila)

        self.spinNumeroPolosFila = QHBoxLayout()
        self.spinNumeroPolosFila.setObjectName(u"spinNumeroPolosFila")
        self.lblSpinNumeroPolos = QLabel(self.contenidoScrollMotor)
        self.lblSpinNumeroPolos.setObjectName(u"lblSpinNumeroPolos")
        self.lblSpinNumeroPolos.setWordWrap(True)

        self.spinNumeroPolosFila.addWidget(self.lblSpinNumeroPolos)

        self.spinNumeroPolos = QSpinBox(self.contenidoScrollMotor)
        self.spinNumeroPolos.setObjectName(u"spinNumeroPolos")
        self.spinNumeroPolos.setMinimum(2)
        self.spinNumeroPolos.setMaximum(40)
        self.spinNumeroPolos.setValue(4)

        self.spinNumeroPolosFila.addWidget(self.spinNumeroPolos)


        self.layoutPaginaAccionamiento.addLayout(self.spinNumeroPolosFila)

        self.groupCurvaCaracteristica = QGroupBox(self.contenidoScrollMotor)
        self.groupCurvaCaracteristica.setObjectName(u"groupCurvaCaracteristica")
        self.groupCurvaCaracteristicaLayout = QVBoxLayout(self.groupCurvaCaracteristica)
        self.groupCurvaCaracteristicaLayout.setObjectName(u"groupCurvaCaracteristicaLayout")
        self.tablaCurvaMotor = QTableWidget(self.groupCurvaCaracteristica)
        if (self.tablaCurvaMotor.columnCount() < 2):
            self.tablaCurvaMotor.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.tablaCurvaMotor.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tablaCurvaMotor.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.tablaCurvaMotor.setObjectName(u"tablaCurvaMotor")
        self.tablaCurvaMotor.setMinimumSize(QSize(0, 145))

        self.groupCurvaCaracteristicaLayout.addWidget(self.tablaCurvaMotor)

        self.layoutAccionesCurvaMotor = QHBoxLayout()
        self.layoutAccionesCurvaMotor.setObjectName(u"layoutAccionesCurvaMotor")
        self.btnAgregarPuntoMotor = QPushButton(self.groupCurvaCaracteristica)
        self.btnAgregarPuntoMotor.setObjectName(u"btnAgregarPuntoMotor")
        self.btnAgregarPuntoMotor.setEnabled(False)

        self.layoutAccionesCurvaMotor.addWidget(self.btnAgregarPuntoMotor)

        self.btnQuitarPuntoMotor = QPushButton(self.groupCurvaCaracteristica)
        self.btnQuitarPuntoMotor.setObjectName(u"btnQuitarPuntoMotor")
        self.btnQuitarPuntoMotor.setEnabled(False)

        self.layoutAccionesCurvaMotor.addWidget(self.btnQuitarPuntoMotor)

        self.btnImportarCurvaMotor = QPushButton(self.groupCurvaCaracteristica)
        self.btnImportarCurvaMotor.setObjectName(u"btnImportarCurvaMotor")
        self.btnImportarCurvaMotor.setEnabled(False)

        self.layoutAccionesCurvaMotor.addWidget(self.btnImportarCurvaMotor)


        self.groupCurvaCaracteristicaLayout.addLayout(self.layoutAccionesCurvaMotor)


        self.layoutPaginaAccionamiento.addWidget(self.groupCurvaCaracteristica)

        self.espacioMotor = QSpacerItem(20, 24, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layoutPaginaAccionamiento.addItem(self.espacioMotor)

        self.scrollPaginaMotor.setWidget(self.contenidoScrollMotor)

        self.layoutScrollMotor.addWidget(self.scrollPaginaMotor)

        self.stackConfiguracion.addWidget(self.pageAccionamiento)
        self.pageCargasExternas = QWidget()
        self.pageCargasExternas.setObjectName(u"pageCargasExternas")
        self.layoutScrollCarga = QVBoxLayout(self.pageCargasExternas)
        self.layoutScrollCarga.setObjectName(u"layoutScrollCarga")
        self.scrollPaginaCarga = QScrollArea(self.pageCargasExternas)
        self.scrollPaginaCarga.setObjectName(u"scrollPaginaCarga")
        self.scrollPaginaCarga.setWidgetResizable(True)
        self.contenidoScrollCarga = QWidget()
        self.contenidoScrollCarga.setObjectName(u"contenidoScrollCarga")
        self.contenidoScrollCarga.setGeometry(QRect(0, 0, 674, 544))
        self.layoutPaginaCargas = QVBoxLayout(self.contenidoScrollCarga)
        self.layoutPaginaCargas.setObjectName(u"layoutPaginaCargas")
        self.lblTituloCargas = QLabel(self.contenidoScrollCarga)
        self.lblTituloCargas.setObjectName(u"lblTituloCargas")

        self.layoutPaginaCargas.addWidget(self.lblTituloCargas)

        self.comboDependenciaParFila = QHBoxLayout()
        self.comboDependenciaParFila.setObjectName(u"comboDependenciaParFila")
        self.lblComboDependenciaPar = QLabel(self.contenidoScrollCarga)
        self.lblComboDependenciaPar.setObjectName(u"lblComboDependenciaPar")
        self.lblComboDependenciaPar.setWordWrap(True)

        self.comboDependenciaParFila.addWidget(self.lblComboDependenciaPar)

        self.comboDependenciaPar = QComboBox(self.contenidoScrollCarga)
        self.comboDependenciaPar.addItem("")
        self.comboDependenciaPar.addItem("")
        self.comboDependenciaPar.addItem("")
        self.comboDependenciaPar.setObjectName(u"comboDependenciaPar")

        self.comboDependenciaParFila.addWidget(self.comboDependenciaPar)


        self.layoutPaginaCargas.addLayout(self.comboDependenciaParFila)

        self.comboTipoLeyCargaFila = QHBoxLayout()
        self.comboTipoLeyCargaFila.setObjectName(u"comboTipoLeyCargaFila")
        self.lblComboTipoLeyCarga = QLabel(self.contenidoScrollCarga)
        self.lblComboTipoLeyCarga.setObjectName(u"lblComboTipoLeyCarga")
        self.lblComboTipoLeyCarga.setWordWrap(True)

        self.comboTipoLeyCargaFila.addWidget(self.lblComboTipoLeyCarga)

        self.comboTipoLeyCarga = QComboBox(self.contenidoScrollCarga)
        self.comboTipoLeyCarga.addItem("")
        self.comboTipoLeyCarga.addItem("")
        self.comboTipoLeyCarga.addItem("")
        self.comboTipoLeyCarga.addItem("")
        self.comboTipoLeyCarga.addItem("")
        self.comboTipoLeyCarga.addItem("")
        self.comboTipoLeyCarga.addItem("")
        self.comboTipoLeyCarga.addItem("")
        self.comboTipoLeyCarga.addItem("")
        self.comboTipoLeyCarga.addItem("")
        self.comboTipoLeyCarga.addItem("")
        self.comboTipoLeyCarga.setObjectName(u"comboTipoLeyCarga")

        self.comboTipoLeyCargaFila.addWidget(self.comboTipoLeyCarga)


        self.layoutPaginaCargas.addLayout(self.comboTipoLeyCargaFila)

        self.comboComponenteCargaFila = QHBoxLayout()
        self.comboComponenteCargaFila.setObjectName(u"comboComponenteCargaFila")
        self.lblComboComponenteCarga = QLabel(self.contenidoScrollCarga)
        self.lblComboComponenteCarga.setObjectName(u"lblComboComponenteCarga")
        self.lblComboComponenteCarga.setWordWrap(True)

        self.comboComponenteCargaFila.addWidget(self.lblComboComponenteCarga)

        self.comboComponenteCarga = QComboBox(self.contenidoScrollCarga)
        self.comboComponenteCarga.addItem("")
        self.comboComponenteCarga.addItem("")
        self.comboComponenteCarga.addItem("")
        self.comboComponenteCarga.setObjectName(u"comboComponenteCarga")

        self.comboComponenteCargaFila.addWidget(self.comboComponenteCarga)


        self.layoutPaginaCargas.addLayout(self.comboComponenteCargaFila)

        self.spinParResistenteFila = QHBoxLayout()
        self.spinParResistenteFila.setObjectName(u"spinParResistenteFila")
        self.lblSpinParResistente = QLabel(self.contenidoScrollCarga)
        self.lblSpinParResistente.setObjectName(u"lblSpinParResistente")
        self.lblSpinParResistente.setWordWrap(True)

        self.spinParResistenteFila.addWidget(self.lblSpinParResistente)

        self.spinParResistente = QDoubleSpinBox(self.contenidoScrollCarga)
        self.spinParResistente.setObjectName(u"spinParResistente")
        self.spinParResistente.setDecimals(4)
        self.spinParResistente.setMinimum(-1000000000.000000000000000)
        self.spinParResistente.setMaximum(1000000000.000000000000000)
        self.spinParResistente.setSingleStep(0.001000000000000)

        self.spinParResistenteFila.addWidget(self.spinParResistente)


        self.layoutPaginaCargas.addLayout(self.spinParResistenteFila)

        self.tablaPuntosCarga = QTableWidget(self.contenidoScrollCarga)
        if (self.tablaPuntosCarga.columnCount() < 2):
            self.tablaPuntosCarga.setColumnCount(2)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tablaPuntosCarga.setHorizontalHeaderItem(0, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tablaPuntosCarga.setHorizontalHeaderItem(1, __qtablewidgetitem3)
        self.tablaPuntosCarga.setObjectName(u"tablaPuntosCarga")
        self.tablaPuntosCarga.setMinimumSize(QSize(0, 185))

        self.layoutPaginaCargas.addWidget(self.tablaPuntosCarga)

        self.layoutBotonesCarga = QHBoxLayout()
        self.layoutBotonesCarga.setObjectName(u"layoutBotonesCarga")
        self.btnAgregarPuntoCarga = QPushButton(self.contenidoScrollCarga)
        self.btnAgregarPuntoCarga.setObjectName(u"btnAgregarPuntoCarga")
        self.btnAgregarPuntoCarga.setEnabled(False)

        self.layoutBotonesCarga.addWidget(self.btnAgregarPuntoCarga)

        self.btnQuitarPuntoCarga = QPushButton(self.contenidoScrollCarga)
        self.btnQuitarPuntoCarga.setObjectName(u"btnQuitarPuntoCarga")
        self.btnQuitarPuntoCarga.setEnabled(False)

        self.layoutBotonesCarga.addWidget(self.btnQuitarPuntoCarga)

        self.btnImportarCarga = QPushButton(self.contenidoScrollCarga)
        self.btnImportarCarga.setObjectName(u"btnImportarCarga")
        self.btnImportarCarga.setEnabled(False)

        self.layoutBotonesCarga.addWidget(self.btnImportarCarga)


        self.layoutPaginaCargas.addLayout(self.layoutBotonesCarga)

        self.espacioCargas = QSpacerItem(20, 24, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layoutPaginaCargas.addItem(self.espacioCargas)

        self.scrollPaginaCarga.setWidget(self.contenidoScrollCarga)

        self.layoutScrollCarga.addWidget(self.scrollPaginaCarga)

        self.stackConfiguracion.addWidget(self.pageCargasExternas)
        self.pageContacto = QWidget()
        self.pageContacto.setObjectName(u"pageContacto")
        self.layoutScrollContacto = QVBoxLayout(self.pageContacto)
        self.layoutScrollContacto.setObjectName(u"layoutScrollContacto")
        self.scrollPaginaContacto = QScrollArea(self.pageContacto)
        self.scrollPaginaContacto.setObjectName(u"scrollPaginaContacto")
        self.scrollPaginaContacto.setWidgetResizable(True)
        self.contenidoScrollContacto = QWidget()
        self.contenidoScrollContacto.setObjectName(u"contenidoScrollContacto")
        self.contenidoScrollContacto.setGeometry(QRect(0, 0, 674, 544))
        self.layoutPaginaContacto = QVBoxLayout(self.contenidoScrollContacto)
        self.layoutPaginaContacto.setObjectName(u"layoutPaginaContacto")
        self.comboModeloContactoFila = QHBoxLayout()
        self.comboModeloContactoFila.setObjectName(u"comboModeloContactoFila")
        self.lblComboModeloContacto = QLabel(self.contenidoScrollContacto)
        self.lblComboModeloContacto.setObjectName(u"lblComboModeloContacto")
        self.lblComboModeloContacto.setWordWrap(True)

        self.comboModeloContactoFila.addWidget(self.lblComboModeloContacto)

        self.comboModeloContacto = QComboBox(self.contenidoScrollContacto)
        self.comboModeloContacto.addItem("")
        self.comboModeloContacto.addItem("")
        self.comboModeloContacto.addItem("")
        self.comboModeloContacto.setObjectName(u"comboModeloContacto")

        self.comboModeloContactoFila.addWidget(self.comboModeloContacto)


        self.layoutPaginaContacto.addLayout(self.comboModeloContactoFila)

        self.spinRigidezNormalFila = QHBoxLayout()
        self.spinRigidezNormalFila.setObjectName(u"spinRigidezNormalFila")
        self.lblSpinRigidezNormal = QLabel(self.contenidoScrollContacto)
        self.lblSpinRigidezNormal.setObjectName(u"lblSpinRigidezNormal")
        self.lblSpinRigidezNormal.setWordWrap(True)

        self.spinRigidezNormalFila.addWidget(self.lblSpinRigidezNormal)

        self.spinRigidezNormal = QDoubleSpinBox(self.contenidoScrollContacto)
        self.spinRigidezNormal.setObjectName(u"spinRigidezNormal")
        self.spinRigidezNormal.setDecimals(3)
        self.spinRigidezNormal.setMinimum(0.000000000000000)
        self.spinRigidezNormal.setMaximum(1000000000000.000000000000000)
        self.spinRigidezNormal.setSingleStep(0.001000000000000)

        self.spinRigidezNormalFila.addWidget(self.spinRigidezNormal)


        self.layoutPaginaContacto.addLayout(self.spinRigidezNormalFila)

        self.spinToleranciaBrechaFila = QHBoxLayout()
        self.spinToleranciaBrechaFila.setObjectName(u"spinToleranciaBrechaFila")
        self.lblSpinToleranciaBrecha = QLabel(self.contenidoScrollContacto)
        self.lblSpinToleranciaBrecha.setObjectName(u"lblSpinToleranciaBrecha")
        self.lblSpinToleranciaBrecha.setWordWrap(True)

        self.spinToleranciaBrechaFila.addWidget(self.lblSpinToleranciaBrecha)

        self.spinToleranciaBrecha = QDoubleSpinBox(self.contenidoScrollContacto)
        self.spinToleranciaBrecha.setObjectName(u"spinToleranciaBrecha")
        self.spinToleranciaBrecha.setDecimals(6)
        self.spinToleranciaBrecha.setMinimum(0.000000000000000)
        self.spinToleranciaBrecha.setMaximum(1.000000000000000)
        self.spinToleranciaBrecha.setSingleStep(0.100000000000000)
        self.spinToleranciaBrecha.setValue(0.001000000000000)

        self.spinToleranciaBrechaFila.addWidget(self.spinToleranciaBrecha)


        self.layoutPaginaContacto.addLayout(self.spinToleranciaBrechaFila)

        self.chkRepartoMulticontacto = QCheckBox(self.contenidoScrollContacto)
        self.chkRepartoMulticontacto.setObjectName(u"chkRepartoMulticontacto")
        self.chkRepartoMulticontacto.setChecked(True)

        self.layoutPaginaContacto.addWidget(self.chkRepartoMulticontacto)

        self.chkRegistrarContactos = QCheckBox(self.contenidoScrollContacto)
        self.chkRegistrarContactos.setObjectName(u"chkRegistrarContactos")
        self.chkRegistrarContactos.setChecked(True)

        self.layoutPaginaContacto.addWidget(self.chkRegistrarContactos)

        self.chkIncluirFriccion = QCheckBox(self.contenidoScrollContacto)
        self.chkIncluirFriccion.setObjectName(u"chkIncluirFriccion")
        self.chkIncluirFriccion.setEnabled(False)

        self.layoutPaginaContacto.addWidget(self.chkIncluirFriccion)

        self.spinAmortiguamientoNormalFila = QHBoxLayout()
        self.spinAmortiguamientoNormalFila.setObjectName(u"spinAmortiguamientoNormalFila")
        self.lblSpinAmortiguamientoNormal = QLabel(self.contenidoScrollContacto)
        self.lblSpinAmortiguamientoNormal.setObjectName(u"lblSpinAmortiguamientoNormal")
        self.lblSpinAmortiguamientoNormal.setWordWrap(True)

        self.spinAmortiguamientoNormalFila.addWidget(self.lblSpinAmortiguamientoNormal)

        self.spinAmortiguamientoNormal = QDoubleSpinBox(self.contenidoScrollContacto)
        self.spinAmortiguamientoNormal.setObjectName(u"spinAmortiguamientoNormal")
        self.spinAmortiguamientoNormal.setEnabled(False)
        self.spinAmortiguamientoNormal.setDecimals(4)
        self.spinAmortiguamientoNormal.setMinimum(0.000000000000000)
        self.spinAmortiguamientoNormal.setMaximum(1000000000000.000000000000000)
        self.spinAmortiguamientoNormal.setSingleStep(0.001000000000000)

        self.spinAmortiguamientoNormalFila.addWidget(self.spinAmortiguamientoNormal)


        self.layoutPaginaContacto.addLayout(self.spinAmortiguamientoNormalFila)

        self.groupComponentesEstudio = QGroupBox(self.contenidoScrollContacto)
        self.groupComponentesEstudio.setObjectName(u"groupComponentesEstudio")
        self.groupComponentesEstudioLayout = QVBoxLayout(self.groupComponentesEstudio)
        self.groupComponentesEstudioLayout.setObjectName(u"groupComponentesEstudioLayout")
        self.tablaComponentesContacto = QTableWidget(self.groupComponentesEstudio)
        if (self.tablaComponentesContacto.columnCount() < 3):
            self.tablaComponentesContacto.setColumnCount(3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tablaComponentesContacto.setHorizontalHeaderItem(0, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tablaComponentesContacto.setHorizontalHeaderItem(1, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tablaComponentesContacto.setHorizontalHeaderItem(2, __qtablewidgetitem6)
        self.tablaComponentesContacto.setObjectName(u"tablaComponentesContacto")
        self.tablaComponentesContacto.setMinimumSize(QSize(0, 155))

        self.groupComponentesEstudioLayout.addWidget(self.tablaComponentesContacto)


        self.layoutPaginaContacto.addWidget(self.groupComponentesEstudio)

        self.espacioContacto = QSpacerItem(20, 24, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layoutPaginaContacto.addItem(self.espacioContacto)

        self.scrollPaginaContacto.setWidget(self.contenidoScrollContacto)

        self.layoutScrollContacto.addWidget(self.scrollPaginaContacto)

        self.stackConfiguracion.addWidget(self.pageContacto)
        self.pageSolucionador = QWidget()
        self.pageSolucionador.setObjectName(u"pageSolucionador")
        self.layoutScrollSolucionador = QVBoxLayout(self.pageSolucionador)
        self.layoutScrollSolucionador.setObjectName(u"layoutScrollSolucionador")
        self.scrollPaginaSolucionador = QScrollArea(self.pageSolucionador)
        self.scrollPaginaSolucionador.setObjectName(u"scrollPaginaSolucionador")
        self.scrollPaginaSolucionador.setWidgetResizable(True)
        self.contenidoScrollSolucionador = QWidget()
        self.contenidoScrollSolucionador.setObjectName(u"contenidoScrollSolucionador")
        self.contenidoScrollSolucionador.setGeometry(QRect(0, 0, 674, 544))
        self.layoutPaginaSolucionador = QVBoxLayout(self.contenidoScrollSolucionador)
        self.layoutPaginaSolucionador.setObjectName(u"layoutPaginaSolucionador")
        self.lblTituloSolucionador = QLabel(self.contenidoScrollSolucionador)
        self.lblTituloSolucionador.setObjectName(u"lblTituloSolucionador")

        self.layoutPaginaSolucionador.addWidget(self.lblTituloSolucionador)

        self.comboMetodoSolucionFila = QHBoxLayout()
        self.comboMetodoSolucionFila.setObjectName(u"comboMetodoSolucionFila")
        self.lblComboMetodoSolucion = QLabel(self.contenidoScrollSolucionador)
        self.lblComboMetodoSolucion.setObjectName(u"lblComboMetodoSolucion")
        self.lblComboMetodoSolucion.setWordWrap(True)

        self.comboMetodoSolucionFila.addWidget(self.lblComboMetodoSolucion)

        self.comboMetodoSolucion = QComboBox(self.contenidoScrollSolucionador)
        self.comboMetodoSolucion.addItem("")
        self.comboMetodoSolucion.setObjectName(u"comboMetodoSolucion")

        self.comboMetodoSolucionFila.addWidget(self.comboMetodoSolucion)


        self.layoutPaginaSolucionador.addLayout(self.comboMetodoSolucionFila)

        self.comboMuestreoEstudioFila = QHBoxLayout()
        self.comboMuestreoEstudioFila.setObjectName(u"comboMuestreoEstudioFila")
        self.lblComboMuestreoEstudio = QLabel(self.contenidoScrollSolucionador)
        self.lblComboMuestreoEstudio.setObjectName(u"lblComboMuestreoEstudio")
        self.lblComboMuestreoEstudio.setWordWrap(True)

        self.comboMuestreoEstudioFila.addWidget(self.lblComboMuestreoEstudio)

        self.comboMuestreoEstudio = QComboBox(self.contenidoScrollSolucionador)
        self.comboMuestreoEstudio.addItem("")
        self.comboMuestreoEstudio.addItem("")
        self.comboMuestreoEstudio.addItem("")
        self.comboMuestreoEstudio.setObjectName(u"comboMuestreoEstudio")

        self.comboMuestreoEstudioFila.addWidget(self.comboMuestreoEstudio)


        self.layoutPaginaSolucionador.addLayout(self.comboMuestreoEstudioFila)

        self.spinToleranciaEquilibrioFila = QHBoxLayout()
        self.spinToleranciaEquilibrioFila.setObjectName(u"spinToleranciaEquilibrioFila")
        self.lblSpinToleranciaEquilibrio = QLabel(self.contenidoScrollSolucionador)
        self.lblSpinToleranciaEquilibrio.setObjectName(u"lblSpinToleranciaEquilibrio")
        self.lblSpinToleranciaEquilibrio.setWordWrap(True)

        self.spinToleranciaEquilibrioFila.addWidget(self.lblSpinToleranciaEquilibrio)

        self.spinToleranciaEquilibrio = QDoubleSpinBox(self.contenidoScrollSolucionador)
        self.spinToleranciaEquilibrio.setObjectName(u"spinToleranciaEquilibrio")
        self.spinToleranciaEquilibrio.setDecimals(7)
        self.spinToleranciaEquilibrio.setMinimum(0.000000000000000)
        self.spinToleranciaEquilibrio.setMaximum(1000000.000000000000000)
        self.spinToleranciaEquilibrio.setSingleStep(0.100000000000000)
        self.spinToleranciaEquilibrio.setValue(0.000001000000000)

        self.spinToleranciaEquilibrioFila.addWidget(self.spinToleranciaEquilibrio)


        self.layoutPaginaSolucionador.addLayout(self.spinToleranciaEquilibrioFila)

        self.spinToleranciaMomentoFila = QHBoxLayout()
        self.spinToleranciaMomentoFila.setObjectName(u"spinToleranciaMomentoFila")
        self.lblSpinToleranciaMomento = QLabel(self.contenidoScrollSolucionador)
        self.lblSpinToleranciaMomento.setObjectName(u"lblSpinToleranciaMomento")
        self.lblSpinToleranciaMomento.setWordWrap(True)

        self.spinToleranciaMomentoFila.addWidget(self.lblSpinToleranciaMomento)

        self.spinToleranciaMomento = QDoubleSpinBox(self.contenidoScrollSolucionador)
        self.spinToleranciaMomento.setObjectName(u"spinToleranciaMomento")
        self.spinToleranciaMomento.setDecimals(7)
        self.spinToleranciaMomento.setMinimum(0.000000000000000)
        self.spinToleranciaMomento.setMaximum(1000000000.000000000000000)
        self.spinToleranciaMomento.setSingleStep(0.100000000000000)
        self.spinToleranciaMomento.setValue(0.000001000000000)

        self.spinToleranciaMomentoFila.addWidget(self.spinToleranciaMomento)


        self.layoutPaginaSolucionador.addLayout(self.spinToleranciaMomentoFila)

        self.spinMaxIteracionesFila = QHBoxLayout()
        self.spinMaxIteracionesFila.setObjectName(u"spinMaxIteracionesFila")
        self.lblSpinMaxIteraciones = QLabel(self.contenidoScrollSolucionador)
        self.lblSpinMaxIteraciones.setObjectName(u"lblSpinMaxIteraciones")
        self.lblSpinMaxIteraciones.setWordWrap(True)

        self.spinMaxIteracionesFila.addWidget(self.lblSpinMaxIteraciones)

        self.spinMaxIteraciones = QSpinBox(self.contenidoScrollSolucionador)
        self.spinMaxIteraciones.setObjectName(u"spinMaxIteraciones")
        self.spinMaxIteraciones.setMinimum(1)
        self.spinMaxIteraciones.setMaximum(100000)
        self.spinMaxIteraciones.setValue(200)

        self.spinMaxIteracionesFila.addWidget(self.spinMaxIteraciones)


        self.layoutPaginaSolucionador.addLayout(self.spinMaxIteracionesFila)

        self.chkPararNoConvergencia = QCheckBox(self.contenidoScrollSolucionador)
        self.chkPararNoConvergencia.setObjectName(u"chkPararNoConvergencia")
        self.chkPararNoConvergencia.setChecked(True)

        self.layoutPaginaSolucionador.addWidget(self.chkPararNoConvergencia)

        self.chkInformarResultadosIndeterminados = QCheckBox(self.contenidoScrollSolucionador)
        self.chkInformarResultadosIndeterminados.setObjectName(u"chkInformarResultadosIndeterminados")
        self.chkInformarResultadosIndeterminados.setChecked(True)

        self.layoutPaginaSolucionador.addWidget(self.chkInformarResultadosIndeterminados)

        self.chkGuardarDiagnosticos = QCheckBox(self.contenidoScrollSolucionador)
        self.chkGuardarDiagnosticos.setObjectName(u"chkGuardarDiagnosticos")
        self.chkGuardarDiagnosticos.setChecked(True)

        self.layoutPaginaSolucionador.addWidget(self.chkGuardarDiagnosticos)

        self.espacioSolucionador = QSpacerItem(20, 24, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layoutPaginaSolucionador.addItem(self.espacioSolucionador)

        self.scrollPaginaSolucionador.setWidget(self.contenidoScrollSolucionador)

        self.layoutScrollSolucionador.addWidget(self.scrollPaginaSolucionador)

        self.stackConfiguracion.addWidget(self.pageSolucionador)

        self.layoutSelectorParametros.addWidget(self.stackConfiguracion)


        self.layoutPanelConfiguracionDinamica.addLayout(self.layoutSelectorParametros)

        self.splitConfiguracionYResultados.addWidget(self.panelConfiguracionDinamica)
        self.panelGraficasDinamicas = QWidget(self.splitConfiguracionYResultados)
        self.panelGraficasDinamicas.setObjectName(u"panelGraficasDinamicas")
        self.layoutPanelGraficasDinamicas = QVBoxLayout(self.panelGraficasDinamicas)
        self.layoutPanelGraficasDinamicas.setObjectName(u"layoutPanelGraficasDinamicas")
        self.layoutPanelGraficasDinamicas.setContentsMargins(0, 0, 0, 0)
        self.lblTituloGraficasEstudio = QLabel(self.panelGraficasDinamicas)
        self.lblTituloGraficasEstudio.setObjectName(u"lblTituloGraficasEstudio")

        self.layoutPanelGraficasDinamicas.addWidget(self.lblTituloGraficasEstudio)

        self.tabGraficasEstudio = QTabWidget(self.panelGraficasDinamicas)
        self.tabGraficasEstudio.setObjectName(u"tabGraficasEstudio")
        self.tabParTiempo = QWidget()
        self.tabParTiempo.setObjectName(u"tabParTiempo")
        self.layoutTabParTiempo = QVBoxLayout(self.tabParTiempo)
        self.layoutTabParTiempo.setObjectName(u"layoutTabParTiempo")
        self.widgetGraficaTabParTiempo = QWidget(self.tabParTiempo)
        self.widgetGraficaTabParTiempo.setObjectName(u"widgetGraficaTabParTiempo")
        self.widgetGraficaTabParTiempo.setMinimumSize(QSize(100, 400))

        self.layoutTabParTiempo.addWidget(self.widgetGraficaTabParTiempo)

        self.layoutVisibilidadTabParTiempo = QHBoxLayout()
        self.layoutVisibilidadTabParTiempo.setObjectName(u"layoutVisibilidadTabParTiempo")
        self.chkMostrarPrescritaTabParTiempo = QCheckBox(self.tabParTiempo)
        self.chkMostrarPrescritaTabParTiempo.setObjectName(u"chkMostrarPrescritaTabParTiempo")
        self.chkMostrarPrescritaTabParTiempo.setChecked(True)

        self.layoutVisibilidadTabParTiempo.addWidget(self.chkMostrarPrescritaTabParTiempo)

        self.chkMostrarCalculadaTabParTiempo = QCheckBox(self.tabParTiempo)
        self.chkMostrarCalculadaTabParTiempo.setObjectName(u"chkMostrarCalculadaTabParTiempo")
        self.chkMostrarCalculadaTabParTiempo.setChecked(True)

        self.layoutVisibilidadTabParTiempo.addWidget(self.chkMostrarCalculadaTabParTiempo)


        self.layoutTabParTiempo.addLayout(self.layoutVisibilidadTabParTiempo)

        self.tabGraficasEstudio.addTab(self.tabParTiempo, "")
        self.tabParAngulo = QWidget()
        self.tabParAngulo.setObjectName(u"tabParAngulo")
        self.layoutTabParAngulo = QVBoxLayout(self.tabParAngulo)
        self.layoutTabParAngulo.setObjectName(u"layoutTabParAngulo")
        self.widgetGraficaTabParAngulo = QWidget(self.tabParAngulo)
        self.widgetGraficaTabParAngulo.setObjectName(u"widgetGraficaTabParAngulo")
        self.widgetGraficaTabParAngulo.setMinimumSize(QSize(100, 400))

        self.layoutTabParAngulo.addWidget(self.widgetGraficaTabParAngulo)

        self.layoutVisibilidadTabParAngulo = QHBoxLayout()
        self.layoutVisibilidadTabParAngulo.setObjectName(u"layoutVisibilidadTabParAngulo")
        self.chkMostrarPrescritaTabParAngulo = QCheckBox(self.tabParAngulo)
        self.chkMostrarPrescritaTabParAngulo.setObjectName(u"chkMostrarPrescritaTabParAngulo")
        self.chkMostrarPrescritaTabParAngulo.setChecked(True)

        self.layoutVisibilidadTabParAngulo.addWidget(self.chkMostrarPrescritaTabParAngulo)

        self.chkMostrarCalculadaTabParAngulo = QCheckBox(self.tabParAngulo)
        self.chkMostrarCalculadaTabParAngulo.setObjectName(u"chkMostrarCalculadaTabParAngulo")
        self.chkMostrarCalculadaTabParAngulo.setChecked(True)

        self.layoutVisibilidadTabParAngulo.addWidget(self.chkMostrarCalculadaTabParAngulo)


        self.layoutTabParAngulo.addLayout(self.layoutVisibilidadTabParAngulo)

        self.tabGraficasEstudio.addTab(self.tabParAngulo, "")
        self.tabParVelocidad = QWidget()
        self.tabParVelocidad.setObjectName(u"tabParVelocidad")
        self.layoutTabParVelocidad = QVBoxLayout(self.tabParVelocidad)
        self.layoutTabParVelocidad.setObjectName(u"layoutTabParVelocidad")
        self.widgetGraficaTabParVelocidad = QWidget(self.tabParVelocidad)
        self.widgetGraficaTabParVelocidad.setObjectName(u"widgetGraficaTabParVelocidad")
        self.widgetGraficaTabParVelocidad.setMinimumSize(QSize(100, 400))

        self.layoutTabParVelocidad.addWidget(self.widgetGraficaTabParVelocidad)

        self.layoutVisibilidadTabParVelocidad = QHBoxLayout()
        self.layoutVisibilidadTabParVelocidad.setObjectName(u"layoutVisibilidadTabParVelocidad")
        self.chkMostrarPrescritaTabParVelocidad = QCheckBox(self.tabParVelocidad)
        self.chkMostrarPrescritaTabParVelocidad.setObjectName(u"chkMostrarPrescritaTabParVelocidad")
        self.chkMostrarPrescritaTabParVelocidad.setChecked(True)

        self.layoutVisibilidadTabParVelocidad.addWidget(self.chkMostrarPrescritaTabParVelocidad)

        self.chkMostrarCalculadaTabParVelocidad = QCheckBox(self.tabParVelocidad)
        self.chkMostrarCalculadaTabParVelocidad.setObjectName(u"chkMostrarCalculadaTabParVelocidad")
        self.chkMostrarCalculadaTabParVelocidad.setChecked(True)

        self.layoutVisibilidadTabParVelocidad.addWidget(self.chkMostrarCalculadaTabParVelocidad)


        self.layoutTabParVelocidad.addLayout(self.layoutVisibilidadTabParVelocidad)

        self.tabGraficasEstudio.addTab(self.tabParVelocidad, "")
        self.tabResultadosDinamicos = QWidget()
        self.tabResultadosDinamicos.setObjectName(u"tabResultadosDinamicos")
        self.layoutResultadosDinamicos = QVBoxLayout(self.tabResultadosDinamicos)
        self.layoutResultadosDinamicos.setObjectName(u"layoutResultadosDinamicos")
        self.tabTipoResultado = QTabWidget(self.tabResultadosDinamicos)
        self.tabTipoResultado.setObjectName(u"tabTipoResultado")
        self.tabFuerzasContacto = QWidget()
        self.tabFuerzasContacto.setObjectName(u"tabFuerzasContacto")
        self.layoutTabFuerzasContacto = QVBoxLayout(self.tabFuerzasContacto)
        self.layoutTabFuerzasContacto.setObjectName(u"layoutTabFuerzasContacto")
        self.widgetGraficaTabFuerzasContacto = QWidget(self.tabFuerzasContacto)
        self.widgetGraficaTabFuerzasContacto.setObjectName(u"widgetGraficaTabFuerzasContacto")
        self.widgetGraficaTabFuerzasContacto.setMinimumSize(QSize(100, 400))

        self.layoutTabFuerzasContacto.addWidget(self.widgetGraficaTabFuerzasContacto)

        self.tablaTabFuerzasContacto = QTableWidget(self.tabFuerzasContacto)
        if (self.tablaTabFuerzasContacto.columnCount() < 5):
            self.tablaTabFuerzasContacto.setColumnCount(5)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tablaTabFuerzasContacto.setHorizontalHeaderItem(0, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tablaTabFuerzasContacto.setHorizontalHeaderItem(1, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tablaTabFuerzasContacto.setHorizontalHeaderItem(2, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tablaTabFuerzasContacto.setHorizontalHeaderItem(3, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tablaTabFuerzasContacto.setHorizontalHeaderItem(4, __qtablewidgetitem11)
        self.tablaTabFuerzasContacto.setObjectName(u"tablaTabFuerzasContacto")
        self.tablaTabFuerzasContacto.setMinimumSize(QSize(0, 135))

        self.layoutTabFuerzasContacto.addWidget(self.tablaTabFuerzasContacto)

        self.tabTipoResultado.addTab(self.tabFuerzasContacto, "")
        self.tabMomentos = QWidget()
        self.tabMomentos.setObjectName(u"tabMomentos")
        self.layoutTabMomentos = QVBoxLayout(self.tabMomentos)
        self.layoutTabMomentos.setObjectName(u"layoutTabMomentos")
        self.widgetGraficaTabMomentos = QWidget(self.tabMomentos)
        self.widgetGraficaTabMomentos.setObjectName(u"widgetGraficaTabMomentos")
        self.widgetGraficaTabMomentos.setMinimumSize(QSize(100, 400))

        self.layoutTabMomentos.addWidget(self.widgetGraficaTabMomentos)

        self.tablaTabMomentos = QTableWidget(self.tabMomentos)
        if (self.tablaTabMomentos.columnCount() < 4):
            self.tablaTabMomentos.setColumnCount(4)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tablaTabMomentos.setHorizontalHeaderItem(0, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.tablaTabMomentos.setHorizontalHeaderItem(1, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.tablaTabMomentos.setHorizontalHeaderItem(2, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.tablaTabMomentos.setHorizontalHeaderItem(3, __qtablewidgetitem15)
        self.tablaTabMomentos.setObjectName(u"tablaTabMomentos")
        self.tablaTabMomentos.setMinimumSize(QSize(0, 135))

        self.layoutTabMomentos.addWidget(self.tablaTabMomentos)

        self.tabTipoResultado.addTab(self.tabMomentos, "")
        self.tabEventos = QWidget()
        self.tabEventos.setObjectName(u"tabEventos")
        self.layoutTabEventos = QVBoxLayout(self.tabEventos)
        self.layoutTabEventos.setObjectName(u"layoutTabEventos")
        self.widgetGraficaTabEventos = QWidget(self.tabEventos)
        self.widgetGraficaTabEventos.setObjectName(u"widgetGraficaTabEventos")
        self.widgetGraficaTabEventos.setMinimumSize(QSize(100, 400))

        self.layoutTabEventos.addWidget(self.widgetGraficaTabEventos)

        self.tablaTabEventos = QTableWidget(self.tabEventos)
        if (self.tablaTabEventos.columnCount() < 4):
            self.tablaTabEventos.setColumnCount(4)
        __qtablewidgetitem16 = QTableWidgetItem()
        self.tablaTabEventos.setHorizontalHeaderItem(0, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        self.tablaTabEventos.setHorizontalHeaderItem(1, __qtablewidgetitem17)
        __qtablewidgetitem18 = QTableWidgetItem()
        self.tablaTabEventos.setHorizontalHeaderItem(2, __qtablewidgetitem18)
        __qtablewidgetitem19 = QTableWidgetItem()
        self.tablaTabEventos.setHorizontalHeaderItem(3, __qtablewidgetitem19)
        self.tablaTabEventos.setObjectName(u"tablaTabEventos")
        self.tablaTabEventos.setMinimumSize(QSize(0, 135))

        self.layoutTabEventos.addWidget(self.tablaTabEventos)

        self.tabTipoResultado.addTab(self.tabEventos, "")

        self.layoutResultadosDinamicos.addWidget(self.tabTipoResultado)

        self.tabGraficasEstudio.addTab(self.tabResultadosDinamicos, "")
        self.tabDiagnosticos = QWidget()
        self.tabDiagnosticos.setObjectName(u"tabDiagnosticos")
        self.layoutDiagnosticos = QVBoxLayout(self.tabDiagnosticos)
        self.layoutDiagnosticos.setObjectName(u"layoutDiagnosticos")
        self.widgetGraficaDiagnostico = QWidget(self.tabDiagnosticos)
        self.widgetGraficaDiagnostico.setObjectName(u"widgetGraficaDiagnostico")
        self.widgetGraficaDiagnostico.setMinimumSize(QSize(100, 400))

        self.layoutDiagnosticos.addWidget(self.widgetGraficaDiagnostico)

        self.tablaDiagnosticoEstudio = QTableWidget(self.tabDiagnosticos)
        if (self.tablaDiagnosticoEstudio.columnCount() < 4):
            self.tablaDiagnosticoEstudio.setColumnCount(4)
        __qtablewidgetitem20 = QTableWidgetItem()
        self.tablaDiagnosticoEstudio.setHorizontalHeaderItem(0, __qtablewidgetitem20)
        __qtablewidgetitem21 = QTableWidgetItem()
        self.tablaDiagnosticoEstudio.setHorizontalHeaderItem(1, __qtablewidgetitem21)
        __qtablewidgetitem22 = QTableWidgetItem()
        self.tablaDiagnosticoEstudio.setHorizontalHeaderItem(2, __qtablewidgetitem22)
        __qtablewidgetitem23 = QTableWidgetItem()
        self.tablaDiagnosticoEstudio.setHorizontalHeaderItem(3, __qtablewidgetitem23)
        self.tablaDiagnosticoEstudio.setObjectName(u"tablaDiagnosticoEstudio")
        self.tablaDiagnosticoEstudio.setMinimumSize(QSize(0, 145))

        self.layoutDiagnosticos.addWidget(self.tablaDiagnosticoEstudio)

        self.tabGraficasEstudio.addTab(self.tabDiagnosticos, "")

        self.layoutPanelGraficasDinamicas.addWidget(self.tabGraficasEstudio)

        self.splitConfiguracionYResultados.addWidget(self.panelGraficasDinamicas)

        self.layoutDinamicoPrincipal.addWidget(self.splitConfiguracionYResultados)

        self.layoutAccionesEstudio = QHBoxLayout()
        self.layoutAccionesEstudio.setObjectName(u"layoutAccionesEstudio")
        self.lblEstadoEstudio = QLabel(self.tabDinamico)
        self.lblEstadoEstudio.setObjectName(u"lblEstadoEstudio")

        self.layoutAccionesEstudio.addWidget(self.lblEstadoEstudio)

        self.progressEstudio = QProgressBar(self.tabDinamico)
        self.progressEstudio.setObjectName(u"progressEstudio")
        self.progressEstudio.setMaximumSize(QSize(170, 16777215))
        self.progressEstudio.setValue(0)

        self.layoutAccionesEstudio.addWidget(self.progressEstudio)

        self.btnEjecutarEstudio = QPushButton(self.tabDinamico)
        self.btnEjecutarEstudio.setObjectName(u"btnEjecutarEstudio")
        self.btnEjecutarEstudio.setEnabled(False)

        self.layoutAccionesEstudio.addWidget(self.btnEjecutarEstudio)

        self.btnCancelarEstudio = QPushButton(self.tabDinamico)
        self.btnCancelarEstudio.setObjectName(u"btnCancelarEstudio")
        self.btnCancelarEstudio.setEnabled(False)

        self.layoutAccionesEstudio.addWidget(self.btnCancelarEstudio)

        self.btnVerResultados = QPushButton(self.tabDinamico)
        self.btnVerResultados.setObjectName(u"btnVerResultados")
        self.btnVerResultados.setEnabled(False)

        self.layoutAccionesEstudio.addWidget(self.btnVerResultados)

        self.btnExportarResultadosEstudio = QPushButton(self.tabDinamico)
        self.btnExportarResultadosEstudio.setObjectName(u"btnExportarResultadosEstudio")
        self.btnExportarResultadosEstudio.setEnabled(False)

        self.layoutAccionesEstudio.addWidget(self.btnExportarResultadosEstudio)


        self.layoutDinamicoPrincipal.addLayout(self.layoutAccionesEstudio)

        self.tabRegimenes.addTab(self.tabDinamico, "")

        self.layoutEditorRegimenes.addWidget(self.tabRegimenes)

        self.layoutAceptarCancelarEditor = QHBoxLayout()
        self.layoutAceptarCancelarEditor.setObjectName(u"layoutAceptarCancelarEditor")
        self.espacioBotonesFinales = QSpacerItem(20, 24, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layoutAceptarCancelarEditor.addItem(self.espacioBotonesFinales)

        self.pushButton_10 = QPushButton(self.centralwidget)
        self.pushButton_10.setObjectName(u"pushButton_10")

        self.layoutAceptarCancelarEditor.addWidget(self.pushButton_10)

        self.pushButton_9 = QPushButton(self.centralwidget)
        self.pushButton_9.setObjectName(u"pushButton_9")

        self.layoutAceptarCancelarEditor.addWidget(self.pushButton_9)


        self.layoutEditorRegimenes.addLayout(self.layoutAceptarCancelarEditor)

        GiroImpuesto_window.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(GiroImpuesto_window)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1370, 33))
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
        self.listSeccionesEstudio.currentRowChanged.connect(self.stackConfiguracion.setCurrentIndex)

        self.tabRegimenes.setCurrentIndex(0)
        self.stackedWidget.setCurrentIndex(4)
        self.listSeccionesEstudio.setCurrentRow(0)
        self.stackConfiguracion.setCurrentIndex(0)
        self.tabGraficasEstudio.setCurrentIndex(0)
        self.tabTipoResultado.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(GiroImpuesto_window)
    # setupUi

    def retranslateUi(self, GiroImpuesto_window):
        GiroImpuesto_window.setWindowTitle(QCoreApplication.translate("GiroImpuesto_window", u"Editor de reg\u00edmenes de simulaci\u00f3n \u2014 RPS Design V2", None))
        self.actionAbrid.setText(QCoreApplication.translate("GiroImpuesto_window", u"Abrir", None))
        self.actionGuardar.setText(QCoreApplication.translate("GiroImpuesto_window", u"Guardar", None))
        self.actionExportar_CSV.setText(QCoreApplication.translate("GiroImpuesto_window", u"Exportar CSV", None))
        self.actionCerra.setText(QCoreApplication.translate("GiroImpuesto_window", u"Cerrar", None))
        self.actionGu_a_Tecnica.setText(QCoreApplication.translate("GiroImpuesto_window", u"Gu\u00eda Tecnica", None))
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
        self.tabRegimenes.setTabText(self.tabRegimenes.indexOf(self.tabCinematico), QCoreApplication.translate("GiroImpuesto_window", u"R\u00e9gimen cinem\u00e1tico", None))
        self.groupEstudioActivo.setTitle(QCoreApplication.translate("GiroImpuesto_window", u"Estudio f\u00edsico asociado al perfil", None))
        self.lblEscenarioPreset.setText(QCoreApplication.translate("GiroImpuesto_window", u"Escenario:", None))
        self.comboEscenarioDinamico.setItemText(0, QCoreApplication.translate("GiroImpuesto_window", u"Personalizado (sin carga externa)", None))
        self.comboEscenarioDinamico.setItemText(1, QCoreApplication.translate("GiroImpuesto_window", u"Escenario asociado al preset", None))
        self.comboEscenarioDinamico.setItemText(2, QCoreApplication.translate("GiroImpuesto_window", u"Nuevo escenario\u2026", None))

#if QT_CONFIG(tooltip)
        self.btnGuardarEscenario.setToolTip(QCoreApplication.translate("GiroImpuesto_window", u"Guardar configuraci\u00f3n del estudio; conectar desde Python.", None))
#endif // QT_CONFIG(tooltip)
        self.btnGuardarEscenario.setText(QCoreApplication.translate("GiroImpuesto_window", u"Guardar escenario\u2026", None))
#if QT_CONFIG(tooltip)
        self.btnRestaurarEscenario.setToolTip(QCoreApplication.translate("GiroImpuesto_window", u"Pendiente de implementaci\u00f3n en Python.", None))
#endif // QT_CONFIG(tooltip)
        self.btnRestaurarEscenario.setText(QCoreApplication.translate("GiroImpuesto_window", u"Restablecer", None))
        self.lblSubtituloConfig.setText(QCoreApplication.translate("GiroImpuesto_window", u"Configuraci\u00f3n del estudio", None))

        __sortingEnabled = self.listSeccionesEstudio.isSortingEnabled()
        self.listSeccionesEstudio.setSortingEnabled(False)
        ___qlistwidgetitem = self.listSeccionesEstudio.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("GiroImpuesto_window", u"Accionamiento", None))
        ___qlistwidgetitem1 = self.listSeccionesEstudio.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("GiroImpuesto_window", u"Cargas externas", None))
        ___qlistwidgetitem2 = self.listSeccionesEstudio.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("GiroImpuesto_window", u"Contacto", None))
        ___qlistwidgetitem3 = self.listSeccionesEstudio.item(3)
        ___qlistwidgetitem3.setText(QCoreApplication.translate("GiroImpuesto_window", u"Solucionador", None))
        self.listSeccionesEstudio.setSortingEnabled(__sortingEnabled)

        self.lblComboTipoMotor.setText(QCoreApplication.translate("GiroImpuesto_window", u"Tipo de motor", None))
        self.comboTipoMotor.setItemText(0, QCoreApplication.translate("GiroImpuesto_window", u"Stepper", None))
        self.comboTipoMotor.setItemText(1, QCoreApplication.translate("GiroImpuesto_window", u"AC \u2014 4 polos, 50 Hz (1500 rpm s\u00edncronas)", None))
        self.comboTipoMotor.setItemText(2, QCoreApplication.translate("GiroImpuesto_window", u"Custom \u2014 parametrizaci\u00f3n obligatoria", None))

        self.lblSpinPotenciaNominal.setText(QCoreApplication.translate("GiroImpuesto_window", u"Potencia mec\u00e1nica nominal", None))
        self.spinPotenciaNominal.setSuffix(QCoreApplication.translate("GiroImpuesto_window", u" W", None))
        self.lblSpinParRetencion.setText(QCoreApplication.translate("GiroImpuesto_window", u"Par de retenci\u00f3n (Stepper)", None))
        self.spinParRetencion.setSuffix(QCoreApplication.translate("GiroImpuesto_window", u" N\u00b7m", None))
        self.lblSpinFrecuenciaRed.setText(QCoreApplication.translate("GiroImpuesto_window", u"Frecuencia de red (AC)", None))
        self.spinFrecuenciaRed.setSuffix(QCoreApplication.translate("GiroImpuesto_window", u" Hz", None))
        self.lblSpinNumeroPolos.setText(QCoreApplication.translate("GiroImpuesto_window", u"N\u00famero de polos (AC)", None))
        self.groupCurvaCaracteristica.setTitle(QCoreApplication.translate("GiroImpuesto_window", u"Curva par\u2013velocidad del motor", None))
        ___qtablewidgetitem = self.tablaCurvaMotor.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("GiroImpuesto_window", u"Velocidad (rpm)", None))
        ___qtablewidgetitem1 = self.tablaCurvaMotor.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("GiroImpuesto_window", u"Par disponible (N\u00b7m)", None))
        self.btnAgregarPuntoMotor.setText(QCoreApplication.translate("GiroImpuesto_window", u"+ Punto", None))
        self.btnQuitarPuntoMotor.setText(QCoreApplication.translate("GiroImpuesto_window", u"\u2212 Punto", None))
        self.btnImportarCurvaMotor.setText(QCoreApplication.translate("GiroImpuesto_window", u"Importar CSV\u2026", None))
        self.lblTituloCargas.setText(QCoreApplication.translate("GiroImpuesto_window", u"Cargas externas \u00b7 perfiles editables", None))
        self.lblComboDependenciaPar.setText(QCoreApplication.translate("GiroImpuesto_window", u"Variable independiente", None))
        self.comboDependenciaPar.setItemText(0, QCoreApplication.translate("GiroImpuesto_window", u"Tiempo \u2014 T(t)", None))
        self.comboDependenciaPar.setItemText(1, QCoreApplication.translate("GiroImpuesto_window", u"Posici\u00f3n angular \u2014 T(\u03b8)", None))
        self.comboDependenciaPar.setItemText(2, QCoreApplication.translate("GiroImpuesto_window", u"Velocidad angular \u2014 T(\u03c9)", None))

        self.lblComboTipoLeyCarga.setText(QCoreApplication.translate("GiroImpuesto_window", u"Ley del perfil", None))
        self.comboTipoLeyCarga.setItemText(0, QCoreApplication.translate("GiroImpuesto_window", u"Constante", None))
        self.comboTipoLeyCarga.setItemText(1, QCoreApplication.translate("GiroImpuesto_window", u"Rampa lineal", None))
        self.comboTipoLeyCarga.setItemText(2, QCoreApplication.translate("GiroImpuesto_window", u"Rampa c\u00fabica", None))
        self.comboTipoLeyCarga.setItemText(3, QCoreApplication.translate("GiroImpuesto_window", u"Cicloidal", None))
        self.comboTipoLeyCarga.setItemText(4, QCoreApplication.translate("GiroImpuesto_window", u"Arm\u00f3nica", None))
        self.comboTipoLeyCarga.setItemText(5, QCoreApplication.translate("GiroImpuesto_window", u"Sinusoidal", None))
        self.comboTipoLeyCarga.setItemText(6, QCoreApplication.translate("GiroImpuesto_window", u"Sinusoidal modificada", None))
        self.comboTipoLeyCarga.setItemText(7, QCoreApplication.translate("GiroImpuesto_window", u"Polin\u00f3mica", None))
        self.comboTipoLeyCarga.setItemText(8, QCoreApplication.translate("GiroImpuesto_window", u"Lista de puntos", None))
        self.comboTipoLeyCarga.setItemText(9, QCoreApplication.translate("GiroImpuesto_window", u"Spline", None))
        self.comboTipoLeyCarga.setItemText(10, QCoreApplication.translate("GiroImpuesto_window", u"Trapezoidal modificada", None))

        self.lblComboComponenteCarga.setText(QCoreApplication.translate("GiroImpuesto_window", u"Aplicaci\u00f3n de carga", None))
        self.comboComponenteCarga.setItemText(0, QCoreApplication.translate("GiroImpuesto_window", u"Componente de salida", None))
        self.comboComponenteCarga.setItemText(1, QCoreApplication.translate("GiroImpuesto_window", u"Eje de entrada", None))
        self.comboComponenteCarga.setItemText(2, QCoreApplication.translate("GiroImpuesto_window", u"Seleccionar componente\u2026", None))

        self.lblSpinParResistente.setText(QCoreApplication.translate("GiroImpuesto_window", u"Par resistente constante", None))
        self.spinParResistente.setSuffix(QCoreApplication.translate("GiroImpuesto_window", u" N\u00b7m", None))
        ___qtablewidgetitem2 = self.tablaPuntosCarga.horizontalHeaderItem(0)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("GiroImpuesto_window", u"Abscisa (t, \u03b8 o \u03c9)", None))
        ___qtablewidgetitem3 = self.tablaPuntosCarga.horizontalHeaderItem(1)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("GiroImpuesto_window", u"Par (N\u00b7m)", None))
        self.btnAgregarPuntoCarga.setText(QCoreApplication.translate("GiroImpuesto_window", u"+ Punto", None))
        self.btnQuitarPuntoCarga.setText(QCoreApplication.translate("GiroImpuesto_window", u"\u2212 Punto", None))
        self.btnImportarCarga.setText(QCoreApplication.translate("GiroImpuesto_window", u"Importar\u2026", None))
        self.lblComboModeloContacto.setText(QCoreApplication.translate("GiroImpuesto_window", u"Formulaci\u00f3n normal", None))
        self.comboModeloContacto.setItemText(0, QCoreApplication.translate("GiroImpuesto_window", u"Equilibrio unilateral / complementariedad", None))
        self.comboModeloContacto.setItemText(1, QCoreApplication.translate("GiroImpuesto_window", u"Penalizaci\u00f3n el\u00e1stica unilateral", None))
        self.comboModeloContacto.setItemText(2, QCoreApplication.translate("GiroImpuesto_window", u"Solo an\u00e1lisis geom\u00e9trico", None))

        self.lblSpinRigidezNormal.setText(QCoreApplication.translate("GiroImpuesto_window", u"Rigidez normal equivalente", None))
        self.spinRigidezNormal.setSuffix(QCoreApplication.translate("GiroImpuesto_window", u" N/mm", None))
        self.lblSpinToleranciaBrecha.setText(QCoreApplication.translate("GiroImpuesto_window", u"Tolerancia geom\u00e9trica de brecha", None))
        self.spinToleranciaBrecha.setSuffix(QCoreApplication.translate("GiroImpuesto_window", u" mm", None))
        self.chkRepartoMulticontacto.setText(QCoreApplication.translate("GiroImpuesto_window", u"Resolver reparto entre contactos activos", None))
        self.chkRegistrarContactos.setText(QCoreApplication.translate("GiroImpuesto_window", u"Registrar todos los contactos y sus normales", None))
        self.chkIncluirFriccion.setText(QCoreApplication.translate("GiroImpuesto_window", u"Fricci\u00f3n tangencial (pendiente de modelo)", None))
        self.lblSpinAmortiguamientoNormal.setText(QCoreApplication.translate("GiroImpuesto_window", u"Amortiguamiento normal (transitorio)", None))
        self.spinAmortiguamientoNormal.setSuffix(QCoreApplication.translate("GiroImpuesto_window", u" N\u00b7s/mm", None))
        self.groupComponentesEstudio.setTitle(QCoreApplication.translate("GiroImpuesto_window", u"Componentes y restricciones", None))
        ___qtablewidgetitem4 = self.tablaComponentesContacto.horizontalHeaderItem(0)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("GiroImpuesto_window", u"Componente", None))
        ___qtablewidgetitem5 = self.tablaComponentesContacto.horizontalHeaderItem(1)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("GiroImpuesto_window", u"V\u00ednculo", None))
        ___qtablewidgetitem6 = self.tablaComponentesContacto.horizontalHeaderItem(2)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("GiroImpuesto_window", u"Contactos activos", None))
        self.lblTituloSolucionador.setText(QCoreApplication.translate("GiroImpuesto_window", u"Resoluci\u00f3n \u00b7 precisi\u00f3n y diagn\u00f3stico", None))
        self.lblComboMetodoSolucion.setText(QCoreApplication.translate("GiroImpuesto_window", u"M\u00e9todo", None))
        self.comboMetodoSolucion.setItemText(0, QCoreApplication.translate("GiroImpuesto_window", u"Equilibrio cuasiest\u00e1tico por posici\u00f3n", None))

        self.lblComboMuestreoEstudio.setText(QCoreApplication.translate("GiroImpuesto_window", u"Discretizaci\u00f3n", None))
        self.comboMuestreoEstudio.setItemText(0, QCoreApplication.translate("GiroImpuesto_window", u"Usar estrategia de Ajustes", None))
        self.comboMuestreoEstudio.setItemText(1, QCoreApplication.translate("GiroImpuesto_window", u"Uniforme por muestras", None))
        self.comboMuestreoEstudio.setItemText(2, QCoreApplication.translate("GiroImpuesto_window", u"Adaptativa por tolerancia", None))

        self.lblSpinToleranciaEquilibrio.setText(QCoreApplication.translate("GiroImpuesto_window", u"Tolerancia de equilibrio", None))
        self.spinToleranciaEquilibrio.setSuffix(QCoreApplication.translate("GiroImpuesto_window", u" N", None))
        self.lblSpinToleranciaMomento.setText(QCoreApplication.translate("GiroImpuesto_window", u"Tolerancia de momento", None))
        self.spinToleranciaMomento.setSuffix(QCoreApplication.translate("GiroImpuesto_window", u" N\u00b7mm", None))
        self.lblSpinMaxIteraciones.setText(QCoreApplication.translate("GiroImpuesto_window", u"M\u00e1ximo de iteraciones", None))
        self.chkPararNoConvergencia.setText(QCoreApplication.translate("GiroImpuesto_window", u"Detener ante falta de convergencia", None))
        self.chkInformarResultadosIndeterminados.setText(QCoreApplication.translate("GiroImpuesto_window", u"Identificar estados f\u00edsicamente indeterminados", None))
        self.chkGuardarDiagnosticos.setText(QCoreApplication.translate("GiroImpuesto_window", u"Registrar residuos de equilibrio", None))
        self.lblTituloGraficasEstudio.setText(QCoreApplication.translate("GiroImpuesto_window", u"Gr\u00e1ficas y resultados del estudio", None))
#if QT_CONFIG(tooltip)
        self.widgetGraficaTabParTiempo.setToolTip(QCoreApplication.translate("GiroImpuesto_window", u"Contenedor para PlotWidget de PyQtGraph: crear e insertar desde Python.", None))
#endif // QT_CONFIG(tooltip)
        self.chkMostrarPrescritaTabParTiempo.setText(QCoreApplication.translate("GiroImpuesto_window", u"Perfil impuesto", None))
        self.chkMostrarCalculadaTabParTiempo.setText(QCoreApplication.translate("GiroImpuesto_window", u"Resultado calculado", None))
        self.tabGraficasEstudio.setTabText(self.tabGraficasEstudio.indexOf(self.tabParTiempo), QCoreApplication.translate("GiroImpuesto_window", u"T(t)", None))
#if QT_CONFIG(tooltip)
        self.widgetGraficaTabParAngulo.setToolTip(QCoreApplication.translate("GiroImpuesto_window", u"Contenedor para PlotWidget de PyQtGraph: crear e insertar desde Python.", None))
#endif // QT_CONFIG(tooltip)
        self.chkMostrarPrescritaTabParAngulo.setText(QCoreApplication.translate("GiroImpuesto_window", u"Perfil impuesto", None))
        self.chkMostrarCalculadaTabParAngulo.setText(QCoreApplication.translate("GiroImpuesto_window", u"Resultado calculado", None))
        self.tabGraficasEstudio.setTabText(self.tabGraficasEstudio.indexOf(self.tabParAngulo), QCoreApplication.translate("GiroImpuesto_window", u"T(\u03b8)", None))
#if QT_CONFIG(tooltip)
        self.widgetGraficaTabParVelocidad.setToolTip(QCoreApplication.translate("GiroImpuesto_window", u"Contenedor para PlotWidget de PyQtGraph: crear e insertar desde Python.", None))
#endif // QT_CONFIG(tooltip)
        self.chkMostrarPrescritaTabParVelocidad.setText(QCoreApplication.translate("GiroImpuesto_window", u"Perfil impuesto", None))
        self.chkMostrarCalculadaTabParVelocidad.setText(QCoreApplication.translate("GiroImpuesto_window", u"Resultado calculado", None))
        self.tabGraficasEstudio.setTabText(self.tabGraficasEstudio.indexOf(self.tabParVelocidad), QCoreApplication.translate("GiroImpuesto_window", u"T(\u03c9)", None))
#if QT_CONFIG(tooltip)
        self.widgetGraficaTabFuerzasContacto.setToolTip(QCoreApplication.translate("GiroImpuesto_window", u"Contenedor para PlotWidget de PyQtGraph: crear e insertar desde Python.", None))
#endif // QT_CONFIG(tooltip)
        ___qtablewidgetitem7 = self.tablaTabFuerzasContacto.horizontalHeaderItem(0)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("GiroImpuesto_window", u"t (s)", None))
        ___qtablewidgetitem8 = self.tablaTabFuerzasContacto.horizontalHeaderItem(1)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("GiroImpuesto_window", u"Contacto", None))
        ___qtablewidgetitem9 = self.tablaTabFuerzasContacto.horizontalHeaderItem(2)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("GiroImpuesto_window", u"Fn (N)", None))
        ___qtablewidgetitem10 = self.tablaTabFuerzasContacto.horizontalHeaderItem(3)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("GiroImpuesto_window", u"Fr (N)", None))
        ___qtablewidgetitem11 = self.tablaTabFuerzasContacto.horizontalHeaderItem(4)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("GiroImpuesto_window", u"Ft (N)", None))
        self.tabTipoResultado.setTabText(self.tabTipoResultado.indexOf(self.tabFuerzasContacto), QCoreApplication.translate("GiroImpuesto_window", u"Fuerzas", None))
#if QT_CONFIG(tooltip)
        self.widgetGraficaTabMomentos.setToolTip(QCoreApplication.translate("GiroImpuesto_window", u"Contenedor para PlotWidget de PyQtGraph: crear e insertar desde Python.", None))
#endif // QT_CONFIG(tooltip)
        ___qtablewidgetitem12 = self.tablaTabMomentos.horizontalHeaderItem(0)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("GiroImpuesto_window", u"t (s)", None))
        ___qtablewidgetitem13 = self.tablaTabMomentos.horizontalHeaderItem(1)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("GiroImpuesto_window", u"Componente", None))
        ___qtablewidgetitem14 = self.tablaTabMomentos.horizontalHeaderItem(2)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("GiroImpuesto_window", u"T (N\u00b7m)", None))
        ___qtablewidgetitem15 = self.tablaTabMomentos.horizontalHeaderItem(3)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("GiroImpuesto_window", u"Estado", None))
        self.tabTipoResultado.setTabText(self.tabTipoResultado.indexOf(self.tabMomentos), QCoreApplication.translate("GiroImpuesto_window", u"Momentos", None))
#if QT_CONFIG(tooltip)
        self.widgetGraficaTabEventos.setToolTip(QCoreApplication.translate("GiroImpuesto_window", u"Contenedor para PlotWidget de PyQtGraph: crear e insertar desde Python.", None))
#endif // QT_CONFIG(tooltip)
        ___qtablewidgetitem16 = self.tablaTabEventos.horizontalHeaderItem(0)
        ___qtablewidgetitem16.setText(QCoreApplication.translate("GiroImpuesto_window", u"t (s)", None))
        ___qtablewidgetitem17 = self.tablaTabEventos.horizontalHeaderItem(1)
        ___qtablewidgetitem17.setText(QCoreApplication.translate("GiroImpuesto_window", u"Sistema", None))
        ___qtablewidgetitem18 = self.tablaTabEventos.horizontalHeaderItem(2)
        ___qtablewidgetitem18.setText(QCoreApplication.translate("GiroImpuesto_window", u"Evento", None))
        ___qtablewidgetitem19 = self.tablaTabEventos.horizontalHeaderItem(3)
        ___qtablewidgetitem19.setText(QCoreApplication.translate("GiroImpuesto_window", u"Diagn\u00f3stico", None))
        self.tabTipoResultado.setTabText(self.tabTipoResultado.indexOf(self.tabEventos), QCoreApplication.translate("GiroImpuesto_window", u"Eventos", None))
        self.tabGraficasEstudio.setTabText(self.tabGraficasEstudio.indexOf(self.tabResultadosDinamicos), QCoreApplication.translate("GiroImpuesto_window", u"Resultados", None))
#if QT_CONFIG(tooltip)
        self.widgetGraficaDiagnostico.setToolTip(QCoreApplication.translate("GiroImpuesto_window", u"Contenedor para PlotWidget de PyQtGraph: crear e insertar desde Python.", None))
#endif // QT_CONFIG(tooltip)
        ___qtablewidgetitem20 = self.tablaDiagnosticoEstudio.horizontalHeaderItem(0)
        ___qtablewidgetitem20.setText(QCoreApplication.translate("GiroImpuesto_window", u"Muestra", None))
        ___qtablewidgetitem21 = self.tablaDiagnosticoEstudio.horizontalHeaderItem(1)
        ___qtablewidgetitem21.setText(QCoreApplication.translate("GiroImpuesto_window", u"Resultado", None))
        ___qtablewidgetitem22 = self.tablaDiagnosticoEstudio.horizontalHeaderItem(2)
        ___qtablewidgetitem22.setText(QCoreApplication.translate("GiroImpuesto_window", u"Residuo", None))
        ___qtablewidgetitem23 = self.tablaDiagnosticoEstudio.horizontalHeaderItem(3)
        ___qtablewidgetitem23.setText(QCoreApplication.translate("GiroImpuesto_window", u"Observaci\u00f3n", None))
        self.tabGraficasEstudio.setTabText(self.tabGraficasEstudio.indexOf(self.tabDiagnosticos), QCoreApplication.translate("GiroImpuesto_window", u"Diagn\u00f3stico", None))
        self.lblEstadoEstudio.setText(QCoreApplication.translate("GiroImpuesto_window", u"Estudio no ejecutado", None))
#if QT_CONFIG(tooltip)
        self.btnEjecutarEstudio.setToolTip(QCoreApplication.translate("GiroImpuesto_window", u"Requiere enlazar los par\u00e1metros y el solucionador con Python.", None))
#endif // QT_CONFIG(tooltip)
        self.btnEjecutarEstudio.setText(QCoreApplication.translate("GiroImpuesto_window", u"Ejecutar estudio", None))
        self.btnCancelarEstudio.setText(QCoreApplication.translate("GiroImpuesto_window", u"Cancelar", None))
        self.btnVerResultados.setText(QCoreApplication.translate("GiroImpuesto_window", u"Ver resultados", None))
        self.btnExportarResultadosEstudio.setText(QCoreApplication.translate("GiroImpuesto_window", u"Exportar\u2026", None))
        self.tabRegimenes.setTabText(self.tabRegimenes.indexOf(self.tabDinamico), QCoreApplication.translate("GiroImpuesto_window", u"R\u00e9gimen din\u00e1mico / contacto", None))
        self.pushButton_10.setText(QCoreApplication.translate("GiroImpuesto_window", u"Cancelar", None))
        self.pushButton_9.setText(QCoreApplication.translate("GiroImpuesto_window", u"Aceptar", None))
        self.menuArchivo.setTitle(QCoreApplication.translate("GiroImpuesto_window", u"Archivo", None))
        self.menuAyuda.setTitle(QCoreApplication.translate("GiroImpuesto_window", u"Ayuda", None))
    # retranslateUi

