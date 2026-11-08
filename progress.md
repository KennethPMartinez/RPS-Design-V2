# RPS Design V2 — progress.md

App de escritorio Python/PySide6 para diseño y simulación de sistemas de piñón de rodillos (tesis, semillero TAMA, Universidad Santo Tomás). V2 migra el render a PyQtGraph y agrega control de motor paso a paso real (Arduino Mega, serial).

> Este archivo se actualiza a medida que avanza el desarrollo (entradas numeradas, no se regenera).

---

## 1. Estado general

| Área | Estado |
|---|---|
| Epitrocoidal | Migrado y funcional |
| Hipotrocoidal | Migrado (comparte ventana con Epitrocoidal) — pendiente de prueba visual |
| Trocoidal (antes Cremallera) | Migrado (sistema lineal) — pendiente de prueba visual |
| Planetario | Pendiente (el menú avisa "aún no migrado") |
| Render (PyQtGraph) | Hecho, con OpenGL opcional en caliente |
| Menú contextual de gráficas | Propio, en español; "Ver todo" encuadra el contenido |
| Transformadas (FFT, derivada, integral) | Solo en la línea de tiempo (visuales) |
| Modo automático / motor real / exportaciones | Hechos |
| Tests | 7 previos + `test_plot_menu` (3) + `test_file_handler` (2) |
| Guía técnica | Pendiente |

---

## 2. Arquitectura

La UI solo lee/valida parámetros (dataclasses), el engine calcula, los widgets dibujan.

- **Punto de entrada:** `main.py`. Busca los módulos de Qt Designer en cualquier subcarpeta (lista `MODULOS_UI`).
- **Módulos de Qt Designer (copiar a `ui/designer/` o a la raíz):** `Seleccion_de_sistema`, `Epi_HipotrocoidalV2`, `TrocoidalV2`, `ToothProfile_Window`, `Graficas_Window`, `Perfildevelocidad_simulador_Window`, `Mostrar_Ocultar_Epitrocoidal`, `Mostrar_Ocultar_Hipotrocoidal`, `Mostrar_Ocultar_Trocoidal` (y `Mostrar_Ocultar_Planetario` cuando se migre Planetario). `Recursos/` junto a `main.py`.
- **Jerarquía de ventanas (POO, DRY):**
  - `ui/sistema_base.py` → `VentanaSistemaBase`: debounce, Manual/Automático, línea de tiempo, motor real, grabación, abrir/guardar/exportar, resumen, ventanas auxiliares, visibilidad. Cada sistema define clases/widgets y los ganchos: `_crear_control`, `_widgets_control_manual`, `_valor_desde_angulo`/`_angulo_desde_valor`, `_resolver_estado`, `_curva_base`, `_preparar_ui`.
  - `ui/epi_hipo_window.py` → `VentanaEpiHipo` (angular, dial) → `VentanaEpitrocoidal`, `VentanaHipotrocoidal` (mismo `Epi_HipotrocoidalV2.ui`; Hipo ajusta rótulo "Engranaje Anular" y 36 dientes por defecto).
  - `ui/trocoidal_window.py` → `VentanaTrocoidal` (lineal, slider de X).
- **Obsoletos (borrar):** `ui/epitrocoidal_window.py`, `EpitrocoidalV2.py`, `Mostrar_Ocultar_Epitrocoide.py`.

---

## 3. Archivos clave (resumen; ver §8 para lo nuevo)

Engine: `motion_engine`, `motor_plan`, `contact_engine` (θ=0 exacto), `rollerpinion_engine` (prrp en Orbitar). Hardware: `motor.py`, `motor_controller.py`. Widgets: `simulation_view.py`, `pg_helpers.py`, `plot_menu.py`, `wheel_widget.py`. Exporters: Excel (hoja 1 CAD), imagen, video MP4. Dialogs/Utils: Mostrar/Ocultar, resumen de diseño, `file_handler`.

---

## 4. Decisiones técnicas

- θ=0 en la raíz: 61 muestras + refinamiento parabólico. Orbitar: factor = cd/prrp.
- Ancho de pluma 1 (cosmética): con antialias, anchos >1 cuestan ~5× por fotograma.
- Motor bloqueante: `MOVE` frena en cada tramo; el resincronizado al pausar minimiza el desfase.
- Camino de contacto solo con piñón Fijo; curva base solo en modo Alterno (Orbitar/Trasladar).
- Mínimo físico por tramo: ACEL·T² ≥ 4·s.

---

## 5. Tests

`python -m pytest tests`

---

## 6. Pendientes

- Prueba visual de Hipotrocoidal y Trocoidal en la app real (contactos, capas, motor).
- Migrar Planetario. Guía técnica. Settings_window definitiva. Radio de fresa editable.
- Exportaciones DXF/CSV/TXT/PDF completas; formato nativo `.rpsf`.
- Preguntas de hardware abiertas (decimales en `MOVE`, respuesta a `S`, reductor, streaming).
- Conceptual: simulación basada en contactos (no solo cinemática).
- Renombrar internamente Cremallera → Trocoidal (`ParametrosCremallera`, `TipoSistema.CREMALLERA`, `cremallera_engine`) si se desea.

---

## 7. Supuestos tomados (sin respuesta explícita)

Q2 diálogos: versión `actualizar_modo`/`HABILITACION_POR_MODO` apuntando a los nuevos `Mostrar_Ocultar_*`. Q3: se conservan los nombres internos de Cremallera. Q8: en Trocoidal el perfil sigue siendo el ángulo del piñón y X = prrp·θ (el motor real usa ese ángulo). Q9: rango de X = [0, longitud de la cremallera]. Q10: en la ventana de propiedades de Trocoidal el dial se sustituye por un slider de X.

---

## 8. Cambios 01-nov-2026 (V2 · lote 1)

- **§8.1 Menú contextual en español** (`widgets/plot_menu.py`): Ver todo, Eje X/Y (autoescala, límites, escala log, invertir), Modo de ratón, Opciones (cuadrícula, Transformadas), Exportar imagen. Sustituye al de pyqtgraph sobreescribiendo `vb.raiseContextMenu`.
- **§8.2 "Ver todo"**: mide solo curvas/puntos visibles (ignora cursor de inspección, líneas, etiquetas); la simulación aporta su proveedor (`resetear_camara`, que ahora incluye el piñón completo).
- **§8.3 Transformadas** solo en la línea de tiempo: ninguna / FFT / derivada / integral; solo cambian lo dibujado. Las marcas de tramo se ocultan fuera del dominio del tiempo.
- **§8.4 Trocoidal**: `SimulationView` soporta modo lineal (patrón se traslada con `setPos`); `ControlLineal` (slider+spinbox); X ↔ θ con prrp.
- **§8.5** `utils/file_handler.py` y `utils/design_report.py` generalizados a los tres sistemas (clave de sistema; el archivo guarda `valor_manual`).
- **§8.6** `engine/hipotrocoidal_engine.py` y `cremallera_engine.py`: versión V1 sin la dependencia de `curva_base_completa` (la curva base la calcula la ventana).

---

## 9. Registro de cambios

| Fecha | Cambio |
|---|---|
| 2026-10-25 | Primera versión: estado de V2 hasta la reconstrucción de los archivos de Designer. |
| 2026-11-01 | Lote 1: menú en español, Ver todo, transformadas, migración de Hipotrocoidal y Trocoidal (§8). |
