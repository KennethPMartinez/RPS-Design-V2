"""Verifica los nombres literales de widgets usados por SettingsWindow."""
from pathlib import Path
from xml.etree import ElementTree as ET
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
class TestWidgetRefs(unittest.TestCase):
    def test_controller_names_present(self):
        source=(ROOT/'ui/settings_window.py').read_text(encoding='utf8')
        refs=set(re.findall(r"self\.w\(['\"]([A-Za-z]\w*)['\"]",source))
        names={el.attrib['name'] for el in ET.parse(ROOT/'ui/designer/Ajustes.ui').findall('.//widget')}
        self.assertFalse(refs-names, f'Controladores huérfanos: {sorted(refs-names)}')

if __name__=='__main__':unittest.main()
