# -*- coding: utf-8 -*-
"""
ui/estudio_qt.py

`GestorEstudio`: estado del estudio físico (régimen de contacto) de UNA ventana de sistema
(funciones 5, 7, 56–58, 60). Vive en la ventana de sistema (no en el editor), así que cerrar el editor no
interrumpe un cálculo en curso.

HILO vs PROCESO: el cálculo es NumPy sobre arreglos pequeños por muestra (~1–10 ms) y depende de engines
con estado (perfiles, cachés) caros de serializar; un proceso en Windows (spawn) tardaría más en arrancar y
copiar el contexto que muchos estudios completos. Se usa un QThread con cancelación cooperativa por
muestra: la interfaz recibe progreso por señales en cola y nunca se bloquea más de una muestra.

Estados: Sin estudio · Calculando · Finalizado · Cancelado · Error · Desactualizado.
`Finalizado` solo tras una ejecución válida; si cambian geometría, perfil, modo o parámetros físicos la
huella deja de coincidir y el resultado pasa a `Desactualizado` (se conserva para consulta, no se muestra
como válido sobre la geometría).
"""
from __future__ import annotations

import copy
import json
import threading
import traceback
from dataclasses import asdict

from PySide6 import QtCore

import numpy as np

from engine import sampling_preferences
from utils.formato_numerico import fmt
from engine.estudio_fisico import (BibliotecaEscenarios, Cancelado, Escenario, ResultadoEstudio,
                                   ejecutar_estudio, estimar_costo, huella_estudio)
from engine.mecanismos_fisicos import adaptador_para

SIN_ESTUDIO, CALCULANDO, FINALIZADO, CANCELADO, ERROR, DESACTUALIZADO = (
    "Sin estudio", "Calculando", "Finalizado", "Cancelado", "Error", "Desactualizado")
ESTADOS = (SIN_ESTUDIO, CALCULANDO, FINALIZADO, CANCELADO, ERROR, DESACTUALIZADO)


def contacto_habilitado() -> bool:
    try:
        from ui.ajustes_runtime import runtime
        return bool(runtime.estado.simulacion.basada_en_contacto)
    except Exception:
        return False


class _Hilo(QtCore.QThread):
    avance = QtCore.Signal(int, int)
    listo = QtCore.Signal(object)
    fallo = QtCore.Signal(str)
    cancelado_sig = QtCore.Signal()

    def __init__(self, tarea, parent=None):
        super().__init__(parent)
        self._tarea = tarea
        self.evento_cancelar = threading.Event()

    def run(self):
        try:
            r = self._tarea(lambda i, n: self.avance.emit(int(i), int(n)), self.evento_cancelar.is_set)
            self.listo.emit(r)
        except Cancelado:
            self.cancelado_sig.emit()
        except Exception as e:                       # recuperación segura: la interfaz queda operativa
            traceback.print_exc()
            self.fallo.emit(f"{type(e).__name__}: {e}")


class GestorEstudio(QtCore.QObject):
    estadoCambiado = QtCore.Signal(str, str)      # estado, detalle
    progreso = QtCore.Signal(int, int)
    resultadoListo = QtCore.Signal(object)
    inspeccion = QtCore.Signal(float)             # cursor temporal (s) -> la ventana muestra esa geometría

    def __init__(self, ventana):
        super().__init__(ventana)
        self.v = ventana
        self.biblioteca = BibliotecaEscenarios()
        self.escenario = Escenario()               # el aplicado al último estudio / editado en el editor
        self.seleccion = self.escenario.nombre
        self.resultado: ResultadoEstudio | None = None
        self.estado, self.detalle = SIN_ESTUDIO, ""
        self._hilo: _Hilo | None = None
        self._perfil_estudio = None
        self.escenario_edicion: Escenario | None = None   # lo que muestra el editor (aunque no esté guardado)
        self._ad_inst = (None, None)

    # ------------------------------------------------------------------ estado
    def _set(self, estado: str, detalle: str = "") -> None:
        self.estado, self.detalle = estado, detalle
        self.estadoCambiado.emit(estado, detalle)

    def calculando(self) -> bool:
        return self._hilo is not None and self._hilo.isRunning()

    def valido(self) -> bool:
        return self.estado == FINALIZADO and self.resultado is not None

    def huella(self, perfil_mov=None, escenario: Escenario | None = None) -> str:
        v = self.v
        pm = perfil_mov if perfil_mov is not None else v.perfil_mov
        try:
            params = asdict(v.leer_parametros())
        except Exception:
            params = {}
        return huella_estudio(v.SISTEMA, params, bool(v._alterno()), pm.to_dict() if pm else None,
                              v._rango_angulo_auto(), (escenario or self.escenario).to_dict(),
                              sampling_preferences.politica_actual().clave)

    def verificar(self) -> None:
        """Invalida el resultado si cambió algo que lo determina (geometría, perfil, modo, física)."""
        if self.calculando() or self.resultado is None:
            return
        vigente = self.resultado.huella == self.huella()
        if vigente and self.estado == DESACTUALIZADO:
            self._set(FINALIZADO, "resultado vigente")
        elif not vigente and self.estado == FINALIZADO:
            self._set(DESACTUALIZADO, "cambió la geometría, el perfil o los parámetros físicos")

    def escenario_vigente(self) -> Escenario:
        return copy.deepcopy(self.escenario_edicion or self.escenario)

    def estado_instantaneo(self, theta_deg: float, omega_deg_s: float) -> dict:
        """Equilibrio cuasiestático en UNA posición (modo manual): fuerzas, deflexión y par motor al vuelo."""
        from engine import contacto_fisico as cf
        from engine.cargas import DEP_OMEGA, DEP_T, EN_ENTRADA
        e = self.escenario_edicion or self.escenario
        clave = (getattr(self.v, "_clave_pintada", None), self.v._alterno())
        if self._ad_inst[0] != clave:
            self._ad_inst = (clave, self.adaptador())
        ad = self._ad_inst[1]
        ent = e.carga.componente == EN_ENTRADA
        rel = ad.relacion(theta_deg)
        if e.carga.dependencia == DEP_T:
            T = 0.0 if e.carga.ley == "Constante" else float("nan")
            if e.carga.ley == "Constante":
                T = e.carga.constante
        else:
            x = (theta_deg if ent else ad.salida_desde_entrada(theta_deg)) if e.carga.dependencia != DEP_OMEGA \
                else (omega_deg_s if ent else rel * omega_deg_s)
            T = float(e.carga.evaluar([x])[0])
        c = ad.contactos(theta_deg)
        if not np.isfinite(T):
            return dict(q=None, cs=[], texto="Contacto (manual): carga T(t) sin tiempo definido en modo manual")
        tol = [e.solucionador.tol_equilibrio_n if tp == "traslación" else e.solucionador.tol_momento_n_mm
               for _, tp in ad.coordenadas]
        modelo = e.contacto.modelo if e.contacto.modelo != cf.MODELO_GEOMETRICO else cf.MODELO_GEOMETRICO
        eq = cf.resolver_equilibrio(c.gap, c.J, np.zeros(ad.m) if ent else ad.Q_salida(T), modelo,
                                    e.contacto.rigidez_n_mm, e.contacto.tolerancia_brecha_mm, tol,
                                    e.solucionador.max_iteraciones, e.contacto.reparto)
        if eq.estado != cf.DETERMINADO:
            return dict(q=None, cs=[], texto=f"Contacto (manual): {eq.estado} — {eq.mensaje}")
        mom = ad.momentos(theta_deg, c, eq.F)
        tm = ad.par_motor(mom, T if ent else 0.0)
        cs = [dict(px=float(c.px[i]), py=float(c.py[i]), nx=float(c.nx[i]), ny=float(c.ny[i]), Fn=float(eq.F[i]))
              for i in range(c.n) if eq.F[i] > 0]
        txt = (f"Contacto (manual, cuasiestático): par motor = {fmt(tm, 'N·m')}"
               + (f" · Fn máx = {fmt(max(x['Fn'] for x in cs), 'N')}" if cs else " · sin carga"))
        return dict(q=np.asarray(eq.q, float), cs=cs, texto=txt)

    # ------------------------------------------------------------------ preparación
    def adaptador(self):
        v = self.v
        if v.motor_actual is None:
            raise RuntimeError("no hay una geometría válida")
        res = None if v.SISTEMA == "PLANETARIO" else v.perfil_actual
        return adaptador_para(v.SISTEMA, v.motor_actual, res, v._alterno())

    def estimar(self, perfil_mov, escenario: Escenario) -> dict:
        from engine.estudio_fisico import parametros_muestreo
        lt = self.v.linea_tiempo_para(perfil_mov)
        est, n0, nmax = parametros_muestreo(escenario.solucionador, sampling_preferences.politica_actual())
        e = estimar_costo(self.adaptador(), lt, escenario, n0)
        e["estrategia"], e["n_max"] = est, nmax
        return e

    # ------------------------------------------------------------------ ejecución
    def ejecutar(self, perfil_mov, escenario: Escenario) -> bool:
        if self.calculando():
            return False
        if not contacto_habilitado():
            self._set(ERROR, "el análisis por contacto está desactivado en Ajustes → Simulación")
            return False
        try:
            avisos = []
            lt = self.v.linea_tiempo_para(perfil_mov, avisos)      # mismo escalado/desplazamiento/recorte que la simulación
            ad = self.adaptador()
            err = escenario.motor.validar() if escenario.motor.modo.startswith("Evaluación") else []
            err += escenario.carga.validar()
            from engine.estudio_fisico import METODO_DINAMICO
            from engine import contacto_fisico as cf
            if escenario.solucionador.metodo == METODO_DINAMICO and (
                    escenario.contacto.modelo != cf.MODELO_PENALIZACION or escenario.contacto.rigidez_n_mm <= 0):
                err.append("la simulación dinámica requiere «Penalización elástica unilateral» y una rigidez normal "
                           "> 0 (editor de regímenes → Contacto)")
            if err:
                self._set(ERROR, "; ".join(err))
                return False
        except Exception as e:
            self._set(ERROR, str(e))
            return False
        esc = copy.deepcopy(escenario)
        huella = self.huella(perfil_mov, esc)
        pol = sampling_preferences.politica_actual()
        sistema = self.v.SISTEMA

        def tarea(avance, cancelado):
            r = ejecutar_estudio(ad, lt, esc, sistema, huella, pol, avance, cancelado)
            r.meta["transformacion_perfil"] = avisos or ["ninguna (el perfil cabe en el recorrido)"]
            return r

        self.escenario = esc
        self._perfil_estudio = copy.deepcopy(perfil_mov)
        h = _Hilo(tarea, self)
        h.avance.connect(self.progreso)
        h.listo.connect(self._terminado)
        h.fallo.connect(lambda m: self._set(ERROR, m))
        h.cancelado_sig.connect(lambda: self._set(CANCELADO, "cancelado por el usuario"))
        h.finished.connect(lambda: setattr(self, "_hilo", None))
        self._hilo = h
        h.start()
        self._set(CALCULANDO, "")
        return True

    def cancelar(self) -> None:
        if self._hilo is not None:
            self._hilo.evento_cancelar.set()

    def esperar(self, ms: int = 60000) -> bool:
        h = self._hilo
        return True if h is None else h.wait(ms)

    def _terminado(self, r: ResultadoEstudio) -> None:
        self.resultado = r
        dur = r.meta.get("duracion_medida_s", 0.0)
        self._set(FINALIZADO, f"{len(r.t)} muestras · {dur:.2f} s medidos")
        self.resultadoListo.emit(r)
        self.verificar()

    # ------------------------------------------------------------------ persistencia (función 7)
    def to_dict(self) -> dict:
        return {"version": 1, "biblioteca": self.biblioteca.to_dict(), "escenario": self.escenario.to_dict(),
                "seleccion": self.seleccion,
                "resultado": self.resultado.to_dict() if self.resultado is not None else None}

    def huella_config(self) -> str:
        """Para «cambios sin guardar»: configuración (no los arreglos de resultados)."""
        d = self.to_dict()
        d["resultado"] = self.resultado.huella if self.resultado is not None else None
        return json.dumps(d, sort_keys=True, default=str)

    def cargar(self, d: dict | None) -> None:
        """Compatibilidad hacia atrás: proyectos sin la sección -> estudio vacío."""
        self.cancelar()
        d = d or {}
        self.biblioteca = BibliotecaEscenarios.from_dict(d.get("biblioteca"))
        self.escenario = Escenario.from_dict(d.get("escenario")) if d.get("escenario") else Escenario()
        self.seleccion = d.get("seleccion", self.escenario.nombre)
        r = d.get("resultado")
        self.resultado = ResultadoEstudio.from_dict(r) if r else None
        if self.resultado is None:
            self._set(SIN_ESTUDIO)
        else:
            self.estado = DESACTUALIZADO
            self.verificar()
            if self.estado == DESACTUALIZADO:
                self._set(DESACTUALIZADO, "el resultado guardado no corresponde a la configuración actual")
