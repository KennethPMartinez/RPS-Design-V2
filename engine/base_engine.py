# -*- coding: utf-8 -*-
"""
engine/base_engine.py

Coordinador común de los 3 motores de perfil trocoidal (Cremallera,
Epitrocoidal, Hipotrocoidal). Ya NO contiene la geometría del piñón de
rodillos (ver engine/rollerpinion_engine.py) ni el algoritmo de detección
de contacto (ver engine/contact_engine.py): ambos se instancian aquí, una
sola vez por motor, y quedan disponibles por composición (`self.rodillo`,
`self.contacto`) -- separación de responsabilidades de esta sesión.

Cada motor concreto solo debe implementar:
    - curva_generatriz(theta, xp=np)   -> (x, y) de la curva SIN offset
    - tangente_generatriz(theta, xp=np)-> (dx, dy) derivada analítica
    - calcular_theta_lim()      -> criterio de convergencia propio de cada perfil
    - calcular_paso()           -> paso lineal o angular de referencia
    - vector_referencia_cir(theta, xp=np)
    - camino_de_contacto(theta, xp=np)

El resto (offset, ángulo de presión, curvatura, generación de puntos,
tabulación para exportar, delegación a RollerPinionEngine/ContactEngine)
vive aquí una sola vez.

Ver engine/system_context.py (ContextoSistema): único índice compartido de
identidad geométrica (Zrp, Zg, tipo de ensamble, rotación de vista, fase
inicial, relación de transmisión, cd, perfil_interior) construido aquí y
pasado por referencia a RollerPinionEngine/ContactEngine/CinematicaEngine.

BACKEND CPU/GPU (ver benchmark_cpu_gpu.pdf y engine/backend_selector.py):
sin cambios respecto a la versión anterior -- generar_perfil/generar_patron/
tabular_exportacion deciden `xp` por tamaño de trabajo; la bisección de
theta_lim siempre corre en NumPy puro.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import numpy as np

from engine import math_utils as mu
from engine import backend_selector, sampling_preferences
from engine.system_context import ContextoSistema
from engine.rollerpinion_engine import RollerPinionEngine
from engine.contact_engine import ContactEngine


@dataclass
class ResultadoPerfil:
    """Salida numérica de un motor -- SIN CAMBIOS DE FORMA respecto a la
    versión anterior (widgets.plot_canvas, widgets.opengl_widget y
    exporters.* siguen consumiéndola igual); lo que cambia con esta
    reestructuración es QUIÉN llena cada campo internamente (ver docstring
    del módulo), no el contrato de datos."""
    theta: np.ndarray
    curva_x: np.ndarray
    curva_y: np.ndarray        # curva generatriz "pura" (trocoide/epi/hipo)
    offset_x: np.ndarray
    offset_y: np.ndarray       # perfil real de diente (lo que se grafica/exporta)
    theta_lim: float
    paso: float
    # Pestaña 2: Ángulo de presión
    angulo_presion_grados: Optional[np.ndarray] = None
    # Pestaña 3: Radio de curvatura
    radio_curvatura: Optional[np.ndarray] = None
    radio_curvatura_minimo: Optional[float] = None
    # Pestaña 4: Camino de contacto
    camino_contacto_x: Optional[np.ndarray] = None
    camino_contacto_y: Optional[np.ndarray] = None
    # Patrón de ensamble
    patron_x: Optional[np.ndarray] = None
    patron_y: Optional[np.ndarray] = None
    # Piñón de rodillos (Pestaña 5)
    pinon_centros_x: Optional[np.ndarray] = None
    pinon_centros_y: Optional[np.ndarray] = None
    pinon_plantilla_x: Optional[np.ndarray] = None
    pinon_plantilla_y: Optional[np.ndarray] = None
    distancia_centros_pinon: float = 0.0
    rotacion_vista_grados: float = 0.0
    factor_giro_pinon_fijo: float = -1.0
    factor_giro_pinon_orbitar: float = 1.0
    radio_paso_pinon: Optional[float] = None
    radio_paso_engranaje: Optional[float] = None
    linea_paso_cremallera_x: Optional[np.ndarray] = None
    linea_paso_cremallera_y: Optional[np.ndarray] = None
    radio_rodillo: Optional[float] = None
    diente_centros_x: Optional[np.ndarray] = None
    diente_centros_y: Optional[np.ndarray] = None
    # Discretización usada para el perfil (engine.sampling_preferences.MuestreoInfo); None si el n fue explícito
    muestreo: Optional[object] = None


class BaseEngine(ABC):
    NPUNTOS_EXPORTACION_DEFAULT = 1001
    SIGNO_NORMAL: bool = False   # False=Trocoidal/Epitrocoidal, True=Hipotrocoidal
    NOMBRE_CURVA: str = "Curva"  # usado como encabezado en tabular_exportacion()
    ROTACION_VISTA_SIMULACION_GRADOS: float = 0.0
    TIPO_ENSAMBLE: str = "angular"  # "lineal" (Cremallera) | "angular" (Epi/Hipo)
    FASE_INICIAL_PINON_RODILLOS_GRADOS: float = 0.0

    def __init__(self, parametros):
        self.parametros = parametros
        self._theta_lim_cache: Optional[float] = None

        # Índice único de identidad geométrica (ver system_context.py) --
        # se construye una sola vez aquí y se pasa por referencia a los
        # 2 componentes de abajo (y luego al motor concreto, ver
        # epitrocoidal_engine.py/hipotrocoidal_engine.py), en vez de que
        # cada uno reciba sus propios argumentos sueltos.
        self.contexto = ContextoSistema(
            tipo_ensamble=self.TIPO_ENSAMBLE,
            numero_rodillos=parametros.numero_rodillos,
            numero_dientes=getattr(parametros, "numero_dientes", None),
            rotacion_vista_grados=self.ROTACION_VISTA_SIMULACION_GRADOS,
            fase_inicial_pinon_rodillos_grados=self.FASE_INICIAL_PINON_RODILLOS_GRADOS,
        )
        self.rodillo = RollerPinionEngine(parametros, self.contexto)
        self.contacto = ContactEngine(self, self.contexto, self.rodillo)

    # ------------------------------------------------------------------
    # Delegados a RollerPinionEngine (mantienen la API previa para no
    # romper a quien ya llamaba motor.radio_rodillo / motor.centros_
    # rodillos_pinon() / motor.plantilla_rodillo_pinon())
    # ------------------------------------------------------------------
    @property
    def radio_rodillo(self) -> float:
        return self.rodillo.radio_rodillo

    @property
    def radio_pinon_rodillos(self) -> float:
        return self.rodillo.mrrp

    def centros_rodillos_pinon(self):
        return self.rodillo.centros_rodillos()

    def plantilla_rodillo_pinon(self, n_puntos: int = 200):
        return self.rodillo.plantilla_rodillo(n_puntos)

    def _muestrear_circulo(self, radio: float, n_puntos: int = 200):
        return self.rodillo.muestrear_circulo(radio, n_puntos)

    # ------------------------------------------------------------------
    # Geometría de referencia del engranaje (None/0 por defecto; Epi/Hipo
    # la sobreescriben con su fórmula concreta -- ver esos módulos)
    # ------------------------------------------------------------------
    @property
    def distancia_centros_pinon(self) -> float:
        return 0.0

    @property
    def radio_valle(self) -> Optional[float]:
        return None

    @property
    def radio_cresta(self) -> Optional[float]:
        return None

    @property
    def radio_circulo_centro_rodillo_raiz(self) -> float:
        """Distancia al eje del engranaje del centro del rodillo en θ=0
        (máximo acople). Hipotrocoidal la sobreescribe (signo invertido,
        perfil interior/anular -- ver ese módulo)."""
        gx0, gy0 = self.curva_generatriz(0.0)
        return float(np.hypot(gx0, gy0))

    @property
    def radio_circulo_centro_rodillo_cresta(self) -> float:
        """Ídem, en θ=theta_lim (límite de flanco, cresta del diente)."""
        gxl, gyl = self.curva_generatriz(self.theta_lim)
        return float(np.hypot(gxl, gyl))

    def _normalizar_id_diente(self, indice_diente):
        return self.contexto.normalizar_id_diente(indice_diente)

    @property
    def theta_lim(self) -> float:
        """`calcular_theta_lim()` CACHEADO (progress.md §25): la búsqueda
        por bisección solo depende de los parámetros del motor (fijos
        durante toda la vida de esta instancia); se calcula una sola vez,
        perezosamente."""
        if self._theta_lim_cache is None:
            self._theta_lim_cache = self.calcular_theta_lim()
        return self._theta_lim_cache

    # ------------------------------------------------------------------
    # A implementar por cada motor concreto (geometría de la curva)
    # ------------------------------------------------------------------
    @abstractmethod
    def curva_generatriz(self, theta, xp=np):
        raise NotImplementedError

    @abstractmethod
    def tangente_generatriz(self, theta, xp=np):
        raise NotImplementedError

    @abstractmethod
    def calcular_theta_lim(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def calcular_paso(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def vector_referencia_cir(self, theta, xp=np):
        raise NotImplementedError

    @abstractmethod
    def camino_de_contacto(self, theta, xp=np):
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Comunes a los 3 perfiles
    # ------------------------------------------------------------------
    @property
    def factor_correccion_angulo(self) -> float:
        """Fr = 1 / cos(angulo_presion_minimo) — ver progress.md §4."""
        return 1.0 / np.cos(np.radians(self.parametros.angulo_presion_minimo))

    def curva_offset(self, theta, xp=np):
        """Perfil real de diente: curva_generatriz desplazada radio_rodillo
        en la dirección normal a su tangente."""
        x, y = self.curva_generatriz(theta, xp=xp)
        dx, dy = self.tangente_generatriz(theta, xp=xp)
        return mu.offset_desde_tangente(x, y, dx, dy, self.radio_rodillo,
                                         invertido=self.SIGNO_NORMAL, xp=xp)

    def _posicionar_en_diente(self, x, y, indice_diente, xp=np):
        """Traslada (lineal, Cremallera) o rota (angular, Epi/Hipotrocoidal)
        un punto ya evaluado en el marco LOCAL del diente base hasta la
        posición real del diente/copia `indice_diente` en el patrón ya
        ensamblado -- mismo criterio que generar_patron_lineal/angular de
        cada motor (ver progress.md §22). Queda en BaseEngine (y no en
        ContextoSistema) porque necesita `calcular_paso()`, propio de cada
        motor concreto."""
        if self.contexto.tipo_ensamble == "lineal":
            return x + indice_diente * self.calcular_paso(), y
        beta = indice_diente * self.contexto.paso_angular_diente
        return mu.rotar(x, y, beta, xp=xp)

    def angulo_presion(self, theta, xp=np):
        """Ángulo de presión con signo, en grados (ver progress.md §11)."""
        dx, dy = self.tangente_generatriz(theta, xp=xp)
        nx, ny = mu.normal_unitario(dx, dy, invertido=self.SIGNO_NORMAL, xp=xp)
        vx, vy = self.vector_referencia_cir(theta, xp=xp)
        cos_ang = xp.clip(-(vx * nx + vy * ny), -1.0, 1.0)
        angulo_deg = xp.degrees(xp.arccos(cos_ang))
        return xp.where(xp.asarray(theta) < 0, angulo_deg - 180.0, angulo_deg)

    def curvatura(self, theta, h: float = 1e-5, xp=np):
        """κ(θ) de la curva OFFSET por diferenciación numérica (ver
        progress.md §11 y math_utils.derivada_numerica)."""
        funcion_offset = lambda th: self.curva_offset(th, xp=xp)
        r1x, r1y = mu.derivada_numerica(funcion_offset, theta, h=h, orden=1)
        r2x, r2y = mu.derivada_numerica(funcion_offset, theta, h=h, orden=2)
        det = r1x * r2y - r1y * r2x
        norma_r1 = xp.hypot(r1x, r1y)
        return xp.abs(det) / norma_r1 ** 3

    def radio_curvatura(self, theta, h: float = 1e-5, xp=np):
        """1/curvatura(θ) -- se expone el radio, no la curvatura."""
        return 1.0 / self.curvatura(theta, h=h, xp=xp)

    def _evaluador_offset(self):
        """θ (array NumPy) -> (N, 2) del perfil real: lo que se discretiza (el muestreo adaptativo es dependiente de
        datos y siempre corre en NumPy; el resto del cálculo sigue usando el backend elegido)."""
        return lambda ts: np.column_stack(self.curva_offset(ts, xp=np))

    def generar_perfil(self, n_puntos: int | None = None,
                        incluir_analisis: bool = True) -> ResultadoPerfil:
        """`n_puntos` explícito (exportaciones, CAD): malla uniforme de ese tamaño, SIN cambios.
        `None` (simulación): discretización según Ajustes → Cálculo (`sampling_preferences.politica_actual()`)."""
        theta_lim = self.theta_lim
        info = None
        if n_puntos is None:
            theta_np, info = sampling_preferences.muestrear(self._evaluador_offset(), -theta_lim, theta_lim)
            n_puntos = theta_np.size
            xp = backend_selector.xp_para(n_puntos)
            theta = xp.asarray(theta_np)
        else:
            xp = backend_selector.xp_para(n_puntos)
            theta = xp.linspace(-theta_lim, theta_lim, n_puntos)
        cx, cy = self.curva_generatriz(theta, xp=xp)
        ox, oy = self.curva_offset(theta, xp=xp)
        resultado = ResultadoPerfil(
            theta=backend_selector.a_numpy(theta),
            curva_x=backend_selector.a_numpy(cx), curva_y=backend_selector.a_numpy(cy),
            offset_x=backend_selector.a_numpy(ox), offset_y=backend_selector.a_numpy(oy),
            theta_lim=theta_lim, paso=self.calcular_paso(), muestreo=info,
        )
        if incluir_analisis:
            angulo = self.angulo_presion(theta, xp=xp)
            radio = self.radio_curvatura(theta, xp=xp)
            ccx, ccy = self.camino_de_contacto(theta, xp=xp)
            resultado.angulo_presion_grados = backend_selector.a_numpy(angulo)
            resultado.radio_curvatura = backend_selector.a_numpy(radio)
            resultado.radio_curvatura_minimo = float(xp.min(radio))
            resultado.camino_contacto_x = backend_selector.a_numpy(ccx)
            resultado.camino_contacto_y = backend_selector.a_numpy(ccy)
        return resultado

    def tabular_exportacion(self, n_puntos: int = NPUNTOS_EXPORTACION_DEFAULT) -> dict:
        resultado = self.generar_perfil(n_puntos)
        return {
            "Theta": resultado.theta,
            "Offset_X": resultado.offset_x,
            "Offset_Y": resultado.offset_y,
            f"{self.NOMBRE_CURVA}_X": resultado.curva_x,
            f"{self.NOMBRE_CURVA}_Y": resultado.curva_y,
            "Angulo_Presion_deg": resultado.angulo_presion_grados,
            "Radio_Curvatura": resultado.radio_curvatura,
            "Camino_Contacto_X": resultado.camino_contacto_x,
            "Camino_Contacto_Y": resultado.camino_contacto_y,
        }

    def generar_patron(self) -> Optional[ResultadoPerfil]:
        """Devuelve None por defecto; cada motor concreto sobreescribe con
        su propio ensamble (lineal o angular)."""
        return None

    # ------------------------------------------------------------------
    # Delegado a ContactEngine (ver engine/contact_engine.py)
    # ------------------------------------------------------------------
    def rodillos_en_contacto(self, theta_referencia_rad: float,
                             theta_lim: float | None = None,
                             modo_pinon_alterno: bool = False,
                             estado_cinematico=None) -> list[dict]:
        """`estado_cinematico` (engine.cinematica_engine.EstadoCinematico):
        OBLIGATORIO para Epitrocoidal/Hipotrocoidal desde la reestructuración
        del 27 jul 2026 (ver contact_engine.py) -- el nuevo criterio de
        detección de contacto necesita angulo_pinon_rad/centro_pinon/
        angulo_patron_rad para ubicar los rodillos geométricamente, no solo
        theta_referencia_rad. Cremallera sigue sin necesitarlo (queda en
        None, se ignora)."""
        return self.contacto.calcular(theta_referencia_rad, theta_lim,
                                      modo_pinon_alterno, estado_cinematico)
