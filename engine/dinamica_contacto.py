# -*- coding: utf-8 -*-
"""
engine/dinamica_contacto.py

RÉGIMEN DINÁMICO QUE GOBIERNA AL CINEMÁTICO (lote 10). Integración temporal del mecanismo con los
contactos rodillo–perfil como ÚNICO vínculo entre entrada y salida. Sin Qt.

Coordenadas (todas respecto a la cinemática ideal del ángulo de entrada REAL θ):
    θ            ángulo del perfil (entrada) — prescrito mientras el accionamiento lo sostiene
    q_c          deflexión de cada coordenada de salida (salida: giro/traslación; planetario: + giro de
                 cada planeta). Posición absoluta del cuerpo c = R_c·θ + q_c, con R_c = d(cinemática)/dθ.
Energía cinética:  T = ½·I_e·θ̇² + ½·Σ I_c·(R_c·θ̇ + q̇_c)²
Contactos (unilaterales, sin fricción):  δ_i = −g_i(θ) + J_i·q,   F_i = max(0, k·δ_i + c·δ̇_i) si δ_i > 0
Ecuaciones de Lagrange:
    M·ẍ + Gᵀ·F(x, ẋ) = Q_ext (+ par motor en θ),   G = [−∂g/∂θ , J]
Integrador: Newmark implícito (γ = 0.6, β = 0.3025: amortiguamiento numérico leve, incondicionalmente
estable) con Newton por paso. Un cuerpo con inercia nula queda en equilibrio instantáneo (la ecuación se
vuelve algebraica): con todas las inercias nulas la integración reproduce el régimen cuasiestático.

Accionamiento:
  · Movimiento impuesto: θ(t) sigue el perfil; la salida se mueve SOLO por las fuerzas de contacto (holgura,
    deflexión, pérdida y recuperación de contacto, inversión de flanco con la inercia de la carga).
  · Evaluación de capacidad: el motor sostiene el perfil mientras el par requerido no supere el par
    disponible a esa velocidad; si lo supera, el par se satura y θ se integra libremente (pérdida de
    sincronismo / retraso); vuelve a engancharse cuando su velocidad iguala a la del perfil. Hipótesis:
    servo de posición ideal limitado por la curva par–velocidad (el modelo eléctrico no se simula).

Tablas: g_i(θ) y J_i(θ) se precalculan con el detector exacto (PerfilDentado) sobre una malla de θ; en los
mecanismos de 1 GDL se detecta la PERIODICIDAD por paso de rodillo (misma configuración con los rodillos
renumerados) para precalcular un solo paso. Entre nodos: interpolación lineal.
Unidades internas: rad, mm, N, N·mm, s; inercias kg·mm² -> N·mm·s² (÷1000), masas kg -> N·s²/mm (÷1000).
"""
from __future__ import annotations

import math
import time

import numpy as np

from engine import contacto_fisico as cf
from engine.accionamiento import MODO_CAPACIDAD, intervalos

GAMMA, BETA = 0.6, 0.3025
SINCRONIZADO, SATURADO = "Sincronizado", "Saturado"


from engine.estudio_fisico import Cancelado  # noqa: E402  (misma excepción que el estudio cuasiestático)


# ======================================================================
# Tablas de separación y jacobiano
# ======================================================================
class TablaContactos:
    def __init__(self, ad, th_min_deg, th_max_deg, n_por_paso=160, progreso=None, cancelado=None):
        self.ad = ad
        self.m = ad.m
        self.slots: dict = {}
        self._periodo = None
        zrp = self._numero_rodillos()
        paso = 360.0 / zrp
        self.r = self._radio()
        # malla base en el CENTRO del recorrido (en la cremallera, lejos de sus extremos)
        if self.m == 1 and self._detectar_periodo(paso, 0.5 * (th_min_deg + th_max_deg)):
            ths = np.linspace(self._t0, self._t0 + paso, n_por_paso + 1)
        else:
            self._periodo = None
            n = int(max(2, math.ceil((th_max_deg - th_min_deg) / paso * n_por_paso))) + 1
            ths = np.linspace(th_min_deg, th_max_deg, n)
        self.th = ths
        filas = []
        for i, th in enumerate(ths):
            if cancelado is not None and cancelado():
                raise Cancelado()
            filas.append(ad.contactos(float(th)))
            if progreso is not None and i % 20 == 0:
                progreso(i, len(ths))
        for c in filas:
            for e, p, k in zip(c.engranaje, c.planeta, c.rodillo):
                self.slots.setdefault((e, int(p), int(k)), len(self.slots))
        S = len(self.slots)
        self.G = np.full((len(ths), S), 10.0 * self.r)      # ausente = muy separado (nunca activo)
        self.J = np.zeros((len(ths), S, self.m))
        for i, c in enumerate(filas):
            idx = [self.slots[(e, int(p), int(k))] for e, p, k in zip(c.engranaje, c.planeta, c.rodillo)]
            self.G[i, idx] = c.gap
            self.J[i, idx, :] = c.J
        self.claves = sorted(self.slots, key=self.slots.get)

    def _numero_rodillos(self):
        e = getattr(self.ad, "e", None)
        if e is not None:
            return int(e.Zrp)
        return int(self.ad.motor.parametros.numero_rodillos)

    def _radio(self):
        p = getattr(self.ad, "perfil", None) or getattr(self.ad, "p_sol")
        return float(p.r)

    def _detectar_periodo(self, paso, th0) -> bool:
        """¿c(θ+paso) = c(θ) con los rodillos renumerados k -> k+s? (1 GDL)."""
        z = self._numero_rodillos()
        self._t0 = float(th0)
        try:
            muestras = [th0 + 0.37 * paso, th0 + 0.81 * paso]
            mejor = None
            for s in range(z):
                ok = True
                for t in muestras:
                    a, b = self.ad.contactos(t), self.ad.contactos(t + paso)
                    da = {int(k): (g, j) for k, g, j in zip(a.rodillo, a.gap, a.J[:, 0]) if g < 0.2 * self._radio()}
                    db = {int(k): (g, j) for k, g, j in zip(b.rodillo, b.gap, b.J[:, 0]) if g < 0.2 * self._radio()}
                    if len(da) != len(db) or not da:
                        ok = False
                        break
                    for k, (g, j) in da.items():
                        o = db.get((k + s) % z)
                        if o is None or abs(o[0] - g) > 1e-7 or abs(o[1] - j) > 1e-6 * max(1.0, abs(j)):
                            ok = False
                            break
                    if not ok:
                        break
                if ok:
                    mejor = s
                    break
            if mejor is None:
                return False
            self._periodo, self._shift, self._z = paso, mejor, z
            return True
        except Exception:
            return False

    def evaluar(self, th_deg: float):
        """(g, dg/dθ [mm/rad], J) por RANURA de la malla base en θ (°). Con tabla periódica la ranura i
        corresponde al rodillo real `rodillo_real(i, θ)` (la identidad solo importa para informar)."""
        if self._periodo is not None:
            n = math.floor((th_deg - self._t0) / self._periodo)
            return self._interp(th_deg - n * self._periodo)
        return self._interp(th_deg)

    def ranura_de(self, engranaje, planeta, rodillo, th_deg):
        """Ranura de la malla base que representa al rodillo real (engranaje, planeta, rodillo) en θ."""
        k = int(rodillo)
        if self._periodo is not None:
            n = math.floor((th_deg - self._t0) / self._periodo)
            k = (k - n * self._shift) % self._z
        return self.slots.get((engranaje, int(planeta), k))

    def _interp(self, th):
        ths = self.th
        if not hasattr(self, "_dG"):                       # pendientes por tramo, una sola vez
            self._dG = np.diff(self.G, axis=0) / np.radians(np.diff(ths))[:, None]
            self._dJ = np.diff(self.J, axis=0)
            self._h = np.diff(ths)
        i = int(np.searchsorted(ths, th)) - 1
        i = 0 if i < 0 else (len(ths) - 2 if i > len(ths) - 2 else i)
        w = (th - ths[i]) / self._h[i]
        dg = self._dG[i]
        return self.G[i] + dg * math.radians(th - ths[i]), dg, self.J[i] + w * self._dJ[i]

    def clave_rodillo(self, i):
        return self.claves[i]


# ======================================================================
# Integración
# ======================================================================
def _inercias(ad, din):
    """(I_entrada, [I_c]) en N·mm·s² (o N·s²/mm para traslación)."""
    I_e = max(0.0, din.inercia_entrada_kg_mm2) / 1000.0
    Ic = [max(0.0, din.inercia_salida) / 1000.0]
    Ic += [max(0.0, din.inercia_planeta_kg_mm2) / 1000.0] * (ad.m - 1)
    return I_e, np.asarray(Ic, float)


def simular(ad, lt, esc, sistema="", huella="", progreso=None, cancelado=None):
    from engine.estudio_fisico import ResultadoEstudio, _eventos, _holgura   # noqa: dependencia circular
    t_inicio = time.perf_counter()
    ct, sol, din, mot = esc.contacto, esc.solucionador, esc.dinamica, esc.motor
    k, c_am = float(ct.rigidez_n_mm), float(max(0.0, ct.amortiguamiento_n_s_mm))
    if ct.modelo != cf.MODELO_PENALIZACION or k <= 0:
        raise ValueError("La integración temporal requiere la formulación «Penalización elástica unilateral» con "
                         "rigidez normal > 0 (Contacto). Sin rigidez el problema dinámico con contactos rígidos "
                         "(impactos) no está modelado.")
    capacidad = mot.modo == MODO_CAPACIDAD
    par_disp = mot.funcion_par()                 # validada una sola vez
    carga_f = esc.carga.compilada()
    I_e, Ic = _inercias(ad, din)
    m = ad.m
    th_ref_all = np.asarray(lt.pos, float)
    margen = max(5.0, 0.05 * (th_ref_all.max() - th_ref_all.min()))
    total = [100]

    def avance(i, n, fase):
        if progreso is not None:
            progreso(int(fase[0] + (fase[1] - fase[0]) * i / max(n, 1)), 100)

    tabla = TablaContactos(ad, th_ref_all.min() - margen, th_ref_all.max() + margen,
                           progreso=lambda i, n: avance(i, n, (0, 35)), cancelado=cancelado)
    dur = lt.t_fin - lt.t_ini
    if din.paso_ms > 0:
        dt = din.paso_ms / 1000.0
    else:
        dt = min(5e-4, dur / 4000.0)
    n_pasos = int(min(400_000, max(10, math.ceil(dur / dt))))
    dt = dur / n_pasos
    n_cuadros = int(max(2, min(din.cuadros, n_pasos + 1)))
    t_cuadros = np.linspace(lt.t_ini, lt.t_fin, n_cuadros)
    tolv = np.array([sol.tol_equilibrio_n if tp == "traslación" else sol.tol_momento_n_mm for _, tp in ad.coordenadas])
    tolv = np.maximum(tolv, 1e-9)
    eps_m = 1e-12 * max(1e-6, float(Ic.max(initial=0.0)), I_e)
    lin = ad.lineal_salida
    en_entrada = esc.carga.componente == "entrada"

    def ref(t):
        return (math.radians(float(np.interp(t, lt.t, lt.pos))), math.radians(float(np.interp(t, lt.t, lt.vel))),
                math.radians(float(np.interp(t, lt.t, lt.acc))))

    # cinemática lineal (los 4 mecanismos): tasas y salida se calculan una vez y se reutilizan si se confirma
    th_a, th_b = float(th_ref_all.min()), float(th_ref_all.max()) + 1.0
    R_a, R_b = ad.tasas(th_a), ad.tasas(th_b)
    s_a = ad.salida_desde_entrada(th_a)
    lineal_cin = bool(np.allclose(R_a, R_b, rtol=1e-6, atol=1e-12))
    _tasas = (lambda thd: R_a) if lineal_cin else ad.tasas
    if lineal_cin:
        _r0 = R_a[0] * (math.pi / 180.0 if lin else 1.0)          # d(salida)/dθ en (mm o °) por °
        _salida = lambda thd: s_a + _r0 * (thd - th_a)
    else:
        _salida = ad.salida_desde_entrada

    def carga(t, th_deg, w_deg, q, v, R):
        sal = _salida(th_deg)
        R0 = R[0] * (1.0 if lin else 1.0)
        vq = v[0] if Ic[0] > 0 else 0.0     # salida sin masa: su velocidad es la cinemática (q̇ no es un estado)
        if lin:
            sal_real, v_real = sal + q[0], (R[0] * math.radians(w_deg) + vq)
        else:
            sal_real, v_real = sal + math.degrees(q[0]), math.degrees(R0 * math.radians(w_deg) + vq)
        x = {"t": t, "theta": th_deg if en_entrada else sal_real,
             "omega": w_deg if en_entrada else v_real}[esc.carga.dependencia]
        return carga_f(x), x

    def fuerzas(g, dg, J, th_dot, q, v):
        d = -g + J @ q
        dd = -dg * th_dot + J @ v
        f = k * d + c_am * dd
        act = (d > 0) & (f > 0)
        return np.where(act, f, 0.0), act

    def paso_bloqueado(t, th, th_d, th_dd, q, v, a, Qc, R):
        """Newmark sobre q con θ(t) impuesto. Devuelve (q, v, a, F, act, iter, conv)."""
        g, dg, J = tabla.evaluar(math.degrees(th))
        qn = q.copy()
        M = Ic + eps_m
        b = Qc - Ic * R * th_dd
        rig = k + c_am * GAMMA / (BETA * dt)
        for it in range(1, sol.max_iteraciones + 1):
            an = (qn - q - dt * v - dt * dt * (0.5 - BETA) * a) / (BETA * dt * dt)
            vn = v + dt * ((1 - GAMMA) * a + GAMMA * an)
            F, act = fuerzas(g, dg, J, th_d, qn, vn)
            res = M * an + J.T @ F - b
            if np.all(np.abs(res) <= tolv):
                return qn, vn, an, F, act, it, True
            Ja = J[act]
            H = np.diag(M / (BETA * dt * dt)) + rig * (Ja.T @ Ja)
            try:
                dq = np.linalg.solve(H, -res)
            except np.linalg.LinAlgError:
                dq = np.linalg.lstsq(H, -res, rcond=None)[0]
            qn = qn + dq
        an = (qn - q - dt * v - dt * dt * (0.5 - BETA) * a) / (BETA * dt * dt)
        vn = v + dt * ((1 - GAMMA) * a + GAMMA * an)
        F, act = fuerzas(g, dg, J, th_d, qn, vn)
        return qn, vn, an, F, act, sol.max_iteraciones, False

    def par_requerido(th_dd, q_dd, F, dg, R, Qc, Qth):
        """T_m conjugado de θ (N·mm) para sostener el estado: M_θθ θ̈ + Σ I_c R_c q̈_c − ΣR Q − Q_θ − Σ F g'."""
        Mtt = I_e + float(np.sum(Ic * R * R))
        return Mtt * th_dd + float(np.sum(Ic * R * q_dd)) - float(np.sum(R * Qc)) - Qth - float(F @ dg)

    def paso_libre(t, th, th_d, th_dd, q, v, a, Tm, Qc, Qth, R):
        """Newmark sobre x = [θ, q] con par motor Tm (N·mm) fijo en el paso."""
        x0 = np.concatenate(([th], q)); v0 = np.concatenate(([th_d], v)); a0 = np.concatenate(([th_dd], a))
        Mtt = I_e + float(np.sum(Ic * R * R)) + eps_m
        M = np.zeros((m + 1, m + 1))
        M[0, 0] = Mtt
        M[0, 1:] = M[1:, 0] = Ic * R
        M[1:, 1:] = np.diag(Ic + eps_m)
        Qx = np.concatenate(([Tm + Qth + float(np.sum(R * Qc))], Qc))
        x = x0.copy()
        rig = k + c_am * GAMMA / (BETA * dt)
        for it in range(1, sol.max_iteraciones + 1):
            an = (x - x0 - dt * v0 - dt * dt * (0.5 - BETA) * a0) / (BETA * dt * dt)
            vn = v0 + dt * ((1 - GAMMA) * a0 + GAMMA * an)
            g, dg, J = tabla.evaluar(math.degrees(x[0]))
            F, act = fuerzas(g, dg, J, vn[0], x[1:], vn[1:])
            Gm = np.hstack((-dg[:, None], J))
            res = M @ an + Gm.T @ F - Qx
            if abs(res[0]) <= 1e-6 * max(1.0, abs(Tm)) and np.all(np.abs(res[1:]) <= tolv):
                return x[0], vn[0], an[0], x[1:], vn[1:], an[1:], F, act, it, True
            Ga = Gm[act]
            H = M / (BETA * dt * dt) + rig * (Ga.T @ Ga)
            try:
                dx = np.linalg.solve(H, -res)
            except np.linalg.LinAlgError:
                dx = np.linalg.lstsq(H, -res, rcond=None)[0]
            x = x + dx
        an = (x - x0 - dt * v0 - dt * dt * (0.5 - BETA) * a0) / (BETA * dt * dt)
        vn = v0 + dt * ((1 - GAMMA) * a0 + GAMMA * an)
        g, dg, J = tabla.evaluar(math.degrees(x[0]))
        F, act = fuerzas(g, dg, J, vn[0], x[1:], vn[1:])
        return x[0], vn[0], an[0], x[1:], vn[1:], an[1:], F, act, sol.max_iteraciones, False

    # ---- estado inicial: equilibrio cuasiestático en t0 ----
    t = lt.t_ini
    th, th_d, th_dd = ref(t)
    R = _tasas(math.degrees(th))
    T0, _ = carga(t, math.degrees(th), math.degrees(th_d), np.zeros(m), np.zeros(m), R)
    Qc = np.zeros(m) if (en_entrada or not np.isfinite(T0)) else ad.Q_salida(T0)
    g0, _, J0 = tabla.evaluar(math.degrees(th))
    eq0 = cf.resolver_equilibrio(g0, J0, Qc, cf.MODELO_PENALIZACION, k, ct.tolerancia_brecha_mm, tolv, sol.max_iteraciones)
    q = eq0.q.copy() if eq0.estado == cf.DETERMINADO else np.zeros(m)
    v = np.zeros(m)
    a = np.zeros(m)
    offset = 0.0
    regimen = SINCRONIZADO
    eventos_motor = []
    cuadros = []
    j_cuadro = 0
    detenido = ""
    F, act, it_, conv = np.zeros(len(tabla.claves)), np.zeros(len(tabla.claves), bool), 0, True
    Tm_ult = float("nan")
    limite_q = math.radians(30.0) if not lin else 5.0

    def guardar(tc, estado):
        cuadros.append(dict(t=tc, th=th, th_d=th_d, th_ref=ref(tc)[0], q=q.copy(), v=v.copy(), F=F.copy(),
                            Tm=Tm_ult, regimen=regimen, estado=estado, it=it_, carga=Tcur, x=xcur))

    Tcur, xcur = T0, 0.0
    if eq0.estado == cf.DETERMINADO:
        F = np.asarray(eq0.F, float).copy()
        _g, dg0, _J = tabla.evaluar(math.degrees(th))
        Qth0 = -T0 * 1000.0 if (en_entrada and np.isfinite(T0)) else 0.0
        Tm_ult = par_requerido(th_dd, np.zeros(m), F, dg0, R, Qc, Qth0) / 1000.0
    guardar(t, "Determinado")
    j_cuadro = 1
    for n in range(1, n_pasos + 1):
        if cancelado is not None and cancelado():
            raise Cancelado()
        t = lt.t_ini + n * dt
        th_r, thd_r, thdd_r = ref(t)
        R = _tasas(math.degrees(th))
        Tcur, xcur = carga(t, math.degrees(th), math.degrees(th_d), q, v, R)
        if not np.isfinite(Tcur):
            detenido = f"t = {t:.6g} s: carga prescrita no definida en esa abscisa (dominio)"
            break
        Qc = np.zeros(m) if en_entrada else ad.Q_salida(Tcur)
        Qth = -Tcur * 1000.0 if en_entrada else 0.0
        if regimen == SINCRONIZADO:
            th_n, thd_n, thdd_n = th_r + offset, thd_r, thdd_r
            qn, vn, an, F, act, it_, conv = paso_bloqueado(t, th_n, thd_n, thdd_n, q, v, a, Qc, R)
            g_, dg_, _ = tabla.evaluar(math.degrees(th_n))
            Treq = par_requerido(thdd_n, an, F, dg_, R, Qc, Qth)
            libre = False
            if capacidad:
                Td, _causa = par_disp(math.degrees(thd_n) / 6.0)
                if Td is not None and abs(Treq) > Td * 1000.0 * (1 + 1e-9):
                    if I_e + float(np.sum(Ic * R * R)) <= 0:
                        if not any(e[2] == "Pérdida de sincronismo" for e in eventos_motor):
                            eventos_motor.append((t, ad.nombre_sistema, "Pérdida de sincronismo",
                                                  "par requerido > disponible; sin inercias definidas el movimiento "
                                                  "resultante no es integrable (se mantiene el perfil)"))
                    else:
                        libre = True
                        regimen = SATURADO
                        Tm = math.copysign(Td * 1000.0, Treq)
                        eventos_motor.append((t, ad.nombre_sistema, "Pérdida de sincronismo",
                                              f"par requerido {abs(Treq) / 1000:.4g} N·m > disponible {Td:.4g} N·m"))
            if not libre:
                th, th_d, th_dd, q, v, a = th_n, thd_n, thdd_n, qn, vn, an
                Tm_ult = Treq / 1000.0
        if regimen == SATURADO:
            Td, causa_td = par_disp(math.degrees(th_d) / 6.0)
            if Td is None:
                detenido = (f"t = {t:.6g} s: motor saturado y par disponible indeterminado a "
                            f"{math.degrees(th_d) / 6.0:.4g} rpm ({causa_td})")
                break
            g_, dg_, _J = tabla.evaluar(math.degrees(th))
            Treq_est = par_requerido(thdd_r, a, F, dg_, R, Qc, Qth)
            dw = thd_r - th_d          # el campo del motor arrastra al rotor hacia la velocidad del perfil
            Tm = math.copysign(Td * 1000.0, dw if abs(dw) > math.radians(1e-3) else Treq_est)
            th, th_d, th_dd, q, v, a, F, act, it_, conv = paso_libre(t, th, th_d, th_dd, q, v, a, Tm, Qc, Qth, R)
            Tm_ult = Tm / 1000.0
            # re-enganche: velocidad igual a la del perfil y par requerido dentro de la capacidad
            if abs(th_d - thd_r) <= max(0.02 * abs(thd_r), math.radians(0.5)):
                Td2, _ = par_disp(math.degrees(th_d) / 6.0)
                if Td2 is not None and abs(Treq_est) <= Td2 * 1000.0:
                    regimen = SINCRONIZADO
                    offset = th - th_r
                    eventos_motor.append((t, ad.nombre_sistema, "Re-enganche",
                                          f"desfase acumulado {math.degrees(offset):.4g}° respecto al perfil"))
        if not conv and sol.parar_no_convergencia:
            detenido = f"t = {t:.6g} s: sin convergencia del paso de integración"
            break
        if not np.all(np.isfinite(q)) or np.any(np.abs(q[:1]) > limite_q):
            detenido = (f"t = {t:.6g} s: la salida perdió el engrane (deflexión {q[0]:.4g}); ningún contacto "
                        "retiene la carga")
            break
        while j_cuadro < n_cuadros and t_cuadros[j_cuadro] <= t + 1e-12:
            guardar(t_cuadros[j_cuadro], "Determinado" if conv else cf.NO_CONVERGIDO)
            j_cuadro += 1
        if progreso is not None and n % 500 == 0:
            progreso(int(35 + 60 * n / n_pasos), 100)

    # ---- resultado (cuadros) ----
    r = ResultadoEstudio(sistema=sistema, huella=huella)
    comps = [x.nombre for x in ad.componentes()]
    r.momentos = {kk: [] for kk in comps}
    escala = {x.nombre: (1.0 if x.tipo == "traslación" else 1e-3) for x in ad.componentes()}
    tol = ct.tolerancia_brecha_mm
    for cd in cuadros:
        th_deg = math.degrees(cd["th"])
        cc = ad.contactos(th_deg)
        ran = [tabla.ranura_de(e, p, kk, th_deg) for e, p, kk in zip(cc.engranaje, cc.planeta, cc.rodillo)]
        Fs = np.array([cd["F"][i] if i is not None else 0.0 for i in ran])
        mom = ad.momentos(th_deg, cc, Fs)
        fr, ft = cc.componentes_locales(Fs) if cc.n else (np.zeros(0), np.zeros(0))
        reg = []
        for i in range(cc.n):
            activo = bool(Fs[i] > 0 or cc.gap[i] <= tol)
            if not (ct.registrar_todos or activo):
                continue
            reg.append(dict(clave=cc.clave[i], engranaje=cc.engranaje[i], planeta=int(cc.planeta[i]),
                            rodillo=int(cc.rodillo[i]), diente=int(cc.diente[i]), gap=float(cc.gap[i]),
                            Fn=float(Fs[i]), Fr=float(fr[i]), Ft=float(ft[i]), px=float(cc.px[i]), py=float(cc.py[i]),
                            nx=float(cc.nx[i]), ny=float(cc.ny[i]), J0=float(cc.J[i, 0]), activo=activo))
        R = ad.tasas(th_deg)
        w_in = math.degrees(cd["th_d"])
        r.t.append(float(cd["t"])); r.theta_in.append(th_deg); r.omega_in.append(w_in)
        r.alfa_in.append(float(np.interp(cd["t"], lt.t, lt.acc)))
        sal = ad.salida_desde_entrada(th_deg)
        r.salida.append(sal + (cd["q"][0] if lin else math.degrees(cd["q"][0])))
        r.v_salida.append((R[0] * cd["th_d"] + cd["v"][0]) if lin else math.degrees(R[0] * cd["th_d"] + cd["v"][0]))
        r.carga.append(float(cd["carga"])); r.abscisa_carga.append(float(cd["x"]))
        r.par_motor.append(float(cd["Tm"])); r.par_motor_origen.append("dinámica")
        r.par_transmitido.append(mom.get(ad.salida, float("nan")) * escala.get(ad.salida, 1e-3))
        for kk in comps:
            r.momentos[kk].append(mom.get(kk, float("nan")) * escala.get(kk, 1e-3))
        r.estado.append(cd["estado"]); r.mensaje.append("" if cd["regimen"] == SINCRONIZADO else "motor saturado")
        r.residuo.append(float("nan")); r.iteraciones.append(int(cd["it"]))
        d = -cc.gap + cc.J @ cd["q"] if cc.n else np.zeros(0)
        r.delta_max.append(float(d.max(initial=0.0))); r.penetracion.append(0.0)
        r.holgura.append(_holgura(cc, tol)); r.n_activos.append(int(np.sum(Fs > 0)))
        r.contactos.append(reg); r.q.append([float(x) for x in cd["q"]])
        r.theta_ref.append(math.degrees(cd["th_ref"])); r.regimen_motor.append(cd["regimen"])
    if capacidad:
        r.capacidad = ["Viable" if x == SINCRONIZADO else "No viable" for x in r.regimen_motor]
        disp = []
        for w in r.omega_in:
            Td, _ = par_disp(w / 6.0)
            disp.append(float("nan") if Td is None else Td)
        r.par_disponible = disp
        r.causa_capacidad = ["" if x == SINCRONIZADO else "par requerido > disponible (saturación)" for x in r.regimen_motor]
    r.eventos = _eventos(r, ad, esc) + eventos_motor
    if detenido:
        r.eventos.append((r.t[-1] if r.t else 0.0, ad.nombre_sistema, "Integración detenida", detenido))
    r.eventos.sort(key=lambda e: e[0])
    w_n = None
    J_rep = np.abs(tabla.J).max() if tabla.J.size else 0.0
    if Ic[0] > 0 and J_rep > 0:
        w_n = math.sqrt(k * J_rep * J_rep * 3 / Ic[0])
    r.meta = {
        "modo": "dinamico", "sistema": sistema, "salida": ad.salida, "entrada": ad.entrada,
        "coordenadas_deflexion": [nn for nn, _ in ad.coordenadas],
        "integrador": f"Newmark implícito γ={GAMMA}, β={BETA}", "paso_s": dt, "pasos": n_pasos,
        "cuadros": len(r.t), "muestras": len(r.t), "duracion_medida_s": time.perf_counter() - t_inicio,
        "tabla": {"nodos": int(len(tabla.th)), "periodica": tabla._periodo is not None},
        "frecuencia_contacto_rad_s": w_n,
        "resuelve_vibracion_contacto": bool(w_n is not None and dt < 2 * math.pi / w_n / 10),
        "inercias": {"entrada_kg_mm2": din.inercia_entrada_kg_mm2, "salida": din.inercia_salida,
                     "planeta_kg_mm2": din.inercia_planeta_kg_mm2},
        "modelo_contacto": ct.modelo, "rigidez_N_mm": k, "amortiguamiento_N_s_mm": c_am,
        "tolerancia_brecha_mm": tol, "detenido": detenido,
        "hipotesis": ["contactos normales unilaterales sin fricción (penalización elástica)",
                      "cuerpos rígidos salvo la deflexión de contacto; inercia nula = equilibrio instantáneo",
                      "accionamiento: servo de posición ideal limitado por su curva de par (capacidad)",
                      "carga dependiente del estado evaluada con el paso anterior", *mot.descripcion_hipotesis()],
        "escenario": esc.to_dict(),
        "traslacion": [x.nombre for x in ad.componentes() if x.tipo == "traslación"],
        "unidades": {"salida": "mm" if lin else "deg", "v_salida": "mm_s" if lin else "deg_s",
                     "carga": "N" if lin and not en_entrada else "N_m", "holgura": "mm" if lin else "rad"},
        "convenciones": "q = desviación respecto a la cinemática ideal del θ real (rad o mm); "
                        "n: del engranaje al rodillo; F sobre el rodillo = +Fn·n",
    }
    if progreso is not None:
        progreso(100, 100)
    return r
