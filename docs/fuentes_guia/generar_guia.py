# -*- coding: utf-8 -*-
"""Genera docs/Guia_tecnica_RPS_Design_V2.pdf (manual de usuario + fundamentos técnicos)."""
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, Spacer, Table, TableStyle)
from reportlab.platypus.doctemplate import BaseDocTemplate, PageTemplate
from reportlab.platypus.frames import Frame
from reportlab.platypus.tableofcontents import TableOfContents

D = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", D + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", D + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVI", D + "DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DVM", D + "DejaVuSansMono.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily  # noqa: E402
registerFontFamily("DV", normal="DV", bold="DVB", italic="DVI", boldItalic="DVB")

REPO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
IMG = Path(__file__).parent / "img"
SALIDA = REPO / "docs" / "Guia_tecnica_RPS_Design_V2.pdf"
AZUL, NARANJA, GRIS = colors.HexColor("#0E2A4A"), colors.HexColor("#E08A2E"), colors.HexColor("#5B6B7C")

ss = getSampleStyleSheet()
S = {
    "t": ParagraphStyle("t", fontName="DVB", fontSize=26, leading=32, textColor=AZUL, alignment=TA_CENTER),
    "st": ParagraphStyle("st", fontName="DV", fontSize=13, leading=18, textColor=GRIS, alignment=TA_CENTER),
    "h1": ParagraphStyle("h1", fontName="DVB", fontSize=17, leading=22, textColor=AZUL, spaceBefore=6, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="DVB", fontSize=12.5, leading=16, textColor=AZUL, spaceBefore=8, spaceAfter=4),
    "p": ParagraphStyle("p", fontName="DV", fontSize=10, leading=14.2, alignment=TA_JUSTIFY, spaceAfter=5),
    "li": ParagraphStyle("li", fontName="DV", fontSize=10, leading=13.6, leftIndent=14, bulletIndent=4, spaceAfter=2),
    "cap": ParagraphStyle("cap", fontName="DVI", fontSize=8.6, leading=11, textColor=GRIS, alignment=TA_CENTER,
                          spaceAfter=8),
    "eq": ParagraphStyle("eq", fontName="DVM", fontSize=9.2, leading=13, leftIndent=18, spaceAfter=5,
                         textColor=colors.HexColor("#1B3B5E")),
    "nota": ParagraphStyle("nota", fontName="DV", fontSize=9.4, leading=13, backColor=colors.HexColor("#FFF4E5"),
                           borderColor=NARANJA, borderWidth=0.6, borderPadding=6, spaceBefore=4, spaceAfter=9),
    "td": ParagraphStyle("td", fontName="DV", fontSize=8.8, leading=11.4),
    "th": ParagraphStyle("th", fontName="DVB", fontSize=8.8, leading=11.4, textColor=colors.white),
    "toc1": ParagraphStyle("toc1", fontName="DVB", fontSize=10.5, leading=16, leftIndent=8),
    "toc2": ParagraphStyle("toc2", fontName="DV", fontSize=9.5, leading=13, leftIndent=24),
}


class Doc(BaseDocTemplate):
    def __init__(self, f, **kw):
        super().__init__(f, pagesize=A4, leftMargin=2.1 * cm, rightMargin=2.1 * cm, topMargin=2.2 * cm,
                         bottomMargin=2 * cm, title="Guía técnica — RPS Design V2", author="RPS Design V2",
                         subject="Manual de usuario y fundamentos técnicos", **kw)
        fr = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="f")
        self.addPageTemplates([PageTemplate("p", [fr], onPage=self._pie)])

    def _pie(self, c, d):
        if d.page == 1:
            return
        c.saveState()
        c.setFont("DV", 8); c.setFillColor(GRIS)
        c.drawString(2.1 * cm, 1.2 * cm, "RPS Design V2 · Guía técnica (manual de usuario)")
        c.drawRightString(A4[0] - 2.1 * cm, 1.2 * cm, f"Página {d.page}")
        c.setStrokeColor(NARANJA); c.setLineWidth(0.8)
        c.line(2.1 * cm, A4[1] - 1.6 * cm, A4[0] - 2.1 * cm, A4[1] - 1.6 * cm)
        c.restoreState()

    def afterFlowable(self, fl):
        if isinstance(fl, Paragraph) and fl.style.name in ("h1", "h2"):
            nivel = 0 if fl.style.name == "h1" else 1
            texto = fl.getPlainText()
            clave = f"k{id(fl)}"
            self.canv.bookmarkPage(clave)
            self.canv.addOutlineEntry(texto, clave, level=nivel, closed=nivel > 0)
            self.notify("TOCEntry", (nivel, texto, self.page, clave))


st = []
H1 = lambda t: st.append(Paragraph(t, S["h1"]))
H2 = lambda t: st.append(Paragraph(t, S["h2"]))
P = lambda t: st.append(Paragraph(t, S["p"]))
EQ = lambda t: st.append(Paragraph(t, S["eq"]))
NOTA = lambda t: st.append(Paragraph(t, S["nota"]))


def L(*items):
    for i in items:
        st.append(Paragraph(i, S["li"], bulletText="•"))
    st.append(Spacer(1, 4))


def FIG(nombre, cap, ancho=16.6):
    ruta = IMG / f"{nombre}.png"
    if not ruta.exists():
        return
    from PIL import Image as PI
    w, h = PI.open(ruta).size
    a = ancho * cm
    al = a * h / w
    if al > 14.5 * cm:
        al = 14.5 * cm; a = al * w / h
    st.append(KeepTogether([Image(str(ruta), width=a, height=al), Paragraph(cap, S["cap"])]))


def TAB(filas, anchos):
    data = [[Paragraph(str(c), S["th"] if i == 0 else S["td"]) for c in f] for i, f in enumerate(filas)]
    t = Table(data, colWidths=[w * cm for w in anchos], repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), AZUL), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#B8C4D0")),
                           ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
                           ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]))
    st.append(t); st.append(Spacer(1, 8))


# ============================================================ portada
logo = REPO / "Recursos" / "RPSDesign_VID.png"
st.append(Spacer(1, 3 * cm))
if logo.exists():
    from PIL import Image as PI
    w, h = PI.open(logo).size
    caja = Table([[Image(str(logo), width=11 * cm, height=11 * cm * h / w)]], colWidths=[14 * cm])
    caja.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), AZUL), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                              ("TOPPADDING", (0, 0), (-1, -1), 18), ("BOTTOMPADDING", (0, 0), (-1, -1), 18)]))
    st.append(caja)
    st.append(Spacer(1, 1 * cm))
st.append(Paragraph("RPS Design V2", S["t"]))
st.append(Spacer(1, 0.4 * cm))
st.append(Paragraph("Guía técnica · Manual de usuario", S["st"]))
st.append(Spacer(1, 0.3 * cm))
st.append(Paragraph("Diseño y simulación de sistemas de piñón de rodillos: Epitrocoidal, Hipotrocoidal, "
                    "Trocoidal (cremallera) y Planetario, con régimen cinemático y régimen dinámico por contacto",
                    S["st"]))
st.append(Spacer(1, 4 * cm))
st.append(Paragraph("Semillero TAMA · Facultad de Ingeniería Mecánica · Universidad Santo Tomás<br/>"
                    "Versión de la aplicación: V2 (lote 10, noviembre de 2026)", S["st"]))
st.append(PageBreak())
st.append(Paragraph("Contenido", ParagraphStyle("c0", parent=S["h1"])))
toc = TableOfContents()
toc.levelStyles = [S["toc1"], S["toc2"]]
st.append(toc)
st.append(PageBreak())

# ============================================================ 1
H1("1. Introducción")
P("RPS Design V2 es una aplicación de escritorio (Python 3.11+, PySide6, PyQtGraph) para diseñar el perfil "
  "trocoidal de engranajes que engranan con un <b>piñón de rodillos</b> y para simular su funcionamiento. Calcula "
  "la geometría del diente, el ángulo de presión, el radio de curvatura y el camino de contacto; anima el "
  "mecanismo; y, con la <b>simulación basada en contactos</b> activa, calcula las fuerzas entre cada rodillo y el "
  "flanco real, el par que exige o puede dar el motor y el movimiento que resulta de esas fuerzas.")
P("Esta guía explica cómo usar cada ventana (capítulos 2 a 9), los fundamentos de cálculo y las convenciones "
  "(capítulo 10), un flujo de trabajo recomendado (capítulo 11) y la solución de problemas frecuentes "
  "(capítulo 12). Las limitaciones físicas se resumen en el capítulo 13.")
TAB([["Sistema", "Engranaje", "Movimiento de la salida"],
     ["Epitrocoidal", "Engranaje externo (epitrocoide)", "Giro del engranaje (Fijo en X+) o del brazo (Orbitar)"],
     ["Hipotrocoidal", "Engranaje anular interno (hipotrocoide)", "Giro del anular (Fijo) o del brazo (Orbitar)"],
     ["Trocoidal", "Cremallera de longitud L", "Traslación de la cremallera (Fijo en origen) o del carro (Trasladar)"],
     ["Planetario", "Sol epitrocoidal + anular hipotrocoidal + N planetas",
      "Componente libre según entrada y bloqueado (relación de Willis)"]], [3.2, 6.2, 7.4])

# ============================================================ 2
H1("2. Instalación y arranque")
L("Requisitos: Windows 10/11 (o Linux/macOS), Python 3.11 o superior.",
  "Instalación de dependencias: <font name='DVM'>pip install -r requirements.txt</font> "
  "(PySide6, pyqtgraph, numpy, openpyxl, imageio, imageio-ffmpeg). CuPy es opcional (modo GPU/Híbrido).",
  "Arranque: <font name='DVM'>python main.py</font> (o doble clic en <font name='DVM'>main.pyw</font> para no abrir "
  "la consola).",
  "Pruebas: <font name='DVM'>python -m pytest tests --ignore=tests/RPS_Ajustes_Claude</font>.")
P("Al arrancar se cargan las preferencias guardadas (Ajustes) y se abre el <b>menú principal</b>. Si alguna "
  "preferencia está dañada, la aplicación arranca con los valores predeterminados.")
FIG("menu", "Figura 1. Menú principal: selección del sistema.", 12)

# ============================================================ 3
H1("3. Ventana de sistema")
P("Las cuatro ventanas comparten la misma organización: <b>parámetros principales</b> a la izquierda, la "
  "<b>vista de simulación</b> en el centro y las <b>opciones de simulación</b>, el <b>control manual</b> y el "
  "<b>control automático</b> a la derecha.")
FIG("epi_manual", "Figura 2. Ventana Epitrocoidal en modo manual.")
H2("3.1 Parámetros principales")
TAB([["Parámetro", "Significado", "Notas"],
     ["Número de dientes", "Z del engranaje (externo, anular o sol)", "Planetario: Z del anular = Zs + 2·Zrp"],
     ["Número de rodillos", "Zrp del piñón de rodillos", "≥ 3"],
     ["Diámetro de rodillos", "d del rodillo (mm)", "radio r = d/2"],
     ["Distancia entre centros de rodillos", "rd (mm) entre rodillos vecinos", "mrrp = rd / (2·sen(π/Zrp))"],
     ["Ángulo de presión mínimo", "α mín. (°), rango [1°, 45°]", "prrp = mrrp / cos(α mín.)"],
     ["Longitud de la cremallera", "L (mm), solo Trocoidal", "el recorrido cumple 0 ≤ x = prrp·θ ≤ L"]],
    [4.2, 6.2, 6.4])
P("Cualquier cambio recalcula la geometría (con un retardo corto para no recalcular a cada tecla). Si la "
  "geometría ya se calculó con los mismos parámetros, se reutiliza de la caché.")
H2("3.2 Simulación manual y automática")
L("<b>Manual</b>: el dial (o el deslizador X en Trocoidal) fija la posición del piñón. El dial funciona como "
  "un encoder incremental: acumula vueltas.",
  "<b>Automático</b>: la posición sale de la <b>línea de tiempo</b> (perfil de movimiento).  «Editar línea de tiempo» abre el <b>editor de regímenes</b>.",
  "<b>Modo del piñón</b>: Fijo (el engranaje gira y el piñón queda en su eje) o alterno (Orbitar / Trasladar: "
  "el engranaje queda fijo y el piñón se mueve).",
  "«Valores predeterminados» usa el preset de movimiento por defecto; al aceptar un perfil editado se desmarca.")
H2("3.3 Indicadores en pantalla (HUD)")
P("En la esquina de la vista se muestran los FPS, las velocidades instantáneas de entrada y salida y, si se "
  "activa, la relación de transmisión instantánea. Se configuran con clic derecho sobre la vista → "
  "<b>Opciones de la gráfica → Indicadores en pantalla</b>: FPS, velocidades, relación, unidades angulares "
  "(rpm, rad/s, °/s; la cremallera siempre en mm/s) y la <b>amplificación de deformaciones</b> (×1 a ×1000), "
  "que solo exagera visualmente la deflexión calculada por contacto.")
L("En Automático las velocidades salen de la línea de tiempo o, si la simulación por contacto gobierna, del "
  "movimiento integrado; nunca del tiempo entre fotogramas.",
  "En Manual la velocidad es la derivada del control respecto al reloj real (ventana de 0,25 s) y vuelve a 0 "
  "cuando se suelta el control; el HUD lo indica.",
  "La relación i = ω<sub>ent</sub>/ω<sub>sal</sub> se obtiene del mapa cinemático, de modo que está definida "
  "incluso en reposo; conserva el signo (sentido de giro).")
H2("3.4 Menús")
TAB([["Menú", "Contenido"],
     ["Archivo", "Abrir / Guardar proyecto (JSON), Exportar (XLSX, CSV, TXT, DXF, PDF), Ajustes, Resumen de "
                 "diseño, Cerrar"],
     ["Propiedades físicas", "Perfil del diente, ángulo de presión, radio de curvatura y camino de contacto en "
                             "ventanas independientes"],
     ["Info", "Guía técnica (este documento)"]], [4, 12.8])
H2("3.5 Estado de la simulación por contacto")
P("Debajo del botón de la línea de tiempo aparecen el <b>estado del estudio físico</b> (Sin estudio, "
  "Calculando, Finalizado, Cancelado, Error, Desactualizado) y el botón <b>Ver resultados</b>, que solo se "
  "habilita con un estudio vigente. El estudio pasa a «Desactualizado» cuando cambian la geometría, el perfil, "
  "el modo del piñón, la discretización o los parámetros físicos.")

# ============================================================ 4
H1("4. Editor de regímenes · régimen cinemático")
FIG("editor_cinematico", "Figura 3. Régimen cinemático: preset, rueda de vista previa, curvas θ, ω, α y tramos.")
L("<b>Presets</b>: Arranque y parada suaves, Oscilador 100 Hz, Backlash, Giro de 90°, Giro de 180°, Indexer, "
  "Lavadora y Vibrador. «Aplicar» carga el preset (en Trocoidal se escala al recorrido de la cremallera).",
  "<b>Tramos</b>: intervalos [t₁, t₂] con valores Y₁, Y₂ de la propiedad de entrada (posición, velocidad o "
  "aceleración).",
  "<b>Funciones de movimiento</b> por tramo (se suman): rampa lineal, rampa cúbica, cicloidal, armónica, "
  "sinusoidal, sinusoidal modificada, polinómica, lista de puntos, spline (independiente) y trapezoidal "
  "modificada.",
  "<b>Mostrar curvas</b>: posición, velocidad y aceleración. El menú contextual agrega transformadas (FFT, "
  "derivada, integral) que solo cambian lo que se dibuja.",
  "Archivo: abrir/guardar el perfil (JSON) y exportar CSV. «Aceptar» aplica el perfil a la ventana.")

# ============================================================ 5
H1("5. Editor de regímenes · régimen dinámico / contacto")
NOTA("Requisito: <b>Ajustes → Simulación → «Habilitar análisis basado en contacto»</b>. Con la opción apagada "
     "la configuración se puede editar, pero no se ejecutan estudios y la animación es puramente cinemática.")
P("La pestaña tiene cuatro secciones de configuración y un panel de gráficas. El <b>escenario</b> agrupa toda "
  "la configuración física y se puede asociar a cada preset de movimiento.")
H2("5.1 Escenarios")
L("<b>Personalizado (sin carga externa)</b>: escenario base, sin pares asignados.",
  "<b>Escenario asociado al preset</b>: cada preset recuerda su escenario; al cambiar de preset se recupera el "
  "suyo (si hay cambios sin guardar, se pregunta).",
  "<b>Nuevo escenario…</b>: duplica la configuración vigente con un nombre propio. Los presets de movimiento "
  "originales nunca se modifican.",
  "«Guardar escenario…» guarda en la selección actual; «Restablecer» descarta los cambios sin guardar.")
H2("5.2 Accionamiento")
FIG("editor_accionamiento", "Figura 4. Accionamiento: tipo de motor, modo de evaluación, datos e inercia de entrada.")
TAB([["Motor", "Datos", "Par disponible"],
     ["Stepper", "Potencia y velocidad nominales, par de retención, curva par–velocidad",
      "Curva tabulada; el par de retención solo vale en reposo"],
     ["AC (4 polos, 50 Hz por defecto)", "Frecuencia, polos, potencia y velocidad nominales, curva",
      "Curva; sin curva, modelo lineal de deslizamiento entre n<sub>nom</sub> y n<sub>s</sub> = 120·f/p"],
     ["Custom", "Obligatorio: curva, expresión T(n) o par/potencia/velocidad",
      "Expresión segura en n (rpm) o w (rad/s); por valores: par constante y luego potencia constante"]],
    [3.4, 6.6, 6.8])
L("<b>Movimiento impuesto</b>: la entrada sigue exactamente el perfil y se calcula el par requerido.",
  "<b>Evaluación de capacidad</b>: además compara el par requerido con el disponible. En la integración temporal "
  "el motor <b>pierde sincronismo</b> si no le alcanza el par: se satura, la entrada se retrasa y vuelve a "
  "engancharse cuando iguala la velocidad del perfil.",
  "La potencia nominal es capacidad de régimen continuo, no potencia entregada. Sin datos suficientes el "
  "resultado es <b>Indeterminado</b>, nunca «Viable».",
  "<b>Inercia de entrada</b> (motor + piñón, kg·mm²): 0 significa «sin masa» (no se asume ningún valor).")
H2("5.3 Cargas externas")
FIG("editor_cargas", "Figura 5. Cargas: variable independiente, ley, punto de aplicación e inercia de la salida.")
L("Variable independiente: tiempo T(t), posición T(θ) o velocidad T(ω) del componente donde se aplica (en la "
  "cremallera, x en mm y v en mm/s).",
  "Leyes: constante, rampas, sinusoidal (offset + amplitud, frecuencia y fase), polinómica (fila i = a<sub>i</sub>), "
  "lista de puntos (ajuste de grado n) y spline. Las tabuladas valen solo entre su primer y último punto; "
  "fuera de ese dominio la carga es Indeterminada, salvo que se indique un periodo.",
  "Signo: un valor positivo es <b>resistente</b> (se opone al sentido positivo del componente).",
  "Aplicación: componente de salida o eje de entrada.",
  "<b>Inercia de la salida</b> (kg·mm²; masa en kg para la cremallera o el carro) y, en el Planetario, la "
  "inercia de giro propio de cada planeta.")
H2("5.4 Contacto")
FIG("editor_contacto", "Figura 6. Contacto: formulación, rigidez, tolerancia y amortiguamiento.")
TAB([["Formulación", "Qué hace", "Cuándo usarla"],
     ["Penalización elástica unilateral", "F = k·δ (+ c·δ̇) si δ > 0; reparto por compatibilidad",
      "Recomendada; obligatoria para la integración temporal"],
     ["Equilibrio unilateral / complementariedad", "Contacto rígido F ≥ 0, g ≥ 0, F·g = 0",
      "Casos isostáticos; con varios contactos el reparto resulta Indeterminado"],
     ["Solo análisis geométrico", "Separaciones, normales y contactos sin fuerzas", "Inspección geométrica"]],
    [4.6, 6.6, 5.6])
L("<b>Rigidez normal equivalente</b> (N/mm por contacto): dato de entrada; con 0 no se asume valor.",
  "<b>Tolerancia de brecha</b> (mm): una separación menor se considera contacto.",
  "<b>Amortiguamiento normal</b> (N·s/mm): solo con penalización; actúa con velocidades relativas no nulas.",
  "La tabla «Componentes y restricciones» lista cada cuerpo, su vínculo y sus contactos activos.")
H2("5.5 Solucionador")
FIG("editor_solucionador", "Figura 7. Solucionador: método, paso de integración, tolerancias y diagnóstico.")
TAB([["Método", "Descripción"],
     ["Integración temporal (dinámica de contacto) — predeterminado",
      "La dinámica GOBIERNA el movimiento: la salida se mueve por las fuerzas de contacto; incluye inercias, "
      "deflexión, holgura y pérdida de sincronismo del motor. Paso automático (≤ 0,5 ms) o fijo; «instantes "
      "guardados» define la resolución de la animación."],
     ["Equilibrio cuasiestático por posición",
      "Fuerzas en cada muestra de la trayectoria prescrita (sin inercias). Muestreo uniforme, adaptativo o el "
      "de Ajustes, siempre con extremos e inversiones."]], [5.6, 11.2])
L("Tolerancias: equilibrio en N (traslaciones) y momento en N·mm (giros); máximo de iteraciones.",
  "«Estimar costo» mide tres muestras reales y extrapola (estimación); al terminar se informa la duración medida.",
  "Ejecutar / Cancelar: el cálculo corre en segundo plano; la ventana sigue respondiendo.")
H2("5.6 Resultados")
FIG("editor_par_t", "Figura 8. T(t): [Prescrita] discontinua, [Motor] punteada, [Calculada] continua.")
L("<b>T(t), T(θ), T(ω)</b>: carga prescrita, par motor calculado y, en capacidad, par disponible. T(θ) y T(ω) "
  "son curvas paramétricas (pueden ser multivaluadas).",
  "<b>Fuerzas</b>: historial de la fuerza normal por contacto; seleccione filas de la tabla para elegir rodillos.",
  "<b>Momentos</b>: par motor, carga, par transmitido y momento sobre cada componente.",
  "<b>Eventos</b>: pérdida/recuperación de contacto, cambio de conjunto activo, cambio de flanco, inversión de "
  "carga con holgura, pérdida de sincronismo, re-enganche e intervalos no viables con su causa.",
  "<b>Diagnóstico</b>: estado por muestra, residuo, iteraciones y aproximación elástica.",
  "La <b>línea naranja</b> es el cursor temporal: al moverla, la ventana de sistema muestra esa posición con las "
  "flechas de fuerza.",
  "«Exportar…»: CSV (serie temporal + <i>_contactos.csv</i> con punto, normal y fuerza de cada contacto) o JSON.")
FIG("editor_fuerzas", "Figura 9. Fuerzas normales por contacto y cursor de inspección.")

# ============================================================ 6
H1("6. Simulación gobernada por la dinámica")
P("Con la simulación por contacto activa, el régimen dinámico gobierna al cinemático:")
L("<b>Automático</b>: al pulsar Reproducir sin un estudio vigente, la aplicación calcula primero la dinámica (el estado "
  "muestra «Calculando») y reproduce al terminar. La posición de la entrada es la integrada (puede retrasarse "
  "si el motor satura) y la salida se dibuja en su posición real: cinemática + deflexión (amplificable).",
  "<b>Manual</b>: en cada posición del dial se resuelve el equilibrio cuasiestático con el escenario que muestra "
  "el editor (aunque no esté guardado); la velocidad estimada del dial alimenta las cargas T(ω).",
  "Las flechas magenta son las fuerzas normales sobre los rodillos; el HUD muestra el par motor, la fuerza "
  "máxima y el estado del motor.")
FIG("epi_contacto", "Figura 10. Animación gobernada por la dinámica: fuerzas, HUD y estado del estudio.")
FIG("planetario", "Figura 11. Planetario: contactos sol–planetas y anular–planetas.")

# ============================================================ 7
H1("7. Ajustes")
FIG("ajustes", "Figura 12. Ventana de Ajustes.", 14)
TAB([["Pestaña", "Opciones principales"],
     ["General", "Restaurar sesión, confirmar al salir, guardado automático, avisos, sobrescritura"],
     ["Cálculo y precisión", "Decimales mostrados (no redondea el cálculo), muestreo uniforme/adaptativo, "
                             "desviaciones lineal y angular, estimación de costo"],
     ["Simulación y rendimiento", "FPS, menos FPS en ventana inactiva, render Software/OpenGL, CPU/GPU/Híbrido, "
                                  "detener ante estado inválido, conservar pausa, caché de geometría y "
                                  "<b>simulación basada en contacto</b>"],
     ["Apariencia", "Presets de tema, colores de interfaz y técnicos, trazos, tipografías y antialias"],
     ["Exportación", "Formato y resolución de imagen; formato, resolución, FPS y calidad de video"]], [4.2, 12.6])
NOTA("Configuración recomendada para cualquier equipo: FPS automático (monitor), render <b>Software</b> (OpenGL "
     "solo si el controlador lo soporta), CPU — NumPy, muestreo adaptativo, caché de geometría activa. El render "
     "por software es estable en todos los equipos; OpenGL puede mejorar escenas muy cargadas.")

# ============================================================ 8
H1("8. Proyectos, sesión y exportaciones")
L("El proyecto (JSON) guarda parámetros, modos, perfil de movimiento, capas visibles y el estudio de contacto "
  "(escenarios y resultados). Los proyectos de versiones anteriores abren con «Sin estudio».",
  "La sesión de cada sistema se restaura al abrirlo (si está activo en Ajustes) y el autoguardado ofrece "
  "recuperar un cierre inesperado.",
  "Exportar geometría: XLSX (la primera hoja con X, Y, Z lista para CAD), CSV/TXT (nube de puntos), DXF R12 y "
  "PDF con el resumen y las gráficas. El Planetario genera un archivo por engranaje.",
  "Video MP4 (H.264) o WebM (VP9) desde el modo automático.")

# ============================================================ 9
H1("9. Ventanas de propiedades")
P("Desde «Propiedades físicas» se abren, sin cerrar la ventana principal, el perfil del diente con su tabla de "
  "coordenadas y las gráficas de ángulo de presión, radio de curvatura y camino de contacto con la tabla de "
  "rodillos activos. Todas las gráficas tienen cursor de inspección, menú contextual en español y exportación de "
  "imagen.")
FIG("trocoidal", "Figura 13. Ventana Trocoidal (cremallera).")

# ============================================================ 10
H1("10. Fundamentos técnicos")
H2("10.1 Geometría")
EQ("mrrp = rd / (2·sen(π/Zrp))      prrp = mrrp / cos(α<sub>mín</sub>)")
EQ("Epitrocoidal:  R₁ = prrp·Zg/Zrp,  cd = prrp + R₁")
EQ("x(θ) = (R₁+r)·sen θ − mrrp·sen(kθ),  y(θ) = (R₁+r)·cos θ − mrrp·cos(kθ),  k = (R₁+r)/r")
P("El perfil real del diente es la equidistante a distancia r (radio del rodillo) de la curva generatriz, que "
  "es la trayectoria del centro del rodillo relativa al engranaje. Hipotrocoidal y Trocoidal usan sus "
  "generatrices propias; el Planetario reutiliza ambas con Za = Zs + 2·Zrp y la relación de Willis "
  "Zs·φs + Za·φa = (Zs + Za)·φc.")
H2("10.2 Detección de contactos")
P("Para cada rodillo se busca el punto más cercano del flanco real (malla de 241 puntos y seis pasadas de "
  "refinamiento sobre la curva exacta) entre tres dientes candidatos. La separación con signo es "
  "g = s·|c − p| − r, con s = +1 si el centro está del lado libre; la normal n va del material del engranaje "
  "hacia el rodillo. En la cresta (esquina convexa entre dos flancos) el centro está fuera si queda del lado "
  "libre de cualquiera de los dos.")
H2("10.3 Equilibrio cuasiestático")
EQ("δ<sub>i</sub> = −g<sub>i</sub> + J<sub>i</sub>·q        F<sub>i</sub> = k·max(0, δ<sub>i</sub>)")
EQ("Σ F<sub>i</sub>·J<sub>i</sub> = Q    ⇔    mín E(q) = ½·k·Σ max(0, δ<sub>i</sub>)² − Q·q")
P("q son deflexiones elásticas pequeñas de las coordenadas de salida (y del giro de cada planeta) alrededor de "
  "la posición cinemática; J<sub>i</sub> = ∂δ<sub>i</sub>/∂q se obtiene de las velocidades de los cuerpos en "
  "el punto de contacto. La energía es convexa: se resuelve por conjunto activo con Newton y búsqueda lineal. "
  "La validación con trabajo virtual (T<sub>motor</sub>·dθ = T<sub>carga</sub>·d(salida)) se cumple con error "
  "~1e-8 en los cuatro mecanismos.")
H2("10.4 Dinámica de contacto (integración temporal)")
EQ("T = ½·I<sub>e</sub>·θ̇² + ½·Σ I<sub>c</sub>·(R<sub>c</sub>·θ̇ + q̇<sub>c</sub>)²")
EQ("M·ẍ + Gᵀ·F(x, ẋ) = Q<sub>ext</sub> + T<sub>m</sub>·e<sub>θ</sub>,   G = [−∂g/∂θ , J]")
EQ("F<sub>i</sub> = max(0, k·δ<sub>i</sub> + c·δ̇<sub>i</sub>) si δ<sub>i</sub> > 0")
P("R<sub>c</sub> es la tasa cinemática de cada coordenada. Se integra con Newmark implícito (γ = 0,6; "
  "β = 0,3025), incondicionalmente estable y con un amortiguamiento numérico leve, resolviendo cada paso con "
  "Newton. Las separaciones y jacobianos se precalculan en tablas de θ (un solo paso de rodillo cuando el "
  "mecanismo es periódico). Un cuerpo con inercia nula queda en equilibrio instantáneo; con todas las inercias "
  "nulas se reproduce el resultado cuasiestático.")
H2("10.5 Convenciones y unidades")
TAB([["Magnitud", "Convención / unidad"],
     ["Longitudes, separaciones", "mm"], ["Fuerzas", "N (sobre el rodillo = +Fn·n)"],
     ["Pares", "N·m en pantalla y exportación; N·mm internamente"], ["Momentos", "positivos antihorarios (+z)"],
     ["Par motor", "conjugado del ángulo θ del perfil (en Trocoidal el piñón gira −θ)"],
     ["Inercias", "kg·mm² (masa en kg para traslaciones)"],
     ["Carga", "positiva = resistente"], ["Fr, Ft", "radial y tangencial respecto al centro del engranaje"]],
    [5, 11.8])

# ============================================================ 11
H1("11. Flujo de trabajo recomendado")
L("1. Elija el sistema y ajuste los parámetros hasta obtener un perfil sin subcorte (Propiedades físicas → "
  "radio de curvatura).",
  "2. Pase a Automático, abra el editor y elija o edite el perfil de movimiento.",
  "3. Active la simulación por contacto en Ajustes.",
  "4. En «Régimen dinámico / contacto» elija el escenario, el motor, la carga y sus inercias.",
  "5. En Contacto, elija «Penalización elástica unilateral» e introduzca la rigidez normal de su par de "
  "materiales (dato propio; por ejemplo, estimada con contacto de Hertz lineal para el largo del rodillo).",
  "6. Use «Estimar costo» y ejecute. Revise Eventos y Diagnóstico antes de interpretar fuerzas.",
  "7. Reproduzca en la ventana de sistema (con amplificación de deformaciones si quiere ver la deflexión) y "
  "exporte CSV/JSON para análisis CAE o fatiga.")

# ============================================================ 12
H1("12. Solución de problemas")
TAB([["Síntoma", "Causa probable", "Qué hacer"],
     ["«No se pudo aplicar OpenGL»", "El controlador no entrega un contexto OpenGL (el motivo se indica)",
      "Actualice el driver de video o use render Software (recomendado)"],
     ["El estado dice «Indeterminado»", "Faltan datos: rigidez, curva del motor o carga fuera de su dominio",
      "Revise el mensaje en Diagnóstico y complete el dato indicado"],
     ["Reproducir muestra solo cinemática", "Estudio no ejecutable (p. ej. rigidez = 0 con integración temporal)",
      "Defina la rigidez en Contacto o desactive la simulación por contacto"],
     ["«La salida perdió el engrane»", "Ningún contacto retiene la carga (holgura o carga excesiva)",
      "Revise el signo y la magnitud de la carga y la geometría"],
     ["Pérdida de sincronismo", "Par requerido mayor que el disponible", "Motor de más par, perfil más suave o menos inercia"],
     ["Estudio lento", "Paso de integración muy pequeño o perfil largo",
      "Paso automático, menos instantes guardados o método cuasiestático"],
     ["No se ve la deflexión", "Las deflexiones elásticas son de micrómetros",
      "Menú de la vista → Indicadores → Amplificación ×100 o ×1000"]], [4.2, 6, 6.6])

# ============================================================ 13
H1("13. Limitaciones")
L("Contacto normal sin fricción; las leyes tangenciales quedan para una versión futura.",
  "Rigidez normal única por contacto (sin Hertz no lineal ni dependencia del radio de curvatura).",
  "Cuerpos rígidos salvo la deflexión de contacto; sin flexión de ejes ni de dientes.",
  "Accionamiento ideal: servo de posición limitado por la curva de par; no se simula el modelo eléctrico; acople "
  "directo (sin reductor intermedio).",
  "Geometría ideal: la holgura (backlash) calculada es nula mientras no se modelen tolerancias.",
  "En la cremallera, la tabla periódica no modela los extremos físicos de la cremallera.",
  "Sin ensayos en el banco: los resultados deben validarse experimentalmente.")

Path(SALIDA).parent.mkdir(parents=True, exist_ok=True)
doc = Doc(str(SALIDA))
doc.multiBuild(st)
print(SALIDA)
