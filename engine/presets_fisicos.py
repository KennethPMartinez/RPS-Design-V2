# -*- coding: utf-8 -*-
"""
engine/presets_fisicos.py

Los presets del régimen cinemático IMPONEN también la física (lote 11): cada uno representa una aplicación
y trae su perfil de movimiento, su carga externa, la inercia a mover y el accionamiento. Sin Qt.

Dos modos (Ajustes → Simulación → «Modo seguro para banco de pruebas»):
  · Seguro (por defecto): banco RP-PG-TB con el stepper Oriental Motor PK244-01B, SIN carga externa (el banco
    trabaja sin carga) e inercias propias del banco. La FORMA del movimiento es la de la aplicación; solo se
    estira el tiempo (posiciones iguales, velocidades ÷s, aceleraciones ÷s²) hasta que la entrada quede por debajo
    de 600 rpm y el par requerido por debajo de la mitad del par de salida (factor de seguridad 2).
  · Realista: valores típicos de la aplicación en la SALIDA (velocidad, carga e inercia). La entrada se obtiene con
    la relación de transmisión nominal del mecanismo (la velocidad se multiplica por i y el par se divide entre i),
    y el motor se DIMENSIONA: stepper (posicionamiento) o AC 4 polos con variador (giro continuo).

Todos los valores son datos de partida editables, con su origen indicado; no sustituyen los de una máquina real.
"""
from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field

import numpy as np

from engine.accionamiento import AC, MODO_CAPACIDAD, STEPPER, ModeloMotor
from engine.cargas import CargaExterna
from engine.motion_engine import FabricaPresets, Ley, LineaTiempo, PerfilMovimiento, RegistroLeyes, Tramo, \
    escalar_perfil

# ---------------------------------------------------------------------- motores
# Oriental Motor PK244-01B (ficha técnica del usuario, 19/10/2026): par de retención 0,26 N·m, J rotor 54×10⁻⁷ kg·m²,
# 1,8°/paso, responde hasta 10 kHz (3000 rpm en paso completo). Curva de par de salida (pull-out) a 24 VDC,
# 1,2 A/fase, paso completo, leída del diagrama «Speed – Torque Characteristics».
PK244_CURVA = [[0.0, 0.25], [100.0, 0.245], [250.0, 0.215], [500.0, 0.19], [750.0, 0.165], [1000.0, 0.13],
               [1250.0, 0.11], [1500.0, 0.09], [2000.0, 0.068], [2400.0, 0.055]]
PK244_RETENCION = 0.26
PK244_J_KG_MM2 = 5.4
PK244_POTENCIA_W = round(max(n * math.pi / 30.0 * t for n, t in PK244_CURVA), 1)   # máx. T·ω de la curva ≈ 14 W
RPM_MAX_BANCO = 600.0
FS_STEPPER = 2.0              # factor de seguridad sobre el par de salida (práctica habitual de dimensionado)

# Steppers de mayor tamaño para el modo realista: curva de la misma forma que la PK244 escalada al par de retención
# típico de catálogo de cada tamaño (aproximación declarada).
STEPPERS = [("PK244-01B (NEMA 17)", 0.26, 5.4), ("NEMA 17 largo", 0.45, 8.2), ("NEMA 23", 1.2, 30.0),
            ("NEMA 23 largo", 2.0, 48.0), ("NEMA 34", 4.5, 140.0), ("NEMA 34 largo", 8.5, 270.0)]
# AC trifásico 4 polos, tamaños normalizados IEC (kW) e inercia de rotor típica (kg·mm²), alimentado con variador.
AC_IEC = [(0.09, 150.0), (0.12, 200.0), (0.18, 350.0), (0.25, 550.0), (0.37, 800.0), (0.55, 1400.0),
          (0.75, 1800.0), (1.1, 3000.0), (1.5, 4500.0), (2.2, 7500.0), (3.0, 10000.0), (4.0, 13000.0)]
DESLIZAMIENTO = 0.05          # deslizamiento nominal típico de un 4 polos pequeño (hipótesis)


def motor_pk244() -> ModeloMotor:
    return ModeloMotor(STEPPER, MODO_CAPACIDAD, potencia_nominal_w=PK244_POTENCIA_W, par_retencion_nm=PK244_RETENCION,
                       frecuencia_hz=50.0, polos=4, curva=copy.deepcopy(PK244_CURVA))


def curva_stepper(retencion: float) -> list:
    f = retencion / PK244_RETENCION
    return [[n, round(t * f, 5)] for n, t in PK244_CURVA]


def curva_ac(potencia_w: float, frecuencia_hz: float = 50.0, polos: int = 4, deslizamiento: float = DESLIZAMIENTO):
    """Curva con variador (control V/f): par nominal constante hasta la velocidad nominal y potencia constante
    hasta 2·n_s. T_nom = P/ω_nom, n_nom = (1 − s)·120·f/p."""
    ns = 120.0 * frecuencia_hz / max(polos, 2)
    nn = (1.0 - deslizamiento) * ns
    tn = potencia_w / (nn * math.pi / 30.0) if nn > 0 else 0.0
    pts = [[0.0, tn], [round(nn, 3), tn]]
    for f in (1.25, 1.5, 1.75, 2.0):
        n = f * ns
        pts.append([round(n, 3), round(potencia_w / (n * math.pi / 30.0), 6)])
    return pts


def par_nominal_ac(potencia_w: float, frecuencia_hz: float = 50.0, polos: int = 4) -> float:
    return curva_ac(potencia_w, frecuencia_hz, polos)[0][1]


def motor_ac(potencia_w: float = 250.0, frecuencia_hz: float = 50.0, polos: int = 4) -> ModeloMotor:
    return ModeloMotor(AC, MODO_CAPACIDAD, potencia_nominal_w=potencia_w,
                       par_retencion_nm=round(par_nominal_ac(potencia_w, frecuencia_hz, polos), 5),
                       frecuencia_hz=frecuencia_hz, polos=polos, curva=curva_ac(potencia_w, frecuencia_hz, polos))


def motor_defecto(tipo: str) -> ModeloMotor:
    """Valores por defecto al elegir el tipo de motor en el editor."""
    if tipo == AC:
        return motor_ac(250.0)
    if tipo == STEPPER:
        return motor_pk244()
    return ModeloMotor(tipo, MODO_CAPACIDAD)


# ---------------------------------------------------------------------- aplicaciones de los presets
@dataclass
class Aplicacion:
    preset: str
    nombre: str
    motor: str                     # STEPPER (posicionamiento) | AC (giro continuo)
    perfil_salida: PerfilMovimiento  # movimiento REAL de la salida (°)
    carga: CargaExterna            # en la salida (N·m)
    inercia_salida_kg_m2: float
    fuente: str = ""
    notas: list = field(default_factory=list)


def _T(i, f, y0, y1, ley, **p) -> Tramo:
    return Tramo(i, f, y0, y1, [Ley(ley, dict(p))])


def aplicaciones() -> dict:
    """Aplicación representativa de cada preset (salida). Valores típicos, editables."""
    A = {}
    A["Arranque y parada suaves"] = Aplicacion(
        "Arranque y parada suaves", "Tambor motriz de banda transportadora pequeña con arranque/parada suave", AC,
        PerfilMovimiento("Velocidad", [_T(0, 3, 0, 360, "Rampa cúbica", pendiente=None),        # 60 rpm en 3 s
                                       _T(3, 13, 360, 360, "Rampa lineal", pendiente=0.0),
                                       _T(13, 16, 360, 0, "Rampa cúbica", pendiente=None)]),
        CargaExterna(constante=8.0), 0.05,
        "Arranque suave por rampa con variador o arrancador para limitar el par de aceleración (machinedesign.com; "
        "911metallurgist.com). Tambor Ø≈100 mm, carga de fricción de banda ≈ 8 N·m (estimación).")
    A["Oscilador 100Hz"] = Aplicacion(
        "Oscilador 100Hz", "Excitador oscilante de un alimentador vibratorio de cuenco pequeño (100 Hz)", STEPPER,
        PerfilMovimiento("Posición", [_T(0, 0.2, 0, 0, "Sinusoidal", amplitud=0.5, frecuencia=100.0, fase=0.0)]),
        CargaExterna(), 2e-4,
        "Alimentadores pequeños a 100–180 Hz con amplitud máx. ≈ 0,6 mm en la periferia del cuenco (catálogo "
        "SHINWHA); ±0,5° ≈ 0,6 mm a r = 70 mm. La carga dominante es la inercia del cuenco.")
    A["Backlash"] = Aplicacion(
        "Backlash", "Ensayo de holgura: inversión de giro de ±5° con par de prueba", STEPPER,
        FabricaPresets.crear("Backlash"),
        CargaExterna(dependencia="omega", ley="Lista de puntos", puntos=[[-1.0, -1.0], [1.0, 1.0]], grado=1,
                     periodo=0.0), 1e-3,
        "Par de prueba que se invierte con el sentido de giro (±1 N·m saturado fuera de ±1 °/s: se usa la recta "
        "del ensayo); inercia del disco de ensayo ≈ 1×10⁻³ kg·m².")
    A["Giro de 90°"] = Aplicacion(
        "Giro de 90°", "Actuador eléctrico de válvula de cuarto de vuelta (mariposa/bola)", STEPPER,
        PerfilMovimiento("Posición", [_T(0, 4, 0, 90, "Cicloidal", pendiente=None)]),
        CargaExterna(constante=20.0), 2e-3,
        "Actuadores de 20–50 N·m y 4–90 s por 90° (Valworx 50 N·m en 4 s; Regin 20 N·m; ATO 50 N·m en 20 s). Se "
        "usa 20 N·m en 4 s.")
    A["Giro de 180°"] = Aplicacion(
        "Giro de 180°", "Volteador / brazo de transferencia (pick-and-place) de 180°", STEPPER,
        PerfilMovimiento("Posición", [_T(0, 1, 0, 180, "Cicloidal", pendiente=None)]),
        CargaExterna(constante=0.5), 0.01,
        "Brazo ligero con pinza: inercia ≈ 0,01 kg·m² y fricción ≈ 0,5 N·m (estimación de dimensionado).")
    tr, y = [], 0.0
    for k in range(4):                                      # 90° en 0,5 s + 2,5 s de permanencia
        tr.append(_T(k * 3.0, k * 3.0 + 0.5, y, y + 90, "Cicloidal", pendiente=None))
        tr.append(_T(k * 3.0 + 0.5, k * 3.0 + 3.0, y + 90, y + 90, "Rampa lineal", pendiente=0.0))
        y += 90
    A["Indexer"] = Aplicacion(
        "Indexer", "Mesa indexadora de 4 estaciones", STEPPER, PerfilMovimiento("Posición", tr), CargaExterna(),
        0.0265,
        "Ejemplo de mesa indexadora de Oriental Motor: J_L = 265,44×10⁻⁴ kg·m² y par de carga 0; ciclo de 0,5 s de "
        "indexado y 2,5 s de permanencia (engineersuniverse.com).")
    A["Lavadora"] = Aplicacion(
        "Lavadora", "Tambor de lavadora en fase de lavado (agitación alternante)", AC,
        PerfilMovimiento("Posición", [_T(0, 8, 0, 0, "Sinusoidal", amplitud=360.0, frecuencia=0.25, fase=0.0)]),
        CargaExterna(dependencia="omega", ley="Lista de puntos", puntos=[[-600.0, -6.0], [600.0, 6.0]], grado=1),
        0.25,
        "Tambor con ropa: inercia ≈ 0,25 kg·m² y par de volteo de la ropa ≈ 6 N·m a 100 rpm (estimación); "
        "velocidades de tambor de 90–140 rpm en las fases de distribución (patentes de control de lavadoras).")
    A["Vibrador"] = Aplicacion(
        "Vibrador", "Vibrador / compactador oscilante de baja frecuencia", STEPPER,
        PerfilMovimiento("Posición", [_T(0, 2, 0, 0, "Sinusoidal", amplitud=3.0, frecuencia=15.0, fase=0.0)]),
        CargaExterna(dependencia="omega", ley="Lista de puntos", puntos=[[-300.0, -0.3], [300.0, 0.3]], grado=1),
        5e-4,
        "Oscilación de ±3° a 15 Hz con amortiguamiento viscoso equivalente (0,001 N·m por °/s); inercia de la "
        "bandeja ≈ 5×10⁻⁴ kg·m².")
    return A


# ---------------------------------------------------------------------- transformaciones del perfil
def estirar_perfil(perfil: PerfilMovimiento, s: float) -> PerfilMovimiento:
    """Misma FORMA y mismas posiciones en un tiempo s veces mayor: v ÷ s, a ÷ s²."""
    if abs(s - 1.0) < 1e-12:
        return copy.deepcopy(perfil)
    p = copy.deepcopy(perfil)
    k = {"Posición": 1.0, "Velocidad": 1.0 / s, "Aceleración": 1.0 / s ** 2}[p.propiedad]
    for t in p.tramos:
        t.inicio, t.fin = t.inicio * s, t.fin * s
        t.y_ini, t.y_fin = t.y_ini * k, t.y_fin * k
        for ley in t.leyes:
            q = ley.params
            if q.get("pendiente") is not None:
                q["pendiente"] = float(q["pendiente"]) * k / s
            for c in ("pendiente_ini", "pendiente_fin"):
                if q.get(c) is not None:
                    q[c] = float(q[c]) * k / s
            if "amplitud" in q:
                q["amplitud"] = float(q["amplitud"]) * k
            if "frecuencia" in q:
                q["frecuencia"] = float(q["frecuencia"]) / s
            if "coeficientes" in q:
                q["coeficientes"] = [float(c) * k / s ** j for j, c in enumerate(q["coeficientes"])]
            if "puntos" in q:
                q["puntos"] = [[x * s, y * k] for x, y in q["puntos"]]
    return p


def _pico(lt):
    return float(np.max(np.abs(lt.vel))), float(np.max(np.abs(lt.acc)))


# ---------------------------------------------------------------------- inercia propia del banco
def inercia_poligono(x, y, espesor_mm: float, densidad: float) -> float:
    """J (kg·mm²) de una placa plana con contorno (x, y) en mm respecto al origen (fórmula de Green)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    if x.size < 3:
        return 0.0
    x1, y1 = np.roll(x, -1), np.roll(y, -1)
    c = x * y1 - x1 * y
    Iz = abs(np.sum(c * (x * x + x * x1 + x1 * x1 + y * y + y * y1 + y1 * y1)) / 12.0)   # mm⁴
    return float(Iz * espesor_mm * densidad * 1e-9)          # kg/m³ → kg/mm³


@dataclass
class Contexto:
    """Lo que el mecanismo aporta: relación nominal entrada→salida y cómo se expresa la salida."""
    relacion: float = 1.0          # d(salida)/d(entrada) cinemática (° por °, o mm por ° en la cremallera)
    lineal: bool = False
    radio_paso_mm: float = 0.0     # cremallera: par equivalente → fuerza (F = T/r)
    inercia_salida_banco_kg_mm2: float = 0.0
    inercia_entrada_banco_kg_mm2: float = PK244_J_KG_MM2


def contexto_de_ventana(v) -> Contexto:
    """Relación nominal y la inercia del banco (engranaje 7075, espesor de diente 4 mm) desde una ventana."""
    h = 1e-3
    try:
        rel = (v._mapa_salida(10.0 + h) - v._mapa_salida(10.0 - h)) / (2 * h)
    except Exception:
        rel = 1.0
    ctx = Contexto(relacion=float(rel), lineal=bool(v.LINEAL))
    try:
        if v.SISTEMA == "PLANETARIO":
            m = v.motor_actual
            ctx.radio_paso_mm = 0.0
            res = m.res_anular
        else:
            res = v.perfil_actual
        if v.LINEAL:
            ctx.radio_paso_mm = float(v.motor_actual.rodillo.prrp)
        elif res is not None and res.patron_x is not None:
            ctx.inercia_salida_banco_kg_mm2 = inercia_poligono(res.patron_x, res.patron_y, 4.0, 2810.0)
    except Exception:
        pass
    return ctx


# ---------------------------------------------------------------------- generación
def _par_requerido(lt, J_in_kg_mm2, J_out_kg_mm2, rel, carga: CargaExterna, lineal, r_mm, en_entrada=False):
    """Par de entrada requerido [N·m] por instante (inercias + carga reflejada, sin pérdidas)."""
    a_in = np.radians(np.asarray(lt.acc))                     # rad/s²
    rel_rad = rel * (180.0 / math.pi if lineal else 1.0)     # mm/rad o rad/rad
    J_in = J_in_kg_mm2 * 1e-6                                 # kg·m²
    if lineal:                                                # masa (kg) de la salida
        m_out = J_out_kg_mm2
        F_in = m_out * (rel_rad * 1e-3) ** 2 * a_in           # m·(dx/dθ)²·α  [N·m]
        T_inerc = J_in * a_in + F_in
    else:
        T_inerc = (J_in + J_out_kg_mm2 * 1e-6 * rel * rel) * a_in
    sal = np.asarray(lt.pos) * rel
    vs = np.asarray(lt.vel) * rel
    x = {"t": lt.t, "theta": sal, "omega": vs}[carga.dependencia]
    T = np.nan_to_num(carga.evaluar(x))
    T_ref = T * (rel_rad * 1e-3 if lineal else rel)           # carga en la salida reflejada a la entrada
    return T_inerc + T_ref


def generar(nombre: str, ctx: Contexto, modo_seguro: bool = True) -> dict:
    """{perfil (entrada), escenario-motor/carga/inercias, informe}. El perfil queda definido en el ÁNGULO DE ENTRADA."""
    ap = aplicaciones().get(nombre)
    if ap is None:
        return {"perfil": FabricaPresets.crear(nombre), "informe": ["preset sin aplicación asociada"]}
    rel = ctx.relacion if abs(ctx.relacion) > 1e-12 else 1.0
    informe = [f"Aplicación: {ap.nombre}.", ap.fuente]
    if ctx.lineal:
        r = ctx.radio_paso_mm or 1.0
        # salida angular de la aplicación ↔ traslación de la cremallera con el radio de paso: x = r·φ
        perfil_in = copy.deepcopy(ap.perfil_salida)
        rel_eff = math.copysign(1.0, rel)
        perfil_in = escalar_perfil(perfil_in, rel_eff)
        inercia_out_real = ap.inercia_salida_kg_m2 / (r * 1e-3) ** 2           # masa equivalente (kg)
        carga_real = _a_fuerza(ap.carga, r)
        informe.append(f"Cremallera: la salida angular de la aplicación se traduce con el radio de paso r = {r:.3f} mm "
                       f"(masa equivalente J/r², fuerza T/r).")
        rel_calc = rel
    else:
        perfil_in = escalar_perfil(copy.deepcopy(ap.perfil_salida), 1.0 / rel)  # entrada = salida·i
        inercia_out_real = ap.inercia_salida_kg_m2 * 1e6                       # kg·mm²
        carga_real = copy.deepcopy(ap.carga)
        rel_calc = rel
        informe.append(f"Relación nominal i = ω_ent/ω_sal = {1.0 / rel:.4g}: la entrada gira {abs(1.0 / rel):.4g} veces la "
                       f"salida y el par de la carga se divide entre {abs(1.0 / rel):.4g}.")
    if modo_seguro:
        motor = motor_pk244()
        carga = CargaExterna()                                                  # el banco trabaja sin carga
        J_out = ctx.inercia_salida_banco_kg_mm2
        J_in = ctx.inercia_entrada_banco_kg_mm2
        s = 1.0
        for _ in range(60):
            lt = LineaTiempo.construir(estirar_perfil(perfil_in, s), RegistroLeyes(), 4000)
            vmax, _ = _pico(lt)
            Treq = _par_requerido(lt, J_in, J_out, rel_calc, carga, ctx.lineal, ctx.radio_paso_mm)
            n_rpm = np.abs(lt.vel) / 6.0
            disp = np.interp(n_rpm, [p[0] for p in PK244_CURVA], [p[1] for p in PK244_CURVA], right=0.0)
            ok_v = vmax / 6.0 <= RPM_MAX_BANCO
            ok_t = np.all(np.abs(Treq) * FS_STEPPER <= disp + 1e-12)
            if ok_v and ok_t:
                break
            s *= max(1.1, (vmax / 6.0 / RPM_MAX_BANCO) if not ok_v else 1.25)
        perfil = estirar_perfil(perfil_in, s)
        informe.append(f"MODO SEGURO (banco RP-PG-TB): stepper PK244-01B, sin carga externa; inercia del banco: entrada "
                       f"{J_in:.4g} kg·mm² (rotor), salida {J_out:.4g} {'kg' if ctx.lineal else 'kg·mm²'} (engranaje 7075, "
                       f"espesor 4 mm, estimación geométrica). Misma forma de movimiento con el tiempo ×{s:.3g}: "
                       f"pico {vmax / 6.0:.4g} rpm (límite {RPM_MAX_BANCO:g}) y par ≤ par de salida/{FS_STEPPER:g}.")
    else:
        perfil = perfil_in
        carga = carga_real
        J_out = inercia_out_real
        lt = LineaTiempo.construir(perfil, RegistroLeyes(), 4000)
        motor, J_in, txt = dimensionar(ap.motor, lt, J_out, rel_calc, carga, ctx.lineal, ctx.radio_paso_mm)
        informe.append(txt)
    return {"perfil": perfil, "motor": motor, "carga": carga, "inercia_entrada": J_in, "inercia_salida": J_out,
            "aplicacion": ap.nombre, "informe": [x for x in informe if x]}


def _a_fuerza(c: CargaExterna, r_mm: float) -> CargaExterna:
    """Carga de la aplicación (par en la salida angular) -> fuerza en la cremallera, con x = r·φ."""
    c = copy.deepcopy(c)
    f = 1000.0 / max(r_mm, 1e-9)                              # N·m → N
    gx = r_mm * math.pi / 180.0 if c.dependencia in ("theta", "omega") else 1.0   # ° -> mm  ·  °/s -> mm/s
    c.constante *= f
    c.amplitud *= f
    c.puntos = [[x * gx, y * f] for x, y in c.puntos] if c.ley != "Polinómica" else \
        [[i, a * f / gx ** int(i)] for i, a in c.puntos]
    c.periodo *= gx
    c.frecuencia /= gx
    return c


def dimensionar(tipo: str, lt, J_out, rel, carga, lineal, r_mm):
    """El motor más pequeño del catálogo que cubre el par requerido (FS 2 para steppers, 1,0 continuo para AC)."""
    n = np.abs(lt.vel) / 6.0
    if tipo == STEPPER:
        for nom, ret, J in STEPPERS:
            T = _par_requerido(lt, J, J_out, rel, carga, lineal, r_mm)
            curva = curva_stepper(ret)
            disp = np.interp(n, [p[0] for p in curva], [p[1] for p in curva], right=0.0)
            if np.all(np.abs(T) * FS_STEPPER <= disp) and n.max() <= curva[-1][0]:
                m = ModeloMotor(STEPPER, MODO_CAPACIDAD, potencia_nominal_w=round(PK244_POTENCIA_W * ret / PK244_RETENCION, 1),
                                par_retencion_nm=ret, curva=curva)
                return m, J, (f"Motor dimensionado: stepper {nom} (retención {ret:g} N·m, curva PK244 escalada; "
                              f"par máx. requerido {np.abs(T).max():.4g} N·m con FS {FS_STEPPER:g}).")
        tipo = AC
    for kw, J in AC_IEC:
        P = kw * 1000.0
        T = _par_requerido(lt, J, J_out, rel, carga, lineal, r_mm)
        curva = curva_ac(P)
        disp = np.interp(n, [p[0] for p in curva], [p[1] for p in curva], right=0.0)
        if np.all(np.abs(T) <= disp) and n.max() <= curva[-1][0]:
            return motor_ac(P), J, (f"Motor dimensionado: AC 4 polos {kw:g} kW con variador (par nominal "
                                    f"{par_nominal_ac(P):.4g} N·m; par máx. requerido {np.abs(T).max():.4g} N·m).")
    kw, J = AC_IEC[-1]
    T = _par_requerido(lt, J, J_out, rel, carga, lineal, r_mm)
    return motor_ac(kw * 1000.0), J, (f"Ningún motor del catálogo cubre la aplicación (par máx. {np.abs(T).max():.4g} "
                                      f"N·m a {n.max():.4g} rpm): se asigna el mayor ({kw:g} kW) y el estudio mostrará "
                                      f"los intervalos no viables.")
