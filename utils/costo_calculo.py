# -*- coding: utf-8 -*-
"""
utils/costo_calculo.py — texto del indicador «Mostrar estimación de costo» (Ajustes → Cálculo y precisión).

Solo reporta lo VERIFICABLE: nº real de muestras, tiempo MEDIDO (perf_counter) de la última geometría calculada,
error/giro máximos observados frente a la tolerancia y si se alcanzó el límite de muestras. No predice tiempos: con
unos pocos milisegundos por cálculo y dependencia del backend/CPU no hay base para un estimador fiable.
"""
from __future__ import annotations

from utils.formato_numerico import fmt


def _um(mm: float) -> str:
    """Errores de muestreo del orden de micras: se muestran en µm para que los decimales no los oculten."""
    return fmt(mm * 1000.0, "µm")


def _agregar(infos):
    n = sum(i.n_muestras for _e, i in infos)
    verificados = [i for _e, i in infos if i.error_mm is not None]
    err = max((i.error_mm for i in verificados), default=None)
    giro = max((i.giro_grados for i in verificados), default=None)
    cumple = None if not verificados else all(i.cumple for i in verificados)
    return n, err, giro, cumple, any(i.limite_alcanzado for _e, i in infos)


def advertencia(infos) -> str | None:
    """Mensaje cuando la discretización NO cumple la tolerancia configurada (None si cumple o no se verificó)."""
    if not infos:
        return None
    n, err, _giro, cumple, limite = _agregar(infos)
    i0 = infos[0][1]
    if limite:
        return (f"Discretización: se alcanzó el límite de {i0.n_solicitado} muestras y la tolerancia no se cumple "
                f"(error máx. {_um(err)} frente a {_um(i0.tol_mm)}). Sube el máximo o relaja la tolerancia.")
    if cumple is False:
        return (f"Discretización uniforme: el error máx. {_um(err)} supera la tolerancia {_um(i0.tol_mm)}. "
                "Usa más muestras o la estrategia adaptativa.")
    return None


def resumen(infos, tiempo_geometria_s: float, reutilizada: bool) -> tuple[str, str]:
    """(texto, nivel) con nivel «ok» o «aviso»."""
    if not infos:
        return "Sin discretización registrada", "ok"
    n, err, giro, cumple, limite = _agregar(infos)
    i0 = infos[0][1]
    partes = [("+".join(f"{e} {i.n_muestras}" if e else str(i.n_muestras) for e, i in infos)) + " muestras"
              + f" ({i0.estrategia})"]
    if i0.ajustado_a_impar:
        partes.append(f"{i0.n_solicitado} → {i0.n_muestras} (impar, conserva θ = 0)")
    if err is not None:
        partes.append(f"error máx. {_um(err)} {'≤' if err <= i0.tol_mm else '>'} {_um(i0.tol_mm)}")
        partes.append(f"giro máx. {fmt(giro, '°')} {'≤' if giro <= i0.ang_grados else '>'} {fmt(i0.ang_grados, '°')}")
    if limite:
        partes.append(f"⚠ límite de {i0.n_solicitado} muestras alcanzado")
    partes.append("geometría reutilizada (caché)" if reutilizada else f"geometría {tiempo_geometria_s * 1e3:.1f} ms (medido)")
    aviso = limite or cumple is False
    return ("⚠ " if aviso else "") + " · ".join(partes), ("aviso" if aviso else "ok")
