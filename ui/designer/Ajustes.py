# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ajustes.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QDoubleSpinBox, QFontComboBox, QGridLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QPushButton,
    QSizePolicy, QSlider, QSpacerItem, QSpinBox,
    QTabWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(1070, 824)
        self.gridLayout_2 = QGridLayout(Dialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.pushButton_2 = QPushButton(Dialog)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.gridLayout_2.addWidget(self.pushButton_2, 1, 2, 1, 1)

        self.pushButton_3 = QPushButton(Dialog)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.gridLayout_2.addWidget(self.pushButton_3, 1, 3, 1, 1)

        self.widget = QWidget(Dialog)
        self.widget.setObjectName(u"widget")
        self.gridLayout = QGridLayout(self.widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tabWidget = QTabWidget(self.widget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout_3 = QGridLayout(self.tab)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.groupBox = QGroupBox(self.tab)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_4 = QGridLayout(self.groupBox)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.checkBox = QCheckBox(self.groupBox)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setChecked(True)

        self.gridLayout_4.addWidget(self.checkBox, 0, 0, 1, 1)

        self.checkBox_2 = QCheckBox(self.groupBox)
        self.checkBox_2.setObjectName(u"checkBox_2")
        self.checkBox_2.setChecked(True)

        self.gridLayout_4.addWidget(self.checkBox_2, 1, 0, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox, 0, 0, 1, 1)

        self.groupBox_2 = QGroupBox(self.tab)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_5 = QGridLayout(self.groupBox_2)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.lblIntervalo = QLabel(self.groupBox_2)
        self.lblIntervalo.setObjectName(u"lblIntervalo")
        self.lblIntervalo.setWordWrap(True)

        self.gridLayout_5.addWidget(self.lblIntervalo, 1, 0, 1, 1)

        self.spinIntervaloGuardado = QSpinBox(self.groupBox_2)
        self.spinIntervaloGuardado.setObjectName(u"spinIntervaloGuardado")
        self.spinIntervaloGuardado.setMinimum(1)
        self.spinIntervaloGuardado.setMaximum(120)
        self.spinIntervaloGuardado.setSingleStep(1)
        self.spinIntervaloGuardado.setValue(5)

        self.gridLayout_5.addWidget(self.spinIntervaloGuardado, 1, 1, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_5.addItem(self.horizontalSpacer_2, 1, 2, 1, 1)

        self.chkGuardadoAuto = QCheckBox(self.groupBox_2)
        self.chkGuardadoAuto.setObjectName(u"chkGuardadoAuto")
        self.chkGuardadoAuto.setEnabled(True)
        self.chkGuardadoAuto.setChecked(False)

        self.gridLayout_5.addWidget(self.chkGuardadoAuto, 0, 0, 1, 3)

        self.chkGuardarPrefs = QCheckBox(self.groupBox_2)
        self.chkGuardarPrefs.setObjectName(u"chkGuardarPrefs")
        self.chkGuardarPrefs.setEnabled(True)
        self.chkGuardarPrefs.setChecked(True)

        self.gridLayout_5.addWidget(self.chkGuardarPrefs, 3, 0, 1, 3)


        self.gridLayout_3.addWidget(self.groupBox_2, 1, 0, 1, 1)

        self.groupBox_3 = QGroupBox(self.tab)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout_6 = QGridLayout(self.groupBox_3)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.chkAvisosDatos = QCheckBox(self.groupBox_3)
        self.chkAvisosDatos.setObjectName(u"chkAvisosDatos")
        self.chkAvisosDatos.setEnabled(True)
        self.chkAvisosDatos.setChecked(True)

        self.gridLayout_6.addWidget(self.chkAvisosDatos, 0, 0, 1, 1)

        self.chkAvisosSobrescribir = QCheckBox(self.groupBox_3)
        self.chkAvisosSobrescribir.setObjectName(u"chkAvisosSobrescribir")
        self.chkAvisosSobrescribir.setEnabled(True)
        self.chkAvisosSobrescribir.setChecked(True)

        self.gridLayout_6.addWidget(self.chkAvisosSobrescribir, 1, 0, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox_3, 2, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer, 3, 0, 1, 1)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.gridLayout_7 = QGridLayout(self.tab_2)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.groupPrecisionNumerica = QGroupBox(self.tab_2)
        self.groupPrecisionNumerica.setObjectName(u"groupPrecisionNumerica")
        self.groupPrecisionNumericaLayout = QVBoxLayout(self.groupPrecisionNumerica)
        self.groupPrecisionNumericaLayout.setSpacing(11)
        self.groupPrecisionNumericaLayout.setObjectName(u"groupPrecisionNumericaLayout")
        self.groupPrecisionNumericaLayout.setContentsMargins(14, 14, 14, 14)
        self.comboDecimalesRow = QHBoxLayout()
        self.comboDecimalesRow.setSpacing(10)
        self.comboDecimalesRow.setObjectName(u"comboDecimalesRow")
        self.comboDecimalesRow.setContentsMargins(0, 0, 0, 0)
        self.comboDecimalesLabel = QLabel(self.groupPrecisionNumerica)
        self.comboDecimalesLabel.setObjectName(u"comboDecimalesLabel")
        self.comboDecimalesLabel.setMinimumSize(QSize(172, 0))

        self.comboDecimalesRow.addWidget(self.comboDecimalesLabel)

        self.comboDecimales = QComboBox(self.groupPrecisionNumerica)
        self.comboDecimales.addItem("")
        self.comboDecimales.addItem("")
        self.comboDecimales.addItem("")
        self.comboDecimales.addItem("")
        self.comboDecimales.addItem("")
        self.comboDecimales.setObjectName(u"comboDecimales")

        self.comboDecimalesRow.addWidget(self.comboDecimales)


        self.groupPrecisionNumericaLayout.addLayout(self.comboDecimalesRow)


        self.gridLayout_7.addWidget(self.groupPrecisionNumerica, 1, 0, 1, 1)

        self.groupMuestreo = QGroupBox(self.tab_2)
        self.groupMuestreo.setObjectName(u"groupMuestreo")
        self.groupMuestreoLayout = QVBoxLayout(self.groupMuestreo)
        self.groupMuestreoLayout.setSpacing(11)
        self.groupMuestreoLayout.setObjectName(u"groupMuestreoLayout")
        self.groupMuestreoLayout.setContentsMargins(14, 14, 14, 14)
        self.comboEstrategiaMuestreoRow = QHBoxLayout()
        self.comboEstrategiaMuestreoRow.setSpacing(10)
        self.comboEstrategiaMuestreoRow.setObjectName(u"comboEstrategiaMuestreoRow")
        self.comboEstrategiaMuestreoRow.setContentsMargins(0, 0, 0, 0)
        self.comboEstrategiaMuestreoLabel = QLabel(self.groupMuestreo)
        self.comboEstrategiaMuestreoLabel.setObjectName(u"comboEstrategiaMuestreoLabel")
        self.comboEstrategiaMuestreoLabel.setMinimumSize(QSize(172, 0))

        self.comboEstrategiaMuestreoRow.addWidget(self.comboEstrategiaMuestreoLabel)

        self.comboEstrategiaMuestreo = QComboBox(self.groupMuestreo)
        self.comboEstrategiaMuestreo.addItem("")
        self.comboEstrategiaMuestreo.addItem("")
        self.comboEstrategiaMuestreo.setObjectName(u"comboEstrategiaMuestreo")

        self.comboEstrategiaMuestreoRow.addWidget(self.comboEstrategiaMuestreo)


        self.groupMuestreoLayout.addLayout(self.comboEstrategiaMuestreoRow)

        self.layoutMuestras = QHBoxLayout()
        self.layoutMuestras.setSpacing(10)
        self.layoutMuestras.setObjectName(u"layoutMuestras")
        self.layoutMuestras.setContentsMargins(0, 0, 0, 0)
        self.lblNumMuestras = QLabel(self.groupMuestreo)
        self.lblNumMuestras.setObjectName(u"lblNumMuestras")
        self.lblNumMuestras.setWordWrap(True)

        self.layoutMuestras.addWidget(self.lblNumMuestras)

        self.spinMuestras = QSpinBox(self.groupMuestreo)
        self.spinMuestras.setObjectName(u"spinMuestras")
        self.spinMuestras.setMinimum(101)
        self.spinMuestras.setMaximum(1000001)
        self.spinMuestras.setSingleStep(200)
        self.spinMuestras.setValue(2001)

        self.layoutMuestras.addWidget(self.spinMuestras)

        self.muestrasSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layoutMuestras.addItem(self.muestrasSpacer)


        self.groupMuestreoLayout.addLayout(self.layoutMuestras)

        self.layoutMaxMuestras = QHBoxLayout()
        self.layoutMaxMuestras.setSpacing(10)
        self.layoutMaxMuestras.setObjectName(u"layoutMaxMuestras")
        self.layoutMaxMuestras.setContentsMargins(0, 0, 0, 0)
        self.lblMaxMuestras = QLabel(self.groupMuestreo)
        self.lblMaxMuestras.setObjectName(u"lblMaxMuestras")
        self.lblMaxMuestras.setWordWrap(True)

        self.layoutMaxMuestras.addWidget(self.lblMaxMuestras)

        self.spinMaxMuestras = QSpinBox(self.groupMuestreo)
        self.spinMaxMuestras.setObjectName(u"spinMaxMuestras")
        self.spinMaxMuestras.setMinimum(1001)
        self.spinMaxMuestras.setMaximum(1000001)
        self.spinMaxMuestras.setSingleStep(1000)
        self.spinMaxMuestras.setValue(30001)

        self.layoutMaxMuestras.addWidget(self.spinMaxMuestras)

        self.maxMuestrasSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layoutMaxMuestras.addItem(self.maxMuestrasSpacer)


        self.groupMuestreoLayout.addLayout(self.layoutMaxMuestras)


        self.gridLayout_7.addWidget(self.groupMuestreo, 2, 0, 1, 1)

        self.groupDesviaciones = QGroupBox(self.tab_2)
        self.groupDesviaciones.setObjectName(u"groupDesviaciones")
        self.groupDesviacionesLayout = QVBoxLayout(self.groupDesviaciones)
        self.groupDesviacionesLayout.setSpacing(11)
        self.groupDesviacionesLayout.setObjectName(u"groupDesviacionesLayout")
        self.groupDesviacionesLayout.setContentsMargins(14, 14, 14, 14)
        self.desviacionLinealFila = QHBoxLayout()
        self.desviacionLinealFila.setSpacing(10)
        self.desviacionLinealFila.setObjectName(u"desviacionLinealFila")
        self.desviacionLinealFila.setContentsMargins(0, 0, 0, 0)
        self.desviacionLinealTxt = QLabel(self.groupDesviaciones)
        self.desviacionLinealTxt.setObjectName(u"desviacionLinealTxt")

        self.desviacionLinealFila.addWidget(self.desviacionLinealTxt)

        self.desviacionLinealSlider = QSlider(self.groupDesviaciones)
        self.desviacionLinealSlider.setObjectName(u"desviacionLinealSlider")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.desviacionLinealSlider.sizePolicy().hasHeightForWidth())
        self.desviacionLinealSlider.setSizePolicy(sizePolicy)
        self.desviacionLinealSlider.setMinimum(0)
        self.desviacionLinealSlider.setMaximum(1000)
        self.desviacionLinealSlider.setValue(2)
        self.desviacionLinealSlider.setOrientation(Qt.Orientation.Horizontal)

        self.desviacionLinealFila.addWidget(self.desviacionLinealSlider)

        self.desviacionLinealSpin = QDoubleSpinBox(self.groupDesviaciones)
        self.desviacionLinealSpin.setObjectName(u"desviacionLinealSpin")
        self.desviacionLinealSpin.setDecimals(6)
        self.desviacionLinealSpin.setMinimum(0.000000000000000)
        self.desviacionLinealSpin.setMaximum(0.100000000000000)
        self.desviacionLinealSpin.setSingleStep(0.000100000000000)
        self.desviacionLinealSpin.setValue(0.000300000000000)

        self.desviacionLinealFila.addWidget(self.desviacionLinealSpin)


        self.groupDesviacionesLayout.addLayout(self.desviacionLinealFila)

        self.desviacionAngularFila = QHBoxLayout()
        self.desviacionAngularFila.setSpacing(10)
        self.desviacionAngularFila.setObjectName(u"desviacionAngularFila")
        self.desviacionAngularFila.setContentsMargins(0, 0, 0, 0)
        self.desviacionAngularTxt = QLabel(self.groupDesviaciones)
        self.desviacionAngularTxt.setObjectName(u"desviacionAngularTxt")

        self.desviacionAngularFila.addWidget(self.desviacionAngularTxt)

        self.desviacionAngularSlider = QSlider(self.groupDesviaciones)
        self.desviacionAngularSlider.setObjectName(u"desviacionAngularSlider")
        sizePolicy.setHeightForWidth(self.desviacionAngularSlider.sizePolicy().hasHeightForWidth())
        self.desviacionAngularSlider.setSizePolicy(sizePolicy)
        self.desviacionAngularSlider.setMinimum(0)
        self.desviacionAngularSlider.setMaximum(1000)
        self.desviacionAngularSlider.setValue(500)
        self.desviacionAngularSlider.setOrientation(Qt.Orientation.Horizontal)

        self.desviacionAngularFila.addWidget(self.desviacionAngularSlider)

        self.desviacionAngularSpin = QDoubleSpinBox(self.groupDesviaciones)
        self.desviacionAngularSpin.setObjectName(u"desviacionAngularSpin")
        self.desviacionAngularSpin.setDecimals(4)
        self.desviacionAngularSpin.setMinimum(0.000000000000000)
        self.desviacionAngularSpin.setMaximum(1.000000000000000)
        self.desviacionAngularSpin.setSingleStep(0.000100000000000)
        self.desviacionAngularSpin.setValue(0.500000000000000)

        self.desviacionAngularFila.addWidget(self.desviacionAngularSpin)


        self.groupDesviacionesLayout.addLayout(self.desviacionAngularFila)

        self.chkMostrarEstimacion = QCheckBox(self.groupDesviaciones)
        self.chkMostrarEstimacion.setObjectName(u"chkMostrarEstimacion")
        self.chkMostrarEstimacion.setEnabled(True)
        self.chkMostrarEstimacion.setChecked(False)

        self.groupDesviacionesLayout.addWidget(self.chkMostrarEstimacion)


        self.gridLayout_7.addWidget(self.groupDesviaciones, 0, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_7.addItem(self.verticalSpacer_2, 4, 0, 1, 1)

        self.groupEstimacionCosto = QGroupBox(self.tab_2)
        self.groupEstimacionCosto.setObjectName(u"groupEstimacionCosto")
        self.groupEstimacionCostoLayout = QVBoxLayout(self.groupEstimacionCosto)
        self.groupEstimacionCostoLayout.setObjectName(u"groupEstimacionCostoLayout")
        self.lblCalculoExplicacion = QLabel(self.groupEstimacionCosto)
        self.lblCalculoExplicacion.setObjectName(u"lblCalculoExplicacion")
        self.lblCalculoExplicacion.setWordWrap(True)

        self.groupEstimacionCostoLayout.addWidget(self.lblCalculoExplicacion)

        self.filaEstimacionMuestras = QHBoxLayout()
        self.filaEstimacionMuestras.setObjectName(u"filaEstimacionMuestras")
        self.lblTituloMuestrasPrevistas = QLabel(self.groupEstimacionCosto)
        self.lblTituloMuestrasPrevistas.setObjectName(u"lblTituloMuestrasPrevistas")

        self.filaEstimacionMuestras.addWidget(self.lblTituloMuestrasPrevistas)

        self.lblEstimacionMuestras = QLabel(self.groupEstimacionCosto)
        self.lblEstimacionMuestras.setObjectName(u"lblEstimacionMuestras")

        self.filaEstimacionMuestras.addWidget(self.lblEstimacionMuestras)


        self.groupEstimacionCostoLayout.addLayout(self.filaEstimacionMuestras)

        self.filaEstimacionDuracion = QHBoxLayout()
        self.filaEstimacionDuracion.setObjectName(u"filaEstimacionDuracion")
        self.lblTituloCostoPrevisto = QLabel(self.groupEstimacionCosto)
        self.lblTituloCostoPrevisto.setObjectName(u"lblTituloCostoPrevisto")

        self.filaEstimacionDuracion.addWidget(self.lblTituloCostoPrevisto)

        self.lblEstimacionCosto = QLabel(self.groupEstimacionCosto)
        self.lblEstimacionCosto.setObjectName(u"lblEstimacionCosto")

        self.filaEstimacionDuracion.addWidget(self.lblEstimacionCosto)


        self.groupEstimacionCostoLayout.addLayout(self.filaEstimacionDuracion)

        self.lblMetodoEstimacion = QLabel(self.groupEstimacionCosto)
        self.lblMetodoEstimacion.setObjectName(u"lblMetodoEstimacion")
        self.lblMetodoEstimacion.setWordWrap(True)

        self.groupEstimacionCostoLayout.addWidget(self.lblMetodoEstimacion)


        self.gridLayout_7.addWidget(self.groupEstimacionCosto, 3, 0, 1, 1)

        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.gridLayout_8 = QGridLayout(self.tab_3)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.groupRender = QGroupBox(self.tab_3)
        self.groupRender.setObjectName(u"groupRender")
        self.groupRenderLayout = QVBoxLayout(self.groupRender)
        self.groupRenderLayout.setSpacing(11)
        self.groupRenderLayout.setObjectName(u"groupRenderLayout")
        self.groupRenderLayout.setContentsMargins(14, 14, 14, 14)
        self.comboRenderRow = QHBoxLayout()
        self.comboRenderRow.setSpacing(10)
        self.comboRenderRow.setObjectName(u"comboRenderRow")
        self.comboRenderRow.setContentsMargins(0, 0, 0, 0)
        self.comboRenderLabel = QLabel(self.groupRender)
        self.comboRenderLabel.setObjectName(u"comboRenderLabel")
        self.comboRenderLabel.setMinimumSize(QSize(172, 0))

        self.comboRenderRow.addWidget(self.comboRenderLabel)

        self.comboRender = QComboBox(self.groupRender)
        self.comboRender.addItem("")
        self.comboRender.addItem("")
        self.comboRender.setObjectName(u"comboRender")

        self.comboRenderRow.addWidget(self.comboRender)


        self.groupRenderLayout.addLayout(self.comboRenderRow)


        self.gridLayout_8.addWidget(self.groupRender, 2, 0, 1, 1)

        self.groupCadencia = QGroupBox(self.tab_3)
        self.groupCadencia.setObjectName(u"groupCadencia")
        self.groupCadenciaLayout = QVBoxLayout(self.groupCadencia)
        self.groupCadenciaLayout.setSpacing(11)
        self.groupCadenciaLayout.setObjectName(u"groupCadenciaLayout")
        self.groupCadenciaLayout.setContentsMargins(14, 14, 14, 14)
        self.comboFPSRow = QHBoxLayout()
        self.comboFPSRow.setSpacing(10)
        self.comboFPSRow.setObjectName(u"comboFPSRow")
        self.comboFPSRow.setContentsMargins(0, 0, 0, 0)
        self.comboFPSLabel = QLabel(self.groupCadencia)
        self.comboFPSLabel.setObjectName(u"comboFPSLabel")
        self.comboFPSLabel.setMinimumSize(QSize(172, 0))

        self.comboFPSRow.addWidget(self.comboFPSLabel)

        self.comboFPS = QComboBox(self.groupCadencia)
        self.comboFPS.addItem("")
        self.comboFPS.addItem("")
        self.comboFPS.addItem("")
        self.comboFPS.addItem("")
        self.comboFPS.addItem("")
        self.comboFPS.addItem("")
        self.comboFPS.addItem("")
        self.comboFPS.addItem("")
        self.comboFPS.addItem("")
        self.comboFPS.addItem("")
        self.comboFPS.addItem("")
        self.comboFPS.setObjectName(u"comboFPS")

        self.comboFPSRow.addWidget(self.comboFPS)


        self.groupCadenciaLayout.addLayout(self.comboFPSRow)

        self.layoutFPSCustom = QHBoxLayout()
        self.layoutFPSCustom.setSpacing(10)
        self.layoutFPSCustom.setObjectName(u"layoutFPSCustom")
        self.layoutFPSCustom.setContentsMargins(0, 0, 0, 0)
        self.lblFPSCustom = QLabel(self.groupCadencia)
        self.lblFPSCustom.setObjectName(u"lblFPSCustom")
        self.lblFPSCustom.setWordWrap(True)

        self.layoutFPSCustom.addWidget(self.lblFPSCustom)

        self.spinFPSCustom = QSpinBox(self.groupCadencia)
        self.spinFPSCustom.setObjectName(u"spinFPSCustom")
        self.spinFPSCustom.setMinimum(1)
        self.spinFPSCustom.setMaximum(1000)
        self.spinFPSCustom.setSingleStep(1)
        self.spinFPSCustom.setValue(120)

        self.layoutFPSCustom.addWidget(self.spinFPSCustom)

        self.customFpsSpace = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layoutFPSCustom.addItem(self.customFpsSpace)


        self.groupCadenciaLayout.addLayout(self.layoutFPSCustom)

        self.lblMonitorHz = QLabel(self.groupCadencia)
        self.lblMonitorHz.setObjectName(u"lblMonitorHz")
        self.lblMonitorHz.setWordWrap(True)

        self.groupCadenciaLayout.addWidget(self.lblMonitorHz)

        self.chkVSync = QCheckBox(self.groupCadencia)
        self.chkVSync.setObjectName(u"chkVSync")
        self.chkVSync.setEnabled(False)
        self.chkVSync.setChecked(False)

        self.groupCadenciaLayout.addWidget(self.chkVSync)


        self.gridLayout_8.addWidget(self.groupCadencia, 0, 0, 1, 1)

        self.groupProcesamiento = QGroupBox(self.tab_3)
        self.groupProcesamiento.setObjectName(u"groupProcesamiento")
        self.groupProcesamientoLayout = QVBoxLayout(self.groupProcesamiento)
        self.groupProcesamientoLayout.setSpacing(11)
        self.groupProcesamientoLayout.setObjectName(u"groupProcesamientoLayout")
        self.groupProcesamientoLayout.setContentsMargins(14, 14, 14, 14)
        self.comboBackendRow = QHBoxLayout()
        self.comboBackendRow.setSpacing(10)
        self.comboBackendRow.setObjectName(u"comboBackendRow")
        self.comboBackendRow.setContentsMargins(0, 0, 0, 0)
        self.comboBackendLabel = QLabel(self.groupProcesamiento)
        self.comboBackendLabel.setObjectName(u"comboBackendLabel")
        self.comboBackendLabel.setMinimumSize(QSize(172, 0))

        self.comboBackendRow.addWidget(self.comboBackendLabel)

        self.comboBackend = QComboBox(self.groupProcesamiento)
        self.comboBackend.addItem("")
        self.comboBackend.addItem("")
        self.comboBackend.addItem("")
        self.comboBackend.setObjectName(u"comboBackend")

        self.comboBackendRow.addWidget(self.comboBackend)


        self.groupProcesamientoLayout.addLayout(self.comboBackendRow)


        self.gridLayout_8.addWidget(self.groupProcesamiento, 1, 0, 1, 1)

        self.groupSimComportamiento = QGroupBox(self.tab_3)
        self.groupSimComportamiento.setObjectName(u"groupSimComportamiento")
        self.groupSimComportamientoLayout = QVBoxLayout(self.groupSimComportamiento)
        self.groupSimComportamientoLayout.setSpacing(11)
        self.groupSimComportamientoLayout.setObjectName(u"groupSimComportamientoLayout")
        self.groupSimComportamientoLayout.setContentsMargins(14, 14, 14, 14)
        self.chkBajarFPSInactivo_2 = QCheckBox(self.groupSimComportamiento)
        self.chkBajarFPSInactivo_2.setObjectName(u"chkBajarFPSInactivo_2")
        self.chkBajarFPSInactivo_2.setEnabled(True)
        self.chkBajarFPSInactivo_2.setChecked(True)

        self.groupSimComportamientoLayout.addWidget(self.chkBajarFPSInactivo_2)

        self.chkBajarFPSInactivo = QCheckBox(self.groupSimComportamiento)
        self.chkBajarFPSInactivo.setObjectName(u"chkBajarFPSInactivo")
        self.chkBajarFPSInactivo.setEnabled(True)
        self.chkBajarFPSInactivo.setChecked(True)

        self.groupSimComportamientoLayout.addWidget(self.chkBajarFPSInactivo)

        self.chkDetenerInvalido = QCheckBox(self.groupSimComportamiento)
        self.chkDetenerInvalido.setObjectName(u"chkDetenerInvalido")
        self.chkDetenerInvalido.setEnabled(True)
        self.chkDetenerInvalido.setChecked(True)

        self.groupSimComportamientoLayout.addWidget(self.chkDetenerInvalido)

        self.chkConservarPausa = QCheckBox(self.groupSimComportamiento)
        self.chkConservarPausa.setObjectName(u"chkConservarPausa")
        self.chkConservarPausa.setEnabled(True)
        self.chkConservarPausa.setChecked(True)

        self.groupSimComportamientoLayout.addWidget(self.chkConservarPausa)

        self.chkCacheGeometria = QCheckBox(self.groupSimComportamiento)
        self.chkCacheGeometria.setObjectName(u"chkCacheGeometria")
        self.chkCacheGeometria.setEnabled(True)
        self.chkCacheGeometria.setChecked(True)

        self.groupSimComportamientoLayout.addWidget(self.chkCacheGeometria)


        self.gridLayout_8.addWidget(self.groupSimComportamiento, 3, 0, 1, 1)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_8.addItem(self.verticalSpacer_4, 5, 0, 1, 1)

        self.groupAnalisisContacto = QGroupBox(self.tab_3)
        self.groupAnalisisContacto.setObjectName(u"groupAnalisisContacto")
        self.gridLayout_11 = QGridLayout(self.groupAnalisisContacto)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.checkBox_3 = QCheckBox(self.groupAnalisisContacto)
        self.checkBox_3.setObjectName(u"checkBox_3")

        self.gridLayout_11.addWidget(self.checkBox_3, 2, 1, 1, 1)

        self.lblAccesoEditorRegimenes = QLabel(self.groupAnalisisContacto)
        self.lblAccesoEditorRegimenes.setObjectName(u"lblAccesoEditorRegimenes")
        self.lblAccesoEditorRegimenes.setWordWrap(True)

        self.gridLayout_11.addWidget(self.lblAccesoEditorRegimenes, 4, 1, 1, 1)

        self.btnAbrirEditorRegimenes = QPushButton(self.groupAnalisisContacto)
        self.btnAbrirEditorRegimenes.setObjectName(u"btnAbrirEditorRegimenes")
        self.btnAbrirEditorRegimenes.setEnabled(False)
        self.btnAbrirEditorRegimenes.setMinimumSize(QSize(210, 30))

        self.gridLayout_11.addWidget(self.btnAbrirEditorRegimenes, 5, 1, 1, 1)

        self.lblEstadoContactoAjustes = QLabel(self.groupAnalisisContacto)
        self.lblEstadoContactoAjustes.setObjectName(u"lblEstadoContactoAjustes")
        self.lblEstadoContactoAjustes.setWordWrap(True)

        self.gridLayout_11.addWidget(self.lblEstadoContactoAjustes, 3, 1, 1, 1)


        self.gridLayout_8.addWidget(self.groupAnalisisContacto, 4, 0, 1, 1)

        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.gridLayout_9 = QGridLayout(self.tab_4)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.tabApariencia = QTabWidget(self.tab_4)
        self.tabApariencia.setObjectName(u"tabApariencia")
        self.tabTemas = QWidget()
        self.tabTemas.setObjectName(u"tabTemas")
        self.tabTemasLayout = QVBoxLayout(self.tabTemas)
        self.tabTemasLayout.setSpacing(12)
        self.tabTemasLayout.setObjectName(u"tabTemasLayout")
        self.tabTemasLayout.setContentsMargins(10, 10, 10, 10)
        self.comboTemaRow = QHBoxLayout()
        self.comboTemaRow.setSpacing(10)
        self.comboTemaRow.setObjectName(u"comboTemaRow")
        self.comboTemaRow.setContentsMargins(0, 0, 0, 0)
        self.comboTemaLabel = QLabel(self.tabTemas)
        self.comboTemaLabel.setObjectName(u"comboTemaLabel")
        self.comboTemaLabel.setMinimumSize(QSize(172, 0))

        self.comboTemaRow.addWidget(self.comboTemaLabel)

        self.comboTema = QComboBox(self.tabTemas)
        self.comboTema.addItem("")
        self.comboTema.addItem("")
        self.comboTema.addItem("")
        self.comboTema.addItem("")
        self.comboTema.addItem("")
        self.comboTema.addItem("")
        self.comboTema.addItem("")
        self.comboTema.addItem("")
        self.comboTema.addItem("")
        self.comboTema.addItem("")
        self.comboTema.addItem("")
        self.comboTema.addItem("")
        self.comboTema.addItem("")
        self.comboTema.setObjectName(u"comboTema")

        self.comboTemaRow.addWidget(self.comboTema)


        self.tabTemasLayout.addLayout(self.comboTemaRow)

        self.temaBotones = QHBoxLayout()
        self.temaBotones.setSpacing(10)
        self.temaBotones.setObjectName(u"temaBotones")
        self.temaBotones.setContentsMargins(0, 0, 0, 0)
        self.btnGuardarTema = QPushButton(self.tabTemas)
        self.btnGuardarTema.setObjectName(u"btnGuardarTema")

        self.temaBotones.addWidget(self.btnGuardarTema)

        self.btnDuplicarTema = QPushButton(self.tabTemas)
        self.btnDuplicarTema.setObjectName(u"btnDuplicarTema")

        self.temaBotones.addWidget(self.btnDuplicarTema)

        self.btnRestaurarTema = QPushButton(self.tabTemas)
        self.btnRestaurarTema.setObjectName(u"btnRestaurarTema")

        self.temaBotones.addWidget(self.btnRestaurarTema)

        self.temaSp = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.temaBotones.addItem(self.temaSp)


        self.tabTemasLayout.addLayout(self.temaBotones)

        self.temasSp = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.tabTemasLayout.addItem(self.temasSp)

        self.tabApariencia.addTab(self.tabTemas, "")
        self.tabColoresUI = QWidget()
        self.tabColoresUI.setObjectName(u"tabColoresUI")
        self.tabColoresUILayout = QVBoxLayout(self.tabColoresUI)
        self.tabColoresUILayout.setSpacing(12)
        self.tabColoresUILayout.setObjectName(u"tabColoresUILayout")
        self.tabColoresUILayout.setContentsMargins(10, 10, 10, 10)
        self.treeColoresUI = QTreeWidget(self.tabColoresUI)
        QTreeWidgetItem(self.treeColoresUI)
        QTreeWidgetItem(self.treeColoresUI)
        QTreeWidgetItem(self.treeColoresUI)
        QTreeWidgetItem(self.treeColoresUI)
        QTreeWidgetItem(self.treeColoresUI)
        QTreeWidgetItem(self.treeColoresUI)
        QTreeWidgetItem(self.treeColoresUI)
        QTreeWidgetItem(self.treeColoresUI)
        QTreeWidgetItem(self.treeColoresUI)
        QTreeWidgetItem(self.treeColoresUI)
        QTreeWidgetItem(self.treeColoresUI)
        QTreeWidgetItem(self.treeColoresUI)
        QTreeWidgetItem(self.treeColoresUI)
        QTreeWidgetItem(self.treeColoresUI)
        self.treeColoresUI.setObjectName(u"treeColoresUI")
        self.treeColoresUI.setAlternatingRowColors(True)

        self.tabColoresUILayout.addWidget(self.treeColoresUI)

        self.layoutColorUISelect = QHBoxLayout()
        self.layoutColorUISelect.setSpacing(10)
        self.layoutColorUISelect.setObjectName(u"layoutColorUISelect")
        self.layoutColorUISelect.setContentsMargins(0, 0, 0, 0)
        self.lblColorUISeleccion = QLabel(self.tabColoresUI)
        self.lblColorUISeleccion.setObjectName(u"lblColorUISeleccion")

        self.layoutColorUISelect.addWidget(self.lblColorUISeleccion)

        self.uiColorSp = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layoutColorUISelect.addItem(self.uiColorSp)

        self.btnColorUI = QPushButton(self.tabColoresUI)
        self.btnColorUI.setObjectName(u"btnColorUI")

        self.layoutColorUISelect.addWidget(self.btnColorUI)


        self.tabColoresUILayout.addLayout(self.layoutColorUISelect)

        self.tabApariencia.addTab(self.tabColoresUI, "")
        self.tabColoresTecnicos = QWidget()
        self.tabColoresTecnicos.setObjectName(u"tabColoresTecnicos")
        self.tabColoresTecnicosLayout = QVBoxLayout(self.tabColoresTecnicos)
        self.tabColoresTecnicosLayout.setSpacing(12)
        self.tabColoresTecnicosLayout.setObjectName(u"tabColoresTecnicosLayout")
        self.tabColoresTecnicosLayout.setContentsMargins(10, 10, 10, 10)
        self.lblColorTecnicoAyuda = QLabel(self.tabColoresTecnicos)
        self.lblColorTecnicoAyuda.setObjectName(u"lblColorTecnicoAyuda")
        self.lblColorTecnicoAyuda.setWordWrap(True)

        self.tabColoresTecnicosLayout.addWidget(self.lblColorTecnicoAyuda)

        self.treeColoresTecnicos = QTreeWidget(self.tabColoresTecnicos)
        QTreeWidgetItem(self.treeColoresTecnicos)
        QTreeWidgetItem(self.treeColoresTecnicos)
        QTreeWidgetItem(self.treeColoresTecnicos)
        QTreeWidgetItem(self.treeColoresTecnicos)
        QTreeWidgetItem(self.treeColoresTecnicos)
        QTreeWidgetItem(self.treeColoresTecnicos)
        QTreeWidgetItem(self.treeColoresTecnicos)
        QTreeWidgetItem(self.treeColoresTecnicos)
        QTreeWidgetItem(self.treeColoresTecnicos)
        QTreeWidgetItem(self.treeColoresTecnicos)
        QTreeWidgetItem(self.treeColoresTecnicos)
        QTreeWidgetItem(self.treeColoresTecnicos)
        QTreeWidgetItem(self.treeColoresTecnicos)
        QTreeWidgetItem(self.treeColoresTecnicos)
        QTreeWidgetItem(self.treeColoresTecnicos)
        self.treeColoresTecnicos.setObjectName(u"treeColoresTecnicos")
        self.treeColoresTecnicos.setAlternatingRowColors(True)

        self.tabColoresTecnicosLayout.addWidget(self.treeColoresTecnicos)

        self.layoutColorTecnicoSelect = QHBoxLayout()
        self.layoutColorTecnicoSelect.setSpacing(10)
        self.layoutColorTecnicoSelect.setObjectName(u"layoutColorTecnicoSelect")
        self.layoutColorTecnicoSelect.setContentsMargins(0, 0, 0, 0)
        self.lblColorTecnicoSeleccion = QLabel(self.tabColoresTecnicos)
        self.lblColorTecnicoSeleccion.setObjectName(u"lblColorTecnicoSeleccion")

        self.layoutColorTecnicoSelect.addWidget(self.lblColorTecnicoSeleccion)

        self.tecColorSp = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layoutColorTecnicoSelect.addItem(self.tecColorSp)

        self.btnColorTecnico = QPushButton(self.tabColoresTecnicos)
        self.btnColorTecnico.setObjectName(u"btnColorTecnico")

        self.layoutColorTecnicoSelect.addWidget(self.btnColorTecnico)


        self.tabColoresTecnicosLayout.addLayout(self.layoutColorTecnicoSelect)

        self.tabApariencia.addTab(self.tabColoresTecnicos, "")
        self.tabTrazos = QWidget()
        self.tabTrazos.setObjectName(u"tabTrazos")
        self.tabTrazosLayout = QVBoxLayout(self.tabTrazos)
        self.tabTrazosLayout.setSpacing(12)
        self.tabTrazosLayout.setObjectName(u"tabTrazosLayout")
        self.tabTrazosLayout.setContentsMargins(10, 10, 10, 10)
        self.comboTipoCurvaRow = QHBoxLayout()
        self.comboTipoCurvaRow.setSpacing(10)
        self.comboTipoCurvaRow.setObjectName(u"comboTipoCurvaRow")
        self.comboTipoCurvaRow.setContentsMargins(0, 0, 0, 0)
        self.comboTipoCurvaLabel = QLabel(self.tabTrazos)
        self.comboTipoCurvaLabel.setObjectName(u"comboTipoCurvaLabel")
        self.comboTipoCurvaLabel.setMinimumSize(QSize(172, 0))

        self.comboTipoCurvaRow.addWidget(self.comboTipoCurvaLabel)

        self.comboTipoCurva = QComboBox(self.tabTrazos)
        self.comboTipoCurva.addItem("")
        self.comboTipoCurva.addItem("")
        self.comboTipoCurva.addItem("")
        self.comboTipoCurva.addItem("")
        self.comboTipoCurva.addItem("")
        self.comboTipoCurva.addItem("")
        self.comboTipoCurva.addItem("")
        self.comboTipoCurva.addItem("")
        self.comboTipoCurva.addItem("")
        self.comboTipoCurva.setObjectName(u"comboTipoCurva")

        self.comboTipoCurvaRow.addWidget(self.comboTipoCurva)


        self.tabTrazosLayout.addLayout(self.comboTipoCurvaRow)

        self.layoutAnchoLinea = QHBoxLayout()
        self.layoutAnchoLinea.setSpacing(10)
        self.layoutAnchoLinea.setObjectName(u"layoutAnchoLinea")
        self.layoutAnchoLinea.setContentsMargins(0, 0, 0, 0)
        self.lblAnchoLinea = QLabel(self.tabTrazos)
        self.lblAnchoLinea.setObjectName(u"lblAnchoLinea")
        self.lblAnchoLinea.setWordWrap(True)

        self.layoutAnchoLinea.addWidget(self.lblAnchoLinea)

        self.spinAnchoLinea = QDoubleSpinBox(self.tabTrazos)
        self.spinAnchoLinea.setObjectName(u"spinAnchoLinea")
        self.spinAnchoLinea.setDecimals(2)
        self.spinAnchoLinea.setMinimum(0.100000000000000)
        self.spinAnchoLinea.setMaximum(10.000000000000000)
        self.spinAnchoLinea.setSingleStep(0.100000000000000)
        self.spinAnchoLinea.setValue(1.000000000000000)

        self.layoutAnchoLinea.addWidget(self.spinAnchoLinea)

        self.anchoSp = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layoutAnchoLinea.addItem(self.anchoSp)


        self.tabTrazosLayout.addLayout(self.layoutAnchoLinea)

        self.comboTipoLineaRow = QHBoxLayout()
        self.comboTipoLineaRow.setSpacing(10)
        self.comboTipoLineaRow.setObjectName(u"comboTipoLineaRow")
        self.comboTipoLineaRow.setContentsMargins(0, 0, 0, 0)
        self.comboTipoLineaLabel = QLabel(self.tabTrazos)
        self.comboTipoLineaLabel.setObjectName(u"comboTipoLineaLabel")
        self.comboTipoLineaLabel.setMinimumSize(QSize(172, 0))

        self.comboTipoLineaRow.addWidget(self.comboTipoLineaLabel)

        self.comboTipoLinea = QComboBox(self.tabTrazos)
        self.comboTipoLinea.addItem("")
        self.comboTipoLinea.addItem("")
        self.comboTipoLinea.addItem("")
        self.comboTipoLinea.addItem("")
        self.comboTipoLinea.addItem("")
        self.comboTipoLinea.setObjectName(u"comboTipoLinea")

        self.comboTipoLineaRow.addWidget(self.comboTipoLinea)


        self.tabTrazosLayout.addLayout(self.comboTipoLineaRow)

        self.comboLineCapRow = QHBoxLayout()
        self.comboLineCapRow.setSpacing(10)
        self.comboLineCapRow.setObjectName(u"comboLineCapRow")
        self.comboLineCapRow.setContentsMargins(0, 0, 0, 0)
        self.comboLineCapLabel = QLabel(self.tabTrazos)
        self.comboLineCapLabel.setObjectName(u"comboLineCapLabel")
        self.comboLineCapLabel.setMinimumSize(QSize(172, 0))

        self.comboLineCapRow.addWidget(self.comboLineCapLabel)

        self.comboLineCap = QComboBox(self.tabTrazos)
        self.comboLineCap.addItem("")
        self.comboLineCap.addItem("")
        self.comboLineCap.addItem("")
        self.comboLineCap.setObjectName(u"comboLineCap")

        self.comboLineCapRow.addWidget(self.comboLineCap)


        self.tabTrazosLayout.addLayout(self.comboLineCapRow)

        self.comboLineJoinRow = QHBoxLayout()
        self.comboLineJoinRow.setSpacing(10)
        self.comboLineJoinRow.setObjectName(u"comboLineJoinRow")
        self.comboLineJoinRow.setContentsMargins(0, 0, 0, 0)
        self.comboLineJoinLabel = QLabel(self.tabTrazos)
        self.comboLineJoinLabel.setObjectName(u"comboLineJoinLabel")
        self.comboLineJoinLabel.setMinimumSize(QSize(172, 0))

        self.comboLineJoinRow.addWidget(self.comboLineJoinLabel)

        self.comboLineJoin = QComboBox(self.tabTrazos)
        self.comboLineJoin.addItem("")
        self.comboLineJoin.addItem("")
        self.comboLineJoin.addItem("")
        self.comboLineJoin.setObjectName(u"comboLineJoin")

        self.comboLineJoinRow.addWidget(self.comboLineJoin)


        self.tabTrazosLayout.addLayout(self.comboLineJoinRow)

        self.layoutOpacidad = QHBoxLayout()
        self.layoutOpacidad.setSpacing(10)
        self.layoutOpacidad.setObjectName(u"layoutOpacidad")
        self.layoutOpacidad.setContentsMargins(0, 0, 0, 0)
        self.lblOpacidad = QLabel(self.tabTrazos)
        self.lblOpacidad.setObjectName(u"lblOpacidad")
        self.lblOpacidad.setWordWrap(True)

        self.layoutOpacidad.addWidget(self.lblOpacidad)

        self.sliderOpacidad = QSlider(self.tabTrazos)
        self.sliderOpacidad.setObjectName(u"sliderOpacidad")
        self.sliderOpacidad.setMinimum(0)
        self.sliderOpacidad.setMaximum(100)
        self.sliderOpacidad.setValue(100)
        self.sliderOpacidad.setOrientation(Qt.Orientation.Horizontal)

        self.layoutOpacidad.addWidget(self.sliderOpacidad)

        self.spinOpacidad = QSpinBox(self.tabTrazos)
        self.spinOpacidad.setObjectName(u"spinOpacidad")
        self.spinOpacidad.setMinimum(0)
        self.spinOpacidad.setMaximum(100)
        self.spinOpacidad.setSingleStep(1)
        self.spinOpacidad.setValue(100)

        self.layoutOpacidad.addWidget(self.spinOpacidad)


        self.tabTrazosLayout.addLayout(self.layoutOpacidad)

        self.chkAntialias = QCheckBox(self.tabTrazos)
        self.chkAntialias.setObjectName(u"chkAntialias")
        self.chkAntialias.setEnabled(True)
        self.chkAntialias.setChecked(True)

        self.tabTrazosLayout.addWidget(self.chkAntialias)

        self.trazosEnd = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.tabTrazosLayout.addItem(self.trazosEnd)

        self.tabApariencia.addTab(self.tabTrazos, "")
        self.tabFuentes = QWidget()
        self.tabFuentes.setObjectName(u"tabFuentes")
        self.tabFuentesLayout = QVBoxLayout(self.tabFuentes)
        self.tabFuentesLayout.setSpacing(12)
        self.tabFuentesLayout.setObjectName(u"tabFuentesLayout")
        self.tabFuentesLayout.setContentsMargins(10, 10, 10, 10)
        self.groupFuenteUI = QGroupBox(self.tabFuentes)
        self.groupFuenteUI.setObjectName(u"groupFuenteUI")
        self.groupFuenteUILayout = QVBoxLayout(self.groupFuenteUI)
        self.groupFuenteUILayout.setSpacing(10)
        self.groupFuenteUILayout.setObjectName(u"groupFuenteUILayout")
        self.groupFuenteUILayout.setContentsMargins(14, 14, 14, 14)
        self.layoutFontUI = QHBoxLayout()
        self.layoutFontUI.setSpacing(10)
        self.layoutFontUI.setObjectName(u"layoutFontUI")
        self.layoutFontUI.setContentsMargins(0, 0, 0, 0)
        self.lblFontUI = QLabel(self.groupFuenteUI)
        self.lblFontUI.setObjectName(u"lblFontUI")
        self.lblFontUI.setWordWrap(True)

        self.layoutFontUI.addWidget(self.lblFontUI)

        self.fontInterfaz = QFontComboBox(self.groupFuenteUI)
        self.fontInterfaz.setObjectName(u"fontInterfaz")

        self.layoutFontUI.addWidget(self.fontInterfaz)

        self.spinTamanoUI = QSpinBox(self.groupFuenteUI)
        self.spinTamanoUI.setObjectName(u"spinTamanoUI")
        self.spinTamanoUI.setMinimum(7)
        self.spinTamanoUI.setMaximum(28)
        self.spinTamanoUI.setSingleStep(1)
        self.spinTamanoUI.setValue(10)

        self.layoutFontUI.addWidget(self.spinTamanoUI)


        self.groupFuenteUILayout.addLayout(self.layoutFontUI)

        self.chkFuenteUIBold = QCheckBox(self.groupFuenteUI)
        self.chkFuenteUIBold.setObjectName(u"chkFuenteUIBold")
        self.chkFuenteUIBold.setEnabled(True)
        self.chkFuenteUIBold.setChecked(False)

        self.groupFuenteUILayout.addWidget(self.chkFuenteUIBold)


        self.tabFuentesLayout.addWidget(self.groupFuenteUI)

        self.groupFuenteGrafica = QGroupBox(self.tabFuentes)
        self.groupFuenteGrafica.setObjectName(u"groupFuenteGrafica")
        self.groupFuenteGraficaLayout = QVBoxLayout(self.groupFuenteGrafica)
        self.groupFuenteGraficaLayout.setSpacing(10)
        self.groupFuenteGraficaLayout.setObjectName(u"groupFuenteGraficaLayout")
        self.groupFuenteGraficaLayout.setContentsMargins(14, 14, 14, 14)
        self.layoutFontPlot = QHBoxLayout()
        self.layoutFontPlot.setSpacing(10)
        self.layoutFontPlot.setObjectName(u"layoutFontPlot")
        self.layoutFontPlot.setContentsMargins(0, 0, 0, 0)
        self.lblFontPlot = QLabel(self.groupFuenteGrafica)
        self.lblFontPlot.setObjectName(u"lblFontPlot")
        self.lblFontPlot.setWordWrap(True)

        self.layoutFontPlot.addWidget(self.lblFontPlot)

        self.fontGraficas = QFontComboBox(self.groupFuenteGrafica)
        self.fontGraficas.setObjectName(u"fontGraficas")

        self.layoutFontPlot.addWidget(self.fontGraficas)

        self.spinTamanoGrafica = QSpinBox(self.groupFuenteGrafica)
        self.spinTamanoGrafica.setObjectName(u"spinTamanoGrafica")
        self.spinTamanoGrafica.setMinimum(6)
        self.spinTamanoGrafica.setMaximum(32)
        self.spinTamanoGrafica.setSingleStep(1)
        self.spinTamanoGrafica.setValue(9)

        self.layoutFontPlot.addWidget(self.spinTamanoGrafica)


        self.groupFuenteGraficaLayout.addLayout(self.layoutFontPlot)

        self.chkFuenteGraficaBold = QCheckBox(self.groupFuenteGrafica)
        self.chkFuenteGraficaBold.setObjectName(u"chkFuenteGraficaBold")
        self.chkFuenteGraficaBold.setEnabled(True)
        self.chkFuenteGraficaBold.setChecked(False)

        self.groupFuenteGraficaLayout.addWidget(self.chkFuenteGraficaBold)


        self.tabFuentesLayout.addWidget(self.groupFuenteGrafica)

        self.fuentesEnd = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.tabFuentesLayout.addItem(self.fuentesEnd)

        self.tabApariencia.addTab(self.tabFuentes, "")

        self.gridLayout_9.addWidget(self.tabApariencia, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_4, "")
        self.tab_5 = QWidget()
        self.tab_5.setObjectName(u"tab_5")
        self.gridLayout_10 = QGridLayout(self.tab_5)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.groupVideo = QGroupBox(self.tab_5)
        self.groupVideo.setObjectName(u"groupVideo")
        self.groupVideoLayout = QVBoxLayout(self.groupVideo)
        self.groupVideoLayout.setSpacing(11)
        self.groupVideoLayout.setObjectName(u"groupVideoLayout")
        self.groupVideoLayout.setContentsMargins(14, 14, 14, 14)
        self.comboFormatoVideoRow = QHBoxLayout()
        self.comboFormatoVideoRow.setSpacing(10)
        self.comboFormatoVideoRow.setObjectName(u"comboFormatoVideoRow")
        self.comboFormatoVideoRow.setContentsMargins(0, 0, 0, 0)
        self.comboFormatoVideoLabel = QLabel(self.groupVideo)
        self.comboFormatoVideoLabel.setObjectName(u"comboFormatoVideoLabel")
        self.comboFormatoVideoLabel.setMinimumSize(QSize(172, 0))

        self.comboFormatoVideoRow.addWidget(self.comboFormatoVideoLabel)

        self.comboFormatoVideo = QComboBox(self.groupVideo)
        self.comboFormatoVideo.addItem("")
        self.comboFormatoVideo.addItem("")
        self.comboFormatoVideo.setObjectName(u"comboFormatoVideo")

        self.comboFormatoVideoRow.addWidget(self.comboFormatoVideo)


        self.groupVideoLayout.addLayout(self.comboFormatoVideoRow)

        self.comboResolucionVideoRow = QHBoxLayout()
        self.comboResolucionVideoRow.setSpacing(10)
        self.comboResolucionVideoRow.setObjectName(u"comboResolucionVideoRow")
        self.comboResolucionVideoRow.setContentsMargins(0, 0, 0, 0)
        self.comboResolucionVideoLabel = QLabel(self.groupVideo)
        self.comboResolucionVideoLabel.setObjectName(u"comboResolucionVideoLabel")
        self.comboResolucionVideoLabel.setMinimumSize(QSize(172, 0))

        self.comboResolucionVideoRow.addWidget(self.comboResolucionVideoLabel)


        self.groupVideoLayout.addLayout(self.comboResolucionVideoRow)

        self.layoutVideoDims = QHBoxLayout()
        self.layoutVideoDims.setSpacing(10)
        self.layoutVideoDims.setObjectName(u"layoutVideoDims")
        self.layoutVideoDims.setContentsMargins(0, 0, 0, 0)
        self.lblVidDims = QLabel(self.groupVideo)
        self.lblVidDims.setObjectName(u"lblVidDims")
        self.lblVidDims.setWordWrap(True)

        self.layoutVideoDims.addWidget(self.lblVidDims)

        self.spinVidAncho = QSpinBox(self.groupVideo)
        self.spinVidAncho.setObjectName(u"spinVidAncho")
        self.spinVidAncho.setMinimum(100)
        self.spinVidAncho.setMaximum(16384)
        self.spinVidAncho.setSingleStep(10)
        self.spinVidAncho.setValue(1920)

        self.layoutVideoDims.addWidget(self.spinVidAncho)

        self.lblVidX = QLabel(self.groupVideo)
        self.lblVidX.setObjectName(u"lblVidX")

        self.layoutVideoDims.addWidget(self.lblVidX)

        self.spinVidAlto = QSpinBox(self.groupVideo)
        self.spinVidAlto.setObjectName(u"spinVidAlto")
        self.spinVidAlto.setMinimum(100)
        self.spinVidAlto.setMaximum(16384)
        self.spinVidAlto.setSingleStep(10)
        self.spinVidAlto.setValue(1080)

        self.layoutVideoDims.addWidget(self.spinVidAlto)

        self.vidDimsSpace = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layoutVideoDims.addItem(self.vidDimsSpace)


        self.groupVideoLayout.addLayout(self.layoutVideoDims)

        self.comboFPSVideoRow = QHBoxLayout()
        self.comboFPSVideoRow.setSpacing(10)
        self.comboFPSVideoRow.setObjectName(u"comboFPSVideoRow")
        self.comboFPSVideoRow.setContentsMargins(0, 0, 0, 0)
        self.comboFPSVideoLabel = QLabel(self.groupVideo)
        self.comboFPSVideoLabel.setObjectName(u"comboFPSVideoLabel")
        self.comboFPSVideoLabel.setMinimumSize(QSize(172, 0))

        self.comboFPSVideoRow.addWidget(self.comboFPSVideoLabel)


        self.groupVideoLayout.addLayout(self.comboFPSVideoRow)

        self.comboCRFVideoRow = QHBoxLayout()
        self.comboCRFVideoRow.setSpacing(10)
        self.comboCRFVideoRow.setObjectName(u"comboCRFVideoRow")
        self.comboCRFVideoRow.setContentsMargins(0, 0, 0, 0)
        self.comboCRFVideoLabel = QLabel(self.groupVideo)
        self.comboCRFVideoLabel.setObjectName(u"comboCRFVideoLabel")
        self.comboCRFVideoLabel.setMinimumSize(QSize(172, 0))

        self.comboCRFVideoRow.addWidget(self.comboCRFVideoLabel)


        self.groupVideoLayout.addLayout(self.comboCRFVideoRow)

        self.chkRelacionVideo = QCheckBox(self.groupVideo)
        self.chkRelacionVideo.setObjectName(u"chkRelacionVideo")
        self.chkRelacionVideo.setEnabled(True)
        self.chkRelacionVideo.setChecked(True)

        self.groupVideoLayout.addWidget(self.chkRelacionVideo)

        self.chkVideoDeterminista = QCheckBox(self.groupVideo)
        self.chkVideoDeterminista.setObjectName(u"chkVideoDeterminista")
        self.chkVideoDeterminista.setEnabled(True)
        self.chkVideoDeterminista.setChecked(True)

        self.groupVideoLayout.addWidget(self.chkVideoDeterminista)


        self.gridLayout_10.addWidget(self.groupVideo, 1, 0, 1, 1)

        self.groupImagen = QGroupBox(self.tab_5)
        self.groupImagen.setObjectName(u"groupImagen")
        self.groupImagenLayout = QVBoxLayout(self.groupImagen)
        self.groupImagenLayout.setSpacing(11)
        self.groupImagenLayout.setObjectName(u"groupImagenLayout")
        self.groupImagenLayout.setContentsMargins(14, 14, 14, 14)
        self.comboFormatoImagenRow = QHBoxLayout()
        self.comboFormatoImagenRow.setSpacing(10)
        self.comboFormatoImagenRow.setObjectName(u"comboFormatoImagenRow")
        self.comboFormatoImagenRow.setContentsMargins(0, 0, 0, 0)
        self.comboFormatoImagenLabel = QLabel(self.groupImagen)
        self.comboFormatoImagenLabel.setObjectName(u"comboFormatoImagenLabel")
        self.comboFormatoImagenLabel.setMinimumSize(QSize(172, 0))

        self.comboFormatoImagenRow.addWidget(self.comboFormatoImagenLabel)

        self.comboFormatoImagen = QComboBox(self.groupImagen)
        self.comboFormatoImagen.addItem("")
        self.comboFormatoImagen.addItem("")
        self.comboFormatoImagen.addItem("")
        self.comboFormatoImagen.addItem("")
        self.comboFormatoImagen.setObjectName(u"comboFormatoImagen")

        self.comboFormatoImagenRow.addWidget(self.comboFormatoImagen)


        self.groupImagenLayout.addLayout(self.comboFormatoImagenRow)

        self.comboResolucionImagenRow = QHBoxLayout()
        self.comboResolucionImagenRow.setSpacing(10)
        self.comboResolucionImagenRow.setObjectName(u"comboResolucionImagenRow")
        self.comboResolucionImagenRow.setContentsMargins(0, 0, 0, 0)
        self.comboResolucionImagenLabel = QLabel(self.groupImagen)
        self.comboResolucionImagenLabel.setObjectName(u"comboResolucionImagenLabel")
        self.comboResolucionImagenLabel.setMinimumSize(QSize(172, 0))

        self.comboResolucionImagenRow.addWidget(self.comboResolucionImagenLabel)

        self.comboResolucionImagen = QComboBox(self.groupImagen)
        self.comboResolucionImagen.addItem("")
        self.comboResolucionImagen.addItem("")
        self.comboResolucionImagen.addItem("")
        self.comboResolucionImagen.addItem("")
        self.comboResolucionImagen.addItem("")
        self.comboResolucionImagen.setObjectName(u"comboResolucionImagen")

        self.comboResolucionImagenRow.addWidget(self.comboResolucionImagen)


        self.groupImagenLayout.addLayout(self.comboResolucionImagenRow)

        self.layoutImagenDims = QHBoxLayout()
        self.layoutImagenDims.setSpacing(10)
        self.layoutImagenDims.setObjectName(u"layoutImagenDims")
        self.layoutImagenDims.setContentsMargins(0, 0, 0, 0)
        self.lblImgDims = QLabel(self.groupImagen)
        self.lblImgDims.setObjectName(u"lblImgDims")
        self.lblImgDims.setWordWrap(True)

        self.layoutImagenDims.addWidget(self.lblImgDims)

        self.spinImgAncho = QSpinBox(self.groupImagen)
        self.spinImgAncho.setObjectName(u"spinImgAncho")
        self.spinImgAncho.setMinimum(100)
        self.spinImgAncho.setMaximum(16384)
        self.spinImgAncho.setSingleStep(10)
        self.spinImgAncho.setValue(1920)

        self.layoutImagenDims.addWidget(self.spinImgAncho)

        self.lblPor = QLabel(self.groupImagen)
        self.lblPor.setObjectName(u"lblPor")

        self.layoutImagenDims.addWidget(self.lblPor)

        self.spinImgAlto = QSpinBox(self.groupImagen)
        self.spinImgAlto.setObjectName(u"spinImgAlto")
        self.spinImgAlto.setMinimum(100)
        self.spinImgAlto.setMaximum(16384)
        self.spinImgAlto.setSingleStep(10)
        self.spinImgAlto.setValue(1080)

        self.layoutImagenDims.addWidget(self.spinImgAlto)

        self.imgDimsSpace = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layoutImagenDims.addItem(self.imgDimsSpace)


        self.groupImagenLayout.addLayout(self.layoutImagenDims)

        self.layoutJpeg = QHBoxLayout()
        self.layoutJpeg.setSpacing(10)
        self.layoutJpeg.setObjectName(u"layoutJpeg")
        self.layoutJpeg.setContentsMargins(0, 0, 0, 0)
        self.lblJpeg = QLabel(self.groupImagen)
        self.lblJpeg.setObjectName(u"lblJpeg")
        self.lblJpeg.setWordWrap(True)

        self.layoutJpeg.addWidget(self.lblJpeg)

        self.sliderJpeg = QSlider(self.groupImagen)
        self.sliderJpeg.setObjectName(u"sliderJpeg")
        self.sliderJpeg.setMinimum(1)
        self.sliderJpeg.setMaximum(100)
        self.sliderJpeg.setValue(95)
        self.sliderJpeg.setOrientation(Qt.Orientation.Horizontal)

        self.layoutJpeg.addWidget(self.sliderJpeg)

        self.spinJpeg = QSpinBox(self.groupImagen)
        self.spinJpeg.setObjectName(u"spinJpeg")
        self.spinJpeg.setMinimum(1)
        self.spinJpeg.setMaximum(100)
        self.spinJpeg.setSingleStep(1)
        self.spinJpeg.setValue(95)

        self.layoutJpeg.addWidget(self.spinJpeg)


        self.groupImagenLayout.addLayout(self.layoutJpeg)

        self.chkMantenerAspectoImagen = QCheckBox(self.groupImagen)
        self.chkMantenerAspectoImagen.setObjectName(u"chkMantenerAspectoImagen")
        self.chkMantenerAspectoImagen.setEnabled(True)
        self.chkMantenerAspectoImagen.setChecked(True)

        self.groupImagenLayout.addWidget(self.chkMantenerAspectoImagen)

        self.chkFondoTransparente = QCheckBox(self.groupImagen)
        self.chkFondoTransparente.setObjectName(u"chkFondoTransparente")
        self.chkFondoTransparente.setEnabled(True)
        self.chkFondoTransparente.setChecked(False)

        self.groupImagenLayout.addWidget(self.chkFondoTransparente)

        self.chkAntialiasExport = QCheckBox(self.groupImagen)
        self.chkAntialiasExport.setObjectName(u"chkAntialiasExport")
        self.chkAntialiasExport.setEnabled(True)
        self.chkAntialiasExport.setChecked(True)

        self.groupImagenLayout.addWidget(self.chkAntialiasExport)


        self.gridLayout_10.addWidget(self.groupImagen, 0, 0, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_10.addItem(self.verticalSpacer_3, 2, 0, 1, 1)

        self.tabWidget.addTab(self.tab_5, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 1, 1, 1)


        self.gridLayout_2.addWidget(self.widget, 0, 0, 1, 5)

        self.pushButton_4 = QPushButton(Dialog)
        self.pushButton_4.setObjectName(u"pushButton_4")

        self.gridLayout_2.addWidget(self.pushButton_4, 1, 4, 1, 1)

        self.pushButton = QPushButton(Dialog)
        self.pushButton.setObjectName(u"pushButton")

        self.gridLayout_2.addWidget(self.pushButton, 1, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 1, 1, 1, 1)


        self.retranslateUi(Dialog)

        self.tabWidget.setCurrentIndex(2)
        self.comboDecimales.setCurrentIndex(0)
        self.comboEstrategiaMuestreo.setCurrentIndex(0)
        self.comboRender.setCurrentIndex(0)
        self.comboFPS.setCurrentIndex(0)
        self.comboBackend.setCurrentIndex(0)
        self.tabApariencia.setCurrentIndex(0)
        self.comboTema.setCurrentIndex(0)
        self.comboTipoCurva.setCurrentIndex(0)
        self.comboTipoLinea.setCurrentIndex(0)
        self.comboLineCap.setCurrentIndex(0)
        self.comboLineJoin.setCurrentIndex(0)
        self.comboFormatoVideo.setCurrentIndex(0)
        self.comboFormatoImagen.setCurrentIndex(0)
        self.comboResolucionImagen.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Ajustes \u2014 RPS Design V2", None))
        self.pushButton_2.setText(QCoreApplication.translate("Dialog", u"Cancelar", None))
        self.pushButton_3.setText(QCoreApplication.translate("Dialog", u"Aplicar", None))
        self.groupBox.setTitle(QCoreApplication.translate("Dialog", u"Inicio y sesi\u00f3n", None))
        self.checkBox.setText(QCoreApplication.translate("Dialog", u"Restaurar el \u00faltimo proyecto o sesi\u00f3n al iniciar", None))
        self.checkBox_2.setText(QCoreApplication.translate("Dialog", u"Advertir al cerrar cuando existan modificaciones sin guardar", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Dialog", u"Guardado y recuperaci\u00f3n", None))
        self.lblIntervalo.setText(QCoreApplication.translate("Dialog", u"Intervalo de guardado:", None))
        self.spinIntervaloGuardado.setSuffix(QCoreApplication.translate("Dialog", u" min", None))
        self.chkGuardadoAuto.setText(QCoreApplication.translate("Dialog", u"Habilitar guardado autom\u00e1tico del proyecto", None))
        self.chkGuardarPrefs.setText(QCoreApplication.translate("Dialog", u"Guardar las preferencias de la aplicaci\u00f3n entre sesiones", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("Dialog", u"Validaci\u00f3n y avisos", None))
        self.chkAvisosDatos.setText(QCoreApplication.translate("Dialog", u"Mostrar avisos cuando los par\u00e1metros de c\u00e1lculo no sean v\u00e1lidos", None))
        self.chkAvisosSobrescribir.setText(QCoreApplication.translate("Dialog", u"Confirmar antes de sobrescribir archivos existentes", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("Dialog", u"General", None))
        self.groupPrecisionNumerica.setTitle(QCoreApplication.translate("Dialog", u"Precisi\u00f3n num\u00e9rica", None))
        self.comboDecimalesLabel.setText(QCoreApplication.translate("Dialog", u"Cifras decimales", None))
        self.comboDecimales.setItemText(0, QCoreApplication.translate("Dialog", u"4 decimales", None))
        self.comboDecimales.setItemText(1, QCoreApplication.translate("Dialog", u"6 decimales", None))
        self.comboDecimales.setItemText(2, QCoreApplication.translate("Dialog", u"8 decimales", None))
        self.comboDecimales.setItemText(3, QCoreApplication.translate("Dialog", u"12 decimales", None))
        self.comboDecimales.setItemText(4, QCoreApplication.translate("Dialog", u"Autom\u00e1tico", None))

        self.groupMuestreo.setTitle(QCoreApplication.translate("Dialog", u"Estrategia de discretizaci\u00f3n", None))
        self.comboEstrategiaMuestreoLabel.setText(QCoreApplication.translate("Dialog", u"Estrategia", None))
        self.comboEstrategiaMuestreo.setItemText(0, QCoreApplication.translate("Dialog", u"Adaptativa por tolerancia", None))
        self.comboEstrategiaMuestreo.setItemText(1, QCoreApplication.translate("Dialog", u"Uniforme por muestras", None))

        self.lblNumMuestras.setText(QCoreApplication.translate("Dialog", u"Muestras por perfil:", None))
        self.lblMaxMuestras.setText(QCoreApplication.translate("Dialog", u"M\u00e1ximo adaptativo:", None))
        self.groupDesviaciones.setTitle(QCoreApplication.translate("Dialog", u"Desviaciones de simulaci\u00f3n", None))
        self.desviacionLinealTxt.setText(QCoreApplication.translate("Dialog", u"Desviaci\u00f3n lineal", None))
        self.desviacionLinealSpin.setSuffix(QCoreApplication.translate("Dialog", u" mm", None))
        self.desviacionAngularTxt.setText(QCoreApplication.translate("Dialog", u"Desviaci\u00f3n angular", None))
        self.desviacionAngularSpin.setSuffix(QCoreApplication.translate("Dialog", u" \u00b0", None))
        self.chkMostrarEstimacion.setText(QCoreApplication.translate("Dialog", u"Mostrar estimaci\u00f3n del n\u00famero de muestras y costo de c\u00e1lculo", None))
        self.groupEstimacionCosto.setTitle(QCoreApplication.translate("Dialog", u"Estimaci\u00f3n y discretizaci\u00f3n", None))
        self.lblCalculoExplicacion.setText(QCoreApplication.translate("Dialog", u"Los controles existentes de decimales y muestreo se conservan. Los resultados siguientes deber\u00e1n calcularse mediante los motores reales; nunca deben confundirse con mediciones.", None))
        self.lblTituloMuestrasPrevistas.setText(QCoreApplication.translate("Dialog", u"Muestras estimadas:", None))
        self.lblEstimacionMuestras.setText(QCoreApplication.translate("Dialog", u"\u2014 (no calculado)", None))
        self.lblTituloCostoPrevisto.setText(QCoreApplication.translate("Dialog", u"Costo de c\u00e1lculo:", None))
        self.lblEstimacionCosto.setText(QCoreApplication.translate("Dialog", u"\u2014 (sin estimaci\u00f3n)", None))
        self.lblMetodoEstimacion.setText(QCoreApplication.translate("Dialog", u"M\u00e9todo y fiabilidad de la estimaci\u00f3n: pendientes de integrar.", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("Dialog", u"C\u00e1lculo y precisi\u00f3n", None))
        self.groupRender.setTitle(QCoreApplication.translate("Dialog", u"Renderizado", None))
        self.comboRenderLabel.setText(QCoreApplication.translate("Dialog", u"Motor de renderizado", None))
        self.comboRender.setItemText(0, QCoreApplication.translate("Dialog", u"Software", None))
        self.comboRender.setItemText(1, QCoreApplication.translate("Dialog", u"OpenGL", None))

        self.groupCadencia.setTitle(QCoreApplication.translate("Dialog", u"Actualizaci\u00f3n visual", None))
        self.comboFPSLabel.setText(QCoreApplication.translate("Dialog", u"L\u00edmite de FPS", None))
        self.comboFPS.setItemText(0, QCoreApplication.translate("Dialog", u"Autom\u00e1tico (monitor activo)", None))
        self.comboFPS.setItemText(1, QCoreApplication.translate("Dialog", u"30 FPS", None))
        self.comboFPS.setItemText(2, QCoreApplication.translate("Dialog", u"60 FPS", None))
        self.comboFPS.setItemText(3, QCoreApplication.translate("Dialog", u"75 FPS", None))
        self.comboFPS.setItemText(4, QCoreApplication.translate("Dialog", u"90 FPS", None))
        self.comboFPS.setItemText(5, QCoreApplication.translate("Dialog", u"120 FPS", None))
        self.comboFPS.setItemText(6, QCoreApplication.translate("Dialog", u"144 FPS", None))
        self.comboFPS.setItemText(7, QCoreApplication.translate("Dialog", u"165 FPS", None))
        self.comboFPS.setItemText(8, QCoreApplication.translate("Dialog", u"240 FPS", None))
        self.comboFPS.setItemText(9, QCoreApplication.translate("Dialog", u"Personalizado", None))
        self.comboFPS.setItemText(10, QCoreApplication.translate("Dialog", u"Sin l\u00edmite (Uncapped)", None))

        self.lblFPSCustom.setText(QCoreApplication.translate("Dialog", u"FPS personalizados:", None))
        self.lblMonitorHz.setStyleSheet(QCoreApplication.translate("Dialog", u"color: #A5B4C9; font-size: 12px;", None))
        self.lblMonitorHz.setText(QCoreApplication.translate("Dialog", u"Monitor activo: frecuencia por detectar en ejecuci\u00f3n", None))
        self.chkVSync.setText(QCoreApplication.translate("Dialog", u"Solicitar sincronizaci\u00f3n vertical (V-Sync)", None))
        self.groupProcesamiento.setTitle(QCoreApplication.translate("Dialog", u"Procesamiento matem\u00e1tico", None))
        self.comboBackendLabel.setText(QCoreApplication.translate("Dialog", u"Backend", None))
        self.comboBackend.setItemText(0, QCoreApplication.translate("Dialog", u"CPU \u2014 NumPy", None))
        self.comboBackend.setItemText(1, QCoreApplication.translate("Dialog", u"GPU \u2014 CuPy", None))
        self.comboBackend.setItemText(2, QCoreApplication.translate("Dialog", u"H\u00edbrido \u2014 autom\u00e1tico", None))

        self.groupSimComportamiento.setTitle(QCoreApplication.translate("Dialog", u"Comportamiento", None))
        self.chkBajarFPSInactivo_2.setText(QCoreApplication.translate("Dialog", u"Modo seguro para banco de pruebas", None))
        self.chkBajarFPSInactivo.setText(QCoreApplication.translate("Dialog", u"Reducir actualizaciones si la ventana est\u00e1 inactiva", None))
        self.chkDetenerInvalido.setText(QCoreApplication.translate("Dialog", u"Detener simulaci\u00f3n ante un estado matem\u00e1ticamente inv\u00e1lido", None))
        self.chkConservarPausa.setText(QCoreApplication.translate("Dialog", u"Conservar resultados calculados al pausar", None))
        self.chkCacheGeometria.setText(QCoreApplication.translate("Dialog", u"Reutilizar geometr\u00eda no modificada", None))
        self.groupAnalisisContacto.setTitle(QCoreApplication.translate("Dialog", u"Contacto y estudios de transmisi\u00f3n", None))
#if QT_CONFIG(tooltip)
        self.checkBox_3.setToolTip(QCoreApplication.translate("Dialog", u"Preferencia global del proyecto; los par\u00e1metros f\u00edsicos se configuran en el editor de reg\u00edmenes.", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_3.setText(QCoreApplication.translate("Dialog", u"Habilitar an\u00e1lisis basado en contacto (mayor costo de c\u00e1lculo)", None))
        self.lblAccesoEditorRegimenes.setText(QCoreApplication.translate("Dialog", u"Los par\u00e1metros del motor, las curvas de par y las propiedades de contacto pertenecen a cada estudio y se guardar\u00e1n con el proyecto.", None))
#if QT_CONFIG(tooltip)
        self.btnAbrirEditorRegimenes.setToolTip(QCoreApplication.translate("Dialog", u"Disponible despu\u00e9s de conectar este bot\u00f3n con VentanaPerfilVelocidad en Python.", None))
#endif // QT_CONFIG(tooltip)
        self.btnAbrirEditorRegimenes.setText(QCoreApplication.translate("Dialog", u"Abrir editor de reg\u00edmenes\u2026", None))
        self.lblEstadoContactoAjustes.setText(QCoreApplication.translate("Dialog", u"Activar esta opci\u00f3n permite trabajar con estudios de contacto desde el editor de reg\u00edmenes. El an\u00e1lisis cuasiest\u00e1tico inicial no requiere inercias; no calcula impactos ni vibraciones.", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("Dialog", u"Simulaci\u00f3n y rendimiento", None))
        self.comboTemaLabel.setText(QCoreApplication.translate("Dialog", u"Preset global", None))
        self.comboTema.setItemText(0, QCoreApplication.translate("Dialog", u"Oscuro", None))
        self.comboTema.setItemText(1, QCoreApplication.translate("Dialog", u"Claro", None))
        self.comboTema.setItemText(2, QCoreApplication.translate("Dialog", u"Alto contraste", None))
        self.comboTema.setItemText(3, QCoreApplication.translate("Dialog", u"Azul profundo \u2014 RPS", None))
        self.comboTema.setItemText(4, QCoreApplication.translate("Dialog", u"Deuteranopia", None))
        self.comboTema.setItemText(5, QCoreApplication.translate("Dialog", u"Protanopia", None))
        self.comboTema.setItemText(6, QCoreApplication.translate("Dialog", u"Tritanopia", None))
        self.comboTema.setItemText(7, QCoreApplication.translate("Dialog", u"Blanco y negro", None))
        self.comboTema.setItemText(8, QCoreApplication.translate("Dialog", u"Escala de grises", None))
        self.comboTema.setItemText(9, QCoreApplication.translate("Dialog", u"Presentaci\u00f3n CAD", None))
        self.comboTema.setItemText(10, QCoreApplication.translate("Dialog", u"Plano t\u00e9cnico", None))
        self.comboTema.setItemText(11, QCoreApplication.translate("Dialog", u"An\u00e1lisis cinem\u00e1tico", None))
        self.comboTema.setItemText(12, QCoreApplication.translate("Dialog", u"Personalizado", None))

        self.btnGuardarTema.setText(QCoreApplication.translate("Dialog", u"Guardar como preset\u2026", None))
        self.btnDuplicarTema.setText(QCoreApplication.translate("Dialog", u"Duplicar", None))
        self.btnRestaurarTema.setText(QCoreApplication.translate("Dialog", u"Restaurar preset", None))
        self.tabApariencia.setTabText(self.tabApariencia.indexOf(self.tabTemas), QCoreApplication.translate("Dialog", u"Temas", None))
        ___qtreewidgetitem = self.treeColoresUI.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("Dialog", u"Valor HEX", None))
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("Dialog", u"Rol visual", None))

        __sortingEnabled = self.treeColoresUI.isSortingEnabled()
        self.treeColoresUI.setSortingEnabled(False)
        ___qtreewidgetitem1 = self.treeColoresUI.topLevelItem(0)
        ___qtreewidgetitem1.setText(1, QCoreApplication.translate("Dialog", u"#121C2B", None))
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("Dialog", u"Fondo de ventana", None))
        ___qtreewidgetitem2 = self.treeColoresUI.topLevelItem(1)
        ___qtreewidgetitem2.setText(1, QCoreApplication.translate("Dialog", u"#19283B", None))
        ___qtreewidgetitem2.setText(0, QCoreApplication.translate("Dialog", u"Paneles / tarjetas", None))
        ___qtreewidgetitem3 = self.treeColoresUI.topLevelItem(2)
        ___qtreewidgetitem3.setText(1, QCoreApplication.translate("Dialog", u"#243E5A", None))
        ___qtreewidgetitem3.setText(0, QCoreApplication.translate("Dialog", u"Botones", None))
        ___qtreewidgetitem4 = self.treeColoresUI.topLevelItem(3)
        ___qtreewidgetitem4.setText(1, QCoreApplication.translate("Dialog", u"#EDF3FC", None))
        ___qtreewidgetitem4.setText(0, QCoreApplication.translate("Dialog", u"Texto principal", None))
        ___qtreewidgetitem5 = self.treeColoresUI.topLevelItem(4)
        ___qtreewidgetitem5.setText(1, QCoreApplication.translate("Dialog", u"#A5B4C9", None))
        ___qtreewidgetitem5.setText(0, QCoreApplication.translate("Dialog", u"Texto secundario", None))
        ___qtreewidgetitem6 = self.treeColoresUI.topLevelItem(5)
        ___qtreewidgetitem6.setText(1, QCoreApplication.translate("Dialog", u"#0E1D2F", None))
        ___qtreewidgetitem6.setText(0, QCoreApplication.translate("Dialog", u"Campos de entrada", None))
        ___qtreewidgetitem7 = self.treeColoresUI.topLevelItem(6)
        ___qtreewidgetitem7.setText(1, QCoreApplication.translate("Dialog", u"#19283B", None))
        ___qtreewidgetitem7.setText(0, QCoreApplication.translate("Dialog", u"Men\u00fas contextuales", None))
        ___qtreewidgetitem8 = self.treeColoresUI.topLevelItem(7)
        ___qtreewidgetitem8.setText(1, QCoreApplication.translate("Dialog", u"#0E1D2F", None))
        ___qtreewidgetitem8.setText(0, QCoreApplication.translate("Dialog", u"Tablas: fondo", None))
        ___qtreewidgetitem9 = self.treeColoresUI.topLevelItem(8)
        ___qtreewidgetitem9.setText(1, QCoreApplication.translate("Dialog", u"#30547A", None))
        ___qtreewidgetitem9.setText(0, QCoreApplication.translate("Dialog", u"Selecci\u00f3n", None))
        ___qtreewidgetitem10 = self.treeColoresUI.topLevelItem(9)
        ___qtreewidgetitem10.setText(1, QCoreApplication.translate("Dialog", u"#35435A", None))
        ___qtreewidgetitem10.setText(0, QCoreApplication.translate("Dialog", u"Bordes", None))
        ___qtreewidgetitem11 = self.treeColoresUI.topLevelItem(10)
        ___qtreewidgetitem11.setText(1, QCoreApplication.translate("Dialog", u"#EDF3FC", None))
        ___qtreewidgetitem11.setText(0, QCoreApplication.translate("Dialog", u"Iconos", None))
        ___qtreewidgetitem12 = self.treeColoresUI.topLevelItem(11)
        ___qtreewidgetitem12.setText(1, QCoreApplication.translate("Dialog", u"#E88C36", None))
        ___qtreewidgetitem12.setText(0, QCoreApplication.translate("Dialog", u"Aviso / advertencia", None))
        ___qtreewidgetitem13 = self.treeColoresUI.topLevelItem(12)
        ___qtreewidgetitem13.setText(1, QCoreApplication.translate("Dialog", u"#4EA77D", None))
        ___qtreewidgetitem13.setText(0, QCoreApplication.translate("Dialog", u"\u00c9xito / estado", None))
        ___qtreewidgetitem14 = self.treeColoresUI.topLevelItem(13)
        ___qtreewidgetitem14.setText(1, QCoreApplication.translate("Dialog", u"#D96D6D", None))
        ___qtreewidgetitem14.setText(0, QCoreApplication.translate("Dialog", u"Error / estado", None))
        self.treeColoresUI.setSortingEnabled(__sortingEnabled)

        self.lblColorUISeleccion.setText(QCoreApplication.translate("Dialog", u"Selecciona un rol para modificarlo.", None))
        self.btnColorUI.setText(QCoreApplication.translate("Dialog", u"Elegir color\u2026", None))
        self.tabApariencia.setTabText(self.tabApariencia.indexOf(self.tabColoresUI), QCoreApplication.translate("Dialog", u"Colores UI", None))
        self.lblColorTecnicoAyuda.setStyleSheet(QCoreApplication.translate("Dialog", u"color: #A5B4C9; font-size: 12px;", None))
        self.lblColorTecnicoAyuda.setText(QCoreApplication.translate("Dialog", u"Estos estilos se aplican a los elementos mec\u00e1nicos donde est\u00e9n presentes, sin cambiar su visibilidad.", None))
        ___qtreewidgetitem15 = self.treeColoresTecnicos.headerItem()
        ___qtreewidgetitem15.setText(1, QCoreApplication.translate("Dialog", u"Valor HEX", None))
        ___qtreewidgetitem15.setText(0, QCoreApplication.translate("Dialog", u"Elemento geom\u00e9trico", None))

        __sortingEnabled1 = self.treeColoresTecnicos.isSortingEnabled()
        self.treeColoresTecnicos.setSortingEnabled(False)
        ___qtreewidgetitem16 = self.treeColoresTecnicos.topLevelItem(0)
        ___qtreewidgetitem16.setText(1, QCoreApplication.translate("Dialog", u"#388AE6", None))
        ___qtreewidgetitem16.setText(0, QCoreApplication.translate("Dialog", u"Perfil / engranaje", None))
        ___qtreewidgetitem17 = self.treeColoresTecnicos.topLevelItem(1)
        ___qtreewidgetitem17.setText(1, QCoreApplication.translate("Dialog", u"#F2A33C", None))
        ___qtreewidgetitem17.setText(0, QCoreApplication.translate("Dialog", u"Pi\u00f1\u00f3n de rodillos", None))
        ___qtreewidgetitem18 = self.treeColoresTecnicos.topLevelItem(2)
        ___qtreewidgetitem18.setText(1, QCoreApplication.translate("Dialog", u"#F1D16B", None))
        ___qtreewidgetitem18.setText(0, QCoreApplication.translate("Dialog", u"Rodillos activos", None))
        ___qtreewidgetitem19 = self.treeColoresTecnicos.topLevelItem(3)
        ___qtreewidgetitem19.setText(1, QCoreApplication.translate("Dialog", u"#E96363", None))
        ___qtreewidgetitem19.setText(0, QCoreApplication.translate("Dialog", u"Puntos de contacto", None))
        ___qtreewidgetitem20 = self.treeColoresTecnicos.topLevelItem(4)
        ___qtreewidgetitem20.setText(1, QCoreApplication.translate("Dialog", u"#AF85D5", None))
        ___qtreewidgetitem20.setText(0, QCoreApplication.translate("Dialog", u"L\u00ednea de acci\u00f3n", None))
        ___qtreewidgetitem21 = self.treeColoresTecnicos.topLevelItem(5)
        ___qtreewidgetitem21.setText(1, QCoreApplication.translate("Dialog", u"#5DA878", None))
        ___qtreewidgetitem21.setText(0, QCoreApplication.translate("Dialog", u"Curva base", None))
        ___qtreewidgetitem22 = self.treeColoresTecnicos.topLevelItem(6)
        ___qtreewidgetitem22.setText(1, QCoreApplication.translate("Dialog", u"#CE73CB", None))
        ___qtreewidgetitem22.setText(0, QCoreApplication.translate("Dialog", u"Camino de contacto", None))
        ___qtreewidgetitem23 = self.treeColoresTecnicos.topLevelItem(7)
        ___qtreewidgetitem23.setText(1, QCoreApplication.translate("Dialog", u"#8794A2", None))
        ___qtreewidgetitem23.setText(0, QCoreApplication.translate("Dialog", u"Circunferencias de paso", None))
        ___qtreewidgetitem24 = self.treeColoresTecnicos.topLevelItem(8)
        ___qtreewidgetitem24.setText(1, QCoreApplication.translate("Dialog", u"#B8C2CD", None))
        ___qtreewidgetitem24.setText(0, QCoreApplication.translate("Dialog", u"Ejes de coordenadas", None))
        ___qtreewidgetitem25 = self.treeColoresTecnicos.topLevelItem(9)
        ___qtreewidgetitem25.setText(1, QCoreApplication.translate("Dialog", u"#536273", None))
        ___qtreewidgetitem25.setText(0, QCoreApplication.translate("Dialog", u"Cuadr\u00edcula", None))
        ___qtreewidgetitem26 = self.treeColoresTecnicos.topLevelItem(10)
        ___qtreewidgetitem26.setText(1, QCoreApplication.translate("Dialog", u"#1C1C21", None))
        ___qtreewidgetitem26.setText(0, QCoreApplication.translate("Dialog", u"Fondo de gr\u00e1ficas", None))
        ___qtreewidgetitem27 = self.treeColoresTecnicos.topLevelItem(11)
        ___qtreewidgetitem27.setText(1, QCoreApplication.translate("Dialog", u"#EBEFF5", None))
        ___qtreewidgetitem27.setText(0, QCoreApplication.translate("Dialog", u"Etiquetas", None))
        ___qtreewidgetitem28 = self.treeColoresTecnicos.topLevelItem(12)
        ___qtreewidgetitem28.setText(1, QCoreApplication.translate("Dialog", u"#388AE6", None))
        ___qtreewidgetitem28.setText(0, QCoreApplication.translate("Dialog", u"Sol", None))
        ___qtreewidgetitem29 = self.treeColoresTecnicos.topLevelItem(13)
        ___qtreewidgetitem29.setText(1, QCoreApplication.translate("Dialog", u"#6EC78A", None))
        ___qtreewidgetitem29.setText(0, QCoreApplication.translate("Dialog", u"Anular", None))
        ___qtreewidgetitem30 = self.treeColoresTecnicos.topLevelItem(14)
        ___qtreewidgetitem30.setText(1, QCoreApplication.translate("Dialog", u"#F2A33C", None))
        ___qtreewidgetitem30.setText(0, QCoreApplication.translate("Dialog", u"Planetas", None))
        self.treeColoresTecnicos.setSortingEnabled(__sortingEnabled1)

        self.lblColorTecnicoSeleccion.setText(QCoreApplication.translate("Dialog", u"Selecciona un elemento para modificarlo.", None))
        self.btnColorTecnico.setText(QCoreApplication.translate("Dialog", u"Elegir color\u2026", None))
        self.tabApariencia.setTabText(self.tabApariencia.indexOf(self.tabColoresTecnicos), QCoreApplication.translate("Dialog", u"Colores t\u00e9cnicos", None))
        self.comboTipoCurvaLabel.setText(QCoreApplication.translate("Dialog", u"Elemento", None))
        self.comboTipoCurva.setItemText(0, QCoreApplication.translate("Dialog", u"Perfil de engranaje", None))
        self.comboTipoCurva.setItemText(1, QCoreApplication.translate("Dialog", u"Pi\u00f1\u00f3n", None))
        self.comboTipoCurva.setItemText(2, QCoreApplication.translate("Dialog", u"Rodillos activos", None))
        self.comboTipoCurva.setItemText(3, QCoreApplication.translate("Dialog", u"Camino de contacto", None))
        self.comboTipoCurva.setItemText(4, QCoreApplication.translate("Dialog", u"Curva base", None))
        self.comboTipoCurva.setItemText(5, QCoreApplication.translate("Dialog", u"Circunferencias de paso", None))
        self.comboTipoCurva.setItemText(6, QCoreApplication.translate("Dialog", u"L\u00ednea de acci\u00f3n", None))
        self.comboTipoCurva.setItemText(7, QCoreApplication.translate("Dialog", u"Ejes", None))
        self.comboTipoCurva.setItemText(8, QCoreApplication.translate("Dialog", u"Cuadr\u00edcula", None))

        self.lblAnchoLinea.setText(QCoreApplication.translate("Dialog", u"Espesor:", None))
        self.spinAnchoLinea.setSuffix(QCoreApplication.translate("Dialog", u" px", None))
        self.comboTipoLineaLabel.setText(QCoreApplication.translate("Dialog", u"Patr\u00f3n de l\u00ednea", None))
        self.comboTipoLinea.setItemText(0, QCoreApplication.translate("Dialog", u"Continua", None))
        self.comboTipoLinea.setItemText(1, QCoreApplication.translate("Dialog", u"Discontinua", None))
        self.comboTipoLinea.setItemText(2, QCoreApplication.translate("Dialog", u"Punteada", None))
        self.comboTipoLinea.setItemText(3, QCoreApplication.translate("Dialog", u"Raya-punto", None))
        self.comboTipoLinea.setItemText(4, QCoreApplication.translate("Dialog", u"Raya-punto-punto", None))

        self.comboLineCapLabel.setText(QCoreApplication.translate("Dialog", u"Terminaci\u00f3n", None))
        self.comboLineCap.setItemText(0, QCoreApplication.translate("Dialog", u"Plana", None))
        self.comboLineCap.setItemText(1, QCoreApplication.translate("Dialog", u"Redondeada", None))
        self.comboLineCap.setItemText(2, QCoreApplication.translate("Dialog", u"Cuadrada", None))

        self.comboLineJoinLabel.setText(QCoreApplication.translate("Dialog", u"Uni\u00f3n", None))
        self.comboLineJoin.setItemText(0, QCoreApplication.translate("Dialog", u"Bisel", None))
        self.comboLineJoin.setItemText(1, QCoreApplication.translate("Dialog", u"Redondeada", None))
        self.comboLineJoin.setItemText(2, QCoreApplication.translate("Dialog", u"Inglete", None))

        self.lblOpacidad.setText(QCoreApplication.translate("Dialog", u"Opacidad:", None))
        self.spinOpacidad.setSuffix(QCoreApplication.translate("Dialog", u" %", None))
        self.chkAntialias.setText(QCoreApplication.translate("Dialog", u"Antialiasing (suavizado de l\u00edneas)", None))
        self.tabApariencia.setTabText(self.tabApariencia.indexOf(self.tabTrazos), QCoreApplication.translate("Dialog", u"Trazos", None))
        self.groupFuenteUI.setTitle(QCoreApplication.translate("Dialog", u"Fuente de la interfaz", None))
        self.lblFontUI.setText(QCoreApplication.translate("Dialog", u"Familia:", None))
        self.spinTamanoUI.setSuffix(QCoreApplication.translate("Dialog", u" pt", None))
        self.chkFuenteUIBold.setText(QCoreApplication.translate("Dialog", u"Negrita general", None))
        self.groupFuenteGrafica.setTitle(QCoreApplication.translate("Dialog", u"Fuente de gr\u00e1ficas", None))
        self.lblFontPlot.setText(QCoreApplication.translate("Dialog", u"Familia:", None))
        self.spinTamanoGrafica.setSuffix(QCoreApplication.translate("Dialog", u" pt", None))
        self.chkFuenteGraficaBold.setText(QCoreApplication.translate("Dialog", u"Negrita en etiquetas", None))
        self.tabApariencia.setTabText(self.tabApariencia.indexOf(self.tabFuentes), QCoreApplication.translate("Dialog", u"Tipograf\u00eda", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("Dialog", u"Apariencia y estilos", None))
        self.groupVideo.setTitle(QCoreApplication.translate("Dialog", u"Videos de simulaci\u00f3n", None))
        self.comboFormatoVideoLabel.setText(QCoreApplication.translate("Dialog", u"Formato de video", None))
        self.comboFormatoVideo.setItemText(0, QCoreApplication.translate("Dialog", u"MP4 \u2014 H.264", None))
        self.comboFormatoVideo.setItemText(1, QCoreApplication.translate("Dialog", u"WebM \u2014 VP9 (por implementar)", None))

        self.comboResolucionVideoLabel.setText(QCoreApplication.translate("Dialog", u"Resoluci\u00f3n", None))
        self.lblVidDims.setText(QCoreApplication.translate("Dialog", u"Personalizada:", None))
        self.spinVidAncho.setSuffix(QCoreApplication.translate("Dialog", u" px", None))
        self.lblVidX.setText(QCoreApplication.translate("Dialog", u"\u00d7", None))
        self.spinVidAlto.setSuffix(QCoreApplication.translate("Dialog", u" px", None))
        self.comboFPSVideoLabel.setText(QCoreApplication.translate("Dialog", u"FPS de video", None))
        self.comboCRFVideoLabel.setText(QCoreApplication.translate("Dialog", u"Calidad H.264", None))
        self.chkRelacionVideo.setText(QCoreApplication.translate("Dialog", u"Conservar proporci\u00f3n de aspecto", None))
        self.chkVideoDeterminista.setText(QCoreApplication.translate("Dialog", u"Renderizar fotogramas seg\u00fan el tiempo simulado", None))
        self.groupImagen.setTitle(QCoreApplication.translate("Dialog", u"Im\u00e1genes y gr\u00e1ficos", None))
        self.comboFormatoImagenLabel.setText(QCoreApplication.translate("Dialog", u"Formato predeterminado", None))
        self.comboFormatoImagen.setItemText(0, QCoreApplication.translate("Dialog", u"PNG", None))
        self.comboFormatoImagen.setItemText(1, QCoreApplication.translate("Dialog", u"JPEG", None))
        self.comboFormatoImagen.setItemText(2, QCoreApplication.translate("Dialog", u"SVG", None))
        self.comboFormatoImagen.setItemText(3, QCoreApplication.translate("Dialog", u"PDF", None))

        self.comboResolucionImagenLabel.setText(QCoreApplication.translate("Dialog", u"Resoluci\u00f3n", None))
        self.comboResolucionImagen.setItemText(0, QCoreApplication.translate("Dialog", u"Original / tama\u00f1o de gr\u00e1fica", None))
        self.comboResolucionImagen.setItemText(1, QCoreApplication.translate("Dialog", u"1920 \u00d7 1080 (Full HD)", None))
        self.comboResolucionImagen.setItemText(2, QCoreApplication.translate("Dialog", u"2560 \u00d7 1440 (QHD)", None))
        self.comboResolucionImagen.setItemText(3, QCoreApplication.translate("Dialog", u"3840 \u00d7 2160 (4K)", None))
        self.comboResolucionImagen.setItemText(4, QCoreApplication.translate("Dialog", u"Personalizada", None))

        self.lblImgDims.setText(QCoreApplication.translate("Dialog", u"Personalizada:", None))
        self.spinImgAncho.setSuffix(QCoreApplication.translate("Dialog", u" px", None))
        self.lblPor.setText(QCoreApplication.translate("Dialog", u"\u00d7", None))
        self.spinImgAlto.setSuffix(QCoreApplication.translate("Dialog", u" px", None))
        self.lblJpeg.setText(QCoreApplication.translate("Dialog", u"Calidad JPEG:", None))
        self.spinJpeg.setSuffix(QCoreApplication.translate("Dialog", u" %", None))
        self.chkMantenerAspectoImagen.setText(QCoreApplication.translate("Dialog", u"Mantener proporci\u00f3n de aspecto", None))
        self.chkFondoTransparente.setText(QCoreApplication.translate("Dialog", u"Fondo transparente cuando el formato lo permita", None))
        self.chkAntialiasExport.setText(QCoreApplication.translate("Dialog", u"Antialiasing de alta calidad", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), QCoreApplication.translate("Dialog", u"Exportaci\u00f3n", None))
        self.pushButton_4.setText(QCoreApplication.translate("Dialog", u"Aceptar", None))
        self.pushButton.setText(QCoreApplication.translate("Dialog", u"Restaurar Predeterminados", None))
    # retranslateUi

