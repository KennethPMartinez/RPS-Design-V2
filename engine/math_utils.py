# -*- coding: utf-8 -*-
"""
engine/math_utils.py

Utilidades geométricas puras compartidas por los 3 motores de perfil
trocoidal (Cremallera, Epitrocoidal, Hipotrocoidal). No dependen de Qt ni de
ninguna capa superior: reciben y devuelven arrays/escalares.

AGNÓSTICAS DE BACKEND: cada función recibe un parámetro `xp` (el módulo de
arreglos a usar -- `numpy` o `cupy`, ver engine/backend_selector.py),
default `numpy` para no romper ningún llamador existente. Quien orquesta
la elección real es `BaseEngine` (decide con `backend_selector.xp_para()`
según el tamaño del trabajo, no según el modo de Hardware a secas -- ver
docstring de `xp_para`), no este módulo: `math_utils` solo ejecuta con el
`xp` que le pasan.

Ver progress.md §4 para el origen de cada fórmula (derivadas en Wolfram
Mathematica a partir de los PDF del proyecto).
"""
from __future__ import annotations
import numpy as np


def normal_unitario(dx, dy, invertido: bool = False, xp=np):
    """Vector unitario normal a la tangente (dx, dy).

    invertido=False -> normal = (-dy, dx)   [Trocoidal, Epitrocoidal]
    invertido=True  -> normal = ( dy, -dx)  [Hipotrocoidal — offset hacia el
                        lado opuesto por tratarse de un perfil interior/anular,
                        ver progress.md §4.3]
    """
    mag = xp.hypot(dx, dy)
    mag = xp.where(mag == 0, 1e-12, mag)
    if invertido:
        return dy / mag, -dx / mag
    return -dy / mag, dx / mag


def offset_desde_tangente(x, y, dx, dy, radio: float, invertido: bool = False, xp=np):
    """Desplaza el punto (x, y) una distancia `radio` en la dirección normal
    a la tangente (dx, dy). Equivale a 'curvaoffset[θ] := curva[θ] -
    (rr/2)*Normalunitario[θ]' en los PDF (rr/2 = radio del rodillo)."""
    nx, ny = normal_unitario(dx, dy, invertido, xp=xp)
    return x - radio * nx, y - radio * ny


def rotar(x, y, beta, xp=np):
    """Matriz de rotación 2D estándar (equivale a RotationMatrix[β].curva en
    los PDF de Epitrocoidal/Hipotrocoidal)."""
    cos_b, sin_b = xp.cos(beta), xp.sin(beta)
    return cos_b * x - sin_b * y, sin_b * x + cos_b * y


def trasladar(x, y, dx, dy=0.0):
    """Traslación simple (equivale a 'CurvaTrasladada[θ_, i_] := curvaoffset[θ]
    + {i*paso, 0}' en el PDF de Cremallera)."""
    return x + dx, y + dy


def derivada_numerica(funcion, theta, h: float = 1e-5, orden: int = 1):
    """Derivada central de una función vectorial `funcion(theta) -> (x, y)`
    (p. ej. BaseEngine.curva_offset), evaluada en escalares o arrays de
    theta.

    Se usa para curvatura/radio de curvatura (ver progress.md §11): derivar
    a mano la 2da derivada de la curva offset de los 3 perfiles implicaría
    propagar la derivada de la normal unitaria (que a su vez depende de la
    tangente y de su magnitud) a través de la regla del cociente — viable
    pero engorroso y frágil de mantener por perfil. Se opta por
    diferenciación numérica: el error es despreciable tanto para graficar
    como para estimar el radio de curvatura mínimo (diagnóstico de
    subcorte que pide ModusOperandi.docx en la exportación a PDF).
    """
    if orden == 1:
        xp, yp = funcion(theta + h)
        xm, ym = funcion(theta - h)
        return (xp - xm) / (2.0 * h), (yp - ym) / (2.0 * h)
    if orden == 2:
        x0, y0 = funcion(theta)
        xp, yp = funcion(theta + h)
        xm, ym = funcion(theta - h)
        return (xp - 2.0 * x0 + xm) / h ** 2, (yp - 2.0 * y0 + ym) / h ** 2
    raise ValueError(f"orden debe ser 1 o 2, recibido {orden!r}")


def concatenar_segmentos(segmentos, xp=np):
    """Concatena una lista de segmentos [(x0,y0), (x1,y1), ...] insertando
    un separador NaN entre cada uno, para que Matplotlib (y cualquier
    consumidor que respete NaN como "levantar el lápiz") no dibuje una
    línea espuria uniendo el final de un segmento con el inicio del
    siguiente. Sin esto, ensamblar el patrón completo de un perfil
    epi/hipotrocoidal (o el lineal de la cremallera) producía un "glitch"
    que unía las crestas de dientes consecutivos con una cuerda recta en
    vez de dejarlos como curvas separadas (ver progress.md, Paso 1.5)."""
    xs, ys = [], []
    separador = xp.array([xp.nan])
    for i, (x, y) in enumerate(segmentos):
        if i > 0:
            xs.append(separador)
            ys.append(separador)
        xs.append(xp.asarray(x))
        ys.append(xp.asarray(y))
    return xp.concatenate(xs), xp.concatenate(ys)


def resolver_raiz_biseccion(f_diferencia, theta_min: float, theta_max: float,
                             tolerancia: float = 1e-9, max_iter: int = 200,
                             expandir_hasta: float = np.pi):
    """Busca por bisección la raíz de f_diferencia(theta) = 0 en
    [theta_min, theta_max], asumiendo un único cambio de signo en ese
    intervalo (válido para los criterios de convergencia de theta_lim de los
    3 perfiles, todos monótonos cerca del origen). Si no hay cambio de signo,
    expande `theta_max` hasta `expandir_hasta` antes de rendirse.

    Se implementa a mano (sin scipy) para no añadir una dependencia extra al
    proyecto: el resto del motor ya usa NumPy puro (ver ModusOperandi.docx,
    tabla de Hardware CPU/GPU/Híbrido).
    """
    lo, hi = theta_min, theta_max
    f_lo, f_hi = f_diferencia(lo), f_diferencia(hi)
    while f_lo * f_hi > 0 and hi < expandir_hasta:
        hi = min(hi * 1.5, expandir_hasta)
        f_hi = f_diferencia(hi)
    if f_lo * f_hi > 0:
        raise ValueError(
            "No se encontró cambio de signo para resolver theta_lim en "
            f"[{theta_min}, {expandir_hasta}]. Revisar parámetros de entrada."
        )
    for _ in range(max_iter):
        mid = (lo + hi) / 2.0
        f_mid = f_diferencia(mid)
        if abs(f_mid) < tolerancia:
            return mid
        if f_lo * f_mid < 0:
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2.0
