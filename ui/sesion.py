# -*- coding: utf-8 -*-
"""
ui/sesion.py — archivos de sesión y autoguardado (un JSON por sistema, mismo formato que el proyecto).

  sesion/<SISTEMA>.json        último estado al cerrar la ventana (lo lee «Restaurar sesión»)
  autoguardado/<SISTEMA>.json  copia de recuperación; se borra al cerrar con normalidad, así que si EXISTE al abrir
                               es que la sesión anterior terminó mal (corte, cierre forzado) con cambios sin guardar

La carpeta es la de datos del usuario (en pruebas: variable de entorno RPS_DATA_DIR).
"""
from __future__ import annotations

import os
from pathlib import Path

from PySide6 import QtCore


def carpeta() -> Path:
    base = os.environ.get("RPS_DATA_DIR")
    if not base:
        base = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.StandardLocation.GenericDataLocation)
    return Path(base) / "RPS Design"


def ruta_sesion(sistema: str) -> Path:
    return carpeta() / "sesion" / f"{sistema}.json"


def ruta_autoguardado(sistema: str) -> Path:
    return carpeta() / "autoguardado" / f"{sistema}.json"


def preparar(ruta: Path) -> Path:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    return ruta


def borrar(ruta: Path) -> None:
    try:
        ruta.unlink()
    except OSError:
        pass
