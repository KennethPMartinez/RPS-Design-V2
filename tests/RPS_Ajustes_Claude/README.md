# RPS Design V2 — Entrega ordenada de Ajustes

**Alcance:** formularios y módulos para integrar en [RPS-Design-V2](https://github.com/KennethPMartinez/RPS-Design-V2), sin borrar ni sobrescribir directamente los archivos del repositorio.

## Árbol

```text
RPS_Ajustes_Claude/
├── ui/
│   ├── designer/
│   │   └── Ajustes.ui                  # último formulario entregado, sin vista previa
│   ├── selector_color_rps.py         # versión ORIGINAL (sin modificaciones)
│   ├── settings_window.py            # controlador y diálogos de Ajustes
│   └── theme_manager.py             # paleta global y PyQtGraph
├── config/
│   ├── settings_model.py            # contrato validado / temas / estilos
│   └── settings_store.py            # persistencia QSettings
├── simulation/
│   └── frame_scheduler.py           # FPS del monitor, caps, uncapped, inactividad
├── engine/
│   └── sampling_preferences.py      # muestreo uniforme/adaptativo reutilizable
├── exporters/
│   └── settings_adapter.py          # resolución/calidad, sin rutas
├── tests/
│   ├── test_contract.py
│   └── test_sampling.py
├── GUIA_TECNICA_INTEGRACION.md
└── PROMPT_CLAUDE.md
```

## Qué se conservó y qué cambió

- Se parte del **`Ajustes.ui` más reciente suministrado**, sin sustituirlo por la maqueta anterior.
- Se suprime `groupPreviewTema` con su progreso, checkbox de demostración y texto, por solicitud expresa.
- Se renombra el nuevo checkbox de comportamiento `checkBox_3` a **`chkSimulacionPorContacto`**.
- Se renombran `pushButton*` y dos checkboxes genéricos del formulario a nombres significativos.
- Se completan tres filas **ya presentes** en Exportación: `comboResolucionVideo`, `comboFPSVideo`, `spinCRFVideo`.
- El archivo `selector_color_rps.py` es **byte por byte idéntico a la versión inicial** conservada en esta conversación (SHA-256 `24f3003e225055ee1b8d1521c54241626a301be1d2168cd19497ca3e173265af`).
- No hay archivo de previsualizador autónomo ni una sección de preview.
- Los colores se editan con el mismo selector HSV/RGB/CMYK/HSL/HEX original.

## Estado de integración (importante)

**Implementados en el paquete:** carga del `.ui` con QUiLoader, lectura/escritura y validación de preferencias, navegación existente del QTabWidget, selector de colores, edición de presets, controles de trazos/fuentes, aplicación de paleta global Qt y a widgets PyQtGraph existentes, cálculo de cadencia visual para monitor/fps/uncapped, muestreo matemático independiente, configuración y render raster de imágenes con resolución elegida, parámetros H.264.

**Necesitan conectar o validar en el repositorio (Claude):** startup de preferencias, eliminar *todas* las dependencias de Arduino/motor físico, nuevas ventanas creadas después del cambio de tema, control general de eventos/mecanismo, temporización de ventanas simulación, V-Sync real según backend, vincular muestreo al pipeline geométrico tras pruebas, ruta de captura a resolución de video configurada, calidad/exportadores vectoriales y VP9, persistencia de sesión y guardado automático, cache y solver de contacto. No se deben afirmar operativas funciones aún no integradas.

**No duplicar:** Mostrar/Ocultar, rango/escala/transformadas del menú contextual, elección de directorio de exportación, Control de banco.

**Nota documental solicitada, NO ejecutar ahora:** todos los *tips*, ayudas explicativas y textos técnicos de controles deberán migrarse posteriormente a la **Guía Técnica**. En esta entrega solo queda registrado el pendiente; no se mueve contenido ni se crea la guía final.

## Uso por Claude

1. Leer `PROMPT_CLAUDE.md` completo.
2. Revisar el estado del repositorio y conservar las modificaciones posteriores.
3. Integrar archivos por responsabilidad y conectar los motores existentes **sin hardware físico**.
4. Ejecutar tests y validación visual local. Corregir incompatibilidades reales, sin inventar resultados.

## Validación ejecutable independiente de Qt

```bash
python -m unittest discover -s tests -v
python -m compileall -q ui config simulation engine exporters
```

**Limitación de esta entrega:** en el entorno de generación no está instalado PySide6 y no fue posible instalarlo por falta de conectividad. Se verifican sintaxis Python, esquema de widgets XML y pruebas numéricas, **no** ejecución gráfica de Qt. Esa prueba queda obligatoria en Windows con PySide6.
