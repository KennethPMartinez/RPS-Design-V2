# -*- coding: utf-8 -*-
"""
ui/main_menu.py — Seleccion_de_sistema.ui. Cada botón abre la ventana de su sistema y OCULTA (no destruye)
el menú. Migrados a V2: Epitrocoidal, Hipotrocoidal y Trocoidal (botón "cremallera" del menú);
Planetario avisa sin tumbar nada. Las ventanas se importan al abrirse (un fallo no tumba el menú).
"""
from PySide6 import QtWidgets

from config.data_structures import TipoSistema
from ui.errores import manejador_seguro

from Seleccion_de_sistema import Ui_MainWindow   # noqa: E402


def _crear_ventana(tipo: TipoSistema, retorno):
    if tipo is TipoSistema.EPITROCOIDAL:
        from ui.epi_hipo_window import VentanaEpitrocoidal as clase
    elif tipo is TipoSistema.HIPOTROCOIDAL:
        from ui.epi_hipo_window import VentanaHipotrocoidal as clase
    elif tipo is TipoSistema.CREMALLERA:                 # en V2 se llama Trocoidal
        from ui.trocoidal_window import VentanaTrocoidal as clase
    elif tipo is TipoSistema.PLANETARIO:
        from ui.planetary_window import VentanaPlanetario as clase
    else:
        return None
    return clase(retorno=retorno)


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

    def closeEvent(self, e):
        """«Confirmar al salir»: cerrar el menú principal cierra la aplicación."""
        from ui.ajustes_runtime import runtime
        if runtime.estado.general.confirmar_salir and self.ventana_activa is None:
            B = QtWidgets.QMessageBox.StandardButton
            if QtWidgets.QMessageBox.question(self, "Salir", "¿Quieres cerrar RPS Design?", B.Yes | B.No, B.No) != B.Yes:
                e.ignore()
                return
        super().closeEvent(e)
