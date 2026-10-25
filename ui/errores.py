# -*- coding: utf-8 -*-
"""
Aislamiento de fallos para slots de Qt.

Principio de diseño pedido: un error en un manejador de señal (al leer un
parámetro, al invocar el motor de cálculo, al sincronizar un widget) NO
debe tumbar la ventana ni el resto de la aplicación. Este decorador
atrapa la excepción, la reporta (barra de estado si el objeto la tiene,
si no por consola) y deja que el resto de la UI siga respondiendo.

Uso:
    class MiVentana(QtWidgets.QMainWindow):
        @manejador_seguro
        def al_cambiar_algo(self, valor):
            ...
"""
import functools
import traceback


def manejador_seguro(func):
    @functools.wraps(func)
    def envoltura(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as error:
            mensaje = f"[{type(self).__name__}.{func.__name__}] {error}"
            print(mensaje)
            traceback.print_exc()
            barra = getattr(self, "statusBar", None)
            if callable(barra):
                try:
                    barra().showMessage(f"⚠ {mensaje}", 5000)
                except Exception:
                    pass
            return None
    return envoltura
