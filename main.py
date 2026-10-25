# -*- coding: utf-8 -*-
"""RPS Design V2 — punto de entrada.  Uso:  python main.py   (también funciona renombrado a main.pyw)"""
import os
import sys
import traceback

RAIZ = os.path.dirname(os.path.abspath(__file__))
os.chdir(RAIZ)                                   # Seleccion_de_sistema.py usa rutas relativas "Recursos/..."
os.environ.setdefault("PYQTGRAPH_QT_LIB", "PySide6")   # antes de importar pyqtgraph
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

# Módulos generados por Qt Designer (pyside6-uic). Se buscan en TODA la carpeta del proyecto.
MODULOS_UI = ["Seleccion_de_sistema", "EpitrocoidalV2", "ToothProfile_Window", "Graficas_Window",
              "Perfildevelocidad_simulador_Window", "Mostrar_Ocultar_Epitrocoide"]

from PySide6 import QtWidgets   # noqa: E402


def localizar_modulos_ui() -> list:
    """Añade a sys.path la carpeta de cada módulo de Designer y devuelve los que NO aparecen."""
    pendientes = set(MODULOS_UI)
    for base, dirs, files in os.walk(RAIZ):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", ".venv", "venv", "tests")]
        for m in list(pendientes):
            if f"{m}.py" in files:
                if base not in sys.path:
                    sys.path.insert(0, base)
                pendientes.discard(m)
    return sorted(pendientes)


def _mostrar_error(titulo: str, detalle: str) -> None:
    print(detalle, file=sys.stderr)              # con .pyw no hay consola: se muestra también en un diálogo
    if QtWidgets.QApplication.instance() is not None:
        cuadro = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Critical, titulo, detalle.splitlines()[0])
        cuadro.setDetailedText(detalle)
        cuadro.exec()


def main() -> int:
    app = QtWidgets.QApplication(sys.argv)
    sys.excepthook = lambda t, v, tb: _mostrar_error(
        "Error inesperado", "".join(traceback.format_exception(t, v, tb)))

    faltan = localizar_modulos_ui()
    if faltan:
        _mostrar_error(
            "Faltan archivos de Qt Designer",
            "No se encontraron estos archivos en la carpeta del proyecto:\n  " + "\n  ".join(f"{m}.py" for m in faltan)
            + f"\n\nCópialos a:\n  {os.path.join(RAIZ, 'ui', 'designer')}\n(o a la raíz del proyecto) y vuelve a abrir."
            "\nSeleccion_de_sistema también necesita la carpeta 'Recursos/' junto a main.")
        return 1

    from config.app_settings import ajustes
    from hardware.motor_controller import obtener_controlador
    from ui.style_manager import aplicar_tema
    from widgets.pg_helpers import configurar_pyqtgraph

    configurar_pyqtgraph(ajustes.render_opengl, ajustes.modo_oscuro)
    aplicar_tema(app, ajustes.modo_oscuro)
    app.aboutToQuit.connect(lambda: obtener_controlador().desconectar())   # frena y cierra el puerto
    from ui.main_menu import MenuPrincipal
    menu = MenuPrincipal()
    menu.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
