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
MODULOS_UI = ["Seleccion_de_sistema", "Epi_HipotrocoidalV2", "TrocoidalV2", "ToothProfile_Window",
              "Graficas_Window", "Perfildevelocidad_simulador_Window", "Mostrar_Ocultar_Epitrocoidal", "Mostrar_Ocultar_Epitrocoide",
              "Mostrar_Ocultar_Hipotrocoidal", "Mostrar_Ocultar_Trocoidal",
              "PlanetarioV2", "Graficas_Window_PlanetarioV2", "ToothProfile_Window_PlanetarioV2", "Logo_rc"]

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
    # Nombres alternativos que Designer pudo generar (el diálogo acepta cualquiera de los dos)
    for oficial, alterno in (("Mostrar_Ocultar_Epitrocoidal", "Mostrar_Ocultar_Epitrocoide"),):
        if oficial not in pendientes or alterno not in pendientes:     # basta con que exista uno
            pendientes.discard(oficial)
            pendientes.discard(alterno)
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
    from utils.recursos import asegurar_recursos, normalizar_rutas_designer
    asegurar_recursos(RAIZ)             # Logo_rc.py (Recursos/Logo.qrc); se recompila si el .qrc cambió
    normalizar_rutas_designer(RAIZ)     # "../../Recursos/" -> "Recursos/" (el cwd es la raíz)
    faltan = localizar_modulos_ui()
    if faltan:
        _mostrar_error(
            "Faltan archivos de Qt Designer",
            "No se encontraron estos archivos en la carpeta del proyecto:\n  " + "\n  ".join(f"{m}.py" for m in faltan)
            + f"\n\nCópialos a:\n  {os.path.join(RAIZ, 'ui', 'designer')}\n(o a la raíz del proyecto) y vuelve a abrir."
            "\nSeleccion_de_sistema también necesita la carpeta 'Recursos/' junto a main.")
        return 1

    from config.app_settings import ajustes
    from ui.style_manager import aplicar_tema
    from widgets.pg_helpers import configurar_pyqtgraph

    from ui.ajustes_runtime import runtime
    runtime.iniciar(app)                # QSettings -> ajustes (OpenGL, backend, desviaciones) ANTES de crear ventanas
    configurar_pyqtgraph(ajustes.render_opengl, ajustes.modo_oscuro)
    aplicar_tema(app, ajustes.modo_oscuro)
    runtime.aplicar_tema_guardado()     # preset/colores/fuentes/trazos guardados
    from ui.main_menu import MenuPrincipal
    menu = MenuPrincipal()
    menu.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
