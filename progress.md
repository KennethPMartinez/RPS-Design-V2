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
| 2026-11-22 | Lote 8: Cálculo y precisión (decimales, discretización, costo) (§17). |
| 2026-11-26 | Lote 9 (261120261): régimen dinámico/contacto cuasiestático, editor de regímenes, HUD (§18). |
| 2026-11-26 | Lote 10 (261120262): la dinámica de contacto gobierna la animación, OpenGL, tema, ω manual, optimización, guía PDF (§19). |
| 2026-11-26 | Lote 11 (261120263): presets con física (modo seguro del banco / realista), PK244-01B, AC con variador, HUD (§20). |

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

## 14. Checklist de la ventana Ajustes (actualizado 22-nov-2026, lote 8)

**Resumen:** 35 funcionales · 2 programadas (se guardan, sin efecto) · 1 no programadas · 38 en total.

General, Exportación, Simulación (salvo V-Sync y contacto) y Cálculo quedan completas. Pendiente: V-Sync y contacto (🟡) y la migración de tips (❌).

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
| Desviación lineal y angular | ✅ Funcional | Definen la resolución de muestreo de la simulación (como dice `AjustesDesviacion`): error máx. a la cuerda [mm] y giro máx. entre mitades de cuerda [°]. Las usa la estrategia adaptativa y la verificación; también se imprimen en el PDF. Probado contra una referencia densa independiente |
| Decimales mostrados | ✅ Funcional | `utils/formato_numerico` (4/6/8/12/Automático, científica si el valor se mostraría como 0) en inspector de gráficas, tablas de propiedades y del perfil de velocidad, resumen/PDF, textos del planetario, dial y barra de estado. Se repinta al Aplicar. Los arrays, el motor y CSV/TXT/XLSX/DXF conservan la precisión completa (probado) |
| Estrategia de muestreo: uniforme | ✅ Funcional | Malla de EXACTAMENTE n muestras con extremos y θ = 0 exactos; si n es par usa n+1 (se informa). Probado |
| Estrategia de muestreo: adaptativa | ✅ Funcional | Subdivisión por niveles con sondas a 1/4, 1/2 y 3/4 de cada tramo; conserva extremos y θ = 0, respeta el máximo de muestras y la profundidad, prioriza los peores tramos y avisa si no cumple. Con la tolerancia por defecto usa ~290 muestras frente a 1001. Probado (error real denso ≤ tolerancia, concentración en curvatura, límites) |
| Habilitar/deshabilitar campos según estrategia | ✅ Funcional | Lógica de la ventana (`_sampling_ui`) |
| Mostrar estimación de costo | ✅ Funcional | Indicador en la barra de estado: nº real de muestras, error y giro máx. frente a la tolerancia, límite alcanzado y tiempo MEDIDO de la última geometría (o «reutilizada de la caché»). No predice tiempos. Probado |

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

---

## 17. Lote 8 · Cálculo y precisión (22-nov-2026)

- **§17.1 Decimales**: `utils/formato_numerico.py` (`fmt`, `fmt_signo`, `configurar`, `clave`) es el único formateador de presentación. Aplicado en `widgets/pg_helpers` (inspector), `ui/property_windows` y `planetary_property_windows` (tablas), `velocity_profile_window`, `utils/design_report` (resumen y PDF), `engine/planetario_engine` (textos), dial y barra de estado. `ui/ajustes_runtime` lo configura al arrancar y al aplicar; `VentanaSistemaBase` repinta (`_refrescar_formato`) solo si el formato cambió. NO se tocó: arrays, algoritmos, CSV/TXT/XLSX/DXF ni los spin de entrada (redondearían parámetros).
- **§17.2 Discretización**: `engine/sampling_preferences.py` añade `Politica`, `MuestreoInfo`, `uniforme_vec`, `adaptativa_vec` y `muestrear` (las funciones antiguas `uniform`/`adaptive` siguen igual). `BaseEngine.generar_perfil(n_puntos=None)` usa la política vigente (simulación); con `n_puntos` explícito (exportaciones/CAD, `tabular_exportacion`) la malla uniforme es la de siempre. El muestreo de contactos de `contact_engine` no se tocó. Sin runtime, la política por defecto es la antigua (uniforme 1001), así que los motores puros no cambian.
- **§17.3 Significado de las desviaciones**: se conserva el de `AjustesDesviacion` («resolución de muestreo de la simulación»): lineal = distancia máxima a la cuerda medida en sondas, angular = giro entre mitades de cuerda. Es una verificación numérica con sondas, no una cota rigurosa.
- **§17.4 Caché**: la clave de geometría ya no usa las desviaciones sueltas sino `Politica.clave` (adaptativa: máx., tol., ang.; uniforme: n y, si se verifica, tol.), de modo que solo se invalida lo que cambia el resultado. Al Aplicar, las ventanas abiertas recalculan sin reiniciar. Actualizado `test_cambiar_la_tolerancia_invalida_la_cache`.
- **§17.5 Costo**: `utils/costo_calculo.py` + etiqueta en la barra de estado (`_lbl_costo`). Solo métricas verificables; el tiempo es el medido de la última geometría. Advertencia (vía «Avisos de datos») cuando se alcanza el límite o la malla uniforme no cumple. Con «Mostrar estimación» la malla uniforme también se verifica (~3n evaluaciones extra).
- **§17.6 Resultados**: con tolerancias por defecto, Epitrocoidal/Hipotrocoidal/Trocoidal usan ~283–303 muestras (antes 1001) con error ≤ 0,3 µm; calcular la geometría tarda 2–3 ms. Tolerancias muy estrictas con límite bajo devuelven `limite_alcanzado` y `cumple = False`.
- **§17.7 Limitaciones**: la malla uniforme con n par usa n+1; el muestreo adaptativo corre en NumPy aunque el backend sea GPU; no hay estimador de tiempo predictivo (a propósito); decimales no afectan los spin de entrada ni los exportados de datos; no se probó en Windows ni con GPU. Tips → Guía Técnica sigue pendiente.
- **Tests**: `test_calculo_precision.py` (17). Suite completa: 88 pasaron, 2 omitidos (preexistentes); sin regresiones.


---

## 18. Lote 9 · Régimen dinámico / contacto (26-nov-2026, entrega 261120261)

### §18.1 Estado previo (ya satisfecho antes de este lote, verificado en el código del repo)
Régimen cinemático completo (F1, F6, F42), los 8 presets (F8), `RegistroLeyes` con rampas/seno/polinomio/puntos/spline (base de F15), encaje del Trocoidal en `0 ≤ x = prrp·θ ≤ L` con escalado/desplazamiento/recorte informado y pos/vel/acc consistentes (F39–F41, §10.5), reproducción por reloj real independiente de FPS (F59 en cinemática), formateo centralizado `utils/formato_numerico` (F62), muestreo uniforme/adaptativo de la geometría (F63, sin conectar a contactos), indicador de costo MEDIDO (F64, sin estimación), `SettingsState.simulacion.basada_en_contacto` solo guardado (F58), y el `.ui` del editor ya traía la pestaña dinámica sin conexiones (F3 visual). Los `.ui` de los sistemas no tenían `lblEstadoSolucionador`/`btnVerResultados`.

### §18.2 Arquitectura añadida (sin capas extra; núcleo común + adaptadores)
- `engine/contacto_fisico.py` — núcleo: `PerfilDentado` (separación con signo g, punto, normal y diente sobre la curva_offset REAL; zoom vectorizado) y `resolver_equilibrio` (unilateral sin fricción: penalización elástica por energía convexa + conjunto activo + Newton con búsqueda lineal; rígido por NNLS con prueba de unicidad).
- `engine/mecanismos_fisicos.py` — adaptadores Epi/Hipo (Fijo: salida engranaje; Orbitar: salida brazo), Trocoidal (Fijo: cremallera; Trasladar: carro) y Planetario (sol–planetas y anular–planetas, GDL = salida + giro de cada planeta). Reutilizan `SolverCinematico` / `PlanetarioEngine.estado` sin tocarlos.
- `engine/accionamiento.py` (Stepper/AC/Custom, capacidad), `engine/cargas.py` (T(t), T(θ), T(ω) con RegistroLeyes), `engine/estudio_fisico.py` (escenarios, ejecución por muestras, eventos, exportación).
- `ui/estudio_qt.py` (`GestorEstudio`: QThread + cancelación cooperativa, estados, huella/invalidación, persistencia), `ui/regimen_dinamico.py` (pestaña dinámica del editor), `widgets/hud.py` (HUD + flechas de fuerza).
- Convenciones: n del material del engranaje hacia el rodillo; F sobre el rodillo = +Fn·n; momentos +z; carga positiva = resistente (Q = −T); mm, N, N·mm (presentación en N·m). Par motor = conjugado de θ del perfil (en Trocoidal el piñón gira −θ: `signo_entrada = −1`).

### §18.3 Cumplimiento de las 64 funciones
Leyenda: ✅ Implementada/Probada · 🟡 Implementada con limitaciones · ⚪ Físicamente indeterminada por falta de datos (tratada explícitamente).

| # | Función | Estado | Evidencia |
|---|---|---|---|
| 1 | Régimen cinemático íntegro | ✅ | sin cambios de comportamiento; suite previa (90) pasa |
| 2 | Régimen dinámico/contacto operativo | ✅ | `ui/regimen_dinamico.py`; `test_cuatro_ventanas_dos_regimenes_y_estudio` |
| 3 | Ambos regímenes en el editor | ✅ | `tabRegimenes` (2 pestañas) probado |
| 4 | Accionamiento, Cargas, Contacto, Integración conectados | ✅ | `listSeccionesEstudio`↔`stackConfiguracion`; formulario ↔ `Escenario` |
| 5 | Referencia temporal común, estados separados | ✅ | `linea_tiempo_para()` (misma LineaTiempo encajada); `ResultadoEstudio` aparte del estado cinemático |
| 6 | Edición de leyes/tramos/reproducción/importar/exportar | ✅ | controlador cinemático intacto (se quitaron solo líneas duplicadas) |
| 7 | Persistencia en el proyecto + compatibilidad | ✅ | clave opcional `estudio_dinamico` (JSON estricto, NaN→null); `test_persistencia_en_proyecto_y_compatibilidad` |
| 8 | 8 presets conservados | ✅ | `FabricaPresets` sin cambios |
| 9 | Escenario dinámico por preset | ✅ | `BibliotecaEscenarios.por_preset`; por defecto SIN carga (no se inventan pares) |
| 10 | Recuperar escenario al seleccionar preset, respetando cambios sin guardar | ✅ | `_preset_cambiado` + diálogo Guardar/Descartar/Cancelar; `test_escenario_por_preset…` |
| 11 | Duplicar/personalizar sin destruir originales | ✅ | «Nuevo escenario…» copia el formulario; presets intactos (probado) |
| 12–14 | Editores T(t), T(θ), T(ω) | ✅ | `engine/cargas.py`; `test_t_de_t_theta_omega_en_el_estudio` |
| 15 | Leyes reutilizadas, dominios, unidades, periodicidad | ✅ | RegistroLeyes; fuera de dominio = Indeterminado salvo periodo; `test_leyes_dominios_y_periodicidad` |
| 16 | Prescrita / motor / calculada inequívocas | ✅ | leyendas [Prescrita] discontinua, [Motor] punteada, [Calculada] continua |
| 17 | Combo Stepper / AC 4p-50 Hz / Custom | ✅ | `comboTipoMotor` con visibilidad por tipo |
| 18 | Stepper: P, n, par de retención, curva | ✅ | retención solo en reposo; fuera: curva o Indeterminado (probado) |
| 19 | AC: f, polos, P, curva/modelo; síncrona vs real | ✅ | n_s = 120f/p = 1500 rpm (probado); sin curva: modelo lineal de deslizamiento declarado, solo en [n_nom, n_s] |
| 20 | Custom obligatorio: valores, curva o expresión validada | ✅ | `compilar_expresion` (AST restringido); vacío = error de validación (probado) |
| 21 | Movimiento impuesto | ✅ | par motor requerido sobre la trayectoria prescrita |
| 22 | Evaluación de capacidad sin alterar la trayectoria | ✅ | `evaluar_capacidad`; la trayectoria no se modifica |
| 23 | Intervalos no viables con causa | ✅ | eventos «Intervalo no viable/indeterminado [t1, t2]» + causa (par > disponible, fuera de curva, sin datos); potencia nominal solo como advertencia |
| 24 | Contactos rodillo–perfil trocoidal real | ✅ | `PerfilDentado` sobre `curva_offset`; |g| < 1e-9 mm en engrane ideal (4 mecanismos) |
| 25 | Separación con signo | ✅ | `test_separacion_con_signo_contacto_y_penetracion` |
| 26 | Normales y puntos de contacto | ✅ | normal unitaria ⟂ flanco (< 1e-6) probada |
| 27 | Unilateral sin fuerza atractiva | ✅ | F ≥ 0; contacto del lado equivocado = 0; sin contacto capaz = «Sin equilibrio» |
| 28 | Rigidez normal parametrizable (modelo elástico simplificado) | ✅ | penalización lineal F = k·max(0, δ); k = 0 → no se asume valor (análisis rígido) |
| 29 | Amortiguamiento solo si es determinable | 🟡 | F = kδ + c·δ̇ con δ̇ de las velocidades relativas PRESCRITAS; nulo en reposo (probado). No modela transitorios (no hay inercias) |
| 30 | Normal sin fricción; tangencial separado | ✅ | `chkIncluirFriccion` deshabilitado con explicación |
| 31 | Reparto por equilibrio + compatibilidad + rigidez | ✅ | F_i ∝ J_i con k igual (12/16 N, no 50/50); holgura retrasa el contacto (analítico exacto) |
| 32 | Componentes radial y tangencial | ✅ | `componentes_locales` (centro del engranaje; cremallera: Y/X) exportadas Fr/Ft |
| 33 | Momentos por brazos y suma por contacto | ✅ | `momentos()` por componente; trabajo virtual verificado a 1e-8 en los 4 mecanismos |
| 34 | Pérdida/recuperación de contacto y conjunto activo | ✅ | eventos por muestra |
| 35 | Inversión de carga, cambio de flanco, backlash | ✅ | eventos + holgura geométrica (suma de separaciones por flanco / |J|) |
| 36 | Análisis en Epi, Hipo, Trocoidal y Planetario (núcleo común) | ✅ | `test_contactos_reales_y_trabajo_virtual_en_los_cuatro` |
| 37 | GDL, modos fijo/alterno y montajes existentes | ✅ | Fijo/Orbitar/Trasladar y combinaciones entrada/bloqueado del planetario |
| 38 | Estado prescrito y resultados físicos independientes | ✅ | q = deflexiones elásticas; el estado cinemático nunca se sobrescribe |
| 39 | Trocoidal 0 ≤ x ≤ L con x = prrp·θ | ✅ | `validar_muestra` + misma LineaTiempo encajada; `test_trocoidal_recorrido_0_a_L` |
| 40 | Adaptar/rechazar presets, informar escalado/desplazamiento/recorte | ✅ | `ajustada` existente; el estudio guarda `meta.transformacion_perfil` |
| 41 | Consistencia pos/vel/acc tras transformar | ✅ | probado (escalado y recorte) |
| 42 | θ(t), ω(t), α(t) en el editor cinemático | ✅ | preexistente |
| 43 | T(t), T(θ), T(ω) prescritas y calculadas (multivaluadas) | ✅ | curvas paramétricas, no se reducen a funciones unívocas |
| 44 | Historial de fuerzas por contacto con selección | ✅ | selección en `tablaTabFuerzasContacto` |
| 45 | Par motor, resistente, transmitido y por componente | ✅ | pestaña Momentos (cuando son determinables; si no, «Indeterminado») |
| 46 | Gráficas/datos cinemático y contacto desacoplados | ✅ | gráficas y modelos separados |
| 47 | Cursor temporal con estado geométrico | ✅ | línea móvil sincronizada → la ventana muestra la geometría y las flechas Fn en ese t (probado) |
| 48 | HUD con velocidades de entrada/salida manteniendo FPS | ✅ | `widgets/hud.py` |
| 49 | Unidades rpm, rad/s, °/s; mm/s en cremallera | ✅ | probado |
| 50 | Relación instantánea con signo y velocidades nulas | ✅ | del MAPA cinemático d(sal)/d(ent) (definida con ω = 0); «∞»/«—» explícitos |
| 51 | Submenú Opciones de la gráfica → Indicadores en pantalla | ✅ | `widgets/plot_menu.py` (FPS, velocidades, relación, unidades), persistente en QSettings |
| 52 | Exportar CSV/JSON con puntos, direcciones y fuerzas individuales | ✅ | serie + `_contactos.csv` (formato largo) y JSON estricto; probado |
| 53 | Equilibrio cuasiestático por muestras, unilateral | ✅ | `ejecutar_estudio` |
| 54 | Tolerancias configurables y dimensionalmente adecuadas | ✅ | N para coordenadas de traslación, N·mm para giros; brecha en mm |
| 55 | Diagnósticos: residuos, penetración, falta de datos, no convergencia | ✅ | pestaña Diagnóstico + mensajes por muestra; `test_no_convergencia_informada` |
| 56 | Sin bloquear la UI (hilo elegido con criterio) | ✅ | QThread (ver docstring de `ui/estudio_qt.py`) |
| 57 | Progreso, cancelación cooperativa, estados, recuperación | ✅ | `test_cancelacion_y_recuperacion` |
| 58 | Activación desde Ajustes (`basada_en_contacto`) | ✅ | apagado: no se ejecuta ni se dibujan fuerzas; `test_activacion_desde_ajustes` |
| 59 | Muestreo/cálculo independientes de los FPS | ✅ | muestras de la LineaTiempo; HUD lee `LineaTiempo.vel` (probado) |
| 60 | Compatibilidad: proyectos, sesión, autoguardado, temas, caché, manual, exportaciones | ✅ | sección opcional; suite previa completa pasa |
| 61 | Pruebas unitarias, Qt y físicas | ✅ | `test_contacto_fisico.py` (24) + `test_regimen_qt.py` (8) |
| 62 | Precisión de presentación centralizada | ✅ | tablas/etiquetas con `fmt`; exportaciones con precisión completa |
| 63 | Muestreo uniforme/adaptativo conectado, extremos y eventos | ✅ | «Usar estrategia de Ajustes» / uniforme / adaptativa: siempre incluye extremos e inversiones; la adaptativa refina cambios de conjunto activo o de estado (probado) |
| 64 | Costo: estimación calibrada vs duración medida | ✅ | «Estimar costo» mide 3 muestras reales y extrapola (etiquetado ESTIMACIÓN); al terminar, «s medidos» |

Ventanas principales: `lblEstadoSolucionador` (Sin estudio · Calculando · Finalizado · Cancelado · Error · Desactualizado) y `btnVerResultados` añadidos en los 3 `.ui` (Designer) y regenerados; el botón de línea de tiempo abre el editor de regímenes; la ejecución sigue SOLO en el editor. Finalizado solo tras una ejecución válida; cambiar geometría, perfil, modo, discretización o física lo pasa a Desactualizado (y vuelve a Finalizado si se restaura la misma configuración). `§14`: «Simulación basada en contacto» deja de ser solo guardada.

### §18.4 Limitaciones físicas verificadas (no se inventan datos)
- Sin masas ni inercias en el proyecto: no hay impactos, vibraciones, aceleraciones libres ni dinámica transitoria; el amortiguamiento solo usa velocidades prescritas.
- Rigidez normal = dato de entrada (0 por defecto). Sin ella, con varios contactos el reparto es INDETERMINADO (hiperestático o precarga entre flancos opuestos con geometría ideal sin holgura). En ese caso el par motor sí se informa por TRABAJO VIRTUAL (válido sin fricción ni inercia; verificado a 1e-8), etiquetado como tal.
- La geometría actual es ideal (holgura ≈ 1e-16 rad): el backlash se calcula pero será nulo hasta que exista geometría con holgura/tolerancias.
- Motor: acople directo supuesto (no hay reductor ni variador en el modelo); un AC sin curva solo se evalúa en su zona lineal de deslizamiento; fuera de los datos = Indeterminado.
- Rigidez única por contacto (no por material/radio de curvatura, Hertz pendiente); sin fricción.
- Reparto rígido multi-GDL: la unicidad se demuestra para nulidad ≤ 1; si no, se informa Indeterminado (conservador).
- No probado: Windows real, GPU, diálogos nativos.


---

## 19. Lote 10 · La dinámica gobierna a la cinemática (26-nov-2026, entrega 261120262)

Pedidos del usuario (8) y su estado:

| # | Pedido | Estado | Evidencia / detalle |
|---|---|---|---|
| 1 | OpenGL no funcionaba | ✅ Corregido | Causa: `_PLOTS` (WeakSet) conservaba envoltorios de gráficas ya destruidas (el editor se borra al cerrarse) y `useOpenGL` lanzaba `RuntimeError: Internal C++ object already deleted`, que hacía fallar TODO el cambio. `pg_helpers.plots_vivos()` las filtra (shiboken6.isValid); si de verdad falla un driver se revierte a software en todas y el diálogo informa el motivo (`ULTIMO_ERROR_OPENGL`). Test `test_opengl_ignora_graficas_destruidas`. No verificado con GPU real. |
| 2 | ω en modo manual | ✅ | Derivada del control respecto al RELOJ REAL (ventana 0,25 s; 0 tras 0,3 s quieto; refresco 150 ms), marcada en el HUD como estimada. Alimenta también T(ω). Test `test_modo_manual_omega_y_fuerzas_en_vivo` |
| 3 | Gráfica de la línea de tiempo sin colores del tema | ✅ | Curvas (posición = Piñón de rodillos, velocidad = Curva base, aceleración = Perfil/engranaje), marcas y la rueda (antes blanca fija) toman los colores técnicos; `ThemeManager.apply_to_plot` llama al gancho `plot._retemar`. Mismo criterio en las gráficas del estudio. Test `test_editor_sigue_el_tema` |
| 4 | Sin comunicación del modo contacto con la ventana principal | ✅ | Etiqueta «Simulación por contacto ACTIVA · estado», HUD con par motor/Fn máx./estado del motor, flechas de fuerza, deformación amplificable (×1–×1000, menú Indicadores) en Automático y en Manual (equilibrio en vivo con el escenario que muestra el editor) |
| 5 | Optimización general y valores por defecto | ✅ | `ContactEngine._localizar_contacto` vectorizado (bit a bit idéntico a la referencia, conservada como `_localizar_contacto_referencia`; test): Planetario 11 → 5 ms/fotograma, Epi 1,5 → 1,1 ms. Muestras base del flanco en caché. Integración: tablas periódicas, carga y curva del motor precompiladas, cinemática lineal cacheada (21 s → ~5 s para 40 000 pasos). Valores por defecto verificados: FPS automático, render Software, CPU, muestreo adaptativo, caché activa (ver guía §7) |
| 6 | El régimen dinámico gobierna al cinemático | ✅ | `engine/dinamica_contacto.py`: integración temporal Newmark implícito (γ 0,6, β 0,3025) + Newton; la salida (y cada planeta) se mueve solo por las fuerzas de contacto; inercias como datos (0 = sin masa = equilibrio instantáneo). Con «Evaluación de capacidad» el motor pierde sincronismo si no le alcanza el par y se re-engancha. ▶ sin estudio vigente lo calcula y reproduce al terminar; la animación usa θ integrado + deflexión. Método por defecto: «Integración temporal (dinámica de contacto)» |
| 7 | Revisar la conversación de ChatGPT | ⚪ No accesible | La página compartida carga con JavaScript y desde aquí solo se obtuvo el título («Recordar aplicación»). Pegar el texto o exportarlo para revisarlo |
| 8 | Guía técnica en PDF | ✅ | `docs/Guia_tecnica_RPS_Design_V2.pdf` (17 págs., 13 capturas reales, índice con marcadores): manual por ventana, fundamentos (geometría, detector, cuasiestático, dinámica), convenciones, flujo recomendado, solución de problemas, limitaciones. Info → Guía técnica la abre (`utils/guia.py`). Fuentes y capturas regenerables en `docs/fuentes_guia/` |

### §19.1 Modelo dinámico
- Coordenadas: θ (entrada; prescrita mientras el motor la sostiene) y q (deflexión de la salida y del giro de cada planeta respecto a la cinemática del θ REAL). T = ½I_eθ̇² + ½ΣI_c(R_cθ̇ + q̇_c)²; contactos δ = −g(θ) + J·q, F = max(0, kδ + cδ̇); M·ẍ + Gᵀ·F = Q (+ par motor en θ).
- Validación: límite sin inercias = cuasiestático (T_m = T·rel, mediana exacta, <1 % al entrar un rodillo por el amortiguamiento); par inercial T_m = I_s·rel²·θ̈ (<3 %); 4 mecanismos sin saltos de diente (q < 0,01); pérdida de sincronismo con motor débil (θ real ≠ θ prescrito). `tests/test_contacto_fisico.py::Dinamica`.
- Bug encontrado al integrar (también afectaba al cuasiestático): en la arista de la cresta el signo de la separación salía invertido para un rodillo tocando la punta (g ≈ −2r). Ahora el centro está fuera si queda del lado libre de cualquiera de los dos flancos.
- Requisitos: penalización elástica con rigidez > 0 (no hay modelo de impactos rígidos). Sin ella, ▶ avisa y reproduce la cinemática.
- Limitaciones nuevas: carga dependiente del estado evaluada con un paso de retraso; servo ideal limitado por la curva (sin modelo eléctrico); la tabla periódica de la cremallera no modela sus extremos; la vibración de contacto solo se resuelve si el paso es < 1/10 del periodo (`meta.resuelve_vibracion_contacto`).

### §19.2 Archivos
Nuevos: `engine/dinamica_contacto.py`, `utils/guia.py`, `docs/Guia_tecnica_RPS_Design_V2.pdf`, `docs/fuentes_guia/` (generador, capturas). Modificados: `engine/contact_engine.py`, `engine/contacto_fisico.py`, `engine/mecanismos_fisicos.py`, `engine/estudio_fisico.py`, `engine/accionamiento.py`, `engine/cargas.py`, `ui/sistema_base.py`, `ui/planetary_window.py`, `ui/estudio_qt.py`, `ui/regimen_dinamico.py`, `ui/velocity_profile_window.py`, `ui/theme_manager.py`, `ui/settings_window.py`, `widgets/hud.py`, `widgets/plot_menu.py`, `widgets/pg_helpers.py`, `widgets/wheel_widget.py`, pruebas.
- **Tests**: 134 (31 de física/dinámica/optimización, 13 Qt del régimen, resto previos). Sin regresiones. Arranque de la app verificado (offscreen).


---

## 20. Lote 11 · Los presets imponen la física (26-nov-2026, entrega 261120263)

Base: cambios del usuario en el repo (`c187535`, `267b8df`): se retiraron del `.ui` del editor `comboModoAccionamiento` («Movimiento impuesto») y `spinVelocidadNominal`; en Ajustes se añadió «Modo seguro para banco de pruebas» (`chkBajarFPSInactivo_2`, marcado por defecto).

| Pedido | Estado | Detalle |
|---|---|---|
| Valores por defecto de Stepper y AC | ✅ | Stepper = **PK244-01B** de la ficha del usuario: retención 0,26 N·m, J rotor 54×10⁻⁷ kg·m² = 5,4 kg·mm², curva de par de salida a 24 VDC y 1,2 A/fase (paso completo, leída del diagrama), potencia ≈ 14,4 W (máx. T·ω de la curva). AC = 4 polos, 50 Hz, 250 W con variador: par nominal P/ω_nom (n_nom = 0,95·n_s, hipótesis de deslizamiento 5 %) constante y potencia constante hasta 2·n_s; par nominal y curva se regeneran al cambiar P, f o polos. Elegir el tipo de motor carga sus valores |
| Retirar rpm impuestas y «Movimiento impuesto» | ✅ | `ModeloMotor.modo` siempre = capacidad (los proyectos anteriores se convierten al abrir); sin velocidad nominal en el modelo AC ni en Custom por valores (esquina = P/T) |
| Presets imponen cargas e inercias | ✅ | `engine/presets_fisicos.py`: una aplicación por preset (banda transportadora, alimentador vibratorio 100 Hz, ensayo de holgura, actuador de válvula 90°, volteador 180°, mesa indexadora, tambor de lavadora, vibrador) con perfil de la SALIDA, carga e inercia típicas y su origen. «Aplicar» en el régimen cinemático impone motor, carga e inercias como «Escenario asociado al preset» (un escenario guardado por el usuario tiene prioridad) |
| Relación de transmisión nominal | ✅ | entrada = salida·i (velocidad ×i) y la carga se refleja ÷i; cremallera: x = r·φ con r = prrp (masa J/r², fuerza T/r, abscisas en mm y mm/s) |
| Modo seguro del banco | ✅ | PK244-01B, sin carga externa (el banco opera sin carga), inercias del banco (rotor + engranaje 7075 de 4 mm, estimación geométrica por la fórmula de Green). Misma forma de movimiento; solo se estira el tiempo (posiciones iguales, v ÷ s, a ÷ s²) hasta < 600 rpm en la entrada y par ≤ par de salida/2 |
| Modo realista con motor dimensionado | ✅ | stepper (NEMA 17/23/34, curva PK244 escalada al par de retención típico, FS 2) para posicionar o AC 4 polos con variador (0,09–4 kW IEC) para giro continuo: el más pequeño que cubre el par requerido; si ninguno alcanza se asigna el mayor y el estudio muestra los intervalos no viables |
| Bug: el HUD desaparece al cambiar Ajustes | ✅ (no reproducible aquí con OpenGL real) | Al cambiar el render se crea un viewport nuevo que queda ENCIMA de la etiqueta del HUD. Ahora el HUD se trae al frente en cada repintado y tras cada cambio de viewport. Test `test_hud_queda_encima_del_viewport`. Además, el error de OpenGL de `ajustes_runtime.aplicar` también informa el motivo |
| Bug encontrado al probar | ✅ | Al cargar un escenario el formulario redondea a sus decimales y quedaba «sin guardar» al instante (diálogo modal inesperado). La base se toma ahora del formulario |

- Valores de aplicación (fuentes indicadas en el informe del editor y en la guía §5.3): ejemplo de mesa indexadora de Oriental Motor (J_L = 265,44×10⁻⁴ kg·m², T_L = 0), actuadores de válvula de 20–50 N·m en 4–90 s, alimentadores de 100–180 Hz con ≈ 0,6 mm de amplitud, arranque suave de transportadores con variador; el resto son estimaciones de dimensionado declaradas como tales.
- Pendiente/criterio: la línea de tiempo «predeterminada» de cada ventana sigue siendo la histórica (80 °/s) hasta que se aplica un preset en el editor.
- **Tests**: 141 (+7: ficha PK244, estiramiento temporal, modos seguro/realista, relación ×i/÷i, preset en el editor, valores por defecto del motor, HUD). Guía técnica actualizada (18 págs.).
