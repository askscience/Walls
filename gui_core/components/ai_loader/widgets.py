from PySide6.QtCore import QTimer, QPointF, Qt
from PySide6.QtGui import QPainter, QBrush, QColor, QConicalGradient, QPainterPath
from PySide6.QtWidgets import QWidget
import math
import random


class AiLoader(QWidget):
    """Animated AI loader composed of 3 thin wavy circles on a transparent background.

    Modes:
    - active: faster motion
    - stop: slower, calmer motion

    Sizes: small, medium, big. Control animation via start()/stop() or setAnimated().
    """

    # Shared animation driver to reduce CPU usage across multiple instances
    _instances = set()
    _shared_timer = None
    _shared_fps = 60
    _shared_time = 0.0

    SIZE_MAP = {
        "small": 48,
        "medium": 80,
        "big": 120,
    }

    def __init__(self, size: str = "medium", animated: bool = True, parent=None):
        super().__init__(parent)
        self._size_key = size if size in self.SIZE_MAP else "medium"
        self._diameter = self.SIZE_MAP[self._size_key]
        self.setFixedSize(self._diameter, self._diameter)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Instance animation state
        self._time = 0.0
        self._animated = False
        self._is_active = True

        # Visual properties (kept for API compatibility, not heavily used now)
        self._core_color = QColor(235, 180, 255)
        self._glow_color = QColor(120, 90, 255)

        # Pre-calculated animation values for per-instance variation
        self._pulse_offset = random.uniform(0, 2 * math.pi)
        self._noise_seed = random.randint(0, 1000)

        # Three thin wavy rings: radius (relative), width (relative), alpha, wave amp factor,
        # wave frequency, rotation speed (deg/s), initial phase (rad), highlight spread
        self._arc_specs = [
            {"r": 0.65, "w": 0.050, "alpha": 220, "amp": 0.55, "freq": 6.0, "speed": 38.0, "phase": random.uniform(0.0, 2*math.pi), "spread": 0.06},
            {"r": 0.80, "w": 0.045, "alpha": 200, "amp": 0.50, "freq": 7.0, "speed": 28.0, "phase": random.uniform(0.0, 2*math.pi), "spread": 0.06},
            {"r": 0.95, "w": 0.040, "alpha": 180, "amp": 0.45, "freq": 8.0, "speed": 20.0, "phase": random.uniform(0.0, 2*math.pi), "spread": 0.06},
        ]

        if animated:
            self.start()
    
    def __del__(self):
        """Ensure instance is removed from shared instances set when deleted."""
        try:
            self.__class__._instances.discard(self)
        except:
            pass  # Ignore any errors during cleanup
    
    def closeEvent(self, event):
        """Handle widget close event with proper cleanup."""
        self.stop()  # Stop animation and remove from instances
        super().closeEvent(event)

    # Shared driver setup
    @classmethod
    def _ensure_shared_timer(cls):
        if cls._shared_timer is None:
            cls._shared_timer = QTimer()
            cls._shared_timer.setTimerType(Qt.PreciseTimer)
            cls._shared_timer.timeout.connect(cls._on_shared_tick)
            cls._shared_timer.start(int(1000 / max(1, cls._shared_fps)))
        elif not cls._shared_timer.isActive():
            cls._shared_timer.start(int(1000 / max(1, cls._shared_fps)))

    @classmethod
    def _on_shared_tick(cls):
        if not cls._instances:
            if cls._shared_timer and cls._shared_timer.isActive():
                cls._shared_timer.stop()
            return
        dt = 1.0 / max(1, cls._shared_fps)
        cls._shared_time += dt
        # Create a copy of instances to iterate over and remove invalid ones
        instances_to_remove = set()
        for inst in list(cls._instances):
            try:
                if inst._animated and inst.isVisible():
                    inst._time = cls._shared_time
                    inst.update()
            except RuntimeError:
                # C++ object has been deleted, remove from instances
                instances_to_remove.add(inst)
        
        # Remove invalid instances
        for inst in instances_to_remove:
            cls._instances.discard(inst)

    # Public API
    def start(self):
        if not self._animated:
            self._animated = True
            self.__class__._instances.add(self)
            self.__class__._ensure_shared_timer()

    def stop(self):
        if self._animated:
            self._animated = False
            self.__class__._instances.discard(self)

    def setAnimated(self, animated: bool):
        if animated:
            self.start()
        else:
            self.stop()

    def isAnimated(self) -> bool:
        return self._animated

    def setActive(self, active: bool):
        self._is_active = bool(active)
        self.update()

    def isActive(self) -> bool:
        return self._is_active

    def setSize(self, size: str):
        if size in self.SIZE_MAP:
            self._size_key = size
            self._diameter = self.SIZE_MAP[self._size_key]
            self.setFixedSize(self._diameter, self._diameter)
            self.update()

    # Kept for compatibility
    def setCoreColor(self, color: QColor):
        if isinstance(color, QColor):
            self._core_color = QColor(color)
            self.update()

    def setGlowColor(self, color: QColor):
        if isinstance(color, QColor):
            self._glow_color = QColor(color)
            self.update()

    def setFps(self, fps: int):
        fps = int(max(12, min(60, fps)))
        self.__class__._shared_fps = fps
        if self.__class__._shared_timer:
            if self.__class__._shared_timer.isActive():
                self.__class__._shared_timer.stop()
            self.__class__._shared_timer.start(int(1000 / fps))

    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        return self.size()

    # Internal helpers
    def _simple_noise(self, x: float) -> float:
        x = (x + self._noise_seed) * 0.1
        return math.sin(x) * math.cos(x * 1.3) * math.sin(x * 0.7)

    def _wavy_ring_path(self, cx: float, cy: float, radius: float, width: float, amp: float, freq: float, phase: float) -> QPainterPath:
        """Build a thin ring with slight sinusoidal radius modulation to look like waves."""
        steps = 140
        two_pi = 2.0 * math.pi
        da = two_pi / steps

        # Outer boundary
        outer = QPainterPath()
        a = 0.0
        r0 = radius + width * 0.5 + amp * math.sin(freq * a + phase)
        outer.moveTo(QPointF(cx + math.cos(a) * r0, cy + math.sin(a) * r0))
        a = da
        for _ in range(1, steps + 1):
            r = radius + width * 0.5 + amp * math.sin(freq * a + phase)
            outer.lineTo(QPointF(cx + math.cos(a) * r, cy + math.sin(a) * r))
            a += da
        outer.closeSubpath()

        # Inner boundary (reverse)
        inner = QPainterPath()
        a = 0.0
        r0 = radius - width * 0.5 + amp * math.sin(freq * a + phase)
        inner.moveTo(QPointF(cx + math.cos(a) * r0, cy + math.sin(a) * r0))
        a = da
        for _ in range(1, steps + 1):
            r = radius - width * 0.5 + amp * math.sin(freq * a + phase)
            inner.lineTo(QPointF(cx + math.cos(a) * r, cy + math.sin(a) * r))
            a += da
        inner.closeSubpath()

        return outer.subtracted(inner)

    # Painting
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        w = self.width()
        h = self.height()
        cx, cy = w / 2.0, h / 2.0
        base_radius = min(w, h) / 2.0

        # Animation parameters based on mode
        if self._is_active:
            speed_mult = 1.0
            pulse_intensity = 0.28
            noise_intensity = 0.20
        else:
            speed_mult = 0.5
            pulse_intensity = 0.12
            noise_intensity = 0.08

        # Calculate animation values
        t = self._time * speed_mult
        pulse_phase = t + self._pulse_offset
        pulse = 0.5 + pulse_intensity * math.sin(pulse_phase)
        pulse += noise_intensity * self._simple_noise(t * 3.0)
        pulse = max(0.35, min(1.0, pulse))

        painter.setPen(Qt.NoPen)

        # Only draw 3 thin wavy circles, no background or filled core
        arc_speed_scale = 1.8 if self._is_active else 0.8
        for spec in self._arc_specs:
            r = base_radius * spec["r"]
            wth = base_radius * spec["w"]
            amp = wth * spec["amp"] * (0.7 + 0.3 * pulse)
            freq = spec["freq"]
            phase = spec["phase"] + (t * spec["speed"] * arc_speed_scale * math.pi / 180.0)  # radians

            path = self._wavy_ring_path(cx, cy, r, wth, amp, freq, phase)

            # Base faint ring
            base_alpha = int(spec["alpha"] * (0.30 + 0.40 * pulse))
            painter.fillPath(path, QColor(255, 255, 255, max(0, min(255, int(base_alpha * 0.40)))))

            # Moving highlight around circumference (small wedge)
            angle_deg = math.degrees(phase)
            cg = QConicalGradient(QPointF(cx, cy), angle_deg)
            a = max(0, min(255, int(spec["alpha"] * (0.6 + 0.4 * pulse))))
            spread = spec["spread"]
            cg.setColorAt(0.5 - spread, QColor(255, 255, 255, 0))
            cg.setColorAt(0.5, QColor(255, 255, 255, a))
            cg.setColorAt(0.5 + spread, QColor(255, 255, 255, 0))
            painter.fillPath(path, QBrush(cg))

        painter.end()


# Convenience subclasses for explicit sizes
class AiLoaderSmall(AiLoader):
    def __init__(self, animated: bool = True, active: bool = True, parent=None):
        super().__init__(size="small", animated=animated, parent=parent)
        self.setActive(active)


class AiLoaderMedium(AiLoader):
    def __init__(self, animated: bool = True, active: bool = True, parent=None):
        super().__init__(size="medium", animated=animated, parent=parent)
        self.setActive(active)


class AiLoaderBig(AiLoader):
    def __init__(self, animated: bool = True, active: bool = True, parent=None):
        super().__init__(size="big", animated=animated, parent=parent)
        self.setActive(active)