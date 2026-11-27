# -*- coding: utf-8 -*-
"""
utils/formato_numerico.py — ÚNICO punto de formateo de números para mostrar en pantalla y en reportes legibles.

Solo afecta a la PRESENTACIÓN: los arrays de NumPy, los algoritmos y las exportaciones de datos (CSV/TXT/XLSX/DXF)
conservan la precisión completa. Preferencia: Ajustes → Cálculo y precisión → «Decimales».

  4/6/8/12 decimales -> notación fija con esa cantidad de decimales; si un valor no nulo se mostraría como cero
                        (|v| < medio decimal) o es enorme (≥ 1e9) se pasa a notación científica para no ocultarlo.
  Automático         -> 8 cifras significativas con notación científica fuera de [1e-4, 1e9).
"""
from __future__ import annotations

import math
import re

_FIJOS = (4, 6, 8, 12)
_estado = {"decimales": 6, "auto": False}


def configurar(texto: str) -> None:
    """Acepta el texto del combo de Ajustes («6 decimales», «Automático»)."""
    if "auto" in (texto or "").lower():
        _estado.update(auto=True)
        return
    m = re.match(r"\s*(\d+)", texto or "")
    n = int(m.group(1)) if m else 6
    _estado.update(auto=False, decimales=n if n in _FIJOS else 6)


def decimales() -> int | None:
    """Decimales fijos vigentes, o None en modo Automático."""
    return None if _estado["auto"] else _estado["decimales"]


def clave() -> tuple:
    """Valor hashable del formato vigente (para invalidar cachés de texto)."""
    return (_estado["auto"], _estado["decimales"])


def fmt(valor, unidades: str = "") -> str:
    """Texto de `valor` con el formato vigente y, si se da, la unidad física detrás («mm», «°», «mm/rev»…)."""
    try:
        v = float(valor)
    except (TypeError, ValueError):
        return str(valor)
    if math.isnan(v):
        t = "nan"
    elif math.isinf(v):
        t = "inf" if v > 0 else "-inf"
    elif _estado["auto"]:
        t = f"{v:.8g}"
    else:
        d = _estado["decimales"]
        if v != 0.0 and (abs(v) < 0.5 * 10.0 ** -d or abs(v) >= 1e9):
            t = f"{v:.{min(d, 6)}e}"
        else:
            t = f"{v:.{d}f}"
        if t.startswith("-") and float(t) == 0.0:       # «-0.000000» no aporta nada
            t = t[1:]
    return f"{t} {unidades}".rstrip() if unidades else t


def fmt_signo(valor, unidades: str = "") -> str:
    """Igual que `fmt` pero con «+» explícito en los positivos (razones de transmisión, desplazamientos)."""
    t = fmt(valor, unidades)
    return t if t.startswith(("-", "+", "n", "i")) else "+" + t
