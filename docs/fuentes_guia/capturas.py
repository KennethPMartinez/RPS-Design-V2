import os, sys, tempfile, time
os.environ["QT_QPA_PLATFORM"]="offscreen"; os.environ["RPS_DATA_DIR"]=tempfile.mkdtemp()
RAIZ=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")); sys.path.insert(0,RAIZ); os.chdir(RAIZ)
from PySide6 import QtWidgets, QtCore
import main as M
M.localizar_modulos_ui()
from utils.recursos import asegurar_recursos, normalizar_rutas_designer
APP = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
from widgets.pg_helpers import configurar_pyqtgraph; configurar_pyqtgraph(False, True)
from ui.ajustes_runtime import runtime
runtime.iniciar(APP); runtime.aplicar_tema_guardado()
runtime.estado.general.restaurar_sesion=False; runtime.estado.general.confirmar_salir=False
runtime.estado.simulacion.basada_en_contacto=True
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)), "img") + os.sep
def shot(w, n, size=None):
    if size: w.resize(*size)
    w.show(); APP.processEvents(); time.sleep(0.05); APP.processEvents()
    w.grab().save(OUT+n+".png")
from ui.main_menu import MenuPrincipal
m=MenuPrincipal(); shot(m,"menu")
from ui.epi_hipo_window import VentanaEpitrocoidal
from ui.planetary_window import VentanaPlanetario
from ui.trocoidal_window import VentanaTrocoidal
w=VentanaEpitrocoidal(); shot(w,"epi_manual",(1300,820))
w.ui.comboBox_modo_sim.setCurrentIndex(1)
ed=w._editar_linea_tiempo(); shot(ed,"editor_cinematico",(1400,900))
u=ed.ui; u.tabRegimenes.setCurrentWidget(u.tabDinamico)
u.comboBox_preset.setCurrentText("Indexer"); u.pushButton_Aplicar_preset.click(); u.comboModeloContacto.setCurrentIndex(1); u.spinRigidezNormal.setValue(2e4); u.spinAmortiguamientoNormal.setValue(2.0)
pass
APP.processEvents(); shot(ed,"editor_accionamiento")
u.listSeccionesEstudio.setCurrentRow(1); shot(ed,"editor_cargas")
u.listSeccionesEstudio.setCurrentRow(2); shot(ed,"editor_contacto")
u.listSeccionesEstudio.setCurrentRow(3); shot(ed,"editor_solucionador")
u.btnEjecutarEstudio.click(); g=w.gestor_estudio
while g.calculando(): APP.processEvents(); time.sleep(0.01)
APP.processEvents()
shot(ed,"editor_par_t")
ed.dinamico.ver_resultados(); u.tabTipoResultado.setCurrentIndex(0); ed.dinamico.cursores[0].setValue(10.0); APP.processEvents(); shot(ed,"editor_fuerzas")
u.tabTipoResultado.setCurrentIndex(1); shot(ed,"editor_momentos")
u.tabTipoResultado.setCurrentIndex(2); shot(ed,"editor_eventos")
u.tabGraficasEstudio.setCurrentIndex(4); shot(ed,"editor_diagnostico")
ed.ui.pushButton_9.click(); APP.processEvents()
w.sim._menu._set_amplificacion(1000, True); w.sim._menu._set_indicador("relacion", True)
w._t=0.3; w._mostrar_auto(); shot(w,"epi_contacto")
p=VentanaPlanetario(); p.resize(1300,860); p.ui.comboBox_modo_sim.setCurrentIndex(1); p._t=3; p._mostrar_auto(); shot(p,"planetario")
t=VentanaTrocoidal(); shot(t,"trocoidal",(1300,820))
from ui.settings_window import SettingsWindow
sw=SettingsWindow(None, on_apply=lambda e: None, store=runtime.store, theme_manager=runtime.theme)
d=getattr(sw,"dialog",sw); shot(d,"ajustes")
print("ok", g.estado, g.detalle)
