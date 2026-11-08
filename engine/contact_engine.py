# -*- coding: utf-8 -*-
"""
engine/contact_engine.py

Caracteriza, evalúa y valida los contactos rodillo-diente activos en un
instante de la simulación.

REESTRUCTURACIÓN (Kenneth, 27 jul 2026): el caso ANGULAR (Epitrocoidal/
Hipotrocoidal) ya NO deriva "a qué diente pertenece" a partir de álgebra
sobre el parámetro θ de la curva -- se demostró (ver chat) que θ no tiene
relación aritmética simple con el índice de diente, porque `generar_patron_
angular` ensambla los Zg dientes ROTANDO copias idénticas de la forma base
(evaluada solo cerca de θ≈0), no reevaluando la curva en otro rango de θ.
El nuevo criterio usa la POSICIÓN GEOMÉTRICA real de cada rodillo:

  1) `_rodillos_k_activos`: candidatos = los Zrp rodillos cuyo CENTRO (real,
     cinemático) cae dentro de la banda radial [r_raiz, r_cresta] del
     diente -- reemplaza el viejo filtro angular por ventana de θ.
  2) `_dientes_j_activos`: para cada rodillo activo, φ = ángulo entre +X y
     la línea centro_rodillo-centro_engranaje (el engranaje SIEMPRE está
     centrado en el origen, con el diente 0 SIEMPRE centrado en +X); dividir
     φ entre el paso angular de diente da el índice de diente exacto, sin
     ninguna relación con θ.
  3) `_localizar_contacto`: con (rodillo, diente) ya identificados, se busca
     el punto del flanco REAL (curva_offset, ya rotada a la posición del
     diente) más cercano al centro candidato del rodillo (condición de
     no-penetración aplicada indirectamente, búsqueda discreta por argmin
     -- ver nota de Kenneth sobre una futura variante con splines).
  4) `_construir_contactos`: igual que antes (sin cambios).

MARCO DE REFERENCIA (¡importante, ver aviso al final del archivo!): el
nuevo criterio de φ solo es válido en el marco donde el diente 0 vive
exactamente en +X -- ese marco es el de generación del patrón CON la
rotación de vista (`ROTACION_VISTA_SIMULACION_GRADOS`, -90°) ya aplicada.
Antes, `punto_contacto`/`centro_rodillo` NO llevaban esa rotación (vivían
en el marco crudo, θ=0 en +Y) y era `widgets/opengl_widget.py` quien la
aplicaba después, en cada fotograma. Ahora esa rotación queda INCLUIDA
dentro de los puntos que devuelve este módulo -- opengl_widget.py ya NO
debe volver a aplicarla (ver aviso al final).

El caso LINEAL (Cremallera) NO cambia: no tiene "engranaje centrado en el
origen" del que medir φ, así que sigue con su propio pipeline (ya
validado, ver progress.md/chat del 27 jul 2026).

CIR (Centro Instantáneo de Rotación): delegado a
engine.cinematica_engine.calcular_cir() (cantidad cinemática, no de la
geometría de la curva).
"""
from __future__ import annotations
import numpy as np

from engine import math_utils as mu
from engine.system_context import ContextoSistema
from engine.cinematica_engine import calcular_cir


class ContactEngine:
    def __init__(self, motor_curva, contexto: ContextoSistema, rodillo):
        self.motor = motor_curva
        self.contexto = contexto
        self.rodillo = rodillo

    def calcular(self, theta_referencia_rad: float, theta_lim: float | None = None,
                modo_pinon_alterno: bool = False, estado_cinematico=None) -> list[dict]:
        """Punto de entrada único. `estado_cinematico` (engine.cinematica_
        engine.EstadoCinematico) es NUEVO y OBLIGATORIO para el caso
        angular (necesita angulo_pinon_rad/centro_pinon/angulo_patron_rad
        para ubicar los rodillos geométricamente, ver _candidatos_
        generacion) -- el caso lineal (Cremallera) sigue sin necesitarlo,
        usa theta_referencia_rad directo como antes."""
        theta_lim = theta_lim if theta_lim is not None else self.motor.theta_lim

        if self.contexto.tipo_ensamble == "lineal":
            return self._calcular_lineal(theta_referencia_rad, theta_lim, modo_pinon_alterno)
        return self._calcular_angular(theta_referencia_rad, theta_lim, modo_pinon_alterno,
                                      estado_cinematico)

    # ==================================================================
    # CASO LINEAL (Cremallera) -- SIN CAMBIOS, ya validado
    # ==================================================================
    def _calcular_lineal(self, theta_referencia_rad, theta_lim, modo_pinon_alterno):
        Zrp = self.contexto.numero_rodillos
        indices, theta_k = self._theta_k_candidatos(theta_referencia_rad, Zrp, modo_pinon_alterno)
        indices, indice_diente, theta_k = self._filtrar_por_theta_lim_lineal(
            indices, theta_k, theta_lim, theta_referencia_rad)
        if theta_k.size == 0:
            return []

        ox, oy = self.motor.curva_offset(theta_k)
        gx, gy = self.motor.curva_generatriz(theta_k)
        angulos = self.motor.angulo_presion(theta_k)

        mascara = self._mascara_banda_radial(gx, gy, ox, oy)
        if not np.any(mascara):
            return []
        indices, indice_diente, theta_k, ox, oy, gx, gy, angulos = (
            arr[mascara] for arr in (indices, indice_diente, theta_k, ox, oy, gx, gy, angulos)
        )

        ox_diente, oy_diente = self.motor._posicionar_en_diente(ox, oy, indice_diente)
        gx_diente, gy_diente = self.motor._posicionar_en_diente(gx, gy, indice_diente)
        cir_global = self._cir_global(theta_referencia_rad, modo_pinon_alterno)

        return self._construir_contactos(
            indices, indice_diente, theta_k, ox_diente, oy_diente,
            gx_diente, gy_diente, angulos, cir_global,
        )

    def _theta_k_candidatos(self, theta_referencia_rad: float, Zrp: int, modo_pinon_alterno: bool):
        """SOLO Cremallera ahora (el caso angular ya no pasa por aquí, ver
        _rodillos_k_activos). Ángulo local (envuelto a (-π,π]) de cada uno
        de los Zrp rodillos respecto a la trocoide base."""
        paso_angular_rodillo = self.contexto.paso_angular_rodillo
        indices = np.arange(Zrp)
        theta_crudo = theta_referencia_rad - indices * paso_angular_rodillo
        theta_k = (theta_crudo + np.pi) % (2.0 * np.pi) - np.pi
        return indices, theta_k

    def _filtrar_por_theta_lim_lineal(self, indices, theta_k, theta_lim, theta_ref):
        """SOLO Cremallera (ver docstring de contact_engine.py, chat del
        27 jul 2026, para la derivación completa: i_ref + desplazamiento
        centrado -- verificado contra la posición física real del piñón)."""
        activos = np.abs(theta_k) <= theta_lim
        indices = indices[activos]
        theta_k = theta_k[activos]
        paso_angular_rodillo = self.contexto.paso_angular_rodillo
        i_ref = int(np.round(theta_ref / paso_angular_rodillo))
        i_ref_mod = i_ref % self.contexto.numero_rodillos
        desplazamiento = indices - i_ref_mod
        desplazamiento_centrado = (
            (desplazamiento + self.contexto.numero_rodillos // 2)
            % self.contexto.numero_rodillos
        ) - self.contexto.numero_rodillos // 2
        indice_diente = i_ref + desplazamiento_centrado
        return indices, indice_diente, theta_k

    # ==================================================================
    # CASO ANGULAR (Epitrocoidal/Hipotrocoidal) -- NUEVO
    # ==================================================================
    def _calcular_angular(self, theta_referencia_rad, theta_lim, modo_pinon_alterno,
                          estado_cinematico):
        if estado_cinematico is None:
            raise ValueError(
                "ContactEngine._calcular_angular requiere estado_cinematico "
                "(engine.cinematica_engine.EstadoCinematico) -- ver system_window.py."
            )
        indices, cx_cand, cy_cand = self._rodillos_k_activos(estado_cinematico, modo_pinon_alterno)
        if indices.size == 0:
            return []

        indices, dientes_j, cx_cand, cy_cand = self._dientes_j_activos(indices, cx_cand, cy_cand)

        (ox_contacto, oy_contacto, gx_contacto, gy_contacto,
         theta_local, angulos, dientes_final) = self._localizar_contacto(
            indices, dientes_j, cx_cand, cy_cand)

        (indices, dientes_final, theta_local, ox_contacto, oy_contacto,
         gx_contacto, gy_contacto, angulos) = self._desempatar_diente_duplicado(
            indices, dientes_final, theta_local, ox_contacto, oy_contacto,
            gx_contacto, gy_contacto, angulos)

        cir_global = self._cir_global(theta_referencia_rad, modo_pinon_alterno)

        return self._construir_contactos(
            indices, dientes_final, theta_local, ox_contacto, oy_contacto,
            gx_contacto, gy_contacto, angulos, cir_global,
        )

    def _candidatos_generacion(self, estado_cinematico, modo_pinon_alterno):
        """Centro CANDIDATO (aproximado, círculo del piñón -- RollerPinionEngine,
        NO el trocoide exacto) de los Zrp rodillos, en el marco de
        GENERACIÓN del engranaje CON la rotación de vista ya incorporada
        -- el marco donde el diente 0 vive siempre en +X (ver docstring del
        módulo).

        CORRECCIÓN (Kenneth, ver captura "contactos dibujados abajo"): la
        rotación de vista (`rot_vista`, -90°) SOLO debe afectar al PATRÓN
        LOCAL de rodillos (offset respecto al centro del piñón) -- nunca a
        la TRASLACIÓN del centro del piñón (`centro_pinon`), que ya vive en
        coordenadas de MUNDO reales ("Fijo en X+" significa literalmente
        que el piñón queda anclado en +X del mundo, ver
        engine.cinematica_engine.resolver_estado). La versión anterior
        sumaba la traslación ANTES de rotar por rot_vista, así que el
        ancla física (cd, 0) terminaba rotada a (0, -cd) -- el piñón se
        veía bien en widgets/opengl_widget.py (que sí separa correctamente
        traslación de offset local, ver `_dibujar_pinon`), pero los
        contactos calculados aquí quedaban desplazados 90° (abajo en vez
        de a la derecha). Ahora se sigue EXACTAMENTE el mismo orden que ya
        usa `_dibujar_pinon`:
          1) offset local = Rotar(spin + rot_vista) · centro_local_sin_rotar.
          2) Si el ANILLO gira en vivo (Fijo): se deshace esa rotación
             (-angulo_patron_rad) -- aplicada por igual al offset local Y a
             la traslación del centro (una rotación se distribuye sobre una
             suma de vectores) -- para volver al marco de generación, donde
             el anillo NUNCA se mueve. En Orbitar el anillo no gira en vivo
             -- no hace falta deshacer nada, y el marco de generación YA
             coincide con el marco de mundo.
          3) offset local (ya con rot_vista+deshecho) + traslación del
             centro (con el mismo deshecho, SIN rot_vista)."""
        cx_local, cy_local = self.rodillo.centros_rodillos()
        rot_vista = np.radians(self.motor.ROTACION_VISTA_SIMULACION_GRADOS)
        angulo_offset = estado_cinematico.angulo_pinon_rad + rot_vista
        cos_s, sin_s = np.cos(angulo_offset), np.sin(angulo_offset)
        cx_offset = cx_local * cos_s - cy_local * sin_s
        cy_offset = cx_local * sin_s + cy_local * cos_s

        centro_x, centro_y = estado_cinematico.centro_pinon

        if not modo_pinon_alterno:
            cos_p = np.cos(-estado_cinematico.angulo_patron_rad)
            sin_p = np.sin(-estado_cinematico.angulo_patron_rad)
            cx_offset, cy_offset = (cx_offset * cos_p - cy_offset * sin_p,
                                     cx_offset * sin_p + cy_offset * cos_p)
            centro_x, centro_y = (centro_x * cos_p - centro_y * sin_p,
                                   centro_x * sin_p + centro_y * cos_p)

        return cx_offset + centro_x, cy_offset + centro_y

    def _rodillos_k_activos(self, estado_cinematico, modo_pinon_alterno):
        """PASO 1 (antes `_theta_k_candidatos`): candidatos = los rodillos
        cuyo centro cae dentro de la banda radial [r_raiz, r_cresta] del
        diente -- ya NO se usa ninguna ventana angular de θ para decidir
        quién es candidato."""
        cx, cy = self._candidatos_generacion(estado_cinematico, modo_pinon_alterno)
        r_raiz = self.motor.radio_circulo_centro_rodillo_raiz
        r_cresta = self.motor.radio_circulo_centro_rodillo_cresta
        r_min, r_max = min(r_raiz, r_cresta), max(r_raiz, r_cresta)
        EPS = 1e-6
        dist = np.hypot(cx, cy)
        activos = (dist >= r_min - EPS) & (dist <= r_max + EPS)
        indices = np.arange(self.contexto.numero_rodillos)[activos]
        return indices, cx[activos], cy[activos]

    def _dientes_j_activos(self, indices, cx_cand, cy_cand):
        """PASO 2 (antes `_mascara_banda_radial`): φ = ángulo entre +X y la
        línea centro_rodillo-centro_engranaje (origen). Como el engranaje
        SIEMPRE está centrado en el origen y el diente 0 SIEMPRE en +X
        (ver _candidatos_generacion), dividir φ entre el paso angular de
        diente da el índice exacto -- sin pasar por θ en ningún momento."""
        Zg = self.contexto.numero_dientes
        paso_diente = self.contexto.paso_angular_diente
        EPS_FRONTERA = 1e-9
        phi = np.arctan2(cy_cand, cx_cand)
        phi_wrapped = (phi + 2.0 * np.pi) % (2.0 * np.pi)
        dientes_j = np.floor((phi_wrapped + EPS_FRONTERA) / paso_diente).astype(int) % Zg
        return indices, dientes_j, cx_cand, cy_cand

    def _localizar_contacto(self, indices, dientes_j, cx_cand, cy_cand, n_muestras=61):
        """PASO 3: para cada rodillo activo, busca el punto del flanco REAL
        más cercano a su centro candidato -- condición de no-penetración
        aplicada indirectamente vía búsqueda discreta (argmin).

        CORRECCIÓN (Kenneth, 28 jul 2026): el diente que da `_dientes_j_
        activos` (vía φ, usando el centro APROXIMADO de RollerPinionEngine)
        es solo una SEMILLA -- confirmado numéricamente que, cerca de la
        frontera entre 2 dientes, el error de esa aproximación circular
        (no es el trocoide exacto) puede meter el candidato en el "cubo"
        angular equivocado (ej. asignado a diente 9 cuando su verdadera
        coincidencia más cercana está en diente 10 -- síntoma observado:
        2 rodillos distintos "reclamando" el mismo diente, uno de ellos
        con theta_local pegado al borde de theta_lim). Se busca también en
        los 2 dientes VECINOS (j-1, j+1) y se toma el mínimo GLOBAL de
        distancia entre los 3 -- la condición de no-penetración (menor
        distancia real) decide el diente final, no el bucket angular de φ.

        NOTA (Kenneth): variante con spline (scipy CubicSpline, con >=201
        puntos impares para el perfil) queda pendiente de evaluar costo
        por fotograma -- esta versión usa búsqueda discreta,
        n_muestras=60 por defecto en cada uno de los 3 dientes candidatos
        (180 puntos evaluados por rodillo activo)."""
        rot_vista = np.radians(self.motor.ROTACION_VISTA_SIMULACION_GRADOS)
        theta_muestras = np.linspace(-self.motor.theta_lim, self.motor.theta_lim, n_muestras)
        ox_base_cruda, oy_base_cruda = self.motor.curva_offset(theta_muestras)
        ox_base, oy_base = mu.rotar(ox_base_cruda, oy_base_cruda, rot_vista)

        Zg = self.contexto.numero_dientes
        paso_diente = self.contexto.paso_angular_diente
        n = len(indices)
        ox_contacto = np.empty(n)
        oy_contacto = np.empty(n)
        gx_contacto = np.empty(n)
        gy_contacto = np.empty(n)
        theta_local = np.empty(n)
        dientes_final = np.empty(n, dtype=int)
        radio_rodillo = self.rodillo.radio_rodillo

        for pos in range(n):
            j_semilla = int(dientes_j[pos])
            mejor_dist2 = None
            mejor_px = mejor_py = mejor_theta = mejor_j = None
            for delta in (-1, 0, 1):
                j = (j_semilla + delta) % Zg
                beta = j * paso_diente
                ox_j, oy_j = mu.rotar(ox_base, oy_base, beta)
                dist2 = (ox_j - cx_cand[pos]) ** 2 + (oy_j - cy_cand[pos]) ** 2
                i_min = int(np.argmin(dist2))
                if mejor_dist2 is None or dist2[i_min] < mejor_dist2:
                    mejor_dist2 = dist2[i_min]
                    mejor_px, mejor_py = ox_j[i_min], oy_j[i_min]
                    mejor_theta = theta_muestras[i_min]
                    mejor_j = j
                    mejor_arr, mejor_i = dist2, i_min

            # V2.1: refinamiento por ZOOM sobre la curva EXACTA. Sustituye al parabólico sobre d², que con la
            # malla de 61 muestras dejaba saltos de theta_local en la raíz (más visibles en Hipotrocoidal).
            # Cada pasada evalúa 21 puntos en ±1 paso y estrecha la ventana ÷10 (5 pasadas ~ 1e-8 rad).
            paso_malla = float(theta_muestras[1] - theta_muestras[0])
            lo = max(float(mejor_theta) - paso_malla, float(theta_muestras[0]))
            hi = min(float(mejor_theta) + paso_malla, float(theta_muestras[-1]))
            for _ in range(5):
                ts = np.linspace(lo, hi, 21)
                oxz, oyz = self.motor.curva_offset(ts)
                oxz, oyz = mu.rotar(oxz, oyz, rot_vista)
                oxz, oyz = mu.rotar(oxz, oyz, mejor_j * paso_diente)
                kz = int(np.argmin((oxz - cx_cand[pos]) ** 2 + (oyz - cy_cand[pos]) ** 2))
                mejor_px, mejor_py, mejor_theta = float(oxz[kz]), float(oyz[kz]), float(ts[kz])
                lo, hi = float(ts[max(kz - 1, 0)]), float(ts[min(kz + 1, 20)])

            ox_contacto[pos], oy_contacto[pos] = mejor_px, mejor_py
            theta_local[pos] = mejor_theta
            dientes_final[pos] = mejor_j

            dx, dy = cx_cand[pos] - mejor_px, cy_cand[pos] - mejor_py
            norma = np.hypot(dx, dy)
            if norma > 1e-15:
                gx_contacto[pos] = mejor_px + radio_rodillo * dx / norma
                gy_contacto[pos] = mejor_py + radio_rodillo * dy / norma
            else:
                gx_contacto[pos], gy_contacto[pos] = cx_cand[pos], cy_cand[pos]

        angulos = self.motor.angulo_presion(theta_local)
        return ox_contacto, oy_contacto, gx_contacto, gy_contacto, theta_local, angulos, dientes_final

    def _desempatar_diente_duplicado(self, indices, dientes_final, theta_local, ox_contacto,
                                     oy_contacto, gx_contacto, gy_contacto, angulos):
        """PASO 4 (Kenneth, 28 jul 2026): incluso con la búsqueda en los 3
        dientes vecinos (ver _localizar_contacto), cerca del borde de la
        banda radial o de theta_lim el candidato APROXIMADO de un rodillo
        puede seguir resolviendo al mismo diente que otro rodillo ya bien
        centrado (síntoma: 2 rodillos "reclamando" el mismo diente en el
        mismo frame). Ante un empate por diente, se descarta todo menos el
        contacto mejor centrado (|theta_local| mínimo) -- la condición de
        no-penetración real ya se aplicó en _localizar_contacto; esto solo
        resuelve la ambigüedad de asignación cuando 2 candidatos distintos
        convergen al mismo flanco."""
        mejor_posicion_por_diente = {}
        for pos in range(len(indices)):
            j = int(dientes_final[pos])
            actual = mejor_posicion_por_diente.get(j)
            if actual is None or abs(theta_local[pos]) < abs(theta_local[actual]):
                mejor_posicion_por_diente[j] = pos

        seleccion = np.array(sorted(mejor_posicion_por_diente.values()), dtype=int)
        return (indices[seleccion], dientes_final[seleccion], theta_local[seleccion],
                ox_contacto[seleccion], oy_contacto[seleccion],
                gx_contacto[seleccion], gy_contacto[seleccion], angulos[seleccion])

    # ==================================================================
    # Comunes a ambos casos
    # ==================================================================
    def _mascara_banda_radial(self, gx, gy, ox, oy):
        """SOLO Cremallera ahora (el caso angular resuelve su propia banda
        radial dentro de `_rodillos_k_activos`). Confirma que el centro
        del rodillo cae físicamente entre la raíz y la cresta del diente,
        y que dista exactamente radio_rodillo de su punto de contacto."""
        r_raiz = self.motor.radio_circulo_centro_rodillo_raiz
        r_cresta = self.motor.radio_circulo_centro_rodillo_cresta
        r_min, r_max = min(r_raiz, r_cresta), max(r_raiz, r_cresta)
        EPS = 1e-6

        dist_centro = np.hypot(gx, gy)
        en_banda = (dist_centro >= r_min - EPS) & (dist_centro <= r_max + EPS)

        dist_offset = np.hypot(gx - ox, gy - oy)
        offset_ok = np.isclose(dist_offset, self.rodillo.radio_rodillo, atol=1e-6)

        return en_banda & offset_ok

    def _cir_global(self, theta_referencia_rad: float, modo_pinon_alterno: bool):
        """CIR es GLOBAL (no se repite por diente). Delegado a
        engine.cinematica_engine.calcular_cir() -- pero ESE cálculo vive en
        el marco VIEJO (θ=0 en +Y, sin la rotación de vista). Desde la
        reestructuración del 27 jul 2026, `punto_contacto`/`centro_rodillo`
        (caso angular) SÍ incluyen esa rotación (-90°, ver
        _candidatos_generacion) -- si no rotamos el CIR IGUAL, la línea de
        acción apunta a un punto que no corresponde (bug reportado por
        Kenneth: "el CIR se dibuja donde no es"). Se aplica la MISMA
        rotación de vista aquí, solo para el caso angular (en Cremallera
        ROTACION_VISTA_SIMULACION_GRADOS=0, no cambia nada)."""
        cir = calcular_cir(self.contexto, theta_referencia_rad, modo_pinon_alterno)
        if cir is None or self.contexto.tipo_ensamble != "angular":
            return cir
        rot_vista = np.radians(self.motor.ROTACION_VISTA_SIMULACION_GRADOS)
        cos_v, sin_v = np.cos(rot_vista), np.sin(rot_vista)
        cx, cy = cir
        return cx * cos_v - cy * sin_v, cx * sin_v + cy * cos_v

    def _construir_contactos(self, indices, indice_diente, theta_k, ox_diente, oy_diente,
                             gx_diente, gy_diente, angulos, cir_global):
        """Arma la lista final de dicts de contacto (sin cambios de forma).

        RELABELING de `indice` en Cremallera: el rodillo `k` que usa
        `_theta_k_candidatos` numera los rodillos en sentido físico
        OPUESTO al que usa `RollerPinionEngine.centros_rodillos()` --
        verificado numéricamente que el rodillo físico correcto es
        `(Zrp - k) % Zrp`. NO aplica al caso angular: `_rodillos_k_activos`
        ya construye sus candidatos DIRECTAMENTE desde
        `RollerPinionEngine.centros_rodillos()`, así que `indices` ya está
        en la numeración física correcta -- aplicar el espejo otra vez
        sería un doble-error."""
        aplicar_espejo = self.contexto.tipo_ensamble == "lineal"
        Zrp = self.contexto.numero_rodillos
        contactos = []
        for i, k in enumerate(indices):
            k = int(k)
            indice_reportado = (Zrp - k) % Zrp if aplicar_espejo else k
            entrada = {
                "indice": indice_reportado,
                "indice_flanco": int(indice_diente[i]),
                "theta_local": float(theta_k[i]),
                "punto_contacto": (float(ox_diente[i]), float(oy_diente[i])),
                "centro_rodillo": (float(gx_diente[i]), float(gy_diente[i])),
                "angulo_presion_local_deg": float(angulos[i]),
            }
            if cir_global is not None:
                cx_g, cy_g = cir_global
                entrada["punto_cir"] = (float(cx_g), float(cy_g))
                entrada["vector_linea_accion"] = (
                    float(cx_g - ox_diente[i]),
                    float(cy_g - oy_diente[i]),
                )
            contactos.append(entrada)
        return contactos