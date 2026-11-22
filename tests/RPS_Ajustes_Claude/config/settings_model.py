"""Contrato serializable de preferencias RPS Design V2.

No contiene widgets ni valores físicos de proyectos. `desviacion_*` son las
preferencias ya existentes de simulación; NO se convierten automáticamente
 en tolerancias certificadas del perfil geométrico.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict, fields
from typing import Any

SCHEMA_VERSION = 1

UI_ROLES = (
    'Fondo de ventana', 'Paneles / tarjetas', 'Botones', 'Texto principal',
    'Texto secundario', 'Campos de entrada', 'Menús contextuales',
    'Tablas: fondo', 'Selección', 'Bordes', 'Iconos',
    'Aviso / advertencia', 'Éxito / estado', 'Error / estado',
)
TECH_ROLES = (
    'Perfil / engranaje', 'Piñón de rodillos', 'Rodillos activos',
    'Puntos de contacto', 'Línea de acción', 'Curva base', 'Camino de contacto',
    'Circunferencias de paso', 'Ejes de coordenadas', 'Cuadrícula',
    'Fondo de gráficas', 'Etiquetas', 'Sol', 'Anular', 'Planetas',
)

DARK_UI = dict(zip(UI_ROLES, (
    '#24252B', '#30323A', '#404650', '#F1F3F7', '#ABB2BF', '#191B21',
    '#30323A', '#191B21', '#368FED', '#545E69', '#F1F3F7',
    '#E79A40', '#4EA77D', '#D96D6D',
)))
DARK_TECH = dict(zip(TECH_ROLES, (
    '#388AE6', '#F2A33C', '#F1D16B', '#E96363', '#AF85D5',
    '#5DA878', '#CE73CB', '#8794A2', '#B8C2CD', '#536273',
    '#1C1C21', '#EBEFF5', '#388AE6', '#6EC78A', '#F2A33C',
)))
LIGHT_UI = dict(zip(UI_ROLES, (
    '#F2F3F5', '#FFFFFF', '#E3E8EE', '#1F2935', '#526070', '#FFFFFF',
    '#FFFFFF', '#FFFFFF', '#1674C6', '#B5C2CE', '#1F2935',
    '#A96600', '#21784A', '#A33F3F',
)))
LIGHT_TECH = {**DARK_TECH, 'Fondo de gráficas':'#FFFFFF',
              'Etiquetas':'#182633', 'Ejes de coordenadas':'#405061',
              'Cuadrícula':'#CCD3DB', 'Circunferencias de paso':'#687482'}

PRESET_NAMES = (
    'Oscuro', 'Claro', 'Alto contraste', 'Azul profundo — RPS',
    'Deuteranopia', 'Protanopia', 'Tritanopia', 'Blanco y negro',
    'Escala de grises', 'Presentación CAD', 'Plano técnico',
    'Análisis cinemático', 'Personalizado',
)


def preset_colors(name: str) -> tuple[dict[str,str], dict[str,str]]:
    """Paletas editables. Las paletas CVD son propuestas de diferenciación,
    no simulaciones clínicas ni garantía de accesibilidad WCAG.
    """
    u, t = dict(DARK_UI), dict(DARK_TECH)
    if name == 'Claro':
        return dict(LIGHT_UI), dict(LIGHT_TECH)
    if name == 'Azul profundo — RPS':
        u.update({'Fondo de ventana':'#07182E','Paneles / tarjetas':'#102A4B',
                  'Botones':'#16395E','Campos de entrada':'#061428',
                  'Menús contextuales':'#102A4B','Tablas: fondo':'#061428',
                  'Texto principal':'#EAF4FF','Texto secundario':'#B0CBDF',
                  'Selección':'#ED9639','Bordes':'#35567A','Iconos':'#EAF4FF'})
        t.update({'Fondo de gráficas':'#081B35','Perfil / engranaje':'#48A2F8',
                  'Piñón de rodillos':'#F49B38'})
    elif name == 'Alto contraste':
        u.update({'Fondo de ventana':'#000000','Paneles / tarjetas':'#080808',
                  'Botones':'#111111','Campos de entrada':'#000000',
                  'Menús contextuales':'#080808','Tablas: fondo':'#000000',
                  'Texto principal':'#FFFFFF','Texto secundario':'#FFFFFF',
                  'Selección':'#FFFF00','Bordes':'#FFFFFF','Iconos':'#FFFFFF'})
        t.update({'Fondo de gráficas':'#000000','Perfil / engranaje':'#00FFFF',
                  'Piñón de rodillos':'#FFFF00','Etiquetas':'#FFFFFF'})
    elif name in ('Blanco y negro','Plano técnico'):
        u = {k:('#FFFFFF' if k in ('Fondo de ventana','Paneles / tarjetas',
                                   'Campos de entrada','Menús contextuales','Tablas: fondo')
                 else '#000000') for k in UI_ROLES}
        t = {k:('#FFFFFF' if k=='Fondo de gráficas' else '#000000') for k in TECH_ROLES}
        if name == 'Plano técnico':
            u.update({'Fondo de ventana':'#ECEFF1','Botones':'#CFD8DC',
                      'Bordes':'#6D7880'})
            t.update({'Circunferencias de paso':'#777777','Cuadrícula':'#D0D0D0'})
    elif name == 'Escala de grises':
        u.update({'Fondo de ventana':'#2A2A2A','Paneles / tarjetas':'#414141',
                  'Botones':'#565656','Texto principal':'#FFFFFF',
                  'Texto secundario':'#C8C8C8','Selección':'#929292',
                  'Bordes':'#838383'})
        palette=['#EFEFEF','#AAAAAA','#DBDBDB','#FFFFFF','#777777','#BBBBBB',
                 '#888888','#555555','#CECECE','#777777','#121212','#F2F2F2',
                 '#E6E6E6','#999999','#CCCCCC']
        t=dict(zip(TECH_ROLES,palette))
    elif name == 'Presentación CAD':
        u.update({'Fondo de ventana':'#101820','Paneles / tarjetas':'#1B2935',
                  'Campos de entrada':'#0D141C','Selección':'#22B7E9'})
        t.update({'Fondo de gráficas':'#0B1015','Perfil / engranaje':'#00D9FF',
                  'Piñón de rodillos':'#FFD166','Cuadrícula':'#345063'})
    elif name == 'Análisis cinemático':
        u.update({'Selección':'#FFB703'})
        t.update({'Perfil / engranaje':'#53D8FB','Piñón de rodillos':'#FFB703',
                  'Puntos de contacto':'#FF5D73','Camino de contacto':'#80ED99'})
    elif name in ('Deuteranopia','Protanopia','Tritanopia'):
        # Colores con forma y trazos complementarios, evitando asociar
        # el diagnóstico a una única transformación RGB sin validación.
        if name == 'Deuteranopia':
            t.update({'Perfil / engranaje':'#56B4E9','Piñón de rodillos':'#E69F00',
                      'Puntos de contacto':'#F0E442'})
        elif name == 'Protanopia':
            t.update({'Perfil / engranaje':'#0072B2','Piñón de rodillos':'#E69F00',
                      'Puntos de contacto':'#CC79A7'})
        else:
            t.update({'Perfil / engranaje':'#E76F51','Piñón de rodillos':'#92C36E',
                      'Puntos de contacto':'#FFFFFF'})
    return u,t


@dataclass
class General:
    restaurar_sesion: bool = True
    confirmar_salir: bool = True
    guardado_automatico: bool = False
    intervalo_guardado_min: int = 5
    guardar_preferencias: bool = True
    avisos_datos: bool = True
    confirmar_sobrescritura: bool = True


@dataclass
class Calculo:
    decimales: str = '6 decimales'
    estrategia_muestreo: str = 'Adaptativa por tolerancia'
    muestras_uniformes: int = 2001
    max_muestras: int = 30001
    desviacion_lineal_mm: float = 0.0003
    desviacion_angular_grados: float = 0.5
    mostrar_estimacion: bool = False


@dataclass
class Simulacion:
    fps: str = 'Automático (monitor activo)'
    fps_personalizado: int = 120
    vsync_solicitado: bool = False
    backend: str = 'CPU — NumPy'
    render: str = 'Software'
    bajar_fps_inactivo: bool = True
    detener_invalido: bool = True
    conservar_pausa: bool = True
    cache_geometria: bool = True
    basada_en_contacto: bool = False


@dataclass
class EstiloLinea:
    ancho: float = 1.0
    tipo: str = 'Continua'
    terminacion: str = 'Plana'
    union: str = 'Bisel'
    opacidad: int = 100


def estilos_iniciales():
    return {name: asdict(EstiloLinea()) for name in (
        'Perfil de engranaje','Piñón','Rodillos activos','Camino de contacto',
        'Curva base','Circunferencias de paso','Línea de acción','Ejes','Cuadrícula')}


@dataclass
class Apariencia:
    preset: str = 'Azul profundo — RPS'
    ui_colores: dict[str,str] = field(default_factory=lambda:preset_colors('Azul profundo — RPS')[0])
    tecnicos_colores: dict[str,str] = field(default_factory=lambda:preset_colors('Azul profundo — RPS')[1])
    estilos_lineas: dict[str,dict] = field(default_factory=estilos_iniciales)
    antialias: bool = True
    fuente_ui: str = 'Segoe UI'
    tamano_ui: int = 10
    negrita_ui: bool = False
    fuente_graficas: str = 'Consolas'
    tamano_graficas: int = 9
    negrita_graficas: bool = False


@dataclass
class Exportacion:
    formato_imagen: str = 'PNG'
    resolucion_imagen: str = '1920 × 1080 (Full HD)'
    imagen_ancho: int = 1920
    imagen_alto: int = 1080
    jpeg_calidad: int = 95
    mantener_aspecto_imagen: bool = True
    fondo_transparente: bool = False
    antialias_export: bool = True
    formato_video: str = 'MP4 — H.264'
    resolucion_video: str = '1920 × 1080 (Full HD)'
    video_ancho: int = 1920
    video_alto: int = 1080
    video_fps: int = 30
    video_crf: int = 23
    mantener_aspecto_video: bool = True
    video_determinista: bool = True


@dataclass
class SettingsState:
    version: int = SCHEMA_VERSION
    general: General = field(default_factory=General)
    calculo: Calculo = field(default_factory=Calculo)
    simulacion: Simulacion = field(default_factory=Simulacion)
    apariencia: Apariencia = field(default_factory=Apariencia)
    exportacion: Exportacion = field(default_factory=Exportacion)

    def to_dict(self)->dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str,Any]) -> 'SettingsState':
        if not isinstance(data, dict):
            return cls()
        def create(typ,key):
            raw=data.get(key,{})
            if not isinstance(raw,dict):raw={}
            names={f.name for f in fields(typ)}
            return typ(**{k:v for k,v in raw.items() if k in names})
        return cls(version=SCHEMA_VERSION, general=create(General,'general'),
                   calculo=create(Calculo,'calculo'),simulacion=create(Simulacion,'simulacion'),
                   apariencia=create(Apariencia,'apariencia'),
                   exportacion=create(Exportacion,'exportacion'))

    def validate(self)->None:
        p=self.calculo; s=self.simulacion; e=self.exportacion
        if not (0<=p.desviacion_lineal_mm<=.1 and 0<=p.desviacion_angular_grados<=1):
            raise ValueError('Desviaciones fuera de rango')
        if not (101<=p.muestras_uniformes<=1000001 and 1001<=p.max_muestras<=1000001):
            raise ValueError('Número de muestras fuera de rango')
        if p.estrategia_muestreo=='Adaptativa por tolerancia' and p.max_muestras<2:
            raise ValueError('Límite de muestras inválido')
        if not 1<=s.fps_personalizado<=1000:
            raise ValueError('FPS personalizados fuera de rango')
        if any(not 100<=v<=16384 for v in (e.imagen_ancho,e.imagen_alto,e.video_ancho,e.video_alto)):
            raise ValueError('Dimensiones de exportación fuera de rango')
        if not (1<=e.jpeg_calidad<=100 and 0<=e.video_crf<=51 and e.video_fps in (24,30,60,120)):
            raise ValueError('Calidad o FPS de exportación inválidos')
        if e.formato_video not in ('MP4 — H.264','WebM — VP9 (por implementar)'):
            raise ValueError('Formato de video no reconocido')
        if not 1<=self.general.intervalo_guardado_min<=120:
            raise ValueError('Intervalo de guardado no válido')
        for colors in (self.apariencia.ui_colores,self.apariencia.tecnicos_colores):
            for value in colors.values():
                import re
                if not isinstance(value,str) or not re.fullmatch('#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?',value):
                    raise ValueError('Color HEX inválido: '+str(value))
