# -*- coding: utf-8 -*-
"""
engine/contacto_fisico.py

NÚCLEO COMÚN del régimen de contacto (funciones 24–35 y 53–55). Sin Qt. Dos piezas:

1) `PerfilDentado`: detector GEOMÉTRICO sobre el perfil trocoidal REAL (curva_offset de los engines
   Epi/Hipo/Cremallera). Para cada centro de rodillo (en el marco del patrón) da:
     - separación con signo  g = s·|c − p| − r   (g > 0 separado, g ≈ 0 contacto, g < 0 penetración),
     - punto de contacto p (punto del flanco más cercano), normal unitaria n (del material del engranaje
       hacia el lado libre, donde vive el centro del rodillo) e índice de diente.
   El signo s se obtiene de la generatriz: el perfil es la equidistante a distancia r de la trayectoria
   del centro del rodillo, así que n = (g(θ*) − p)/r apunta exactamente al lado libre.

2) `resolver_equilibrio`: equilibrio CUASIESTÁTICO con contacto UNILATERAL normal sin fricción.
   Coordenadas generalizadas q (pequeñas deflexiones elásticas alrededor de la posición cinemática
   prescrita); penetración elástica de cada contacto δ_i = −g_i + J_i·q; fuerzas F_i ≥ 0.
     Equilibrio:      Σ_i F_i J_i = Q      (Q = cargas externas generalizadas)
     · Penalización elástica unilateral: F_i = k·max(0, δ_i). Es el mínimo de la energía convexa
       E(q) = ½k Σ max(0, δ_i)² − Q·q  -> conjunto activo + Newton con búsqueda lineal.
       Reparto entre contactos simultáneos por COMPATIBILIDAD y rigidez (no se divide la carga).
     · Unilateral rígido (complementariedad): F ≥ 0, g ≥ 0, F·g = 0 sin rigidez. Si la solución no es
       única (hiperestático, o precarga entre flancos opuestos) el resultado es INDETERMINADO.
     · Sin rigidez definida o sin reparto habilitado -> análisis rígido.
   La deflexión q es solo elástica (modelo simplificado identificado): no hay masas ni inercias, así que
   NO se resuelven impactos, vibraciones ni dinámica transitoria.

Unidades internas: mm, N, N·mm. J tiene unidades de mm (coordenada de giro) o adimensional (traslación).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from engine import math_utils as mu

# Estados de un equilibrio
DETERMINADO = "Determinado"
INDETERMINADO = "Indeterminado"
SIN_EQUILIBRIO = "Sin equilibrio"
NO_CONVERGIDO = "No convergido"
GEOMETRICO = "Solo geometría"

MODELO_RIGIDO = "Equilibrio unilateral / complementariedad"
MODELO_PENALIZACION = "Penalización elástica unilateral"
MODELO_GEOMETRICO = "Solo análisis geométrico"
MODELOS = (MODELO_RIGIDO, MODELO_PENALIZACION, MODELO_GEOMETRICO)


# ======================================================================
# 1) Detector geométrico
# ======================================================================
class PerfilDentado:
    """Perfil dentado periódico de un engine (Epitrocoidal, Hipotrocoidal o Cremallera) en el marco del
    PATRÓN (el mismo que dibuja la vista: incluye la rotación de vista del engine)."""

    N_BASE = 241
    PASADAS = 6
    N_ZOOM = 15

    def __init__(self, motor, nombre: str = "engranaje"):
        self.motor = motor
        self.nombre = nombre
        self.lineal = motor.contexto.tipo_ensamble == "lineal"
        self.rv = math.radians(motor.ROTACION_VISTA_SIMULACION_GRADOS)
        self.r = float(motor.radio_rodillo)
        self.th_lim = float(motor.theta_lim)
        self.paso = float(motor.calcular_paso()) if self.lineal else 2.0 * math.pi / motor.parametros.numero_dientes
        self.th = np.linspace(-self.th_lim, self.th_lim, self.N_BASE)
        self.ox, self.oy = self._offset(self.th)

    # -- curvas exactas en el marco local del diente 0 ------------------------------------------
    def _offset(self, th):
        x, y = self.motor.curva_offset(th)
        return mu.rotar(np.asarray(x, float), np.asarray(y, float), self.rv)

    def _generatriz(self, th):
        x, y = self.motor.curva_generatriz(th)
        return mu.rotar(np.asarray(x, float), np.asarray(y, float), self.rv)

    def _normal_local(self, th):
        qx, qy = self._offset(th)
        gx, gy = self._generatriz(th)
        vx, vy = gx - qx, gy - qy
        nv = np.hypot(vx, vy)
        nv = np.where(nv > 1e-15, nv, 1.0)
        return vx / nv, vy / nv

    def _a_local(self, px, py, j):
        if self.lineal:
            return px - j * self.paso, py
        return mu.rotar(px, py, -j * self.paso)

    def _de_local(self, x, y, j, vector=False):
        if self.lineal:
            return (x, y) if vector else (x + j * self.paso, y)
        return mu.rotar(x, y, j * self.paso)

    # -- consulta -------------------------------------------------------------------------------
    def consultar(self, px, py) -> dict:
        """px, py: centros de rodillo en el marco del patrón (arrays 1-D). Devuelve arrays por rodillo."""
        px, py = np.atleast_1d(np.asarray(px, float)), np.atleast_1d(np.asarray(py, float))
        n = px.size
        if n == 0:
            vacio = np.zeros(0)
            return dict(gap=vacio, px=vacio, py=vacio, nx=vacio, ny=vacio, diente=np.zeros(0, int),
                        theta=vacio, borde=np.zeros(0, bool))
        semilla = np.round(px / self.paso) if self.lineal else np.round(np.arctan2(py, px) / self.paso)
        semilla = semilla.astype(int)
        mejor_d = np.full(n, np.inf)
        mejor_j = semilla.copy()
        mejor_k = np.zeros(n, int)
        for dj in (-1, 0, 1):
            j = semilla + dj
            lx, ly = self._a_local(px, py, j)
            d2 = (self.ox[None, :] - lx[:, None]) ** 2 + (self.oy[None, :] - ly[:, None]) ** 2
            k = np.argmin(d2, axis=1)
            dk = d2[np.arange(n), k]
            mejor = dk < mejor_d
            mejor_d[mejor], mejor_j[mejor], mejor_k[mejor] = dk[mejor], j[mejor], k[mejor]
        lx, ly = self._a_local(px, py, mejor_j)
        # Refinamiento por ZOOM sobre la curva exacta (vectorizado sobre los rodillos)
        h = self.th[1] - self.th[0]
        t0 = self.th[mejor_k]
        lo = np.maximum(t0 - h, -self.th_lim)
        hi = np.minimum(t0 + h, self.th_lim)
        for _ in range(self.PASADAS):
            ts = lo[:, None] + (hi - lo)[:, None] * np.linspace(0.0, 1.0, self.N_ZOOM)[None, :]
            zx, zy = self._offset(ts)
            d2 = (zx - lx[:, None]) ** 2 + (zy - ly[:, None]) ** 2
            k = np.argmin(d2, axis=1)
            paso = (hi - lo) / (self.N_ZOOM - 1)
            tk = ts[np.arange(n), k]
            lo = np.maximum(tk - paso, -self.th_lim)
            hi = np.minimum(tk + paso, self.th_lim)
        th = tk
        qx, qy = self._offset(th)
        gx, gy = self._generatriz(th)
        vx, vy = gx - qx, gy - qy                      # normal * r (hacia el lado libre)
        nv = np.hypot(vx, vy)
        nv = np.where(nv > 1e-15, nv, 1.0)
        nx, ny = vx / nv, vy / nv
        dx, dy = lx - qx, ly - qy
        dist = np.hypot(dx, dy)
        signo = np.where(dx * nx + dy * ny >= 0.0, 1.0, -1.0)
        borde = np.abs(np.abs(th) - self.th_lim) < 1e-9
        # En la arista (cresta, esquina convexa entre el flanco de este diente y el del vecino) el centro está
        # FUERA del material si queda del lado libre de cualquiera de los dos flancos; la normal útil es la
        # dirección punto->centro.
        if np.any(borde):
            b = np.nonzero(borde)[0]
            jv = mejor_j[b] + np.where(th[b] > 0, 1, -1)
            tv = -th[b]
            vx2, vy2 = self._normal_local(tv)
            # normal del flanco vecino llevada al marco local del diente actual
            vx2, vy2 = self._de_local(vx2, vy2, jv - mejor_j[b], vector=True)
            fuera = (dx[b] * vx2 + dy[b] * vy2) >= 0.0
            signo[b] = np.where(fuera | (signo[b] > 0), 1.0, -1.0)
            dd = np.where(dist > 1e-15, dist, 1.0)
            nx = np.where(borde, signo * dx / dd, nx)
            ny = np.where(borde, signo * dy / dd, ny)
        gap = signo * dist - self.r
        Px, Py = self._de_local(qx, qy, mejor_j)
        Nx, Ny = self._de_local(nx, ny, mejor_j, vector=True)
        return dict(gap=gap, px=np.asarray(Px), py=np.asarray(Py), nx=np.asarray(Nx), ny=np.asarray(Ny),
                    diente=mejor_j, theta=th, borde=borde)


# ======================================================================
# 2) Solucionador de equilibrio unilateral
# ======================================================================
@dataclass
class Equilibrio:
    estado: str
    F: np.ndarray                       # N (NaN si indeterminado)
    q: np.ndarray                       # deflexiones generalizadas (rad o mm)
    residuo: np.ndarray                 # J^T F − Q por coordenada (N·mm o N)
    iteraciones: int = 0
    mensaje: str = ""
    delta_max: float = 0.0              # aproximación elástica máxima (mm)
    penetracion_geom: float = 0.0       # penetración geométrica previa (mm, ≥ 0)
    activos: np.ndarray = field(default_factory=lambda: np.zeros(0, bool))


def _nnls(A: np.ndarray, b: np.ndarray, max_iter: int = 500) -> np.ndarray:
    """min ||A x − b|| con x ≥ 0 (Lawson–Hanson). A: (m, n)."""
    m, n = A.shape
    x = np.zeros(n)
    P = np.zeros(n, bool)
    w = A.T @ (b - A @ x)
    tol = 1e-12 * max(1.0, np.abs(A).max() if A.size else 1.0) * max(1.0, np.abs(b).max() if b.size else 1.0)
    it = 0
    while (~P).any() and w[~P].max(initial=-np.inf) > tol and it < max_iter:
        it += 1
        j = int(np.argmax(np.where(~P, w, -np.inf)))
        P[j] = True
        while True:
            z = np.zeros(n)
            z[P] = np.linalg.lstsq(A[:, P], b, rcond=None)[0]
            if (z[P] > 0).all():
                break
            mask = P & (z <= 0)
            alfa = np.min(x[mask] / (x[mask] - z[mask] + 1e-300))
            x = x + alfa * (z - x)
            P &= x > 1e-14
        x = z
        w = A.T @ (b - A @ x)
    return x


def _unicidad(Jc: np.ndarray, F: np.ndarray) -> tuple[bool, str]:
    """¿Es única la solución F ≥ 0 de Jc^T F = Q? Jc: (nc, m)."""
    nc = Jc.shape[0]
    if nc == 0:
        return True, ""
    rango = np.linalg.matrix_rank(Jc, tol=1e-9 * max(1.0, np.abs(Jc).max()))
    nulidad = nc - rango
    if nulidad == 0:
        return True, ""
    _, _, vt = np.linalg.svd(Jc.T)
    base = vt[rango:]                                  # filas: base del núcleo de Jc^T
    Z = F <= 1e-12 * max(1.0, np.abs(F).max())
    if nulidad == 1:
        b = base[0]
        if not Z.any() or (b[Z] >= -1e-12).all() or (-b[Z] >= -1e-12).all():
            return False, f"hiperestático: {nc} contactos candidatos con rango {rango} (precarga o reparto no determinables sin rigidez)"
        return True, ""
    return False, f"hiperestático: {nc} contactos candidatos con rango {rango}; el reparto exige compatibilidad (rigidez normal)"


def resolver_equilibrio(gap, J, Q, modelo: str = MODELO_PENALIZACION, rigidez: float = 0.0,
                        tol_gap: float = 1e-3, tol_q=1e-6, max_iter: int = 200, reparto: bool = True,
                        gap_rate=None, amortiguamiento: float = 0.0) -> Equilibrio:
    """gap (n,) mm · J (n, m) · Q (m,) · tol_q escalar o (m,) en las unidades de Q.
    `gap_rate` (mm/s, prescrito por la cinemática) + `amortiguamiento` (N·s/mm): término viscoso normal
    solo en penalización; se anula solo cuando las velocidades relativas son nulas (equilibrio estático)."""
    g = np.asarray(gap, float).ravel()
    J = np.asarray(J, float).reshape(g.size, -1) if g.size else np.zeros((0, np.size(Q)))
    Q = np.asarray(Q, float).ravel()
    m = Q.size
    tol = np.broadcast_to(np.asarray(tol_q, float), (m,)).astype(float)
    n = g.size
    pen0 = float(max(0.0, -(g[g < -tol_gap]).min())) if np.any(g < -tol_gap) else 0.0
    nan = np.full(n, np.nan)

    if modelo == MODELO_GEOMETRICO:
        return Equilibrio(GEOMETRICO, nan, np.zeros(m), np.full(m, np.nan), 0,
                          "modelo geométrico: no se calculan fuerzas", 0.0, pen0, g <= tol_gap)

    usar_penal = modelo == MODELO_PENALIZACION and rigidez > 0 and reparto
    if not usar_penal:
        motivo = ""
        if modelo == MODELO_PENALIZACION and rigidez <= 0:
            motivo = "rigidez normal no definida: análisis rígido; "
        elif modelo == MODELO_PENALIZACION and not reparto:
            motivo = "reparto entre contactos desactivado: análisis rígido; "
        return _rigido(g, J, Q, tol, tol_gap, pen0, motivo)

    # ---- penalización elástica unilateral ----
    k = float(rigidez)
    ge = g.copy()           # separaciones reales (la tolerancia solo clasifica el estado del contacto)
    if gap_rate is not None and amortiguamiento > 0:
        ge = ge + amortiguamiento * np.asarray(gap_rate, float).ravel() / k
    q = np.zeros(m)

    def energia(qq):
        d = np.maximum(0.0, -ge + J @ qq)
        return 0.5 * k * float(d @ d) - float(Q @ qq)

    it = 0
    for it in range(1, max_iter + 1):
        d = -ge + J @ q
        act = d > 0
        F = k * np.where(act, d, 0.0)
        r = J.T @ F - Q
        if np.all(np.abs(r) <= tol):
            return Equilibrio(DETERMINADO, F, q, r, it, "", float(d[act].max(initial=0.0)), pen0, act)
        Ja = J[act]
        H = k * (Ja.T @ Ja) if act.any() else np.zeros((m, m))
        w, V = np.linalg.eigh(H) if m else (np.zeros(0), np.zeros((0, 0)))
        escala = max(w.max(initial=0.0), 1e-300)
        rango = w > 1e-10 * escala if escala > 1e-300 else np.zeros(m, bool)
        rc = V.T @ r
        r_null = V[:, ~rango] @ rc[~rango]
        if np.any(np.abs(r_null) > tol):
            dirn = -r_null
            Jd = J @ dirn
            cand = (~act) & (Jd > 1e-15)
            if not cand.any():
                return Equilibrio(SIN_EQUILIBRIO, nan, q, r, it,
                                  "ningún contacto puede equilibrar la carga en el sentido requerido "
                                  "(separación, pérdida de contacto o holgura)", 0.0, pen0, act)
            s = (ge[cand] - (J @ q)[cand]) / Jd[cand]
            q = q + (max(float(s.min()), 0.0) * (1 + 1e-9) + 1e-15) * dirn
            continue
        paso = -(V[:, rango] @ (rc[rango] / w[rango]))
        e0, alfa, pendiente = energia(q), 1.0, float(r @ paso)       # pendiente < 0 (dirección de descenso)
        while alfa > 1e-12 and energia(q + alfa * paso) > e0 + 1e-4 * alfa * pendiente:
            alfa *= 0.5
        q = q + alfa * paso
    d = -ge + J @ q
    act = d > 0
    F = k * np.where(act, d, 0.0)
    r = J.T @ F - Q
    if np.all(np.abs(r) <= tol):
        return Equilibrio(DETERMINADO, F, q, r, it, "", float(d[act].max(initial=0.0)), pen0, act)
    return Equilibrio(NO_CONVERGIDO, F, q, r, it,
                      f"sin convergencia en {max_iter} iteraciones (residuo máx. {np.abs(r).max():.3g})",
                      float(d[act].max(initial=0.0)), pen0, act)


def _rigido(g, J, Q, tol, tol_gap, pen0, motivo) -> Equilibrio:
    n, m = J.shape
    cand = g <= tol_gap
    F = np.zeros(n)
    if not cand.any():
        if np.all(np.abs(Q) <= tol):
            return Equilibrio(DETERMINADO, F, np.zeros(m), -Q, 0, motivo + "sin carga y sin contactos", 0.0, pen0, cand)
        return Equilibrio(SIN_EQUILIBRIO, np.full(n, np.nan), np.zeros(m), -Q, 0,
                          motivo + "sin contactos: la carga no puede equilibrarse (holgura)", 0.0, pen0, cand)
    Jc = J[cand]
    Fc = _nnls(Jc.T, Q)
    res = Jc.T @ Fc - Q
    if np.any(np.abs(res) > tol):
        return Equilibrio(SIN_EQUILIBRIO, np.full(n, np.nan), np.zeros(m), res, 0,
                          motivo + "los contactos activos no pueden equilibrar la carga en ese sentido", 0.0, pen0, cand)
    unica, porque = _unicidad(Jc, Fc)
    if not unica:
        return Equilibrio(INDETERMINADO, np.full(n, np.nan), np.zeros(m), res, 0, motivo + porque, 0.0, pen0, cand)
    F[cand] = Fc
    return Equilibrio(DETERMINADO, F, np.zeros(m), res, 0, motivo + "isostático", 0.0, pen0, cand)
