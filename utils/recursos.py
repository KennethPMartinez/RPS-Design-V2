# -*- coding: utf-8 -*-
"""
utils/recursos.py

Seleccion_de_sistema.py (generado por Qt Designer) hace `import Logo_rc`: ese módulo se obtiene compilando
Recursos/Logo.qrc con pyside6-rcc. `asegurar_recursos` lo genera en ui/designer/ si todavía no existe, así
nadie tiene que acordarse del comando tras clonar el repositorio (o tras cambiar el logo: borra Logo_rc.py).
Sin dependencias de Qt en tiempo de importación.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_RCC_EN_PROCESO = ("import sys; from PySide6.scripts.pyside_tool import rcc; "
                   "sys.argv = ['pyside6-rcc'] + sys.argv[1:]; rcc()")


def asegurar_recursos(raiz) -> bool:
    """True si Logo_rc.py existe al terminar (ya estaba o se compiló ahora)."""
    raiz = Path(raiz)
    destino = raiz / "ui" / "designer" / "Logo_rc.py"
    if destino.exists() or (raiz / "Logo_rc.py").exists():
        return True
    qrc = raiz / "Recursos" / "Logo.qrc"
    if not qrc.exists():
        return False
    comandos = []
    exe = Path(sys.executable).parent / ("pyside6-rcc.exe" if os.name == "nt" else "pyside6-rcc")
    if exe.exists():
        comandos.append([str(exe), str(qrc), "-o", str(destino)])
    comandos.append([sys.executable, "-c", _RCC_EN_PROCESO, str(qrc), "-o", str(destino)])
    for cmd in comandos:
        try:
            subprocess.run(cmd, check=True, capture_output=True, cwd=str(raiz))
        except (OSError, subprocess.CalledProcessError) as e:
            print(f"[recursos] {cmd[0]} falló: {e}", file=sys.stderr)
            continue
        if destino.exists():
            return True
    return False
