# -*- coding: utf-8 -*-
"""
ui/sistema_base.py

Clase base de las ventanas de sistema de V2 (Epitrocoidal, Hipotrocoidal, Trocoidal). Contiene TODO lo
común (principio DRY): debounce de recálculo, modo Manual/Automático, línea de tiempo, motor real,
grabación de video, abrir/guardar/exportar, resumen de diseño, ventanas de propiedades y
visibilidad. Cada sistema concreto solo declara sus clases/widgets y los pocos "ganchos" que cambian:

  _crear_control()            control manual (AngleControl o ControlLineal)
  _widgets_control_manual()   widgets que se deshabilitan en modo Automático
  _valor_desde_angulo / _angulo_desde_valor   conversión control <-> ángulo del piñón (°)
  _resolver_estado(alt, ang)  EstadoCinematico (angular o lineal)
  _curva_base(motor)          curva generatriz base, ya en el marco de vista
  _preparar_ui()              ajustes de textos/valores propios del sistema

Arquitectura: la UI solo lee/valida parámetros (dataclasses), el engine calcula, los widgets dibujan.
El perfil de la línea de tiempo es SIEMPRE el ángulo del piñón (°); en Trocoidal, X = prrp·θ.
"""
from __future__ import annotations

import copy
from collections import OrderedDict
from dataclasses import asdict
from pathlib import Path
import json
import time

import numpy as np
from PySide6 import QtCore, QtWidgets

from config.app_settings import ajustes
from config.data_structures import AjustesVisibilidadSimulacion
from dialogs.design_summary_dialog import DialogoResumenDiseno
from engine.cinematica_engine import SolverCinematico
from engine.motion_engine import PRESET_DEFECTO, FabricaPresets, LineaTiempo, RegistroLeyes
from exporters.excel_exporter import exportar_excel
from exporters.video_recorder import GrabadorVideo
from ui.errores import manejador_seguro
from ui.property_windows import VentanaPerfilDiente, VentanaPropiedad
from simulation.frame_scheduler import FrameScheduler
from ui import sesion
from ui.ajustes_runtime import runtime
from ui.velocity_profile_window import VentanaPerfilVelocidad
from utils import file_handler
from widgets.pg_helpers import reemplazar_widget
from widgets.simulation_view import SimulationView

FPS_VIDEO = 30


class VentanaSistemaBase(QtWidgets.QMainWindow):
    # ---- a definir en cada sistema ----
    SISTEMA = ""                       # clave en los archivos de proyecto
    NOMBRE = ""
    CLASE_UI = None                    # clase Ui_* generada por Qt Designer
    CLASE_PARAMETROS = None
    CLASE_MOTOR = None
    CLASE_DIALOGO_VISIBILIDAD = None
    MAPEO_PARAMETROS: tuple = ()       # (campo del dataclass, objectName del spinbox)
    LINEAL = False
    ARCHIVO_EXCEL = "sistema.xlsx"

    perfilActualizado = QtCore.Signal(object)   # ResultadoPerfil (con patrón y análisis)

    def __init__(self, retorno=None):
        super().__init__()
        self._retorno = retorno
        self.motor_actual = None
        self.perfil_actual = None
        self._solver = None
        self.vis = AjustesVisibilidadSimulacion()
        self._dlg_vis = None
        self._editor = None
        self._aux: list = []
        self._ruta = None
        self.perfil_mov_defecto = FabricaPresets.crear(PRESET_DEFECTO)
        self.perfil_mov = copy.deepcopy(self.perfil_mov_defecto)
        self.linea_tiempo: LineaTiempo | None = None
        self._t = 0.0
        self._t_ultimo = 0.0
        self._t_msg = 0.0

        self.ui = self.CLASE_UI()
        self.ui.setupUi(self)
        self._preparar_ui()
        self.sim = self._crear_vista()
        self.control = self._crear_control()

        self._debounce = QtCore.QTimer(self, singleShot=True, interval=150)
        self._debounce.timeout.connect(self._recalcular)
        self._anim = QtCore.QTimer(self)
        self._anim.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
        self._anim.setInterval(8)
        self._anim.timeout.connect(self._tick)

        sim = runtime.estado.simulacion         # cadencia visual (FPS) desde Ajustes; el tiempo sigue siendo perf_counter
        self._scheduler = FrameScheduler(self, self._anim, sim.fps, sim.fps_personalizado, sim.bajar_fps_inactivo)
        runtime.cambiado.connect(self._ajustes_cambiaron)
        self._cache_geo = OrderedDict()         # «Reutilizar geometría no modificada» (hasta 8 geometrías)
        self._clave_pintada = None              # geometría que la vista ya dibuja
        self._clave_lt = None                   # línea de tiempo vigente (para «Conservar resultados al pausar»)
        self._conectar()
        self._aplicar_modo()
        self._recalcular()
        self._huella_limpia = ""
        self._t_auto = QtCore.QTimer(self)
        self._t_auto.timeout.connect(self._autoguardar)
        self._configurar_autoguardado()
        self._restaurar_sesion()                # autoguardado pendiente o última sesión (según Ajustes → General)

    # ------------------------------------------------------------------ ganchos (cada sistema)
    def _preparar_ui(self):
        pass

    def _crear_control(self):
        raise NotImplementedError

    def _widgets_control_manual(self) -> tuple:
        raise NotImplementedError

    def _valor_desde_angulo(self, angulo_grados: float) -> float:
        return angulo_grados

    def _angulo_desde_valor(self, valor: float) -> float:
        return valor

    def _resolver_estado(self, alterno: bool, angulo_grados: float):
        raise NotImplementedError

    def _curva_base(self, motor):
        raise NotImplementedError

    def _refrescar_indicadores(self, angulo_grados: float):
        pass

    def _actualizar_rango_control(self, parametros):
        pass

    def _crear_vista(self):
        return reemplazar_widget(self.ui.graphicsView_epi, SimulationView())

    def _alterno(self) -> bool:
        """True si el piñón está en modo alterno (Orbitar / Trasladar)."""
        return self.ui.comboBox_modo_pinon.currentIndex() == 1

    def _rango_angulo_auto(self):
        """(mín, máx) en ° que puede recorrer la línea de tiempo, o None si no hay límite
        (Trocoidal: el piñón no debe salirse de la cremallera)."""
        return None

    def _conectar_modo_pinon(self):
        self.ui.comboBox_modo_pinon.currentIndexChanged.connect(lambda *_: self._modo_pinon_cambiado())

    def _conectar_propiedades(self):
        u = self.ui
        u.actionPerfil_del_diente.triggered.connect(lambda *_: self._abrir_aux(lambda: VentanaPerfilDiente(self)))
        u.action_ngulo_de_Presi_n.triggered.connect(lambda *_: self._abrir_aux(lambda: VentanaPropiedad(self, "angulo")))
        u.actionRadio_de_Curvatura.triggered.connect(lambda *_: self._abrir_aux(lambda: VentanaPropiedad(self, "curvatura")))
        u.actionCamino_de_Contacto.triggered.connect(lambda *_: self._abrir_aux(lambda: VentanaPropiedad(self, "contacto")))

    def _combos_modo(self, s: dict) -> tuple:
        """(combo, valor guardado) que se restauran al abrir un proyecto."""
        return ((self.ui.comboBox_modo_pinon, s.get("modo_pinon", 0)),)

    # ------------------------------------------------------------------ conexiones
    def _spins(self) -> tuple:
        return tuple(getattr(self.ui, nombre) for _, nombre in self.MAPEO_PARAMETROS)

    def _conectar(self):
        u = self.ui
        for sp in self._spins():
            sp.valueChanged.connect(lambda *_: self._debounce.start())
        self.control.cambiado.connect(lambda *_: self._emitir_estado())
        self._conectar_modo_pinon()
        u.comboBox_modo_sim.currentIndexChanged.connect(lambda *_: self._aplicar_modo())
        u.pushButton_mostrar_ocultar.clicked.connect(lambda *_: self._abrir_visibilidad())
        u.pushButton_sim_reset.clicked.connect(lambda *_: self._reset())
        u.pushButton_anim_play.clicked.connect(lambda *_: self._play())
        u.pushButton_anim_pause.clicked.connect(lambda *_: self._pausar())
        u.pushButton_restart.clicked.connect(lambda *_: self._reiniciar())
        u.pushButton_record.clicked.connect(lambda *_: self._grabar())
        u.Editarlineadetiempo_button.clicked.connect(lambda *_: self._editar_linea_tiempo())
        u.checkBox_valpredeterminados.toggled.connect(self._predeterminado_cambiado)
        u.actionAbrir.triggered.connect(lambda *_: self._abrir())
        u.actionGuardar.triggered.connect(lambda *_: self._guardar())
        u.actionExportar.triggered.connect(lambda *_: self._exportar())
        u.actionConfiguraci_n.triggered.connect(lambda *_: runtime.abrir_dialogo(self))
        u.actionCerrar.triggered.connect(lambda *_: self.volver_al_menu())
        u.actionGu_a_T_cnica.triggered.connect(lambda *_: QtWidgets.QMessageBox.information(
            self, "Guía técnica", "La guía técnica se desarrollará más adelante."))
        u.actionResumen_de_Dise_o.triggered.connect(lambda *_: self._resumen())
        self._conectar_propiedades()

    # ------------------------------------------------------------------ parámetros y motor
    def leer_parametros(self):
        return self.CLASE_PARAMETROS(**{campo: getattr(self.ui, nombre).value()
                                        for campo, nombre in self.MAPEO_PARAMETROS})

    def _escribir_parametros(self, p) -> None:
        for campo, nombre in self.MAPEO_PARAMETROS:
            sp = getattr(self.ui, nombre)
            sp.blockSignals(True); sp.setValue(getattr(p, campo)); sp.blockSignals(False)

    @manejador_seguro
    def _clave_geometria(self, p) -> str:
        """Todo lo que determina la geometría calculada: parámetros + tolerancias + backend de cálculo."""
        d = ajustes.desviacion
        return repr((type(p).__name__, sorted(asdict(p).items()), d.desviacion_lineal_mm,
                     d.desviacion_angular_grados, ajustes.modo_hardware))

    def _geometria(self, p, fabrica):
        """(valor, clave, reutilizado). «Reutilizar geometría no modificada»: parámetros ya calculados no se recalculan."""
        clave = self._clave_geometria(p)
        if not runtime.estado.simulacion.cache_geometria:
            self._cache_geo.clear()
            return fabrica(), clave, False
        if clave in self._cache_geo:
            self._cache_geo.move_to_end(clave)
            return self._cache_geo[clave], clave, True
        valor = fabrica()
        self._cache_geo[clave] = valor
        while len(self._cache_geo) > 8:
            self._cache_geo.popitem(last=False)
        return valor, clave, False

    def _invalido(self, texto: str, ms: int = 4000) -> None:
        """Estado no calculable: aviso y, si Ajustes lo pide, se detiene la reproducción en curso."""
        if self._anim.isActive() and runtime.estado.simulacion.detener_invalido:
            self._pausar()
            self.statusBar().showMessage("Simulación detenida: " + texto, max(ms, 6000))
        else:
            self._aviso(texto, ms)

    def _recalcular(self, *_):
        p = self.leer_parametros()
        if not p.es_valido():
            self._invalido("Parámetros fuera de rango: la geometría no se recalcula.")
            return

        def fabricar():
            m = self.CLASE_MOTOR(p)
            return m, m.generar_patron()      # incluye el análisis del perfil (1 sola pasada)

        (motor, res), clave, reutilizado = self._geometria(p, fabricar)
        self.motor_actual, self.perfil_actual = motor, res
        self._solver = SolverCinematico(motor.contexto)
        self._actualizar_rango_control(p)
        if not (reutilizado and clave == self._clave_pintada):      # la vista ya dibuja exactamente esta geometría
            self.sim.set_geometria(res)
            self.sim.set_curva_base(*self._curva_base(motor))
        self._clave_pintada = clave
        self.perfilActualizado.emit(res)
        self._emitir_estado()
        if self._es_auto() and self._rango_angulo_auto() is not None:    # L / prrp cambiaron: reencajar
            self._reconstruir_auto()

    # ------------------------------------------------------------------ estado de la simulación
    def _modo_pinon_cambiado(self):
        if self._dlg_vis is not None:
            self._dlg_vis.actualizar_modo(self.ui.comboBox_modo_pinon.currentIndex() == 1)
        self._emitir_estado()

    def _es_auto(self) -> bool:
        return self.ui.comboBox_modo_sim.currentIndex() == 1

    def _angulo_motor(self) -> float:
        """Ángulo del piñón (°) según el modo: línea de tiempo o control manual."""
        if self._es_auto() and self.linea_tiempo is not None:
            return self.linea_tiempo.posicion_en(self._t)
        return self._angulo_desde_valor(self.control.acumulado)

    def _estado_para(self, angulo_grados: float):
        alt = self.ui.comboBox_modo_pinon.currentIndex() == 1
        est = self._resolver_estado(alt, angulo_grados)
        cont = self.motor_actual.rodillos_en_contacto(
            est.angulo_relativo_generatriz_rad, modo_pinon_alterno=alt, estado_cinematico=est)
        return est, cont

    def contactos_para_propiedad(self, valor_control: float) -> list:
        """Contactos con el piñón en modo FIJO y el control en `valor_control` (θ° o X mm). Los usan
        las ventanas de propiedades (marcan los rodillos activos sobre sus gráficas)."""
        est = self._resolver_estado(False, self._angulo_desde_valor(valor_control))
        return self.motor_actual.rodillos_en_contacto(
            est.angulo_relativo_generatriz_rad, modo_pinon_alterno=False, estado_cinematico=est)

    @manejador_seguro
    def _emitir_estado(self, *_):
        if self.motor_actual is None:
            return
        try:
            ang = self._angulo_motor()
            self._refrescar_indicadores(ang)
            self.sim.actualizar(*self._estado_para(ang))
        except Exception:
            if self._anim.isActive() and runtime.estado.simulacion.detener_invalido:
                self._pausar()          # estado matemáticamente inválido: no seguir calculando a cada tick
                self.statusBar().showMessage("Simulación detenida: el estado calculado no es válido.", 6000)
            raise                       # `manejador_seguro` lo registra

    # ------------------------------------------------------------------ Manual / Automático
    @manejador_seguro
    def _aplicar_modo(self, *_):
        auto = self._es_auto()
        u = self.ui
        self._pausar()
        if auto:
            clave = self._clave_linea()
            if not (runtime.estado.simulacion.conservar_pausa and self.linea_tiempo is not None
                    and clave == self._clave_lt):       # «Conservar resultados al pausar»: misma línea => misma posición
                self._construir_linea_tiempo()
                self._t = self.linea_tiempo.t_ini if self.linea_tiempo else 0.0
                self._clave_lt = clave
        elif self.linea_tiempo is not None:
            self.control.reiniciar(self._valor_desde_angulo(self.linea_tiempo.posicion_en(self._t)))
        for w in self._widgets_control_manual():
            w.setEnabled(not auto)
        for w in (u.frame_anim_controls, u.Editarlineadetiempo_button, u.checkBox_valpredeterminados):
            w.setEnabled(auto)
        self._emitir_estado()

    def _construir_linea_tiempo(self):
        try:
            lt = LineaTiempo.construir(self.perfil_mov, RegistroLeyes())
            avisos = list(lt.errores[-3:])
            rango = self._rango_angulo_auto()
            if rango is not None:       # el recorrido debe caber (Trocoidal: X = prrp·θ en [0, L])
                lt, f, off, recortada = lt.ajustada(*rango, escalar=self.ui.checkBox_valpredeterminados.isChecked())
                if f < 1.0:
                    avisos.append(f"preset escalado ×{f:.3f} para que el piñón no salga del mecanismo")
                if off:
                    avisos.append(f"recorrido desplazado {off:+.1f}° para quedar dentro del rango")
                if recortada:
                    avisos.append("el perfil excede el recorrido permitido: se recortó")
            self.linea_tiempo = lt
            if avisos:
                self.statusBar().showMessage("Aviso: " + " | ".join(avisos), 8000)
                self._t_msg = time.perf_counter() + 4.0      # que el mensaje de t/θ no lo pise
        except Exception as e:
            self.linea_tiempo = None
            self.statusBar().showMessage(f"Perfil de giro inválido: {e}", 6000)

    @manejador_seguro
    def _predeterminado_cambiado(self, marcado: bool):
        if marcado:
            self.perfil_mov = copy.deepcopy(self.perfil_mov_defecto)
            self._reconstruir_auto()

    def _clave_linea(self) -> str:
        """Qué define la línea de tiempo: perfil de movimiento, si es el preset y el recorrido permitido."""
        return json.dumps([self._proyecto_dict()["perfil_movimiento"], self._rango_angulo_auto(),
                           self.ui.checkBox_valpredeterminados.isChecked()], sort_keys=True, default=str)

    def _reconstruir_auto(self):
        self._pausar()
        self._construir_linea_tiempo()
        self._clave_lt = self._clave_linea()
        self._t = self.linea_tiempo.t_ini if self.linea_tiempo else 0.0
        self._mostrar_auto()

    @manejador_seguro
    def _editar_linea_tiempo(self, *_):
        self._editor = VentanaPerfilVelocidad(self.perfil_mov, self, rango=self._rango_angulo_auto())
        self._editor.perfilAceptado.connect(self._perfil_aceptado)
        self._editor.show()

    @manejador_seguro
    def _perfil_aceptado(self, perfil):
        self.perfil_mov = perfil
        chk = self.ui.checkBox_valpredeterminados
        chk.blockSignals(True); chk.setChecked(False); chk.blockSignals(False)
        self._reconstruir_auto()

    # -- reproducción (solo simulación: el control del banco físico vive en otra aplicación) ----------
    @manejador_seguro
    def _play(self, *_):
        lt = self.linea_tiempo
        if not self._es_auto() or lt is None or self._anim.isActive():
            return
        if self._t >= lt.t_fin:
            self._t = lt.t_ini
        self._arrancar()

    def _arrancar(self):
        self._t_ultimo = time.perf_counter()
        self._anim.start()

    def _pausar(self):
        self._anim.stop()

    def _ajustes_cambiaron(self, estado):
        """Tras Aplicar/Aceptar en Ajustes: nueva cadencia visual (no altera el tiempo simulado)."""
        sim = estado.simulacion
        self._scheduler.set_preferences(sim.fps, sim.fps_personalizado, sim.bajar_fps_inactivo)
        self._configurar_autoguardado()

    def _reiniciar(self):
        self._pausar()
        if self.linea_tiempo is not None:
            self._t = self.linea_tiempo.t_ini
            self._mostrar_auto()

    @manejador_seguro
    def _tick(self, *_):
        ahora = time.perf_counter()
        self._t += ahora - self._t_ultimo     # reloj real: la velocidad no depende del FPS
        self._t_ultimo = ahora
        if self._t >= self.linea_tiempo.t_fin:
            self._t = self.linea_tiempo.t_fin
            self._pausar()
        try:
            self._mostrar_auto()
        except Exception:
            if runtime.estado.simulacion.detener_invalido:     # no seguir intentando a cada tick con un estado roto
                self._pausar()
            raise

    def _mostrar_auto(self):
        if self.linea_tiempo is None:
            return
        ang = self.linea_tiempo.posicion_en(self._t)
        if not np.isfinite(ang):
            raise ArithmeticError("el ángulo del motor no es finito (perfil de movimiento inválido)")
        self.control.mostrar(self._valor_desde_angulo(ang))
        self._emitir_estado()
        ahora = time.perf_counter()
        if ahora - self._t_msg > 0.1:
            self.statusBar().showMessage(f"t = {self._t:6.2f} s   ·   θ motor = {ang:9.2f}°")
            self._t_msg = ahora

    @manejador_seguro
    def _reset(self, *_):
        if self._es_auto():
            self._reiniciar()
        else:
            self.control.reiniciar(0.0)
            self._emitir_estado()
        self.sim.resetear_camara()

    # -- grabación (formato, resolución, FPS y calidad vienen de Ajustes → Exportación) -----------------
    @manejador_seguro
    def _grabar(self, *_):
        lt = self.linea_tiempo
        if not self._es_auto() or lt is None or self.motor_actual is None:
            self._aviso_modal("Grabar video", "La grabación requiere el modo Automático con una línea de tiempo válida.")
            return
        from exporters import settings_adapter as ad
        op = runtime.estado.exportacion
        try:
            pv = ad.parametros_video(op)
        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, "Grabar video", f"Configuración de video no válida:\n{e}")
            return
        ext = pv["extension"]
        filtro = "Video WebM (*.webm)" if pv["vp9"] else "Video MP4 (*.mp4)"
        ruta, _f = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar video de la simulación", "simulacion" + ext,
                                                         filtro, options=runtime.opciones_guardado())
        if not ruta:
            return
        if not Path(ruta).suffix:
            ruta += ext
        self._pausar()
        t_prev = self._t
        fps = pv["fps"]
        n = int(lt.duracion * fps) + 1
        angulos = lt.posiciones_en(lt.t_ini + np.arange(n) / fps)           # vectorizado (xp según hardware)
        prog = QtWidgets.QProgressDialog("Grabando video…", "Cancelar", 0, n, self)
        prog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        prog.setMinimumDuration(0)
        grab = GrabadorVideo(ruta, fps, pv["crf"], pv["vp9"])
        exacto = op.video_determinista          # True: cada fotograma se renderiza a la resolución elegida
        cancelado = False
        self.sim.lbl_fps.hide()
        gl = ajustes.render_opengl
        if gl:                       # widget.grab() es fiable con viewport por software
            self.sim.useOpenGL(False)
        try:
            for k in range(n):
                if prog.wasCanceled():
                    cancelado = True
                    break
                self.sim.actualizar(*self._estado_para(float(angulos[k])))
                img = (ad.renderizar_grafica(self.sim, pv["ancho"], pv["alto"], False, op.antialias_export)
                       if exacto else self.sim.fotograma())                     # False: captura rápida de la vista
                grab.agregar(img)
                prog.setValue(k + 1)
        finally:
            grab.cerrar()
            prog.close()
            self.sim.lbl_fps.show()
            if gl:
                self.sim.useOpenGL(True)
            self._t = t_prev
            self._mostrar_auto()
        if cancelado:
            import os
            os.remove(ruta)
            self.statusBar().showMessage("Grabación cancelada.", 4000)
        else:
            QtWidgets.QMessageBox.information(self, "Video guardado", f"Se guardó el video:\n{ruta}")

    # ------------------------------------------------------------------ menú: archivo
    def _sim_dict(self) -> dict:
        return {"modo": self.ui.comboBox_modo_sim.currentIndex(),
                "modo_pinon": self.ui.comboBox_modo_pinon.currentIndex(),
                "valor_manual": self.control.acumulado,      # θ (°) en angular · X (mm) en lineal
                "predeterminado": self.ui.checkBox_valpredeterminados.isChecked()}

    def _proyecto_dict(self) -> dict:
        pm = None if self.ui.checkBox_valpredeterminados.isChecked() else self.perfil_mov
        return file_handler.serializar(self.SISTEMA, self.leer_parametros(), self._sim_dict(), pm, self.vis)

    def _guardar_en(self, ruta) -> None:
        pm = None if self.ui.checkBox_valpredeterminados.isChecked() else self.perfil_mov
        file_handler.guardar_proyecto(ruta, self.SISTEMA, self.leer_parametros(), self._sim_dict(), pm, self.vis)

    @manejador_seguro
    def _guardar(self, *_):
        ruta = self._ruta
        if not ruta:
            ruta, _f = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar proyecto", "proyecto.json",
                                                             "Proyecto RPS (*.json)", options=runtime.opciones_guardado())
        if not ruta:
            return
        self._guardar_en(ruta)
        self._ruta = ruta
        self._marcar_limpio()
        sesion.borrar(sesion.ruta_autoguardado(self.SISTEMA))
        self.statusBar().showMessage(f"Proyecto guardado: {ruta}", 5000)

    @manejador_seguro
    def _abrir(self, *_):
        ruta, _f = QtWidgets.QFileDialog.getOpenFileName(self, "Abrir proyecto", "", "Proyecto RPS (*.json)")
        if not ruta:
            return
        try:
            d = file_handler.abrir_proyecto(ruta, self.SISTEMA)
        except file_handler.ArchivoInvalido as e:
            QtWidgets.QMessageBox.warning(self, "Abrir proyecto", str(e))
            return
        self._aplicar_proyecto(d)
        self._ruta = ruta
        self._marcar_limpio()
        self.statusBar().showMessage(f"Proyecto abierto: {ruta}", 5000)

    def _aplicar_proyecto(self, d: dict) -> None:
        """Vuelca un proyecto ya validado (`file_handler.abrir_proyecto`) en la ventana."""
        self._pausar()
        self._escribir_parametros(d["parametros"])
        s = d["simulacion"]
        self.vis = d["visibilidad"]
        self.sim.set_visibilidad(self.vis)
        self._dlg_vis = None
        self.perfil_mov = d["perfil_movimiento"] if d["perfil_movimiento"] is not None \
            else copy.deepcopy(self.perfil_mov_defecto)
        for w, v in ((self.ui.checkBox_valpredeterminados, d["perfil_movimiento"] is None),
                     *self._combos_modo(s),
                     (self.ui.comboBox_modo_sim, s.get("modo", 0))):
            w.blockSignals(True)
            w.setChecked(v) if isinstance(w, QtWidgets.QCheckBox) else w.setCurrentIndex(int(v))
            w.blockSignals(False)
        self._recalcular()                      # antes que el control: en lineal fija el rango de X
        self.control.reiniciar(float(s.get("valor_manual", s.get("angulo_manual", 0.0))))
        self._aplicar_modo()

    # -- sesión, autoguardado y cambios sin guardar (Ajustes → General) -----------------------------------
    def _huella_cambios(self) -> str:
        d = self._proyecto_dict()
        d["simulacion"].pop("valor_manual", None)       # girar el dial no cuenta como «trabajo sin guardar»
        return json.dumps(d, sort_keys=True, default=str)

    def _marcar_limpio(self) -> None:
        self._huella_limpia = self._huella_cambios()

    def _hay_cambios(self) -> bool:
        return self._huella_cambios() != self._huella_limpia

    def _restaurar_sesion(self) -> None:
        d, recuperado = None, False
        auto = sesion.ruta_autoguardado(self.SISTEMA)
        if auto.exists():                       # la sesión anterior no se cerró bien
            r = QtWidgets.QMessageBox.question(
                self, "Recuperar autoguardado",
                f"Se encontró un autoguardado de {self.NOMBRE} de una sesión que no se cerró correctamente.\n"
                "¿Quieres recuperarlo?")
            if r == QtWidgets.QMessageBox.StandardButton.Yes:
                d, recuperado = self._leer_proyecto_tolerante(auto), True
            sesion.borrar(auto)
        if d is None and runtime.estado.general.restaurar_sesion:
            d = self._leer_proyecto_tolerante(sesion.ruta_sesion(self.SISTEMA))
        if d is not None:
            try:
                self._aplicar_proyecto(d)
            except Exception as e:              # sesión incompatible: se ignora y se arranca con valores por defecto
                print(f"[sesión] no se pudo restaurar: {e}")
        self._huella_limpia = "" if recuperado else self._huella_cambios()

    def _leer_proyecto_tolerante(self, ruta):
        if not ruta.exists():
            return None
        try:
            return file_handler.abrir_proyecto(ruta, self.SISTEMA)
        except file_handler.ArchivoInvalido as e:
            print(f"[sesión] {ruta.name} ignorado: {e}")
            return None

    def _configurar_autoguardado(self) -> None:
        g = runtime.estado.general
        if g.guardado_automatico:
            self._t_auto.start(max(1, int(g.intervalo_guardado_min)) * 60_000)
        else:
            self._t_auto.stop()

    def _autoguardar(self) -> None:
        if self.motor_actual is None or not self._hay_cambios():
            return
        try:
            self._guardar_en(sesion.preparar(sesion.ruta_autoguardado(self.SISTEMA)))
        except Exception as e:
            print(f"[autoguardado] falló: {e}")
            return
        self.statusBar().showMessage(f"Autoguardado a las {time.strftime('%H:%M')}", 4000)

    def _guardar_sesion(self) -> None:
        ruta = sesion.ruta_sesion(self.SISTEMA)
        if not runtime.estado.general.restaurar_sesion:
            sesion.borrar(ruta)
            return
        try:
            self._guardar_en(sesion.preparar(ruta))
        except Exception as e:
            print(f"[sesión] no se pudo guardar: {e}")

    def _confirmar_cierre(self) -> bool:
        """«Confirmar al salir»: solo pregunta si hay cambios sin guardar."""
        if not runtime.estado.general.confirmar_salir or not self._hay_cambios():
            return True
        B = QtWidgets.QMessageBox.StandardButton
        r = QtWidgets.QMessageBox.question(self, "Cambios sin guardar",
                                           "Hay cambios sin guardar en el proyecto. ¿Quieres guardarlos antes de salir?",
                                           B.Save | B.Discard | B.Cancel, B.Save)
        if r == B.Cancel:
            return False
        if r == B.Save:
            self._guardar()
            return not self._hay_cambios()      # si cancelaste el diálogo de guardado, no se sale
        return True

    # -- avisos (Ajustes → General → Avisos de datos) ------------------------------------------------------
    def _aviso(self, texto: str, ms: int = 4000) -> None:
        if runtime.estado.general.avisos_datos:
            self.statusBar().showMessage(texto, ms)

    def _aviso_modal(self, titulo: str, texto: str) -> None:
        if runtime.estado.general.avisos_datos:
            QtWidgets.QMessageBox.information(self, titulo, texto)

    @manejador_seguro
    def _exportar(self, *_):
        if self.motor_actual is None:
            self._aviso_modal("Exportar", "No hay una geometría válida para exportar: revisa los parámetros.")
            return
        from exporters.export_manager import exportar_con_dialogo
        exportar_con_dialogo(self, self._items_exportacion(), self.NOMBRE, self.ARCHIVO_EXCEL,
                             self._html_extra_exportacion())

    def _items_exportacion(self) -> list:
        """[(etiqueta, motor, parámetros)]: un elemento por engranaje a exportar (planetario: sol y anular)."""
        return [("", self.motor_actual, self.leer_parametros())]

    def _html_extra_exportacion(self) -> str:
        """HTML que antecede a las secciones del informe PDF (planetario: resumen cinemático)."""
        return ""

    # ------------------------------------------------------------------ menú: otras ventanas
    @manejador_seguro
    def _resumen(self, *_):
        if self.motor_actual is not None:
            DialogoResumenDiseno(self.motor_actual, self.leer_parametros(), self).exec()

    @manejador_seguro
    def _abrir_aux(self, fabrica):
        if self.perfil_actual is None:
            self._aviso("Aún no hay un perfil válido para mostrar.")
            return
        w = fabrica()
        self._aux.append(w)
        w.destroyed.connect(lambda *_, w=w: self._aux.remove(w) if w in self._aux else None)
        w.show()

    @manejador_seguro
    def _abrir_visibilidad(self, *_):
        if self._dlg_vis is None:
            self._dlg_vis = self.CLASE_DIALOGO_VISIBILIDAD(self.vis, self.sim.set_visibilidad, parent=self)
        self._dlg_vis.actualizar_modo(self._alterno())
        self._dlg_vis.show(); self._dlg_vis.raise_(); self._dlg_vis.activateWindow()

    # ------------------------------------------------------------------ navegación
    @manejador_seguro
    def volver_al_menu(self, *_):
        self.close()

    def closeEvent(self, e):
        if not self._confirmar_cierre():
            e.ignore()
            return
        self._pausar()
        self._t_auto.stop()
        self._guardar_sesion()
        sesion.borrar(sesion.ruta_autoguardado(self.SISTEMA))
        for w in list(self._aux):
            w.close()
        if self._retorno is not None and self._retorno.isHidden():
            self._retorno.mostrar_de_nuevo()
        super().closeEvent(e)
