# -*- coding: utf-8 -*-
"""
engine/mecanismos_fisicos.py

ADAPTADORES por mecanismo para el régimen de contacto (funciones 36–38). Reutilizan sin cambios la
cinemática existente (SolverCinematico / PlanetarioEngine.estado) y el núcleo común
(`engine.contacto_fisico`). Cada adaptador, para un ángulo de entrada θ (°, el mismo de la línea de
tiempo), entrega:

  - los contactos rodillo–perfil REALES (separación con signo, punto y normal en el MUNDO),
  - la matriz J (contactos × coordenadas de deflexión) y el significado de cada coordenada,
  - el cálculo de momentos/fuerzas por componente a partir de las fuerzas normales.

El estado cinemático PRESCRITO no se modifica nunca: las coordenadas q son deflexiones elásticas
pequeñas alrededor de él (resultado físico separado, función 38).

Convención: normal n del material del engranaje hacia el rodillo. Fuerza sobre el rodillo = +F·n,
sobre el engranaje = −F·n (F ≥ 0). Momentos positivos antihorarios (+z). Unidades: mm, N, N·mm.
Carga externa de la salida: par "resistente" T (N·m; en la cremallera fuerza en N) => Q = −T.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from config.data_structures import Componente
from engine import math_utils as mu
from engine.cinematica_engine import SolverCinematico
from engine.contacto_fisico import PerfilDentado

MARGEN_REGISTRO = 0.5        # se registran contactos con separación < MARGEN_REGISTRO·r_rodillo


def _cruz(ax, ay, bx, by):
    return ax * by - ay * bx


@dataclass
class ContactosMuestra:
    clave: list                     # identificador estable por contacto ("Sol·P1·R3·D5")
    engranaje: list                 # nombre del perfil
    planeta: np.ndarray             # índice del piñón/planeta (0 si hay uno solo)
    rodillo: np.ndarray
    diente: np.ndarray
    gap: np.ndarray
    px: np.ndarray
    py: np.ndarray
    nx: np.ndarray
    ny: np.ndarray
    J: np.ndarray                   # (n, m)
    cx_eng: np.ndarray              # centro del engranaje (para el sistema local radial/tangencial)
    cy_eng: np.ndarray
    lineal: np.ndarray              # True si el engranaje es una cremallera
    ccx: np.ndarray = None          # centro del piñón/planeta dueño del rodillo
    ccy: np.ndarray = None

    @property
    def n(self) -> int:
        return len(self.clave)

    def seleccion(self, mask) -> "ContactosMuestra":
        mask = np.asarray(mask, bool)
        return ContactosMuestra([c for c, m in zip(self.clave, mask) if m],
                                [c for c, m in zip(self.engranaje, mask) if m],
                                *(getattr(self, a)[mask] for a in
                                  ("planeta", "rodillo", "diente", "gap", "px", "py", "nx", "ny")),
                                self.J[mask], self.cx_eng[mask], self.cy_eng[mask], self.lineal[mask],
                                self.ccx[mask], self.ccy[mask])

    def componentes_locales(self, F):
        """(Fr, Ft) de la fuerza sobre el ENGRANAJE (−F n) en su sistema local: radial hacia afuera desde el
        centro del engranaje y tangencial antihoraria; en la cremallera radial = +Y, tangencial = +X."""
        fx, fy = -F * self.nx, -F * self.ny
        rx, ry = self.px - self.cx_eng, self.py - self.cy_eng
        rn = np.hypot(rx, ry)
        rn = np.where(rn > 1e-12, rn, 1.0)
        ex, ey = np.where(self.lineal, 0.0, rx / rn), np.where(self.lineal, 1.0, ry / rn)
        tx, ty = -ey, ex
        return fx * ex + fy * ey, fx * tx + fy * ty


def _contactos_vacios(m: int) -> ContactosMuestra:
    z = np.zeros(0)
    return ContactosMuestra([], [], z.astype(int), z.astype(int), z.astype(int), z, z, z, z, z,
                            np.zeros((0, m)), z, z, z.astype(bool), z, z)


def _unir(partes: list, m: int) -> ContactosMuestra:
    partes = [p for p in partes if p.n]
    if not partes:
        return _contactos_vacios(m)
    cat = lambda a: np.concatenate([getattr(p, a) for p in partes])
    return ContactosMuestra(sum((p.clave for p in partes), []), sum((p.engranaje for p in partes), []),
                            *(cat(a) for a in ("planeta", "rodillo", "diente", "gap", "px", "py", "nx", "ny")),
                            np.vstack([p.J for p in partes]), cat("cx_eng"), cat("cy_eng"), cat("lineal"),
                            cat("ccx"), cat("ccy"))


@dataclass
class Componente_:
    nombre: str
    vinculo: str                    # "Entrada (prescrita)" | "Salida (carga)" | "Fijo" | "Libre (equilibrio)"
    tipo: str = "giro"              # "giro" | "traslación"


@dataclass
class AdaptadorBase:
    """Interfaz común. `m` coordenadas de deflexión; la 0 es SIEMPRE la de la salida."""
    nombre_sistema: str = ""
    coordenadas: list = field(default_factory=list)       # [(nombre, "giro"|"traslación")]
    entrada: str = "Piñón"
    salida: str = ""
    lineal_salida: bool = False
    signo_entrada: float = 1.0      # dφ(giro físico +z del componente de entrada)/dθ(perfil)

    @property
    def m(self) -> int:
        return len(self.coordenadas)

    # -- a implementar ---------------------------------------------------------------------------
    def contactos(self, theta_deg: float) -> ContactosMuestra:
        raise NotImplementedError

    def componentes(self) -> list:
        raise NotImplementedError

    def salida_desde_entrada(self, theta_deg: float) -> float:
        """Coordenada cinemática de la salida (° o mm) para el ángulo de entrada θ (°)."""
        raise NotImplementedError

    def momentos(self, theta_deg: float, c: ContactosMuestra, F) -> dict:
        """{componente: momento (N·mm) o fuerza (N) que ejercen los contactos sobre él}."""
        raise NotImplementedError

    def unidad_salida(self) -> str:
        return "mm" if self.lineal_salida else "°"

    def relacion(self, theta_deg: float, h: float = 1e-3) -> float:
        """d(salida)/d(θ entrada) (° /° o mm/°), por diferencias centradas sobre el MAPA cinemático (no por tiempo)."""
        return (self.salida_desde_entrada(theta_deg + h) - self.salida_desde_entrada(theta_deg - h)) / (2 * h)

    def tasas(self, theta_deg: float) -> np.ndarray:
        """R_c = d(coordenada absoluta c)/dθ [rad/rad o mm/rad] en la cinemática prescrita (para la dinámica:
        posición absoluta de cada cuerpo = cinemática(θ) + deflexión q_c)."""
        r = self.relacion(theta_deg)
        return np.array([r * 180.0 / math.pi if self.lineal_salida else r] + [0.0] * (self.m - 1))

    def Q_salida(self, carga_salida: float) -> np.ndarray:
        """Carga generalizada: par resistente T (N·m -> N·mm) o fuerza resistente (N) en la salida."""
        Q = np.zeros(self.m)
        Q[0] = -(carga_salida if self.lineal_salida else carga_salida * 1000.0)
        return Q

    def validar_muestra(self, theta_deg: float) -> str:
        return ""

    def par_motor(self, momentos: dict, carga_entrada: float = 0.0) -> float:
        """Par (N·m) conjugado de la coordenada prescrita θ que debe aportar el accionamiento:
        equilibra el momento de los contactos sobre la entrada y la carga aplicada en el eje de entrada."""
        return -self.signo_entrada * momentos.get(self.entrada, 0.0) / 1000.0 + carga_entrada


# ======================================================================
# Epitrocoidal / Hipotrocoidal
# ======================================================================
class AdaptadorEpiHipo(AdaptadorBase):
    def __init__(self, motor, res, alterno: bool, nombre: str):
        super().__init__(nombre_sistema=nombre)
        self.motor, self.res, self.alterno = motor, res, bool(alterno)
        self.solver = SolverCinematico(motor.contexto)
        self.perfil = PerfilDentado(motor, "Engranaje" if not motor.contexto.perfil_interior else "Anular")
        self.lx, self.ly = np.asarray(res.pinon_centros_x, float), np.asarray(res.pinon_centros_y, float)
        self.salida = "Brazo (portapiñón)" if self.alterno else self.perfil.nombre
        self.coordenadas = [(f"Δ{self.salida}", "giro")]

    def _estado(self, theta_deg):
        return self.solver.resolver("angular", True, self.alterno, theta_deg, 0.0)

    def salida_desde_entrada(self, theta_deg):
        e = self._estado(theta_deg)
        return math.degrees(e.angulo_relativo_generatriz_rad if self.alterno else e.angulo_patron_rad)

    def componentes(self):
        if self.alterno:
            return [Componente_(self.perfil.nombre, "Fijo"), Componente_("Piñón", "Entrada (prescrita)"),
                    Componente_(self.salida, "Salida (carga)")]
        return [Componente_("Piñón", "Entrada (prescrita)"), Componente_(self.perfil.nombre, "Salida (carga)")]

    def contactos(self, theta_deg):
        e = self._estado(theta_deg)
        cx, cy = e.centro_pinon
        s = e.angulo_pinon_rad
        wx = cx + math.cos(s) * self.lx - math.sin(s) * self.ly
        wy = cy + math.sin(s) * self.lx + math.cos(s) * self.ly
        a = 0.0 if e.patron_fijo else e.angulo_patron_rad
        px, py = mu.rotar(wx, wy, -a)
        d = self.perfil.consultar(px, py)
        sel = d["gap"] < MARGEN_REGISTRO * self.perfil.r
        idx = np.nonzero(sel)[0]
        Px, Py = mu.rotar(d["px"][sel], d["py"][sel], a)
        Nx, Ny = mu.rotar(d["nx"][sel], d["ny"][sel], a)
        Px, Py, Nx, Ny = (np.asarray(v, float) for v in (Px, Py, Nx, Ny))
        if self.alterno:                 # salida = brazo: el centro del piñón orbita, su orientación absoluta no
            J = -((-cy) * Nx + cx * Ny)          # −(ẑ×C)·n
        else:                            # salida = engranaje que gira alrededor del origen
            J = Px * Ny - Py * Nx
        n = idx.size
        Zg = self.motor.parametros.numero_dientes
        return ContactosMuestra([f"R{k}·D{int(j) % Zg}" for k, j in zip(idx, d["diente"][sel])],
                                [self.perfil.nombre] * n, np.zeros(n, int), idx, d["diente"][sel] % Zg,
                                d["gap"][sel], Px, Py, Nx, Ny, J.reshape(n, 1), np.zeros(n), np.zeros(n),
                                np.zeros(n, bool), np.full(n, cx), np.full(n, cy))

    def momentos(self, theta_deg, c, F):
        e = self._estado(theta_deg)
        cx, cy = e.centro_pinon
        F = np.nan_to_num(np.asarray(F, float))
        fx, fy = F * c.nx, F * c.ny                       # sobre los rodillos
        m_eng = float(np.sum(_cruz(c.px, c.py, -fx, -fy)))
        m_pin = float(np.sum(_cruz(c.px - cx, c.py - cy, fx, fy)))
        out = {"Piñón": m_pin, self.perfil.nombre: m_eng}
        if self.alterno:
            out[self.salida] = float(_cruz(cx, cy, fx.sum(), fy.sum()))
        return out


# ======================================================================
# Trocoidal (cremallera)
# ======================================================================
class AdaptadorTrocoidal(AdaptadorBase):
    def __init__(self, motor, res, alterno: bool):
        super().__init__(nombre_sistema="Trocoidal", lineal_salida=True, signo_entrada=-1.0)   # angulo_pinon = −θ
        self.motor, self.res, self.alterno = motor, res, bool(alterno)
        self.solver = SolverCinematico(motor.contexto)
        self.perfil = PerfilDentado(motor, "Cremallera")
        self.prrp = float(motor.rodillo.prrp)
        self.L = float(motor.parametros.longitud_cremallera)
        self.lx, self.ly = np.asarray(res.pinon_centros_x, float), np.asarray(res.pinon_centros_y, float)
        self.salida = "Carro (piñón)" if self.alterno else "Cremallera"
        self.coordenadas = [(f"Δx {self.salida}", "traslación")]

    def x_desde_theta(self, theta_deg):
        return math.radians(theta_deg) * self.prrp          # x = prrp·θ (θ en rad), función existente

    def _estado(self, theta_deg):
        return self.solver.resolver("lineal", True, self.alterno, theta_deg, self.x_desde_theta(theta_deg))

    def validar_muestra(self, theta_deg):
        x = self.x_desde_theta(theta_deg)
        if x < -1e-9 or x > self.L + 1e-9:
            return f"x = {x:.4f} mm fuera del recorrido 0 ≤ x ≤ L = {self.L:g} mm"
        return ""

    def salida_desde_entrada(self, theta_deg):
        e = self._estado(theta_deg)
        return float(e.centro_pinon[0] if self.alterno else e.traslacion_patron[0])

    def componentes(self):
        if self.alterno:
            return [Componente_("Cremallera", "Fijo", "traslación"), Componente_("Piñón", "Entrada (prescrita)"),
                    Componente_(self.salida, "Salida (carga)", "traslación")]
        return [Componente_("Piñón", "Entrada (prescrita)"), Componente_("Cremallera", "Salida (carga)", "traslación")]

    def contactos(self, theta_deg):
        e = self._estado(theta_deg)
        cx, cy = e.centro_pinon
        s = e.angulo_pinon_rad
        wx = cx + math.cos(s) * self.lx - math.sin(s) * self.ly
        wy = cy + math.sin(s) * self.lx + math.cos(s) * self.ly
        dx = 0.0 if e.patron_fijo else e.traslacion_patron[0]
        d = self.perfil.consultar(wx - dx, wy)
        sel = d["gap"] < MARGEN_REGISTRO * self.perfil.r
        # solo dientes que existen físicamente sobre la cremallera [0, L] (más medio paso)
        xd = d["diente"] * self.perfil.paso
        sel &= (xd >= -self.perfil.paso) & (xd <= self.L + self.perfil.paso)
        idx = np.nonzero(sel)[0]
        Px, Py = d["px"][sel] + dx, d["py"][sel]
        Nx, Ny = d["nx"][sel], d["ny"][sel]
        J = -Nx if self.alterno else Nx
        n = idx.size
        return ContactosMuestra([f"R{k}·D{int(j)}" for k, j in zip(idx, d["diente"][sel])], ["Cremallera"] * n,
                                np.zeros(n, int), idx, d["diente"][sel], d["gap"][sel], Px, Py, Nx, Ny,
                                J.reshape(n, 1), np.zeros(n), np.zeros(n), np.ones(n, bool),
                                np.full(n, cx), np.full(n, cy))

    def Q_salida(self, carga_salida):
        return np.array([-float(carga_salida)])

    def momentos(self, theta_deg, c, F):
        e = self._estado(theta_deg)
        cx, cy = e.centro_pinon
        F = np.nan_to_num(np.asarray(F, float))
        fx, fy = F * c.nx, F * c.ny
        out = {"Piñón": float(np.sum(_cruz(c.px - cx, c.py - cy, fx, fy))),
               "Cremallera": float(np.sum(-fx))}
        if self.alterno:
            out[self.salida] = float(np.sum(fx))
        return out


# ======================================================================
# Planetario (sol–planetas y anular–planetas)
# ======================================================================
class AdaptadorPlanetario(AdaptadorBase):
    def __init__(self, eng):
        super().__init__(nombre_sistema="Planetario")
        self.e = eng
        p = eng.parametros
        self.c_entrada = Componente(p.componente_entrada)
        self.c_bloq = Componente(p.componente_bloqueado)
        self.c_salida = ({Componente.SOL, Componente.BRAZO, Componente.ANULAR} - {self.c_entrada, self.c_bloq}).pop()
        self.entrada, self.salida = self.c_entrada.value, self.c_salida.value
        self.p_sol = PerfilDentado(eng.sol, "Sol")
        self.p_anu = PerfilDentado(eng.anular, "Anular")
        self.coordenadas = [(f"Δ{self.salida}", "giro")] + [(f"Δψ planeta {i + 1}", "giro") for i in range(eng.N)]

    def salida_desde_entrada(self, theta_deg):
        k = {Componente.SOL: self.e.k_sol, Componente.BRAZO: self.e.k_brazo, Componente.ANULAR: self.e.k_anular}
        return k[self.c_salida] * theta_deg

    def tasas(self, theta_deg, h=1e-3):
        e1, e0 = self.e.estado(math.radians(theta_deg + h)), self.e.estado(math.radians(theta_deg - h))
        dpsi = (e1.psi - e0.psi) / math.radians(2 * h)
        return np.concatenate(([self.relacion(theta_deg)], dpsi))

    def componentes(self):
        out = []
        for c in (Componente.SOL, Componente.BRAZO, Componente.ANULAR):
            v = ("Entrada (prescrita)" if c == self.c_entrada else "Fijo" if c == self.c_bloq else "Salida (carga)")
            out.append(Componente_(c.value, v))
        out += [Componente_(f"Planeta {i + 1}", "Libre (equilibrio)") for i in range(self.e.N)]
        return out

    def contactos(self, theta_deg):
        e = self.e
        est = e.estado(math.radians(theta_deg))
        rx, ry = e.centros_rodillos_mundo(est)                       # (N, Zrp)
        partes = []
        for perfil, fi, comp in ((self.p_sol, est.fi_sol, Componente.SOL), (self.p_anu, est.fi_anular, Componente.ANULAR)):
            px, py = mu.rotar(rx.ravel(), ry.ravel(), -fi)
            d = perfil.consultar(px, py)
            sel = d["gap"] < MARGEN_REGISTRO * perfil.r
            idx = np.nonzero(sel)[0]
            pl, kk = idx // e.Zrp, idx % e.Zrp
            Px, Py = (np.asarray(v, float) for v in mu.rotar(d["px"][sel], d["py"][sel], fi))
            Nx, Ny = (np.asarray(v, float) for v in mu.rotar(d["nx"][sel], d["ny"][sel], fi))
            Cx, Cy = est.centros[pl, 0], est.centros[pl, 1]
            n = idx.size
            J = np.zeros((n, self.m))
            vgx = vgy = 0.0
            if comp == self.c_salida:                                    # el engranaje es la salida: gira
                vgx, vgy = -Py, Px
            vpx = vpy = np.zeros(n)
            if self.c_salida == Componente.BRAZO:                         # centro del planeta arrastrado
                vpx, vpy = -Cy, Cx
            J[:, 0] = (vgx - vpx) * Nx + (vgy - vpy) * Ny
            J[np.arange(n), 1 + pl] = -((-(Py - Cy)) * Nx + (Px - Cx) * Ny)
            Zg = perfil.motor.parametros.numero_dientes
            dj = d["diente"][sel] % Zg
            partes.append(ContactosMuestra([f"{perfil.nombre}·P{p + 1}·R{k}·D{j}" for p, k, j in zip(pl, kk, dj)],
                                           [perfil.nombre] * n, pl, kk, dj, d["gap"][sel], Px, Py, Nx, Ny, J,
                                           np.zeros(n), np.zeros(n), np.zeros(n, bool), Cx, Cy))
        return _unir(partes, self.m)

    def momentos(self, theta_deg, c, F):
        e = self.e
        est = e.estado(math.radians(theta_deg))
        F = np.nan_to_num(np.asarray(F, float))
        fx, fy = F * c.nx, F * c.ny                                   # sobre los rodillos (planetas)
        es_sol = np.array([g == "Sol" for g in c.engranaje], bool)
        out = {"Sol": float(np.sum(_cruz(c.px[es_sol], c.py[es_sol], -fx[es_sol], -fy[es_sol]))),
               "Anular": float(np.sum(_cruz(c.px[~es_sol], c.py[~es_sol], -fx[~es_sol], -fy[~es_sol])))}
        brazo = 0.0
        for i in range(e.N):
            mi = c.planeta == i
            Cx, Cy = est.centros[i]
            out[f"Planeta {i + 1}"] = float(np.sum(_cruz(c.px[mi] - Cx, c.py[mi] - Cy, fx[mi], fy[mi])))
            brazo += float(_cruz(Cx, Cy, fx[mi].sum(), fy[mi].sum()))
        out["Brazo"] = brazo
        return out


# ======================================================================
def adaptador_para(sistema: str, motor, res=None, alterno: bool = False):
    """Fábrica: `sistema` = clave de proyecto (EPITROCOIDAL, HIPOTROCOIDAL, TROCOIDAL, PLANETARIO)."""
    if sistema == "PLANETARIO":
        return AdaptadorPlanetario(motor)
    if res is None:
        res = motor.generar_patron()
    if sistema == "TROCOIDAL":
        return AdaptadorTrocoidal(motor, res, alterno)
    return AdaptadorEpiHipo(motor, res, alterno, sistema.capitalize())
