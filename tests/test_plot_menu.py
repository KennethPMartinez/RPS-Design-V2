import numpy as np
from widgets.plot_menu import transformar


def test_integral_de_constante():
    x = np.linspace(0, 2, 101)
    _, y = transformar("integral", x, np.ones_like(x))
    assert abs(y[-1] - 2.0) < 1e-9


def test_derivada_de_rampa():
    x = np.linspace(0, 1, 101)
    _, y = transformar("derivada", x, 3 * x)
    assert np.allclose(y, 3.0)


def test_fft_detecta_la_frecuencia():
    x = np.linspace(0, 2, 2001)
    f, p = transformar("fft", x, np.sin(2 * np.pi * 5 * x))
    assert abs(f[np.argmax(p)] - 5.0) < 0.2
