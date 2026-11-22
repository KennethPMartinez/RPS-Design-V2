"""Tema global Qt + PyQtGraph. No cambia visibilidad, zoom, ejes ni transformadas.

La integración debe reemplazar los colores fijos en widgets específicos del
proyecto por roles de esta paleta, o llamar apply_to_plot() tras crearlos.
"""
from __future__ import annotations
from PySide6 import QtGui, QtCore, QtWidgets
from config.settings_model import Apariencia


def qcolor(css:str)->QtGui.QColor:
    """Interpreta #RRGGBB y #RRGGBBAA (alfa final, convención del selector)."""
    if len(css)==9:
        c=QtGui.QColor(css[:7]);c.setAlpha(int(css[7:],16));return c
    return QtGui.QColor(css)


_PENS={'Continua':QtCore.Qt.PenStyle.SolidLine,
       'Discontinua':QtCore.Qt.PenStyle.DashLine,
       'Punteada':QtCore.Qt.PenStyle.DotLine,
       'Raya-punto':QtCore.Qt.PenStyle.DashDotLine,
       'Raya-punto-punto':QtCore.Qt.PenStyle.DashDotDotLine}
_CAPS={'Plana':QtCore.Qt.PenCapStyle.FlatCap,
       'Redondeada':QtCore.Qt.PenCapStyle.RoundCap,
       'Cuadrada':QtCore.Qt.PenCapStyle.SquareCap}
_JOINS={'Bisel':QtCore.Qt.PenJoinStyle.BevelJoin,
        'Redondeada':QtCore.Qt.PenJoinStyle.RoundJoin,
        'Inglete':QtCore.Qt.PenJoinStyle.MiterJoin}

# objeto PyQtGraph -> rol semántico / estilo; solo objetos existentes.
PLOT_ITEMS={
    'c_patron':('Perfil / engranaje','Perfil de engranaje'),
    'c_pinon':('Piñón de rodillos','Piñón'),
    'c_roll_act':('Rodillos activos','Rodillos activos'),
    'c_camino':('Camino de contacto','Camino de contacto'),
    'c_base':('Curva base','Curva base'),
    'c_paso_eng':('Circunferencias de paso','Circunferencias de paso'),
    'c_paso_pin':('Circunferencias de paso','Circunferencias de paso'),
    'c_paso_sol':('Circunferencias de paso','Circunferencias de paso'),
    'c_paso_anu':('Circunferencias de paso','Circunferencias de paso'),
    'c_paso_pla':('Circunferencias de paso','Circunferencias de paso'),
    'c_accion':('Línea de acción','Línea de acción'),
    'c_sol':('Sol','Perfil de engranaje'),
    'c_anu':('Anular','Perfil de engranaje'),
    'c_pla':('Planetas','Piñón'),
}


class ThemeManager(QtCore.QObject):
    applied=QtCore.Signal()

    def __init__(self,app:QtWidgets.QApplication):
        super().__init__(app)
        self.app=app
        self.current=Apariencia()

    @staticmethod
    def pen(color:str,options:dict|None=None)->QtGui.QPen:
        cfg=options or {}
        c=qcolor(color);c.setAlpha(round(c.alpha()*max(0,min(100,int(cfg.get('opacidad',100))))/100))
        pen=QtGui.QPen(c)
        pen.setWidthF(max(.1,float(cfg.get('ancho',1))))
        pen.setStyle(_PENS.get(cfg.get('tipo','Continua'),QtCore.Qt.PenStyle.SolidLine))
        pen.setCapStyle(_CAPS.get(cfg.get('terminacion','Plana'),QtCore.Qt.PenCapStyle.FlatCap))
        pen.setJoinStyle(_JOINS.get(cfg.get('union','Bisel'),QtCore.Qt.PenJoinStyle.BevelJoin))
        return pen

    def apply(self,visual:Apariencia)->None:
        self.current=visual
        u,t=visual.ui_colores,visual.tecnicos_colores
        pal=QtGui.QPalette()
        role={
            'Window':'Fondo de ventana', 'WindowText':'Texto principal',
            'Base':'Campos de entrada','AlternateBase':'Paneles / tarjetas',
            'Text':'Texto principal','Button':'Botones','ButtonText':'Texto principal',
            'Highlight':'Selección','HighlightedText':'Texto principal',
            'ToolTipBase':'Paneles / tarjetas','ToolTipText':'Texto principal',
            'PlaceholderText':'Texto secundario','Mid':'Bordes'
        }
        for name,key in role.items():
            if key in u:
                pal.setColor(getattr(QtGui.QPalette.ColorRole,name),qcolor(u[key]))
        # Texto de selección basado en luminancia del resaltado, importante en alto contraste.
        selected=qcolor(u.get('Selección','#368FED'))
        selection_text=QtGui.QColor('#101010') if selected.lightness()>140 else QtGui.QColor('#FFFFFF')
        pal.setColor(QtGui.QPalette.ColorRole.HighlightedText,selection_text)
        for name in ('WindowText','Text','ButtonText'):
            c=qcolor(u.get('Texto secundario','#808080'))
            pal.setColor(QtGui.QPalette.ColorGroup.Disabled,getattr(QtGui.QPalette.ColorRole,name),c)
        self.app.setStyle('Fusion')
        self.app.setPalette(pal)
        font=QtGui.QFont(visual.fuente_ui)
        font.setPointSize(visual.tamano_ui);font.setBold(visual.negrita_ui)
        self.app.setFont(font)
        # Uso moderado de QSS: colores base vienen de QPalette; los textos de
        # QMessageBox/QFileDialog y los QMenu heredan la paleta.
        self.app.setStyleSheet('''
            QToolTip { border: 1px solid %(border)s; background: %(panel)s; color: %(txt)s; }
            QMenu { border: 1px solid %(border)s; }
            QMenu::item:selected { background: %(selection)s; }
            QGroupBox { border: 1px solid %(border)s; border-radius: 5px;
                        margin-top: 8px; padding-top: 7px; }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }
            ''' % dict(border=u.get('Bordes','#555555'),panel=u.get('Paneles / tarjetas','#333333'),
                       txt=u.get('Texto principal','#FFFFFF'),selection=u.get('Selección','#3768A0')))
        try:
            import pyqtgraph as pg
            pg.setConfigOptions(background=qcolor(t.get('Fondo de gráficas','#000000')),
                                foreground=qcolor(t.get('Etiquetas','#FFFFFF')),
                                antialias=bool(visual.antialias))
            # Aplica a TODAS las gráficas vivas, incluidas las de ventanas auxiliares.
            for w in self.app.allWidgets():
                if isinstance(w,pg.PlotWidget):
                    self.apply_to_plot(w)
        except ImportError:
            pass
        self.applied.emit()

    def apply_to_plot(self,plot)->None:
        """No altera geometría, visibilidad, rangos, transformadas ni datos."""
        try:
            import pyqtgraph as pg
            if not isinstance(plot,pg.PlotWidget):return
        except ImportError:
            return
        v=self.current;t=v.tecnicos_colores
        plot.setBackground(qcolor(t.get('Fondo de gráficas','#000000')))
        item=plot.getPlotItem()
        for axis in ('left','right','top','bottom'):
            ax=item.getAxis(axis)
            ax.setPen(self.pen(t.get('Ejes de coordenadas','#AAAAAA')))
            ax.setTextPen(self.pen(t.get('Etiquetas','#FFFFFF')))
            f=QtGui.QFont(v.fuente_graficas,v.tamano_graficas)
            f.setBold(v.negrita_graficas)
            ax.setStyle(tickFont=f)
        for attr,(role,stylename) in PLOT_ITEMS.items():
            obj=getattr(plot,attr,None)
            if obj is not None and hasattr(obj,'setPen'):
                obj.setPen(self.pen(t.get(role,'#FFFFFF'),v.estilos_lineas.get(stylename,{})))
        obj=getattr(plot,'s_contactos',None)
        if obj is not None:
            obj.setBrush(pg.mkBrush(qcolor(t.get('Puntos de contacto','#FF7777'))))
        for attribute in ('_labels_rod','_labels_dient','_lab_rod','_lab_dient'):
            for textitem in getattr(plot,attribute,[]) or []:
                if hasattr(textitem,'setColor'):
                    textitem.setColor(qcolor(t.get('Etiquetas','#FFFFFF')))
                if hasattr(textitem,'setFont'):
                    f=QtGui.QFont(v.fuente_graficas,v.tamano_graficas)
                    f.setBold(v.negrita_graficas)
                    textitem.setFont(f)
        # Respetar la elección de visibilidad del usuario: no invocar showGrid().
