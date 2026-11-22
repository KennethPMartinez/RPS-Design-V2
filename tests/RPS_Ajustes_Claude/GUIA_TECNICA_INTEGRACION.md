# RPS Design V2 — Guía de integración de Ajustes

**Documento de integración, no Guía Técnica final.** Versión de entrega: 22 de noviembre de 2026. Fuente del formulario: último `Ajustes.ui` adjunto por el usuario. El formulario tiene cinco pestañas principales, sin vista previa del tema.

## 1. Propósito y alcance

Configurar globalmente la aplicación de diseño de sistemas con piñón de rodillos. `Ajustes` determina **cómo** se calculan y presentan resultados, no **qué** curvas se ven en un instante. Se conservan intactos el diálogo Mostrar/Ocultar y los menús contextuales de las gráficas. **Control de banco** abrirá la aplicación independiente del equipo físico; no implementar comunicación, motores ni Arduino aquí.

## 2. Inventario de archivos y puntos de integración

| Archivo incluido | Función | Nivel |
|---|---|---|
| `ui/designer/Ajustes.ui` | Formulario Qt Designer actualizado | Completo como estructura XML |
| `ui/selector_color_rps.py` | Selector original HSV, HEX, RGB, CMYK, HSL y alfa, con conexión a árboles | Implementación original conservada |
| `ui/settings_window.py` | Diálogo, señales, widgets, validación, confirmación, presets | Código listo; integración host pendiente |
| `config/settings_model.py` | Dataclasses, presets, estilos, rangos y validación | Implementado y probado sin Qt |
| `config/settings_store.py` | Preferencias por QSettings | Implementado; probar en Windows |
| `ui/theme_manager.py` | Paleta global Qt y recoloreo de PlotWidget | Implementado parcialmente; revisar widgets especiales |
| `simulation/frame_scheduler.py` | Límite FPS/monitor/uncapped/inactividad | Implementado; conectar a `_anim` |
| `engine/sampling_preferences.py` | Muestreo geométrico uniforme/adaptativo genérico | Independiente; **no conectado a motores** |
| `exporters/settings_adapter.py` | Exportación raster a resolución destino; FPS/CRF/dimensiones H.264 | Adaptador; conectar al menú y a grabación |
| `tests/` | Esquema XML, contrato, presets y muestreo básico | 6 tests de unidad (sin Qt) |

**Importante:** `ui/settings_window.py` utiliza `QUiLoader` para abrir `Ajustes.ui` directamente; **no necesita generar otro archivo `.py` a partir del formulario**. Es compatible con `SettingsWindow(self).exec()` que utiliza el repositorio, pero la clase usa composición (`.dialog`) y no hereda de QDialog. Los adaptadores reales del programa que necesiten un QWidget deben recibir `.dialog`.

## 3. Árbol de controles de `Ajustes.ui`

### General

`chkRestaurarSesion`, `chkConfirmarSalir`, `chkGuardadoAuto`, `spinIntervaloGuardado`, `chkGuardarPrefs`, `chkAvisosDatos`, `chkAvisosSobrescribir`.

Los cambios del diálogo se guardan con QSettings, pero **autosave del proyecto** y recuperación de sesión exigen lógica de proyecto y formato de archivo de RPS Design; el checkbox solo registra preferencia hasta que se conecte.

### Cálculo y precisión

`desviacionLinealSlider`, `desviacionLinealSpin`, `desviacionAngularSlider`, `desviacionAngularSpin`, `comboDecimales`, `comboEstrategiaMuestreo`, `spinMuestras`, `spinMaxMuestras`, `chkMostrarEstimacion`.

Valores existentes: desviación lineal de simulación **0,0003 mm** y desviación angular **0,5°**. Preservar estas unidades y semántica. La discretización genérica adjunta es un bloque reutilizable y **no sustituye** sin validación el algoritmo de contacto que usa búsqueda discreta y refinamiento.

El número de decimales configura solo presentación; conservar `float64` en cálculos numéricos. Si se activa estimación de costo, calcularla desde un algoritmo real o dejarla pendiente de integración; no inventar tiempos.

### Simulación y rendimiento

`comboFPS`, `spinFPSCustom`, `chkVSync`, `comboBackend`, `comboRender`, `chkBajarFPSInactivo`, `chkDetenerInvalido`, `chkConservarPausa`, `chkCacheGeometria`, **`chkSimulacionPorContacto`**.

`FrameScheduler` calcula la cadencia y actualiza el QTimer existente. El modo `Uncapped` usa intervalo Qt `0`, que puede consumir CPU: mantener la función solo mientras la simulación esté activa. La simulación debe progresar con `time.perf_counter()` y el perfil de movimiento, no sumando `1/FPS` por frame. `QScreen.refreshRate()` proporciona una frecuencia aproximada del monitor activo; no enumera todos los modos físicos. Si el usuario cambia el monitor, actualizar FPS con `screenChanged`.

**V-Sync:** guardar y mostrar la preferencia, pero no informar «V-Sync activo» hasta verificar que el backend/contexto gráfico realmente sincroniza el intercambio de buffers. Un `QTimer` por sí solo no implementa V-Sync. El cambio de OpenGL debe usar el helper existente y tratar adecuadamente fallos de contexto o de controlador.

**Simulación basada en contacto:** el checkbox se registra. No habilitar un solver inexistente ni sustituir silenciosamente el cálculo cinemático. Conectar solo después de probar colisiones/contactos y criterios de estabilidad/tiempo.

**CPU/GPU/Híbrido:** utilizar el `engine/backend_selector.py` actual, que ya selecciona NumPy/CuPy; conservar fallback cuando CuPy no está disponible.

### Apariencia y estilos

`comboTema`, `btnGuardarTema`, `btnDuplicarTema`, `btnRestaurarTema`, `treeColoresUI`, `treeColoresTecnicos`, `btnColorUI`, `btnColorTecnico`, `comboTipoCurva`, `spinAnchoLinea`, `comboTipoLinea`, `comboLineCap`, `comboLineJoin`, `sliderOpacidad`, `spinOpacidad`, `chkAntialias`, `fontInterfaz`, `spinTamanoUI`, `chkFuenteUIBold`, `fontGraficas`, `spinTamanoGrafica`, `chkFuenteGraficaBold`.

- Los presets afectan la **UI completa** (menús, ventanas secundarias, paneles, cuadros de diálogo, controles, texto, selecciones) y todas las gráficas (fondos, curvas, ejes, textos). Aplicar también a widgets nuevos cuando se construyen.
- **No** cambiar estados de visibilidad, rangos, escalas logarítmicas, transformadas, acciones de mouse ni la cuadrícula activada/desactivada por el menú contextual.
- El selector personalizado adjunto es el de la primera entrega, **sin ninguna modificación**. El componente emite `colorConfirmado(categoria, rol, QColor)`; `settings_window.py` acumula cambios hasta pulsar Aplicar/Aceptar.
- El color personalizable es una preferencia global; en el menú contextual puede mantenerse la exportación de gráfica individual. Los presets integrados son inmutables; los duplicados se guardan aparte.
- Las paletas para daltonismo son propuestas de diferenciación visual, **no** una certificación de accesibilidad. Complementar con patrones de línea, y comprobar contraste de la UI.
- Líneas gruesas, anti-aliasing y OpenGL pueden alterar mucho el rendimiento; probar con el motor real de PyQtGraph. Algunos widgets tienen estilo hardcodeado en sus `set_tema` y requieren migrar sus colores a roles.
- El `ThemeManager` es una capa inicial; no promete recolorear iconos bitmap, componentes Qt nativos que ignoren QPalette ni QSS hardcodeado heredado. Estas excepciones deben resolverse en la integración, no ocultarse.

### Exportación

`comboFormatoImagen`, `comboResolucionImagen`, `spinImgAncho`, `spinImgAlto`, `sliderJpeg`, `spinJpeg`, `chkMantenerAspectoImagen`, `chkFondoTransparente`, `chkAntialiasExport`, `comboFormatoVideo`, `comboResolucionVideo`, `spinVidAncho`, `spinVidAlto`, `comboFPSVideo`, `spinCRFVideo`, `chkRelacionVideo`, `chkVideoDeterminista`.

- **Nunca** añadir un control de carpeta o ruta a Ajustes; el directorio y nombre se eligen desde las acciones del menú Archivo y del menú contextual donde ya existen.
- PNG/JPEG: el adaptador renderiza la escena con QPainter al tamaño destino sin agrandar a posteriori un fotograma pequeño. Probar gráficos con distinta relación de aspecto, estilos y fondos. El archivo elegido por el usuario (extensión/filtro) prevalece sobre el formato predeterminado de Ajustes.
- SVG y PDF: mantener el exportador existente. No afirmar que el PDF es vectorial: la versión actual del proyecto incrusta una imagen raster en PDF.
- MP4/H.264: `GrabadorVideo` admite FPS y CRF; el adaptador devuelve también dimensiones. **No basta** con pasar estas dimensiones a `GrabadorVideo`: el proveedor de fotogramas debe generar imágenes reales a la resolución solicitada. Exportación determinista = avanzar el tiempo simulado fotograma por fotograma.
- VP9/WebM figura en el formulario como «por implementar». El adaptador lanza `NotImplementedError`; Claude debe implementar un writer verificable antes de prometerlo funcional.
- JPG no soporta transparencia; forzar fondo opaco al exportar JPG, no borrar la casilla del formulario.

## 4. Ciclo de vida y transacciones

1. Al iniciar la app: leer QSettings y validar; aplicar tema y preferencias predeterminadas antes de crear ventanas de simulación.
2. Abrir Ajustes: cargar estado persistido a controles, sin aplicar cambios por cada evento de control.
3. Pulsar Elegir color: abre el selector original, `Cancelar` conserva color anterior.
4. Pulsar **Aplicar**: validar formulario; aplicar configuraciones admitidas; persistir; mantener diálogo abierto.
5. Pulsar **Aceptar**: lo anterior + cerrar.
6. Pulsar **Cancelar**: descartar cambios no aplicados en la sesión del diálogo.
7. **Restaurar predeterminados**: modificar el formulario, sin persistir hasta Aplicar/Aceptar.
8. **Guardar como preset/Duplicar**: guardado explícito del tema nombrado por el usuario, separado del comportamiento de Cancelar del diálogo completo.

## 5. Código mínimo de arranque (orientativo; integrar en clase real)

```python
from config.settings_store import SettingsStore
from ui.theme_manager import ThemeManager
from ui.settings_window import SettingsWindow

# Tras crear QApplication y antes de abrir las ventanas:
store = SettingsStore()
settings = store.load()
theme_manager = ThemeManager(app)
theme_manager.apply(settings.apariencia)

# Desde ui/sistema_base.py:
SettingsWindow(self, store=store, theme_manager=theme_manager).exec()
```

**Nota:** la llamada anterior presupone que `store` y `theme_manager` se comparten desde el arranque. La implementación de ejemplo utiliza valores predeterminados si no se suministran, pero para aplicación coherente es mejor una única instancia centralizada. El arranque del repositorio actual incluye dependencias de Arduino que deben limpiarse con pruebas de regresión.

## 6. Plan de verificación en Windows

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m compileall -q ui config engine simulation exporters
pyside6-designer ui\designer\Ajustes.ui
python main.py
```

Comprobar manualmente: abrir Ajustes, cambiar a cada pestaña, elegir colores, cancelar y verificar reversión; aplicar un tema y examinar ventanas secundarias y gráficas; reiniciar app y comprobar persistencia; duplicar/guardar presets; comprobar sliders de desviación; FPS monitor e inactividad; pérdida de backend GPU; probar OpenGL y volver a software; exportar PNG/JPEG/MP4 con resolución y FPS elegidos y verificar tamaño/tiempo reales; comprobar que Mostrar/Ocultar y menús contextuales se conservan. **No afirmar que V-Sync real funciona sin instrumentar la presentación de frames.**

## 7. Tarea documental expresamente pospuesta

> **PENDIENTE — No implementar ahora:** migrar todos los *tips*, ayudas contextuales y textos explicativos de interfaz a la **Guía Técnica** de RPS Design V2. Esta entrega únicamente registra la decisión; no edita tooltips, no redacta la guía final y no retira la información de su ubicación actual.

## 8. Revisión y advertencias

El formulario `.ui` se validó como XML y se verificó que no hay nombres de widget duplicados. El código se compiló con `compileall` y se ejecutaron pruebas unitarias independientes de Qt. **No fue posible ejecutar interfaz PySide6 en el entorno generador**, por falta del paquete y acceso a red para instalarlo. Las pruebas gráficas y de integración del proyecto real son requisitos para considerar el trabajo terminado.
