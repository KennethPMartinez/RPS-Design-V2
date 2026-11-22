# Prompt para Claude — Integración completa de Ajustes en RPS Design V2

Actúa como ingeniero de software senior especializado en Python, PySide6, Qt Designer, PyQtGraph, ingeniería mecánica y arquitecturas de simulación científica.

## Contexto obligatorio

Repositorio de destino: `https://github.com/KennethPMartinez/RPS-Design-V2`, rama de trabajo existente (no asumir que `master` refleja todo el estado local). Tengo una entrega adjunta llamada `RPS_Ajustes_Claude` que contiene el formulario Qt Designer, módulos Python, pruebas y `GUIA_TECNICA_INTEGRACION.md`. **Lee primero esta entrega completa y los archivos actuales del repositorio antes de modificar código.** Trata esta entrega como un punto de partida integrable, no como una sustitución indiscriminada de archivos más recientes.

**Decisiones innegociables del usuario:**

1. Usar el archivo `ui/designer/Ajustes.ui` de la entrega. Se basa en el último formulario del usuario, **sin vista previa de tema**. No reintroducirla, no crear previsualizador aparte, no rediseñar desde cero.
2. Preservar exactamente la implementación ORIGINAL de `ui/selector_color_rps.py`: selector profesional HSV/SV + barra tono + HEX/RGB/CMYK/HSV/HSL/alfa. No sustituirlo con `QColorDialog`, no simplificarlo ni reconstruirlo a menos que una prueba detecte un defecto real; si corriges algo, justificarlo y limitar el parche.
3. **Eliminar de RPS Design el control de hardware físico:** Arduino, puerto COM, motores, controladores, armar/alinear/parar motor físico y dependencias correspondientes. El botón `Control de banco` será acceso a otra app independiente de control del dispositivo. No implementar por anticipado sistemas de hardware.
4. Mantener CPU/GPU/Híbrido porque es procesamiento local de NumPy/CuPy, no hardware físico externo.
5. No duplicar ni modificar funcionalidad de **Mostrar/Ocultar** ni las opciones de las gráficas (zoom, ejes, pan, escala log, cuadrícula on/off, FFT, derivada, integral, exportación puntual). Las preferencias de estilos no deben sobreescribir elecciones de visibilidad ni estado local de cada gráfica.
6. Los presets (Oscuro, Claro, Alto contraste, Azul profundo RPS, Deuteranopia, Protanopia, Tritanopia, Blanco y negro, Escala de grises, Presentación CAD, Plano técnico, Análisis cinemático, Personalizado) **aplican a toda la UI y las gráficas**, incluidas ventanas secundarias y diálogos. El usuario puede editar cada rol de color, fuentes de UI/gráficas y trazos por categoría; conservar los presets integrados y guardar variantes personales.
7. En `Comportamiento` conservar `chkSimulacionPorContacto`: opción de simulación física por contactos costosa, no es «mostrar contacto». **No afirmar que existe el solver** ni conectar a rutinas no verificadas. Si no existe, persistir el ajuste y marcarlo como pendiente hasta implementarlo de verdad.
8. Simulación: modos FPS por frecuencia real/monitor activo, límites 30/60/75/90/120/144/165/240, personalizado y sin límite, menor actualización al estar inactivo. La cinemática se rige por tiempo real/simulado, **no por conteo de frames**. V-Sync es una preferencia solicitada, cuya aplicación efectiva depende del backend y hay que verificar. No equiparar QTimer con V-Sync.
9. Cálculo y precisión: conservar desviaciones existentes de simulación (0,0003 mm y 0,5°), precisión numérica de *presentación*, muestreo uniforme/adaptativo con pruebas geométricas; no modificar los algoritmos de contacto y geometría sin comparar tolerancias, exactitud y desempeño.
10. Exportación: tamaño, formato y calidad de imagen/video (resolución, FPS y CRF H.264); **sin selector de directorio en Ajustes** porque la ruta de exportación se establece mediante el menú correspondiente. Exportar fotogramas a resolución solicitada de verdad, sin agrandar capturas pequeñas. La cadencia visual y la cadencia de video son independientes. Mantener SVG/PDF/CSV/DXF/XLSX ya existentes; implementar VP9/WebM solo si puede verificarse. El formato del diálogo de guardar prevalece sobre el predeterminado.
11. **Tarea documental diferida:** todos los tips de la UI deben migrarse a la Guía Técnica posteriormente, pero **NO ejecutar la migración ahora**. Limítate a dejarlo consignado en el Markdown de integración.
12. No agregar funciones especulativas ni interfaces vacías que parezcan operativas. Explica las limitaciones y deja pendientes verificables.

## Plan de ejecución obligatorio

### Fase 1 — Inspección y compatibilidad

- Examina `main.py`, `ui/settings_window.py`, `ui/sistema_base.py`, `ui/style_manager.py`, `widgets/pg_helpers.py`, `widgets/plot_menu.py`, `widgets/simulation_view.py`, `widgets/planetary_view.py`, `engine/backend_selector.py`, `engine/contact_engine.py`, `config/app_settings.py`, `config/data_structures.py`, `exporters/image_exporter.py`, `exporters/video_recorder.py`, `exporters/export_manager.py` y los archivos `.ui` existentes.
- Inventaría todas las referencias de `hardware.*`, `ajustes.motor`, `motor_ctrl`, `plan_alineacion`, `planificar`, `getOpenFileName`/`getSaveFileName`, grabación y funciones de menú. Evita borrar funcionalidades de software manual/automático que no dependan del motor real.
- Reconcilia los nombres reales de widgets con el `Ajustes.ui` adjunto. Se renombraron `pushButton_*` → `btnCancelar`, `btnAplicar`, `btnAceptar`, `btnRestaurar`; `checkBox_3` → `chkSimulacionPorContacto`.

### Fase 2 — Integración de preferencia / controlador

- Integra `config/settings_model.py`, `config/settings_store.py`, `ui/settings_window.py`, `ui/selector_color_rps.py`, `ui/theme_manager.py`. La clase SettingsWindow utiliza `QtUiTools.QUiLoader` y expone `.exec()` compatible con las llamadas actuales; si necesitas convertirla en QDialog derivado por restricciones reales, conserva el formulario y toda la lógica.
- Implementa transacciones Aplicar/Aceptar/Cancelar/Restaurar. Validar rangos; impedir que Cancelar persista cambios no aplicados. Los presets nombrados se guardan explícitamente al pedirlo.
- Centraliza preferencias de arranque con una sola instancia del store y del theme manager. Implementa migración simple o fallback ante configuración incompatible, pero no borres proyectos.

### Fase 3 — Temas globales y gráficas

- Reemplaza colores de UI y curvas *hardcodeados* por los roles del tema, sin romper los mecanismos actuales. Aplica a `QApplication`, `QPalette`, QSS mínimos y cada PlotWidget, incluidos widgets creados posteriormente.
- Conecta fuentes de UI/etiquetas, colores de categorías, ancho/opacidad/tipo/terminación/unión de trazos. Respeta los controles de mostrar/ocultar y el menú contextual existente. Valida el render con OpenGL/software y grosor >1 px.
- Nunca pases los cambios de interfaz por el diálogo Mostrar/Ocultar; ambos subsistemas deben permanecer desacoplados.

### Fase 4 — Simulación y cómputo

- Integra `simulation/frame_scheduler.py` al QTimer existente, sin alterar el flujo físico/virtual. Detecta actualización de pantalla, actividad de ventana y monitor. Respeta preferencia de FPS; mide FPS real sin declarar V-Sync exitoso automáticamente.
- Conecta backend NumPy/CuPy y render OpenGL con fallback seguro; distingue explícitamente la GPU de cálculo del renderizador. Las nuevas preferencias de caché, pausa e invalidez deben operar donde ya existan los hooks; no agregues no-ops silenciosos.
- Analiza el muestreo `engine/sampling_preferences.py` como alternativa **independiente**. Compara con el algoritmo real, garantiza ausencia de saltos visibles, preserva theta=0 exacto y límites de contacto, y agrega pruebas antes de aplicar al engine.
- `chkSimulacionPorContacto` debe persistirse; si la simulación de contacto aún no existe, no activar un modo ficticio. Documenta la dependencia.

### Fase 5 — Exportación

- Integra `exporters/settings_adapter.py` respetando el menú que selecciona el archivo de destino. No agregar carpetas predeterminadas en Ajustes. Formatos imagen: PNG/JPEG/SVG/PDF. Video: MP4/H.264, y VP9/WebM solamente con codificador disponible y pruebas.
- Habilita exportación de captura a resolución real elegida, con aspecto y transparencia cuando aplique; nunca escalar después una captura de baja resolución. La salida PNG/JPEG debe respetar extensión de guardado. Verifica imágenes raster vs vectoriales.
- Configura el `GrabadorVideo` para FPS/CRF y render del frame a las dimensiones solicitadas; preserva su iteración temporal determinista. Verifica fps, dimensiones y duración resultante, sin inventar tiempos de ejecución.

### Fase 6 — Limpieza de hardware y regresiones

- Retira imports y rutas de ejecución al motor físico que impidan arrancar la aplicación sin pyserial/Arduino. Evita retirar módulos de cálculo geométrico por confundir la palabra “motor” (en varios sitios significa motor matemático).
- Ajusta arranque, menú Control de banco, proyecto nativo, diálogos y pruebas existentes. No borrar tests útiles. Mantén los cuatro sistemas de diseño actuales y sus ventanas; no desarrollar otros sistemas futuros.
- Ejecuta todas las pruebas que puedan ejecutarse, luego test visual de `Ajustes.ui` en Qt Designer y del selector original con PySide6. Añade tests para persistencia QSettings, reversión Cancelar, temas globales, adaptación de FPS y grabación de video.

## Entregables esperados al terminar

1. Archivos integrados en el repositorio y lista exacta de archivos modificados/agregados/eliminados.
2. Instrucciones de instalación y ejecución de Windows 11/Python/PySide6.
3. Resultados observables de pytest, pruebas visuales y comparación antes/después. No reportar pruebas no ejecutadas.
4. Tabla de requisitos: implementado / parcialmente integrado / pendiente con causa.
5. Ninguna regresión de Mostrar/Ocultar, menús contextuales, cálculo y reproducción.
6. Actualizar documentación de integración; anotar exclusivamente la futura migración de tips a Guía Técnica, sin hacerla.

**Modo de trabajo:** procede directamente con la implementación y pruebas en el entorno de Claude; si una función no puede implementarse correctamente, conserva la integridad del proyecto, identifica el bloqueo y entrega el mejor resultado verificable. No sustituyas funcionalidad real por cambios cosméticos.
