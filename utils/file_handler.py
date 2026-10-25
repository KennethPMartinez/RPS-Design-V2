# -*- coding: utf-8 -*-
"""
utils/file_handler.py

Abrir / Guardar del proyecto V2 (JSON). Un archivo contiene todo lo necesario para
reproducir la sesión: parámetros del sistema, modo de simulación, perfil de giro
(si fue editado) y capas visibles. Sin dependencias de Qt.
"""
from __future__ import annotations

import json
from dataclasses import asdict, fields
from pathlib import Path
from typing import Optional

from config.data_structures import (AjustesVisibilidadSimulacion, ParametrosEpitrocoidal)
from engine.motion_engine import PerfilMovimiento

FORMATO = "RPS Design V2"
VERSION = 1


class ArchivoInvalido(ValueError):
    pass


def guardar_proyecto(ruta, parametros: ParametrosEpitrocoidal, sim: dict,
                     perfil_mov: Optional[PerfilMovimiento],
                     visibilidad: AjustesVisibilidadSimulacion) -> None:
    carga = {
        "formato": FORMATO, "version": VERSION, "sistema": "EPITROCOIDAL",
        "parametros": asdict(parametros),
        "simulacion": sim,   # {"modo": "Manual"|"Automático", "modo_pinon_alterno": bool, "angulo_manual": float, "predeterminado": bool}
        "perfil_movimiento": perfil_mov.to_dict() if perfil_mov else None,
        "visibilidad": asdict(visibilidad),
    }
    Path(ruta).write_text(json.dumps(carga, indent=2, ensure_ascii=False), encoding="utf-8")


def abrir_proyecto(ruta) -> dict:
    try:
        d = json.loads(Path(ruta).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ArchivoInvalido(f"No se pudo leer el archivo: {e}") from e
    if d.get("formato") != FORMATO:
        raise ArchivoInvalido("El archivo no es un proyecto de RPS Design V2.")
    if d.get("sistema") != "EPITROCOIDAL":
        raise ArchivoInvalido(f"Sistema '{d.get('sistema')}' aún no soportado en V2.")
    nombres = {f.name for f in fields(ParametrosEpitrocoidal)}
    params = ParametrosEpitrocoidal(**{k: v for k, v in d.get("parametros", {}).items() if k in nombres})
    if not params.es_valido():
        raise ArchivoInvalido("Los parámetros del archivo no son válidos.")
    vis_n = {f.name for f in fields(AjustesVisibilidadSimulacion)}
    vis = AjustesVisibilidadSimulacion(**{k: v for k, v in d.get("visibilidad", {}).items() if k in vis_n})
    pm = d.get("perfil_movimiento")
    return {"parametros": params, "simulacion": d.get("simulacion", {}),
            "perfil_movimiento": PerfilMovimiento.from_dict(pm) if pm else None,
            "visibilidad": vis}
