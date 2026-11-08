# -*- coding: utf-8 -*-
"""
engine/motion_engine.py

Perfil de giro de la rueda motriz (piñón de rodillos) para el modo de simulación
AUTOMÁTICO de V2. Sin dependencias de Qt: modelo de datos + leyes de movimiento por
tramos (derivado de wheel_motion_studio_active.py) + una línea de tiempo precalculada.

ACELERACIÓN POR HARDWARE
  - Las leyes (rampas, seno, spline...) se evalúan con NumPy: son vectoriales y baratas.
  - La parte pesada -derivar/integrar para obtener posición-velocidad-aceleración sobre
    una malla densa y la interpolación de miles de fotogramas (p. ej. al grabar video)-
    usa `backend_selector.xp_para(n)`, o sea CuPy en modo GPU / Híbrido (si n es
    grande) y NumPy en el resto. El resultado siempre vuelve a NumPy (`a_numpy`).
  - En reproducción interactiva la consulta es 1 escalar por fotograma: `np.interp`
    sobre la tabla ya precalculada (no hay nada que acelerar ahí).

Nombres de leyes = textos del combo `comboBox_tipodefuncion` de
Perfildevelocidad_simulador_Window, para mapear directo UI <-> modelo <-> JSON.
"""
from __future__ import annotations

import copy
import copy
import copy
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np

from engine import backend_selector

LEYES = [
    "Rampa lineal", "Rampa cúbica", "Cicloidal", "Armónica", "Sinusoidal",
    "Sinusoidal modificada", "Polinómica", "Lista de puntos", "Spline",
    "Trapezoidal modificada",
]
PROPIEDADES = ["Posición", "Velocidad", "Aceleración"]
UNIDADES = {"Posición": "°", "Velocidad": "°/s", "Aceleración": "°/s²"}
PRESET_DEFECTO = "Arranque y parada suaves"
MAX_COEFICIENTES = 6  # polinomio hasta grado 5


# ----------------------------------------------------------------------
# Modelo de datos
# ----------------------------------------------------------------------
@dataclass
class Ley:
    nombre: str
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"nombre": self.nombre, "params": self.params}

    @staticmethod
    def from_dict(d: dict) -> "Ley":
        nombre = d.get("nombre", "Rampa lineal")
        return Ley(nombre if nombre in LEYES else "Rampa lineal", dict(d.get("params", {})))


@dataclass
class Tramo:
    inicio: float
    fin: float
    y_ini: float = 0.0
    y_fin: float = 0.0
    leyes: list[Ley] = field(default_factory=list)

    def __post_init__(self):
        if self.fin <= self.inicio:
            raise ValueError("El final del tramo debe ser posterior al inicio.")

    @property
    def duracion(self) -> float:
        return self.fin - self.inicio

    def to_dict(self) -> dict:
        return {"inicio": self.inicio, "fin": self.fin, "y_ini": self.y_ini,
                "y_fin": self.y_fin, "leyes": [l.to_dict() for l in self.leyes]}

    @staticmethod
    def from_dict(d: dict) -> "Tramo":
        return Tramo(float(d["inicio"]), float(d["fin"]), float(d.get("y_ini", 0.0)),
                     float(d.get("y_fin", 0.0)), [Ley.from_dict(x) for x in d.get("leyes", [])])


@dataclass
class PerfilMovimiento:
    propiedad: str = "Velocidad"
    tramos: list[Tramo] = field(default_factory=list)

    def validar(self) -> None:
        if self.propiedad not in PROPIEDADES:
            raise ValueError(f"Propiedad desconocida: {self.propiedad}")
        if not self.tramos:
            raise ValueError("El perfil necesita al menos un tramo.")
        orden = sorted(self.tramos, key=lambda t: t.inicio)
        for t in orden:
            if not all(math.isfinite(v) for v in (t.inicio, t.fin, t.y_ini, t.y_fin)):
                raise ValueError("Tiempos y valores deben ser finitos.")
        for a, b in zip(orden, orden[1:]):
            if b.inicio < a.fin - 1e-9:
                raise ValueError("Los tramos no pueden solaparse.")

    @property
    def t_ini(self) -> float:
        return min((t.inicio for t in self.tramos), default=0.0)

    @property
    def t_fin(self) -> float:
        return max((t.fin for t in self.tramos), default=1.0)

    def to_dict(self) -> dict:
        return {"propiedad": self.propiedad, "tramos": [t.to_dict() for t in self.tramos]}

    @staticmethod
    def from_dict(d: dict) -> "PerfilMovimiento":
        p = PerfilMovimiento(d.get("propiedad", "Velocidad"),
                             sorted((Tramo.from_dict(t) for t in d.get("tramos", [])),
                                    key=lambda t: t.inicio))
        p.validar()
        return p


# ----------------------------------------------------------------------
# Leyes de movimiento (cada una aislada: si una falla, aporta 0)
# ----------------------------------------------------------------------
class MotorLey(ABC):
    nombre: str

    @abstractmethod
    def evaluar(self, t: np.ndarray, tramo: Tramo, ley: Ley, idx: int) -> np.ndarray:
        """Aporte aditivo de esta ley, relativo a tramo.y_ini."""

    def params_defecto(self, tramo: Optional[Tramo] = None) -> dict:
        return {}


class _Rampa(MotorLey):
    @abstractmethod
    def forma(self, u: np.ndarray) -> np.ndarray: ...

    def evaluar(self, t, tramo, ley, idx):
        u = np.clip((t - tramo.inicio) / tramo.duracion, 0.0, 1.0)
        pend = ley.params.get("pendiente")
        if pend is None:
            pend = (tramo.y_fin - tramo.y_ini) / tramo.duracion if idx == 0 else 0.0
        return float(pend) * tramo.duracion * self.forma(u)

    def params_defecto(self, tramo=None):
        return {"pendiente": None}


class RampaLineal(_Rampa):
    nombre = "Rampa lineal"
    def forma(self, u): return u


class RampaCubica(_Rampa):
    nombre = "Rampa cúbica"
    def forma(self, u): return 3.0 * u**2 - 2.0 * u**3


class Cicloidal(_Rampa):
    nombre = "Cicloidal"
    def forma(self, u): return u - np.sin(2.0 * np.pi * u) / (2.0 * np.pi)


class Armonica(_Rampa):
    nombre = "Armónica"
    def forma(self, u): return 0.5 * (1.0 - np.cos(np.pi * u))


class SinusoidalModificada(_Rampa):
    nombre = "Sinusoidal modificada"

    def forma(self, u):
        x = np.clip(u, 0.0, 1.0)
        d = 4.0 + np.pi
        r = np.empty_like(x, dtype=float)
        a, c = x <= 1 / 8, x > 7 / 8
        b = ~(a | c)
        r[a] = (np.pi / d) * x[a] - np.sin(4 * np.pi * x[a]) / (4 * d)
        r[b] = 2 / d + (np.pi / d) * x[b] - 9 * np.sin(np.pi / 3 + (4 * np.pi / 3) * x[b]) / (4 * d)
        r[c] = 4 / d + (np.pi / d) * x[c] - np.sin(4 * np.pi * x[c]) / (4 * d)
        return r


class TrapezoidalModificada(_Rampa):
    nombre = "Trapezoidal modificada"

    @staticmethod
    def _mitad(x):
        out = np.empty_like(x, dtype=float)
        a, c = x <= 1 / 8, x > 3 / 8
        b = ~(a | c)
        den = 2.0 + np.pi
        out[a] = (2 / den) * x[a] - np.sin(4 * np.pi * x[a]) / (2 * np.pi * den)
        out[b] = ((np.pi**2 - 8) / (16 * np.pi * den) + ((2 - np.pi) / den) * x[b]
                  + (4 * np.pi / den) * x[b] ** 2)
        out[c] = (-np.pi / (4 + 2 * np.pi) + ((2 + 2 * np.pi) / den) * x[c]
                  - np.sin(4 * np.pi * x[c] - np.pi) / (2 * np.pi * den))
        return out

    def forma(self, u):
        x = np.clip(u, 0.0, 1.0)
        izq = x <= 0.5
        r = np.empty_like(x, dtype=float)
        r[izq] = self._mitad(x[izq])
        r[~izq] = 1.0 - self._mitad(1.0 - x[~izq])
        return r


class Sinusoidal(MotorLey):
    nombre = "Sinusoidal"

    def params_defecto(self, tramo=None):
        return {"amplitud": 10.0, "frecuencia": 1.0, "fase": 0.0}

    def evaluar(self, t, tramo, ley, idx):
        p = ley.params
        return (float(p.get("amplitud", 10.0))
                * np.sin(2 * np.pi * float(p.get("frecuencia", 1.0)) * (t - tramo.inicio)
                         + math.radians(float(p.get("fase", 0.0)))))


class Polinomica(MotorLey):
    nombre = "Polinómica"

    def params_defecto(self, tramo=None):
        return {"coeficientes": [0.0, 0.0]}

    def evaluar(self, t, tramo, ley, idx):
        coef = [float(c) for c in ley.params.get("coeficientes", [0.0])][:MAX_COEFICIENTES]
        return np.polynomial.polynomial.polyval(t - tramo.inicio, coef) if coef else np.zeros_like(t)


class ListaPuntos(MotorLey):
    """Polinomio de grado `grado` ajustado por mínimos cuadrados a una lista de puntos
    (x = tiempo absoluto, y = valor absoluto de la propiedad)."""
    nombre = "Lista de puntos"

    def params_defecto(self, tramo=None):
        pts = [[tramo.inicio, tramo.y_ini], [tramo.fin, tramo.y_fin]] if tramo else []
        return {"grado": 1, "puntos": pts}

    def evaluar(self, t, tramo, ley, idx):
        pts = np.asarray(ley.params.get("puntos", []), dtype=float).reshape(-1, 2)
        grado = int(np.clip(int(ley.params.get("grado", 1)), 0, MAX_COEFICIENTES - 1))
        if len(pts) < grado + 1:
            raise ValueError(f"grado {grado} requiere al menos {grado + 1} puntos")
        c = np.polynomial.polynomial.polyfit(pts[:, 0] - tramo.inicio, pts[:, 1] - tramo.y_ini, grado)
        return np.polynomial.polynomial.polyval(t - tramo.inicio, c)


class Spline(MotorLey):
    """Hermite cúbico por tramos (pendientes interiores por diferencias centrales)."""
    nombre = "Spline"

    def params_defecto(self, tramo=None):
        pts = [[tramo.inicio, tramo.y_ini], [tramo.fin, tramo.y_fin]] if tramo else []
        return {"pendiente_ini": 0.0, "pendiente_fin": 0.0, "puntos": pts}

    def evaluar(self, t, tramo, ley, idx):
        raw = np.asarray(ley.params.get("puntos", []), dtype=float).reshape(-1, 2)
        if len(raw) < 2:
            u = np.clip((t - tramo.inicio) / tramo.duracion, 0.0, 1.0)
            return (tramo.y_fin - tramo.y_ini) * (3 * u**2 - 2 * u**3)
        xs, idxu = np.unique(raw[:, 0], return_index=True)
        ys = raw[idxu, 1]
        if len(xs) < 2:
            return np.zeros_like(t)
        m = np.empty_like(ys)
        m[1:-1] = (ys[2:] - ys[:-2]) / (xs[2:] - xs[:-2])
        m[0] = float(ley.params.get("pendiente_ini", (ys[1] - ys[0]) / (xs[1] - xs[0])))
        m[-1] = float(ley.params.get("pendiente_fin", (ys[-1] - ys[-2]) / (xs[-1] - xs[-2])))
        tc = np.clip(t, xs[0], xs[-1])
        i = np.clip(np.searchsorted(xs, tc, side="right") - 1, 0, len(xs) - 2)
        h = xs[i + 1] - xs[i]
        u = (tc - xs[i]) / h
        val = ((2 * u**3 - 3 * u**2 + 1) * ys[i] + (u**3 - 2 * u**2 + u) * h * m[i]
               + (-2 * u**3 + 3 * u**2) * ys[i + 1] + (u**3 - u**2) * h * m[i + 1])
        return val - tramo.y_ini


class RegistroLeyes:
    """Registro + frontera de fallos: una ley que lanza excepción aporta 0 y queda
    anotada en `errores`, sin tumbar las demás."""

    def __init__(self):
        motores = (RampaLineal(), RampaCubica(), Cicloidal(), Armonica(), Sinusoidal(),
                   SinusoidalModificada(), Polinomica(), ListaPuntos(), Spline(),
                   TrapezoidalModificada())
        self._m = {m.nombre: m for m in motores}
        self.errores: list[str] = []

    def es_rampa(self, nombre: str) -> bool:
        return isinstance(self._m.get(nombre), _Rampa)

    def nueva_ley(self, nombre: str, tramo: Optional[Tramo] = None, aditiva: bool = False) -> Ley:
        params = self._m[nombre].params_defecto(tramo)
        if aditiva and "pendiente" in params:
            params["pendiente"] = 0.0
        return Ley(nombre, params)

    def evaluar(self, t, tramo, ley, idx):
        try:
            v = np.asarray(self._m[ley.nombre].evaluar(t, tramo, ley, idx), dtype=float)
            if v.shape != t.shape:
                v = np.broadcast_to(v, t.shape).astype(float, copy=True)
            if not np.all(np.isfinite(v)):
                raise FloatingPointError("NaN o infinito")
            return v
        except Exception as exc:
            msg = f"{ley.nombre}: {type(exc).__name__}: {exc}"
            if msg not in self.errores:
                self.errores.append(msg)
            return np.zeros_like(t, dtype=float)


# ----------------------------------------------------------------------
# Evaluación + línea de tiempo precalculada
# ----------------------------------------------------------------------
def _valor_tramo(reg: RegistroLeyes, t: np.ndarray, tramo: Tramo) -> np.ndarray:
    if not tramo.leyes:
        u = np.clip((t - tramo.inicio) / tramo.duracion, 0.0, 1.0)
        return tramo.y_ini + (tramo.y_fin - tramo.y_ini) * u
    for i, ley in enumerate(tramo.leyes):
        if ley.nombre == "Spline":  # ley independiente
            return tramo.y_ini + reg.evaluar(t, tramo, ley, i)
    res = np.full_like(t, tramo.y_ini, dtype=float)
    for i, ley in enumerate(tramo.leyes):
        res += reg.evaluar(t, tramo, ley, i)
    return res


def evaluar_entrada(perfil: PerfilMovimiento, reg: RegistroLeyes, tiempos: np.ndarray) -> np.ndarray:
    """Valor de la propiedad de entrada. Antes del primer tramo vale y_ini; en huecos y
    después del último se mantiene el último valor."""
    tiempos = np.asarray(tiempos, dtype=float)
    reg.errores.clear()
    tr = sorted(perfil.tramos, key=lambda x: x.inicio)
    res = np.empty_like(tiempos)
    res[:] = tr[0].y_ini
    for i, tramo in enumerate(tr):
        mask = (tiempos >= tramo.inicio) & (tiempos <= tramo.fin)
        if mask.any():
            res[mask] = _valor_tramo(reg, tiempos[mask], tramo)
        fin_val = _valor_tramo(reg, np.array([tramo.fin]), tramo)[0]
        sig_ini = tr[i + 1].inicio if i + 1 < len(tr) else np.inf
        hueco = (tiempos > tramo.fin) & (tiempos < sig_ini)
        if hueco.any():
            res[hueco] = fin_val
    return res


class LineaTiempo:
    """Tabla t -> {posición, velocidad, aceleración} lista para reproducir/grabar."""

    def __init__(self, tiempos, entrada, pos, vel, acc, errores):
        self.t, self.entrada, self.pos, self.vel, self.acc = tiempos, entrada, pos, vel, acc
        self.errores = errores

    @property
    def t_ini(self) -> float: return float(self.t[0])
    @property
    def t_fin(self) -> float: return float(self.t[-1])
    @property
    def duracion(self) -> float: return self.t_fin - self.t_ini

    @classmethod
    def construir(cls, perfil: PerfilMovimiento, reg: Optional[RegistroLeyes] = None,
                  n: Optional[int] = None) -> "LineaTiempo":
        perfil.validar()
        reg = reg or RegistroLeyes()
        dur = perfil.t_fin - perfil.t_ini
        n = int(n or min(max(2000, dur * 2000), 400_000))
        tiempos = np.linspace(perfil.t_ini, perfil.t_fin, n)
        entrada = evaluar_entrada(perfil, reg, tiempos)

        xp = backend_selector.xp_para(n)           # CuPy si GPU/Híbrido y n grande
        dt = float(tiempos[1] - tiempos[0])
        e = xp.asarray(entrada)

        def integrar(v):
            return xp.concatenate((xp.zeros(1), xp.cumsum((v[:-1] + v[1:]) * 0.5 * dt)))

        def derivar(v):
            return xp.gradient(v, dt)

        if perfil.propiedad == "Posición":
            pos = e; vel = derivar(pos); acc = derivar(vel)
        elif perfil.propiedad == "Velocidad":
            vel = e; pos = integrar(vel); acc = derivar(vel)
        else:
            acc = e; vel = integrar(acc); pos = integrar(vel)
        a = backend_selector.a_numpy
        return cls(tiempos, entrada, a(pos), a(vel), a(acc), list(reg.errores))

    # --- encaje de la posición en un rango permitido (p. ej. largo de la cremallera) ---
    def rango_posicion(self) -> tuple[float, float]:
        return float(np.min(self.pos)), float(np.max(self.pos))

    def ajustada(self, lo: float, hi: float, escalar: bool = True):
        """Encaja la posición en [lo, hi]. Devuelve (LineaTiempo, factor, desplazamiento, recortada).
        1) escalar=True y el recorrido total > hi-lo -> se escala (pos, vel y acc son lineales: exacto).
        2) Si aún sobresale por un extremo, se desplaza lo mínimo. 3) escalar=False y no cabe -> se recorta."""
        pmin, pmax = self.rango_posicion()
        ext, ancho = pmax - pmin, hi - lo
        f = 1.0
        if escalar and ext > ancho + 1e-9 and ext > 1e-12:
            f = 0.999 * ancho / ext
        smin, smax = f * pmin, f * pmax
        off = (lo - smin) if smin < lo - 1e-9 else ((hi - smax) if smax > hi + 1e-9 else 0.0)
        if f == 1.0 and off == 0.0:
            return self, 1.0, 0.0, False
        if not escalar and ext > ancho + 1e-9:
            pos = np.clip(self.pos, lo, hi)
            vel = np.gradient(pos, self.t)
            acc = np.gradient(vel, self.t)
            return LineaTiempo(self.t, self.entrada, pos, vel, acc, list(self.errores)), 1.0, 0.0, True
        return (LineaTiempo(self.t, f * self.entrada, f * self.pos + off, f * self.vel, f * self.acc,
                            list(self.errores)), f, off, False)

    # --- encaje de la posición en un rango permitido (p. ej. largo de la cremallera) ---
    def rango_posicion(self) -> tuple[float, float]:
        return float(np.min(self.pos)), float(np.max(self.pos))

    def ajustada(self, lo: float, hi: float, escalar: bool = True):
        """Encaja la posición en [lo, hi]. Devuelve (LineaTiempo, factor, desplazamiento, recortada).
        1) escalar=True y el recorrido total > hi-lo -> se escala (pos, vel y acc son lineales: exacto).
        2) Si aún sobresale por un extremo, se desplaza lo mínimo. 3) escalar=False y no cabe -> se recorta."""
        pmin, pmax = self.rango_posicion()
        ext, ancho = pmax - pmin, hi - lo
        f = 1.0
        if escalar and ext > ancho + 1e-9 and ext > 1e-12:
            f = 0.999 * ancho / ext
        smin, smax = f * pmin, f * pmax
        off = (lo - smin) if smin < lo - 1e-9 else ((hi - smax) if smax > hi + 1e-9 else 0.0)
        if f == 1.0 and off == 0.0:
            return self, 1.0, 0.0, False
        if not escalar and ext > ancho + 1e-9:
            pos = np.clip(self.pos, lo, hi)
            vel = np.gradient(pos, self.t)
            acc = np.gradient(vel, self.t)
            return LineaTiempo(self.t, self.entrada, pos, vel, acc, list(self.errores)), 1.0, 0.0, True
        return (LineaTiempo(self.t, f * self.entrada, f * self.pos + off, f * self.vel, f * self.acc,
                            list(self.errores)), f, off, False)

    # --- encaje de la posición en un rango permitido (p. ej. largo de la cremallera) ---
    def rango_posicion(self) -> tuple[float, float]:
        return float(np.min(self.pos)), float(np.max(self.pos))

    def ajustada(self, lo: float, hi: float, escalar: bool = True):
        """Encaja la posición en [lo, hi]. Devuelve (LineaTiempo, factor, desplazamiento, recortada).
        1) escalar=True y el recorrido total > hi-lo -> se escala (pos, vel y acc son lineales: exacto).
        2) Si aún sobresale por un extremo, se desplaza lo mínimo. 3) escalar=False y no cabe -> se recorta."""
        pmin, pmax = self.rango_posicion()
        ext, ancho = pmax - pmin, hi - lo
        f = 1.0
        if escalar and ext > ancho + 1e-9 and ext > 1e-12:
            f = 0.999 * ancho / ext
        smin, smax = f * pmin, f * pmax
        off = (lo - smin) if smin < lo - 1e-9 else ((hi - smax) if smax > hi + 1e-9 else 0.0)
        if f == 1.0 and off == 0.0:
            return self, 1.0, 0.0, False
        if not escalar and ext > ancho + 1e-9:
            pos = np.clip(self.pos, lo, hi)
            vel = np.gradient(pos, self.t)
            acc = np.gradient(vel, self.t)
            return LineaTiempo(self.t, self.entrada, pos, vel, acc, list(self.errores)), 1.0, 0.0, True
        return (LineaTiempo(self.t, f * self.entrada, f * self.pos + off, f * self.vel, f * self.acc,
                            list(self.errores)), f, off, False)

    def posicion_en(self, t: float) -> float:
        """Escalar por fotograma (reproducción interactiva)."""
        return float(np.interp(t, self.t, self.pos))

    def posiciones_en(self, tiempos: np.ndarray) -> np.ndarray:
        """Vectorizado (p. ej. todos los fotogramas de una grabación) -- usa xp."""
        xp = backend_selector.xp_para(len(tiempos))
        r = xp.interp(xp.asarray(tiempos), xp.asarray(self.t), xp.asarray(self.pos))
        return backend_selector.a_numpy(r)


# ----------------------------------------------------------------------
# Presets (los 8 del combo comboBox_preset)
# ----------------------------------------------------------------------
class FabricaPresets:
    NOMBRES = ["Arranque y parada suaves", "Oscilador 100Hz", "Backlash", "Giro de 90°",
               "Giro de 180°", "Indexer", "Lavadora", "Vibrador"]

    @staticmethod
    def _t(i, f, y0, y1, ley, **p) -> Tramo:
        return Tramo(i, f, y0, y1, [Ley(ley, dict(p))])

    @classmethod
    def crear(cls, nombre: str) -> PerfilMovimiento:
        T = cls._t
        if nombre == "Oscilador 100Hz":
            return PerfilMovimiento("Posición", [T(0, 0.2, 0, 0, "Sinusoidal", amplitud=2.0, frecuencia=100.0, fase=0.0)])
        if nombre == "Backlash":
            return PerfilMovimiento("Posición", [
                T(0, 1, 0, 5, "Rampa cúbica", pendiente=None), T(1, 2, 5, 5, "Rampa lineal", pendiente=0.0),
                T(2, 3, 5, -5, "Rampa cúbica", pendiente=None), T(3, 4, -5, -5, "Rampa lineal", pendiente=0.0),
                T(4, 5, -5, 0, "Rampa cúbica", pendiente=None)])
        if nombre == "Giro de 90°":
            return PerfilMovimiento("Posición", [T(0, 2, 0, 90, "Cicloidal", pendiente=None)])
        if nombre == "Giro de 180°":
            return PerfilMovimiento("Posición", [T(0, 3, 0, 180, "Cicloidal", pendiente=None)])
        if nombre == "Indexer":
            tr, y = [], 0.0
            for k in range(4):
                tr.append(T(k * 1.5, k * 1.5 + 0.5, y, y + 90, "Cicloidal", pendiente=None))
                tr.append(T(k * 1.5 + 0.5, k * 1.5 + 1.5, y + 90, y + 90, "Rampa lineal", pendiente=0.0))
                y += 90
            return PerfilMovimiento("Posición", tr)
        if nombre == "Lavadora":
            return PerfilMovimiento("Posición", [T(0, 8, 0, 0, "Sinusoidal", amplitud=270.0, frecuencia=0.25, fase=0.0)])
        if nombre == "Vibrador":
            return PerfilMovimiento("Posición", [T(0, 2, 0, 0, "Sinusoidal", amplitud=3.0, frecuencia=15.0, fase=0.0)])
        # Arranque y parada suaves (por defecto): 0 -> 80 °/s -> 0
        return PerfilMovimiento("Velocidad", [
            T(0, 5, 0, 80, "Rampa cúbica", pendiente=None),
            T(5, 15, 80, 80, "Rampa lineal", pendiente=0.0),
            T(15, 20, 80, 0, "Rampa cúbica", pendiente=None)])


def escalar_perfil(perfil: PerfilMovimiento, f: float) -> PerfilMovimiento:
    """Copia del perfil con todas sus magnitudes multiplicadas por f (las leyes son lineales en y)."""
    p = copy.deepcopy(perfil)
    for t in p.tramos:
        t.y_ini *= f
        t.y_fin *= f
        for ley in t.leyes:
            q = ley.params
            for k in ("amplitud", "pendiente", "pendiente_ini", "pendiente_fin"):
                if q.get(k) is not None:
                    q[k] = float(q[k]) * f
            if "coeficientes" in q:
                q["coeficientes"] = [float(c) * f for c in q["coeficientes"]]
            if "puntos" in q:
                q["puntos"] = [[x, y * f] for x, y in q["puntos"]]
    return p
