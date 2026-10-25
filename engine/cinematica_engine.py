# -*- coding: utf-8 -*-
"""
engine/cinematica_engine.py

Dos responsabilidades separadas a propósito:

  - EstadoCinematico: un snapshot de "dónde está todo" en un instante dado
    (ángulo/posición del motor, tiempo, transformación resultante del
    patrón y del piñón de rodillos). Pensado para conectarse más adelante
    a los controles de animación (reproducir/pausar, velocidad, línea de
    tiempo) sin tener que rediseñar el contrato de datos -- por ahora
    `omega_motor_rad_s` y `tiempo_s` quedan poblados pero sin un
    integrador propio detrás (el ángulo lo sigue resolviendo el encoder
    incremental del dial en ui/system_window.py).

  - SolverCinematico: aplica las restricciones de rodadura sin
    deslizamiento (ver progress.md §19/§24) para resolver, a partir de
    ParametrosSimulacion (modo angular/lineal, piñón Fijo/Alterno) y del
    ángulo motor ya acumulado, la EstadoCinematico resultante -- cuánto
    gira/traslada el patrón, y dónde queda el piñón de rodillos (centro +
    giro propio). Reemplaza la lógica que antes vivía DUPLICADA entre
    ui/system_window.py (_calcular_angulo_motor_grados) y
    widgets/opengl_widget.py (_centro_pinon_en_vivo,
    _transformar_patron_en_vivo), y también las propiedades
    factor_giro_pinon_fijo/orbitar que antes cada motor angular
    (Epitrocoidal/Hipotrocoidal) repetía casi igual, cambiando solo el
    signo -- aquí ese signo se deriva UNA vez de `contexto.perfil_interior`
    (ver engine/system_context.py).

Toda la resolución numérica real vive en la función de módulo
`resolver_estado()`, sin dependencias de ContextoSistema -- para que
widgets/opengl_widget.py pueda llamarla directamente con los pocos
escalares que ya trae en ResultadoPerfil (cd, factor_fijo, factor_orbitar)
sin tener que reconstruir un ContextoSistema completo solo para dibujar.
SolverCinematico es la envoltura que sí conoce el contexto completo (la
usan los motores de curva en su generar_patron(), ver epitrocoidal_engine.py
/ hipotrocoidal_engine.py) y delega en la misma función.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

import numpy as np

from engine.system_context import ContextoSistema


@dataclass
class EstadoCinematico:
    """Estado instantáneo del ensamble. Ver docstring del módulo."""
    theta_motor_rad: float = 0.0
    omega_motor_rad_s: float = 0.0
    tiempo_s: float = 0.0
    # Transformación resultante del PATRÓN (engranaje/cremallera ya
    # ensamblado); solo válida cuando patron_fijo=False.
    angulo_patron_rad: float = 0.0
    traslacion_patron: Tuple[float, float] = (0.0, 0.0)
    patron_fijo: bool = True  # True = modo "Alterno" (Orbitar/Trasladar): el patrón no se mueve
    # Transformación resultante del PIÑÓN DE RODILLOS (siempre válida)
    angulo_pinon_rad: float = 0.0
    centro_pinon: Tuple[float, float] = (0.0, 0.0)
    # Ángulo de ROTACIÓN RELATIVA rodillo<->engranaje, en el marco de generación
    # de la curva (el mismo "θ" que consume curva_generatriz/curva_offset/
    # ContactEngine, ver progress.md -- hallazgo de Kenneth del 26 jul 2026):
    # - Fijo: coincide con angulo_patron_rad (el engranaje gira, el piñón no).
    # - Orbitar: es el ángulo de ÓRBITA del centro del piñón (angulo_motor /
    #   factor_giro_orbitar), NO angulo_motor directo -- antes de este fix,
    #   ContactEngine recibía angulo_motor sin dividir por el factor, así que
    #   el contacto avanzaba k veces más rápido que la órbita real del piñón
    #   (k = factor_giro_orbitar, el mismo factor de "la moneda que rueda"
    #   ya presente en curva_generatriz vía k*theta). Este campo es la ÚNICA
    #   fuente que tanto el render (rotación del patrón/órbita del piñón)
    #   como engine.contact_engine.ContactEngine deben consumir para
    #   theta_referencia_rad -- ya no deben calcularse por separado.
    angulo_relativo_generatriz_rad: float = 0.0


def calcular_cir(contexto: ContextoSistema, theta_referencia_rad: float,
                 modo_pinon_alterno: bool):
    """CIR (Centro Instantáneo de Rotación): punto de referencia global usado
    para dibujar la línea de acción del contacto (progress.md §29, ver
    widgets/opengl_widget.py:_dibujar_contactos). Antes vivía en
    ContactEngine, que le pedía prestado `self.motor.cir()` -- pero el CIR
    es una cantidad CINEMÁTICA (depende del estado de la simulación:
    theta_referencia_rad, modo_pinon_alterno), no de la geometría de la
    curva en sí (que es lo que sí usa `camino_de_contacto()`, evaluado
    sobre TODO el rango de theta del perfil -- ese uso NO se mueve, sigue
    en el motor de curva). Aquí solo se necesita `radio_paso_engranaje`
    (R1, guardado en el contexto por Epitrocoidal/Hipotrocoidal) y el
    mismo criterio de signo que ya usa `_theta_k_candidatos` para decidir
    el ángulo de referencia según el modo. None en Cremallera (no hay
    engranaje circular del que definir un CIR)."""
    R1 = contexto.radio_paso_engranaje
    if R1 is None:
        return None
    theta_cir = -theta_referencia_rad if modo_pinon_alterno else theta_referencia_rad
    return R1 * np.sin(theta_cir), R1 * np.cos(theta_cir)


def resolver_estado(cd: float, factor_giro_fijo: float, factor_giro_orbitar: float,
                    modo: str, activa: bool, modo_pinon_alterno: bool,
                    angulo_motor_grados: float, posicion_x_mm: float) -> EstadoCinematico:
    """Resuelve la EstadoCinematico completa para un instante dado, idéntico
    fórmula por fórmula al comportamiento confirmado antes de esta
    reestructuración (ver progress.md §19 y Pasos_a_seguir_1407262.docx,
    items 7/10/12/13/16). No depende de ContextoSistema: solo de los
    escalares que ya viajan en ResultadoPerfil, para que
    widgets/opengl_widget.py la pueda llamar sin reconstruir nada."""
    angulo_motor = np.radians(angulo_motor_grados) if activa else 0.0
    posicion_x = posicion_x_mm if activa else 0.0

    estado = EstadoCinematico(
        theta_motor_rad=angulo_motor,
        patron_fijo=bool(modo_pinon_alterno),
    )

    if modo == "angular":
        if not modo_pinon_alterno:
            # "Fijo en X+": el piñón queda quieto, el patrón rota.
            angulo_patron = angulo_motor / factor_giro_fijo if factor_giro_fijo else 0.0
            estado.angulo_patron_rad = angulo_patron
            estado.angulo_pinon_rad = angulo_motor
            estado.centro_pinon = (cd, 0.0)
            # El engranaje es lo que gira relativo al piñón fijo -> el ángulo
            # de generación coincide con la rotación del patrón.
            estado.angulo_relativo_generatriz_rad = angulo_patron
        else:
            # "Orbitar": el patrón queda fijo, el piñón orbita + gira.
            estado.angulo_pinon_rad = angulo_motor
            angulo_orbita = angulo_motor / factor_giro_orbitar if factor_giro_orbitar else 0.0
            estado.centro_pinon = (cd * np.cos(angulo_orbita), cd * np.sin(angulo_orbita))
            # El piñón es lo que orbita relativo al engranaje fijo -> el
            # ángulo de generación es el ángulo de ÓRBITA, NO angulo_motor
            # (ver nota del campo en EstadoCinematico -- este era el bug).
            estado.angulo_relativo_generatriz_rad = angulo_orbita
    else:  # "lineal" (Cremallera)
        if not modo_pinon_alterno:
            # "Fijo en Origen": el piñón queda quieto, el patrón se traslada.
            estado.traslacion_patron = (-posicion_x, 0.0)
            estado.angulo_pinon_rad = -angulo_motor
            estado.centro_pinon = (0.0, 0.0)
            estado.angulo_relativo_generatriz_rad = angulo_motor
        else:
            # "Trasladar": el patrón queda fijo, el piñón se traslada en X.
            estado.angulo_pinon_rad = -angulo_motor
            estado.centro_pinon = (posicion_x, 0.0)
            estado.angulo_relativo_generatriz_rad = angulo_motor

    return estado


class SolverCinematico:
    """Envoltura consciente de ContextoSistema: deriva los factores de giro
    del piñón (fijo/orbitar) a partir de la relación de transmisión y de si
    el engranaje es interior o exterior, y delega la resolución numérica en
    `resolver_estado()`. La usan los motores de curva angulares
    (Epitrocoidal/Hipotrocoidal) en su generar_patron() para poblar
    ResultadoPerfil.factor_giro_pinon_fijo/orbitar sin que cada uno tenga
    su propia propiedad ±derivada a mano."""

    def __init__(self, contexto: ContextoSistema):
        self.contexto = contexto

    def factor_giro_fijo(self) -> float:
        """ω_piñón/ω_motor en modo Fijo: rodadura sin deslizamiento en el
        punto de contacto fijo -> factor = R1/r = relación de transmisión
        (self.contexto.relacion_transmision). Signo: -1 si el engranaje es
        EXTERIOR (Epitrocoidal, engranaje externo-externo, sentido
        contrario, CONFIRMADO), +1 si es INTERIOR (Hipotrocoidal, anular,
        mismo sentido, CONFIRMADO) -- ver Pasos_a_seguir_1607262.docx."""
        i = self.contexto.relacion_transmision
        if i is None:
            return -1.0  # Cremallera no usa este factor (ver resolver_estado, rama lineal)
        signo = 1.0 if self.contexto.perfil_interior else -1.0
        return signo * i

    def factor_giro_orbitar(self) -> float:
        """ω_piñón/ω_órbita en modo Orbitar: factor = cd/prrp (derivación de
        rodadura sin deslizamiento, Kenneth, Pasos_a_seguir_1607262.docx).
        Signo opuesto al de factor_giro_fijo: +1 exterior (Epitrocoidal),
        -1 interior (Hipotrocoidal) -- ambos CONFIRMADOS."""
        cd = self.contexto.distancia_centros_pinon
        r = self.contexto.radio_primitivo_pinon_rodillos
        if not r:
            return 1.0
        signo = -1.0 if self.contexto.perfil_interior else 1.0
        return signo * (cd / r)

    def calcular_angulo_motor_grados(self, modo: str, angulo_acumulado_dial_grados: float,
                                     posicion_x_mm: float, prrp: float | None) -> float:
        """Ángulo acumulado del 'motor':
        - angular: el acumulado del encoder incremental del dial, YA
          resuelto por la UI (ver ui/system_window.py:_acumular_angulo_dial)
          -- se recibe tal cual, no se recalcula aquí.
        - lineal (Cremallera): rodadura sin deslizamiento del piñón sobre
          la cremallera -- ángulo = posicion_x_mm/prrp (rad), a grados."""
        if modo == "angular":
            return angulo_acumulado_dial_grados
        if prrp:
            return float(np.degrees(posicion_x_mm / prrp))
        return 0.0

    def resolver(self, modo: str, activa: bool, modo_pinon_alterno: bool,
                angulo_motor_grados: float, posicion_x_mm: float) -> EstadoCinematico:
        return resolver_estado(
            cd=self.contexto.distancia_centros_pinon,
            factor_giro_fijo=self.factor_giro_fijo(),
            factor_giro_orbitar=self.factor_giro_orbitar(),
            modo=modo, activa=activa, modo_pinon_alterno=modo_pinon_alterno,
            angulo_motor_grados=angulo_motor_grados, posicion_x_mm=posicion_x_mm,
        )

    def cir(self, theta_referencia_rad: float, modo_pinon_alterno: bool):
        """Conveniencia: ver la función de módulo `calcular_cir()` (misma
        firma salvo que aquí `contexto` ya está fijado por el constructor)."""
        return calcular_cir(self.contexto, theta_referencia_rad, modo_pinon_alterno)
