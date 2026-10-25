# -*- coding: utf-8 -*-
"""
exporters/video_recorder.py

Grabación de la simulación a MP4 (H.264, yuv420p): el mejor equilibrio calidad/peso y
reproducible en cualquier dispositivo. Usa imageio + imageio-ffmpeg (trae su propio
ffmpeg: no requiere instalar nada más). CRF 23 + preset 'medium' ≈ calidad visualmente
limpia con archivos de pocos MB para un minuto de curvas sobre fondo plano.

La captura es DETERMINISTA (offline): quien graba avanza el tiempo fotograma a fotograma y
llama a `agregar()`; el video sale a 1x aunque renderizar tarde más que el tiempo real.
"""
from __future__ import annotations

import numpy as np


def qimage_a_rgb(img) -> np.ndarray:
    from PySide6.QtGui import QImage
    img = img.convertToFormat(QImage.Format.Format_RGB888)
    w, h = img.width(), img.height()
    buf = np.frombuffer(img.constBits(), dtype=np.uint8, count=img.bytesPerLine() * h)
    arr = buf.reshape(h, img.bytesPerLine())[:, : w * 3].reshape(h, w, 3)
    # .copy(): el buffer pertenece al QImage local (se libera al salir) -> sin copia = puntero colgante
    return np.ascontiguousarray(arr[: h - (h % 2), : w - (w % 2)]).copy()   # H.264 4:2:0: dimensiones pares


class GrabadorVideo:
    def __init__(self, ruta: str, fps: int = 30, crf: int = 23):
        import imageio.v2 as imageio
        self.ruta, self.fps, self.n = ruta, fps, 0
        self._w = imageio.get_writer(
            ruta, format="FFMPEG", fps=fps, codec="libx264", pixelformat="yuv420p",
            macro_block_size=2, output_params=["-crf", str(crf), "-preset", "medium",
                                               "-movflags", "+faststart"])

    def agregar(self, qimage) -> None:
        self._w.append_data(qimage_a_rgb(qimage)); self.n += 1

    def cerrar(self) -> None:
        self._w.close()
