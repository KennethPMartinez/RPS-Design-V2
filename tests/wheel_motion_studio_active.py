#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wheel Motion Studio.

Loads the Qt Designer form Perfildevelocidad_simulador_Window.ui from the same
folder. This build is a kinematic simulator/editor only. Physical hardware
commands are deliberately not implemented or enabled.

Dependencies: Python 3.10+, PySide6, pyqtgraph, NumPy
Install: python -m pip install PySide6 pyqtgraph numpy
Run:     python wheel_motion_studio_active.py
"""
from __future__ import annotations

import csv
import json
import logging
import math
import os
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import numpy as np

# Select PySide6 before importing pyqtgraph to prevent a Qt-binding conflict.
os.environ["PYQTGRAPH_QT_LIB"] = "PySide6"

from PySide6.QtCore import QFile, QIODevice, QObject, QPoint, QPointF, QRectF, Qt, QTimer, QEvent
from PySide6.QtGui import QAction, QColor, QPainter, QPen, QBrush
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog,
    QGraphicsItem, QGraphicsObject, QGraphicsScene, QInputDialog, QLabel, QMenu,
    QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QHBoxLayout, QWidget, QAbstractItemView, QHeaderView, QSpinBox, QDialog,
    QDialogButtonBox,
)
import pyqtgraph as pg

APP_NAME = "Wheel Motion Studio"
LOG = logging.getLogger("wheel_motion_studio")
UI_FILENAME = "Perfildevelocidad_simulador_Window.ui"

# UI names are Spanish; internal engine names stay stable for profiles/code.
LAW_TO_ENGINE = {
    "Rampa lineal": "Linear ramp",
    "Rampa cúbica": "Cubic ramp",
    "Cicloidal": "Cycloid",
    "Armónica": "Harmonic",
    "Sinusoidal": "Sine",
    "Sinusoidal modificada": "Modified sine",
    "Polinómica": "Polynomial",
    "Lista de puntos": "Point list",
    "Spline": "Spline",
    "Trapezoidal modificada": "Modified trapezoid",
}
ENGINE_TO_LAW = {v: k for k, v in LAW_TO_ENGINE.items()}
ENGINE_TO_LAW["Vibration envelope"] = "Oscilación con envolvente (preset)"
LAW_NAMES = list(LAW_TO_ENGINE)
CURVE_NAMES = ("Posición", "Velocidad", "Aceleración")
CURVE_UNITS = {"Posición": "°", "Velocidad": "°/s", "Aceleración": "°/s²"}


# ---------------------------------------------------------------------------
# Domain model. Profiles always describe angular position versus time.
# ---------------------------------------------------------------------------
@dataclass
class LawTerm:
    name: str
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "params": self.params}

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "LawTerm":
        name = str(data.get("name", "Cubic ramp"))
        # Accept old English names as well as current Spanish labels.
        if name in LAW_TO_ENGINE:
            name = LAW_TO_ENGINE[name]
        if name not in set(LAW_TO_ENGINE.values()) | {"Vibration envelope"}:
            raise ValueError(f"Ley no reconocida en el perfil: {name}")
        return LawTerm(name, dict(data.get("params", {})))


@dataclass
class Sector:
    start: float
    end: float
    y_start: float = 0.0
    y_end: float = 0.0
    terms: list[LawTerm] = field(default_factory=list)
    control_points: list[tuple[float, float]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not (math.isfinite(self.start) and math.isfinite(self.end)) or self.end <= self.start:
            raise ValueError("El final del tramo debe ser posterior al inicio.")

    @property
    def duration(self) -> float:
        return self.end - self.start

    def to_dict(self) -> dict[str, Any]:
        return {
            "start": self.start, "end": self.end,
            "y_start": self.y_start, "y_end": self.y_end,
            "terms": [term.to_dict() for term in self.terms],
            "control_points": [[x, y] for x, y in self.control_points],
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Sector":
        return Sector(
            start=float(data["start"]), end=float(data["end"]),
            y_start=float(data.get("y_start", 0.0)), y_end=float(data.get("y_end", 0.0)),
            terms=[LawTerm.from_dict(x) for x in data.get("terms", [])],
            control_points=[(float(p[0]), float(p[1])) for p in data.get("control_points", [])],
        )


@dataclass
class MotionProfile:
    sectors: list[Sector] = field(default_factory=list)
    sample_count: int = 4000
    name: str = "Perfil personalizado"

    def validate(self) -> None:
        if not self.sectors:
            raise ValueError("El perfil necesita al menos un tramo.")
        if not 200 <= int(self.sample_count) <= 1_000_000:
            raise ValueError("La resolución de muestreo debe estar entre 200 y 1 000 000.")
        ordered = sorted(self.sectors, key=lambda s: s.start)
        for sector in ordered:
            numbers = (sector.start, sector.end, sector.y_start, sector.y_end)
            if not all(math.isfinite(float(v)) for v in numbers):
                raise ValueError("Los tiempos y posiciones deben ser valores finitos.")
            if sector.end <= sector.start:
                raise ValueError("Todos los tramos deben tener duración positiva.")
            if sector.duration > 600.0:
                raise ValueError("La duración de un tramo no puede superar 600 s en esta versión.")
            for term in sector.terms:
                if term.name not in set(LAW_TO_ENGINE.values()) | {"Vibration envelope"}:
                    raise ValueError(f"Ley no registrada: {term.name}")
                self._validate_params(term.params)
            for x, y in sector.control_points:
                if not (math.isfinite(float(x)) and math.isfinite(float(y))):
                    raise ValueError("Los puntos de control deben ser finitos.")
            if sector.control_points:
                points = sorted(sector.control_points)
                if len(points) < 2:
                    raise ValueError("Se necesitan al menos dos puntos de control.")
                if any(points[i + 1][0] <= points[i][0] for i in range(len(points) - 1)):
                    raise ValueError("Los tiempos de los puntos deben ser estrictamente crecientes.")
                if points[0][0] < sector.start - 1e-9 or points[-1][0] > sector.end + 1e-9:
                    raise ValueError("Los puntos de control deben estar dentro de su tramo.")
        for left, right in zip(ordered, ordered[1:]):
            if right.start < left.end - 1e-9:
                raise ValueError("Los tramos no pueden solaparse.")

    @staticmethod
    def _validate_params(params: dict[str, Any]) -> None:
        for key, value in params.items():
            if value is None:
                continue
            if key == "coefficients":
                if not isinstance(value, (list, tuple)) or not all(math.isfinite(float(x)) for x in value):
                    raise ValueError("Los coeficientes polinómicos deben ser una lista de números finitos.")
                continue
            if isinstance(value, (int, float)) and not math.isfinite(float(value)):
                raise ValueError(f"El parámetro '{key}' no es finito.")
        if "frequency" in params and not (0 < float(params["frequency"]) <= 10_000.0):
            raise ValueError("La frecuencia debe estar entre 0 y 10 000 Hz en esta versión.")
        if "amplitude" in params and abs(float(params["amplitude"])) > 1e6:
            raise ValueError("La amplitud excede el límite numérico de la aplicación.")

    @property
    def start_time(self) -> float:
        return min((s.start for s in self.sectors), default=0.0)

    @property
    def end_time(self) -> float:
        return max((s.end for s in self.sectors), default=1.0)


# ---------------------------------------------------------------------------
# Independent law engines.
# ---------------------------------------------------------------------------
class MotionEngine:
    name = ""
    is_ramp = False
    is_point_based = False

    def default_params(self) -> dict[str, Any]:
        return {}

    def evaluate(self, t: np.ndarray, sector: Sector, term: LawTerm) -> np.ndarray:
        raise NotImplementedError


class RampEngine(MotionEngine):
    is_ramp = True

    def shape(self, u: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def evaluate(self, t: np.ndarray, sector: Sector, term: LawTerm) -> np.ndarray:
        u = np.clip((t - sector.start) / sector.duration, 0.0, 1.0)
        # Endpoint values define the displacement; the optional slope control
        # is applied by updating the endpoint, avoiding inconsistent curves.
        return (sector.y_end - sector.y_start) * self.shape(u)


class LinearRampEngine(RampEngine):
    name = "Linear ramp"

    def shape(self, u: np.ndarray) -> np.ndarray:
        return u


class CubicRampEngine(RampEngine):
    name = "Cubic ramp"

    def shape(self, u: np.ndarray) -> np.ndarray:
        return 3 * u**2 - 2 * u**3


class CycloidEngine(RampEngine):
    name = "Cycloid"

    def shape(self, u: np.ndarray) -> np.ndarray:
        return u - np.sin(2 * np.pi * u) / (2 * np.pi)


class HarmonicEngine(RampEngine):
    name = "Harmonic"

    def shape(self, u: np.ndarray) -> np.ndarray:
        return 0.5 * (1 - np.cos(np.pi * u))


class ModifiedSineEngine(RampEngine):
    name = "Modified sine"

    def shape(self, u: np.ndarray) -> np.ndarray:
        # Modified-sine cam-style displacement normalized to [0, 1].
        x = np.clip(u, 0.0, 1.0)
        den = 4.0 + np.pi
        result = np.empty_like(x, dtype=float)
        a = x <= 1.0 / 8.0
        b = (x > 1.0 / 8.0) & (x <= 7.0 / 8.0)
        c = x > 7.0 / 8.0
        result[a] = (np.pi / den) * x[a] - np.sin(4 * np.pi * x[a]) / (4 * den)
        result[b] = 2 / den + (np.pi / den) * x[b] - 9 * np.sin(
            np.pi / 3 + (4 * np.pi / 3) * x[b]
        ) / (4 * den)
        result[c] = 4 / den + (np.pi / den) * x[c] - np.sin(4 * np.pi * x[c]) / (4 * den)
        # Formula is already normalized at u=0 and u=1; normalization must not
        # depend on the subset of time samples requested by the evaluator.
        return result


class ModifiedTrapezoidEngine(RampEngine):
    name = "Modified trapezoid"

    @staticmethod
    def _left_half(x: np.ndarray) -> np.ndarray:
        out = np.empty_like(x, dtype=float)
        first = x <= 1.0 / 8.0
        second = (x > 1.0 / 8.0) & (x <= 3.0 / 8.0)
        third = x > 3.0 / 8.0
        den = 2.0 + np.pi
        out[first] = (2.0 / den) * x[first] - np.sin(4.0 * np.pi * x[first]) / (2.0 * np.pi * den)
        out[second] = (
            (np.pi**2 - 8.0) / (16.0 * np.pi * den)
            + ((2.0 - np.pi) / den) * x[second]
            + (4.0 * np.pi / den) * x[second] ** 2
        )
        out[third] = (
            -np.pi / (4.0 + 2.0 * np.pi)
            + ((2.0 + 2.0 * np.pi) / den) * x[third]
            - np.sin(4.0 * np.pi * x[third] - np.pi) / (2.0 * np.pi * den)
        )
        return out

    def shape(self, u: np.ndarray) -> np.ndarray:
        x = np.clip(u, 0.0, 1.0)
        left = x <= 0.5
        result = np.empty_like(x, dtype=float)
        result[left] = self._left_half(x[left])
        result[~left] = 1.0 - self._left_half(1.0 - x[~left])
        # This formula is pointwise; its output must not depend on the sampled
        # sub-interval passed to evaluate().
        return result


class SineEngine(MotionEngine):
    name = "Sine"

    def default_params(self) -> dict[str, Any]:
        return {"amplitude": 10.0, "frequency": 1.0, "phase": 0.0}

    def evaluate(self, t: np.ndarray, sector: Sector, term: LawTerm) -> np.ndarray:
        p = term.params
        amp = float(p.get("amplitude", 10.0))
        freq = float(p.get("frequency", 1.0))
        phase = math.radians(float(p.get("phase", 0.0)))
        local = np.asarray(t, dtype=float) - sector.start
        theta = 2 * np.pi * freq * local + phase
        # Shift the sinusoid to start at y_start and correct its end point to
        # y_end. The correction is zero for an integer number of cycles.
        start_sine = math.sin(phase)
        end_sine = math.sin(2 * np.pi * freq * sector.duration + phase)
        oscillation = amp * (np.sin(theta) - start_sine)
        correction = amp * (end_sine - start_sine) * (local / sector.duration)
        baseline = (sector.y_end - sector.y_start) * (local / sector.duration)
        return baseline + oscillation - correction


class PolynomialEngine(MotionEngine):
    name = "Polynomial"

    def default_params(self) -> dict[str, Any]:
        # Coefficients define the normalized displacement shape over u in [0, 1].
        return {"coefficients": [0.0, 0.0, 3.0, -2.0]}

    def evaluate(self, t: np.ndarray, sector: Sector, term: LawTerm) -> np.ndarray:
        coeff = np.asarray(term.params.get("coefficients", [0.0, 0.0, 3.0, -2.0]), dtype=float)
        u = np.clip((np.asarray(t, dtype=float) - sector.start) / sector.duration, 0.0, 1.0)
        raw = np.polynomial.polynomial.polyval(u, coeff)
        raw_start = float(np.polynomial.polynomial.polyval(0.0, coeff))
        raw_end = float(np.polynomial.polynomial.polyval(1.0, coeff))
        span = raw_end - raw_start
        if abs(span) <= 1e-12:
            if abs(sector.y_end - sector.y_start) <= 1e-12:
                return np.zeros_like(u)
            # Degenerate coefficients fall back to a finite, endpoint-preserving shape.
            shape = 3*u**2 - 2*u**3
        else:
            shape = (raw - raw_start) / span
        return (sector.y_end - sector.y_start) * shape


class PointListEngine(MotionEngine):
    name = "Point list"
    is_point_based = True

    def default_params(self) -> dict[str, Any]:
        return {"degree": 3}

    def evaluate(self, t: np.ndarray, sector: Sector, term: LawTerm) -> np.ndarray:
        points = sorted(sector.control_points)
        if len(points) < 2:
            return (sector.y_end - sector.y_start) * np.clip((t - sector.start) / sector.duration, 0, 1)
        x = np.asarray([(p[0] - sector.start) / sector.duration for p in points], dtype=float)
        y = np.asarray([p[1] - sector.y_start for p in points], dtype=float)
        unique, idx = np.unique(x, return_index=True)
        x, y = unique, y[idx]
        if len(x) < 2:
            return np.zeros_like(t, dtype=float)
        degree = int(np.clip(term.params.get("degree", 3), 1, min(8, len(x) - 1)))
        # Normalize time to [0, 1] before fitting to improve conditioning.
        coeff = np.polynomial.polynomial.polyfit(x, y, degree)
        local = np.clip((t - sector.start) / sector.duration, 0.0, 1.0)
        return np.polynomial.polynomial.polyval(local, coeff)


class SplineEngine(MotionEngine):
    name = "Spline"
    is_point_based = True

    def default_params(self) -> dict[str, Any]:
        return {"initial_slope": 0.0, "final_slope": 0.0}

    def evaluate(self, t: np.ndarray, sector: Sector, term: LawTerm) -> np.ndarray:
        points = sorted(sector.control_points or [(sector.start, sector.y_start), (sector.end, sector.y_end)])
        if len(points) < 2:
            return np.zeros_like(t)
        xs = np.asarray([p[0] for p in points], dtype=float)
        ys = np.asarray([p[1] - sector.y_start for p in points], dtype=float)
        if np.any(np.diff(xs) <= 0):
            raise ValueError("Los puntos spline deben tener tiempos crecientes.")
        slopes = np.empty_like(ys)
        slopes[1:-1] = (ys[2:] - ys[:-2]) / (xs[2:] - xs[:-2])
        slopes[0] = float(term.params.get("initial_slope", (ys[1] - ys[0]) / (xs[1] - xs[0])))
        slopes[-1] = float(term.params.get("final_slope", (ys[-1] - ys[-2]) / (xs[-1] - xs[-2])) )
        clipped = np.clip(t, xs[0], xs[-1])
        idx = np.searchsorted(xs, clipped, side="right") - 1
        idx = np.clip(idx, 0, len(xs) - 2)
        x0, x1 = xs[idx], xs[idx + 1]
        y0, y1 = ys[idx], ys[idx + 1]
        h = x1 - x0
        u = (clipped - x0) / h
        m0, m1 = slopes[idx], slopes[idx + 1]
        h00 = 2*u**3 - 3*u**2 + 1
        h10 = u**3 - 2*u**2 + u
        h01 = -2*u**3 + 3*u**2
        h11 = u**3 - u**2
        return h00*y0 + h10*h*m0 + h01*y1 + h11*h*m1


class VibrationEnvelopeEngine(MotionEngine):
    """Internal preset-only engine: sinusoid with smooth in/out amplitude envelope."""
    name = "Vibration envelope"

    def default_params(self) -> dict[str, Any]:
        return {"amplitude": 3.0, "frequency": 8.0, "rise_time": 1.0, "fall_time": 1.0}

    def evaluate(self, t: np.ndarray, sector: Sector, term: LawTerm) -> np.ndarray:
        p = term.params
        amp = float(p.get("amplitude", 3.0))
        freq = float(p.get("frequency", 8.0))
        rise = max(1e-6, float(p.get("rise_time", 1.0)))
        fall = max(1e-6, float(p.get("fall_time", 1.0)))
        local = t - sector.start
        u_in = np.clip(local / rise, 0.0, 1.0)
        u_out = np.clip((sector.end - t) / fall, 0.0, 1.0)
        smooth_in = 3*u_in**2 - 2*u_in**3
        smooth_out = 3*u_out**2 - 2*u_out**3
        envelope = np.minimum(smooth_in, smooth_out)
        baseline = (sector.y_end - sector.y_start) * (local / sector.duration)
        return baseline + amp * envelope * np.sin(2 * np.pi * freq * local)


class EngineRegistry:
    def __init__(self) -> None:
        engines: Iterable[MotionEngine] = (
            LinearRampEngine(), CubicRampEngine(), CycloidEngine(), HarmonicEngine(),
            SineEngine(), ModifiedSineEngine(), PolynomialEngine(), PointListEngine(),
            SplineEngine(), ModifiedTrapezoidEngine(), VibrationEnvelopeEngine(),
        )
        self.engines = {e.name: e for e in engines}

    def get(self, name: str) -> MotionEngine:
        if name not in self.engines:
            raise KeyError(f"No hay motor matemático registrado para '{name}'.")
        return self.engines[name]

    def new_term(self, display_name: str) -> LawTerm:
        internal = LAW_TO_ENGINE.get(display_name, display_name)
        engine = self.get(internal)
        params = engine.default_params()
        return LawTerm(internal, params)


# ---------------------------------------------------------------------------
# Evaluation, numerical derivatives and preflight validation.
# ---------------------------------------------------------------------------
class MotionEvaluator:
    def __init__(self, profile: MotionProfile, registry: EngineRegistry) -> None:
        self.profile, self.registry = profile, registry

    def _sector_value(self, t: np.ndarray, sector: Sector) -> np.ndarray:
        if not sector.terms:
            u = np.clip((t - sector.start) / sector.duration, 0.0, 1.0)
            return sector.y_start + (sector.y_end - sector.y_start) * u
        special = next((term for term in sector.terms if term.name in {"Spline", "Point list"}), None)
        if special is not None:
            return sector.y_start + self.registry.get(special.name).evaluate(t, sector, special)
        result = np.full_like(t, sector.y_start, dtype=float)
        for term in sector.terms:
            result += self.registry.get(term.name).evaluate(t, sector, term)
        return result

    def evaluate_position(self, times: np.ndarray) -> np.ndarray:
        times = np.asarray(times, dtype=float)
        if not self.profile.sectors:
            return np.zeros_like(times)
        sectors = sorted(self.profile.sectors, key=lambda s: s.start)
        result = np.empty_like(times)
        first, last = sectors[0], sectors[-1]
        first_val = float(self._sector_value(np.asarray([first.start]), first)[0])
        last_val = float(self._sector_value(np.asarray([last.end]), last)[0])
        result[times < first.start] = first_val
        result[times > last.end] = last_val
        assigned = (times < first.start) | (times > last.end)
        held_value = first_val
        for index, sector in enumerate(sectors):
            mask = (times >= sector.start) & (times <= sector.end)
            if np.any(mask):
                result[mask] = self._sector_value(times[mask], sector)
                assigned |= mask
            held_value = float(self._sector_value(np.asarray([sector.end]), sector)[0])
            if index + 1 < len(sectors):
                next_sector = sectors[index + 1]
                gap = (times > sector.end) & (times < next_sector.start)
                if np.any(gap):
                    result[gap] = held_value
                    assigned |= gap
        result[~assigned] = held_value
        return result

    @staticmethod
    def _differentiate(values: np.ndarray, times: np.ndarray) -> np.ndarray:
        if len(times) < 2:
            return np.zeros_like(values)
        return np.gradient(values, times, edge_order=2 if len(times) > 2 else 1)

    def sample_all(self) -> dict[str, np.ndarray]:
        start, end = self.profile.start_time, self.profile.end_time
        duration = max(end - start, 1e-6)
        max_freq = max((float(term.params.get("frequency", 0.0)) for s in self.profile.sectors for term in s.terms), default=0.0)
        required = int(math.ceil(duration * max(500.0, max_freq * 128.0)))
        count = min(1_000_000, max(2000, int(self.profile.sample_count), required))
        times = np.linspace(start, end, count)
        position = self.evaluate_position(times)
        velocity = self._differentiate(position, times)
        acceleration = self._differentiate(velocity, times)
        jerk = self._differentiate(acceleration, times)
        return {"time": times, "Posición": position, "Velocidad": velocity,
                "Aceleración": acceleration, "Jerk": jerk}

    def angle_at(self, time_value: float, samples: dict[str, np.ndarray]) -> float:
        return float(np.interp(time_value, samples["time"], samples["Posición"]))


@dataclass
class HardwareLimits:
    """Unknown values stay None; physical execution remains locked until configured."""
    max_position_abs_deg: float | None = None
    max_velocity_deg_s: float | None = None
    max_acceleration_deg_s2: float | None = None
    max_jerk_deg_s3: float | None = None
    max_frequency_hz: float | None = None


class MotionValidator:
    def validate_structure(self, profile: MotionProfile) -> list[str]:
        try:
            profile.validate()
        except Exception as exc:
            return [str(exc)]
        return []

    def metrics(self, samples: dict[str, np.ndarray], profile: MotionProfile | None = None) -> dict[str, float]:
        max_frequency = 0.0
        if profile is not None:
            max_frequency = max((float(t.params.get("frequency", 0.0)) for sec in profile.sectors for t in sec.terms), default=0.0)
        return {
            "posición máxima absoluta (°)": float(np.max(np.abs(samples["Posición"]))),
            "velocidad máxima (°/s)": float(np.max(np.abs(samples["Velocidad"]))),
            "aceleración máxima (°/s²)": float(np.max(np.abs(samples["Aceleración"]))),
            "jerk máximo (°/s³)": float(np.max(np.abs(samples["Jerk"]))),
            "frecuencia máxima configurada (Hz)": max_frequency,
        }

    def check_limits(self, metrics: dict[str, float], limits: HardwareLimits) -> list[str]:
        failures: list[str] = []
        mapping = (
            ("posición máxima absoluta (°)", limits.max_position_abs_deg, "posición angular"),
            ("velocidad máxima (°/s)", limits.max_velocity_deg_s, "velocidad angular"),
            ("aceleración máxima (°/s²)", limits.max_acceleration_deg_s2, "aceleración angular"),
            ("jerk máximo (°/s³)", limits.max_jerk_deg_s3, "jerk"),
            ("frecuencia máxima configurada (Hz)", limits.max_frequency_hz, "frecuencia"),
        )
        for key, limit, label in mapping:
            if key == "frecuencia máxima configurada (Hz)" and metrics[key] <= 0:
                continue
            if limit is None or not math.isfinite(limit) or limit <= 0:
                failures.append(f"Falta configurar un límite válido de {label}.")
            elif metrics[key] > limit:
                failures.append(f"{label.capitalize()} excede el límite configurado ({metrics[key]:.4g} > {limit:.4g}).")
        return failures

    def physical_readiness(self) -> tuple[bool, list[str]]:
        return False, [
            "El control físico no está implementado en esta versión.",
            "Falta identificar el modelo exacto del NEMA 17 y su driver.",
            "Faltan los límites verificados de la transmisión, la carga y el recorrido.",
            "La interfaz gráfica no sustituye un paro de emergencia ni las funciones de seguridad del equipo.",
        ]


# ---------------------------------------------------------------------------
# Presets: position-angle profiles. No hardware command is issued by presets.
# ---------------------------------------------------------------------------
class PresetFactory:
    NAMES = [
        "Arranque y parada suaves", "Oscilador 100 Hz", "Backlash", "Giro de 90°",
        "Giro de 180°", "Indexer", "Lavadora", "Vibrador",
    ]

    @staticmethod
    def _ramp(start: float, end: float, y0: float, y1: float, law: str = "Cycloid") -> Sector:
        return Sector(start, end, y0, y1, [LawTerm(law, {})])

    @classmethod
    def create(cls, name: str) -> MotionProfile:
        if name == "Arranque y parada suaves":
            return MotionProfile([cls._ramp(0.0, 8.0, 0.0, 360.0)], name=name)
        if name == "Oscilador 100 Hz":
            return MotionProfile([
                Sector(0.0, 2.0, 0.0, 0.0, [LawTerm("Sine", {"amplitude": 0.1, "frequency": 100.0, "phase": -90.0})])
            ], sample_count=4000, name=name)
        if name == "Backlash":
            return MotionProfile([
                cls._ramp(0.0, 2.0, 0.0, 30.0),
                Sector(2.0, 2.4, 30.0, 30.0, []),
                cls._ramp(2.4, 4.4, 30.0, 0.0),
            ], name=name)
        if name == "Giro de 90°":
            return MotionProfile([cls._ramp(0.0, 2.5, 0.0, 90.0)], name=name)
        if name == "Giro de 180°":
            return MotionProfile([cls._ramp(0.0, 3.0, 0.0, 180.0)], name=name)
        if name == "Indexer":
            return MotionProfile([
                cls._ramp(0.0, 1.0, 0.0, 90.0),
                Sector(1.0, 1.8, 90.0, 90.0, []),
                cls._ramp(1.8, 2.8, 90.0, 180.0),
                Sector(2.8, 3.6, 180.0, 180.0, []),
            ], name=name)
        if name == "Lavadora":
            return MotionProfile([
                Sector(0.0, 12.0, 0.0, 0.0, [LawTerm("Vibration envelope", {"amplitude": 20.0, "frequency": 0.5, "rise_time": 1.5, "fall_time": 1.5})]),
                cls._ramp(12.0, 18.0, 0.0, 720.0),
                cls._ramp(18.0, 21.0, 720.0, 0.0),
            ], name=name)
        if name == "Vibrador":
            return MotionProfile([
                Sector(0.0, 8.0, 0.0, 0.0, [LawTerm("Vibration envelope", {"amplitude": 3.0, "frequency": 8.0, "rise_time": 1.0, "fall_time": 1.0})])
            ], name=name)
        # Default custom profile is a valid, low-speed angular move.
        return MotionProfile([cls._ramp(0.0, 4.0, 0.0, 90.0)], name="Perfil personalizado")


class ProfileStore:
    @staticmethod
    def save_json(profile: MotionProfile, path: str | Path) -> None:
        profile.validate()
        payload = {
            "format": "Wheel Motion Studio", "version": 2,
            "quantity": "angular_position", "units": {"time": "s", "position": "deg"},
            "name": profile.name, "sample_count": profile.sample_count,
            "sectors": [s.to_dict() for s in profile.sectors],
        }
        Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def load_json(path: str | Path) -> MotionProfile:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        version = int(payload.get("version", 1))
        if version < 2 and payload.get("property_name", "Position") not in {"Position", "Posición", "angular_position"}:
            raise ValueError("Este perfil antiguo usa velocidad/aceleración como entrada. Revisa o convierte sus datos antes de abrirlo en el modelo de posición angular.")
        profile = MotionProfile(
            sectors=sorted((Sector.from_dict(x) for x in payload.get("sectors", [])), key=lambda s: s.start),
            sample_count=int(payload.get("sample_count", 4000)), name=str(payload.get("name", "Perfil personalizado")),
        )
        profile.validate()
        return profile

    @staticmethod
    def export_csv(samples: dict[str, np.ndarray], path: str | Path) -> None:
        with Path(path).open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["tiempo_s", "posicion_angular_deg", "velocidad_angular_deg_s", "aceleracion_angular_deg_s2", "jerk_deg_s3"])
            writer.writerows(zip(samples["time"], samples["Posición"], samples["Velocidad"], samples["Aceleración"], samples["Jerk"]))


# ---------------------------------------------------------------------------
# Wheel renderer for the QGraphicsView defined in Qt Designer.
# ---------------------------------------------------------------------------
class WheelGraphicsItem(QGraphicsObject):
    def __init__(self) -> None:
        super().__init__()
        self.setTransformOriginPoint(0.0, 0.0)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)

    def boundingRect(self) -> QRectF:
        return QRectF(-125.0, -125.0, 250.0, 250.0)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        del option, widget
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#283747"), 3))
        painter.setBrush(QBrush(QColor("#dce3eb")))
        painter.drawEllipse(-108, -108, 216, 216)
        painter.setBrush(QBrush(QColor("#eef2f6")))
        painter.drawEllipse(-78, -78, 156, 156)
        painter.setPen(QPen(QColor("#526779"), 5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        for i in range(8):
            painter.save()
            painter.rotate(i * 45)
            painter.drawLine(0, -15, 0, -82)
            painter.setPen(QPen(QColor("#526779"), 2))
            painter.setBrush(QBrush(QColor("#aab7c4")))
            painter.drawEllipse(-9, -75, 18, 18)
            painter.restore()
            painter.setPen(QPen(QColor("#526779"), 5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.setPen(QPen(QColor("#d35400"), 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(0, 0, 0, -92)
        painter.setPen(QPen(QColor("#ffffff"), 2))
        painter.setBrush(QBrush(QColor("#34495e")))
        painter.drawEllipse(-14, -14, 28, 28)


# ---------------------------------------------------------------------------
# Controller wired to the Qt Designer form.
# ---------------------------------------------------------------------------
class WheelMotionController(QObject):
    def __init__(self, ui_path: Path | None = None) -> None:
        resolved_ui_path = ui_path or Path(__file__).with_name(UI_FILENAME)
        if not resolved_ui_path.exists():
            raise FileNotFoundError(f"No se encontró el formulario Qt Designer: {resolved_ui_path}\nColoca {UI_FILENAME} junto a este archivo .py.")
        loader = QUiLoader()
        ui_file = QFile(str(resolved_ui_path))
        if not ui_file.open(QIODevice.OpenModeFlag.ReadOnly):
            raise OSError(f"No se pudo abrir el archivo UI: {resolved_ui_path}")
        loaded_window = loader.load(ui_file, None)
        ui_file.close()
        if loaded_window is None:
            raise RuntimeError(f"Qt Designer no pudo cargar el formulario: {loader.errorString()}")
        super().__init__(loaded_window)
        self.ui_path = resolved_ui_path
        self.window = loaded_window
        self.window.setWindowTitle(APP_NAME)

        self.registry = EngineRegistry()
        self.validator = MotionValidator()
        self.hardware_limits = HardwareLimits()  # intentionally unconfigured
        self.profile = PresetFactory.create("Arranque y parada suaves")
        self.samples: dict[str, np.ndarray] = {}
        self.selected_sector_index = 0
        self.selected_term_index = 0
        self.playing = False
        self.play_speed = 1.0
        self.play_time = self.profile.start_time
        self.last_tick_ms: int | None = None
        self.manual_edit = False
        self._drag_index: int | None = None
        self._drag_kind = ""
        self._drag_points: list[tuple[float, float]] = []
        self._loading_controls = False
        self._current_file: str | None = None
        self._wire_existing_widgets()
        self._build_graph()
        self._build_wheel()
        self._build_graph_toolbar()
        self._build_context_menu()
        self._build_menus()
        self._configure_controls()
        self._connect_signals()
        self._sync_sector_list(0)
        self._sync_term_list(0)
        self._refresh_all()
        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self._tick)
        self.window.statusBar().showMessage("Simulación cinemática · Control físico deshabilitado hasta validar el hardware.")

    def _find(self, cls, name: str):
        item = self.window.findChild(cls, name)
        if item is None:
            raise RuntimeError(f"El .ui no contiene el objeto requerido '{name}'.")
        return item

    def _wire_existing_widgets(self) -> None:
        # Preserve the user's object names from Qt Designer.
        n = {
            "preset": (QComboBox, "comboBox_preset"), "apply_preset": (QPushButton, "pushButton_Aplicar_preset"),
            "law_combo": (QComboBox, "comboBox_tipodefuncion"), "add_law": (QPushButton, "pushButton_ponerfuncion"),
            "remove_law": (QPushButton, "pushButton_quitarfuncion"), "replace_law": (QPushButton, "pushButton_reemplazarfuncion"),
            "term_list": (QListWidget, "listWidget_Ley"), "sector_list": (QListWidget, "listWidget_tramo"),
            "add_sector": (QPushButton, "pushButton_ponertramo"), "remove_sector": (QPushButton, "pushButton_quitartramo"),
            "t0": (QDoubleSpinBox, "doubleSpinBox_tiempoini"), "t1": (QDoubleSpinBox, "doubleSpinBox_tiempofin"),
            "y0": (QDoubleSpinBox, "doubleSpinBox_yini"), "y1": (QDoubleSpinBox, "doubleSpinBox_yfin"),
            "law_page": (QWidget, "stackedWidget"), "slope": (QDoubleSpinBox, "doubleSpinBox_pendientegen"),
            "amplitude": (QDoubleSpinBox, "doubleSpinBox_amplitud"), "frequency": (QDoubleSpinBox, "doubleSpinBox_frecuencia"),
            "phase": (QDoubleSpinBox, "doubleSpinBox_Fase"), "coeff_table": (QTableWidget, "tableWidget_coeficientes"),
            "coeff_add": (QPushButton, "pushButton_ponercoeficiente"), "coeff_remove": (QPushButton, "pushButton_quitarcoeficiente"),
            "degree": (QSpinBox, "spinBox_gradocurva"), "point_table": (QTableWidget, "tableWidget_listapuntos"),
            "point_add": (QPushButton, "pushButton_ponerpunto"), "point_remove": (QPushButton, "pushButton_quitarpunto"),
            "spline_table": (QTableWidget, "tableWidget_Listapuntosspline"), "spline_add": (QPushButton, "pushButton_ponerpuntospline"),
            "spline_remove": (QPushButton, "pushButton_quitarpuntospline"), "slope_start": (QDoubleSpinBox, "doubleSpinBox_pendienteini"),
            "slope_end": (QDoubleSpinBox, "doubleSpinBox_pendientefin"), "graph_host": (QWidget, "widget_grafica"),
            "wheel_view": (QWidget, "graphicsView_ruedamovil"), "show_position": (QCheckBox, "checkBox_Posicion"),
            "show_velocity": (QCheckBox, "checkBox_Velocidad"), "show_acceleration": (QCheckBox, "checkBox_Aceleracion"),
            "play": (QPushButton, "pushButton_reproducir"), "pause": (QPushButton, "pushButton_pausar"),
            "stop": (QPushButton, "pushButton_detener"), "rewind": (QPushButton, "pushButton_Reiniciar"),
            "speed": (QComboBox, "comboBox_4"), "time": (QDoubleSpinBox, "doubleSpinBox_5"),
            "progress": (QWidget, "progressBar"), "accept": (QPushButton, "pushButton_9"),
            "cancel": (QPushButton, "pushButton_10"),
        }
        for attr, (cls, name) in n.items():
            setattr(self, attr, self._find(cls, name))
        # Retire the input-property selector: position is the sole independent quantity.
        property_combo = self.window.findChild(QComboBox, "comboBox_Propiedadentrada")
        property_label = self.window.findChild(QLabel, "label_2")
        if property_combo:
            property_combo.hide()
        if property_label:
            property_label.hide()
        # Top-level buttons kept from the designer form are assigned useful actions.
        self.accept.setText("Validar perfil")
        self.cancel.setText("Cerrar")
        self.sector_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.term_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def _build_graph(self) -> None:
        layout = self.graph_host.layout()
        if layout is None:
            layout = QVBoxLayout(self.graph_host)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(3)
        self.plot = pg.PlotWidget(self.graph_host)
        self.plot.setBackground("#ffffff")
        self.plot.showGrid(x=True, y=True, alpha=0.25)
        self.plot.setLabel("bottom", "Tiempo", units="s", color="#1c4587")
        self.plot.setLabel("left", "Ángulo", units="°", color="#1c4587")
        self.plot.getAxis("left").setTextPen("#a61c1c")
        self.plot.getAxis("bottom").setTextPen("#1c4587")
        self.plot.addLegend(offset=(10, 10))
        self.curves = {
            "Posición": self.plot.plot([], [], pen=pg.mkPen("#c0392b", width=1.8), name="Posición (°)"),
            "Velocidad": self.plot.plot([], [], pen=pg.mkPen("#239b56", width=1.4), name="Velocidad (°/s)"),
            "Aceleración": self.plot.plot([], [], pen=pg.mkPen("#2468d7", width=1.3), name="Aceleración (°/s²)"),
        }
        self.playhead = pg.InfiniteLine(pos=0.0, angle=90, movable=False, pen=pg.mkPen("#5b5b5b", width=1, style=Qt.PenStyle.DashLine))
        self.plot.addItem(self.playhead)
        self.control_scatter = pg.ScatterPlotItem(size=11, symbol="o", pen=pg.mkPen("#173bff", width=1.4), brush=pg.mkBrush("#d6e4ff"))
        self.plot.addItem(self.control_scatter)
        layout.addWidget(self.plot, 1)
        self.plot.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.plot.customContextMenuRequested.connect(
            lambda pos: self.context_menu.exec(self.plot.mapToGlobal(pos))
        )
        self.plot.viewport().installEventFilter(self)
        self.graph_host.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.graph_host.customContextMenuRequested.connect(
            lambda pos: self.context_menu.exec(self.graph_host.mapToGlobal(pos))
        )

    def _build_wheel(self) -> None:
        self.wheel_scene = QGraphicsScene(self.window)
        self.wheel = WheelGraphicsItem()
        self.wheel_scene.addItem(self.wheel)
        self.wheel_scene.setSceneRect(-135, -135, 270, 270)
        self.wheel_view.setScene(self.wheel_scene)
        self.wheel_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.wheel_view.setBackgroundBrush(QBrush(QColor("#f6f8fb")))
        self.wheel_view.setSceneRect(self.wheel_scene.sceneRect())
        self.wheel_view.fitInView(self.wheel_scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def _build_graph_toolbar(self) -> None:
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)
        self.edit_manual_button = QPushButton("Editar manualmente")
        self.edit_manual_button.setCheckable(True)
        self.edit_manual_button.setToolTip("Activa el arrastre de puntos del tramo seleccionado.")
        self.view_all_button = QPushButton("Ver todo")
        self.graph_status = QLabel("Edición desactivada")
        self.graph_status.setStyleSheet("color: #555; padding-left: 6px;")
        toolbar.addWidget(self.edit_manual_button)
        toolbar.addWidget(self.view_all_button)
        toolbar.addStretch(1)
        toolbar.addWidget(self.graph_status)
        self.graph_host.layout().insertLayout(0, toolbar)

    def _build_context_menu(self) -> None:
        self.context_menu = QMenu(self.window)
        self.context_menu.addAction("View All", self._view_all)

        self.x_axis_menu = self.context_menu.addMenu("X Axis")
        self.x_axis_menu.addAction("Auto scale", lambda: self._axis_auto("x"))
        self.x_axis_menu.addAction("Set limits…", lambda: self._set_axis_limits("x"))
        self._add_scale_actions(self.x_axis_menu, "x")

        self.y_axis_menu = self.context_menu.addMenu("Y Axis")
        self.y_axis_menu.addAction("Auto scale", lambda: self._axis_auto("y"))
        self.y_axis_menu.addAction("Set limits…", lambda: self._set_axis_limits("y"))
        self._add_scale_actions(self.y_axis_menu, "y")

        self.mouse_mode_menu = self.context_menu.addMenu("Mouse Mode")
        self._action_pan = QAction("Pan", self.window)
        self._action_zoom = QAction("Zoom to region", self.window)
        self._action_pan.setCheckable(True)
        self._action_zoom.setCheckable(True)
        self._action_pan.setChecked(True)
        self._action_pan.triggered.connect(lambda: self._set_mouse_mode(False))
        self._action_zoom.triggered.connect(lambda: self._set_mouse_mode(True))
        self.mouse_mode_menu.addAction(self._action_pan)
        self.mouse_mode_menu.addAction(self._action_zoom)

        options = self.context_menu.addMenu("Plot Options")
        self._grid_action = QAction("Show grid", self.window)
        self._grid_action.setCheckable(True)
        self._grid_action.setChecked(True)
        self._grid_action.triggered.connect(self._toggle_grid)
        options.addAction(self._grid_action)
        for label, attr in (("Position", "show_position"), ("Velocity", "show_velocity"), ("Acceleration", "show_acceleration")):
            act = QAction(label, self.window)
            act.setCheckable(True)
            act.setChecked(getattr(self, attr).isChecked())
            act.triggered.connect(lambda checked, a=attr: getattr(self, a).setChecked(checked))
            options.addAction(act)

        export_menu = self.context_menu.addMenu("Export")
        export_menu.addAction("Export CSV…", self._export_csv)
        export_menu.addAction("Export plot image…", self._export_plot_image)

    def _add_scale_actions(self, menu: QMenu, axis: str) -> None:
        scale = menu.addMenu("Scale visible range")
        for factor in (0.5, 0.8, 1.25, 2.0):
            scale.addAction(f"× {factor:g}", lambda checked=False, f=factor, a=axis: self._scale_axis(a, f))

    def _build_menus(self) -> None:
        file_menu = self.window.findChild(QObject, "menuArchivo")
        help_menu = self.window.findChild(QObject, "menuAyuda")
        if file_menu is not None and hasattr(file_menu, "addAction"):
            file_menu.addAction("Abrir perfil…", self._open_profile)
            file_menu.addAction("Guardar perfil…", self._save_profile)
            file_menu.addAction("Exportar CSV…", self._export_csv)
            file_menu.addAction("Exportar gráfica…", self._export_plot_image)
            file_menu.addAction("Validar perfil…", self._validate_profile)
            file_menu.addAction("Configurar límites cinemáticos…", self._configure_limits)
            file_menu.addSeparator()
            file_menu.addAction("Salir", self.window.close)
        if help_menu is not None and hasattr(help_menu, "addAction"):
            help_menu.addAction("Acerca de…", self._about)

    def _configure_controls(self) -> None:
        self.preset.clear()
        self.preset.addItems(PresetFactory.NAMES)
        self.preset.setCurrentText(self.profile.name)
        self.law_combo.clear()
        self.law_combo.addItems(LAW_NAMES)
        self.speed.clear()
        for value in (0.25, 0.5, 1.0, 2.0, 4.0):
            self.speed.addItem(f"{value:g}×", value)
        self.speed.setCurrentIndex(2)
        self.time.setDecimals(3)
        self.time.setRange(0.0, 600.0)
        self.time.setSingleStep(0.01)
        self.time.setSuffix(" s")
        for spin in (self.t0, self.t1):
            spin.setDecimals(4); spin.setRange(-1e6, 1e6); spin.setSingleStep(0.1)
        for spin in (self.y0, self.y1):
            spin.setDecimals(5); spin.setRange(-1e6, 1e6); spin.setSingleStep(1.0)
        for spin in (self.slope, self.amplitude, self.frequency, self.phase, self.slope_start, self.slope_end):
            spin.setDecimals(5)
            spin.setRange(-1e6, 1e6)
        self.frequency.setRange(0.001, 10_000.0)
        self.degree.setRange(1, 8)
        for table in (self.coeff_table, self.point_table, self.spline_table):
            table.setAlternatingRowColors(True)
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.EditKeyPressed)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.coeff_table.setColumnCount(2)
        self.coeff_table.setHorizontalHeaderLabels(["Potencia", "Coeficiente"])
        self.point_table.setColumnCount(2)
        self.point_table.setHorizontalHeaderLabels(["Tiempo (s)", "Ángulo (°)"])
        self.spline_table.setColumnCount(2)
        self.spline_table.setHorizontalHeaderLabels(["Tiempo (s)", "Ángulo (°)"])
        self.show_position.setChecked(True)
        self.show_velocity.setChecked(False)
        self.show_acceleration.setChecked(False)
        # The existing Apply button is the only control that replaces a preset.
        self.progress.setRange(0, 1000)

    def _connect_signals(self) -> None:
        self.apply_preset.clicked.connect(self._apply_preset)
        self.preset.activated.connect(lambda _: self._preview_preset_name())
        self.sector_list.currentRowChanged.connect(self._sector_selected)
        self.term_list.currentRowChanged.connect(self._term_selected)
        self.add_sector.clicked.connect(self._add_sector)
        self.remove_sector.clicked.connect(self._remove_sector)
        self.add_law.clicked.connect(self._add_law)
        self.remove_law.clicked.connect(self._remove_law)
        self.replace_law.clicked.connect(self._replace_law)
        for widget in (self.t0, self.t1, self.y0, self.y1):
            widget.valueChanged.connect(self._bounds_changed)
        self.slope.valueChanged.connect(self._slope_changed)
        for widget in (self.amplitude, self.frequency, self.phase):
            widget.valueChanged.connect(self._sine_params_changed)
        self.degree.valueChanged.connect(self._point_params_changed)
        self.slope_start.valueChanged.connect(self._spline_params_changed)
        self.slope_end.valueChanged.connect(self._spline_params_changed)
        self.coeff_add.clicked.connect(lambda: self._add_table_row(self.coeff_table, ["", "0"]))
        self.coeff_remove.clicked.connect(lambda: self._remove_table_row(self.coeff_table, minimum=1))
        self.point_add.clicked.connect(lambda: self._add_control_point("point"))
        self.point_remove.clicked.connect(lambda: self._remove_control_point("point"))
        self.spline_add.clicked.connect(lambda: self._add_control_point("spline"))
        self.spline_remove.clicked.connect(lambda: self._remove_control_point("spline"))
        self.coeff_table.cellChanged.connect(self._coefficients_changed)
        self.point_table.cellChanged.connect(lambda *_: self._control_table_changed("point"))
        self.spline_table.cellChanged.connect(lambda *_: self._control_table_changed("spline"))
        self.show_position.toggled.connect(self._refresh_graph)
        self.show_velocity.toggled.connect(self._refresh_graph)
        self.show_acceleration.toggled.connect(self._refresh_graph)
        self.play.clicked.connect(self._play)
        self.pause.clicked.connect(self._pause)
        self.stop.clicked.connect(self._stop)
        self.rewind.clicked.connect(self._rewind)
        self.speed.currentIndexChanged.connect(self._speed_changed)
        self.time.valueChanged.connect(self._seek)
        self.edit_manual_button.toggled.connect(self._toggle_manual_edit)
        self.view_all_button.clicked.connect(self._view_all)
        self.accept.clicked.connect(self._validate_profile)
        self.cancel.clicked.connect(self.window.close)

    # ---- Current model selectors -------------------------------------------------
    def _selected_sector(self) -> Sector | None:
        if not self.profile.sectors:
            return None
        self.selected_sector_index = max(0, min(self.selected_sector_index, len(self.profile.sectors) - 1))
        return self.profile.sectors[self.selected_sector_index]

    def _selected_term(self) -> LawTerm | None:
        sector = self._selected_sector()
        if sector is None or not sector.terms:
            return None
        self.selected_term_index = max(0, min(self.selected_term_index, len(sector.terms) - 1))
        return sector.terms[self.selected_term_index]

    def _sync_sector_list(self, select: int | None = None) -> None:
        old = self.selected_sector_index if select is None else select
        self.sector_list.blockSignals(True)
        self.sector_list.clear()
        for i, sector in enumerate(self.profile.sectors):
            self.sector_list.addItem(f"Tramo {i + 1}: {sector.start:.3f}–{sector.end:.3f} s · {sector.y_start:.3f}→{sector.y_end:.3f}°")
        if self.profile.sectors:
            old = max(0, min(old, len(self.profile.sectors) - 1))
            self.sector_list.setCurrentRow(old)
        self.sector_list.blockSignals(False)
        self.selected_sector_index = old
        self._load_bounds()

    def _sync_term_list(self, select: int | None = None) -> None:
        sector = self._selected_sector()
        old = self.selected_term_index if select is None else select
        self.term_list.blockSignals(True)
        self.term_list.clear()
        if sector:
            for term in sector.terms:
                self.term_list.addItem(ENGINE_TO_LAW.get(term.name, term.name))
        if sector and sector.terms:
            old = max(0, min(old, len(sector.terms) - 1))
            self.term_list.setCurrentRow(old)
        else:
            old = 0
        self.term_list.blockSignals(False)
        self.selected_term_index = old
        self._sync_parameter_page()
        self._update_edit_handles()

    def _load_bounds(self) -> None:
        sector = self._selected_sector()
        if sector is None:
            return
        self._loading_controls = True
        try:
            for widget, value in ((self.t0, sector.start), (self.t1, sector.end), (self.y0, sector.y_start), (self.y1, sector.y_end)):
                widget.blockSignals(True); widget.setValue(float(value)); widget.blockSignals(False)
        finally:
            self._loading_controls = False

    def _sector_selected(self, row: int) -> None:
        if row < 0 or row >= len(self.profile.sectors):
            return
        self.selected_sector_index = row
        self.selected_term_index = 0
        self._load_bounds()
        self._sync_term_list(0)
        self._refresh_all()

    def _term_selected(self, row: int) -> None:
        sector = self._selected_sector()
        if sector is None or row < 0 or row >= len(sector.terms):
            return
        self.selected_term_index = row
        self._sync_parameter_page()
        self._update_edit_handles()

    def _law_for_term(self, term: LawTerm | None) -> str:
        return ENGINE_TO_LAW.get(term.name, "Rampa cúbica") if term else "Rampa cúbica"

    def _sync_parameter_page(self) -> None:
        sector, term = self._selected_sector(), self._selected_term()
        if sector is None or term is None:
            self.law_page.setCurrentIndex(0)
            return
        display = self._law_for_term(term)
        if term.name == "Vibration envelope":
            self.law_page.setCurrentIndex(1)
            self.law_combo.setCurrentText("Sinusoidal")
            self.law_combo.setEnabled(False)
            p = term.params
            for widget, key, default in ((self.amplitude, "amplitude", 3.0), (self.frequency, "frequency", 8.0)):
                widget.blockSignals(True); widget.setValue(float(p.get(key, default))); widget.blockSignals(False)
            self.phase.blockSignals(True); self.phase.setValue(0.0); self.phase.blockSignals(False)
            return
        self.law_combo.setEnabled(True)
        ix = {"Sinusoidal": 1, "Polinómica": 2, "Lista de puntos": 3, "Spline": 4}.get(display, 0)
        self.law_page.setCurrentIndex(ix)
        self.law_combo.blockSignals(True); self.law_combo.setCurrentText(display); self.law_combo.blockSignals(False)
        if ix == 0:
            slope = (sector.y_end - sector.y_start) / max(sector.duration, 1e-9)
            self.slope.blockSignals(True); self.slope.setValue(slope); self.slope.blockSignals(False)
        elif ix == 1:
            p = term.params
            for widget, key, default in ((self.amplitude, "amplitude", 10.0), (self.frequency, "frequency", 1.0), (self.phase, "phase", 0.0)):
                widget.blockSignals(True); widget.setValue(float(p.get(key, default))); widget.blockSignals(False)
        elif ix == 2:
            self._fill_coeff_table(term.params.get("coefficients", [0.0, 0.0, 3.0, -2.0]))
        elif ix == 3:
            self.degree.blockSignals(True); self.degree.setValue(int(term.params.get("degree", 3))); self.degree.blockSignals(False)
            self._ensure_point_defaults(sector)
            self._fill_points_table(self.point_table, sector.control_points)
        elif ix == 4:
            self._ensure_point_defaults(sector)
            self._fill_points_table(self.spline_table, sector.control_points)
            self.slope_start.blockSignals(True); self.slope_start.setValue(float(term.params.get("initial_slope", 0.0))); self.slope_start.blockSignals(False)
            self.slope_end.blockSignals(True); self.slope_end.setValue(float(term.params.get("final_slope", 0.0))); self.slope_end.blockSignals(False)

    def _ensure_point_defaults(self, sector: Sector) -> None:
        if not sector.control_points or len(sector.control_points) < 2:
            sector.control_points = [(sector.start, sector.y_start), (sector.end, sector.y_end)]
        else:
            points = sorted(sector.control_points)
            points[0] = (sector.start, points[0][1])
            points[-1] = (sector.end, points[-1][1])
            sector.control_points = points

    @staticmethod
    def _fill_points_table(table: QTableWidget, points: list[tuple[float, float]]) -> None:
        table.blockSignals(True)
        table.setRowCount(len(points))
        for row, (x, y) in enumerate(points):
            for col, value in enumerate((x, y)):
                item = QTableWidgetItem(f"{value:.8g}")
                if col == 0 and row in (0, len(points) - 1):
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(row, col, item)
        table.blockSignals(False)

    def _fill_coeff_table(self, coefficients: list[float]) -> None:
        values = list(coefficients) or [0.0, 0.0, 3.0, -2.0]
        self.coeff_table.blockSignals(True)
        self.coeff_table.setRowCount(len(values))
        for i, value in enumerate(values):
            idx = QTableWidgetItem(str(i)); idx.setFlags(idx.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.coeff_table.setItem(i, 0, idx)
            self.coeff_table.setItem(i, 1, QTableWidgetItem(f"{float(value):.8g}"))
        self.coeff_table.blockSignals(False)

    # ---- Model edits -------------------------------------------------------------
    def _bounds_changed(self, *_: Any) -> None:
        if self._loading_controls:
            return
        sector = self._selected_sector()
        if sector is None:
            return
        start, end = self.t0.value(), self.t1.value()
        if end <= start:
            self.window.statusBar().showMessage("El tiempo final debe ser mayor que el inicial.", 4000)
            self._load_bounds(); return
        others = [s for i, s in enumerate(self.profile.sectors) if i != self.selected_sector_index]
        for other in others:
            if start < other.end - 1e-9 and end > other.start + 1e-9:
                self.window.statusBar().showMessage("El tramo no puede solaparse con otro.", 4000)
                self._load_bounds(); return
        sector.start, sector.end = start, end
        sector.y_start, sector.y_end = self.y0.value(), self.y1.value()
        if sector.control_points:
            points = sorted(sector.control_points)
            points[0] = (start, points[0][1]); points[-1] = (end, points[-1][1])
            sector.control_points = points
        self._sync_sector_list(self.selected_sector_index)
        self._refresh_all()
        self._sync_parameter_page()

    def _slope_changed(self, value: float) -> None:
        term, sector = self._selected_term(), self._selected_sector()
        if term is None or sector is None or term.name not in {"Linear ramp", "Cubic ramp", "Cycloid", "Harmonic", "Modified sine", "Modified trapezoid"}:
            return
        self._loading_controls = True
        try:
            sector.y_end = sector.y_start + value * sector.duration
            self.y1.blockSignals(True); self.y1.setValue(sector.y_end); self.y1.blockSignals(False)
        finally:
            self._loading_controls = False
        self._sync_sector_list(self.selected_sector_index)
        self._refresh_all()

    def _sine_params_changed(self, *_: Any) -> None:
        term = self._selected_term()
        if term is None or term.name not in {"Sine", "Vibration envelope"}:
            return
        term.params.update({"amplitude": self.amplitude.value(), "frequency": self.frequency.value()})
        if term.name == "Sine":
            term.params["phase"] = self.phase.value()
        self._refresh_all()

    def _spline_params_changed(self, *_: Any) -> None:
        term = self._selected_term()
        if term is None or term.name != "Spline":
            return
        term.params.update({"initial_slope": self.slope_start.value(), "final_slope": self.slope_end.value()})
        self._refresh_all()

    def _point_params_changed(self, *_: Any) -> None:
        term = self._selected_term()
        if term is not None and term.name == "Point list":
            term.params["degree"] = self.degree.value()
            self._refresh_all()

    def _coefficients_changed(self, *_: Any) -> None:
        term = self._selected_term()
        if term is None or term.name != "Polynomial" or self._loading_controls:
            return
        try:
            coeff = [float(self.coeff_table.item(i, 1).text()) for i in range(self.coeff_table.rowCount())]
            if not all(math.isfinite(x) for x in coeff):
                raise ValueError("Los coeficientes deben ser finitos.")
            term.params["coefficients"] = coeff
            self._refresh_all()
        except (ValueError, AttributeError) as exc:
            self.window.statusBar().showMessage(f"Coeficientes no válidos: {exc}", 4000)

    def _control_table_changed(self, kind: str) -> None:
        sector, term = self._selected_sector(), self._selected_term()
        if sector is None or term is None or self._loading_controls:
            return
        if (kind == "point" and term.name != "Point list") or (kind == "spline" and term.name != "Spline"):
            return
        table = self.point_table if kind == "point" else self.spline_table
        try:
            points = [(float(table.item(i, 0).text()), float(table.item(i, 1).text())) for i in range(table.rowCount())]
            points = sorted(points)
            if len(points) < 2 or any(points[i + 1][0] <= points[i][0] for i in range(len(points) - 1)):
                raise ValueError("Los tiempos deben ser estrictamente crecientes.")
            if points[0][0] < sector.start or points[-1][0] > sector.end:
                raise ValueError("Los puntos deben permanecer dentro del tramo.")
            sector.control_points = points
            sector.y_start = points[0][1]
            sector.y_end = points[-1][1]
            self._fill_points_table(table, points)
            self._load_bounds()
            self._sync_sector_list(self.selected_sector_index)
            self._refresh_all()
        except (ValueError, AttributeError) as exc:
            self.window.statusBar().showMessage(f"Lista de puntos no válida: {exc}", 4000)

    def _add_table_row(self, table: QTableWidget, values: list[str]) -> None:
        row = table.rowCount(); table.insertRow(row)
        for col, value in enumerate(values):
            table.setItem(row, col, QTableWidgetItem(value))
        if table is self.coeff_table:
            idx = QTableWidgetItem(str(row)); idx.setFlags(idx.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 0, idx)
        self._coefficients_changed()

    def _remove_table_row(self, table: QTableWidget, minimum: int = 1) -> None:
        row = table.currentRow()
        if row < 0:
            row = table.rowCount() - 1
        if table.rowCount() > minimum and row >= 0:
            table.removeRow(row)
            for i in range(table.rowCount()):
                item = table.item(i, 0)
                if table is self.coeff_table and item:
                    item.setText(str(i))
            self._coefficients_changed()

    def _add_control_point(self, kind: str) -> None:
        sector, term = self._selected_sector(), self._selected_term()
        expected = "Point list" if kind == "point" else "Spline"
        if sector is None or term is None or term.name != expected:
            QMessageBox.information(self.window, "Puntos", f"Selecciona primero la ley {ENGINE_TO_LAW[expected]}.")
            return
        self._ensure_point_defaults(sector)
        points = sorted(sector.control_points)
        if len(points) < 2:
            points = [(sector.start, sector.y_start), (sector.end, sector.y_end)]
        left, right = points[-2], points[-1]
        points.insert(len(points) - 1, ((left[0] + right[0]) / 2, (left[1] + right[1]) / 2))
        sector.control_points = points
        self._sync_parameter_page(); self._refresh_all()

    def _remove_control_point(self, kind: str) -> None:
        sector, term = self._selected_sector(), self._selected_term()
        expected = "Point list" if kind == "point" else "Spline"
        table = self.point_table if kind == "point" else self.spline_table
        if sector is None or term is None or term.name != expected:
            return
        row = table.currentRow()
        if len(sector.control_points) <= 2 or row <= 0 or row >= len(sector.control_points) - 1:
            QMessageBox.information(self.window, "Puntos", "Se conservan los puntos inicial y final del tramo; selecciona un punto interior para quitarlo.")
            return
        sector.control_points.pop(row)
        self._sync_parameter_page(); self._refresh_all()

    def _add_law(self) -> None:
        sector = self._selected_sector()
        if sector is None:
            return
        display = self.law_combo.currentText()
        term = self.registry.new_term(display)
        if term.name in {"Point list", "Spline"}:
            sector.control_points = [(sector.start, sector.y_start), (sector.end, sector.y_end)]
        sector.terms.append(term)
        self.selected_term_index = len(sector.terms) - 1
        self._sync_term_list(self.selected_term_index); self._refresh_all()

    def _replace_law(self) -> None:
        sector = self._selected_sector()
        if sector is None:
            return
        display = self.law_combo.currentText()
        term = self.registry.new_term(display)
        sector.terms = [term]
        self.selected_term_index = 0
        if term.name in {"Point list", "Spline"}:
            sector.control_points = [(sector.start, sector.y_start), (sector.end, sector.y_end)]
        else:
            sector.control_points = []
        self._sync_term_list(0); self._refresh_all()

    def _remove_law(self) -> None:
        sector = self._selected_sector()
        if sector is None or not sector.terms:
            return
        row = self.term_list.currentRow()
        if row < 0:
            row = self.selected_term_index
        if 0 <= row < len(sector.terms):
            sector.terms.pop(row)
        self.selected_term_index = max(0, row - 1)
        self._sync_term_list(self.selected_term_index); self._refresh_all()

    def _add_sector(self) -> None:
        self._stop()
        previous = sorted(self.profile.sectors, key=lambda s: s.end)[-1]
        start = previous.end
        y = previous.y_end
        sector = Sector(start, start + 1.0, y, y + 30.0, [LawTerm("Cycloid", {})])
        # Keep the new segment contiguous and outside existing intervals.
        self.profile.sectors.append(sector)
        self.profile.sectors.sort(key=lambda s: s.start)
        self.profile.name = "Perfil personalizado"
        self.selected_sector_index = self.profile.sectors.index(sector)
        self.selected_term_index = 0
        self._sync_sector_list(self.selected_sector_index); self._sync_term_list(0); self._refresh_all()

    def _remove_sector(self) -> None:
        if len(self.profile.sectors) <= 1:
            QMessageBox.information(self.window, "Tramos", "El perfil debe conservar al menos un tramo.")
            return
        self._stop()
        self.profile.sectors.pop(self.selected_sector_index)
        self.selected_sector_index = max(0, self.selected_sector_index - 1)
        self.profile.name = "Perfil personalizado"
        self._sync_sector_list(self.selected_sector_index); self._sync_term_list(0); self._refresh_all()

    # ---- Preset/load, plot and animation ----------------------------------------
    def _preview_preset_name(self) -> None:
        self.window.statusBar().showMessage(f"Preset seleccionado: {self.preset.currentText()} (pulsa Aplicar para cargarlo).", 3000)

    def _apply_preset(self) -> None:
        name = self.preset.currentText()
        self._stop()
        self.profile = PresetFactory.create(name)
        self.selected_sector_index = self.selected_term_index = 0
        self.profile.name = name
        self._sync_sector_list(0); self._sync_term_list(0); self._refresh_all()
        self.window.statusBar().showMessage(f"Preset aplicado: {name}. Solo simulación; no envía comandos a hardware.", 5000)

    def _refresh_all(self) -> None:
        errors = self.validator.validate_structure(self.profile)
        if errors:
            self.window.statusBar().showMessage("Perfil inválido: " + " · ".join(errors), 7000)
            return
        try:
            self.samples = MotionEvaluator(self.profile, self.registry).sample_all()
            for name in ("Posición", "Velocidad", "Aceleración"):
                if not np.all(np.isfinite(self.samples[name])):
                    raise FloatingPointError(f"La curva de {name.lower()} contiene NaN o infinito.")
            self._refresh_graph()
            self._update_playback_range()
            self._seek(min(max(self.play_time, self.profile.start_time), self.profile.end_time))
            self._update_edit_handles()
        except Exception as exc:
            self.window.statusBar().showMessage(f"No se puede evaluar el perfil: {exc}", 7000)
            LOG.exception("No se pudo evaluar el perfil")

    def _refresh_graph(self, *_: Any) -> None:
        if not self.samples:
            return
        visible = {
            "Posición": self.show_position.isChecked(),
            "Velocidad": self.show_velocity.isChecked(),
            "Aceleración": self.show_acceleration.isChecked(),
        }
        for name, curve in self.curves.items():
            curve.setData(self.samples["time"], self.samples[name])
            curve.setVisible(visible[name])
        self._update_edit_handles()

    def _update_edit_handles(self) -> None:
        sector = self._selected_sector()
        if sector is None or not self.manual_edit:
            self.control_scatter.setData([], [])
            return
        term = self._selected_term()
        if term and term.name in {"Point list", "Spline"}:
            self._ensure_point_defaults(sector)
            points = sorted(sector.control_points)
        else:
            evaluator = MotionEvaluator(self.profile, self.registry)
            points = [
                (sector.start, float(evaluator.evaluate_position(np.asarray([sector.start]))[0])),
                (sector.end, float(evaluator.evaluate_position(np.asarray([sector.end]))[0])),
            ]
        self._drag_points = [(float(x), float(y)) for x, y in points]
        self.control_scatter.setData(x=[p[0] for p in points], y=[p[1] for p in points])

    def _toggle_manual_edit(self, enabled: bool) -> None:
        self.manual_edit = bool(enabled)
        self.edit_manual_button.setText("Terminar edición" if enabled else "Editar manualmente")
        self.graph_status.setText("Arrastra puntos azules para editar" if enabled else "Edición desactivada")
        self._update_edit_handles()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.plot.viewport() and self.manual_edit:
            et = event.type()
            if et == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                pos = event.position().toPoint()
                view_pos = self.plot.getPlotItem().vb.mapSceneToView(self.plot.mapToScene(pos))
                nearest = self._nearest_handle(pos)
                if nearest is not None:
                    self._drag_index = nearest
                    self._drag_kind = "point"
                    return True
            elif et == QEvent.Type.MouseMove and self._drag_index is not None and (event.buttons() & Qt.MouseButton.LeftButton):
                pos = event.position().toPoint()
                view_pos = self.plot.getPlotItem().vb.mapSceneToView(self.plot.mapToScene(pos))
                self._drag_handle(float(view_pos.x()), float(view_pos.y()))
                return True
            elif et == QEvent.Type.MouseButtonRelease and self._drag_index is not None:
                self._drag_index = None
                self._drag_kind = ""
                self._update_edit_handles()
                self._validate_after_edit()
                return True
        return super().eventFilter(watched, event)

    def _nearest_handle(self, mouse_pos: QPoint) -> int | None:
        if not self._drag_points:
            return None
        distances = []
        for x, y in self._drag_points:
            scene_pos = self.plot.getPlotItem().vb.mapViewToScene(QPointF(x, y))
            pixel = self.plot.mapFromScene(scene_pos)
            distances.append(math.hypot(pixel.x() - mouse_pos.x(), pixel.y() - mouse_pos.y()))
        idx = int(np.argmin(distances))
        return idx if distances[idx] <= 18 else None

    def _drag_handle(self, x: float, y: float) -> None:
        sector, term = self._selected_sector(), self._selected_term()
        i = self._drag_index
        if sector is None or i is None or not self._drag_points:
            return
        if term and term.name in {"Point list", "Spline"}:
            self._ensure_point_defaults(sector)
            pts = sorted(sector.control_points)
            if i == 0:
                x = sector.start
            elif i == len(pts) - 1:
                x = sector.end
            else:
                x = min(max(x, pts[i - 1][0] + 1e-5), pts[i + 1][0] - 1e-5)
            pts[i] = (x, y)
            sector.control_points = pts
            if i == 0:
                sector.y_start = y
            elif i == len(pts) - 1:
                sector.y_end = y
            self._load_bounds()
            table = self.point_table if term.name == "Point list" else self.spline_table
            self._fill_points_table(table, pts)
        else:
            # Analytic laws retain their form: endpoint drags alter sector bounds.
            pts = self._drag_points
            endpoint = 0 if i == 0 else len(pts) - 1
            if endpoint == 0:
                new_start = min(x, sector.end - 1e-4)
                prev = self.profile.sectors[self.selected_sector_index - 1] if self.selected_sector_index > 0 else None
                if prev is None or new_start >= prev.end - 1e-9:
                    sector.start, sector.y_start = new_start, y
            else:
                new_end = max(x, sector.start + 1e-4)
                nxt = self.profile.sectors[self.selected_sector_index + 1] if self.selected_sector_index + 1 < len(self.profile.sectors) else None
                if nxt is None or new_end <= nxt.start + 1e-9:
                    sector.end, sector.y_end = new_end, y
        self._load_bounds()
        self._sync_sector_list(self.selected_sector_index)
        self._refresh_all()

    def _validate_after_edit(self) -> None:
        errors = self.validator.validate_structure(self.profile)
        if errors:
            self.window.statusBar().showMessage("Edición rechazada: " + " · ".join(errors), 5000)
        else:
            self.window.statusBar().showMessage("Perfil recalculado. La edición no autoriza ejecución física.", 4000)

    def _update_playback_range(self) -> None:
        self.time.blockSignals(True)
        self.time.setRange(self.profile.start_time, self.profile.end_time)
        self.time.setValue(min(max(self.time.value(), self.profile.start_time), self.profile.end_time))
        self.time.blockSignals(False)

    def _play(self) -> None:
        if self.playing:
            return
        if self.play_time >= self.profile.end_time - 1e-9:
            self.play_time = self.profile.start_time
        self.playing = True
        self.last_tick_ms = None
        self.timer.start()
        self.window.statusBar().showMessage("Reproduciendo simulación (no se transmiten comandos al motor).")

    def _pause(self) -> None:
        self.playing = False
        if hasattr(self, "timer"):
            self.timer.stop()
        self.last_tick_ms = None
        self.window.statusBar().showMessage("Simulación en pausa.", 3000)

    def _stop(self) -> None:
        self.playing = False
        if hasattr(self, "timer"):
            self.timer.stop()
        self.last_tick_ms = None
        if hasattr(self, "time"):
            self._seek(self.profile.start_time)

    def _rewind(self) -> None:
        self._stop()
        self.window.statusBar().showMessage("Reproducción reiniciada.", 2500)

    def _speed_changed(self, index: int) -> None:
        value = self.speed.itemData(index)
        if value is not None:
            self.play_speed = float(value)

    def _tick(self) -> None:
        from time import perf_counter
        now = perf_counter()
        if self.last_tick_ms is None:
            self.last_tick_ms = now
            return
        dt = min(now - self.last_tick_ms, 0.1) * self.play_speed
        self.last_tick_ms = now
        self.play_time = min(self.play_time + dt, self.profile.end_time)
        self._seek(self.play_time)
        if self.profile.end_time - self.play_time <= 1e-9:
            self._pause()

    def _seek(self, value: float) -> None:
        if not self.samples:
            return
        self.play_time = float(np.clip(value, self.profile.start_time, self.profile.end_time))
        angle = MotionEvaluator(self.profile, self.registry).angle_at(self.play_time, self.samples)
        self.wheel.setRotation(angle)
        self.playhead.setValue(self.play_time)
        self.time.blockSignals(True); self.time.setValue(self.play_time); self.time.blockSignals(False)
        duration = max(self.profile.end_time - self.profile.start_time, 1e-9)
        self.progress.setValue(int(1000 * (self.play_time - self.profile.start_time) / duration))
        self.window.statusBar().showMessage(f"t = {self.play_time:.3f} s · θ = {angle:.3f}° · Solo simulación.", 2500)

    # ---- Context menu / axes / export -------------------------------------------
    def _view_all(self) -> None:
        self.plot.getPlotItem().autoRange()

    def _axis_auto(self, axis: str) -> None:
        self.plot.getPlotItem().enableAutoRange(axis=axis, enable=True)
        self.plot.getPlotItem().autoRange()

    def _set_axis_limits(self, axis: str) -> None:
        vb = self.plot.getPlotItem().vb
        if axis == "x":
            current = vb.viewRange()[0]
            label = "Tiempo mínimo y máximo (s)"
        else:
            current = vb.viewRange()[1]
            label = "Valor mínimo y máximo"
        low, ok1 = QInputDialog.getDouble(self.window, "Límites del eje", f"{label} · mínimo", float(current[0]), -1e9, 1e9, 5)
        if not ok1:
            return
        high, ok2 = QInputDialog.getDouble(self.window, "Límites del eje", f"{label} · máximo", float(current[1]), -1e9, 1e9, 5)
        if not ok2:
            return
        if high <= low:
            QMessageBox.warning(self.window, "Límites del eje", "El máximo debe ser mayor que el mínimo.")
            return
        if axis == "x":
            vb.setXRange(low, high, padding=0)
        else:
            vb.setYRange(low, high, padding=0)
        self.plot.getPlotItem().disableAutoRange(axis=axis)

    def _scale_axis(self, axis: str, factor: float) -> None:
        vb = self.plot.getPlotItem().vb
        limits = vb.viewRange()[0 if axis == "x" else 1]
        center = (limits[0] + limits[1]) / 2
        half = (limits[1] - limits[0]) * factor / 2
        if half <= 0 or not math.isfinite(half):
            return
        if axis == "x":
            vb.setXRange(center - half, center + half, padding=0)
        else:
            vb.setYRange(center - half, center + half, padding=0)
        self.plot.getPlotItem().disableAutoRange(axis=axis)

    def _set_mouse_mode(self, zoom_to_region: bool) -> None:
        view = self.plot.getPlotItem().vb
        view.setMouseMode(pg.ViewBox.RectMode if zoom_to_region else pg.ViewBox.PanMode)
        self._action_zoom.setChecked(zoom_to_region)
        self._action_pan.setChecked(not zoom_to_region)

    def _toggle_grid(self, enabled: bool) -> None:
        self.plot.showGrid(x=enabled, y=enabled, alpha=0.25 if enabled else 0.0)

    def _export_csv(self) -> None:
        if not self.samples:
            QMessageBox.warning(self.window, "Exportar CSV", "No hay datos calculados para exportar.")
            return
        path, _ = QFileDialog.getSaveFileName(self.window, "Exportar datos", "motion_data.csv", "CSV (*.csv)")
        if path:
            try:
                ProfileStore.export_csv(self.samples, path)
                self.window.statusBar().showMessage(f"CSV exportado: {path}", 4000)
            except Exception as exc:
                QMessageBox.critical(self.window, "Exportar CSV", str(exc))

    def _export_plot_image(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self.window, "Exportar gráfica", "motion_plot.png", "PNG (*.png);;JPEG (*.jpg *.jpeg)")
        if path:
            if not Path(path).suffix:
                path += ".png"
            if not self.plot.grab().save(path):
                QMessageBox.warning(self.window, "Exportar gráfica", "No se pudo guardar la imagen.")

    # ---- Validation / persistence -----------------------------------------------
    def _configure_limits(self) -> None:
        dialog = QDialog(self.window)
        dialog.setWindowTitle("Límites cinemáticos de referencia")
        form = QFormLayout(dialog)
        dialog.setMinimumWidth(430)
        specs = [
            ("max_position_abs_deg", "Posición angular absoluta máxima (°)"),
            ("max_velocity_deg_s", "Velocidad angular máxima (°/s)"),
            ("max_acceleration_deg_s2", "Aceleración angular máxima (°/s²)"),
            ("max_jerk_deg_s3", "Jerk máximo (°/s³)"),
            ("max_frequency_hz", "Frecuencia máxima (Hz)"),
        ]
        controls = {}
        for key, label in specs:
            spin = QDoubleSpinBox(dialog)
            spin.setDecimals(4)
            spin.setRange(0.0, 1e9)
            spin.setSingleStep(1.0)
            current = getattr(self.hardware_limits, key)
            spin.setValue(float(current) if current is not None else 0.0)
            spin.setToolTip("Usa 0 para indicar que este límite aún no está configurado.")
            form.addRow(label, spin)
            controls[key] = spin
        note = QLabel("Introduce únicamente valores respaldados por datos verificados del motor, driver, transmisión y carga. Estos límites son una ayuda de validación; no certifican seguridad.", dialog)
        note.setWordWrap(True)
        form.addRow(note)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, parent=dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = {key: (float(spin.value()) if spin.value() > 0 else None) for key, spin in controls.items()}
            self.hardware_limits = HardwareLimits(**values)
            self.window.statusBar().showMessage("Límites de referencia actualizados. El control físico sigue bloqueado.", 5000)

    def _validate_profile(self) -> None:
        errors = self.validator.validate_structure(self.profile)
        if errors:
            QMessageBox.critical(self.window, "Perfil inválido", "\n".join(errors))
            return
        try:
            samples = MotionEvaluator(self.profile, self.registry).sample_all()
            if not all(np.all(np.isfinite(samples[key])) for key in ("Posición", "Velocidad", "Aceleración", "Jerk")):
                raise FloatingPointError("Se generaron valores no finitos.")
            metrics = self.validator.metrics(samples, self.profile)
        except Exception as exc:
            QMessageBox.critical(self.window, "Validación", f"No se pudo evaluar el perfil:\n{exc}")
            return
        limit_results = self.validator.check_limits(metrics, self.hardware_limits)
        if any("excede el límite" in x for x in limit_results):
            limit_status = "RESULTADO DE LÍMITES: FUERA DE LÍMITES. No usar este perfil en hardware."
        elif limit_results:
            limit_status = "RESULTADO DE LÍMITES: INCOMPLETO. Configura todos los límites verificados."
        else:
            limit_status = "RESULTADO DE LÍMITES: dentro de los valores numéricos introducidos; esto no certifica seguridad."
        _, physical_reasons = self.validator.physical_readiness()
        lines = [f"{key}: {value:.6g}" for key, value in metrics.items()]
        lines += ["", "ESTADO DEL PERFIL: evaluación matemática completada.", limit_status]
        if limit_results:
            lines += ["", "Detalles de límites:", *[f"• {x}" for x in limit_results]]
        lines += ["", "EJECUCIÓN FÍSICA: BLOQUEADA.", *[f"• {x}" for x in physical_reasons]]
        QMessageBox.information(self.window, "Informe de validación", "\n".join(lines))

    def _save_profile(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self.window, "Guardar perfil", self._current_file or "motion_profile.json", "Perfiles JSON (*.json)")
        if not path:
            return
        try:
            ProfileStore.save_json(self.profile, path)
            self._current_file = path
            self.window.statusBar().showMessage(f"Perfil guardado: {path}", 4000)
        except Exception as exc:
            QMessageBox.critical(self.window, "Guardar perfil", str(exc))

    def _open_profile(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self.window, "Abrir perfil", "", "Perfiles JSON (*.json)")
        if not path:
            return
        try:
            profile = ProfileStore.load_json(path)
            self._stop()
            self.profile = profile
            self.selected_sector_index = self.selected_term_index = 0
            self.preset.setCurrentText(profile.name if profile.name in PresetFactory.NAMES else PresetFactory.NAMES[0])
            self._sync_sector_list(0); self._sync_term_list(0); self._refresh_all()
            self._current_file = path
            self.window.statusBar().showMessage(f"Perfil abierto: {path}", 4000)
        except Exception as exc:
            LOG.exception("No se pudo abrir el perfil")
            QMessageBox.critical(self.window, "Abrir perfil", f"No se pudo abrir el perfil:\n{exc}")

    def _about(self) -> None:
        QMessageBox.about(self.window, APP_NAME,
            "Editor de perfiles de posición angular para una rueda.\n\n"
            "Incluye leyes cinemáticas, ocho presets, edición interactiva, ejes configurables, JSON y CSV.\n\n"
            "Esta versión solo simula. No controla hardware ni garantiza seguridad de máquina.")

    def show(self) -> None:
        self.window.showMaximized()
        QApplication.processEvents()
        self.wheel_view.fitInView(self.wheel_scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
def configure_logging() -> None:
    logging.basicConfig(
        filename="wheel_motion_studio.log", level=logging.WARNING,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s", encoding="utf-8",
    )


def main() -> int:
    configure_logging()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")
    ui_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
    controller = WheelMotionController(ui_path)
    # Keep an explicit reference for the entire event loop.
    controller.show()
    return app.exec()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise
