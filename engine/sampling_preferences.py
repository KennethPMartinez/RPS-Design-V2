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
