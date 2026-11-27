"""Discretización reutilizable; NO sustituye por sí sola el motor de contacto.

Se prueba independientemente. El criterio de punto medio es una estimación
numérica del error de cuerda, no una cota rigurosa de error de toda curva.
"""
from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass
import math
import numpy as np

@dataclass(frozen=True)
class SamplingResult:
    parametros: np.ndarray
    puntos: np.ndarray
    evaluaciones: int
    alcanzado_limite: bool


def uniform(eval_fn:Callable, a:float,b:float,n:int)->SamplingResult:
    if not a<b or not 3<=n<=1000001:
        raise ValueError('Rango o número de muestras inválido')
    ts=np.linspace(a,b,n)
    pts=np.asarray([eval_fn(float(x)) for x in ts],dtype=float)
    if pts.shape!=(n,2) or not np.isfinite(pts).all():
        raise ValueError('Evaluador geométrico inválido')
    return SamplingResult(ts,pts,n,False)


def adaptive(eval_fn:Callable,a:float,b:float,tol_mm:float,
             angle_deg:float,max_samples:int=30001,max_depth:int=18)->SamplingResult:
    """Evalúa error de cuerda y giro aproximado de tangentes por subtramos.

    tol_mm=0 significa discretización al límite de profundidad (no error 0
    garantizado). angle_deg=0 análogo. Requiere pruebas por mecanismo.
    """
    if not a<b or not (0<=tol_mm<=.1) or not (0<=angle_deg<=1) or max_samples<3:
        raise ValueError('Parámetros de discretización inválidos')
    n_eval=0
    def point(t):
        nonlocal n_eval
        z=np.asarray(eval_fn(float(t)),dtype=float)
        if z.shape!=(2,) or not np.isfinite(z).all():
            raise ValueError('Curva no finita')
        n_eval+=1
        return z
    pa=point(a);pb=point(b)
    # Cola ordenada, subdivisión recursiva limitada explícitamente.
    segs=[(a,b,pa,pb,0)]
    result=[(a,pa)];limit_hit=False
    while segs:
        lo,hi,pl,pr,level=segs.pop()
        mid=(lo+hi)*.5;pm=point(mid)
        chord_error=float(np.linalg.norm(pm-(pl+pr)*.5))
        va=pm-pl;vb=pr-pm
        la=np.linalg.norm(va);lb=np.linalg.norm(vb)
        if la>1e-15 and lb>1e-15:
            cosine=float(np.clip(np.dot(va,vb)/(la*lb),-1,1))
            bend=math.degrees(math.acos(cosine))
        else:
            bend=0
        split=(chord_error>tol_mm or bend>angle_deg)
        if split and level<max_depth and n_eval+2<max_samples:
            segs.append((mid,hi,pm,pr,level+1))
            segs.append((lo,mid,pl,pm,level+1))
        else:
            if split:limit_hit=True
            result.append((hi,pr))
    result.sort(key=lambda x:x[0]);ts=np.array([x[0] for x in result]);points=np.array([x[1] for x in result])
    return SamplingResult(ts,points,n_eval,limit_hit)


# ======================================================================================================
# Discretización VECTORIZADA del perfil (la usa BaseEngine.generar_perfil cuando no se pide un n explícito)
# ======================================================================================================
# Significado de las desviaciones (config/data_structures.AjustesDesviacion): «resolución de muestreo de la
# simulación», no la geometría del diente:
#   · lineal  [mm] : distancia máxima entre la curva real y la polilínea muestreada (medida en sondas internas
#                    a 1/4, 1/2 y 3/4 de cada tramo, a la cuerda del tramo).
#   · angular [°]  : giro máximo entre la primera y la segunda mitad de la cuerda de un tramo (misma definición
#                    que `adaptive`).
# Un tramo se subdivide si SUPERA cualquiera de las dos. Es una verificación numérica con sondas, no una cota
# rigurosa para toda curva; el error reportado es el máximo observado en las sondas finales.
import time
from dataclasses import replace

ESTRATEGIA_UNIFORME = "uniforme"
ESTRATEGIA_ADAPTATIVA = "adaptativa"
N_INICIAL = 65            # malla inicial (impar, incluye θ = 0): evita falsos «ya converge» en tramos anchos
PROFUNDIDAD_MAX = 24


@dataclass(frozen=True)
class Politica:
    estrategia: str = ESTRATEGIA_UNIFORME
    n_uniforme: int = 1001
    max_muestras: int = 30001
    tol_mm: float = 0.0003
    ang_grados: float = 0.5
    verificar: bool = False        # medir también el error en la estrategia uniforme (cuesta ~3n evaluaciones)

    @property
    def clave(self) -> tuple:
        """Solo lo que cambia el resultado: la adaptativa no depende de n_uniforme; la uniforme solo de la
        tolerancia si se verifica (para informar el cumplimiento)."""
        if self.estrategia == ESTRATEGIA_ADAPTATIVA:
            return (self.estrategia, int(self.max_muestras), float(self.tol_mm), float(self.ang_grados))
        if self.verificar:
            return (self.estrategia, int(self.n_uniforme), True, float(self.tol_mm), float(self.ang_grados))
        return (self.estrategia, int(self.n_uniforme), False)


@dataclass(frozen=True)
class MuestreoInfo:
    estrategia: str
    n_muestras: int
    n_solicitado: int | None       # uniforme: lo configurado; adaptativa: el límite
    n_evaluaciones: int
    tiempo_s: float                # medido (perf_counter) para muestrear, no estimado
    error_mm: float | None         # máx. observado en sondas; None si no se verificó
    giro_grados: float | None
    cumple: bool | None            # None = no verificado
    limite_alcanzado: bool
    tol_mm: float
    ang_grados: float
    ajustado_a_impar: bool = False


_POLITICA = Politica()


def configurar_politica(p: Politica) -> None:
    global _POLITICA
    _POLITICA = p


def politica_actual() -> Politica:
    return _POLITICA


def _malla(a: float, b: float, n: int) -> np.ndarray:
    """n nodos con los extremos y θ = 0 EXACTOS (si 0 ∈ (a, b)); espaciado uniforme a cada lado."""
    n = int(n)
    if a < 0.0 < b:
        k1 = max(2, int(round((n - 1) * (-a) / (b - a)))) + 1
        k2 = n + 1 - k1
        return np.concatenate([np.linspace(a, 0.0, k1)[:-1], np.linspace(0.0, b, k2)])
    return np.linspace(a, b, n)


def _dseg(q: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    ab = b - a
    l2 = np.maximum((ab * ab).sum(1), 1e-300)
    s = np.clip(((q - a) * ab).sum(1) / l2, 0.0, 1.0)
    d = q - (a + s[:, None] * ab)
    return np.hypot(d[:, 0], d[:, 1])


def _giro(pl: np.ndarray, pm: np.ndarray, pr: np.ndarray) -> np.ndarray:
    va, vb = pm - pl, pr - pm
    na, nb = np.hypot(va[:, 0], va[:, 1]), np.hypot(vb[:, 0], vb[:, 1])
    ok = (na > 1e-15) & (nb > 1e-15)
    cos = np.where(ok, (va * vb).sum(1) / np.where(ok, na * nb, 1.0), 1.0)
    return np.degrees(np.arccos(np.clip(cos, -1.0, 1.0)))


def _sondear(ev, tl, th, pl, pr):
    """Error (a la cuerda) y giro de cada tramo [tl, th]; devuelve también el punto medio (para subdividir)."""
    tm = 0.5 * (tl + th)
    n = tl.size
    q = ev(np.concatenate([0.5 * (tl + tm), tm, 0.5 * (tm + th)]))
    q1, pm, q3 = q[:n], q[n:2 * n], q[2 * n:]
    err = np.maximum(np.maximum(_dseg(q1, pl, pr), _dseg(pm, pl, pr)), _dseg(q3, pl, pr))
    return err, _giro(pl, pm, pr), tm, pm


def _evaluar(ev, ts: np.ndarray) -> np.ndarray:
    p = np.asarray(ev(ts), dtype=float)
    if p.shape != (ts.size, 2) or not np.isfinite(p).all():
        raise ValueError("Evaluador geométrico inválido (forma o valores no finitos)")
    return p


def uniforme_vec(ev, a: float, b: float, n: int, verificar: bool = False, tol_mm: float = 0.0,
                 ang_grados: float = 0.0):
    """Malla uniforme de EXACTAMENTE `n` nodos (impar: si n es par se usa n+1 para conservar θ = 0)."""
    if not a < b or not 3 <= n <= 1_000_001:
        raise ValueError("Rango o número de muestras inválido")
    impar = (n % 2 == 0)
    ne = n + 1 if impar else n
    t = _malla(a, b, ne)
    err = giro = cumple = None
    evals = 0
    if verificar:
        p = _evaluar(ev, t)
        e, g, _tm, _pm = _sondear(lambda x: _evaluar(ev, x), t[:-1], t[1:], p[:-1], p[1:])
        err, giro, evals = float(e.max()), float(g.max()), t.size + 3 * (t.size - 1)
        cumple = bool(err <= tol_mm and giro <= ang_grados)
    return t, MuestreoInfo(ESTRATEGIA_UNIFORME, int(t.size), int(n), evals, 0.0, err, giro, cumple, False,
                           float(tol_mm), float(ang_grados), impar)


def adaptativa_vec(ev, a: float, b: float, tol_mm: float, ang_grados: float, max_samples: int = 30001,
                   max_depth: int = PROFUNDIDAD_MAX, n_inicial: int = N_INICIAL):
    """Subdivisión adaptativa por niveles (vectorizada). Conserva extremos y θ = 0; nunca supera `max_samples`
    nodos ni `max_depth` subdivisiones; con cupo limitado prioriza los tramos que más se alejan de la tolerancia."""
    if not a < b or not (0 <= tol_mm <= 0.1) or not (0 <= ang_grados <= 1) or max_samples < 3:
        raise ValueError("Parámetros de discretización inválidos")
    n0 = max(3, min(int(n_inicial), int(max_samples)))
    if n0 % 2 == 0:
        n0 -= 1
    t = _malla(a, b, n0)
    p = _evaluar(ev, t)
    evals = t.size
    m = t.size - 1
    prof = np.zeros(m, dtype=int)
    listo = np.zeros(m, dtype=bool)
    err = np.zeros(m)
    giro = np.zeros(m)
    limite = False
    ev_ok = lambda x: _evaluar(ev, x)     # noqa: E731
    tol_d, ang_d = max(tol_mm, 1e-300), max(ang_grados, 1e-300)
    while True:
        pend = np.flatnonzero(~listo)
        if pend.size == 0:
            break
        e, g, tm, pm = _sondear(ev_ok, t[pend], t[pend + 1], p[pend], p[pend + 1])
        evals += 3 * pend.size
        err[pend], giro[pend] = e, g
        viol = np.maximum(e / tol_d, g / ang_d)
        necesita = viol > 1.0
        listo[pend[~necesita]] = True
        cand = np.flatnonzero(necesita)
        if cand.size == 0:
            break
        cand = cand[prof[pend[cand]] < max_depth]
        cupo = max(int(max_samples) - t.size, 0)
        if cand.size > cupo:                                  # cupo insuficiente: los peores primero
            cand = cand[np.argsort(-viol[cand], kind="stable")[:cupo]]
        dividir = np.zeros(pend.size, dtype=bool)
        dividir[cand] = True
        sin_dividir = pend[necesita & ~dividir]
        if sin_dividir.size:                                  # lo necesitaban y no se pudo: límite alcanzado
            limite = True
            listo[sin_dividir] = True
        if cand.size == 0:
            continue
        cand = np.sort(cand)
        sel = pend[cand]
        t = np.insert(t, sel + 1, tm[cand])
        p = np.insert(p, sel + 1, pm[cand], axis=0)
        split = np.zeros(listo.size, dtype=bool)
        split[sel] = True
        cnt = np.where(split, 2, 1)
        prof = np.repeat(prof + split, cnt)
        listo = np.repeat(listo & ~split, cnt)
        err, giro = np.repeat(err, cnt), np.repeat(giro, cnt)
    e_max, g_max = float(err.max()), float(giro.max())
    return t, MuestreoInfo(ESTRATEGIA_ADAPTATIVA, int(t.size), int(max_samples), int(evals), 0.0, e_max, g_max,
                           bool(e_max <= tol_mm and g_max <= ang_grados), bool(limite), float(tol_mm),
                           float(ang_grados))


def muestrear(ev, a: float, b: float, pol: Politica | None = None):
    """(θ, info) según la política vigente (o la dada). `info.tiempo_s` es tiempo MEDIDO de este muestreo."""
    pol = pol or _POLITICA
    t0 = time.perf_counter()
    if pol.estrategia == ESTRATEGIA_ADAPTATIVA:
        t, info = adaptativa_vec(ev, a, b, pol.tol_mm, pol.ang_grados, pol.max_muestras)
    else:
        t, info = uniforme_vec(ev, a, b, pol.n_uniforme, pol.verificar, pol.tol_mm, pol.ang_grados)
    return t, replace(info, tiempo_s=time.perf_counter() - t0)
