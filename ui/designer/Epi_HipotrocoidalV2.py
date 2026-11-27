# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Epi_HipotrocoidalV2.ui'
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
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QCheckBox, QComboBox,
    QDial, QDoubleSpinBox, QFrame, QGraphicsView,
    QGridLayout, QGroupBox, QLabel, QMainWindow,
    QMenu, QMenuBar, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QStatusBar, QToolBar,
    QWidget)

class Ui_Epi_HipotrocoidalV2(object):
    def setupUi(self, Epi_HipotrocoidalV2):
        if not Epi_HipotrocoidalV2.objectName():
            Epi_HipotrocoidalV2.setObjectName(u"Epi_HipotrocoidalV2")
        Epi_HipotrocoidalV2.resize(1281, 831)
        self.actionAbrir = QAction(Epi_HipotrocoidalV2)
        self.actionAbrir.setObjectName(u"actionAbrir")
        self.actionGuardar = QAction(Epi_HipotrocoidalV2)
        self.actionGuardar.setObjectName(u"actionGuardar")
        self.actionGuardar_Como = QAction(Epi_HipotrocoidalV2)
        self.actionGuardar_Como.setObjectName(u"actionGuardar_Como")
        self.actionExportar = QAction(Epi_HipotrocoidalV2)
        self.actionExportar.setObjectName(u"actionExportar")
        self.actionCerrar = QAction(Epi_HipotrocoidalV2)
        self.actionCerrar.setObjectName(u"actionCerrar")
        self.actionResolucion = QAction(Epi_HipotrocoidalV2)
        self.actionResolucion.setObjectName(u"actionResolucion")
        self.actionGu_a_T_cnica = QAction(Epi_HipotrocoidalV2)
        self.actionGu_a_T_cnica.setObjectName(u"actionGu_a_T_cnica")
        self.actionOpen_GL = QAction(Epi_HipotrocoidalV2)
        self.actionOpen_GL.setObjectName(u"actionOpen_GL")
        self.actionActivar_GPU = QAction(Epi_HipotrocoidalV2)
        self.actionActivar_GPU.setObjectName(u"actionActivar_GPU")
        self.actionOscuro = QAction(Epi_HipotrocoidalV2)
        self.actionOscuro.setObjectName(u"actionOscuro")
        self.actionClaro = QAction(Epi_HipotrocoidalV2)
        self.actionClaro.setObjectName(u"actionClaro")
        self.actionPerfil_del_diente = QAction(Epi_HipotrocoidalV2)
        self.actionPerfil_del_diente.setObjectName(u"actionPerfil_del_diente")
        self.action_ngulo_de_Presi_n = QAction(Epi_HipotrocoidalV2)
        self.action_ngulo_de_Presi_n.setObjectName(u"action_ngulo_de_Presi_n")
        self.actionRadio_de_Curvatura = QAction(Epi_HipotrocoidalV2)
        self.actionRadio_de_Curvatura.setObjectName(u"actionRadio_de_Curvatura")
        self.actionCamino_de_Contacto = QAction(Epi_HipotrocoidalV2)
        self.actionCamino_de_Contacto.setObjectName(u"actionCamino_de_Contacto")
        self.actionConfiguraci_n = QAction(Epi_HipotrocoidalV2)
        self.actionConfiguraci_n.setObjectName(u"actionConfiguraci_n")
        self.actionResumen_de_Dise_o = QAction(Epi_HipotrocoidalV2)
        self.actionResumen_de_Dise_o.setObjectName(u"actionResumen_de_Dise_o")
        self.centralwidget = QWidget(Epi_HipotrocoidalV2)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QSize(260, 0))
        self.groupBox.setMouseTracking(False)
        self.groupBox.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        self.groupBox.setAcceptDrops(False)
        self.groupBox.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.spinBox_numeroderodillos = QSpinBox(self.groupBox)
        self.spinBox_numeroderodillos.setObjectName(u"spinBox_numeroderodillos")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.spinBox_numeroderodillos.sizePolicy().hasHeightForWidth())
        self.spinBox_numeroderodillos.setSizePolicy(sizePolicy1)
        self.spinBox_numeroderodillos.setMinimumSize(QSize(0, 40))
        self.spinBox_numeroderodillos.setMaximumSize(QSize(16777215, 35))
        self.spinBox_numeroderodillos.setMaximum(200)
        self.spinBox_numeroderodillos.setValue(12)

        self.gridLayout_2.addWidget(self.spinBox_numeroderodillos, 3, 0, 1, 2)

        self.doubleSpinBox_distancia_centros_rodillos = QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox_distancia_centros_rodillos.setObjectName(u"doubleSpinBox_distancia_centros_rodillos")
        sizePolicy1.setHeightForWidth(self.doubleSpinBox_distancia_centros_rodillos.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_distancia_centros_rodillos.setSizePolicy(sizePolicy1)
        self.doubleSpinBox_distancia_centros_rodillos.setMinimumSize(QSize(0, 40))
        self.doubleSpinBox_distancia_centros_rodillos.setMaximumSize(QSize(16777215, 35))
        self.doubleSpinBox_distancia_centros_rodillos.setDecimals(3)
        self.doubleSpinBox_distancia_centros_rodillos.setValue(8.500000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_distancia_centros_rodillos, 10, 0, 1, 2)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy2)
        self.label.setMinimumSize(QSize(0, 35))
        font = QFont()
        font.setFamilies([u"Bahnschrift"])
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 2)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        sizePolicy2.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy2)
        self.label_2.setMinimumSize(QSize(0, 30))
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_2, 2, 0, 1, 2)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        sizePolicy2.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy2)
        self.label_3.setMinimumSize(QSize(0, 35))
        self.label_3.setFont(font)
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_3, 5, 0, 1, 2)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")
        sizePolicy2.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy2)
        self.label_4.setMinimumSize(QSize(0, 35))
        self.label_4.setFont(font)
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_4, 7, 0, 1, 2)

        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")
        sizePolicy2.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy2)
        self.label_6.setMinimumSize(QSize(0, 35))
        self.label_6.setFont(font)
        self.label_6.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_6, 11, 0, 1, 2)

        self.doubleSpinBox_diametro_rodillos = QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox_diametro_rodillos.setObjectName(u"doubleSpinBox_diametro_rodillos")
        sizePolicy1.setHeightForWidth(self.doubleSpinBox_diametro_rodillos.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_diametro_rodillos.setSizePolicy(sizePolicy1)
        self.doubleSpinBox_diametro_rodillos.setMinimumSize(QSize(0, 40))
        self.doubleSpinBox_diametro_rodillos.setMaximumSize(QSize(16777215, 35))
        self.doubleSpinBox_diametro_rodillos.setDecimals(3)
        self.doubleSpinBox_diametro_rodillos.setValue(3.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_diametro_rodillos, 6, 0, 1, 2)

        self.doubleSpinBox_angulo_presion_minimo = QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox_angulo_presion_minimo.setObjectName(u"doubleSpinBox_angulo_presion_minimo")
        sizePolicy1.setHeightForWidth(self.doubleSpinBox_angulo_presion_minimo.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_angulo_presion_minimo.setSizePolicy(sizePolicy1)
        self.doubleSpinBox_angulo_presion_minimo.setMinimumSize(QSize(0, 40))
        self.doubleSpinBox_angulo_presion_minimo.setMaximumSize(QSize(16777215, 35))
        self.doubleSpinBox_angulo_presion_minimo.setDecimals(3)
        self.doubleSpinBox_angulo_presion_minimo.setMinimum(1.000000000000000)
        self.doubleSpinBox_angulo_presion_minimo.setMaximum(45.000000000000000)
        self.doubleSpinBox_angulo_presion_minimo.setValue(17.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_angulo_presion_minimo, 12, 0, 1, 2)

        self.spinBox_numerodedientes = QSpinBox(self.groupBox)
        self.spinBox_numerodedientes.setObjectName(u"spinBox_numerodedientes")
        sizePolicy1.setHeightForWidth(self.spinBox_numerodedientes.sizePolicy().hasHeightForWidth())
        self.spinBox_numerodedientes.setSizePolicy(sizePolicy1)
        self.spinBox_numerodedientes.setMinimumSize(QSize(0, 40))
        self.spinBox_numerodedientes.setMaximumSize(QSize(16777215, 35))
        self.spinBox_numerodedientes.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.spinBox_numerodedientes.setMaximum(200)
        self.spinBox_numerodedientes.setValue(12)

        self.gridLayout_2.addWidget(self.spinBox_numerodedientes, 1, 0, 1, 2)

        self.spinBox_numerodedientes.raise_()
        self.label.raise_()
        self.doubleSpinBox_angulo_presion_minimo.raise_()
        self.label_2.raise_()
        self.label_6.raise_()
        self.doubleSpinBox_diametro_rodillos.raise_()
        self.spinBox_numeroderodillos.raise_()
        self.doubleSpinBox_distancia_centros_rodillos.raise_()
        self.label_4.raise_()
        self.label_3.raise_()

        self.gridLayout.addWidget(self.groupBox, 1, 1, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(5, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_3, 1, 2, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(5, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 1, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(5, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 1, 4, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(5, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_4, 1, 6, 1, 1)

        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy3)
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_4 = QGridLayout(self.frame)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.graphicsView_epi = QGraphicsView(self.frame)
        self.graphicsView_epi.setObjectName(u"graphicsView_epi")

        self.gridLayout_4.addWidget(self.graphicsView_epi, 0, 1, 1, 6)


        self.gridLayout.addWidget(self.frame, 0, 3, 3, 1)

        self.frame_3 = QFrame(self.centralwidget)
        self.frame_3.setObjectName(u"frame_3")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy4)
        self.frame_3.setMinimumSize(QSize(0, 0))
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_6 = QGridLayout(self.frame_3)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.groupBox_2 = QGroupBox(self.frame_3)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy4.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy4)
        self.groupBox_2.setMaximumSize(QSize(300, 16777215))
        self.gridLayout_3 = QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.frame_anim_controls = QFrame(self.groupBox_2)
        self.frame_anim_controls.setObjectName(u"frame_anim_controls")
        self.frame_anim_controls.setEnabled(False)
        sizePolicy2.setHeightForWidth(self.frame_anim_controls.sizePolicy().hasHeightForWidth())
        self.frame_anim_controls.setSizePolicy(sizePolicy2)
        self.frame_anim_controls.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_anim_controls.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_12 = QGridLayout(self.frame_anim_controls)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.pushButton_record = QPushButton(self.frame_anim_controls)
        self.pushButton_record.setObjectName(u"pushButton_record")
        self.pushButton_record.setMinimumSize(QSize(50, 50))
        self.pushButton_record.setMaximumSize(QSize(50, 50))
        font1 = QFont()
        font1.setPointSize(22)
        self.pushButton_record.setFont(font1)

        self.gridLayout_12.addWidget(self.pushButton_record, 0, 4, 1, 1)

        self.pushButton_anim_play = QPushButton(self.frame_anim_controls)
        self.pushButton_anim_play.setObjectName(u"pushButton_anim_play")
        sizePolicy.setHeightForWidth(self.pushButton_anim_play.sizePolicy().hasHeightForWidth())
        self.pushButton_anim_play.setSizePolicy(sizePolicy)
        self.pushButton_anim_play.setMinimumSize(QSize(50, 50))
        self.pushButton_anim_play.setMaximumSize(QSize(50, 50))
        self.pushButton_anim_play.setFont(font1)

        self.gridLayout_12.addWidget(self.pushButton_anim_play, 0, 1, 1, 1)

        self.pushButton_anim_pause = QPushButton(self.frame_anim_controls)
        self.pushButton_anim_pause.setObjectName(u"pushButton_anim_pause")
        sizePolicy.setHeightForWidth(self.pushButton_anim_pause.sizePolicy().hasHeightForWidth())
        self.pushButton_anim_pause.setSizePolicy(sizePolicy)
        self.pushButton_anim_pause.setMinimumSize(QSize(50, 50))
        self.pushButton_anim_pause.setMaximumSize(QSize(50, 50))
        self.pushButton_anim_pause.setFont(font1)

        self.gridLayout_12.addWidget(self.pushButton_anim_pause, 0, 2, 1, 1)

        self.pushButton_restart = QPushButton(self.frame_anim_controls)
        self.pushButton_restart.setObjectName(u"pushButton_restart")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.pushButton_restart.sizePolicy().hasHeightForWidth())
        self.pushButton_restart.setSizePolicy(sizePolicy5)
        self.pushButton_restart.setMinimumSize(QSize(50, 50))
        self.pushButton_restart.setMaximumSize(QSize(50, 50))
        self.pushButton_restart.setFont(font1)

        self.gridLayout_12.addWidget(self.pushButton_restart, 0, 3, 1, 1)


        self.gridLayout_3.addWidget(self.frame_anim_controls, 0, 1, 1, 2)

        self.Editarlineadetiempo_button = QPushButton(self.groupBox_2)
        self.Editarlineadetiempo_button.setObjectName(u"Editarlineadetiempo_button")
        self.Editarlineadetiempo_button.setEnabled(False)

        self.gridLayout_3.addWidget(self.Editarlineadetiempo_button, 1, 0, 1, 4)

        self.checkBox_valpredeterminados = QCheckBox(self.groupBox_2)
        self.checkBox_valpredeterminados.setObjectName(u"checkBox_valpredeterminados")
        self.checkBox_valpredeterminados.setEnabled(False)
        self.checkBox_valpredeterminados.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.checkBox_valpredeterminados.setChecked(True)
        self.checkBox_valpredeterminados.setTristate(False)

        self.gridLayout_3.addWidget(self.checkBox_valpredeterminados, 2, 0, 1, 4)

        self.lblEstadoSolucionador = QLabel(self.groupBox_2)
        self.lblEstadoSolucionador.setObjectName(u"lblEstadoSolucionador")
        self.lblEstadoSolucionador.setWordWrap(True)

        self.gridLayout_3.addWidget(self.lblEstadoSolucionador, 3, 0, 1, 4)

        self.btnVerResultados = QPushButton(self.groupBox_2)
        self.btnVerResultados.setObjectName(u"btnVerResultados")
        self.btnVerResultados.setEnabled(False)

        self.gridLayout_3.addWidget(self.btnVerResultados, 4, 0, 1, 4)


        self.gridLayout_6.addWidget(self.groupBox_2, 4, 1, 1, 1)

        self.groupBox_5 = QGroupBox(self.frame_3)
        self.groupBox_5.setObjectName(u"groupBox_5")
        sizePolicy4.setHeightForWidth(self.groupBox_5.sizePolicy().hasHeightForWidth())
        self.groupBox_5.setSizePolicy(sizePolicy4)
        self.groupBox_5.setMinimumSize(QSize(0, 0))
        self.groupBox_5.setMaximumSize(QSize(300, 16777215))
        self.gridLayout_9 = QGridLayout(self.groupBox_5)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.label_5 = QLabel(self.groupBox_5)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy2)
        self.label_5.setMinimumSize(QSize(0, 30))
        self.label_5.setFont(font)
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_9.addWidget(self.label_5, 0, 1, 1, 2)

        self.doubleSpinBox_posicion_theta = QDoubleSpinBox(self.groupBox_5)
        self.doubleSpinBox_posicion_theta.setObjectName(u"doubleSpinBox_posicion_theta")
        self.doubleSpinBox_posicion_theta.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.doubleSpinBox_posicion_theta.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_posicion_theta.setSizePolicy(sizePolicy1)
        self.doubleSpinBox_posicion_theta.setMinimumSize(QSize(0, 40))
        self.doubleSpinBox_posicion_theta.setMaximumSize(QSize(16777215, 35))
        self.doubleSpinBox_posicion_theta.setDecimals(6)
        self.doubleSpinBox_posicion_theta.setMaximum(360.000000000000000)
        self.doubleSpinBox_posicion_theta.setSingleStep(0.500000000000000)

        self.gridLayout_9.addWidget(self.doubleSpinBox_posicion_theta, 3, 1, 1, 2)

        self.dial_posicion_theta = QDial(self.groupBox_5)
        self.dial_posicion_theta.setObjectName(u"dial_posicion_theta")
        self.dial_posicion_theta.setEnabled(True)
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

        self.gridLayout_9.addWidget(self.dial_posicion_theta, 6, 1, 1, 2)

        self.label_10 = QLabel(self.groupBox_5)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_9.addWidget(self.label_10, 1, 1, 1, 1)

        self.comboBox_modo_pinon = QComboBox(self.groupBox_5)
        self.comboBox_modo_pinon.addItem("")
        self.comboBox_modo_pinon.addItem("")
        self.comboBox_modo_pinon.setObjectName(u"comboBox_modo_pinon")

        self.gridLayout_9.addWidget(self.comboBox_modo_pinon, 1, 2, 1, 1)


        self.gridLayout_6.addWidget(self.groupBox_5, 2, 1, 1, 1)

        self.groupBox_4 = QGroupBox(self.frame_3)
        self.groupBox_4.setObjectName(u"groupBox_4")
        sizePolicy4.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy4)
        self.groupBox_4.setMaximumSize(QSize(300, 16777215))
        self.gridLayout_8 = QGridLayout(self.groupBox_4)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.pushButton_mostrar_ocultar = QPushButton(self.groupBox_4)
        self.pushButton_mostrar_ocultar.setObjectName(u"pushButton_mostrar_ocultar")

        self.gridLayout_8.addWidget(self.pushButton_mostrar_ocultar, 4, 0, 1, 2)

        self.pushButton_sim_reset = QPushButton(self.groupBox_4)
        self.pushButton_sim_reset.setObjectName(u"pushButton_sim_reset")

        self.gridLayout_8.addWidget(self.pushButton_sim_reset, 5, 0, 1, 2)

        self.comboBox_modo_sim = QComboBox(self.groupBox_4)
        self.comboBox_modo_sim.addItem("")
        self.comboBox_modo_sim.addItem("")
        self.comboBox_modo_sim.setObjectName(u"comboBox_modo_sim")

        self.gridLayout_8.addWidget(self.comboBox_modo_sim, 2, 1, 1, 1)

        self.label_11 = QLabel(self.groupBox_4)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout_8.addWidget(self.label_11, 2, 0, 1, 1)


        self.gridLayout_6.addWidget(self.groupBox_4, 0, 1, 1, 1)


        self.gridLayout.addWidget(self.frame_3, 0, 5, 3, 1)

        Epi_HipotrocoidalV2.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Epi_HipotrocoidalV2)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1281, 33))
        self.menuArchivo = QMenu(self.menubar)
        self.menuArchivo.setObjectName(u"menuArchivo")
        self.menuAyuda = QMenu(self.menubar)
        self.menuAyuda.setObjectName(u"menuAyuda")
        self.menuPropiedades_f_sicas = QMenu(self.menubar)
        self.menuPropiedades_f_sicas.setObjectName(u"menuPropiedades_f_sicas")
        Epi_HipotrocoidalV2.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(Epi_HipotrocoidalV2)
        self.statusbar.setObjectName(u"statusbar")
        Epi_HipotrocoidalV2.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(Epi_HipotrocoidalV2)
        self.toolBar.setObjectName(u"toolBar")
        Epi_HipotrocoidalV2.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)
        QWidget.setTabOrder(self.spinBox_numerodedientes, self.spinBox_numeroderodillos)
        QWidget.setTabOrder(self.spinBox_numeroderodillos, self.doubleSpinBox_diametro_rodillos)
        QWidget.setTabOrder(self.doubleSpinBox_diametro_rodillos, self.doubleSpinBox_distancia_centros_rodillos)
        QWidget.setTabOrder(self.doubleSpinBox_distancia_centros_rodillos, self.doubleSpinBox_angulo_presion_minimo)
        QWidget.setTabOrder(self.doubleSpinBox_angulo_presion_minimo, self.graphicsView_epi)
        QWidget.setTabOrder(self.graphicsView_epi, self.comboBox_modo_sim)
        QWidget.setTabOrder(self.comboBox_modo_sim, self.pushButton_mostrar_ocultar)
        QWidget.setTabOrder(self.pushButton_mostrar_ocultar, self.pushButton_sim_reset)
        QWidget.setTabOrder(self.pushButton_sim_reset, self.doubleSpinBox_posicion_theta)
        QWidget.setTabOrder(self.doubleSpinBox_posicion_theta, self.dial_posicion_theta)
        QWidget.setTabOrder(self.dial_posicion_theta, self.Editarlineadetiempo_button)
        QWidget.setTabOrder(self.Editarlineadetiempo_button, self.checkBox_valpredeterminados)
        QWidget.setTabOrder(self.checkBox_valpredeterminados, self.btnVerResultados)
        QWidget.setTabOrder(self.btnVerResultados, self.pushButton_anim_play)
        QWidget.setTabOrder(self.pushButton_anim_play, self.pushButton_anim_pause)

        self.menubar.addAction(self.menuArchivo.menuAction())
        self.menubar.addAction(self.menuPropiedades_f_sicas.menuAction())
        self.menubar.addAction(self.menuAyuda.menuAction())
        self.menuArchivo.addAction(self.actionAbrir)
        self.menuArchivo.addAction(self.actionGuardar)
        self.menuArchivo.addAction(self.actionExportar)
        self.menuArchivo.addAction(self.actionConfiguraci_n)
        self.menuArchivo.addAction(self.actionCerrar)
        self.menuAyuda.addAction(self.actionGu_a_T_cnica)
        self.menuAyuda.addAction(self.actionResumen_de_Dise_o)
        self.menuPropiedades_f_sicas.addAction(self.actionPerfil_del_diente)
        self.menuPropiedades_f_sicas.addAction(self.action_ngulo_de_Presi_n)
        self.menuPropiedades_f_sicas.addAction(self.actionRadio_de_Curvatura)
        self.menuPropiedades_f_sicas.addAction(self.actionCamino_de_Contacto)

        self.retranslateUi(Epi_HipotrocoidalV2)

        QMetaObject.connectSlotsByName(Epi_HipotrocoidalV2)
    # setupUi

    def retranslateUi(self, Epi_HipotrocoidalV2):
        Epi_HipotrocoidalV2.setWindowTitle(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Epi_Hipotrocoidal", None))
        self.actionAbrir.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Abrir", None))
        self.actionGuardar.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Guardar", None))
        self.actionGuardar_Como.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Guardar Como", None))
        self.actionExportar.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Exportar", None))
        self.actionCerrar.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Cerrar", None))
        self.actionResolucion.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Resoluci\u00f3n", None))
        self.actionGu_a_T_cnica.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Gu\u00eda T\u00e9cnica", None))
        self.actionOpen_GL.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"OpenGL", None))
        self.actionActivar_GPU.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Activar GPU", None))
        self.actionOscuro.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Oscuro", None))
        self.actionClaro.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Claro", None))
        self.actionPerfil_del_diente.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Perfil del diente", None))
        self.action_ngulo_de_Presi_n.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"\u00c1ngulo de Presi\u00f3n", None))
        self.actionRadio_de_Curvatura.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Radio de Curvatura", None))
        self.actionCamino_de_Contacto.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Camino de Contacto", None))
        self.actionConfiguraci_n.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Ajustes", None))
        self.actionResumen_de_Dise_o.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Resumen de Dise\u00f1o", None))
        self.groupBox.setTitle(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Par\u00e1metros Principales ", None))
        self.label.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"N\u00famero de dientes \n"
"(Engranaje Externo)", None))
        self.label_2.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"N\u00famero de rodillos", None))
        self.label_3.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Di\u00e1metro de rodillos \n"
"(mm)", None))
        self.label_4.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Distancia entre centros de rodillos \n"
"(mm)", None))
        self.label_6.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"\u00c1ngulo de Presi\u00f3n m\u00ednimo \n"
"(\u00b0) [1\u00b0,45\u00b0]", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Control Autom\u00e1tico", None))
        self.pushButton_record.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"\U0001f534", None))
        self.pushButton_anim_play.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"\u25b6\ufe0f", None))
        self.pushButton_anim_pause.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"\u23f8", None))
        self.pushButton_restart.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"\U0001f504", None))
        self.Editarlineadetiempo_button.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Editar linea de tiempo", None))
        self.checkBox_valpredeterminados.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Valores predeterminados", None))
#if QT_CONFIG(tooltip)
        self.lblEstadoSolucionador.setToolTip(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Estado del estudio f\u00edsico (r\u00e9gimen de contacto). Se ejecuta desde el editor de reg\u00edmenes.", None))
#endif // QT_CONFIG(tooltip)
        self.lblEstadoSolucionador.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Estudio f\u00edsico: Sin estudio", None))
#if QT_CONFIG(tooltip)
        self.btnVerResultados.setToolTip(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Consultar el estudio f\u00edsico v\u00e1lido e inspeccionarlo sobre la geometr\u00eda.", None))
#endif // QT_CONFIG(tooltip)
        self.btnVerResultados.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Ver resultados", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Control Manual", None))
        self.label_5.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Posici\u00f3n Angular del Pi\u00f1on \u03b8 (\u00b0)", None))
        self.label_10.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Modo del Pi\u00f1on", None))
        self.comboBox_modo_pinon.setItemText(0, QCoreApplication.translate("Epi_HipotrocoidalV2", u"Fijo en X+", None))
        self.comboBox_modo_pinon.setItemText(1, QCoreApplication.translate("Epi_HipotrocoidalV2", u"Orbitar", None))

        self.groupBox_4.setTitle(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Opciones de Simulaci\u00f3n", None))
        self.pushButton_mostrar_ocultar.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Mostrar/Ocultar", None))
        self.pushButton_sim_reset.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Reset", None))
        self.comboBox_modo_sim.setItemText(0, QCoreApplication.translate("Epi_HipotrocoidalV2", u"Manual", None))
        self.comboBox_modo_sim.setItemText(1, QCoreApplication.translate("Epi_HipotrocoidalV2", u"Autom\u00e1tico", None))

        self.label_11.setText(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Modo de Simulaci\u00f3n", None))
        self.menuArchivo.setTitle(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Archivo", None))
        self.menuAyuda.setTitle(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Info", None))
        self.menuPropiedades_f_sicas.setTitle(QCoreApplication.translate("Epi_HipotrocoidalV2", u"Propiedades f\u00edsicas", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("Epi_HipotrocoidalV2", u"toolBar", None))
    # retranslateUi

