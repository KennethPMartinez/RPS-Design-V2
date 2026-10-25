# -*- coding: utf-8 -*-
"""
engine/backend_selector.py

Selector de módulo de arreglos (NumPy/CuPy) según config.app_settings.
ajustes.modo_hardware ("CPU"|"GPU"|"Hibrido") -- ver ModusOperandi.docx
(tabla de Hardware).

`xp_para(n_elementos)` es el punto único de verdad que consultan
`BaseEngine` y los 3 motores concretos (`curva_generatriz`,
`tangente_generatriz`, ensamble de patrón, `rodillos_en_contacto`) para
decidir NumPy o CuPy en cada operación, según su tamaño real -- no una
sola decisión global por ventana (ver docstring de `xp_para`). También
lleva un registro liviano (`resumen_uso`, `ultimo_backend_usado`) para
poder verificar en runtime qué backend se usó en cada cálculo.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from config.app_settings import ajustes

try:
    import cupy as _cupy
except ImportError:  # pragma: no cover - CuPy es opcional
    _cupy = None


_CUPY_UTILIZABLE = None  # None = aún no probado; True/False = resultado cacheado


def cupy_disponible() -> bool:
    """A diferencia de solo comprobar el import, corre una prueba de humo
    real (un kernel elemental trivial) porque CuPy puede importarse sin
    problema y aun así fallar en tiempo de ejecución si falta el CUDA
    Toolkit/NVRTC (ver Pasos_a_seguir_1307262.docx: 'cannot open source
    file cupy/complex.cuh' al primer uso real, p. ej. en
    BaseEngine.rodillos_en_contacto -> xp.arange). El resultado se cachea
    para no repetir la compilación fallida en cada tick de la simulación."""
    global _CUPY_UTILIZABLE
    if _CUPY_UTILIZABLE is not None:
        return _CUPY_UTILIZABLE
    if _cupy is None:
        _CUPY_UTILIZABLE = False
        return False
    try:
        (_cupy.arange(2) + 1).get()  # fuerza compilación NVRTC + transferencia real
        _CUPY_UTILIZABLE = True
    except Exception:
        _CUPY_UTILIZABLE = False
    return _CUPY_UTILIZABLE


_AVISO_CUPY_FALTANTE = {"mostrado": False}


def modulo_arreglos():
    """Devuelve el módulo de arreglos a usar (numpy o cupy) según
    `ajustes.modo_hardware`. Cae a NumPy con un aviso por consola (una
    sola vez por proceso) si se pidió GPU/Híbrido pero CuPy no está
    instalado O no es utilizable en este equipo (ver cupy_disponible) --
    nunca lanza excepción, para no tumbar la simulación por un ajuste de
    hardware mal configurado."""
    if ajustes.modo_hardware in ("GPU", "Hibrido"):
        if cupy_disponible():
            return _cupy
        if not _AVISO_CUPY_FALTANTE["mostrado"]:
            motivo = ("CuPy no está instalado" if _cupy is None else
                       "CuPy está instalado pero no es utilizable en este "
                       "equipo (falta el CUDA Toolkit/NVRTC compatible)")
            print(
                f"[engine.backend_selector] modo_hardware="
                f"'{ajustes.modo_hardware}' pero {motivo}; usando NumPy. "
                "Instala/repara el CUDA Toolkit correspondiente a tu CuPy "
                "(p. ej. 'pip install cupy-cuda12x') para GPU real."
            )
            _AVISO_CUPY_FALTANTE["mostrado"] = True
    return np


# Por debajo de este tamaño, el overhead de lanzar kernels en GPU (~0.1ms+
# por llamada) supera lo que se gana -- ver benchmark_cpu_gpu.pdf: la
# ventaja de CuPy se midió sobre multiplicación de matrices GRANDES, no
# sobre los ~500 puntos de una vista interactiva de las Pestañas 1-4.
UMBRAL_GPU_PUNTOS = 5000


def xp_para(n_elementos: int):
    """Decide qué módulo de arreglos usar para UNA operación de tamaño
    `n_elementos`, según `ajustes.modo_hardware`:
      - "CPU": siempre NumPy.
      - "GPU": siempre CuPy (si es utilizable) -- elección explícita del
        usuario, aunque no compense para arrays chicos.
      - "Hibrido": NumPy para arrays chicos (control, refresco interactivo)
        y CuPy solo cuando `n_elementos` supera UMBRAL_GPU_PUNTOS
        (exportación de alta resolución, patrones con muchos dientes) --
        exactamente 'NumPy para control + CuPy para la geometría pesada'
        de ModusOperandi.docx.
    A diferencia de `modulo_arreglos()` (una sola decisión global), esta
    función se llama una vez POR OPERACIÓN, porque una misma ventana hace
    tanto trabajo chico (bisección de theta_lim, ticks de simulación) como
    trabajo grande (exportar con n_puntos alto) y no tiene sentido forzar
    GPU en el primero solo porque el usuario activó Híbrido."""
    if ajustes.modo_hardware == "CPU":
        xp = np
    elif ajustes.modo_hardware == "Hibrido" and n_elementos < UMBRAL_GPU_PUNTOS:
        xp = np
    else:
        xp = modulo_arreglos()
    _registrar_uso(xp, n_elementos)
    return xp


def a_numpy(arreglo):
    """Trae un arreglo de vuelta a memoria de host (NumPy) si vive en GPU;
    no hace nada si ya es NumPy. Se usa UNA sola vez, al final de cada
    cálculo (ver BaseEngine.generar_perfil/generar_patron), en vez de
    transferir en cada paso intermedio -- cada transferencia GPU<->CPU
    tiene su propio costo fijo, así que múltiples transferencias chicas
    son peores que una sola transferencia grande al final."""
    if _cupy is not None and isinstance(arreglo, _cupy.ndarray):
        return _cupy.asnumpy(arreglo)
    return arreglo


# ------------------------------------------------------------------
# Verificación en runtime: ¿la app corrió en CPU, GPU, o ambas?
# ------------------------------------------------------------------
# nvidia-smi/Administrador de tareas confirman que la GPU física se activa,
# pero no dicen QUÉ operación fue a cada backend -- eso es lo que hace
# falta para comprobar que modo Híbrido de verdad reparte el trabajo
# (control en CPU, geometría pesada en GPU). Este registro liviano lleva
# la cuenta de cada decisión de xp_para() para poder consultarla desde la
# UI (ver ui/system_window.py, barra de estado) o la consola.
_registro_uso = {"CPU": 0, "GPU": 0}
_ultimo_backend: Optional[str] = None
_ultimo_n_elementos: int = 0


def _registrar_uso(xp, n_elementos: int) -> None:
    global _ultimo_backend, _ultimo_n_elementos
    nombre = "GPU" if (_cupy is not None and xp is _cupy) else "CPU"
    _registro_uso[nombre] += 1
    _ultimo_backend = nombre
    _ultimo_n_elementos = n_elementos


def resumen_uso() -> dict:
    """Conteo acumulado de veces que xp_para() resolvió a CPU vs GPU desde
    que arrancó el proceso. En modo Híbrido, ver ambos contadores subir
    (no solo uno) es la prueba de que el reparto de trabajo es real."""
    return dict(_registro_uso)


def ultimo_backend_usado() -> Optional[str]:
    """'CPU' o 'GPU': backend de la última llamada a xp_para(), o None si
    todavía no se ha hecho ningún cálculo. Útil para mostrar en la barra
    de estado justo después de recalcular un perfil/patrón."""
    return _ultimo_backend


def ultimo_tamano_operacion() -> int:
    """n_elementos de la última llamada a xp_para() -- para entender POR
    QUÉ se eligió ese backend (p. ej. '18035 puntos -> GPU' vs '500 puntos
    -> CPU' aunque el modo sea el mismo Híbrido en ambos casos)."""
    return _ultimo_n_elementos
