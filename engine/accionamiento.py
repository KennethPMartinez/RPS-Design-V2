# -*- coding: utf-8 -*-
"""
engine/accionamiento.py

Modelos de ACCIONAMIENTO (funciones 17–23). Sin Qt.

Capacidad ≠ entrega: la potencia nominal es una capacidad (régimen continuo), no la potencia entregada,
y el par de retención de un paso a paso solo vale en reposo. El par DISPONIBLE a una velocidad solo se
afirma si hay datos que lo determinen; si no, el resultado es `None` (= Indeterminado) con su causa.

  Stepper : curva par–velocidad tabulada (obligatoria fuera del reposo); en reposo, par de retención.
  AC      : velocidad síncrona n_s = 120·f/p (4 polos, 50 Hz -> 1500 rpm). Curva tabulada, o bien el modelo
            lineal de deslizamiento entre n_nom (P_nom/ω_nom) y n_s (par nulo) — hipótesis declarada,
            válida solo en esa zona; fuera de ella, Indeterminado.
  Custom  : curva tabulada, expresión validada T(n) [N·m, n en rpm], o valores (par constante = T_ret hasta
            n_nom y potencia constante = P_nom después — envolvente declarada como hipótesis).

Hipótesis comunes (se informan): acople directo motor–eje de entrada (sin reductor intermedio) y curva
simétrica en ambos sentidos de giro.
"""
from __future__ import annotations

import ast
import math
from dataclasses import asdict, dataclass, field

import numpy as np

STEPPER, AC, CUSTOM = "Stepper", "AC", "Custom"
MODO_IMPUESTO = "Movimiento impuesto"
MODO_CAPACIDAD = "Evaluación de capacidad del motor"

_FUNC = {"sqrt": math.sqrt, "exp": math.exp, "log": math.log, "sin": math.sin, "cos": math.cos,
         "tan": math.tan, "abs": abs, "min": min, "max": max, "tanh": math.tanh}
_CONST = {"pi": math.pi, "e": math.e}
_NODOS = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name, ast.Load, ast.Call,
          ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub, ast.UAdd, ast.Mod, ast.IfExp,
          ast.Compare, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.BoolOp, ast.And, ast.Or)


def tipo_desde_texto(texto: str) -> str:
    t = (texto or "").lower()
    return AC if t.startswith("ac") else CUSTOM if t.startswith("custom") else STEPPER


class ExpresionInvalida(ValueError):
    pass


def compilar_expresion(texto: str):
    """Expresión segura T(n): variables n [rpm] y w [rad/s]; funciones matemáticas básicas. Sin atributos,
    sin importaciones, sin nombres libres."""
    texto = (texto or "").strip()
    if not texto:
        raise ExpresionInvalida("expresión vacía")
    try:
        arbol = ast.parse(texto, mode="eval")
    except SyntaxError as e:
        raise ExpresionInvalida(f"sintaxis: {e.msg}") from e
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, _NODOS):
            raise ExpresionInvalida(f"elemento no permitido: {type(nodo).__name__}")
        if isinstance(nodo, ast.Name) and nodo.id not in ("n", "w", *_FUNC, *_CONST):
            raise ExpresionInvalida(f"nombre desconocido: {nodo.id}")
        if isinstance(nodo, ast.Call) and not (isinstance(nodo.func, ast.Name) and nodo.func.id in _FUNC):
            raise ExpresionInvalida("solo se permiten funciones matemáticas básicas")
    codigo = compile(arbol, "<T(n)>", "eval")

    def f(n_rpm: float) -> float:
        v = eval(codigo, {"__builtins__": {}}, {**_FUNC, **_CONST, "n": n_rpm, "w": n_rpm * math.pi / 30.0})
        v = float(v)
        if not math.isfinite(v):
            raise ExpresionInvalida("la expresión no es finita")
        return v
    for prueba in (0.0, 1.0, 100.0):          # validación numérica
        f(prueba)
    return f


@dataclass
class ModeloMotor:
    tipo: str = STEPPER
    modo: str = MODO_IMPUESTO
    potencia_nominal_w: float = 0.0
    velocidad_nominal_rpm: float = 0.0
    par_retencion_nm: float = 0.0
    frecuencia_hz: float = 50.0
    polos: int = 4
    curva: list = field(default_factory=list)         # [[rpm, N·m], ...]
    expresion: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "ModeloMotor":
        campos = ModeloMotor.__dataclass_fields__
        return ModeloMotor(**{k: v for k, v in (d or {}).items() if k in campos})

    # -- derivados ----------------------------------------------------------------------------
    @property
    def velocidad_sincrona_rpm(self):
        if self.tipo != AC or self.polos <= 0 or self.frecuencia_hz <= 0:
            return None
        return 120.0 * self.frecuencia_hz / self.polos

    def _curva_np(self):
        c = np.asarray(self.curva, float).reshape(-1, 2) if self.curva else np.zeros((0, 2))
        c = c[np.all(np.isfinite(c), axis=1)]
        return c[np.argsort(c[:, 0])] if len(c) else c

    def validar(self) -> list[str]:
        """Errores que impiden usar el modelo (vacío = válido aunque sea parcial)."""
        err = []
        c = self._curva_np()
        if len(c) and (np.any(np.diff(c[:, 0]) <= 0) or np.any(c[:, 0] < 0)):
            err.append("la curva par–velocidad debe tener velocidades ≥ 0 estrictamente crecientes")
        if len(c) and np.any(c[:, 1] < 0):
            err.append("la curva par–velocidad no admite pares negativos (se usa el módulo)")
        if self.tipo == AC:
            ns = self.velocidad_sincrona_rpm
            if ns is None:
                err.append("AC: frecuencia y número de polos deben ser positivos")
            elif self.velocidad_nominal_rpm >= ns > 0 and self.velocidad_nominal_rpm > 0 and len(c) < 2:
                err.append(f"AC: la velocidad nominal ({self.velocidad_nominal_rpm:g} rpm) debe ser menor que la "
                           f"síncrona ({ns:g} rpm); la diferencia es el deslizamiento")
        if self.tipo == CUSTOM:
            tiene = len(c) >= 2 or self.expresion.strip() or (self.par_retencion_nm > 0 and self.potencia_nominal_w > 0
                                                               and self.velocidad_nominal_rpm > 0)
            if not tiene:
                err.append("Custom: parametrización obligatoria (curva ≥ 2 puntos, expresión, o par, potencia y "
                           "velocidad nominales)")
            if self.expresion.strip():
                try:
                    compilar_expresion(self.expresion)
                except ExpresionInvalida as e:
                    err.append(f"Custom: expresión inválida ({e})")
        return err

    def descripcion_hipotesis(self) -> list[str]:
        h = ["acople directo motor–eje de entrada", "curva simétrica en ambos sentidos de giro"]
        c = self._curva_np()
        if self.tipo == AC and len(c) < 2:
            h.append("AC sin curva: modelo lineal de deslizamiento entre n_nom y n_s (solo en esa zona)")
        if self.tipo == CUSTOM and len(c) < 2 and not self.expresion.strip():
            h.append("Custom por valores: par constante hasta n_nom y potencia constante después")
        return h

    def par_disponible(self, n_rpm: float):
        """(T disponible N·m | None, causa si None). n_rpm con signo: se usa |n|."""
        n = abs(float(n_rpm))
        c = self._curva_np()
        if self.validar():
            return None, "; ".join(self.validar())
        if len(c) >= 2:
            if n < c[0, 0] - 1e-9 or n > c[-1, 0] + 1e-9:
                return None, f"velocidad {n:.4g} rpm fuera del rango de la curva [{c[0, 0]:g}, {c[-1, 0]:g}] rpm"
            return float(np.interp(n, c[:, 0], np.abs(c[:, 1]))), ""
        if self.tipo == STEPPER:
            if n <= 1e-9 and self.par_retencion_nm > 0:
                return self.par_retencion_nm, ""
            return None, ("Stepper sin curva par–velocidad: el par de retención solo vale en reposo"
                          if self.par_retencion_nm > 0 else "Stepper sin par de retención ni curva")
        if self.tipo == AC:
            ns, nn, P = self.velocidad_sincrona_rpm, self.velocidad_nominal_rpm, self.potencia_nominal_w
            if not (P > 0 and 0 < nn < ns):
                return None, "AC sin curva: faltan potencia y velocidad nominales (real < síncrona)"
            if nn <= n <= ns:
                t_nom = P / (nn * math.pi / 30.0)
                return t_nom * (ns - n) / (ns - nn), ""
            return None, (f"AC: {n:.4g} rpm fuera de la zona lineal [{nn:g}, {ns:g}] rpm "
                          "(se requiere curva característica o variador)")
        # CUSTOM
        if self.expresion.strip():
            try:
                return abs(compilar_expresion(self.expresion)(n)), ""
            except Exception as e:
                return None, f"expresión: {e}"
        T, P, nn = self.par_retencion_nm, self.potencia_nominal_w, self.velocidad_nominal_rpm
        if n <= nn:
            return T, ""
        return P / (n * math.pi / 30.0), ""

    def funcion_par(self):
        """Versión precompilada de `par_disponible` (valida una sola vez): para la integración temporal."""
        err = self.validar()
        if err:
            msg = "; ".join(err)
            return lambda n: (None, msg)
        c = self._curva_np()
        if len(c) >= 2:
            xs, ys = c[:, 0].copy(), np.abs(c[:, 1])
            lo, hi = float(xs[0]), float(xs[-1])

            def f(n):
                n = abs(n)
                if n < lo - 1e-9 or n > hi + 1e-9:
                    return None, f"velocidad {n:.4g} rpm fuera del rango de la curva [{lo:g}, {hi:g}] rpm"
                return float(np.interp(n, xs, ys)), ""
            return f
        if self.tipo == CUSTOM and self.expresion.strip():
            g = compilar_expresion(self.expresion)

            def f(n):
                try:
                    return abs(g(abs(n))), ""
                except Exception as e:
                    return None, f"expresión: {e}"
            return f
        return self.par_disponible

    def potencia_excedida(self, par_nm: float, n_rpm: float) -> bool:
        P = self.potencia_nominal_w
        return P > 0 and abs(par_nm * n_rpm * math.pi / 30.0) > P * (1 + 1e-9)


def evaluar_capacidad(motor: ModeloMotor, par_req, n_rpm):
    """Vectorizado sobre las muestras. Devuelve (estado[], T_disp[], causa[]):
    estado ∈ {"Viable", "No viable", "Indeterminado"}; T_req NaN => Indeterminado."""
    estados, disp, causas = [], [], []
    for T, n in zip(np.asarray(par_req, float), np.asarray(n_rpm, float)):
        Td, causa = motor.par_disponible(n)
        disp.append(np.nan if Td is None else Td)
        if not np.isfinite(T):
            estados.append("Indeterminado"); causas.append("par requerido indeterminado")
        elif Td is None:
            estados.append("Indeterminado"); causas.append(causa)
        elif abs(T) > Td * (1 + 1e-9):
            estados.append("No viable"); causas.append(f"par requerido {abs(T):.4g} N·m > disponible {Td:.4g} N·m")
        else:
            estados.append("Viable")
            causas.append("sobre la potencia nominal (régimen continuo)" if motor.potencia_excedida(T, n) else "")
    return estados, np.asarray(disp, float), causas


def intervalos(t, etiquetas, objetivo: set) -> list[tuple]:
    """[(t_ini, t_fin, etiqueta)] de los tramos contiguos de igual etiqueta incluida en `objetivo`."""
    out = []
    t = list(t)
    i = 0
    while i < len(t):
        j = i
        while j + 1 < len(t) and etiquetas[j + 1] == etiquetas[i]:
            j += 1
        if etiquetas[i] in objetivo:
            out.append((t[i], t[j], etiquetas[i]))
        i = j + 1
    return out
