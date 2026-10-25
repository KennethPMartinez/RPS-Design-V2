# -*- coding: utf-8 -*-
"""
ui/main_menu.py — Seleccion_de_sistema.ui (sin cambios de comportamiento respecto a V1).
Cada botón abre la ventana de su sistema y OCULTA (no destruye) el menú. En V2 solo
Epitrocoidal está migrado; los demás avisan sin tumbar nada.
"""
from PySide6 import QtWidgets

from config.data_structures import TipoSistema
from ui.errores import manejador_seguro

from Seleccion_de_sistema import Ui_MainWindow   # noqa: E402


def _crear_ventana(tipo: TipoSistema, retorno):
    if tipo is TipoSistema.EPITROCOIDAL:
        from ui.epitrocoidal_window import VentanaEpitrocoidalV2
        return VentanaEpitrocoidalV2(retorno=retorno)
    return None


class MenuPrincipal(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ventana_activa = None
        for boton, tipo in ((self.ui.pushButton_cremallera, TipoSistema.CREMALLERA),
                            (self.ui.pushButton_hipotrocoidal, TipoSistema.HIPOTROCOIDAL),
                            (self.ui.pushButton_epitrocoidal, TipoSistema.EPITROCOIDAL),
                            (self.ui.pushButton_planetario, TipoSistema.PLANETARIO)):
            boton.clicked.connect(lambda *_, t=tipo: self._abrir_sistema(t))

    @manejador_seguro
    def _abrir_sistema(self, tipo: TipoSistema):
        try:
            ventana = _crear_ventana(tipo, self)
        except Exception as e:
            import traceback; traceback.print_exc()
            QtWidgets.QMessageBox.warning(self, "No disponible", f"'{tipo.name.title()}' falló al abrirse: {e}")
            return
        if ventana is None:
            QtWidgets.QMessageBox.information(self, "Próximamente",
                                              f"El sistema '{tipo.name.title()}' aún no está migrado a V2.")
            return
        self.ventana_activa = ventana
        ventana.show()
        self.hide()

    def mostrar_de_nuevo(self):
        self.ventana_activa = None
        self.show()
