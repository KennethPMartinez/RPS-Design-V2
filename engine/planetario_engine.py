# -*- coding: utf-8 -*-
"""
engine/planetario_engine.py

Reductor planetario de piñón de rodillos: SOL (epitrocoidal, externo) + N PLANETAS (piñón de rodillos)
+ ANULAR (hipotrocoidal, interno). No añade geometría nueva: reutiliza EpitrocoidalEngine (sol-planeta)
e HipotrocoidalEngine (anular-planeta) y solo aporta condiciones de montaje y cinemática.

GEOMETRÍA. El mismo piñón engrana con ambos -> mismo prrp. cd(sol) = prrp·(1+Zs/Zrp) y
cd(anular) = prrp·(Za/Zrp-1)  =>  cd iguales  <=>  Za = Zs + 2·Zrp.

CINEMÁTICA (Willis): Zs·φs + Za·φa = (Zs+Za)·φc (+ constante de montaje C). Entrada = 1, bloqueado = 0,
el tercer componente se resuelve de la ecuación.

CONTACTOS. Los engines epi/hipo calculan contactos con el engranaje FIJO y el piñón orbitando ("Orbitar").
Para cada par (engranaje, planeta i) se les pasa el movimiento RELATIVO al engranaje: α = γ_i - φ_g y
giro = f·α con f = ±cd/prrp (es exactamente la rodadura sin deslizamiento); el resultado se rota φ_g
para llevarlo al marco del mundo.

MONTAJE. ψ_i (orientación del planeta) se fija con el sol. Respecto al anular el desfase del planeta i es
K_i = (Zs+Za)·β_i/Zrp - C/Zrp + π (constante en el tiempo). Con C = π·(Zrp mod 2) y N | (Zs+Za), K_i es
múltiplo del paso del rodillo: el planeta engrana con ambos y solo cambia la ETIQUETA del rodillo
(m_i = K_i/paso). Reglas de número de planetas (Cálculo_de_numero_de_planetas.pdf):
N | (Zs+Za)  y  D_ap < 2·cd·sin(π/N).
"""
from __future__ import annotations

import math
from utils.formato_numerico import fmt, fmt_signo
from dataclasses import dataclass

import numpy as np

from config.data_structures import (Componente, ParametrosEpitrocoidal, ParametrosHipotrocoidal,
                                    ParametrosPlanetario)
from engine.cinematica_engine import EstadoCinematico
from engine.epitrocoidal_engine import EpitrocoidalEngine
from engine.hipotrocoidal_engine import HipotrocoidalEngine

T_CORONA_MM = 1.0     # t_c: espesor radial de la corona de agujas
T_PARED_MM = 2.0      # t_w: pared mínima del portaplanetas


def geometria_planeta(Zs: int, Zrp: int, diametro_rodillo: float, rd: float, ap_min_deg: float):
    """(mrrp, prrp, cd sol-planeta, D_ap) sin construir los engines."""
    mrrp = rd / (2.0 * math.sin(math.pi / Zrp))
    prrp = mrrp / math.cos(math.radians(ap_min_deg))
    d_ap = 2.0 * (mrrp + diametro_rodillo / 2.0 + T_CORONA_MM + T_PARED_MM)
    return mrrp, prrp, prrp * (1.0 + Zs / Zrp), d_ap


def planetas_validos(Zs: int, Zrp: int, diametro_rodillo: float, rd: float, ap_min_deg: float) -> list[int]:
    if Zs < 3 or Zrp < 3 or rd <= 0 or diametro_rodillo <= 0:
        return []
    _, _, cd, d_ap = geometria_planeta(Zs, Zrp, diametro_rodillo, rd, ap_min_deg)
    suma = 2 * Zs + 2 * Zrp                      # Zs + Za
    return [n for n in range(2, suma + 1) if suma % n == 0 and d_ap < 2.0 * cd * math.sin(math.pi / n)]


def coeficientes_giro(Zs: int, Za: int, entrada: Componente, bloqueado: Componente):
    """(k_sol, k_brazo, k_anular) con ángulo_i = k_i·θ_entrada (Willis)."""
    if entrada == bloqueado:
        raise ValueError("El componente de entrada no puede ser el bloqueado.")
    coef = {Componente.SOL: Zs, Componente.ANULAR: Za, Componente.BRAZO: -(Zs + Za)}
    libre = ({*coef} - {entrada, bloqueado}).pop()
    k = {entrada: 1.0, bloqueado: 0.0, libre: -coef[entrada] / coef[libre]}
    return k[Componente.SOL], k[Componente.BRAZO], k[Componente.ANULAR]


@dataclass
class EstadoPlanetario:
    theta_in_rad: float
    fi_sol: float
    fi_brazo: float
    fi_anular: float
    gamma: np.ndarray      # (N,) ángulo de cada planeta alrededor del origen (mundo)
    psi: np.ndarray        # (N,) orientación de cada planeta (marco de vista del engine epi)
    centros: np.ndarray    # (N, 2) centro de cada planeta (mundo)


class PlanetarioEngine:
    def __init__(self, p: ParametrosPlanetario):
        self.parametros = p
        Zs, Zrp = p.numero_dientes_sol, p.numero_rodillos
        self.Zs, self.Zrp, self.Za = Zs, Zrp, Zs + 2 * Zrp
        base = dict(numero_rodillos=Zrp, diametro_rodillos=p.diametro_rodillos,
                    distancia_centro_rodillos=p.distancia_centro_rodillos,
                    angulo_presion_minimo=p.angulo_presion_minimo)
        self.p_sol = ParametrosEpitrocoidal(numero_dientes=Zs, **base)
        self.p_anular = ParametrosHipotrocoidal(numero_dientes=self.Za, **base)
        self.sol = EpitrocoidalEngine(self.p_sol)
        self.anular = HipotrocoidalEngine(self.p_anular)
        self.prrp = self.sol.rodillo.prrp
        self.cd = self.sol.distancia_centros_pinon
        if not math.isclose(self.cd, self.anular.distancia_centros_pinon, rel_tol=1e-9):
            raise ValueError("cd sol-planeta y anular-planeta no coinciden (Za debe ser Zs + 2·Zrp).")
        _, _, _, self.d_ap = geometria_planeta(Zs, Zrp, p.diametro_rodillos, p.distancia_centro_rodillos,
                                               p.angulo_presion_minimo)
        validos = planetas_validos(Zs, Zrp, p.diametro_rodillos, p.distancia_centro_rodillos,
                                   p.angulo_presion_minimo)
        self.N = int(p.numero_planetas or (validos[-1] if validos else 0))
        if self.N not in validos:
            raise ValueError(f"{self.N} planetas no cumplen N | (Zs+Za) y D_ap < 2·cd·sin(π/N). Válidos: {validos}")

        self.f_s = self.cd / self.prrp           # giro del planeta respecto al sol / órbita
        self.f_a = -self.f_s                     # ídem respecto al anular (engrane interno)
        self.k_sol, self.k_brazo, self.k_anular = coeficientes_giro(
            Zs, self.Za, p.componente_entrada, p.componente_bloqueado)
        self.C = math.pi * (Zrp % 2)             # constante de montaje de Willis
        self.fase_anular0 = self.C / self.Za
        self.beta = 2.0 * np.pi * np.arange(self.N) / self.N
        self.desfase = [self._desfase_etiquetas(i) for i in range(self.N)]   # (m_i, montaje_ok)
        self.montaje_valido = all(ok for _, ok in self.desfase)
        self.res_sol = self.sol.generar_patron()
        self.res_anular = self.anular.generar_patron()

    # ------------------------------------------------------------------ montaje / cinemática
    def _desfase_etiquetas(self, i: int):
        x = (self.Zs + self.Za) * i / self.N - self.C / (2.0 * math.pi) + self.Zrp / 2.0
        m = round(x)
        return int(m) % self.Zrp, abs(x - m) < 1e-6

    def razones_texto(self) -> str:
        return (f"θ sol {fmt_signo(self.k_sol)} · brazo {fmt_signo(self.k_brazo)} · anular {fmt_signo(self.k_anular)}  (× θ entrada)")

    def estado(self, theta_in_rad: float) -> EstadoPlanetario:
        fs = self.k_sol * theta_in_rad
        fc = self.k_brazo * theta_in_rad
        fa = self.fase_anular0 + self.k_anular * theta_in_rad
        gamma = fc + self.beta
        psi = fs + self.f_s * (gamma - fs)
        centros = self.cd * np.column_stack((np.cos(gamma), np.sin(gamma)))
        return EstadoPlanetario(theta_in_rad, fs, fc, fa, gamma, psi, centros)

    def centros_rodillos_mundo(self, est: EstadoPlanetario):
        """(x, y) de forma (N, Zrp): centro de cada rodillo de cada planeta en el mundo."""
        lx = np.asarray(self.res_sol.pinon_centros_x)[None, :]
        ly = np.asarray(self.res_sol.pinon_centros_y)[None, :]
        c, s = np.cos(est.psi)[:, None], np.sin(est.psi)[:, None]
        return est.centros[:, 0:1] + c * lx - s * ly, est.centros[:, 1:2] + s * lx + c * ly

    # ------------------------------------------------------------------ contactos
    def _par(self, motor, i: int, alfa: float, giro: float, fi_g: float, desfase: int) -> list:
        est = EstadoCinematico(theta_motor_rad=giro, patron_fijo=True, angulo_pinon_rad=giro,
                               centro_pinon=(self.cd * math.cos(alfa), self.cd * math.sin(alfa)),
                               angulo_relativo_generatriz_rad=alfa)
        c, s = math.cos(fi_g), math.sin(fi_g)
        salida = []
        for d in motor.rodillos_en_contacto(alfa, modo_pinon_alterno=True, estado_cinematico=est):
            d = dict(d)
            d["planeta"] = i
            d["indice"] = (d["indice"] + desfase) % self.Zrp
            for clave in ("punto_contacto", "centro_rodillo", "punto_cir"):
                if clave in d:
                    x, y = d[clave]
                    d[clave + "_mundo"] = (c * x - s * y, s * x + c * y)
            salida.append(d)
        return salida

    def contactos(self, est: EstadoPlanetario):
        """(contactos_sol, contactos_anular). Cada dict es el del engine + 'planeta' y '*_mundo'."""
        cs, ca = [], []
        for i in range(self.N):
            a_s = float(est.gamma[i] - est.fi_sol)
            cs += self._par(self.sol, i, a_s, self.f_s * a_s, est.fi_sol, 0)
            a_a = float(est.gamma[i] - est.fi_anular)
            ca += self._par(self.anular, i, a_a, self.f_a * a_a, est.fi_anular, self.desfase[i][0])
        return cs, ca

    # ------------------------------------------------------------------ informe
    def resumen_html(self) -> str:
        p = self.parametros
        filas = [("Dientes sol / anular (Za = Zs + 2·Zrp)", f"{self.Zs} / {self.Za}"),
                 ("Rodillos por planeta", self.Zrp), ("Planetas", self.N),
                 ("Distancia entre centros sol-planeta", fmt(self.cd, "mm")),
                 ("Diámetro exterior del planeta D_ap", fmt(self.d_ap, "mm")),
                 ("Entrada / bloqueado", f"{p.componente_entrada.value} / {p.componente_bloqueado.value}"),
                 ("Giros relativos", self.razones_texto())]
        cuerpo = "".join(f"<tr><td style='border-bottom:1px solid #999'>{a}</td>"
                         f"<td align='right' style='border-bottom:1px solid #999'><b>{b}</b></td></tr>"
                         for a, b in filas)
        return ("<h2>RPS Design — Planetario</h2><table cellspacing='0' cellpadding='4' width='100%' "
                f"style='border-collapse:collapse'>{cuerpo}</table>")
