# -*- coding: utf-8 -*-
"""RPS Design V2 — punto de entrada.  Uso:  python main.py"""
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
os.chdir(RAIZ)                                   # Seleccion_de_sistema.py usa rutas relativas "Recursos/..."
os.environ.setdefault("PYQTGRAPH_QT_LIB", "PySide6")   # antes de importar pyqtgraph
# Módulos generados por Qt Designer: pueden vivir en la raíz o en ui/designer/
for ruta in (RAIZ, os.path.join(RAIZ, "ui", "designer")):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

from utils.recursos import asegurar_recursos, normalizar_rutas_designer   # noqa: E402
asegurar_recursos(RAIZ)                         # compila Recursos/Logo.qrc -> ui/designer/Logo_rc.py (si falta o cambió)
normalizar_rutas_designer(RAIZ)                 # "../../Recursos/" -> "Recursos/" (el cwd es la raíz)

from PySide6 import QtWidgets   # noqa: E402

from config.app_settings import ajustes          # noqa: E402
from ui.style_manager import aplicar_tema        # noqa: E402
from widgets.pg_helpers import configurar_pyqtgraph   # noqa: E402


def main() -> int:
    app = QtWidgets.QApplication(sys.argv)
    from ui.ajustes_runtime import runtime
    runtime.iniciar(app)
    configurar_pyqtgraph(ajustes.render_opengl, ajustes.modo_oscuro)
    aplicar_tema(app, ajustes.modo_oscuro)
    runtime.aplicar_tema_guardado()
    from ui.main_menu import MenuPrincipal
    menu = MenuPrincipal()
    menu.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
