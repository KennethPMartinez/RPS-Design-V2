# -*- coding: utf-8 -*-
"""utils/recursos.py: normalización de rutas de Designer y huella del .qrc (sin Qt)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils.recursos import _huella_qrc, normalizar_rutas_designer  # noqa: E402


class TestRecursos(unittest.TestCase):
    def test_normaliza_rutas_y_es_idempotente(self):
        with tempfile.TemporaryDirectory() as d:
            carpeta = Path(d) / "ui" / "designer"
            carpeta.mkdir(parents=True)
            f = carpeta / "X.py"
            f.write_text('icon.addFile(u"../../Recursos/a.png")\nicon.addFile(u"Recursos/b.png")\n', encoding="utf-8")
            self.assertEqual(normalizar_rutas_designer(d), ["X.py"])
            self.assertEqual(f.read_text(encoding="utf-8"),
                             'icon.addFile(u"Recursos/a.png")\nicon.addFile(u"Recursos/b.png")\n')
            self.assertEqual(normalizar_rutas_designer(d), [])

    def test_huella_cambia_con_qrc_e_imagen(self):
        with tempfile.TemporaryDirectory() as d:
            qrc = Path(d) / "Logo.qrc"
            png = Path(d) / "a.png"
            png.write_bytes(b"1")
            qrc.write_text('<RCC><qresource prefix="p"><file>a.png</file></qresource></RCC>', encoding="utf-8")
            h1 = _huella_qrc(qrc)
            png.write_bytes(b"2")
            h2 = _huella_qrc(qrc)
            qrc.write_text('<RCC><qresource prefix="q"><file>a.png</file></qresource></RCC>', encoding="utf-8")
            self.assertEqual(len({h1, h2, _huella_qrc(qrc)}), 3)


if __name__ == "__main__":
    unittest.main()
