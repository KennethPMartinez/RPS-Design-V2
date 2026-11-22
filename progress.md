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
| 2026-11-08 | Lote 2: Planetario + correcciones de 6.2 (contactos hipo, Trocoidal automático dentro de L) (§10). |
| 2026-11-08 | Lote 2: Planetario + correcciones de 6.2 (contactos hipo, Trocoidal automático dentro de L) (§10). |

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
