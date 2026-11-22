# -*- coding: utf-8 -*-
"""
utils/recursos.py

Dos arreglos de recursos que Qt Designer deja a medias al regenerar los .py:

1. `asegurar_recursos`: Seleccion_de_sistema.py / PlanetarioV2.py hacen `import Logo_rc`; ese módulo sale de
   compilar Recursos/Logo.qrc con pyside6-rcc. Se (re)compila en ui/designer/ si NO existe o si el .qrc o alguna
   imagen que referencia cambió desde la última compilación (huella SHA-256 en ui/designer/.logo_rc.sha256, ignorada
   por git). Antes solo se compilaba si faltaba, así que un Logo_rc.py viejo dejaba rutas como
   ":/newPrefix/RPSDesign_VID.png" apuntando a recursos que ya no estaban.
2. `normalizar_rutas_designer`: Designer escribe rutas de iconos relativas al .ui ("../../Recursos/x.png"), pero la app
   corre con cwd = raíz del proyecto (main.py hace os.chdir), así que esas rutas no resolvían y los botones salían
   sin imagen. Se reescriben a "Recursos/x.png" en los .py de ui/designer/ (idempotente; se aplica tras cada uic).

Sin dependencias de Qt en tiempo de importación.
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

_RCC_EN_PROCESO = ("import sys; from PySide6.scripts.pyside_tool import rcc; "
                   "sys.argv = ['pyside6-rcc'] + sys.argv[1:]; rcc()")
_PREFIJO_DESIGNER = re.compile(r"""(["'])(?:\.\./)+Recursos/""")


def _huella_qrc(qrc: Path) -> str:
    """SHA-256 del .qrc y de los archivos que referencia (si un PNG cambia, hay que recompilar)."""
    h = hashlib.sha256()
    texto = qrc.read_bytes()
    h.update(texto)
    for rel in re.findall(r"<file[^>]*>([^<]+)</file>", texto.decode("utf-8", "replace")):
        f = qrc.parent / rel.strip()
        h.update(rel.encode("utf-8"))
        if f.exists():
            h.update(f.read_bytes())
    return h.hexdigest()


def asegurar_recursos(raiz) -> bool:
    """True si Logo_rc.py existe y está al día al terminar (ya lo estaba o se compiló ahora)."""
    raiz = Path(raiz)
    destino = raiz / "ui" / "designer" / "Logo_rc.py"
    qrc = raiz / "Recursos" / "Logo.qrc"
    if not qrc.exists():
        return destino.exists() or (raiz / "Logo_rc.py").exists()
    sello = destino.with_name(".logo_rc.sha256")
    huella = _huella_qrc(qrc)
    if destino.exists():
        try:
            if sello.read_text(encoding="utf-8").strip() == huella:
                return True
        except OSError:
            pass                                    # sin sello: no sabemos con qué .qrc se compiló -> recompilar
    elif (raiz / "Logo_rc.py").exists():
        return True                                 # copia manual en la raíz (compatibilidad)
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
            try:
                sello.write_text(huella + "\n", encoding="utf-8")
            except OSError:
                pass
            return True
    return destino.exists()                         # no se pudo recompilar: se usa lo que haya


def normalizar_rutas_designer(raiz) -> list:
    """Reescribe "../../Recursos/" -> "Recursos/" en ui/designer/*.py. Devuelve los archivos modificados."""
    cambiados = []
    carpeta = Path(raiz) / "ui" / "designer"
    for f in sorted(carpeta.glob("*.py")):
        if f.name == "Logo_rc.py":
            continue
        try:
            s = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        nuevo = _PREFIJO_DESIGNER.sub(lambda m: f"{m.group(1)}Recursos/", s)
        if nuevo != s:
            f.write_text(nuevo, encoding="utf-8", newline="")
            cambiados.append(f.name)
    return cambiados
