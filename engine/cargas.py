# -*- coding: utf-8 -*-
"""
engine/cargas.py

Editores de par PRESCRITO T(t), T(θ), T(ω) (funciones 12–16). Reutilizan las leyes de
`engine.motion_engine.RegistroLeyes` (rampas, sinusoidales, polinomios, lista de puntos y spline)
evaluadas sobre la variable independiente elegida en lugar del tiempo. Sin Qt.

Dominio y periodicidad:
  - Constante, Sinusoidal y Polinómica son analíticas: definidas para toda abscisa.
  - Las leyes definidas por puntos (rampas, lista de puntos, spline) solo valen en [x_min, x_max] de sus
    puntos; fuera de él la carga es INDETERMINADA (NaN), salvo que se declare un periodo: entonces la
    abscisa se reduce a [x_min, x_min + periodo).
Unidades: t [s]; θ [°] (o x [mm] en la cremallera); ω [°/s] (o v [mm/s]); par [N·m] (fuerza [N] en la
cremallera). Convención: valor POSITIVO = par/fuerza RESISTENTE que se opone al sentido positivo del
componente donde se aplica.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

import numpy as np

from engine.motion_engine import Ley, RegistroLeyes, Tramo

DEP_T, DEP_THETA, DEP_OMEGA = "t", "theta", "omega"
DEPENDENCIAS = (DEP_T, DEP_THETA, DEP_OMEGA)
CONSTANTE = "Constante"
ANALITICAS = {CONSTANTE, "Sinusoidal", "Polinómica"}
EN_SALIDA, EN_ENTRADA = "salida", "entrada"


def dependencia_desde_indice(i: int) -> str:
    return DEPENDENCIAS[max(0, min(int(i), 2))]


@dataclass
class CargaExterna:
    dependencia: str = DEP_T
    ley: str = CONSTANTE
    constante: float = 0.0
    puntos: list = field(default_factory=list)          # [[x, T], ...]
    amplitud: float = 0.0
    frecuencia: float = 1.0                             # ciclos por unidad de abscisa
    fase_deg: float = 0.0
    grado: int = 1
    periodo: float = 0.0                                # 0 = no periódica
    componente: str = EN_SALIDA

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "CargaExterna":
        campos = CargaExterna.__dataclass_fields__
        return CargaExterna(**{k: v for k, v in (d or {}).items() if k in campos})

    @property
    def es_nula(self) -> bool:
        return self.ley == CONSTANTE and self.constante == 0.0

    def _pts(self):
        p = np.asarray(self.puntos, float).reshape(-1, 2) if self.puntos else np.zeros((0, 2))
        p = p[np.all(np.isfinite(p), axis=1)]
        return p[np.argsort(p[:, 0], kind="stable")] if len(p) else p

    def validar(self) -> list[str]:
        e = []
        if self.dependencia not in DEPENDENCIAS:
            e.append(f"dependencia desconocida: {self.dependencia}")
        p = self._pts()
        if self.ley not in ANALITICAS:
            if len(p) < 2:
                e.append(f"{self.ley}: requiere al menos 2 puntos (abscisa, par)")
            elif p[-1, 0] <= p[0, 0]:
                e.append(f"{self.ley}: las abscisas deben abarcar un intervalo no nulo")
            if self.ley == "Lista de puntos" and len(p) < self.grado + 1:
                e.append(f"Lista de puntos: grado {self.grado} requiere {self.grado + 1} puntos")
        if self.periodo < 0:
            e.append("el periodo no puede ser negativo")
        return e

    def evaluar(self, x) -> np.ndarray:
        """Par prescrito en las abscisas x (NaN fuera del dominio de una ley tabulada no periódica)."""
        x = np.asarray(x, float)
        if self.validar():
            return np.full_like(x, np.nan)
        if self.ley == CONSTANTE:
            return np.full_like(x, float(self.constante))
        reg = RegistroLeyes()
        if self.ley == "Sinusoidal":
            tr = Tramo(0.0, 1.0, self.constante, self.constante)
            ley = Ley("Sinusoidal", {"amplitud": self.amplitud, "frecuencia": self.frecuencia, "fase": self.fase_deg})
            return self.constante + reg.evaluar(x, tr, ley, 0)
        if self.ley == "Polinómica":
            filas = np.asarray(self.puntos, float).reshape(-1, 2) if self.puntos else np.zeros((0, 2))
            coef = [float(v) for v in filas[:, 1]] if len(filas) else [float(self.constante)]   # fila i = a_i
            return reg.evaluar(x, Tramo(0.0, 1.0), Ley("Polinómica", {"coeficientes": coef}), 0)
        p = self._pts()
        x0, x1 = float(p[0, 0]), float(p[-1, 0])
        xe = x.copy()
        if self.periodo > 0:
            xe = x0 + np.mod(x - x0, self.periodo)
        fuera = (xe < x0 - 1e-12) | (xe > x1 + 1e-12)
        xc = np.clip(xe, x0, x1)
        tr = Tramo(x0, x1, float(p[0, 1]), float(p[-1, 1]))
        if self.ley == "Spline":
            ley = Ley("Spline", {"puntos": p.tolist()})           # pendientes extremas: secantes
            val = tr.y_ini + reg.evaluar(xc, tr, ley, 0)
        elif self.ley == "Lista de puntos":
            ley = Ley("Lista de puntos", {"puntos": p.tolist(), "grado": int(self.grado)})
            val = tr.y_ini + reg.evaluar(xc, tr, ley, 0)
        else:                                       # rampas: del primer al último punto
            val = tr.y_ini + reg.evaluar(xc, tr, Ley(self.ley, {"pendiente": None}), 0)
        if reg.errores:
            return np.full_like(x, np.nan)
        return np.where(fuera, np.nan, val)


    def compilada(self, n: int = 8193):
        """Evaluador ESCALAR rápido (integración temporal): misma ley que `evaluar`. Las leyes analíticas se
        evalúan en forma cerrada; las tabuladas se remuestrean una sola vez en `n` nodos de su dominio
        (interpolación lineal; error de remuestreo < 1e-6 del rango para n = 8193)."""
        import math as _m
        if self.validar():
            return lambda x: float("nan")
        if self.ley == CONSTANTE:
            v = float(self.constante)
            return lambda x: v
        if self.ley == "Sinusoidal":
            c, A, f, ph = float(self.constante), float(self.amplitud), float(self.frecuencia), _m.radians(self.fase_deg)
            return lambda x: c + A * _m.sin(2 * _m.pi * f * x + ph)
        if self.ley == "Polinómica":
            filas = np.asarray(self.puntos, float).reshape(-1, 2) if self.puntos else np.zeros((0, 2))
            coef = [float(v) for v in filas[:, 1]] if len(filas) else [float(self.constante)]
            return lambda x: float(np.polynomial.polynomial.polyval(x, coef))
        p = self._pts()
        x0, x1 = float(p[0, 0]), float(p[-1, 0])
        xs = np.linspace(x0, x1, n)
        ys = self.evaluar(xs)
        per = float(self.periodo)

        def f(x):
            if per > 0:
                x = x0 + (x - x0) % per
            if x < x0 - 1e-12 or x > x1 + 1e-12:
                return float("nan")
            return float(np.interp(x, xs, ys))
        return f
