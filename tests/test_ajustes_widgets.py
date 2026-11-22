"""Nombres de widgets que usa SettingsWindow frente al Ajustes.ui REAL del repo (con sus alias de Designer)."""
import re
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ui.settings_window import ALIAS_WIDGETS, OPCIONALES  # noqa: E402


class TestWidgetRefs(unittest.TestCase):
    def test_controller_names_present(self):
        source = (ROOT / "ui/settings_window.py").read_text(encoding="utf8")
        refs = set(re.findall(r"self\.w\(['\"]([A-Za-z]\w*)['\"]", source))
        names = {el.attrib["name"] for el in ET.parse(ROOT / "ui/designer/Ajustes.ui").findall(".//widget")}
        resueltos = {n if n in names else ALIAS_WIDGETS.get(n, n) for n in refs}
        faltan = {n for n in resueltos - names if n not in OPCIONALES}
        self.assertFalse(faltan, f"Controladores huérfanos: {sorted(faltan)}")

    def test_opcionales_ausentes_solo_los_de_video(self):
        names = {el.attrib["name"] for el in ET.parse(ROOT / "ui/designer/Ajustes.ui").findall(".//widget")}
        self.assertEqual({n for n in OPCIONALES if n not in names}, set(OPCIONALES) - names)


if __name__ == "__main__":
    unittest.main()
