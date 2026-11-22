"""Tests sin PySide6: contrato de modelos, presets y .ui entregado."""
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from config.settings_model import SettingsState,PRESET_NAMES,preset_colors

class TestContract(unittest.TestCase):
    def test_roundtrip(self):
        state=SettingsState()
        state.simulacion.basada_en_contacto=True
        state.exportacion.video_fps=60
        other=SettingsState.from_dict(state.to_dict())
        other.validate()
        self.assertEqual(other.to_dict(),state.to_dict())

    def test_all_presets(self):
        for name in PRESET_NAMES:
            if name=='Personalizado':continue
            ui,tech=preset_colors(name)
            self.assertTrue(ui and tech)
            for color in list(ui.values())+list(tech.values()):
                self.assertTrue(color.startswith('#') and len(color)==7)

    def test_ui_widgets(self):
        root=ET.parse(ROOT/'ui/designer/Ajustes.ui')
        names=[w.get('name') for w in root.findall('.//widget')]
        self.assertEqual(len(names),len(set(names)))
        self.assertNotIn('groupPreviewTema',names)
        from ui.settings_window import ALIAS_WIDGETS
        # El .ui del repo es el del usuario (nombres genéricos de Designer): se resuelven con ALIAS_WIDGETS.
        # comboFPSVideo / comboResolucionVideo / spinCRFVideo aún no existen en ese .ui (son OPCIONALES en el controlador).
        for name in ('chkSimulacionPorContacto','treeColoresUI','treeColoresTecnicos',
                     'btnCancelar','btnAplicar','btnAceptar','btnRestaurar'):
            self.assertTrue(name in names or ALIAS_WIDGETS.get(name) in names,name)

if __name__=='__main__':unittest.main()
