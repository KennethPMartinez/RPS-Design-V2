"""Persistencia QSettings para preferencias; no guarda proyectos ni rutas de exportación."""
from __future__ import annotations
import json
from PySide6 import QtCore
from config.settings_model import SettingsState

class SettingsStore:
    KEY='preferences/v1'
    THEMES_KEY='preferences/custom_themes/v1'
    def __init__(self, organization='RPSDesign', application='V2'):
        self.qs=QtCore.QSettings(organization, application)

    def load(self)->SettingsState:
        raw=self.qs.value(self.KEY)
        if not raw:
            return SettingsState()
        try:
            state=SettingsState.from_dict(json.loads(str(raw)))
            state.validate()
            return state
        except (ValueError,TypeError,KeyError):
            # No bloquea el inicio por archivos de configuración incompatibles.
            return SettingsState()

    def save(self,settings:SettingsState)->None:
        settings.validate()
        if not settings.general.guardar_preferencias:
            self.qs.remove(self.KEY)
        else:
            self.qs.setValue(self.KEY,json.dumps(settings.to_dict(),ensure_ascii=False))
        self.qs.sync()
        if self.qs.status()!=QtCore.QSettings.Status.NoError:
            raise OSError('QSettings no pudo guardar las preferencias')

    def custom_themes(self)->dict:
        try:
            data=json.loads(str(self.qs.value(self.THEMES_KEY,'{}')))
            return data if isinstance(data,dict) else {}
        except (ValueError,TypeError):
            return {}

    def save_custom_theme(self,name:str,theme:dict)->None:
        name=name.strip()
        if not name:
            raise ValueError('El nombre del preset no puede estar vacío')
        data=self.custom_themes()
        data[name]=theme
        self.qs.setValue(self.THEMES_KEY,json.dumps(data,ensure_ascii=False))
        self.qs.sync()
        if self.qs.status()!=QtCore.QSettings.Status.NoError:
            raise OSError('No se pudo guardar el preset')
