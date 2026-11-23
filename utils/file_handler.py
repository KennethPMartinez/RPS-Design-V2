# -*- coding: utf-8 -*-
"""
utils/file_handler.py

Abrir / Guardar del proyecto V2 (JSON) para los tres sistemas migrados. Un archivo contiene todo lo
necesario para reproducir la sesión: parámetros, modo de simulación, perfil de giro (si fue editado)
y capas visibles. Sin dependencias de Qt.
"""
from __future__ import annotations

import json
from dataclasses import asdict, fields
from pathlib import Path
from typing import Optional

from config.data_structures import (AjustesVisibilidadSimulacion, ParametrosCremallera,
                                    ParametrosEpitrocoidal, ParametrosHipotrocoidal,
                                    ParametrosPlanetario)
from engine.motion_engine import PerfilMovimiento

FORMATO = "RPS Design V2"
VERSION = 2
PARAMETROS_POR_SISTEMA = {"EPITROCOIDAL": ParametrosEpitrocoidal,
                          "HIPOTROCOIDAL": ParametrosHipotrocoidal,
                          "TROCOIDAL": ParametrosCremallera,
                          "PLANETARIO": ParametrosPlanetario}


class ArchivoInvalido(ValueError):
    pass


def serializar(sistema: str, parametros, sim: dict, perfil_mov: Optional[PerfilMovimiento],
               visibilidad: AjustesVisibilidadSimulacion) -> dict:
    return {
        "formato": FORMATO, "version": VERSION, "sistema": sistema,
        "parametros": asdict(parametros),
        "simulacion": sim,   # {"modo", "modo_pinon", "valor_manual" (θ° o X mm), "predeterminado"}
        "perfil_movimiento": perfil_mov.to_dict() if perfil_mov else None,
        "visibilidad": asdict(visibilidad),
    }


def guardar_proyecto(ruta, sistema: str, parametros, sim: dict, perfil_mov: Optional[PerfilMovimiento],
                     visibilidad: AjustesVisibilidadSimulacion) -> None:
    carga = serializar(sistema, parametros, sim, perfil_mov, visibilidad)
    Path(ruta).write_text(json.dumps(carga, indent=2, ensure_ascii=False), encoding="utf-8")


def abrir_proyecto(ruta, sistema: str) -> dict:
    """Lee un proyecto y verifica que sea del `sistema` pedido."""
    try:
        d = json.loads(Path(ruta).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ArchivoInvalido(f"No se pudo leer el archivo: {e}") from e
    if d.get("formato") != FORMATO:
        raise ArchivoInvalido("El archivo no es un proyecto de RPS Design V2.")
    guardado = {"CREMALLERA": "TROCOIDAL"}.get(d.get("sistema"), d.get("sistema"))
    if guardado != sistema:
        raise ArchivoInvalido(f"El archivo es del sistema '{guardado}', no de '{sistema}'.")
    clase = PARAMETROS_POR_SISTEMA[sistema]
    nombres = {f.name for f in fields(clase)}
    params = clase(**{k: v for k, v in d.get("parametros", {}).items() if k in nombres})
    if not params.es_valido():
        raise ArchivoInvalido("Los parámetros del archivo no son válidos.")
    vis_n = {f.name for f in fields(AjustesVisibilidadSimulacion)}
    vis = AjustesVisibilidadSimulacion(**{k: v for k, v in d.get("visibilidad", {}).items() if k in vis_n})
    pm = d.get("perfil_movimiento")
    return {"parametros": params, "simulacion": d.get("simulacion", {}),
            "perfil_movimiento": PerfilMovimiento.from_dict(pm) if pm else None,
            "visibilidad": vis}
