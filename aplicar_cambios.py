# -*- coding: utf-8 -*-
"""
aplicar_cambios.py — Lote 2 (Planetario + pendientes §6.2).
Uso: descomprimir el zip en la RAÍZ del proyecto y ejecutar  python aplicar_cambios.py
Parchea los archivos existentes con reemplazos exactos: si un ancla no coincide (porque el archivo cambió),
ese archivo NO se toca y se informa. Es idempotente (volver a ejecutarlo no duplica nada).
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
errores, hechos = [], []


def leer(ruta):
    return (RAIZ / ruta).read_text(encoding="utf-8")


def escribir(ruta, texto):
    (RAIZ / ruta).write_text(texto, encoding="utf-8")
    hechos.append(ruta)


def parchear(ruta, cambios):
    try:
        s = leer(ruta)
    except OSError as e:
        errores.append(f"{ruta}: {e}")
        return
    for viejo, nuevo in cambios:
        n = s.count(viejo)
        if n == 1:
            s = s.replace(viejo, nuevo)
        elif n == 0 and nuevo in s:
            continue                                     # ya aplicado
        else:
            errores.append(f"{ruta}: ancla {'no encontrada' if n == 0 else f'repetida ({n} veces)'}: "
                           f"{viejo.strip()[:80]!r}")
            return
    escribir(ruta, s)


# ====================================================================== contact_engine (§6.2 hipotrocoidal)
ZOOM = '''            # V2.1: refinamiento por ZOOM sobre la curva EXACTA. Sustituye al parabólico sobre d², que con la
            # malla de 61 muestras dejaba saltos de theta_local en la raíz (más visibles en Hipotrocoidal).
            # Cada pasada evalúa 21 puntos en ±1 paso y estrecha la ventana ÷10 (5 pasadas ~ 1e-8 rad).
            paso_malla = float(theta_muestras[1] - theta_muestras[0])
            lo = max(float(mejor_theta) - paso_malla, float(theta_muestras[0]))
            hi = min(float(mejor_theta) + paso_malla, float(theta_muestras[-1]))
            for _ in range(5):
                ts = np.linspace(lo, hi, 21)
                oxz, oyz = self.motor.curva_offset(ts)
                oxz, oyz = mu.rotar(oxz, oyz, rot_vista)
                oxz, oyz = mu.rotar(oxz, oyz, mejor_j * paso_diente)
                kz = int(np.argmin((oxz - cx_cand[pos]) ** 2 + (oyz - cy_cand[pos]) ** 2))
                mejor_px, mejor_py, mejor_theta = float(oxz[kz]), float(oyz[kz]), float(ts[kz])
                lo, hi = float(ts[max(kz - 1, 0)]), float(ts[min(kz + 1, 20)])
'''


def parchear_contact_engine():
    ruta = "engine/contact_engine.py"
    s = leer(ruta)
    if "V2.1: refinamiento por ZOOM" in s:
        return
    ini, fin = s.find("# V2 (θ=0): refinamiento parabólico"), s.find("float(ox_r), float(oy_r), t_ref")
    if ini < 0 or fin < ini:
        errores.append(f"{ruta}: no se encontró el bloque de refinamiento parabólico")
        return
    ini = s.rfind("\n", 0, ini) + 1
    fin = s.find("\n", fin) + 1
    escribir(ruta, s[:ini] + ZOOM + s[fin:])


# ====================================================================== data_structures
parchear("config/data_structures.py", [
    ('class ComponenteBloqueado(Enum):\n    ANULAR = "Anular"\n    BRAZO = "Brazo"\n    SOL = "Sol"\n',
     'class Componente(str, Enum):\n    """Componente del planetario (str: se serializa a JSON como "Sol"/"Brazo"/"Anular")."""\n'
     '    ANULAR = "Anular"\n    BRAZO = "Brazo"\n    SOL = "Sol"\n\n\nComponenteBloqueado = Componente   # nombre anterior\n'),
    ('    numero_dientes_sol: int = 12\n    componente_bloqueado: ComponenteBloqueado = ComponenteBloqueado.ANULAR\n',
     '    numero_dientes_sol: int = 12\n    componente_entrada: Componente = Componente.SOL\n'
     '    componente_bloqueado: Componente = Componente.ANULAR\n'),
    ('    def es_valido(self) -> bool:\n        return super().es_valido() and self.numero_dientes_sol >= 3',
     '    def __post_init__(self):\n        self.componente_entrada = Componente(self.componente_entrada)\n'
     '        self.componente_bloqueado = Componente(self.componente_bloqueado)\n\n'
     '    def es_valido(self) -> bool:\n        return (super().es_valido() and self.numero_dientes_sol >= 3\n'
     '                and self.componente_entrada != self.componente_bloqueado)'),
])

# ====================================================================== motion_engine
METODOS_LT = '''    # --- encaje de la posición en un rango permitido (p. ej. largo de la cremallera) ---
    def rango_posicion(self) -> tuple[float, float]:
        return float(np.min(self.pos)), float(np.max(self.pos))

    def ajustada(self, lo: float, hi: float, escalar: bool = True):
        """Encaja la posición en [lo, hi]. Devuelve (LineaTiempo, factor, desplazamiento, recortada).
        1) escalar=True y el recorrido total > hi-lo -> se escala (pos, vel y acc son lineales: exacto).
        2) Si aún sobresale por un extremo, se desplaza lo mínimo. 3) escalar=False y no cabe -> se recorta."""
        pmin, pmax = self.rango_posicion()
        ext, ancho = pmax - pmin, hi - lo
        f = 1.0
        if escalar and ext > ancho + 1e-9 and ext > 1e-12:
            f = 0.999 * ancho / ext
        smin, smax = f * pmin, f * pmax
        off = (lo - smin) if smin < lo - 1e-9 else ((hi - smax) if smax > hi + 1e-9 else 0.0)
        if f == 1.0 and off == 0.0:
            return self, 1.0, 0.0, False
        if not escalar and ext > ancho + 1e-9:
            pos = np.clip(self.pos, lo, hi)
            vel = np.gradient(pos, self.t)
            acc = np.gradient(vel, self.t)
            return LineaTiempo(self.t, self.entrada, pos, vel, acc, list(self.errores)), 1.0, 0.0, True
        return (LineaTiempo(self.t, f * self.entrada, f * self.pos + off, f * self.vel, f * self.acc,
                            list(self.errores)), f, off, False)

'''

ESCALAR = '''def escalar_perfil(perfil: PerfilMovimiento, f: float) -> PerfilMovimiento:
    """Copia del perfil con todas sus magnitudes multiplicadas por f (las leyes son lineales en y)."""
    p = copy.deepcopy(perfil)
    for t in p.tramos:
        t.y_ini *= f
        t.y_fin *= f
        for ley in t.leyes:
            q = ley.params
            for k in ("amplitud", "pendiente", "pendiente_ini", "pendiente_fin"):
                if q.get(k) is not None:
                    q[k] = float(q[k]) * f
            if "coeficientes" in q:
                q["coeficientes"] = [float(c) * f for c in q["coeficientes"]]
            if "puntos" in q:
                q["puntos"] = [[x, y * f] for x, y in q["puntos"]]
    return p
'''


def parchear_motion_engine():
    ruta = "engine/motion_engine.py"
    parchear(ruta, [
        ("import math\nfrom abc import ABC, abstractmethod", "import copy\nimport math\nfrom abc import ABC, abstractmethod"),
        ('    def posicion_en(self, t: float) -> float:\n        """Escalar por fotograma (reproducción interactiva)."""',
         METODOS_LT + '    def posicion_en(self, t: float) -> float:\n        """Escalar por fotograma (reproducción interactiva)."""'),
    ])
    s = leer(ruta)
    if "def escalar_perfil" not in s:
        escribir(ruta, s.rstrip() + "\n\n\n" + ESCALAR)


# ====================================================================== sistema_base
HOOKS = '''    def _actualizar_rango_control(self, parametros):
        pass

    def _crear_vista(self):
        return reemplazar_widget(self.ui.graphicsView_epi, SimulationView())

    def _alterno(self) -> bool:
        """True si el piñón está en modo alterno (Orbitar / Trasladar)."""
        return self.ui.comboBox_modo_pinon.currentIndex() == 1

    def _rango_angulo_auto(self):
        """(mín, máx) en ° que puede recorrer la línea de tiempo, o None si no hay límite
        (Trocoidal: el piñón no debe salirse de la cremallera)."""
        return None

    def _conectar_modo_pinon(self):
        self.ui.comboBox_modo_pinon.currentIndexChanged.connect(lambda *_: self._modo_pinon_cambiado())

    def _conectar_propiedades(self):
        u = self.ui
        u.actionPerfil_del_diente.triggered.connect(lambda *_: self._abrir_aux(lambda: VentanaPerfilDiente(self)))
        u.action_ngulo_de_Presi_n.triggered.connect(lambda *_: self._abrir_aux(lambda: VentanaPropiedad(self, "angulo")))
        u.actionRadio_de_Curvatura.triggered.connect(lambda *_: self._abrir_aux(lambda: VentanaPropiedad(self, "curvatura")))
        u.actionCamino_de_Contacto.triggered.connect(lambda *_: self._abrir_aux(lambda: VentanaPropiedad(self, "contacto")))

    def _combos_modo(self, s: dict) -> tuple:
        """(combo, valor guardado) que se restauran al abrir un proyecto."""
        return ((self.ui.comboBox_modo_pinon, s.get("modo_pinon", 0)),)
'''

PROPIEDADES_VIEJO = '''        u.actionPerfil_del_diente.triggered.connect(lambda *_: self._abrir_aux(lambda: VentanaPerfilDiente(self)))
        u.action_ngulo_de_Presi_n.triggered.connect(lambda *_: self._abrir_aux(lambda: VentanaPropiedad(self, "angulo")))
        u.actionRadio_de_Curvatura.triggered.connect(lambda *_: self._abrir_aux(lambda: VentanaPropiedad(self, "curvatura")))
        u.actionCamino_de_Contacto.triggered.connect(lambda *_: self._abrir_aux(lambda: VentanaPropiedad(self, "contacto")))
'''

LT_VIEJO = '''        try:
            self.linea_tiempo = LineaTiempo.construir(self.perfil_mov, RegistroLeyes())
            if self.linea_tiempo.errores:
                self.statusBar().showMessage("Aviso: " + " | ".join(self.linea_tiempo.errores[-3:]), 6000)
        except Exception as e:'''

LT_NUEVO = '''        try:
            lt = LineaTiempo.construir(self.perfil_mov, RegistroLeyes())
            avisos = list(lt.errores[-3:])
            rango = self._rango_angulo_auto()
            if rango is not None:       # el recorrido debe caber (Trocoidal: X = prrp·θ en [0, L])
                lt, f, off, recortada = lt.ajustada(*rango, escalar=self.ui.checkBox_valpredeterminados.isChecked())
                if f < 1.0:
                    avisos.append(f"preset escalado ×{f:.3f} para que el piñón no salga del mecanismo")
                if off:
                    avisos.append(f"recorrido desplazado {off:+.1f}° para quedar dentro del rango")
                if recortada:
                    avisos.append("el perfil excede el recorrido permitido: se recortó")
            self.linea_tiempo = lt
            if avisos:
                self.statusBar().showMessage("Aviso: " + " | ".join(avisos), 8000)
                self._t_msg = time.perf_counter() + 4.0      # que el mensaje de t/θ no lo pise
        except Exception as e:'''

parchear("ui/sistema_base.py", [
    (PROPIEDADES_VIEJO, "        self._conectar_propiedades()\n"),
    ("        self.sim = reemplazar_widget(self.ui.graphicsView_epi, SimulationView())",
     "        self.sim = self._crear_vista()"),
    ("    def _actualizar_rango_control(self, parametros):\n        pass\n", HOOKS),
    ("        u.comboBox_modo_pinon.currentIndexChanged.connect(lambda *_: self._modo_pinon_cambiado())\n",
     "        self._conectar_modo_pinon()\n"),
    ("        self.perfilActualizado.emit(res)\n        self._emitir_estado()\n\n"
     "    # ------------------------------------------------------------------ estado de la simulación",
     "        self.perfilActualizado.emit(res)\n        self._emitir_estado()\n"
     "        if self._es_auto() and self._rango_angulo_auto() is not None:    # L / prrp cambiaron: reencajar\n"
     "            self._reconstruir_auto()\n\n"
     "    # ------------------------------------------------------------------ estado de la simulación"),
    (LT_VIEJO, LT_NUEVO),
    ("        self._editor = VentanaPerfilVelocidad(self.perfil_mov, self)",
     "        self._editor = VentanaPerfilVelocidad(self.perfil_mov, self, rango=self._rango_angulo_auto())"),
    ("        self._dlg_vis.actualizar_modo(self.ui.comboBox_modo_pinon.currentIndex() == 1)\n        self._dlg_vis.show()",
     "        self._dlg_vis.actualizar_modo(self._alterno())\n        self._dlg_vis.show()"),
    ('                     (self.ui.comboBox_modo_pinon, s.get("modo_pinon", 0)),',
     "                     *self._combos_modo(s),"),
])

# ====================================================================== trocoidal_window
parchear("ui/trocoidal_window.py", [
    ("    # rodadura sin deslizamiento: X = prrp·θ(rad)",
     "    def _rango_angulo_auto(self):\n"
     '        """El piñón rueda sin deslizar: X = prrp·θ debe quedar en [0, L] -> θ en [0, L/prrp] (°)."""\n'
     "        if self.motor_actual is None:\n            return None\n"
     "        return 0.0, math.degrees(float(self.motor_actual.parametros.longitud_cremallera) / self._prrp())\n\n"
     "    # rodadura sin deslizamiento: X = prrp·θ(rad)"),
])

# ====================================================================== velocity_profile_window
parchear("ui/velocity_profile_window.py", [
    ("PerfilMovimiento, RegistroLeyes, Tramo)", "PerfilMovimiento, RegistroLeyes, Tramo, escalar_perfil)"),
    ("    def __init__(self, perfil: PerfilMovimiento, parent=None):\n        super().__init__(parent)\n",
     "    def __init__(self, perfil: PerfilMovimiento, parent=None, rango=None):\n        super().__init__(parent)\n"
     "        self._rango = rango            # (mín, máx) ° del recorrido permitido (Trocoidal) o None\n"
     '        self._msg_preset = ""\n'),
    ("        self.perfil = FabricaPresets.crear(self.ui.comboBox_preset.currentText())\n",
     "        self.perfil = self._encajar_preset(FabricaPresets.crear(self.ui.comboBox_preset.currentText()))\n"),
    ("        self._marcar_curva_de_entrada()\n        self._t = 0.0\n        self._recalcular()\n",
     "        self._marcar_curva_de_entrada()\n        self._t = 0.0\n        self._recalcular()\n"
     "        if self._msg_preset:\n            self.statusBar().showMessage(self._msg_preset, 6000)\n            self._msg_preset = \"\"\n"),
    ("    def _marcar_curva_de_entrada(self):",
     "    def _encajar_preset(self, perfil):\n"
     '        """Con un rango de recorrido el preset se escala para que el piñón no se salga."""\n'
     "        if self._rango is None:\n            return perfil\n"
     "        lo, hi = self._rango\n"
     "        try:\n            pmin, pmax = LineaTiempo.construir(perfil, RegistroLeyes(), 1600).rango_posicion()\n"
     "        except Exception:\n            return perfil\n"
     "        if pmax - pmin <= hi - lo + 1e-9:\n            return perfil\n"
     "        f = 0.999 * (hi - lo) / (pmax - pmin)\n"
     '        self._msg_preset = f"Preset escalado ×{f:.3f} para caber en el recorrido del piñón ({hi - lo:.1f}°)."\n'
     "        return escalar_perfil(perfil, f)\n\n"
     "    def _marcar_curva_de_entrada(self):"),
    ("        else:\n            self.statusBar().clearMessage()\n        sp = self.ui.doubleSpinBox_5",
     "        else:\n            self.statusBar().clearMessage()\n            if self._rango is not None:\n"
     "                pmin, pmax = self.lt.rango_posicion()\n"
     "                if pmax - pmin > self._rango[1] - self._rango[0] + 1e-9:\n"
     '                    self.statusBar().showMessage("El perfil excede el recorrido del piñón: la simulación lo recortará.", 8000)\n'
     "        sp = self.ui.doubleSpinBox_5"),
])

# ====================================================================== menú, main, file_handler
parchear("ui/main_menu.py", [
    ("        from ui.trocoidal_window import VentanaTrocoidal as clase\n    else:",
     "        from ui.trocoidal_window import VentanaTrocoidal as clase\n"
     "    elif tipo is TipoSistema.PLANETARIO:\n        from ui.planetary_window import VentanaPlanetario as clase\n    else:"),
])
parchear("main.py", [
    ('"Mostrar_Ocultar_Hipotrocoidal", "Mostrar_Ocultar_Trocoidal"]',
     '"Mostrar_Ocultar_Hipotrocoidal", "Mostrar_Ocultar_Trocoidal",\n'
     '              "PlanetarioV2", "Graficas_Window_PlanetarioV2", "ToothProfile_Window_PlanetarioV2"]'),
])
parchear("utils/file_handler.py", [
    ("ParametrosEpitrocoidal, ParametrosHipotrocoidal)", "ParametrosEpitrocoidal, ParametrosHipotrocoidal,\n"
     "                                    ParametrosPlanetario)"),
    ('"TROCOIDAL": ParametrosCremallera}', '"TROCOIDAL": ParametrosCremallera,\n                          "PLANETARIO": ParametrosPlanetario}'),
])

# ====================================================================== progress.md
SECCION_10 = '''## 10. Cambios 08-nov-2026 (V2 · lote 2)

- **§10.1 Planetario migrado** (`engine/planetario_engine.py`, `ui/planetary_window.py`, `widgets/planetary_view.py`, `ui/planetary_property_windows.py`). Sol = `EpitrocoidalEngine`, anular = `HipotrocoidalEngine` con `Za = Zs + 2·Zrp` (mismo prrp, mismo cd). Cinemática por Willis (`Zs·φs + Za·φa = (Zs+Za)·φc`): entrada = 1, bloqueado = 0, el tercero se resuelve (combos válidos: Sol/Anular, Sol/Brazo, Brazo/Anular, Anular/Brazo; si entrada = bloqueado se corrige el bloqueado). El ángulo del motor es el del componente de entrada.
- **§10.2 Contactos del planetario**: cada par (engranaje, planeta) usa el modo "Orbitar" de los engines con el movimiento RELATIVO al engranaje (α = γ − φ_g, giro = ±cd/prrp·α) y el resultado se rota φ_g al mundo. La orientación del planeta se fija con el sol; para el anular, K_i = (Zs+Za)·β_i/Zrp − C/Zrp + π con C = π·(Zrp mod 2) es múltiplo del paso del rodillo si N | (Zs+Za) (solo cambia la etiqueta del rodillo, m_i).
- **§10.3 Número de planetas** (Cálculo_de_numero_de_planetas.pdf): N | (Zs+Za) y D_ap < 2·cd·sin(π/N), con D_ap = 2(mrrp + r_rodillo + t_c + t_w), t_c = 1 mm, t_w = 2 mm. Caso base (12/12/Ø3/8.5/17°): N ∈ {2, 3, 4}; el combo elige el mayor.
- **§10.4 (resp. 6.2) Contactos Hipotrocoidal**: `contact_engine._localizar_contacto` sustituye el refinamiento parabólico sobre d² por un ZOOM sobre la curva exacta (5 pasadas de 21 puntos, ventana ÷10). Test: `theta_local` vs búsqueda densa (< 3e-4 rad).
- **§10.5 (resp. 6.2) Trocoidal automático**: `LineaTiempo.ajustada(lo, hi, escalar)` encaja el perfil en θ ∈ [0, L/prrp]: preset por defecto → se escala (pos/vel/acc son lineales); si aún sobresale se desplaza; perfil editado → solo se desplaza o se recorta (no se escala sin avisar). El editor de línea de tiempo escala los presets que aplica (`escalar_perfil`) y avisa si el perfil excede el recorrido. Se reencaja al cambiar L o cualquier parámetro. También protege al motor real (el plan sale de la misma línea de tiempo).
- **§10.6 Archivos**: `ParametrosPlanetario` gana `componente_entrada`; `Componente(str, Enum)` (serializa a JSON); `file_handler` acepta `PLANETARIO`. `sistema_base.py` gana ganchos (`_crear_vista`, `_alterno`, `_rango_angulo_auto`, `_conectar_modo_pinon`, `_conectar_propiedades`, `_combos_modo`).
- **Pendiente de verificar a mano**: prueba visual del Planetario (4 combinaciones, N = 2/3/4, contactos sol y anular, etiquetas); que el salto de la raíz hipotrocoidal haya desaparecido; Trocoidal automático con L distintos. Opcional: generar `Mostrar_Ocultar_Planetario.py` con `pyside6-uic` (mientras no exista se usa un diálogo equivalente por código).
- **Tests nuevos**: `test_planetario.py` (Willis, N válidos, contactos con sol/anular, rodillo activo = posición en el mundo), `test_contacto_y_rango.py` (refinamiento, `ajustada`, `escalar_perfil`).
'''


def parchear_progress():
    ruta = "progress.md"
    parchear(ruta, [
        ('| Planetario | Pendiente (el menú avisa "aún no migrado") |',
         "| Planetario | Migrado (sol epi + anular hipo + N planetas) — pendiente de prueba visual |"),
        ("| 2026-11-01 | Lote 1: menú en español, Ver todo, transformadas, migración de Hipotrocoidal y Trocoidal (§8). |",
         "| 2026-11-01 | Lote 1: menú en español, Ver todo, transformadas, migración de Hipotrocoidal y Trocoidal (§8). |\n"
         "| 2026-11-08 | Lote 2: Planetario + correcciones de 6.2 (contactos hipo, Trocoidal automático dentro de L) (§10). |"),
    ])
    try:
        s = leer(ruta)
    except OSError:
        return
    if "## 10. Cambios 08-nov-2026" not in s:
        escribir(ruta, s.rstrip() + "\n\n---\n\n" + SECCION_10)


parchear_contact_engine()
parchear_motion_engine()
parchear_progress()

print("Archivos modificados:", ", ".join(sorted(set(hechos))) or "ninguno")
if errores:
    print("\nNO SE PUDO APLICAR:")
    for e in errores:
        print("  -", e)
    sys.exit(1)
print("Listo. Ejecuta:  python -m pytest tests")
