# -*- coding: utf-8 -*-
"""
engine/estudio_fisico.py

ESTUDIO del régimen dinámico/contacto (funciones 5, 7, 9–11, 21–23, 31–35, 52–57, 59, 63, 64). Sin Qt.

  - `Escenario`: configuración física completa (accionamiento, carga, contacto, solucionador).
  - `BibliotecaEscenarios`: escenario asociado a cada preset + escenarios personalizados (copias: los
    presets de movimiento originales nunca se modifican).
  - `ejecutar_estudio`: equilibrio cuasiestático por MUESTRAS de la trayectoria prescrita (misma referencia
    temporal que la línea de tiempo cinemática; muestreo independiente de los FPS). Cancelación
    cooperativa (`cancelado()`), progreso (`progreso(i, n)`).
  - `ResultadoEstudio`: magnitudes calculadas SEPARADAS del estado cinemático, con estado por muestra
    (Determinado / Indeterminado / Sin equilibrio / ...), eventos, diagnósticos, capacidad del motor,
    exportación CSV/JSON con puntos de aplicación, direcciones y fuerzas individuales.

Lo que NO se calcula (no hay masas ni inercias en el proyecto): impactos, vibraciones, aceleraciones
libres ni dinámica transitoria. La trayectoria es siempre la prescrita (ambos modos del accionamiento).
"""
from __future__ import annotations

import copy
import csv
import hashlib
import json
import math
import time
from dataclasses import asdict, dataclass, field

import numpy as np

from engine import contacto_fisico as cf
from engine.accionamiento import MODO_CAPACIDAD, ModeloMotor, evaluar_capacidad, intervalos
from engine.cargas import DEP_OMEGA, DEP_T, DEP_THETA, EN_ENTRADA, CargaExterna

VERSION_RESULTADO = 1
MUESTREO_AJUSTES, MUESTREO_UNIFORME, MUESTREO_ADAPTATIVO = "Usar estrategia de Ajustes", "Uniforme por muestras", \
    "Adaptativa por tolerancia"
ESCENARIO_LIBRE = "Personalizado (sin carga externa)"
ESCENARIO_PRESET = "Escenario asociado al preset"
ESCENARIO_NUEVO = "Nuevo escenario…"


# ======================================================================
# Configuración
# ======================================================================
@dataclass
class ConfigContacto:
    modelo: str = cf.MODELO_PENALIZACION
    rigidez_n_mm: float = 0.0               # 0 = no definida (no se inventa un valor)
    tolerancia_brecha_mm: float = 1e-3
    reparto: bool = True
    registrar_todos: bool = True
    amortiguamiento_n_s_mm: float = 0.0


METODO_ESTATICO = "Equilibrio cuasiestático por posición"
METODO_DINAMICO = "Integración temporal (dinámica de contacto)"
METODOS = (METODO_DINAMICO, METODO_ESTATICO)


@dataclass
class ConfigDinamica:
    """Datos de la integración temporal. Inercias = DATOS de entrada (0 = no definida): con inercia nula el
    cuerpo se trata como sin masa (equilibrio instantáneo), nunca con un valor supuesto."""
    inercia_entrada_kg_mm2: float = 0.0       # motor + piñón (o componente de entrada), respecto a su eje
    inercia_salida: float = 0.0               # kg·mm² (giro) o kg (cremallera / carro)
    inercia_planeta_kg_mm2: float = 0.0       # giro propio de cada planeta
    paso_ms: float = 0.0                      # 0 = automático
    cuadros: int = 1500                       # instantes guardados para animación y consulta


@dataclass
class ConfigSolucionador:
    metodo: str = METODO_DINAMICO
    muestreo: str = MUESTREO_AJUSTES
    muestras: int = 201
    tol_equilibrio_n: float = 1e-6
    tol_momento_n_mm: float = 1e-6
    max_iteraciones: int = 200
    parar_no_convergencia: bool = False
    informar_indeterminados: bool = True
    guardar_diagnosticos: bool = True


@dataclass
class Escenario:
    nombre: str = ESCENARIO_LIBRE
    motor: ModeloMotor = field(default_factory=ModeloMotor)
    carga: CargaExterna = field(default_factory=CargaExterna)
    contacto: ConfigContacto = field(default_factory=ConfigContacto)
    solucionador: ConfigSolucionador = field(default_factory=ConfigSolucionador)
    dinamica: ConfigDinamica = field(default_factory=ConfigDinamica)

    def to_dict(self) -> dict:
        return {"nombre": self.nombre, "motor": self.motor.to_dict(), "carga": self.carga.to_dict(),
                "contacto": asdict(self.contacto), "solucionador": asdict(self.solucionador),
                "dinamica": asdict(self.dinamica)}

    @staticmethod
    def from_dict(d: dict) -> "Escenario":
        d = d or {}

        def sub(cls, x):
            return cls(**{k: v for k, v in (x or {}).items() if k in cls.__dataclass_fields__})
        sol = sub(ConfigSolucionador, d.get("solucionador"))
        if d.get("solucionador") and "metodo" not in d["solucionador"]:
            sol.metodo = METODO_ESTATICO
        return Escenario(d.get("nombre", ESCENARIO_LIBRE), ModeloMotor.from_dict(d.get("motor")),
                         CargaExterna.from_dict(d.get("carga")), sub(ConfigContacto, d.get("contacto")),
                         sol, sub(ConfigDinamica, d.get("dinamica")))

    def huella(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)


class BibliotecaEscenarios:
    """Escenario por preset (por defecto: sin carga externa, sin pares ficticios) + personalizados."""

    def __init__(self):
        self.por_preset: dict[str, Escenario] = {}
        self.personalizados: dict[str, Escenario] = {}

    def de_preset(self, preset: str) -> Escenario:
        e = self.por_preset.get(preset)
        return copy.deepcopy(e) if e is not None else Escenario(nombre=f"{ESCENARIO_PRESET}: {preset}")

    def asociar(self, preset: str, esc: Escenario) -> None:
        e = copy.deepcopy(esc)
        e.nombre = f"{ESCENARIO_PRESET}: {preset}"
        self.por_preset[preset] = e

    def guardar_personalizado(self, nombre: str, esc: Escenario) -> None:
        e = copy.deepcopy(esc)
        e.nombre = nombre
        self.personalizados[nombre] = e

    def to_dict(self) -> dict:
        return {"por_preset": {k: v.to_dict() for k, v in self.por_preset.items()},
                "personalizados": {k: v.to_dict() for k, v in self.personalizados.items()}}

    @staticmethod
    def from_dict(d: dict) -> "BibliotecaEscenarios":
        b = BibliotecaEscenarios()
        d = d or {}
        b.por_preset = {k: Escenario.from_dict(v) for k, v in (d.get("por_preset") or {}).items()}
        b.personalizados = {k: Escenario.from_dict(v) for k, v in (d.get("personalizados") or {}).items()}
        return b


def huella_estudio(*partes) -> str:
    return hashlib.sha1(json.dumps(partes, sort_keys=True, default=str).encode("utf-8")).hexdigest()


# ======================================================================
# Resultado
# ======================================================================
@dataclass
class ResultadoEstudio:
    sistema: str = ""
    huella: str = ""
    t: list = field(default_factory=list)
    theta_in: list = field(default_factory=list)          # °
    omega_in: list = field(default_factory=list)          # °/s
    alfa_in: list = field(default_factory=list)           # °/s²
    salida: list = field(default_factory=list)            # ° o mm
    v_salida: list = field(default_factory=list)          # °/s o mm/s
    carga: list = field(default_factory=list)             # prescrita (N·m o N)
    abscisa_carga: list = field(default_factory=list)
    par_motor: list = field(default_factory=list)         # calculado (N·m), NaN = indeterminado
    par_motor_origen: list = field(default_factory=list)  # "contactos" | "trabajo virtual" | ""
    par_transmitido: list = field(default_factory=list)   # momento de los contactos sobre la salida (N·m o N)
    momentos: dict = field(default_factory=dict)          # componente -> [N·m] (o N en traslación)
    estado: list = field(default_factory=list)
    mensaje: list = field(default_factory=list)
    residuo: list = field(default_factory=list)
    iteraciones: list = field(default_factory=list)
    delta_max: list = field(default_factory=list)
    penetracion: list = field(default_factory=list)
    holgura: list = field(default_factory=list)           # holgura geométrica (rad o mm), 1 GDL
    n_activos: list = field(default_factory=list)
    contactos: list = field(default_factory=list)         # por muestra: [dict]
    capacidad: list = field(default_factory=list)
    par_disponible: list = field(default_factory=list)
    causa_capacidad: list = field(default_factory=list)
    eventos: list = field(default_factory=list)           # [(t, sistema, evento, diagnóstico)]
    meta: dict = field(default_factory=dict)
    q: list = field(default_factory=list)                 # deflexiones generalizadas por muestra (rad o mm)
    theta_ref: list = field(default_factory=list)         # θ prescrito (°): difiere de theta_in si el motor satura
    regimen_motor: list = field(default_factory=list)     # "Sincronizado" | "Saturado" | ""

    # -- utilidades ----------------------------------------------------------------------------
    def arr(self, nombre: str) -> np.ndarray:
        return np.asarray(getattr(self, nombre), float)

    def claves_contacto(self) -> list:
        vistas, orden = set(), []
        for fila in self.contactos:
            for c in fila:
                if c["clave"] not in vistas:
                    vistas.add(c["clave"]); orden.append(c["clave"])
        return orden

    def historial(self, clave: str, campo: str = "Fn") -> np.ndarray:
        out = np.full(len(self.t), np.nan)
        for i, fila in enumerate(self.contactos):
            for c in fila:
                if c["clave"] == clave:
                    out[i] = c[campo]
                    break
        return out

    def indice_en(self, t: float) -> int:
        if not self.t:
            return -1
        return int(np.argmin(np.abs(np.asarray(self.t) - t)))

    def to_dict(self) -> dict:
        """JSON ESTRICTO (legible por otras aplicaciones): NaN/indeterminado -> null."""
        d = asdict(self)
        d["version"] = VERSION_RESULTADO
        return _sin_nan(json.loads(json.dumps(d, default=_json_default, allow_nan=True)))

    @staticmethod
    def from_dict(d: dict) -> "ResultadoEstudio":
        campos = ResultadoEstudio.__dataclass_fields__
        r = ResultadoEstudio(**{k: (v if k in _TEXTO else _con_nan(v)) for k, v in (d or {}).items() if k in campos})
        r.eventos = [tuple(e) for e in r.eventos]
        return r

    # -- exportación (función 52) --------------------------------------------------------------
    def exportar_json(self, ruta) -> None:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=1, ensure_ascii=False, allow_nan=False)

    def exportar_csv(self, ruta) -> list:
        """Escribe `<ruta>` (serie temporal) y `<ruta>_contactos.csv` (fuerzas individuales, formato largo).
        Devuelve las rutas escritas. Precisión completa (sin el formateo de presentación)."""
        from pathlib import Path
        p = Path(ruta)
        p2 = p.with_name(p.stem + "_contactos" + p.suffix)
        u = self.meta.get("unidades", {})
        comps = list(self.momentos)
        with open(p, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow([f"# RPS Design V2 · estudio de contacto · {self.sistema}"])
            for k, v in self.meta.items():
                if k != "unidades":
                    w.writerow([f"# {k}", json.dumps(v, ensure_ascii=False, default=_json_default)])
            w.writerow(["t_s", "theta_in_deg", "omega_in_deg_s", "alfa_in_deg_s2", f"salida_{u.get('salida', '')}",
                        f"v_salida_{u.get('v_salida', '')}", f"carga_prescrita_{u.get('carga', '')}",
                        "par_motor_N_m", "origen_par_motor", f"par_transmitido_{u.get('carga', '')}",
                        *[f"M_{c}_{'N' if c in self.meta.get('traslacion', []) else 'N_m'}" for c in comps],
                        "estado", "residuo", "iteraciones", "aprox_elastica_mm", "penetracion_geom_mm",
                        f"holgura_{u.get('holgura', '')}", "contactos_activos", "capacidad", "par_disponible_N_m",
                        "causa", "mensaje"])
            for i in range(len(self.t)):
                w.writerow([self.t[i], self.theta_in[i], self.omega_in[i], self.alfa_in[i], self.salida[i],
                            self.v_salida[i], self.carga[i], self.par_motor[i], self.par_motor_origen[i],
                            self.par_transmitido[i], *[self.momentos[c][i] for c in comps], self.estado[i],
                            self.residuo[i], self.iteraciones[i], self.delta_max[i], self.penetracion[i],
                            self.holgura[i], self.n_activos[i],
                            self.capacidad[i] if self.capacidad else "", self.par_disponible[i] if self.par_disponible else "",
                            self.causa_capacidad[i] if self.causa_capacidad else "", self.mensaje[i]])
        with open(p2, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["t_s", "muestra", "clave", "engranaje", "planeta", "rodillo", "diente", "separacion_mm",
                        "Fn_N", "Fr_N", "Ft_N", "Fx_sobre_rodillo_N", "Fy_sobre_rodillo_N", "px_mm", "py_mm",
                        "nx", "ny", "activo"])
            for i, fila in enumerate(self.contactos):
                for c in fila:
                    fn = c["Fn"]
                    w.writerow([self.t[i], i, c["clave"], c["engranaje"], c["planeta"] + 1, c["rodillo"], c["diente"],
                                c["gap"], fn, c["Fr"], c["Ft"], fn * c["nx"] if fn == fn else fn,
                                fn * c["ny"] if fn == fn else fn, c["px"], c["py"], c["nx"], c["ny"], c["activo"]])
        return [str(p), str(p2)]


_TEXTO = {"estado", "mensaje", "par_motor_origen", "capacidad", "causa_capacidad", "eventos", "meta", "sistema",
          "huella"}


def _sin_nan(o):
    if isinstance(o, float):
        return None if not math.isfinite(o) else o
    if isinstance(o, list):
        return [_sin_nan(x) for x in o]
    if isinstance(o, dict):
        return {k: _sin_nan(v) for k, v in o.items()}
    return o


def _con_nan(o):
    if o is None:
        return float("nan")
    if isinstance(o, list):
        return [_con_nan(x) for x in o]
    if isinstance(o, dict):
        return {k: (v if isinstance(v, (str, bool)) else _con_nan(v)) for k, v in o.items()}
    return o


def _json_default(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


# ======================================================================
# Muestreo (función 63)
# ======================================================================
def _extremos(lt) -> list:
    """Instantes de inversión de la velocidad (extremos de θ): se preservan siempre."""
    v = np.asarray(lt.vel, float)
    t = np.asarray(lt.t, float)
    s = np.sign(v)
    idx = np.nonzero((s[:-1] * s[1:] < 0))[0]
    out = []
    for i in idx:
        dv = v[i + 1] - v[i]
        out.append(float(t[i] - v[i] * (t[i + 1] - t[i]) / dv) if dv else float(t[i]))
    return out


def muestras_uniformes(lt, n: int) -> np.ndarray:
    n = max(2, int(n))
    base = np.linspace(lt.t_ini, lt.t_fin, n)
    return np.unique(np.concatenate((base, _extremos(lt), [lt.t_ini, lt.t_fin])))


def parametros_muestreo(cfg: ConfigSolucionador, politica=None) -> tuple:
    """(estrategia efectiva, n inicial, n máximo) — `politica` = engine.sampling_preferences.Politica."""
    est = cfg.muestreo
    n, nmax = int(cfg.muestras), int(cfg.muestras) * 8
    if est == MUESTREO_AJUSTES and politica is not None:
        if getattr(politica, "estrategia", "") == "uniforme":
            est = MUESTREO_UNIFORME
        else:
            est = MUESTREO_ADAPTATIVO
            nmax = max(n, min(int(getattr(politica, "max_muestras", nmax)), n * 8))
    elif est == MUESTREO_AJUSTES:
        est = MUESTREO_UNIFORME
    return est, max(3, n), max(3, nmax)


# ======================================================================
# Ejecución
# ======================================================================
class Cancelado(Exception):
    pass


class _Evaluador:
    """Resuelve UNA muestra. Separado para calibrar el costo con las mismas operaciones (función 64)."""

    def __init__(self, ad, lt, esc: Escenario):
        self.ad, self.lt, self.e = ad, lt, esc
        sol = esc.solucionador
        tol = []
        for _, tipo in ad.coordenadas:
            tol.append(sol.tol_equilibrio_n if tipo == "traslación" else sol.tol_momento_n_mm)
        self.tol = np.asarray(tol, float)

    def __call__(self, t: float) -> dict:
        ad, lt, e = self.ad, self.lt, self.e
        th = float(np.interp(t, lt.t, lt.pos))
        om = float(np.interp(t, lt.t, lt.vel))
        al = float(np.interp(t, lt.t, lt.acc))
        rel = ad.relacion(th)
        sal = ad.salida_desde_entrada(th)
        fila = dict(t=t, theta=th, omega=om, alfa=al, salida=sal, v_salida=rel * om)
        en_entrada = e.carga.componente == EN_ENTRADA
        x = {DEP_T: t, DEP_THETA: th if en_entrada else sal, DEP_OMEGA: om if en_entrada else rel * om}[e.carga.dependencia]
        T = float(e.carga.evaluar([x])[0])
        fila.update(carga=T, abscisa=x)
        fuera = ad.validar_muestra(th)
        c = ad.contactos(th)
        if fuera:
            fila.update(estado="Fuera de recorrido", mensaje=fuera, c=c, F=np.full(c.n, np.nan), eq=None)
            return fila
        if not math.isfinite(T):
            fila.update(estado=cf.INDETERMINADO, mensaje="carga prescrita no definida en esta abscisa (dominio)",
                        c=c, F=np.full(c.n, np.nan), eq=None)
            return fila
        Q = np.zeros(ad.m) if en_entrada else ad.Q_salida(T)
        ct = e.contacto
        gr = None
        if ct.amortiguamiento_n_s_mm > 0 and ct.modelo == cf.MODELO_PENALIZACION and abs(om) > 0:
            h = 1e-3
            cp, cm = ad.contactos(th + h), ad.contactos(th - h)
            gp, gm = dict(zip(cp.clave, cp.gap)), dict(zip(cm.clave, cm.gap))
            gr = np.array([(gp.get(k, g) - gm.get(k, g)) / (2 * h) * om for k, g in zip(c.clave, c.gap)])
        eq = cf.resolver_equilibrio(c.gap, c.J, Q, ct.modelo, ct.rigidez_n_mm, ct.tolerancia_brecha_mm, self.tol,
                                    e.solucionador.max_iteraciones, ct.reparto, gr, ct.amortiguamiento_n_s_mm)
        fila.update(estado=eq.estado, mensaje=eq.mensaje, c=c, F=eq.F, eq=eq, Q=Q, rel=rel,
                    carga_entrada=T if en_entrada else 0.0)
        return fila


def _holgura(c, tol) -> float:
    """Holgura geométrica de 1 GDL: suma de las menores separaciones por flanco, en la coordenada de salida."""
    if c.n == 0 or c.J.shape[1] != 1:
        return float("nan")
    J = c.J[:, 0]
    pos, neg = J > 1e-12, J < -1e-12
    if not pos.any() or not neg.any():
        return float("nan")
    gp = np.min(np.maximum(c.gap[pos], 0.0) / J[pos])
    gn = np.min(np.maximum(c.gap[neg], 0.0) / -J[neg])
    return float(gp + gn)


def _post(ad, fila, esc: Escenario) -> dict:
    """Momentos, par motor y registro de contactos de una muestra resuelta."""
    c, F, eq = fila["c"], fila["F"], fila.get("eq")
    tol = esc.contacto.tolerancia_brecha_mm
    det = eq is not None and eq.estado == cf.DETERMINADO
    nan = float("nan")
    comps = [x.nombre for x in ad.componentes()]
    if det:
        mom = ad.momentos(fila["theta"], c, F)
        tm, origen = ad.par_motor(mom, fila.get("carga_entrada", 0.0)), "contactos"
        trans = mom.get(ad.salida, nan)
    else:
        mom = {k: nan for k in comps}
        tm, origen, trans = nan, "", nan
        if eq is not None and eq.estado == cf.INDETERMINADO and math.isfinite(fila["carga"]):
            # reparto indeterminado pero equilibrio posible: par de entrada por trabajo virtual (sin fricción ni
            # inercia, perfiles conjugados): T_m·dθ = T·d(salida)
            rel = fila.get("rel", ad.relacion(fila["theta"]))
            ce = fila.get("carga_entrada", 0.0)
            if ce:
                tm = ce
            elif ad.lineal_salida:
                tm = fila["carga"] * rel * 180.0 / math.pi / 1000.0
            else:
                tm = fila["carga"] * rel
            origen = "trabajo virtual"
    escala = {x.nombre: (1.0 if x.tipo == "traslación" else 1e-3) for x in ad.componentes()}
    mom_u = {k: (v * escala.get(k, 1e-3) if v == v else nan) for k, v in mom.items()}
    fr, ft = c.componentes_locales(np.nan_to_num(F, nan=0.0)) if c.n else (np.zeros(0), np.zeros(0))
    registro = []
    for i in range(c.n):
        activo = bool(c.gap[i] <= tol) or (det and F[i] > 0)
        if not (esc.contacto.registrar_todos or activo):
            continue
        fi = float(F[i]) if np.isfinite(F[i]) else nan
        registro.append(dict(clave=c.clave[i], engranaje=c.engranaje[i], planeta=int(c.planeta[i]),
                             rodillo=int(c.rodillo[i]), diente=int(c.diente[i]), gap=float(c.gap[i]),
                             Fn=fi, Fr=float(fr[i]) if fi == fi else nan, Ft=float(ft[i]) if fi == fi else nan,
                             px=float(c.px[i]), py=float(c.py[i]), nx=float(c.nx[i]), ny=float(c.ny[i]),
                             J0=float(c.J[i, 0]), activo=activo))
    n_act = int(np.sum((F > 0) if det else (c.gap <= tol))) if c.n else 0
    return dict(mom=mom_u, tm=tm, origen=origen,
                trans=(trans * escala.get(ad.salida, 1e-3) if trans == trans else nan),
                registro=registro, n_act=n_act, holgura=_holgura(c, tol))


def estimar_costo(ad, lt, esc: Escenario, n_muestras: int, n_calibracion: int = 3) -> dict:
    """Estimación CALIBRADA: mide el tiempo real de resolver `n_calibracion` muestras con las mismas
    operaciones y lo extrapola a `n_muestras`. No es una duración medida del estudio."""
    ev = _Evaluador(ad, lt, esc)
    ts = np.linspace(lt.t_ini, lt.t_fin, n_calibracion + 2)[1:-1]
    t0 = time.perf_counter()
    for t in ts:
        _post(ad, ev(float(t)), esc)
    por = (time.perf_counter() - t0) / max(1, len(ts))
    return {"segundos_por_muestra": por, "muestras": int(n_muestras), "estimado_s": por * n_muestras,
            "calibracion": int(len(ts))}


def ejecutar_estudio(ad, lt, esc: Escenario, sistema: str = "", huella: str = "", politica=None,
                     progreso=None, cancelado=None) -> ResultadoEstudio:
    if esc.solucionador.metodo == METODO_DINAMICO:
        from engine.dinamica_contacto import simular
        return simular(ad, lt, esc, sistema, huella, progreso, cancelado)
    t_inicio = time.perf_counter()
    sol = esc.solucionador
    estrategia, n0, nmax = parametros_muestreo(sol, politica)
    ev = _Evaluador(ad, lt, esc)
    cache: dict = {}
    total_estimado = [n0 if estrategia == MUESTREO_UNIFORME else nmax]

    def resolver(t):
        if cancelado is not None and cancelado():
            raise Cancelado()
        if t not in cache:
            f = ev(float(t))
            f["post"] = _post(ad, f, esc)
            cache[t] = f
            if progreso is not None:
                progreso(len(cache), total_estimado[0])
            if sol.parar_no_convergencia and f["estado"] == cf.NO_CONVERGIDO:
                raise StopIteration(f"t = {t:.6g} s: {f['mensaje']}")
        return cache[t]

    parado = ""
    ts = list(muestras_uniformes(lt, n0 if estrategia == MUESTREO_UNIFORME else max(11, n0 // 4)))
    try:
        for t in ts:
            resolver(t)
        if estrategia == MUESTREO_ADAPTATIVO:
            dt_min = (lt.t_fin - lt.t_ini) / max(nmax - 1, 1)
            for _ in range(40):
                ts = sorted(cache)
                tm = np.array([cache[t]["post"]["tm"] for t in ts], float)
                fin = tm[np.isfinite(tm)]
                rango = float(fin.max() - fin.min()) if fin.size else 0.0
                nuevos = []
                for a, b in zip(ts, ts[1:]):
                    if b - a <= 2 * dt_min:
                        continue
                    fa, fb = cache[a], cache[b]
                    ka = {r["clave"] for r in fa["post"]["registro"] if r["activo"]}
                    kb = {r["clave"] for r in fb["post"]["registro"] if r["activo"]}
                    evento = ka != kb or fa["estado"] != fb["estado"]
                    salto = (rango > 0 and np.isfinite(fa["post"]["tm"]) and np.isfinite(fb["post"]["tm"])
                             and abs(fa["post"]["tm"] - fb["post"]["tm"]) > 0.02 * rango)
                    if evento or salto:
                        nuevos.append(0.5 * (a + b))
                if not nuevos or len(cache) >= nmax:
                    break
                for t in nuevos[: max(0, nmax - len(cache))]:
                    resolver(t)
    except StopIteration as s:
        parado = str(s)

    ts = sorted(cache)
    r = ResultadoEstudio(sistema=sistema, huella=huella)
    comps = [x.nombre for x in ad.componentes()]
    r.momentos = {k: [] for k in comps}
    for t in ts:
        f, p = cache[t], cache[t]["post"]
        eq = f.get("eq")
        r.t.append(t); r.theta_in.append(f["theta"]); r.omega_in.append(f["omega"]); r.alfa_in.append(f["alfa"])
        r.salida.append(f["salida"]); r.v_salida.append(f["v_salida"]); r.carga.append(f["carga"])
        r.abscisa_carga.append(f["abscisa"])
        r.par_motor.append(p["tm"]); r.par_motor_origen.append(p["origen"]); r.par_transmitido.append(p["trans"])
        for k in comps:
            r.momentos[k].append(p["mom"].get(k, float("nan")))
        r.estado.append(f["estado"]); r.mensaje.append(f["mensaje"])
        r.residuo.append(float(np.abs(eq.residuo).max()) if eq is not None and sol.guardar_diagnosticos
                         and np.all(np.isfinite(eq.residuo)) and eq.residuo.size else float("nan"))
        r.iteraciones.append(int(eq.iteraciones) if eq is not None else 0)
        r.delta_max.append(float(eq.delta_max) if eq is not None else float("nan"))
        r.penetracion.append(float(eq.penetracion_geom) if eq is not None else float("nan"))
        r.holgura.append(p["holgura"]); r.n_activos.append(p["n_act"]); r.contactos.append(p["registro"])
        r.q.append([float(x) for x in eq.q] if eq is not None and eq.estado == cf.DETERMINADO else [float("nan")] * ad.m)
        r.theta_ref.append(f["theta"]); r.regimen_motor.append("")

    # capacidad del motor (función 22): sin alterar la trayectoria
    if esc.motor.modo == MODO_CAPACIDAD:
        n_rpm = np.asarray(r.omega_in) / 6.0
        r.capacidad, disp, r.causa_capacidad = evaluar_capacidad(esc.motor, r.par_motor, n_rpm)
        r.par_disponible = [float(x) for x in disp]
    r.eventos = _eventos(r, ad, esc)
    if parado:
        r.eventos.append((ts[-1] if ts else 0.0, ad.nombre_sistema, "Estudio detenido", parado))
    dur = time.perf_counter() - t_inicio
    lin = ad.lineal_salida
    r.meta = {
        "modo": "cuasiestatico",
        "sistema": sistema, "salida": ad.salida, "entrada": ad.entrada,
        "coordenadas_deflexion": [n for n, _ in ad.coordenadas],
        "muestreo": estrategia, "muestras": len(ts), "duracion_medida_s": dur,
        "modelo_contacto": esc.contacto.modelo, "rigidez_N_mm": esc.contacto.rigidez_n_mm,
        "tolerancia_brecha_mm": esc.contacto.tolerancia_brecha_mm,
        "hipotesis": ["equilibrio cuasiestático por posición (sin masas ni inercias)",
                      "contacto normal unilateral sin fricción (leyes tangenciales separadas, no incluidas)",
                      "trayectoria prescrita conservada (deflexiones elásticas pequeñas)",
                      *esc.motor.descripcion_hipotesis()],
        "escenario": esc.to_dict(),
        "traslacion": [x.nombre for x in ad.componentes() if x.tipo == "traslación"],
        "unidades": {"salida": "mm" if lin else "deg", "v_salida": "mm_s" if lin else "deg_s",
                     "carga": "N" if lin and esc.carga.componente != EN_ENTRADA else "N_m",
                     "holgura": "mm" if lin else "rad"},
        "convenciones": "n: del material del engranaje hacia el rodillo; F sobre el rodillo = +Fn·n; "
                        "momentos +z antihorario; carga positiva = resistente",
    }
    return r


def _eventos(r: ResultadoEstudio, ad, esc: Escenario) -> list:
    ev = []
    sis = ad.nombre_sistema
    prev_act, prev_signo, prev_estado, prev_carga = None, 0, None, None
    for i, t in enumerate(r.t):
        act = {c["clave"] for c in r.contactos[i] if c["activo"]}
        if prev_act is not None:
            for k in sorted(prev_act - act):
                ev.append((t, sis, "Pérdida de contacto", k))
            for k in sorted(act - prev_act):
                ev.append((t, sis, "Inicio/recuperación de contacto", k))
            if act != prev_act:
                ev.append((t, sis, "Cambio del conjunto activo", f"{len(act)} contactos"))
        # flanco cargado (1 GDL): signo de J de los contactos con fuerza
        cargados = [c for c in r.contactos[i] if c["Fn"] == c["Fn"] and c["Fn"] > 0]
        signo = 0
        if cargados and ad.m == 1:          # flanco cargado = signo de J de los contactos con fuerza
            signo = int(np.sign(sum(np.sign(c.get("J0", 0.0)) for c in cargados)))
        if prev_signo and signo and signo != prev_signo:
            ev.append((t, sis, "Cambio de flanco", "la carga pasa al flanco opuesto"))
        c_act = r.carga[i]
        if prev_carga is not None and c_act == c_act and prev_carga == prev_carga and np.sign(c_act) * np.sign(prev_carga) < 0:
            hol = r.holgura[i]
            ev.append((t, sis, "Inversión de carga",
                       f"holgura geométrica {hol:.4g} {'mm' if ad.lineal_salida else 'rad'}" if hol == hol else
                       "holgura geométrica no determinable"))
        e = r.estado[i]
        if e != prev_estado and e != cf.DETERMINADO and (esc.solucionador.informar_indeterminados or e != cf.INDETERMINADO):
            ev.append((t, sis, e, r.mensaje[i]))
        prev_act, prev_signo, prev_estado, prev_carga = act, signo or prev_signo, e, c_act
    if r.capacidad:
        for a, b, etq in intervalos(r.t, r.capacidad, {"No viable", "Indeterminado"}):
            causas = sorted({r.causa_capacidad[i] for i in range(len(r.t)) if a <= r.t[i] <= b and r.capacidad[i] == etq})
            ev.append((a, sis, f"Intervalo {etq.lower()} [{a:.4g}, {b:.4g}] s", "; ".join(c for c in causas if c)))
    ev.sort(key=lambda x: x[0])
    return ev
