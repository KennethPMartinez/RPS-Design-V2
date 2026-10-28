# RPS Design V2 (Epitrocoidal) — progress.md

App de escritorio Python/PySide6 para diseño y simulación de sistemas de piñón de rodillos (tesis, semillero TAMA, Universidad Santo Tomás). V2 migra el render de Matplotlib a PyQtGraph y agrega control de motor paso a paso real (Arduino Mega, serial).

> Este archivo se actualiza a medida que avanza el desarrollo.

---

## 1. Estado general

| Área | Estado |
|---|---|
| Sistema Epitrocoidal en V2 | Migrado y funcional |
| Cremallera / Hipotrocoidal / Planetario | Pendientes (el menú avisa "aún no migrado") |
| Render (PyQtGraph) | Hecho, con OpenGL opcional en caliente |
| Modo automático (perfil de giro) | Hecho (editor, presets, grabación MP4) |
| Motor real (serial) | Hecho, con `MotorSimulado` para pruebas sin hardware |
| Exportación (Excel, imagen, PDF resumen, video) | Hecha |
| Tests | 7 pasando |
| Guía técnica | Pendiente |

---

## 2. Arquitectura

Misma arquitectura de V1, optimizada. La UI solo lee/valida parámetros (dataclasses), el engine calcula, los widgets dibujan.

- **Punto de entrada:** `main.py` (también funciona como `main.pyw`). Busca los 6 módulos de Qt Designer en cualquier subcarpeta; si faltan, muestra un diálogo con instrucciones.
- **Capas:** `config/`, `engine/`, `hardware/`, `ui/`, `widgets/`, `dialogs/`, `exporters/`, `utils/`, `tests/`.
- **Módulos de Qt Designer (NO van en el zip, copiar manualmente a `ui/designer/` o a la raíz):**
  `Seleccion_de_sistema.py`, `EpitrocoidalV2.py`, `ToothProfile_Window.py`, `Graficas_Window.py`, `Perfildevelocidad_simulador_Window.py`, `Mostrar_Ocultar_Epitrocoide.py`.
  La carpeta `Recursos/` va junto a `main.py` (la usa `Seleccion_de_sistema`).
  Todos fueron reconstruidos y entregados al final de la sesión anterior.
- **Entregable:** `RPS_Design_V2.zip` (última versión con los 6 archivos de Designer en `ui/designer/`).

### Archivos sin cambios respecto a V1
`config/data_structures.py`, `engine/base_engine.py`, `engine/epitrocoidal_engine.py`, `engine/cinematica_engine.py`, `engine/math_utils.py`, `engine/backend_selector.py`, `ui/errores.py`.

---

## 3. Archivos nuevos / modificados

### Engine
- `engine/motion_engine.py` — perfil de giro de la rueda motriz. Leyes: rampa lineal/cúbica, cicloidal, armónica, sinusoidal (y modificada), polinómica, lista de puntos, spline, trapezoidal modificada. Presets, `LineaTiempo`, aceleración por hardware vía `backend_selector.xp_para(n)`.
- `engine/motor_plan.py` — convierte la `LineaTiempo` en comandos `MOVE revs rpm`. `planificar()` parte el perfil en tramos de `dt_segmento` s; calcula la rpm para que cada tramo dure exactamente ese tiempo (trapecio con ACEL fija) y avisa si no cabe.
- `engine/contact_engine.py` (modificado) — corrección θ=0: `n_muestras=61` (impar) + refinamiento parabólico del mínimo → θ_local = 0 exacto en la raíz.
- `engine/rollerpinion_engine.py` (modificado) — `contexto.radio_primitivo_pinon_rodillos = prrp` (antes `mrrp`); arregla el factor de giro en modo Orbitar.

### Hardware
- `hardware/motor.py` — `Motor` (protocolo original: `MOVE revs rpm\n` → `OK`; `S` para parar) + `MotorSimulado` (misma interfaz, bloquea el tiempo real).
- `hardware/motor_controller.py` — `ControladorMotor(QObject)`: conexión, ejecución del plan en `QThread`, parada con `S`, estimación de posición al pausar (modelo trapezoidal), señales `terminado`, `progreso`, `conexionCambiada`; persistencia en `QSettings` (el motor nunca arranca "armado").

### Config
- `config/app_settings.py` — `AjustesMotor` (puerto, baud, relación, invertir, rpm_max=600, acel=8000, rpm_alineacion, dt_segmento, tolerancia_silenciosa_deg) y `render_opengl`.

### UI
- `ui/epitrocoidal_window.py` — integra el motor: Play en modo automático con motor habilitado y conectado → `planificar()` y ejecución en hilo. Al pausar resincroniza el tiempo de simulación con la posición estimada del motor. Diálogo de desfase (alinear / referenciar / cancelar). Grabar video desactiva OpenGL temporalmente.
- `ui/settings_window.py` — grupo Motor completo (conectar/desconectar, motor simulado); OpenGL en caliente con barra de progreso y reversión si falla.
- `ui/property_windows.py` — `VentanaPerfilDiente` y `VentanaPropiedad` (ángulo, curvatura, contacto) con `InspectorCurvas`.
- `ui/velocity_profile_window.py` — editor de línea de tiempo (sin botón "A", sin clic en leyenda, marcas de tramo persistentes).
- `ui/style_manager.py` — modo claro con paleta explícita; `retemar_plots()` para gráficas abiertas.

### Widgets
- `widgets/simulation_view.py` — `SimulationView(pg.PlotWidget)`: geometría subida una sola vez, por fotograma solo cambia la transformación (O(1) en Python). Capas: círculos de paso, patrón, piñón, rodillos activos, puntos de contacto, líneas de acción, etiquetas, epitrocoide base, camino de contacto. Contador FPS, `set_tema()`.
- `widgets/pg_helpers.py` — `configurar_menu_plot()`, `InspectorCurvas`, `retemar_plots()`, `aplicar_opengl()`, `AngleControl`, `reemplazar_widget()`.
- `widgets/wheel_widget.py` — rueda para la vista previa del editor.

### Exporters
- `exporters/excel_exporter.py` — hoja 1 "Perfil diente (CAD)": X, Y, Z(=0), θ y curva generatriz (usable directo en Inventor como Spline desde hoja); resumen al final.
- `exporters/image_exporter.py` — PNG, JPG, SVG (respaldo con `QSvgGenerator`), PDF, CSV; oculta el inspector antes de capturar.
- `exporters/video_recorder.py` — MP4 H.264 yuv420p vía imageio-ffmpeg; `.copy()` para evitar puntero colgante al buffer de `QImage`.

### Dialogs / Utils
- `dialogs/mostrar_ocultar_dialog.py` — `actualizar_modo(modo_alterno)`: "Camino de contacto" solo en Fijo, "Epitrocoide base" solo en Orbitar, y sus rótulos "Solo modo …".
- `dialogs/design_summary_dialog.py` + `utils/design_report.py` — ficha técnica y diagnóstico de subcorte (ρ_min vs radio de fresa de referencia 1.5 mm), exportable a PDF.
- `utils/file_handler.py` — Abrir/Guardar JSON (parámetros, modo, perfil de movimiento, visibilidad).

---

## 4. Decisiones técnicas

- **θ = 0 en la raíz:** el error era `n_muestras=60` (par), θ=0 nunca estaba en la malla. Solución: 61 puntos + refinamiento parabólico → θ_local = 0, punto (16.4213, 0).
- **Modo Orbitar:** factor = cd/prrp = 2.0 (no cd/mrrp).
- **Ancho de pluma:** con antialias, ancho > 1 pasaba de ~7 ms a ~37 ms por fotograma (900×700, 12 dientes). Las curvas pesadas van a ancho 1 (pluma cosmética).
- **OpenGL:** `aplicar_opengl()` verifica contexto GL válido; si falla, revierte el checkbox. Default `render_opengl = False` porque la grabación usa `widget.grab()`, más fiable por software.
- **Motor bloqueante:** `MOVE` frena y arranca en cada tramo; la posición al final de cada tramo es exacta, entre tramos no. Para seguir el perfil de forma continua haría falta un comando de streaming en el firmware. El resincronizado al pausar minimiza el desfase.
- **Epitrocoide base:** θ ∈ [0, 2π], 2001 puntos, solo diente 0, con rotación de vista; visible solo en Orbitar.
- **Camino de contacto:** validado contra los puntos de contacto calculados (error < 0.014 mm); visible solo en Fijo.
- **SVG:** `SVGExporter` de pyqtgraph falla en algunas combinaciones pyqtgraph/Qt → respaldo con Qt.
- **Mínimo físico por tramo:** ACEL·T² ≥ 4·s; tramos más cortos no caben y se avisa.

---

## 5. Tests (7 pasando)

- `tests/test_motion_engine.py` — presets sin errores; "Arranque y parada suaves" recorre 1200°; round-trip JSON.
- `tests/test_motor_plan.py` — la rpm reproduce la duración; el trapecio llega a `s`; el plan suma el recorrido del perfil; aviso si el tramo no cabe.

Ejecutar: `python -m pytest tests`

---

## 6. Pendientes

### Preguntas abiertas sobre el hardware
- ¿El firmware acepta decimales en `MOVE`? (se envían revs con 6 decimales y rpm con 3).
- ¿Qué responde el firmware a `S` mientras hay un `MOVE` en curso?
- ¿Hay reductor entre el motor y el piñón? (ajustar en Ajustes → Motor → Relación).
- Streaming continuo en el firmware para seguir el perfil sin frenar entre tramos.

### Desarrollo
- Migrar a V2: Cremallera, Hipotrocoidal, Planetario.
- Guía técnica (el menú muestra un aviso provisional).
- Settings_window definitiva (hoy es provisional, construida por código).
- Radio de fresa de referencia editable desde Ajustes (hoy constante 1.5 mm).
- Exportaciones DXF / CSV / TXT / PDF completas según `ModusOperandi.docx`.
- Formato nativo `.rpsf` (hoy se guarda JSON).

### Conceptual (semillero)
La simulación actual es cinemática pura (ángulo motor → giro de piñón/engranaje por factores de rodadura). El semillero quiere una simulación basada en contactos: el rodillo empuja el flanco y el giro del engranaje sale de la tangencia y la no penetración. Va en la guía técnica y en una fase futura.

---

## 7. Registro de cambios

| Fecha | Cambio |
|---|---|
| 2026-10-25 | Primera versión de este archivo: consolida el estado de V2 hasta la sesión de reconstrucción de los archivos de Qt Designer. |
