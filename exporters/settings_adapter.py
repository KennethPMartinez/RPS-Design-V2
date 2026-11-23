"""Adaptador optativo de exportación de imagen/video SIN selección de rutas.

Las rutas las recibe del flujo del menú Archivo del programa. No sobreescribe
sus diálogos ni guarda carpetas. Un video de salida diferente de 1920x1080
necesita un proveedor de fotogramas renderizados a esa resolución.
"""
from __future__ import annotations
from PySide6 import QtCore,QtGui
from config.settings_model import Exportacion

RESOLUCIONES={
    '1280 × 720 (HD)':(1280,720),
    '1920 × 1080 (Full HD)':(1920,1080),
    '2560 × 1440 (QHD)':(2560,1440),
    '3840 × 2160 (4K)':(3840,2160),
}


def dimensiones_imagen(op:Exportacion,original:tuple[int,int])->tuple[int,int]:
    if op.resolucion_imagen.startswith('Original'):
        return original
    if op.resolucion_imagen=='Personalizada':
        return op.imagen_ancho,op.imagen_alto
    return RESOLUCIONES.get(op.resolucion_imagen,(op.imagen_ancho,op.imagen_alto))


def dimensiones_video(op:Exportacion)->tuple[int,int]:
    return RESOLUCIONES.get(op.resolucion_video,(op.video_ancho,op.video_alto))


def renderizar_grafica(plot,ancho:int,alto:int,transparente:bool=False,
                      antialias:bool=True)->QtGui.QImage:
    """Rasteriza la escena ORIGINAL a las dimensiones solicitadas, sin escalar
    después una captura pequeña. Verificar por tipo de gráfica en integración.
    """
    if not (100<=ancho<=16384 and 100<=alto<=16384):
        raise ValueError('Resolución fuera de rango')
    img=QtGui.QImage(ancho,alto,QtGui.QImage.Format.Format_ARGB32_Premultiplied)
    fondo=plot.palette().color(QtGui.QPalette.ColorRole.Base)
    try:                       # el fondo real de la gráfica (tema) y no el de la paleta: evita bandas de otro color
        pincel=plot.backgroundBrush()
        if pincel.style()!=QtCore.Qt.BrushStyle.NoBrush:fondo=pincel.color()
    except AttributeError:
        pass
    img.fill(QtCore.Qt.GlobalColor.transparent if transparente else fondo)
    painter=QtGui.QPainter(img)
    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing,antialias)
    painter.setRenderHint(QtGui.QPainter.RenderHint.TextAntialiasing,antialias)
    try:
        item=plot.getPlotItem()
        src=item.sceneBoundingRect()
        plot.scene().render(painter,QtCore.QRectF(0,0,ancho,alto),src,
                            QtCore.Qt.AspectRatioMode.KeepAspectRatio)
    finally:
        painter.end()
    return img


def guardar_imagen(plot,ruta:str,op:Exportacion)->None:
    """PNG/JPEG. SVG y PDF vectorial se delegan al exportador existente."""
    # La extensión del archivo elegida en el menú prevalece sobre el preset.
    from pathlib import Path
    ext=Path(ruta).suffix.lower()
    typ='PNG' if ext=='.png' else 'JPEG' if ext in ('.jpg','.jpeg') else ''
    if not typ:
        raise NotImplementedError(f'{ext}: conectar el exportador SVG/PDF actual')
    size=plot.size()
    w,h=dimensiones_imagen(op,(size.width(),size.height()))
    img=renderizar_grafica(plot,w,h,op.fondo_transparente and typ=='PNG',op.antialias_export)
    if typ=='JPEG':
        rgb=QtGui.QImage(img.size(),QtGui.QImage.Format.Format_RGB32)
        rgb.fill(QtCore.Qt.GlobalColor.white)
        p=QtGui.QPainter(rgb);p.drawImage(0,0,img);p.end();img=rgb
    if not img.save(str(ruta),'JPG' if typ=='JPEG' else 'PNG',op.jpeg_calidad if typ=='JPEG' else -1):
        raise OSError('No se pudo escribir el archivo de imagen')


def parametros_video(op:Exportacion)->dict:
    """Parámetros para GrabadorVideo: H.264 (MP4) o VP9 (WebM); yuv420p exige dimensiones pares."""
    from exporters.video_recorder import es_vp9
    w,h=dimensiones_video(op)
    if (w%2) or (h%2):
        raise ValueError('yuv420p requiere dimensiones pares')
    return {'fps':op.video_fps,'crf':op.video_crf,'ancho':w,'alto':h,'vp9':es_vp9(op.formato_video),
            'extension':'.webm' if es_vp9(op.formato_video) else '.mp4'}
