"""Régimen de contacto (sin Qt): detector geométrico, solucionador unilateral, 4 mecanismos, cargas,
accionamiento, muestreo, costo y persistencia. Validaciones con casos analíticos y trabajo virtual."""
import json
import math
import os
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config.data_structures import (Componente, ParametrosCremallera, ParametrosEpitrocoidal,  # noqa: E402
                                    ParametrosHipotrocoidal, ParametrosPlanetario)
from engine import accionamiento as acc  # noqa: E402
from engine import contacto_fisico as cf  # noqa: E402
from engine import math_utils as mu  # noqa: E402
from engine.cargas import CargaExterna  # noqa: E402
from engine.cremallera_engine import CremalleraEngine  # noqa: E402
from engine.epitrocoidal_engine import EpitrocoidalEngine  # noqa: E402
from engine.estudio_fisico import (METODO_ESTATICO, MUESTREO_ADAPTATIVO, BibliotecaEscenarios, Escenario,  # noqa: E402
                                   ResultadoEstudio, ejecutar_estudio, estimar_costo, muestras_uniformes)
from engine.hipotrocoidal_engine import HipotrocoidalEngine  # noqa: E402
from engine.mecanismos_fisicos import adaptador_para  # noqa: E402
from engine.motion_engine import FabricaPresets, LineaTiempo, RegistroLeyes  # noqa: E402
from engine.planetario_engine import PlanetarioEngine  # noqa: E402


def mecanismos():
    return [("EPITROCOIDAL", EpitrocoidalEngine(ParametrosEpitrocoidal()), False),
            ("EPITROCOIDAL", EpitrocoidalEngine(ParametrosEpitrocoidal(numero_dientes=20)), True),
            ("HIPOTROCOIDAL", HipotrocoidalEngine(ParametrosHipotrocoidal(numero_dientes=36)), False),
            ("HIPOTROCOIDAL", HipotrocoidalEngine(ParametrosHipotrocoidal(numero_dientes=36)), True),
            ("TROCOIDAL", CremalleraEngine(ParametrosCremallera()), False),
            ("TROCOIDAL", CremalleraEngine(ParametrosCremallera()), True),
            ("PLANETARIO", PlanetarioEngine(ParametrosPlanetario()), False),
            ("PLANETARIO", PlanetarioEngine(ParametrosPlanetario(componente_entrada=Componente.BRAZO,
                                                                 componente_bloqueado=Componente.SOL)), False)]


class Detector(unittest.TestCase):
    def setUp(self):
        self.m = EpitrocoidalEngine(ParametrosEpitrocoidal())
        self.p = cf.PerfilDentado(self.m)

    def test_separacion_con_signo_contacto_y_penetracion(self):
        th = np.array([0.1, -0.3, 0.4])
        gx, gy = mu.rotar(*self.m.curva_generatriz(th), self.p.rv)            # centros sobre la generatriz
        self.assertLess(np.abs(self.p.consultar(gx, gy)["gap"]).max(), 1e-9)   # contacto exacto
        ox, oy = mu.rotar(*self.m.curva_offset(th), self.p.rv)
        fuera = self.p.consultar(gx + 0.05 * (gx - ox) / self.p.r, gy + 0.05 * (gy - oy) / self.p.r)
        dentro = self.p.consultar(gx - 0.05 * (gx - ox) / self.p.r, gy - 0.05 * (gy - oy) / self.p.r)
        np.testing.assert_allclose(fuera["gap"], 0.05, atol=1e-6)            # separación
        np.testing.assert_allclose(dentro["gap"], -0.05, atol=1e-6)          # penetración

    def test_normal_unitaria_perpendicular_al_flanco(self):
        th = np.linspace(-0.5, 0.5, 7)
        gx, gy = mu.rotar(*self.m.curva_generatriz(th), self.p.rv)
        d = self.p.consultar(gx, gy)
        tx, ty = mu.rotar(*mu.derivada_numerica(lambda t: self.m.curva_offset(t), d["theta"], h=1e-6, orden=1), self.p.rv)
        np.testing.assert_allclose(np.hypot(d["nx"], d["ny"]), 1.0, atol=1e-12)
        self.assertLess(np.abs(d["nx"] * tx + d["ny"] * ty).max() / np.hypot(tx, ty).min(), 1e-6)

    def test_jacobiano_igual_a_diferencias_finitas(self):
        """J = d(penetración)/d(giro de la salida) debe coincidir con el cambio real de la separación."""
        for sis, m, alt in mecanismos()[:6]:
            a = adaptador_para(sis, m, None, alt)
            c = a.contactos(17.0)
            act = c.gap < 1e-6
            eps = 1e-6
            if sis == "TROCOIDAL" and not alt:      # cremallera +ε en X equivale a centros −ε en su marco
                e = a._estado(17.0)
                s = e.angulo_pinon_rad
                wx = e.centro_pinon[0] + math.cos(s) * a.lx - math.sin(s) * a.ly
                wy = e.centro_pinon[1] + math.sin(s) * a.lx + math.cos(s) * a.ly
                g2 = a.perfil.consultar(wx - e.traslacion_patron[0] - eps, wy)["gap"]
                np.testing.assert_allclose(g2[c.rodillo[act]] - c.gap[act], -c.J[act, 0] * eps, atol=1e-9)
            elif not alt:                           # girar el engranaje +ε equivale a girar los centros −ε
                e = a._estado(17.0)
                cx, cy = e.centro_pinon
                s = e.angulo_pinon_rad
                wx = cx + math.cos(s) * a.lx - math.sin(s) * a.ly
                wy = cy + math.sin(s) * a.lx + math.cos(s) * a.ly
                px, py = mu.rotar(wx, wy, -(e.angulo_patron_rad + eps))
                g2 = a.perfil.consultar(px, py)["gap"]
                idx = c.rodillo[act]
                np.testing.assert_allclose(g2[idx] - c.gap[act], -c.J[act, 0] * eps, atol=1e-9, err_msg=sis)


class Solucionador(unittest.TestCase):
    def test_un_contacto_isostatico(self):
        for modelo, k in ((cf.MODELO_PENALIZACION, 1e4), (cf.MODELO_RIGIDO, 0.0)):
            e = cf.resolver_equilibrio([0.0], [[5.0]], [100.0], modelo, k)
            self.assertEqual(e.estado, cf.DETERMINADO)
            self.assertAlmostEqual(float(e.F[0]), 20.0, places=6)

    def test_reparto_por_compatibilidad_y_rigidez(self):
        e = cf.resolver_equilibrio([0, 0], [[3.0], [4.0]], [100.0], cf.MODELO_PENALIZACION, 1e4)
        np.testing.assert_allclose(e.F, [12.0, 16.0], rtol=1e-9)      # F_i = k·J_i·q, no 50/50
        self.assertLess(abs(float(e.F @ np.array([3.0, 4.0])) - 100.0), 1e-6)

    def test_holgura_retrasa_el_contacto(self):
        e = cf.resolver_equilibrio([0.01, 0.0], [[3.0], [-4.0]], [100.0], cf.MODELO_PENALIZACION, 1e4)
        self.assertAlmostEqual(float(e.q[0]), (100.0 / 3 / 1e4 + 0.01) / 3, places=12)
        self.assertEqual(float(e.F[1]), 0.0)

    def test_unilateral_sin_fuerza_atractiva(self):
        e = cf.resolver_equilibrio([0, 0], [[3.0], [-4.0]], [100.0], cf.MODELO_PENALIZACION, 1e4)
        self.assertTrue(np.all(e.F >= 0))
        self.assertEqual(float(e.F[1]), 0.0)
        e = cf.resolver_equilibrio([0.0], [[-3.0]], [100.0], cf.MODELO_PENALIZACION, 1e4)
        self.assertEqual(e.estado, cf.SIN_EQUILIBRIO)

    def test_indeterminado_sin_rigidez(self):
        e = cf.resolver_equilibrio([0, 0], [[3.0], [4.0]], [100.0], cf.MODELO_RIGIDO)
        self.assertEqual(e.estado, cf.INDETERMINADO)
        self.assertTrue(np.all(np.isnan(e.F)))
        e = cf.resolver_equilibrio([0, 0], [[3.0], [4.0]], [100.0], cf.MODELO_PENALIZACION, 0.0)
        self.assertEqual(e.estado, cf.INDETERMINADO)
        self.assertIn("rigidez normal no definida", e.mensaje)

    def test_no_convergencia_informada(self):
        e = cf.resolver_equilibrio([0.01, 0.02], [[3.0], [3.0]], [100.0], cf.MODELO_PENALIZACION, 1e4, max_iter=1)
        self.assertEqual(e.estado, cf.NO_CONVERGIDO)
        self.assertIn("sin convergencia", e.mensaje)

    def test_varios_grados_de_libertad(self):
        J = np.array([[1.0, 0.0], [0.0, 2.0], [1.0, 1.0]])
        e = cf.resolver_equilibrio([0, 0, 0], J, [10.0, 5.0], cf.MODELO_PENALIZACION, 100.0)
        np.testing.assert_allclose(J.T @ e.F, [10.0, 5.0], atol=1e-6)

    def test_amortiguamiento_solo_con_velocidad(self):
        base = cf.resolver_equilibrio([0.0], [[5.0]], [100.0], cf.MODELO_PENALIZACION, 1e4)
        quieto = cf.resolver_equilibrio([0.0], [[5.0]], [100.0], cf.MODELO_PENALIZACION, 1e4, gap_rate=[0.0],
                                        amortiguamiento=50.0)
        self.assertAlmostEqual(float(quieto.q[0]), float(base.q[0]), places=15)


class Mecanismos(unittest.TestCase):
    def test_contactos_reales_y_trabajo_virtual_en_los_cuatro(self):
        """Cuasiestático sin fricción: T_motor·dθ = T_carga·d(salida) (no se impone: se verifica)."""
        for sis, m, alt in mecanismos():
            a = adaptador_para(sis, m, None, alt)
            for th in (7.0, 23.0, 41.0):
                c = a.contactos(th)
                act = c.gap < 1e-6
                self.assertGreaterEqual(int(act.sum()), 1, f"{sis} {alt}: sin contactos")
                self.assertLess(np.abs(c.gap[act]).max(), 1e-9)
                eq = cf.resolver_equilibrio(c.gap, c.J, a.Q_salida(2.0), cf.MODELO_PENALIZACION, 5e4, 1e-3, 1e-6)
                self.assertEqual(eq.estado, cf.DETERMINADO, f"{sis} {alt}")
                tm = a.par_motor(a.momentos(th, c, eq.F))
                rel = a.relacion(th)
                esperado = 2.0 * rel * (180 / math.pi / 1000 if a.lineal_salida else 1.0)
                self.assertAlmostEqual(tm, esperado, delta=1e-6 * max(1.0, abs(esperado)), msg=f"{sis} {alt} θ={th}")

    def test_planetario_sol_anular_sin_reparto_uniforme_supuesto(self):
        e = PlanetarioEngine(ParametrosPlanetario())
        a = adaptador_para("PLANETARIO", e)
        c = a.contactos(13.0)
        self.assertIn("Sol", c.engranaje)
        self.assertIn("Anular", c.engranaje)
        eq = cf.resolver_equilibrio(c.gap, c.J, a.Q_salida(1.0), cf.MODELO_PENALIZACION, 2e4, 1e-3, 1e-6)
        M = a.momentos(13.0, c, eq.F)
        self.assertAlmostEqual(M["Sol"] + M["Anular"] + M["Brazo"], 0.0, delta=1e-6)   # equilibrio global
        for i in range(e.N):
            self.assertAlmostEqual(M[f"Planeta {i + 1}"], 0.0, delta=1e-5)           # cada planeta libre
        self.assertAlmostEqual(M["Brazo"], 1000.0, delta=1e-3)                        # carga en la salida
        # el reparto sale del equilibrio + compatibilidad: no se fija a priori
        por_planeta = [float(eq.F[c.planeta == i].sum()) for i in range(e.N)]
        self.assertTrue(all(p > 0 for p in por_planeta))

    def test_trocoidal_recorrido_0_a_L(self):
        m = CremalleraEngine(ParametrosCremallera(longitud_cremallera=30.0))
        a = adaptador_para("TROCOIDAL", m)
        th_max = math.degrees(30.0 / m.rodillo.prrp)
        self.assertEqual(a.validar_muestra(0.0), "")
        self.assertEqual(a.validar_muestra(th_max), "")
        self.assertIn("fuera del recorrido", a.validar_muestra(th_max + 1))
        self.assertIn("fuera del recorrido", a.validar_muestra(-1.0))
        lt = LineaTiempo.construir(FabricaPresets.crear("Giro de 180°"), RegistroLeyes())
        lt2, f, off, rec = lt.ajustada(0.0, th_max, escalar=True)
        self.assertLess(f, 1.0)
        x = np.radians(lt2.pos) * m.rodillo.prrp
        self.assertGreaterEqual(x.min(), -1e-9)
        self.assertLessEqual(x.max(), 30.0 + 1e-9)
        # consistencia posición–velocidad–aceleración tras la transformación (función 41)
        np.testing.assert_allclose(np.gradient(lt2.pos, lt2.t), lt2.vel, atol=1e-3 * np.abs(lt2.vel).max())
        lt3, _, _, rec3 = lt.ajustada(0.0, th_max, escalar=False)
        self.assertTrue(rec3)
        np.testing.assert_allclose(np.gradient(lt3.pos, lt3.t), lt3.vel, atol=1e-9)


class CargasYMotor(unittest.TestCase):
    def test_leyes_dominios_y_periodicidad(self):
        c = CargaExterna(ley="Rampa lineal", puntos=[[0, 0], [10, 5]])
        v = c.evaluar([-1, 0, 5, 10, 11])
        self.assertTrue(np.isnan(v[0]) and np.isnan(v[-1]))          # fuera del dominio: indeterminada
        np.testing.assert_allclose(v[1:4], [0, 2.5, 5])
        c.periodo = 10
        np.testing.assert_allclose(c.evaluar([15, 25, -5]), [2.5, 2.5, 2.5])
        s = CargaExterna(ley="Sinusoidal", constante=1, amplitud=2, frecuencia=0.25)
        np.testing.assert_allclose(s.evaluar([0, 1, 2]), [1, 3, 1], atol=1e-12)
        p = CargaExterna(ley="Polinómica", puntos=[[0, 1], [1, 2]])
        np.testing.assert_allclose(p.evaluar([0, 2]), [1, 5])
        self.assertTrue(CargaExterna(ley="Spline", puntos=[[0, 0]]).validar())

    def test_t_de_t_theta_omega_en_el_estudio(self):
        m = EpitrocoidalEngine(ParametrosEpitrocoidal())
        a = adaptador_para("EPITROCOIDAL", m)
        lt = LineaTiempo.construir(FabricaPresets.crear("Giro de 90°"), RegistroLeyes())
        for dep, ley, pts in (("t", "Rampa lineal", [[0, 0], [2, 1]]), ("theta", "Rampa lineal", [[-90, 1], [0, 0]]),
                              ("omega", "Lista de puntos", [[-100, -1], [100, 1]])):
            esc = Escenario()
            esc.solucionador.metodo = METODO_ESTATICO
            esc.carga = CargaExterna(dependencia=dep, ley=ley, puntos=pts)
            esc.contacto.rigidez_n_mm = 2e4
            esc.solucionador.muestras = 11
            r = ejecutar_estudio(a, lt, esc, "EPITROCOIDAL")
            x = r.arr("abscisa_carga")
            np.testing.assert_allclose(r.arr("carga"), esc.carga.evaluar(x))
            if dep == "theta":        # abscisa = ángulo de la SALIDA (engranaje), en °
                np.testing.assert_allclose(x, -r.arr("theta_in"), atol=1e-6)
            if dep == "omega":
                np.testing.assert_allclose(x, r.arr("v_salida"))

    def test_motores(self):
        ac_ = acc.ModeloMotor(acc.AC, potencia_nominal_w=750, velocidad_nominal_rpm=1440)
        self.assertEqual(ac_.velocidad_sincrona_rpm, 1500.0)
        self.assertAlmostEqual(ac_.par_disponible(1500)[0], 0.0)
        self.assertIsNone(ac_.par_disponible(100)[0])
        st = acc.ModeloMotor(acc.STEPPER, par_retencion_nm=0.4)
        self.assertEqual(st.par_disponible(0)[0], 0.4)
        self.assertIsNone(st.par_disponible(30)[0])                 # retención ≠ par a toda velocidad
        self.assertTrue(acc.ModeloMotor(acc.CUSTOM).validar())       # parametrización obligatoria
        self.assertTrue(acc.ModeloMotor(acc.CUSTOM, expresion="__import__('os')").validar())
        self.assertEqual(acc.ModeloMotor(acc.CUSTOM, expresion="0.5 - 0.001*n").par_disponible(100)[0], 0.4)
        est, disp, causa = acc.evaluar_capacidad(acc.ModeloMotor(acc.STEPPER, curva=[[0, 0.4], [100, 0.2]]),
                                                 [0.1, 0.5, np.nan, 0.1], [10, 10, 10, 500])
        self.assertEqual(est, ["Viable", "No viable", "Indeterminado", "Indeterminado"])
        self.assertIn("disponible", causa[1])
        self.assertEqual(acc.intervalos([0, 1, 2, 3], ["a", "b", "b", "a"], {"b"}), [(1, 2, "b")])


class Estudio(unittest.TestCase):
    def setUp(self):
        self.a = adaptador_para("EPITROCOIDAL", EpitrocoidalEngine(ParametrosEpitrocoidal()))
        self.lt = LineaTiempo.construir(FabricaPresets.crear("Backlash"), RegistroLeyes())

    def test_muestreo_preserva_extremos(self):
        ts = muestras_uniformes(self.lt, 21)
        for t in (self.lt.t_ini, self.lt.t_fin):
            self.assertIn(t, ts)
        v = np.interp(ts, self.lt.t, self.lt.vel)
        self.assertLess(np.sort(np.abs(v))[:3].max(), 1e-3 * np.abs(self.lt.vel).max())   # inversiones incluidas

    def test_adaptativo_refina_eventos_y_respeta_maximo(self):
        esc = Escenario()
        esc.solucionador.metodo = METODO_ESTATICO
        esc.carga = CargaExterna(dependencia="omega", ley="Lista de puntos", puntos=[[-100, -0.5], [100, 0.5]])
        esc.contacto.rigidez_n_mm = 2e4
        esc.solucionador.muestreo = MUESTREO_ADAPTATIVO
        esc.solucionador.muestras = 21
        r = ejecutar_estudio(self.a, self.lt, esc, "EPITROCOIDAL")
        self.assertGreater(len(r.t), len(muestras_uniformes(self.lt, 21 // 4)))
        self.assertLessEqual(len(r.t), 21 * 8)
        self.assertTrue(any(e[2] == "Inversión de carga" for e in r.eventos))

    def test_independiente_de_fps_y_reproducible(self):
        esc = Escenario()
        esc.solucionador.metodo = METODO_ESTATICO
        esc.carga = CargaExterna(constante=0.3)
        esc.contacto.rigidez_n_mm = 1e4
        esc.solucionador.muestras = 15
        r1 = ejecutar_estudio(self.a, self.lt, esc, "EPITROCOIDAL")
        r2 = ejecutar_estudio(self.a, self.lt, esc, "EPITROCOIDAL")
        np.testing.assert_array_equal(r1.arr("par_motor"), r2.arr("par_motor"))
        self.assertEqual(r1.t, list(muestras_uniformes(self.lt, 15)))

    def test_costo_estimado_y_medido(self):
        esc = Escenario()
        esc.solucionador.metodo = METODO_ESTATICO
        e = estimar_costo(self.a, self.lt, esc, 100)
        self.assertEqual(e["calibracion"], 3)
        self.assertAlmostEqual(e["estimado_s"], 100 * e["segundos_por_muestra"])
        r = ejecutar_estudio(self.a, self.lt, esc, "EPITROCOIDAL")
        self.assertGreater(r.meta["duracion_medida_s"], 0)

    def test_sin_carga_cero_y_carga_indefinida_indeterminada(self):
        esc = Escenario()           # sin pares ficticios
        esc.solucionador.metodo = METODO_ESTATICO
        esc.contacto.rigidez_n_mm = 1e4
        esc.solucionador.muestras = 7
        r = ejecutar_estudio(self.a, self.lt, esc, "EPITROCOIDAL")
        np.testing.assert_allclose(r.arr("par_motor"), 0.0, atol=1e-9)    # residuo numérico de g ≈ −1e-14 mm
        esc.carga = CargaExterna(dependencia="t", ley="Rampa lineal", puntos=[[0, 0], [1, 1]])
        r = ejecutar_estudio(self.a, self.lt, esc, "EPITROCOIDAL")
        self.assertIn(cf.INDETERMINADO, r.estado)
        self.assertTrue(np.isnan(r.arr("par_motor")[-1]))

    def test_rigido_hiperestatico_par_por_trabajo_virtual(self):
        esc = Escenario()
        esc.solucionador.metodo = METODO_ESTATICO
        esc.carga = CargaExterna(constante=0.5)
        esc.contacto.modelo = cf.MODELO_RIGIDO
        esc.solucionador.muestras = 5
        r = ejecutar_estudio(self.a, self.lt, esc, "EPITROCOIDAL")
        self.assertTrue(all(e in (cf.INDETERMINADO, cf.DETERMINADO) for e in r.estado))
        i = r.estado.index(cf.INDETERMINADO)
        self.assertEqual(r.par_motor_origen[i], "trabajo virtual")
        self.assertTrue(all(math.isnan(c["Fn"]) for c in r.contactos[i]))      # fuerzas: no se inventan

    def test_exportacion_y_persistencia(self):
        esc = Escenario()
        esc.solucionador.metodo = METODO_ESTATICO
        esc.carga = CargaExterna(constante=0.2)
        esc.contacto.rigidez_n_mm = 1e4
        esc.solucionador.muestras = 9
        r = ejecutar_estudio(self.a, self.lt, esc, "EPITROCOIDAL", huella="h")
        with tempfile.TemporaryDirectory() as d:
            rutas = r.exportar_csv(os.path.join(d, "e.csv"))
            txt = Path(rutas[1]).read_text(encoding="utf-8-sig")
            for col in ("px_mm", "nx", "Fn_N", "Fr_N", "Ft_N", "separacion_mm"):
                self.assertIn(col, txt)
            r.exportar_json(os.path.join(d, "e.json"))
            raw = Path(d, "e.json").read_text(encoding="utf-8")
            self.assertNotIn("NaN", raw)                                     # JSON estricto
            r2 = ResultadoEstudio.from_dict(json.loads(raw))
        np.testing.assert_allclose(r2.arr("par_motor"), r.arr("par_motor"))
        self.assertEqual(r2.huella, "h")
        b = BibliotecaEscenarios()
        b.asociar("Indexer", esc)
        b2 = BibliotecaEscenarios.from_dict(json.loads(json.dumps(b.to_dict())))
        self.assertEqual(b2.de_preset("Indexer").carga.constante, 0.2)
        self.assertEqual(b2.de_preset("Lavadora").carga.constante, 0.0)          # preset sin escenario: sin carga


if __name__ == "__main__":
    unittest.main()


class Dinamica(unittest.TestCase):
    """Integración temporal: la dinámica de contacto gobierna el movimiento de la salida."""

    def esc(self, I=(0.0, 0.0, 0.0), T=0.0):
        from engine.estudio_fisico import METODO_DINAMICO
        e = Escenario()
        e.solucionador.metodo = METODO_DINAMICO
        e.contacto.rigidez_n_mm = 2e4
        e.contacto.amortiguamiento_n_s_mm = 2.0
        e.carga = CargaExterna(constante=T)
        e.dinamica.inercia_entrada_kg_mm2, e.dinamica.inercia_salida, e.dinamica.inercia_planeta_kg_mm2 = I
        return e

    def test_limite_cuasiestatico_sin_inercias(self):
        a = adaptador_para("EPITROCOIDAL", EpitrocoidalEngine(ParametrosEpitrocoidal()))
        lt = LineaTiempo.construir(FabricaPresets.crear("Giro de 90°"), RegistroLeyes())
        r = ejecutar_estudio(a, lt, self.esc(T=0.5), "EPITROCOIDAL")
        self.assertEqual(r.meta["modo"], "dinamico")
        tm = r.arr("par_motor")      # T·rel con rel = −1; el amortiguamiento al entrar un rodillo desvía < 1 %
        np.testing.assert_allclose(np.median(tm), -0.5, atol=1e-6)
        np.testing.assert_allclose(tm, -0.5, atol=5e-3)

    def test_par_inercial_de_la_salida(self):
        """Sin carga: T_m = I_s·rel²·θ̈ (la salida solo acelera por las fuerzas de contacto)."""
        a = adaptador_para("HIPOTROCOIDAL", HipotrocoidalEngine(ParametrosHipotrocoidal(numero_dientes=36)))
        lt = LineaTiempo.construir(FabricaPresets.crear("Giro de 90°"), RegistroLeyes())
        I = 200.0
        r = ejecutar_estudio(a, lt, self.esc(I=(0.0, I, 0.0)), "HIPOTROCOIDAL")
        rel = a.relacion(10.0)
        esperado = I / 1000.0 * rel ** 2 * np.radians(np.interp(r.t, lt.t, lt.acc)) / 1000.0
        err = np.abs(r.arr("par_motor") - esperado)[20:-20]
        self.assertLess(err.max(), 0.03 * np.abs(esperado).max())

    def test_cuatro_mecanismos_y_desviacion_pequena(self):
        lt = LineaTiempo.construir(FabricaPresets.crear("Giro de 90°"), RegistroLeyes())
        for sis, m, alt in mecanismos()[::2]:
            a = adaptador_para(sis, m, None, alt)
            r = ejecutar_estudio(a, lt, self.esc(I=(0.0, 20.0, 1.0), T=0.2), sis)
            self.assertFalse(r.meta["detenido"], sis)
            q0 = np.abs(np.asarray(r.q)[:, 0])
            self.assertLess(q0.max(), 0.01, sis)               # deflexión elástica, no un salto de diente
            self.assertTrue(all(len(f) for f in r.contactos), sis)

    def test_capacidad_perdida_de_sincronismo(self):
        from engine.accionamiento import MODO_CAPACIDAD, ModeloMotor
        a = adaptador_para("EPITROCOIDAL", EpitrocoidalEngine(ParametrosEpitrocoidal()))
        lt = LineaTiempo.construir(FabricaPresets.crear("Giro de 90°"), RegistroLeyes())
        e = self.esc(I=(2000.0, 20000.0, 0.0), T=0.0)
        e.motor = ModeloMotor("Stepper", MODO_CAPACIDAD, curva=[[0.0, 0.002], [100.0, 0.002]])
        r = ejecutar_estudio(a, lt, e, "EPITROCOIDAL")
        self.assertIn("Saturado", r.regimen_motor)
        self.assertTrue(any(ev[2] == "Pérdida de sincronismo" for ev in r.eventos))
        dif = np.abs(r.arr("theta_in") - r.arr("theta_ref"))
        self.assertGreater(dif.max(), 0.1)                      # el movimiento real se aparta del perfil

    def test_requiere_rigidez(self):
        e = self.esc()
        e.contacto.rigidez_n_mm = 0.0
        a = adaptador_para("EPITROCOIDAL", EpitrocoidalEngine(ParametrosEpitrocoidal()))
        lt = LineaTiempo.construir(FabricaPresets.crear("Giro de 90°"), RegistroLeyes())
        with self.assertRaises(ValueError):
            ejecutar_estudio(a, lt, e, "EPITROCOIDAL")


class Optimizacion(unittest.TestCase):
    def test_localizar_contacto_vectorizado_identico_a_la_referencia(self):
        from engine.cinematica_engine import SolverCinematico
        for m in (EpitrocoidalEngine(ParametrosEpitrocoidal()), HipotrocoidalEngine(ParametrosHipotrocoidal(numero_dientes=36))):
            ce, sol = m.contacto, SolverCinematico(m.contexto)
            for alt in (False, True):
                for ang in np.linspace(0, 720, 97):
                    est = sol.resolver("angular", True, alt, ang, 0)
                    idx, cx, cy = ce._rodillos_k_activos(est, alt)
                    idx, dj, cx, cy = ce._dientes_j_activos(idx, cx, cy)
                    for a, b in zip(ce._localizar_contacto(idx, dj, cx, cy),
                                    ce._localizar_contacto_referencia(idx, dj, cx, cy)):
                        np.testing.assert_array_equal(np.asarray(a, float), np.asarray(b, float))

    def test_guia_tecnica_pdf(self):
        from utils.guia import RUTA_GUIA
        self.assertTrue(RUTA_GUIA.exists())
        self.assertGreater(RUTA_GUIA.stat().st_size, 100_000)
