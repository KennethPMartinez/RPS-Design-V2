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
| Planetario | Migrado (sol epi + anular hipo + N planetas) — pendiente de prueba visual |
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

## 6.2. Respuesta a pendientes

- Se realizo la prueba visual de la operación del aplicativo y funciona adecuadamente, sin embargo el muestreo de los contactos para la ventana hipotrocoidal es de poca resolución en la raiz del diente y produce "saltos".
- La ventana trocoidal requiere revisión en el modo automático porque al ejecutar la simulación nada evita que el piñón se salga del mecanismo (la posición angular no debe superar la máxima para que según tu ecuación de desplazamiento supere la longitud de la cremallera. Esto debería funcionar de acuerdo con L de la cremallera, es decir, los presets deben poder cambiar de acuerdo con L)

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
| 2026-11-08 | Lote 2: Planetario + correcciones de 6.2 (contactos hipo, Trocoidal automático dentro de L) (§10). |
| 2026-11-11 | Lote 3: exportaciones completas, logo, etiquetas del planetario (§11). |
| 2026-11-21 | Lote 4: imágenes de botones/logo, limpieza de duplicados; Ajustes en curso (§12). |
| 2026-11-22 | Lote 5: Ajustes integrados (tema global, FPS), control de banco archivado en `banco_legacy/` (§13). |
| 2026-11-22 | Lote 6: Ajustes → General y Exportación funcionales (§14, §15). |
| 2026-11-22 | Lote 7: Simulación y rendimiento (inválido, pausa, caché) (§16). |

---

## 10. Cambios 08-nov-2026 (V2 · lote 2)

- **§10.1 Planetario migrado** (`engine/planetario_engine.py`, `ui/planetary_window.py`, `widgets/planetary_view.py`, `ui/planetary_property_windows.py`). Sol = `EpitrocoidalEngine`, anular = `HipotrocoidalEngine` con `Za = Zs + 2·Zrp` (mismo prrp, mismo cd). Cinemática por Willis (`Zs·φs + Za·φa = (Zs+Za)·φc`): entrada = 1, bloqueado = 0, el tercero se resuelve (combos válidos: Sol/Anular, Sol/Brazo, Brazo/Anular, Anular/Brazo; si entrada = bloqueado se corrige el bloqueado). El ángulo del motor es el del componente de entrada.
- **§10.2 Contactos del planetario**: cada par (engranaje, planeta) usa el modo "Orbitar" de los engines con el movimiento RELATIVO al engranaje (α = γ − φ_g, giro = ±cd/prrp·α) y el resultado se rota φ_g al mundo. La orientación del planeta se fija con el sol; para el anular, K_i = (Zs+Za)·β_i/Zrp − C/Zrp + π con C = π·(Zrp mod 2) es múltiplo del paso del rodillo si N | (Zs+Za) (solo cambia la etiqueta del rodillo, m_i).
- **§10.3 Número de planetas** (Cálculo_de_numero_de_planetas.pdf): N | (Zs+Za) y D_ap < 2·cd·sin(π/N), con D_ap = 2(mrrp + r_rodillo + t_c + t_w), t_c = 1 mm, t_w = 2 mm. Caso base (12/12/Ø3/8.5/17°): N ∈ {2, 3, 4}; el combo elige el mayor.
- **§10.4 (resp. 6.2) Contactos Hipotrocoidal**: `contact_engine._localizar_contacto` sustituye el refinamiento parabólico sobre d² por un ZOOM sobre la curva exacta (5 pasadas de 21 puntos, ventana ÷10). Test: `theta_local` vs búsqueda densa (< 3e-4 rad).
- **§10.5 (resp. 6.2) Trocoidal automático**: `LineaTiempo.ajustada(lo, hi, escalar)` encaja el perfil en θ ∈ [0, L/prrp]: preset por defecto → se escala (pos/vel/acc son lineales); si aún sobresale se desplaza; perfil editado → solo se desplaza o se recorta (no se escala sin avisar). El editor de línea de tiempo escala los presets que aplica (`escalar_perfil`) y avisa si el perfil excede el recorrido. Se reencaja al cambiar L o cualquier parámetro. También protege al motor real (el plan sale de la misma línea de tiempo).
- **§10.6 Archivos**: `ParametrosPlanetario` gana `componente_entrada`; `Componente(str, Enum)` (serializa a JSON); `file_handler` acepta `PLANETARIO`. `sistema_base.py` gana ganchos (`_crear_vista`, `_alterno`, `_rango_angulo_auto`, `_conectar_modo_pinon`, `_conectar_propiedades`, `_combos_modo`).
- **Pendiente de verificar a mano**: prueba visual del Planetario (4 combinaciones, N = 2/3/4, contactos sol y anular, etiquetas); que el salto de la raíz hipotrocoidal haya desaparecido; Trocoidal automático con L distintos. Opcional: generar `Mostrar_Ocultar_Planetario.py` con `pyside6-uic` (mientras no exista se usa un diálogo equivalente por código).
- **Tests nuevos**: `test_planetario.py` (Willis, N válidos, contactos con sol/anular, rodillo activo = posición en el mundo), `test_contacto_y_rango.py` (refinamiento, `ajustada`, `escalar_perfil`).

---

## 11. Cambios 11-nov-2026 (V2 · lote 3)

- **§11.1 Exportaciones completas** (`exporters/export_manager.py`): Archivo → Exportar abre UN cuadro y el filtro decide el formato. Todos salen del mismo cálculo (`base_exporter.recopilar`, 2001 puntos, θ = 0 en la raíz, unidades mm/rad).
  - **XLSX** (`excel_exporter`): hoja 1 «Perfil diente (CAD)» con SOLO X, Y, Z; luego Perfil (θ, X, Y, generatriz), Ángulo de presión, Radio de curvatura, Camino de contacto y Resumen.
  - **CSV / TXT** (`csv_exporter`): nube de puntos [X, Y, Z, Theta]; CSV con coma, TXT con tabulador y cabecera `#`.
  - **DXF** (`dxf_exporter`): R12 ASCII sin dependencias; polilíneas de 2001 vértices en las capas PERFIL_DIENTE y GENERATRIZ (mm; R12 no declara unidades). Validado con ezdxf (0 errores de auditoría).
  - **PDF** (`pdf_exporter`, `plot_figures`): parámetros de entrada, tolerancias lineal/angular, geometría derivada, resultados críticos con diagnóstico de subcorte y las 4 gráficas (fondo blanco, independiente del tema). Solo Qt: QTextDocument + QPdfWriter, paginado a mano con pie «Página i de n».
  - Planetario: un archivo por engranaje (`_sol`, `_anular`) y un único PDF con resumen cinemático.
  - Formato nativo del proyecto: se mantiene JSON (decisión: lo pueden leer otras aplicaciones). No se crea `.rpsproj`.
- **§11.2 Logo**: `Seleccion_de_sistema.py` importa `Logo_rc` (compilado de `Recursos/Logo.qrc`). `utils/recursos.asegurar_recursos` lo genera en `ui/designer/` al arrancar si falta (pyside6-rcc). Para actualizar el logo: borrar `Logo_rc.py`.
- **§11.3 Planetario, solapamiento de etiquetas**: los N planetas comparten θ_local (reparto simétrico), así que sus marcas caían en el mismo punto; ahora se agrupan en una etiqueta de varias líneas (`P1·R8 / P2·R0 / P3·R4`).
- **Tests nuevos**: `test_exportadores.py` (hoja CAD = X,Y,Z; CSV/TXT; DXF con ezdxf; planetario `_sol/_anular` y PDF).

---

## 12. Cambios 21-nov-2026 (V2 · lote 4)

- **§12.1 Botones de Seleccion_de_sistema sin imagen (causa y arreglo)**: al regenerar con `pyside6-uic`, `ui/designer/Seleccion_de_sistema.py` y `PlanetarioV2.py` quedaron con rutas relativas al .ui (`../../Recursos/x.png`), pero `main.py` hace `os.chdir(RAIZ)`, así que no resolvían (`ui/designer` gana en `sys.path` a `ui/Seleccion_de_sistema.py`, que usaba `Recursos/...`). Arreglo: `utils/recursos.normalizar_rutas_designer(raiz)` reescribe `../../Recursos/` → `Recursos/` en `ui/designer/*.py` al arrancar (idempotente; sobrevive a regenerar con uic) y ya se aplicó a los dos archivos. No se tocaron los .ui.
- **§12.2 Logo roto tras cambiar el .qrc**: `Logo.qrc` pasó a `VisualID/RP-PG-TB_VisualID.png`, pero `Seleccion_de_sistema` (.ui y .py) aún pide `:/newPrefix/RPSDesign_VID.png`, y `asegurar_recursos` no recompilaba si `Logo_rc.py` ya existía. Arreglo: el `.qrc` conserva ambos recursos, y `asegurar_recursos` recompila si cambia el .qrc o cualquier imagen (huella SHA-256 en `ui/designer/.logo_rc.sha256`, en `.gitignore`). `Logo_rc.py` sigue versionado; se regenera solo en la primera ejecución.
- **§12.3 Duplicados eliminados** (parche aplicado dos veces): llamada doble a `asegurar_recursos` en `main.py` y `main.pyw`; `_items_exportacion` / `_html_extra_exportacion` duplicados en `ui/sistema_base.py`; filas repetidas en §9.
- **§12.4 Ajustes**: `tests/RPS_Ajustes_Claude/` (settings_model/store, theme_manager, frame_scheduler, sampling_preferences, settings_adapter) y `ui/designer/Ajustes.ui/.py` están en el repo SIN integrar; `ui/settings_window.py` sigue siendo la versión provisional. Siguiente: integrarlos sin hardware físico en la ventana de Ajustes, conectar el arranque de preferencias y el tema a ventanas nuevas.
- **Tests nuevos**: `test_recursos.py` (normalización de rutas, huella del .qrc).
- **Pendiente de verificar a mano**: abrir la app y comprobar que los 4 botones y el logo muestran imagen; que `Logo_rc.py` se recompila (requiere PySide6 con `pyside6-rcc`).

---

## 13. Cambios 22-nov-2026 (V2 · lote 5: integración de Ajustes)

Fuente: `tests/RPS_Ajustes_Claude/` (guía + prompt) con el **`ui/designer/Ajustes.ui` del repo** (el del usuario, sin tocarlo).

- **§13.1 Módulos integrados**: `config/settings_model.py`, `config/settings_store.py` (QSettings), `ui/selector_color_rps.py` (idéntico byte a byte al original, SHA-256 `24f3003e…`), `ui/theme_manager.py`, `ui/settings_window.py` (sustituye la provisional), `simulation/frame_scheduler.py`, `engine/sampling_preferences.py` y `exporters/settings_adapter.py`. La carpeta `tests/RPS_Ajustes_Claude/` se conserva como referencia.
- **§13.2 .ui del repo ≠ .ui del paquete**: el del repo conserva nombres de Designer (`pushButton`, `pushButton_2/3/4`, `checkBox`, `checkBox_2`, `checkBox_3`) y no tiene los campos de video `comboResolucionVideo`, `comboFPSVideo`, `spinCRFVideo` (solo sus etiquetas). `SettingsWindow` resuelve los nombres con `ALIAS_WIDGETS` (btnCancelar→pushButton_2, btnAplicar→pushButton_3, btnAceptar→pushButton_4, btnRestaurar→pushButton, chkRestaurarSesion→checkBox, chkConfirmarSalir→checkBox_2, chkSimulacionPorContacto→checkBox_3) y trata los tres campos de video como OPCIONALES (se omiten y conservan lo guardado). Para activarlos: añadirlos en Designer con esos nombres.
- **§13.3 Instancia única** (`ui/ajustes_runtime.py`): `runtime.iniciar(app)` (QSettings → `ajustes`, con fallback a predeterminados si la config es ilegible) → `configurar_pyqtgraph`/`aplicar_tema` → `runtime.aplicar_tema_guardado()`. Señal `runtime.cambiado` tras Aplicar/Aceptar; `runtime.abrir_dialogo(parent)` (menú Archivo → Ajustes en `sistema_base`). `widgets/pg_helpers.configurar_menu_plot` aplica el tema vigente a las gráficas nuevas.
- **§13.4 Transacciones**: Aplicar valida, aplica y persiste (el diálogo sigue abierto); Aceptar = Aplicar + cerrar; Cancelar no persiste; Restaurar solo modifica el formulario. Probado en `test_ajustes_qt.py`.
- **§13.5 FPS**: `VentanaSistemaBase` usa `FrameScheduler` sobre el `QTimer` `_anim` (monitor activo / 30–240 / personalizado / sin límite / menos FPS inactivo). El tiempo sigue siendo `time.perf_counter()` (no `1/FPS`).
- **§13.6 Control de banco fuera de la app**: `hardware/`, `engine/motor_plan.py`, `tests/test_motor_plan.py`, `tests/Arduino_Test.py` y `ui/epitrocoidal_window.py` (copia sin uso) pasaron a `banco_legacy/` (no se importa desde la app; `test_motor_plan` sigue pasando). `AjustesMotor` salió de `config/app_settings.py`. Se eliminaron de `sistema_base`: `motor_ctrl`, alineación/desfase, `_resincronizar_con_motor` y el arranque por puerto serie. La app ya no necesita pyserial. CPU/GPU/Híbrido se conserva (NumPy/CuPy).
- **§13.7 Bugs hallados al integrar**: (a) `ThemeManager` ponía `foreground`/`background` de pyqtgraph como `QColor`, pero `simulation_view` y `planetary_view` leen `getConfigOption("foreground")[0]` → ahora tuplas RGB (test de regresión); (b) el repo tiene `Mostrar_Ocultar_Epitrocoide.py` y el código pedía `Mostrar_Ocultar_Epitrocoidal` → `main.py` y `dialogs/mostrar_ocultar_dialog.py` aceptan cualquiera de los dos.
- **Tabla de requisitos**
  | Requisito | Estado |
  |---|---|
  | Tema global (paleta, fuentes UI/gráficas, colores técnicos, trazos) + presets propios | Integrado (probado paleta; falta revisión visual en Windows de widgets con estilo propio en `set_tema`) |
  | Selector de color original | Conservado sin cambios |
  | FPS monitor/fijo/sin límite/inactivo | Integrado (probado intervalo del timer) |
  | Backend CPU/GPU/Híbrido, OpenGL, desviaciones | Integrado vía `ajustes` |
  | Persistencia + Cancelar/Aplicar | Integrado y probado (QSettings en offscreen) |
  | V-Sync | Solo se guarda; no se afirma activo |
  | Simulación por contacto | Solo se guarda; el solver no existe |
  | Detener ante inválido, conservar pausa, caché de geometría | Solo se guardan (sin hooks) |
  | Guardado automático, restaurar sesión, confirmar salida | Solo se guardan (faltan hooks de proyecto/cierre) |
  | Muestreo uniforme/adaptativo | Módulo independiente probado; NO conectado a `contact_engine` (comparar tolerancias primero) |
  | Exportación a resolución/calidad elegidas (`settings_adapter`) | Pendiente de conectar a menú de imagen y a `GrabadorVideo`; campos de video ausentes en el .ui |
  | VP9/WebM | Pendiente (el adaptador lanza `NotImplementedError`) |
  | Migrar tips a la Guía Técnica | Diferido a propósito (solo consignado) |
- **Tests**: `test_ajustes_contract` / `_sampling` / `_widgets` / `_qt` (Qt offscreen), más `banco_legacy/test_motor_plan`. Suite: 44 pasaron, 2 omitidos. Smoke offscreen: arranque, 3 ventanas (Epi, Trocoidal, Planetario) y cambio de FPS sin errores. **No** se probó con ventana real en Windows ni con GPU.
- **§13.8 Trazos enormes al cambiar de tema (corregido)**: `ThemeManager.pen` creaba `QPen` no cosmético, así que el ancho se interpretaba en unidades de datos (mm) y, al aplicar un tema con la ventana abierta, el perfil y los rodillos salían gruesísimos (al abrir una ventana nueva no pasaba porque sus items aún no existían cuando se aplicaba el tema). Ahora `pen.setCosmetic(True)` (ancho en píxeles). Test: `test_trazos_en_pixeles_y_no_en_unidades_de_datos`.

---

## 14. Checklist de la ventana Ajustes (actualizado 22-nov-2026, lote 7)

**Resumen:** 31 funcionales · 5 programadas (se guardan, sin efecto) · 1 no programadas · 37 en total.

General, Exportación y Simulación (salvo V-Sync y contacto) quedan completas. Pendiente: Cálculo (🟡), V-Sync y contacto (🟡) y la migración de tips (❌).

### General

| Función | Estado | Detalle / verificación |
|---|---|---|
| Guardar preferencias (QSettings) | ✅ Funcional | Lo respeta `SettingsStore.save`; sin test del caso «desactivado» |
| Restaurar sesión | ✅ Funcional | Al cerrar cada ventana de sistema se guarda su estado (JSON en la carpeta de datos del usuario) y al abrirla se recupera; apagado = no guarda ni restaura. Probado en las 4 ventanas |
| Confirmar al salir | ✅ Funcional | Ventana de sistema: pregunta Guardar/Descartar/Cancelar solo si hay cambios sin guardar (girar el dial no cuenta). Menú principal: confirma el cierre de la app. Probado |
| Guardado automático + intervalo | ✅ Funcional | Timer por ventana; si hay cambios escribe una copia de recuperación (no toca tu proyecto). Si la sesión terminó mal, al abrir ofrece recuperarla. Probado |
| Avisos de datos | ✅ Funcional | Habilita los avisos no críticos: parámetros fuera de rango, exportar/grabar sin geometría o sin modo automático, perfil no disponible. Los errores (p. ej. archivo inválido) siempre salen. Probado |
| Confirmar sobrescritura | ✅ Funcional | Apagado: los diálogos de guardar no preguntan. Encendido: pregunta también por los archivos derivados (`_sol`, `_anular`). Probado la opción; el diálogo nativo de Windows no |

### Cálculo y precisión

| Función | Estado | Detalle / verificación |
|---|---|---|
| Desviación lineal y angular | ✅ Funcional | `ajustes.desviacion` → `export_manager` (exportaciones); probado Aplicar/Cancelar |
| Habilitar/deshabilitar campos según estrategia | ✅ Funcional | Lógica de la ventana (`_sampling_ui`) |
| Decimales mostrados | 🟡 Programado | Se guarda; ninguna vista/exportador lo lee |
| Estrategia de muestreo (uniforme/adaptativa) + nº de muestras | 🟡 Programado | Se guarda; `sampling_preferences` probado pero NO conectado a `contact_engine` |
| Mostrar estimación de costo | 🟡 Programado | Se guarda; no hay estimador |

### Simulación y rendimiento

| Función | Estado | Detalle / verificación |
|---|---|---|
| FPS (monitor / fijo / personalizado / sin límite) | ✅ Funcional | `FrameScheduler` en cada ventana; probado el intervalo del timer y el cambio en caliente |
| Bajar FPS en ventana inactiva | ✅ Funcional | `FrameScheduler`; sin prueba con ventana real |
| Renderizado Software / OpenGL | ✅ Funcional | `aplicar_opengl`; sin probar en GPU real |
| Procesamiento CPU / GPU / Híbrido | ✅ Funcional | `backend_selector` lee `ajustes.modo_hardware` en cada operación: el cambio aplica en el siguiente cálculo, sin reiniciar. GPU (CuPy/CUDA) sin probar |
| Detener ante estado matemáticamente inválido | ✅ Funcional | Con la simulación en marcha: parámetros inválidos (Epi/Hipo/Trocoidal/Planetario) o un error/ángulo no finito al calcular un fotograma la detienen con aviso; apagado, sigue con la última geometría válida. Probado |
| Conservar resultados al pausar | ✅ Funcional | Al volver a modo Automático se conserva la línea de tiempo y la posición de pausa si el perfil y el recorrido no cambiaron; apagado, reinicia desde t = 0. Probado |
| Reutilizar geometría no modificada | ✅ Funcional | Caché de hasta 8 geometrías (clave: parámetros + tolerancias + backend). Parámetros sin cambios ya no recalculan ni redibujan: 10,9 → 0,9 ms (Epitrocoidal) y 13,8 → 0,4 ms (Trocoidal) por recálculo. Probado en Epi y Planetario |
| V-Sync | 🟡 Programado | Se guarda como «solicitado»; no se aplica ni se afirma activo: un QTimer no sincroniza y el intercambio de buffers no se puede verificar sin GPU real (lo pide así tu guía) |
| Simulación basada en contacto | 🟡 Programado | Se guarda; el solver de contacto no existe y la guía prohíbe sustituir el cálculo cinemático. Requiere diseñarlo (colisiones, estabilidad, tiempo) |

### Apariencia y estilos

| Función | Estado | Detalle / verificación |
|---|---|---|
| Selección de tema/preset | ✅ Funcional | `ThemeManager.apply`: paleta, hoja de estilo, gráficas; probado |
| Colores UI (árbol + selector) | ✅ Funcional | Se aplican a la paleta global; edición manual sin test |
| Colores técnicos | ✅ Funcional | Perfil, piñón, rodillos, camino, etc., también en gráficas nuevas |
| Trazos (tipo, ancho, extremo, unión) | ✅ Funcional | Corregido el ancho (§13.8); confirmado por ti |
| Tipografía UI y de gráficas | ✅ Funcional | Fuente/tamaño/negrita en app y ejes; sin test |
| Antialias | ✅ Funcional | Opción global de pyqtgraph |
| Guardar / Duplicar / Restaurar preset | ✅ Funcional | Código completo; sin tests de estas tres acciones |

### Exportación

| Función | Estado | Detalle / verificación |
|---|---|---|
| Imagen: formato por defecto, resolución, ancho/alto, calidad JPEG, fondo transparente, antialias | ✅ Funcional | `image_exporter` → `settings_adapter.guardar_imagen` (PNG/JPEG); el ancho también rige SVG/PDF. Probado tamaño exacto, calidad y alfa. Transparencia solo en PNG |
| Video: formato (MP4 H.264 / WebM VP9) | ✅ Funcional | `GrabadorVideo` con libx264 o libvpx-vp9; ya sin «(por implementar)». Probado ambos |
| Video: resolución, FPS y calidad (CRF) | ✅ Funcional | Campos creados en código dentro de las filas de tu `.ui` (que solo tenía las etiquetas); si los añades en Designer con esos nombres se usan esos. Probado grabación 320×180 a 24 FPS y lectura de metadatos |
| Video: «Renderizar fotogramas según el tiempo simulado» | ✅ Funcional | Activado: cada fotograma se renderiza a la resolución elegida. Desactivado: captura rápida de la vista tal como se ve (resolución de la ventana) |

### Ventana y persistencia

| Función | Estado | Detalle / verificación |
|---|---|---|
| Aplicar / Aceptar / Cancelar | ✅ Funcional | Probado: Cancelar no persiste, Aplicar sí |
| Restaurar predeterminados (solo formulario) | ✅ Funcional | Confirmación previa; sin test |
| Persistencia en QSettings | ✅ Funcional | Probado ida y vuelta |
| Fallback si las preferencias están corruptas | ✅ Funcional | `runtime.iniciar`; sin test |
| Aplicación en caliente a ventanas abiertas | ✅ Funcional | Tema y FPS (probado; ver §13.8) |
| Ayuda/tips migrados a la Guía Técnica | ❌ No programado | Diferido a propósito |

---

## 15. Lote 6 · General y Exportación (22-nov-2026)

- **§15.1 Sesión y proyecto**: `VentanaSistemaBase` reutiliza el JSON de proyecto (`file_handler.serializar`) para: guardar/abrir (`_aplicar_proyecto`), sesión por sistema (`ui/sesion.py`: `sesion/<SISTEMA>.json`), autoguardado (`autoguardado/<SISTEMA>.json`) y detección de cambios (`_huella_cambios`, sin contar `valor_manual`). Carpeta: datos del usuario (`GenericDataLocation/RPS Design`; en tests `RPS_DATA_DIR`).
- **§15.2 Cambio de comportamiento a tener presente**: con «Restaurar sesión» activo (valor por defecto) cada ventana se abre con los últimos parámetros, modo, perfil y capas usados, no con los predeterminados. Se desactiva en Ajustes → General.
- **§15.3 Grabación**: `_grabar` usa formato, resolución, FPS y CRF de Ajustes. Con «según el tiempo simulado» activo cada fotograma se renderiza (`settings_adapter.renderizar_grafica`) a la resolución elegida con el fondo real de la gráfica; desactivado, `sim.fotograma()` (captura rápida).
- **§15.4 Imágenes**: `exportar_grafica` ya lee Ajustes (antes: 1920 px fijo); el diálogo propone el formato por defecto.
- **§15.5 Modelo**: `formato_video` acepta «WebM — VP9» (y el texto antiguo con «(por implementar)»).
- **Tests**: `test_ajustes_general_export.py` (15). Suite: 60 pasaron, 2 omitidos.
- **No verificado**: diálogos nativos de Windows (sobrescritura), rendimiento de 4K en tu equipo, VP9 con el ffmpeg de tu instalación (aquí funcionó el de imageio-ffmpeg).

---

## 16. Lote 7 · Simulación y rendimiento (22-nov-2026)

- **§16.1 Detener ante inválido**: `_invalido()` (base y Planetario) sustituye los avisos de parámetros inválidos; con la reproducción activa y la preferencia encendida pausa y avisa. `_emitir_estado` pausa si el cálculo de un fotograma falla (antes `manejador_seguro` lo tragaba y seguía fallando a cada tick) y `_mostrar_auto` rechaza ángulos no finitos.
- **§16.2 Conservar resultados al pausar**: `_aplicar_modo` reutiliza la `LineaTiempo` y `_t` si la clave (perfil de movimiento + preset + recorrido permitido) no cambió; `_reconstruir_auto` actualiza esa clave.
- **§16.3 Caché de geometría**: `_geometria()` (LRU de 8). Clave: tipo de parámetros + valores + desviaciones lineal/angular + `modo_hardware`. Si la geometría ya está dibujada se omiten `set_geometria`/`set_curva_base`. Planetario usa el mismo mecanismo.
- **§16.4 No implementados a propósito**: V-Sync (no verificable sin GPU; la guía exige no afirmarlo) y simulación por contacto (no existe el solver).
- **Tests**: `test_simulacion_rendimiento.py` (11). Suite: 71 pasaron, 2 omitidos.
