# -*- coding: utf-8 -*-
"""
ui/epitrocoidal_window.py

Controlador de EpitrocoidalV2.ui: ventana principal del sistema Epitrocoidal en V2.
La ventana solo contiene los parámetros + la simulación (PyQtGraph); las propiedades
(perfil, ángulo de presión, curvatura, camino de contacto) se abren desde el menú en
ventanas independientes (ui/property_windows.py) que se refrescan con `perfilActualizado`.

Modos de simulación:
  Manual     -> dial/spinbox (ángulo acumulado) + modo del piñón, como en V1.
  Automático -> perfil de giro (engine/motion_engine.py; por defecto "Arranque y parada
                suaves"), con Play / Pausa / Reiniciar / Grabar (MP4) y editor de línea de tiempo.

Arquitectura igual a V1: la UI solo lee/valida parámetros (dataclasses), el engine calcula,
los widgets dibujan. Cada recálculo hace UNA llamada a motor.generar_patron() (que ya
incluye el análisis del perfil) y se agrupa con un debounce de 150 ms.
"""
from __future__ import annotations

import copy
import time

import numpy as np
from PySide6 import QtCore, QtWidgets

from config.app_settings import ajustes
from config.data_structures import AjustesVisibilidadSimulacion, ParametrosEpitrocoidal
from dialogs.design_summary_dialog import DialogoResumenDiseno
from dialogs.mostrar_ocultar_dialog import DialogoMostrarOcultarEpitrocoidal   # usa Mostrar_Ocultar_Epitrocoide.ui
from engine import math_utils as mu
from engine.cinematica_engine import SolverCinematico
from engine.epitrocoidal_engine import EpitrocoidalEngine
from engine.motion_engine import PRESET_DEFECTO, FabricaPresets, LineaTiempo, RegistroLeyes
from engine.motor_plan import plan_alineacion, planificar
from hardware.motor_controller import obtener_controlador
from exporters.excel_exporter import exportar_excel
from exporters.video_recorder import GrabadorVideo
from ui.errores import manejador_seguro
from ui.property_windows import VentanaPerfilDiente, VentanaPropiedad
from ui.settings_window import SettingsWindow
from ui.velocity_profile_window import VentanaPerfilVelocidad
from utils import file_handler
from widgets.pg_helpers import AngleControl, reemplazar_widget
from widgets.simulation_view import SimulationView

from EpitrocoidalV2 import Ui_EpitrocoidalV2   # noqa: E402

FPS_VIDEO = 30


class VentanaEpitrocoidalV2(QtWidgets.QMainWindow):
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

        self.ui = Ui_EpitrocoidalV2()
        self.ui.setupUi(self)
        self.sim = reemplazar_widget(self.ui.graphicsView_epi, SimulationView())
        self.control = AngleControl(self.ui.dial_posicion_theta, self.ui.doubleSpinBox_posicion_theta, self)

        self._debounce = QtCore.QTimer(self, singleShot=True, interval=150)
        self._debounce.timeout.connect(self._recalcular)
        self._anim = QtCore.QTimer(self)
        self._anim.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
        self._anim.setInterval(8)
        self._anim.timeout.connect(self._tick)

        self.motor_ctrl = obtener_controlador()
        self.motor_ctrl.terminado.connect(self._motor_terminado)
        self.motor_ctrl.progreso.connect(self._motor_progreso)
        self._conectar()
        self._aplicar_modo()
        self._recalcular()

    # ------------------------------------------------------------------
    # Conexiones
    # ------------------------------------------------------------------
    def _spins(self):
        u = self.ui
        return (u.spinBox_numerodedientes, u.spinBox_numeroderodillos, u.doubleSpinBox_diametro_rodillos,
                u.doubleSpinBox_distancia_centros_rodillos, u.doubleSpinBox_angulo_presion_minimo)

    def _conectar(self):
        u = self.ui
        for sp in self._spins():
            sp.valueChanged.connect(lambda *_: self._debounce.start())
        self.control.cambiado.connect(lambda *_: self._emitir_estado())
        u.comboBox_modo_pinon.currentIndexChanged.connect(lambda *_: self._modo_pinon_cambiado())
        u.comboBox_modo_sim.currentIndexChanged.connect(lambda *_: self._aplicar_modo())
        u.pushButton_mostrar_ocultar.clicked.connect(lambda *_: self._abrir_visibilidad())
        u.pushButton_sim_reset.clicked.connect(lambda *_: self._reset())
        u.pushButton_anim_play.clicked.connect(lambda *_: self._play())
        u.pushButton_anim_pause.clicked.connect(lambda *_: self._pausar())
        u.pushButton_restart.clicked.connect(lambda *_: self._reiniciar())
        u.pushButton_record.clicked.connect(lambda *_: self._grabar())
        u.Editarlineadetiempo_button.clicked.connect(lambda *_: self._editar_linea_tiempo())
        u.checkBox_valpredeterminados.toggled.connect(self._predeterminado_cambiado)
        # Menú
        u.actionAbrir.triggered.connect(lambda *_: self._abrir())
        u.actionGuardar.triggered.connect(lambda *_: self._guardar())
        u.actionExportar.triggered.connect(lambda *_: self._exportar())
        u.actionConfiguraci_n.triggered.connect(lambda *_: SettingsWindow(self).exec())
        u.actionCerrar.triggered.connect(lambda *_: self.volver_al_menu())
        u.actionGu_a_T_cnica.triggered.connect(lambda *_: QtWidgets.QMessageBox.information(
            self, "Guía técnica", "La guía técnica se desarrollará más adelante."))
        u.actionResumen_de_Dise_o.triggered.connect(lambda *_: self._resumen())
        u.actionPerfil_del_diente.triggered.connect(lambda *_: self._abrir_aux(lambda: VentanaPerfilDiente(self)))
        u.action_ngulo_de_Presi_n.triggered.connect(lambda *_: self._abrir_aux(lambda: VentanaPropiedad(self, "angulo")))
        u.actionRadio_de_Curvatura.triggered.connect(lambda *_: self._abrir_aux(lambda: VentanaPropiedad(self, "curvatura")))
        u.actionCamino_de_Contacto.triggered.connect(lambda *_: self._abrir_aux(lambda: VentanaPropiedad(self, "contacto")))

    # ------------------------------------------------------------------
    # Parámetros y motor
    # ------------------------------------------------------------------
    def leer_parametros(self) -> ParametrosEpitrocoidal:
        u = self.ui
        return ParametrosEpitrocoidal(
            numero_dientes=u.spinBox_numerodedientes.value(),
            numero_rodillos=u.spinBox_numeroderodillos.value(),
            diametro_rodillos=u.doubleSpinBox_diametro_rodillos.value(),
            distancia_centro_rodillos=u.doubleSpinBox_distancia_centros_rodillos.value(),
            angulo_presion_minimo=u.doubleSpinBox_angulo_presion_minimo.value())

    @manejador_seguro
    def _recalcular(self, *_):
        p = self.leer_parametros()
        if not p.es_valido():
            self.statusBar().showMessage("Parámetros fuera de rango: la geometría no se recalcula.", 4000)
            return
        motor = EpitrocoidalEngine(p)
        res = motor.generar_patron()          # incluye el análisis del perfil (1 sola pasada)
        self.motor_actual, self.perfil_actual = motor, res
        self._solver = SolverCinematico(motor.contexto)
        self.sim.set_geometria(res)
        th = np.linspace(0.0, 2.0 * np.pi, 2001)       # epitrocoide base: θ de 0 a 2π, solo el diente 0
        bx, by = motor.curva_generatriz(th)
        self.sim.set_curva_base(*mu.rotar(bx, by, np.radians(motor.ROTACION_VISTA_SIMULACION_GRADOS)))
        self.perfilActualizado.emit(res)
        self._emitir_estado()

    # ------------------------------------------------------------------
    # Estado de la simulación
    # ------------------------------------------------------------------
    def _modo_pinon_cambiado(self):
        if self._dlg_vis is not None:
            self._dlg_vis.actualizar_modo(self.ui.comboBox_modo_pinon.currentIndex() == 1)
        self._emitir_estado()

    def _es_auto(self) -> bool:
        return self.ui.comboBox_modo_sim.currentIndex() == 1

    def _angulo_motor(self) -> float:
        if self._es_auto() and self.linea_tiempo is not None:
            return self.linea_tiempo.posicion_en(self._t)
        return self.control.acumulado

    def _estado_para(self, angulo_grados: float):
        alt = self.ui.comboBox_modo_pinon.currentIndex() == 1
        est = self._solver.resolver("angular", True, alt, angulo_grados, 0.0)
        cont = self.motor_actual.rodillos_en_contacto(
            est.angulo_relativo_generatriz_rad, modo_pinon_alterno=alt, estado_cinematico=est)
        return est, cont

    @manejador_seguro
    def _emitir_estado(self, *_):
        if self.motor_actual is None:
            return
        self.sim.actualizar(*self._estado_para(self._angulo_motor()))

    # ------------------------------------------------------------------
    # Manual / Automático
    # ------------------------------------------------------------------
    @manejador_seguro
    def _aplicar_modo(self, *_):
        auto = self._es_auto()
        u = self.ui
        self._pausar()
        if auto:
            self._construir_linea_tiempo()
            self._t = self.linea_tiempo.t_ini if self.linea_tiempo else 0.0
        else:
            if self.linea_tiempo is not None:
                self.control.reiniciar(self.linea_tiempo.posicion_en(self._t))
        for w in (u.dial_posicion_theta, u.doubleSpinBox_posicion_theta):
            w.setEnabled(not auto)
        for w in (u.frame_anim_controls, u.Editarlineadetiempo_button, u.checkBox_valpredeterminados):
            w.setEnabled(auto)
        self._emitir_estado()

    def _construir_linea_tiempo(self):
        try:
            self.linea_tiempo = LineaTiempo.construir(self.perfil_mov, RegistroLeyes())
            if self.linea_tiempo.errores:
                self.statusBar().showMessage("Aviso: " + " | ".join(self.linea_tiempo.errores[-3:]), 6000)
        except Exception as e:
            self.linea_tiempo = None
            self.statusBar().showMessage(f"Perfil de giro inválido: {e}", 6000)

    @manejador_seguro
    def _predeterminado_cambiado(self, marcado: bool):
        if marcado:
            self.perfil_mov = copy.deepcopy(self.perfil_mov_defecto)
            self._reconstruir_auto()

    def _reconstruir_auto(self):
        self._pausar()
        self._construir_linea_tiempo()
        self._t = self.linea_tiempo.t_ini if self.linea_tiempo else 0.0
        self._mostrar_auto()

    @manejador_seguro
    def _editar_linea_tiempo(self, *_):
        self._editor = VentanaPerfilVelocidad(self.perfil_mov, self)
        self._editor.perfilAceptado.connect(self._perfil_aceptado)
        self._editor.show()

    @manejador_seguro
    def _perfil_aceptado(self, perfil):
        self.perfil_mov = perfil
        chk = self.ui.checkBox_valpredeterminados
        chk.blockSignals(True); chk.setChecked(False); chk.blockSignals(False)
        self._reconstruir_auto()

    # -- reproducción ---------------------------------------------------
    def _motor_activo(self) -> bool:
        return ajustes.motor.habilitado and self._es_auto()

    @manejador_seguro
    def _play(self, *_):
        lt = self.linea_tiempo
        if not self._es_auto() or lt is None or self._anim.isActive():
            return
        if self._t >= lt.t_fin:
            self._t = lt.t_ini
        if self._motor_activo():
            ctrl, aj = self.motor_ctrl, ajustes.motor
            if not ctrl.conectado:
                QtWidgets.QMessageBox.information(self, "Motor", "El motor está habilitado pero no conectado.\n"
                                                  "Conéctalo en Archivo → Ajustes.")
                return
            if ctrl.ocupado():
                self.statusBar().showMessage("Esperando a que el motor termine de detenerse…", 3000)
                return
            error = lt.posicion_en(self._t) - ctrl.pos_deg
            if abs(error) > aj.tolerancia_silenciosa_deg:
                r = self._preguntar_desfase(error)
                if r == "cancelar":
                    return
                if r == "alinear":
                    self.statusBar().showMessage(f"Alineando el motor ({error:+.1f}°)…")
                    ctrl.ejecutar([plan_alineacion(error, aj)], "alineacion")
                    return                      # la simulación arranca al terminar la alineación
                ctrl.referenciar(lt.posicion_en(self._t))
        self._arrancar()

    def _preguntar_desfase(self, error: float) -> str:
        m = QtWidgets.QMessageBox(self)
        m.setWindowTitle("Motor desalineado")
        m.setText(f"La posición estimada del motor difiere {error:+.1f}° de la simulación.")
        b_al = m.addButton("Alinear (mover el motor)", QtWidgets.QMessageBox.ButtonRole.AcceptRole)
        b_ref = m.addButton("Tomar la posición actual como referencia", QtWidgets.QMessageBox.ButtonRole.ActionRole)
        m.addButton("Cancelar", QtWidgets.QMessageBox.ButtonRole.RejectRole)
        m.exec()
        return {b_al: "alinear", b_ref: "referenciar"}.get(m.clickedButton(), "cancelar")

    def _arrancar(self):
        lt = self.linea_tiempo
        if self._motor_activo() and self.motor_ctrl.conectado:
            segs, avisos = planificar(lt, self._t, self.motor_ctrl.pos_deg, ajustes.motor)
            if avisos:
                self.statusBar().showMessage("Motor: " + " ".join(avisos), 8000)
            self.motor_ctrl.ejecutar(segs, "perfil")
        self._t_ultimo = time.perf_counter()
        self._anim.start()

    @manejador_seguro
    def _motor_terminado(self, ok: bool, msg: str, etiqueta: str):
        if etiqueta == "alineacion":
            if ok and self._es_auto():
                self._arrancar()
            elif msg:
                QtWidgets.QMessageBox.warning(self, "Motor", f"Falló la alineación:\n{msg}")
        elif not ok and msg:                    # error real (no una parada pedida por el usuario)
            self._pausar(detener_motor=False)
            QtWidgets.QMessageBox.warning(self, "Motor", f"El motor reportó un error y se detuvo la simulación:\n{msg}")

    def _motor_progreso(self, i: int, n: int):
        if self._anim.isActive():
            self.statusBar().showMessage(f"Motor: tramo {i}/{n}", 1500)

    def _pausar(self, detener_motor: bool = True):
        corriendo = self._anim.isActive()
        self._anim.stop()
        if detener_motor:
            estaba = self.motor_ctrl.ocupado()
            self.motor_ctrl.detener()
            if corriendo and estaba and self.linea_tiempo is not None and self._es_auto():
                self._resincronizar_con_motor()

    def _resincronizar_con_motor(self):
        """Tras pausar, el motor queda donde lo dejó la parada (estimado) y va por detrás de la
        simulación (avanza por tramos con rampas). Se retrocede el tiempo de la simulación hasta
        el instante cuya posición coincide con la del motor: al reanudar no hay desfase que corregir."""
        lt = self.linea_tiempo
        idx = np.flatnonzero((lt.t <= self._t + 2.0 * ajustes.motor.dt_segmento) & (lt.t >= self._t - 2.0 * ajustes.motor.dt_segmento))
        if idx.size:
            k = idx[int(np.argmin(np.abs(lt.pos[idx] - self.motor_ctrl.pos_deg)))]
            self._t = float(lt.t[k])
            self._mostrar_auto()

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
            self._pausar(detener_motor=False)      # el último tramo del motor termina solo
        self._mostrar_auto()

    def _mostrar_auto(self):
        if self.linea_tiempo is None:
            return
        ang = self.linea_tiempo.posicion_en(self._t)
        self.control.mostrar(ang)
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

    # -- grabación ------------------------------------------------------
    @manejador_seguro
    def _grabar(self, *_):
        lt = self.linea_tiempo
        if not self._es_auto() or lt is None or self.motor_actual is None:
            return
        ruta, _f = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar video de la simulación",
                                                         "simulacion.mp4", "Video MP4 (*.mp4)")
        if not ruta:
            return
        self._pausar()
        t_prev = self._t
        n = int(lt.duracion * FPS_VIDEO) + 1
        tiempos = lt.t_ini + np.arange(n) / FPS_VIDEO
        angulos = lt.posiciones_en(tiempos)          # vectorizado (xp según hardware)
        prog = QtWidgets.QProgressDialog("Grabando video…", "Cancelar", 0, n, self)
        prog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        prog.setMinimumDuration(0)
        grab = GrabadorVideo(ruta, FPS_VIDEO)
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
                grab.agregar(self.sim.fotograma())
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

    # ------------------------------------------------------------------
    # Menú: archivo
    # ------------------------------------------------------------------
    def _sim_dict(self) -> dict:
        return {"modo": self.ui.comboBox_modo_sim.currentIndex(),
                "modo_pinon": self.ui.comboBox_modo_pinon.currentIndex(),
                "angulo_manual": self.control.acumulado,
                "predeterminado": self.ui.checkBox_valpredeterminados.isChecked()}

    @manejador_seguro
    def _guardar(self, *_):
        ruta = self._ruta
        if not ruta:
            ruta, _f = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar proyecto", "proyecto.json", "Proyecto RPS (*.json)")
        if not ruta:
            return
        pm = None if self.ui.checkBox_valpredeterminados.isChecked() else self.perfil_mov
        file_handler.guardar_proyecto(ruta, self.leer_parametros(), self._sim_dict(), pm, self.vis)
        self._ruta = ruta
        self.statusBar().showMessage(f"Proyecto guardado: {ruta}", 5000)

    @manejador_seguro
    def _abrir(self, *_):
        ruta, _f = QtWidgets.QFileDialog.getOpenFileName(self, "Abrir proyecto", "", "Proyecto RPS (*.json)")
        if not ruta:
            return
        try:
            d = file_handler.abrir_proyecto(ruta)
        except file_handler.ArchivoInvalido as e:
            QtWidgets.QMessageBox.warning(self, "Abrir proyecto", str(e))
            return
        self._pausar()
        p = d["parametros"]
        for sp, v in zip(self._spins(), (p.numero_dientes, p.numero_rodillos, p.diametro_rodillos,
                                         p.distancia_centro_rodillos, p.angulo_presion_minimo)):
            sp.blockSignals(True); sp.setValue(v); sp.blockSignals(False)
        s = d["simulacion"]
        self.vis = d["visibilidad"]
        self.sim.set_visibilidad(self.vis)
        self._dlg_vis = None
        if d["perfil_movimiento"] is not None:
            self.perfil_mov = d["perfil_movimiento"]
        else:
            self.perfil_mov = copy.deepcopy(self.perfil_mov_defecto)
        for w, v in ((self.ui.checkBox_valpredeterminados, d["perfil_movimiento"] is None),
                     (self.ui.comboBox_modo_pinon, s.get("modo_pinon", 0))):
            w.blockSignals(True)
            w.setChecked(v) if isinstance(w, QtWidgets.QCheckBox) else w.setCurrentIndex(int(v))
            w.blockSignals(False)
        self.control.reiniciar(float(s.get("angulo_manual", 0.0)))
        self.ui.comboBox_modo_sim.blockSignals(True)
        self.ui.comboBox_modo_sim.setCurrentIndex(int(s.get("modo", 0)))
        self.ui.comboBox_modo_sim.blockSignals(False)
        self._recalcular()
        self._aplicar_modo()
        self._ruta = ruta
        self.statusBar().showMessage(f"Proyecto abierto: {ruta}", 5000)

    @manejador_seguro
    def _exportar(self, *_):
        if self.motor_actual is None:
            return
        ruta, _f = QtWidgets.QFileDialog.getSaveFileName(self, "Exportar a Excel", "epitrocoidal.xlsx", "Libro de Excel (*.xlsx)")
        if not ruta:
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            exportar_excel(ruta, self.motor_actual, self.leer_parametros())
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
        self.statusBar().showMessage(f"Excel exportado: {ruta}", 5000)

    # ------------------------------------------------------------------
    # Menú: otras ventanas
    # ------------------------------------------------------------------
    @manejador_seguro
    def _resumen(self, *_):
        if self.motor_actual is not None:
            DialogoResumenDiseno(self.motor_actual, self.leer_parametros(), self).exec()

    @manejador_seguro
    def _abrir_aux(self, fabrica):
        if self.perfil_actual is None:
            self.statusBar().showMessage("Aún no hay un perfil válido para mostrar.", 4000)
            return
        w = fabrica()
        self._aux.append(w)
        w.destroyed.connect(lambda *_, w=w: self._aux.remove(w) if w in self._aux else None)
        w.show()

    @manejador_seguro
    def _abrir_visibilidad(self, *_):
        if self._dlg_vis is None:
            self._dlg_vis = DialogoMostrarOcultarEpitrocoidal(self.vis, self.sim.set_visibilidad, parent=self)
        self._dlg_vis.actualizar_modo(self.ui.comboBox_modo_pinon.currentIndex() == 1)
        self._dlg_vis.show(); self._dlg_vis.raise_(); self._dlg_vis.activateWindow()

    # ------------------------------------------------------------------
    # Navegación
    # ------------------------------------------------------------------
    @manejador_seguro
    def volver_al_menu(self, *_):
        self.close()

    def closeEvent(self, e):
        self._pausar()
        for sig, slot in ((self.motor_ctrl.terminado, self._motor_terminado), (self.motor_ctrl.progreso, self._motor_progreso)):
            try:
                sig.disconnect(slot)
            except (RuntimeError, TypeError):
                pass
        for w in list(self._aux):
            w.close()
        if self._retorno is not None and self._retorno.isHidden():
            self._retorno.mostrar_de_nuevo()
        super().closeEvent(e)
