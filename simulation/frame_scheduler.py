"""Cadencia visual: autónoma del tiempo físico/virtual de simulación.

Se acopla a un QTimer existente de VentanaSistemaBase. V-Sync real no se
puede garantizar desde este módulo, que NO configura swaps de OpenGL.
"""
from __future__ import annotations
from PySide6 import QtCore, QtGui, QtWidgets


def fps_monitor(ventana:QtWidgets.QWidget,default:int=60)->int:
    handle=ventana.windowHandle()
    screen=handle.screen() if handle is not None else QtGui.QGuiApplication.primaryScreen()
    hz=screen.refreshRate() if screen is not None else 0
    return max(1,round(hz)) if 1<=hz<=1000 else default


def resolver_fps(modo:str,custom:int,ventana:QtWidgets.QWidget)->int|None:
    """None=sin tope de temporizador (Qt interval=0), no V-Sync real."""
    if 'Uncapped' in modo:return None
    if 'Automático' in modo:return fps_monitor(ventana)
    if 'Personalizado' in modo:return max(1,min(1000,int(custom)))
    try:
        return max(1,int(modo.split(' ')[0]))
    except (ValueError,IndexError):
        return fps_monitor(ventana)


def configurar_timer(timer:QtCore.QTimer,ventana:QtWidgets.QWidget,modo:str,personalizado:int,
                     inactivo:bool=False,reducir_inactivo:bool=False)->int|None:
    """Mantener _tick basado en time.perf_counter() y NO en dt=1/FPS."""
    fps=resolver_fps(modo,personalizado,ventana)
    if inactivo and reducir_inactivo:
        fps=min(fps or 60,15)
    timer.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
    timer.setInterval(0 if fps is None else max(1,round(1000.0/fps)))
    return fps


class FrameScheduler(QtCore.QObject):
    """Actualiza el intervalo al cambiar ajustes/pantalla/actividad.

    Instanciar DESPUÉS de construir QMainWindow/QTimer y conservar referencia.
    """
    def __init__(self,window:QtWidgets.QWidget,timer:QtCore.QTimer,mode='Automático (monitor activo)',
                 custom=120,reduce_inactive=True):
        super().__init__(window)
        self.window=window;self.timer=timer;self.mode=mode;self.custom=custom
        self.reduce_inactive=reduce_inactive
        self._connected_handle=None
        self.window.installEventFilter(self)
        self.update()

    def set_preferences(self,mode:str,custom:int,reduce_inactive:bool)->None:
        self.mode=mode;self.custom=custom;self.reduce_inactive=reduce_inactive
        self.update()

    def update(self)->None:
        handle=self.window.windowHandle()
        if handle is not None and handle is not self._connected_handle:
            handle.screenChanged.connect(lambda _screen:self.update())
            self._connected_handle=handle
        configurar_timer(self.timer,self.window,self.mode,self.custom,
                         inactivo=not self.window.isActiveWindow(),
                         reducir_inactivo=self.reduce_inactive)

    def eventFilter(self,watched,event):
        if watched is self.window and event.type() in (
                QtCore.QEvent.Type.Show,QtCore.QEvent.Type.WindowActivate,
                QtCore.QEvent.Type.WindowDeactivate):
            self.update()
        return False
