"""Controlador del formulario `ui/designer/Ajustes.ui` sin generar .py con uic.

Compatible con la llamada existente: SettingsWindow(self).exec().
El QDialog real se carga mediante QtUiTools.QUiLoader; `self.dialog` conserva
TODOS los widgets creados/editados en Qt Designer. NO se importa hardware.
"""
from __future__ import annotations
from dataclasses import asdict
from copy import deepcopy
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets, QtUiTools

from config.settings_model import (SettingsState,Apariencia,PRESET_NAMES,preset_colors,
                                   estilos_iniciales,UI_ROLES,TECH_ROLES)
from config.settings_store import SettingsStore
from ui.selector_color_rps import ConectorColores
from ui.theme_manager import ThemeManager


# El Ajustes.ui del repo (el del usuario) conserva nombres genéricos de Designer; se resuelven aquí en vez de
# modificar el formulario. Si algún día se renombran en Designer, el nombre real tiene prioridad.
ALIAS_WIDGETS = {
    'btnCancelar': 'pushButton_2', 'btnAplicar': 'pushButton_3', 'btnAceptar': 'pushButton_4',
    'btnRestaurar': 'pushButton', 'chkRestaurarSesion': 'checkBox', 'chkConfirmarSalir': 'checkBox_2',
    'chkSimulacionPorContacto': 'checkBox_3', 'chkModoSeguroBanco': 'chkBajarFPSInactivo_2',
}
# Campos de video que el .ui del repo no trae (solo sus etiquetas): `_completar_campos_video` los CREA en código dentro
# de las filas existentes. Si algún día se añaden en Designer con estos nombres, se usan tal cual.
OPCIONALES = ('comboResolucionVideo', 'comboFPSVideo', 'spinCRFVideo')


class SettingsWindow(QtCore.QObject):
    """Contenedor de QDialog cargado. Para acceso a QWidget, usar `.dialog`."""
    def __init__(self,parent=None,on_apply=None,store=None,theme_manager=None):
        super().__init__(parent)
        path=Path(__file__).resolve().parent/'designer'/'Ajustes.ui'
        file=QtCore.QFile(str(path))
        if not file.open(QtCore.QIODevice.OpenModeFlag.ReadOnly):
            raise OSError(f'No se pudo abrir el formulario: {path}')
        try:
            self.dialog=QtUiTools.QUiLoader().load(file,parent)
        finally:
            file.close()
        if self.dialog is None:
            raise RuntimeError('QUiLoader no pudo cargar Ajustes.ui')
        self.dialog.setWindowTitle('RPS Design V2 — Ajustes')
        self.store=store or SettingsStore()
        self.state=self.store.load()
        self._on_apply=on_apply
        self._theme=theme_manager or ThemeManager(QtWidgets.QApplication.instance())
        self._styles=deepcopy(self.state.apariencia.estilos_lineas)
        self._curva_actual=None
        self._guardando=False
        self._completar_campos_video()
        self._setup()
        combo=self.w('comboTema',QtWidgets.QComboBox)
        for name in self.store.custom_themes():
            if combo.findText(name)<0:
                combo.addItem(name)
        self._load_into_form(self.state)

    def w(self,name,typ=QtWidgets.QWidget):
        result=self.dialog.findChild(typ,name)
        if result is None and name in ALIAS_WIDGETS:
            result=self.dialog.findChild(typ,ALIAS_WIDGETS[name])
        if result is None and name not in OPCIONALES:
            raise RuntimeError('Falta widget en Ajustes.ui: '+name)
        return result

    def _completar_campos_video(self):
        """Resolución, FPS y calidad del video: las filas del .ui solo tienen la etiqueta. Se añade el campo a cada fila
        (QHBoxLayout `<nombre>Row`) sin modificar el .ui. También se quita «(por implementar)» del combo VP9."""
        from exporters.settings_adapter import RESOLUCIONES
        filas={'comboResolucionVideo':lambda:self._combo_video(list(RESOLUCIONES)+['Personalizada']),
               'comboFPSVideo':lambda:self._combo_video(['24 FPS','30 FPS','60 FPS']),
               'spinCRFVideo':self._spin_crf}
        for nombre,fabrica in filas.items():
            if self.dialog.findChild(QtWidgets.QWidget,nombre) is not None:
                continue
            fila=self.dialog.findChild(QtWidgets.QHBoxLayout,nombre+'Row')
            if fila is None and nombre=='spinCRFVideo':
                fila=self.dialog.findChild(QtWidgets.QHBoxLayout,'comboCRFVideoRow')
            if fila is None:
                continue
            campo=fabrica();campo.setObjectName(nombre);fila.addWidget(campo,1)
        combo=self.dialog.findChild(QtWidgets.QComboBox,'comboFormatoVideo')
        if combo is not None:
            for i in range(combo.count()):
                if 'por implementar' in combo.itemText(i):
                    combo.setItemText(i,combo.itemText(i).replace(' (por implementar)',''))

    def _combo_video(self,items):
        c=QtWidgets.QComboBox();c.addItems(items);return c

    def _spin_crf(self):
        sp=QtWidgets.QSpinBox();sp.setRange(0,51)
        sp.setToolTip('CRF: menor = más calidad y más peso (H.264 ≈ 18–28; VP9 ≈ 25–35).')
        return sp

    def tiene(self,name):
        return self.w(name) is not None

    def _set_combo(self,name,text):
        w=self.w(name,QtWidgets.QComboBox)
        if w is None:return None
        idx=w.findText(str(text))
        if idx>=0:w.setCurrentIndex(idx)
        return w

    def _setup(self):
        self.w('btnCancelar',QtWidgets.QPushButton).clicked.connect(self.dialog.reject)
        self.w('btnAceptar',QtWidgets.QPushButton).clicked.connect(self._accept)
        self.w('btnAplicar',QtWidgets.QPushButton).clicked.connect(self._apply)
        self.w('btnRestaurar',QtWidgets.QPushButton).clicked.connect(self._restore)
        self.w('comboTema',QtWidgets.QComboBox).currentTextChanged.connect(self._theme_changed)
        self.w('btnGuardarTema',QtWidgets.QPushButton).clicked.connect(self._save_theme)
        self.w('btnDuplicarTema',QtWidgets.QPushButton).clicked.connect(self._duplicate_theme)
        self.w('btnRestaurarTema',QtWidgets.QPushButton).clicked.connect(self._reset_theme)
        self.colors=ConectorColores(self.dialog,self.dialog)
        self.colors.colorConfirmado.connect(self._color_changed)
        self.w('comboTipoCurva',QtWidgets.QComboBox).currentTextChanged.connect(self._curve_changed)
        for key in ('spinAnchoLinea','comboTipoLinea','comboLineCap','comboLineJoin',
                    'spinOpacidad','sliderOpacidad'):
            widget=self.w(key)
            signal=widget.valueChanged if hasattr(widget,'valueChanged') else widget.currentTextChanged
            signal.connect(self._line_changed)
        self._pair_spin_slider('desviacionLinealSpin','desviacionLinealSlider',10000.)
        self._pair_spin_slider('desviacionAngularSpin','desviacionAngularSlider',1000.)
        self._pair_spin_slider('spinOpacidad','sliderOpacidad',1.)
        self._pair_spin_slider('spinJpeg','sliderJpeg',1.)
        self.w('comboEstrategiaMuestreo',QtWidgets.QComboBox).currentTextChanged.connect(self._sampling_ui)
        self.w('comboFPS',QtWidgets.QComboBox).currentTextChanged.connect(self._fps_ui)
        self.w('comboResolucionImagen',QtWidgets.QComboBox).currentTextChanged.connect(self._image_resolution_ui)
        if self.tiene('comboResolucionVideo'):
            self.w('comboResolucionVideo',QtWidgets.QComboBox).currentTextChanged.connect(self._video_resolution_ui)
        # No hay reproductor/vista previa: el cambio no afecta la app hasta Aplicar.

    def _pair_spin_slider(self,spin_name,slider_name,mul):
        s=self.w(spin_name);sl=self.w(slider_name)
        def slide(v):
            with QtCore.QSignalBlocker(s):s.setValue(v/mul)
        def typed(v):
            with QtCore.QSignalBlocker(sl):sl.setValue(round(v*mul))
        sl.valueChanged.connect(slide);s.valueChanged.connect(typed)

    def _sampling_ui(self,*_):
        uniform='Uniforme' in self.w('comboEstrategiaMuestreo',QtWidgets.QComboBox).currentText()
        self.w('spinMuestras').setEnabled(uniform)
        self.w('spinMaxMuestras').setEnabled(not uniform)

    def _fps_ui(self,*_):
        text=self.w('comboFPS',QtWidgets.QComboBox).currentText()
        self.w('spinFPSCustom').setEnabled('Personalizado' in text)

    @staticmethod
    def _dimension_preset(text):
        from exporters.settings_adapter import RESOLUCIONES
        return next((size for name,size in RESOLUCIONES.items() if name==text),None)

    def _image_resolution_ui(self,text):
        dims=self._dimension_preset(text)
        if dims:
            self.w('spinImgAncho').setValue(dims[0]);self.w('spinImgAlto').setValue(dims[1])

    def _video_resolution_ui(self,text):
        dims=self._dimension_preset(text)
        if dims:
            self.w('spinVidAncho').setValue(dims[0]);self.w('spinVidAlto').setValue(dims[1])

    def _get_tree(self,name):
        w=self.w(name,QtWidgets.QTreeWidget)
        return {w.topLevelItem(i).text(0):w.topLevelItem(i).text(1)
                for i in range(w.topLevelItemCount())}

    def _set_tree(self,name,values):
        w=self.w(name,QtWidgets.QTreeWidget)
        for i in range(w.topLevelItemCount()):
            row=w.topLevelItem(i);color=values.get(row.text(0))
            if color:
                row.setText(1,color)
                self.colors._icono(row)

    def _load_into_form(self,state):
        self._guardando=True
        try:
            g,c,s,a,e=state.general,state.calculo,state.simulacion,state.apariencia,state.exportacion
            checks={
                'chkRestaurarSesion':g.restaurar_sesion, 'chkConfirmarSalir':g.confirmar_salir,
                'chkGuardadoAuto':g.guardado_automatico,'chkGuardarPrefs':g.guardar_preferencias,
                'chkAvisosDatos':g.avisos_datos,'chkAvisosSobrescribir':g.confirmar_sobrescritura,
                'chkMostrarEstimacion':c.mostrar_estimacion,'chkVSync':s.vsync_solicitado,
                'chkBajarFPSInactivo':s.bajar_fps_inactivo,'chkDetenerInvalido':s.detener_invalido,
                'chkConservarPausa':s.conservar_pausa,'chkCacheGeometria':s.cache_geometria,
                'chkSimulacionPorContacto':s.basada_en_contacto,'chkModoSeguroBanco':s.modo_seguro_banco,'chkAntialias':a.antialias,
                'chkFuenteUIBold':a.negrita_ui,'chkFuenteGraficaBold':a.negrita_graficas,
                'chkMantenerAspectoImagen':e.mantener_aspecto_imagen,'chkFondoTransparente':e.fondo_transparente,
                'chkAntialiasExport':e.antialias_export,'chkRelacionVideo':e.mantener_aspecto_video,
                'chkVideoDeterminista':e.video_determinista,
            }
            for name,value in checks.items():self.w(name,QtWidgets.QCheckBox).setChecked(value)
            nums={
                'spinIntervaloGuardado':g.intervalo_guardado_min,
                'spinMuestras':c.muestras_uniformes,'spinMaxMuestras':c.max_muestras,
                'desviacionLinealSpin':c.desviacion_lineal_mm,
                'desviacionAngularSpin':c.desviacion_angular_grados,
                'spinFPSCustom':s.fps_personalizado,'spinTamanoUI':a.tamano_ui,
                'spinTamanoGrafica':a.tamano_graficas,
                'spinImgAncho':e.imagen_ancho,'spinImgAlto':e.imagen_alto,'spinJpeg':e.jpeg_calidad,
                'spinVidAncho':e.video_ancho,'spinVidAlto':e.video_alto,'spinCRFVideo':e.video_crf,
            }
            for name,value in nums.items():
                if self.tiene(name):self.w(name).setValue(value)
            combos={
                'comboDecimales':c.decimales,'comboEstrategiaMuestreo':c.estrategia_muestreo,
                'comboFPS':s.fps,'comboBackend':s.backend,'comboRender':s.render,
                'comboTema':a.preset,'comboFormatoImagen':e.formato_imagen,
                'comboResolucionImagen':e.resolucion_imagen,
                'comboFormatoVideo':e.formato_video,
                'comboResolucionVideo':e.resolucion_video,
                'comboFPSVideo':f'{e.video_fps} FPS',
            }
            for name,value in combos.items():
                if self.tiene(name):self._set_combo(name,value)
            self.w('fontInterfaz',QtWidgets.QFontComboBox).setCurrentFont(QtGui.QFont(a.fuente_ui))
            self.w('fontGraficas',QtWidgets.QFontComboBox).setCurrentFont(QtGui.QFont(a.fuente_graficas))
            self._set_tree('treeColoresUI',a.ui_colores)
            self._set_tree('treeColoresTecnicos',a.tecnicos_colores)
            self._styles=deepcopy(a.estilos_lineas)
            self._curva_actual=self.w('comboTipoCurva',QtWidgets.QComboBox).currentText()
            self._show_style(self._curva_actual)
            self._sampling_ui();self._fps_ui()
        finally:
            self._guardando=False

    def _theme_changed(self,name):
        if self._guardando:return
        customs=self.store.custom_themes()
        if name in customs:
            ui=customs[name].get('ui_colores',{});tech=customs[name].get('tecnicos_colores',{})
        elif name in PRESET_NAMES and name!='Personalizado':
            ui,tech=preset_colors(name)
        else:
            return
        self._set_tree('treeColoresUI',ui)
        self._set_tree('treeColoresTecnicos',tech)

    def _color_changed(self,_categoria,_role,_color):
        if not self._guardando:
            self._set_combo('comboTema','Personalizado')

    def _show_style(self,name):
        cfg=self._styles.get(name,{})
        widgets={
            'spinAnchoLinea':cfg.get('ancho',1),
            'comboTipoLinea':cfg.get('tipo','Continua'),
            'comboLineCap':cfg.get('terminacion','Plana'),
            'comboLineJoin':cfg.get('union','Bisel'),
            'spinOpacidad':cfg.get('opacidad',100),
        }
        for widgetname,value in widgets.items():
            w=self.w(widgetname)
            with QtCore.QSignalBlocker(w):
                if isinstance(w,QtWidgets.QComboBox):self._set_combo(widgetname,value)
                else:w.setValue(value)
        self.w('sliderOpacidad').setValue(int(cfg.get('opacidad',100)))

    def _curve_changed(self,name):
        self._curva_actual=name
        self._show_style(name)

    def _line_changed(self,*_):
        if self._guardando or not self._curva_actual:return
        self._styles[self._curva_actual]={
            'ancho':self.w('spinAnchoLinea').value(),
            'tipo':self.w('comboTipoLinea').currentText(),
            'terminacion':self.w('comboLineCap').currentText(),
            'union':self.w('comboLineJoin').currentText(),
            'opacidad':(self.w('sliderOpacidad').value()
                        if self.sender() is self.w('sliderOpacidad')
                        else self.w('spinOpacidad').value()),
        }

    def _collect(self):
        state=deepcopy(self.state)
        g,c,s,a,e=state.general,state.calculo,state.simulacion,state.apariencia,state.exportacion
        for obj,key in [
            ('chkRestaurarSesion','restaurar_sesion'),('chkConfirmarSalir','confirmar_salir'),
            ('chkGuardadoAuto','guardado_automatico'),('chkGuardarPrefs','guardar_preferencias'),
            ('chkAvisosDatos','avisos_datos'),('chkAvisosSobrescribir','confirmar_sobrescritura')]:
            setattr(g,key,self.w(obj).isChecked())
        g.intervalo_guardado_min=self.w('spinIntervaloGuardado').value()
        for obj,key in [('comboDecimales','decimales'),('comboEstrategiaMuestreo','estrategia_muestreo')]:
            setattr(c,key,self.w(obj).currentText())
        for obj,key in [('spinMuestras','muestras_uniformes'),('spinMaxMuestras','max_muestras'),
                        ('desviacionLinealSpin','desviacion_lineal_mm'),
                        ('desviacionAngularSpin','desviacion_angular_grados')]:
            setattr(c,key,self.w(obj).value())
        c.mostrar_estimacion=self.w('chkMostrarEstimacion').isChecked()
        for obj,key in [('comboFPS','fps'),('comboBackend','backend'),('comboRender','render')]:
            setattr(s,key,self.w(obj).currentText())
        s.fps_personalizado=self.w('spinFPSCustom').value()
        for obj,key in [('chkVSync','vsync_solicitado'),('chkBajarFPSInactivo','bajar_fps_inactivo'),
                        ('chkDetenerInvalido','detener_invalido'),('chkConservarPausa','conservar_pausa'),
                        ('chkCacheGeometria','cache_geometria'),
                        ('chkSimulacionPorContacto','basada_en_contacto'),('chkModoSeguroBanco','modo_seguro_banco')]:
            setattr(s,key,self.w(obj).isChecked())
        a.preset=self.w('comboTema').currentText()
        a.ui_colores=self._get_tree('treeColoresUI')
        a.tecnicos_colores=self._get_tree('treeColoresTecnicos')
        a.estilos_lineas=deepcopy(self._styles)
        a.antialias=self.w('chkAntialias').isChecked()
        a.fuente_ui=self.w('fontInterfaz').currentFont().family()
        a.tamano_ui=self.w('spinTamanoUI').value()
        a.negrita_ui=self.w('chkFuenteUIBold').isChecked()
        a.fuente_graficas=self.w('fontGraficas').currentFont().family()
        a.tamano_graficas=self.w('spinTamanoGrafica').value()
        a.negrita_graficas=self.w('chkFuenteGraficaBold').isChecked()
        for obj,key in [('comboFormatoImagen','formato_imagen'),('comboResolucionImagen','resolucion_imagen'),
                        ('comboFormatoVideo','formato_video'),('comboResolucionVideo','resolucion_video')]:
            if self.tiene(obj):setattr(e,key,self.w(obj).currentText())
        for obj,key in [('spinImgAncho','imagen_ancho'),('spinImgAlto','imagen_alto'),
                        ('spinJpeg','jpeg_calidad'),('spinVidAncho','video_ancho'),
                        ('spinVidAlto','video_alto'),('spinCRFVideo','video_crf')]:
            if self.tiene(obj):setattr(e,key,self.w(obj).value())
        if self.tiene('comboFPSVideo'):
            e.video_fps=int(self.w('comboFPSVideo').currentText().split()[0])
        for obj,key in [('chkMantenerAspectoImagen','mantener_aspecto_imagen'),
                        ('chkFondoTransparente','fondo_transparente'),
                        ('chkAntialiasExport','antialias_export'),
                        ('chkRelacionVideo','mantener_aspecto_video'),
                        ('chkVideoDeterminista','video_determinista')]:
            setattr(e,key,self.w(obj).isChecked())
        state.validate();return state

    def _apply(self):
        try:
            value=self._collect()
            # El callback externo aplica los comportamientos reales de cada ventana.
            if self._on_apply is not None:
                self._on_apply(value)
            else:
                self._default_apply(value)
            self.store.save(value)
            self.state=deepcopy(value)
            return True
        except Exception as exc:
            QtWidgets.QMessageBox.warning(self.dialog,'Ajustes no aplicados',str(exc))
            return False

    def _default_apply(self,state):
        from config.app_settings import ajustes
        ajustes.modo_hardware=state.simulacion.backend.split(' — ')[0].replace('Híbrido','Hibrido')
        ajustes.desviacion.desviacion_lineal_mm=state.calculo.desviacion_lineal_mm
        ajustes.desviacion.desviacion_angular_grados=state.calculo.desviacion_angular_grados
        usar_gl=state.simulacion.render=='OpenGL'
        if usar_gl!=ajustes.render_opengl:
            from widgets import pg_helpers
            if not pg_helpers.aplicar_opengl(usar_gl,self.dialog):
                motivo=pg_helpers.ULTIMO_ERROR_OPENGL or 'motivo no informado por el controlador'
                raise RuntimeError(f'No se pudo aplicar OpenGL ({motivo}); se conserva la preferencia anterior')
            ajustes.render_opengl=usar_gl
        # Compatibilidad con ventanas antiguas, en tanto se migren sus estilos.
        bg=state.apariencia.ui_colores.get('Fondo de ventana','#222222')
        color=QtGui.QColor(bg)
        ajustes.modo_oscuro=color.lightness()<128
        self._theme.apply(state.apariencia)
        # Sin control físico. `basada_en_contacto` habilita los estudios de contacto (ui/estudio_qt.contacto_habilitado).

    def _accept(self):
        if self._apply():self.dialog.accept()

    def _restore(self):
        answer=QtWidgets.QMessageBox.question(self.dialog,'Restaurar preferencias',
                                               '¿Restaurar todos los ajustes predeterminados en este formulario?')
        if answer==QtWidgets.QMessageBox.StandardButton.Yes:
            self._load_into_form(SettingsState())

    def _reset_theme(self):
        current=self.w('comboTema').currentText()
        if current not in PRESET_NAMES or current=='Personalizado':
            current='Azul profundo — RPS'
        self._theme_changed(current)

    def _theme_data(self):
        return {'ui_colores':self._get_tree('treeColoresUI'),
                'tecnicos_colores':self._get_tree('treeColoresTecnicos')}

    def _save_theme(self):
        name,ok=QtWidgets.QInputDialog.getText(self.dialog,'Guardar preset','Nombre del preset:')
        if not ok or not name.strip():return
        if name in PRESET_NAMES:
            QtWidgets.QMessageBox.warning(self.dialog,'Preset protegido','No se pueden sobrescribir presets integrados.')
            return
        self.store.save_custom_theme(name,self._theme_data())
        combo=self.w('comboTema',QtWidgets.QComboBox)
        if combo.findText(name)<0:combo.addItem(name)
        combo.setCurrentText(name)

    def _duplicate_theme(self):
        stem=self.w('comboTema').currentText()
        existing=set(self.store.custom_themes())
        i=1
        name=f'{stem} — copia {i}'
        while name in existing:i+=1;name=f'{stem} — copia {i}'
        self.store.save_custom_theme(name,self._theme_data())
        combo=self.w('comboTema',QtWidgets.QComboBox)
        combo.addItem(name);combo.setCurrentText(name)

    def exec(self):
        # Un QDialog real para la compatibilidad con SettingsWindow(self).exec().
        return self.dialog.exec()

    def show(self):
        return self.dialog.show()
