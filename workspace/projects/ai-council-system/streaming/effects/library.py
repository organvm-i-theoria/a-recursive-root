"""
Effects Library

Provides core visual effects for video composition including transitions,
overlays, and particle systems.
"""

import math
import random
from dataclasses import dataclass
from enum import Enum
from typing import Tuple, List, Optional, Callable
import logging

try:
    from PIL import Image, ImageDraw, ImageFilter
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class EffectType(str, Enum):
    """Available effect types"""
    # Transitions
    FADE = "fade"
    WIPE_LEFT = "wipe_left"
    WIPE_RIGHT = "wipe_right"
    WIPE_UP = "wipe_up"
    WIPE_DOWN = "wipe_down"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    ROTATE = "rotate"
    CROSS_FADE = "cross_fade"

    # Overlays
    VIGNETTE = "vignette"
    BLUR = "blur"
    GLOW = "glow"
    GRAIN = "grain"
    CHROMATIC_ABERRATION = "chromatic_aberration"

    # Particles
    CONFETTI = "confetti"
    SPARKLES = "sparkles"
    SNOW = "snow"
    FIREFLIES = "fireflies"


@dataclass
class TransitionEffect:
    """Configuration for a transition effect"""
    effect_type: EffectType
    duration: float  # seconds
    easing: str = "ease-in-out"  # CSS-style easing
    reverse: bool = False


@dataclass
class OverlayEffect:
    """Configuration for an overlay effect"""
    effect_type: EffectType
    intensity: float = 0.5  # 0.0 to 1.0
    parameters: dict = None


@dataclass
class Particle:
    """Single particle in a particle system"""
    x: float
    y: float
    vx: float  # velocity x
    vy: float  # velocity y
    size: float
    color: Tuple[int, int, int, int]  # RGBA
    lifetime: float  # seconds
    age: float = 0.0


@dataclass
class ParticleEffect:
    """Configuration for particle effect"""
    effect_type: EffectType
    particle_count: int = 100
    spawn_rate: float = 10.0  # particles per second
    lifetime: Tuple[float, float] = (1.0, 3.0)  # min, max
    size_range: Tuple[float, float] = (2.0, 8.0)
    color_palette: List[Tuple[int, int, int]] = None


class EffectLibrary:
    """
    Library of video effects

    Provides implementations of various transitions, overlays, and particle effects.
    """

    def __init__(self):
        """Initialize effects library"""
        if not PIL_AVAILABLE:
            raise ImportError("PIL/Pillow and numpy required for effects")

    # ========== TRANSITION EFFECTS ==========

    def apply_fade(
        self,
        frame_a: np.ndarray,
        frame_b: np.ndarray,
        progress: float
    ) -> np.ndarray:
        """
        Fade transition between two frames

        Args:
            frame_a: Starting frame
            frame_b: Ending frame
            progress: Transition progress (0.0 to 1.0)

        Returns:
            Blended frame
        """
        progress = np.clip(progress, 0.0, 1.0)
        return (frame_a * (1 - progress) + frame_b * progress).astype(np.uint8)

    def apply_wipe(
        self,
        frame_a: np.ndarray,
        frame_b: np.ndarray,
        progress: float,
        direction: str = "left"
    ) -> np.ndarray:
        """
        Wipe transition

        Args:
            frame_a: Starting frame
            frame_b: Ending frame
            progress: Transition progress (0.0 to 1.0)
            direction: Wipe direction ("left", "right", "up", "down")

        Returns:
            Wiped frame
        """
        progress = np.clip(progress, 0.0, 1.0)
        h, w = frame_a.shape[:2]
        result = frame_a.copy()

        if direction == "left":
            split = int(w * progress)
            result[:, :split] = frame_b[:, :split]
        elif direction == "right":
            split = int(w * (1 - progress))
            result[:, split:] = frame_b[:, split:]
        elif direction == "up":
            split = int(h * progress)
            result[:split, :] = frame_b[:split, :]
        elif direction == "down":
            split = int(h * (1 - progress))
            result[split:, :] = frame_b[split:, :]

        return result

    def apply_slide(
        self,
        frame_a: np.ndarray,
        frame_b: np.ndarray,
        progress: float,
        direction: str = "left"
    ) -> np.ndarray:
        """
        Slide transition

        Args:
            frame_a: Starting frame
            frame_b: Ending frame
            progress: Transition progress (0.0 to 1.0)
            direction: Slide direction

        Returns:
            Slid frame
        """
        progress = np.clip(progress, 0.0, 1.0)
        h, w = frame_a.shape[:2]
        result = np.zeros_like(frame_a)

        if direction == "left":
            offset = int(w * progress)
            # Frame A slides out to left
            if offset < w:
                result[:, :w-offset] = frame_a[:, offset:]
            # Frame B slides in from right
            if offset > 0:
                result[:, w-offset:] = frame_b[:, :offset]

        elif direction == "right":
            offset = int(w * progress)
            if offset < w:
                result[:, offset:] = frame_a[:, :w-offset]
            if offset > 0:
                result[:, :offset] = frame_b[:, w-offset:]

        elif direction == "up":
            offset = int(h * progress)
            if offset < h:
                result[:h-offset, :] = frame_a[offset:, :]
            if offset > 0:
                result[h-offset:, :] = frame_b[:offset, :]

        elif direction == "down":
            offset = int(h * progress)
            if offset < h:
                result[offset:, :] = frame_a[:h-offset, :]
            if offset > 0:
                result[:offset, :] = frame_b[h-offset:, :]

        return result

    def apply_zoom(
        self,
        frame_a: np.ndarray,
        frame_b: np.ndarray,
        progress: float,
        zoom_in: bool = True
    ) -> np.ndarray:
        """
        Zoom transition

        Args:
            frame_a: Starting frame
            frame_b: Ending frame
            progress: Transition progress (0.0 to 1.0)
            zoom_in: True for zoom in, False for zoom out

        Returns:
            Zoomed frame
        """
        progress = np.clip(progress, 0.0, 1.0)

        if zoom_in:
            # Zoom into frame_a, reveal frame_b
            scale = 1.0 + progress
            alpha = progress
        else:
            # Zoom out from frame_a, reveal frame_b
            scale = 1.0 / (1.0 + progress)
            alpha = progress

        # Scale frame_a
        img_a = Image.fromarray(frame_a)
        h, w = frame_a.shape[:2]

        new_size = (int(w * scale), int(h * scale))
        img_scaled = img_a.resize(new_size, Image.Resampling.LANCZOS)

        # Center crop or pad
        result = Image.new('RGB', (w, h), (0, 0, 0))
        paste_x = (w - new_size[0]) // 2
        paste_y = (h - new_size[1]) // 2

        if scale > 1.0:
            # Crop
            crop_box = (-paste_x, -paste_y, w - paste_x, h - paste_y)
            img_scaled = img_scaled.crop(crop_box)
            paste_x, paste_y = 0, 0

        result.paste(img_scaled, (paste_x, paste_y))
        frame_a_zoomed = np.array(result)

        # Blend with frame_b
        return self.apply_fade(frame_a_zoomed, frame_b, alpha)

    def apply_rotate(
        self,
        frame_a: np.ndarray,
        frame_b: np.ndarray,
        progress: float
    ) -> np.ndarray:
        """
        Rotate transition

        Args:
            frame_a: Starting frame
            frame_b: Ending frame
            progress: Transition progress (0.0 to 1.0)

        Returns:
            Rotated frame
        """
        progress = np.clip(progress, 0.0, 1.0)

        # Rotate frame_a out
        angle_a = int(180 * progress)
        img_a = Image.fromarray(frame_a)
        img_a_rotated = img_a.rotate(angle_a, fillcolor=(0, 0, 0))

        # Rotate frame_b in
        angle_b = int(-180 * (1 - progress))
        img_b = Image.fromarray(frame_b)
        img_b_rotated = img_b.rotate(angle_b, fillcolor=(0, 0, 0))

        # Blend
        frame_a_rot = np.array(img_a_rotated)
        frame_b_rot = np.array(img_b_rotated)

        return self.apply_fade(frame_a_rot, frame_b_rot, progress)

    # ========== OVERLAY EFFECTS ==========

    def apply_vignette(
        self,
        frame: np.ndarray,
        intensity: float = 0.5
    ) -> np.ndarray:
        """
        Apply vignette effect

        Args:
            frame: Input frame
            intensity: Vignette intensity (0.0 to 1.0)

        Returns:
            Frame with vignette
        """
        h, w = frame.shape[:2]

        # Create radial gradient
        y, x = np.ogrid[:h, :w]
        center_y, center_x = h // 2, w // 2

        # Distance from center
        dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_dist = np.sqrt(center_x**2 + center_y**2)

        # Normalize distance
        vignette = 1 - (dist / max_dist) * intensity
        vignette = np.clip(vignette, 0, 1)

        # Apply to all channels
        result = frame.copy()
        for i in range(3):
            result[:, :, i] = (result[:, :, i] * vignette).astype(np.uint8)

        return result

    def apply_blur(
        self,
        frame: np.ndarray,
        intensity: float = 0.5
    ) -> np.ndarray:
        """
        Apply blur effect

        Args:
            frame: Input frame
            intensity: Blur intensity (0.0 to 1.0)

        Returns:
            Blurred frame
        """
        radius = int(intensity * 20)
        if radius < 1:
            return frame

        img = Image.fromarray(frame)
        img_blurred = img.filter(ImageFilter.GaussianBlur(radius))
        return np.array(img_blurred)

    def apply_glow(
        self,
        frame: np.ndarray,
        intensity: float = 0.5,
        color: Tuple[int, int, int] = (255, 255, 255)
    ) -> np.ndarray:
        """
        Apply glow effect

        Args:
            frame: Input frame
            intensity: Glow intensity
            color: Glow color

        Returns:
            Frame with glow
        """
        # Blur the frame
        blurred = self.apply_blur(frame, intensity * 0.3)

        # Create glow layer
        glow = np.full_like(frame, color)

        # Blend
        alpha = intensity * 0.3
        result = (frame * (1 - alpha) + glow * alpha).astype(np.uint8)
        result = self.apply_fade(result, blurred, 0.5)

        return result

    def apply_grain(
        self,
        frame: np.ndarray,
        intensity: float = 0.5
    ) -> np.ndarray:
        """
        Apply film grain effect

        Args:
            frame: Input frame
            intensity: Grain intensity

        Returns:
            Frame with grain
        """
        h, w = frame.shape[:2]

        # Generate noise
        noise = np.random.normal(0, intensity * 25, (h, w, 3))

        # Add to frame
        result = frame.astype(np.float32) + noise
        result = np.clip(result, 0, 255).astype(np.uint8)

        return result

    # ========== PARTICLE EFFECTS ==========

    def create_confetti_particles(
        self,
        count: int,
        width: int,
        height: int
    ) -> List[Particle]:
        """Create confetti particles"""
        particles = []
        colors = [
            (255, 0, 0, 255),    # Red
            (0, 255, 0, 255),    # Green
            (0, 0, 255, 255),    # Blue
            (255, 255, 0, 255),  # Yellow
            (255, 0, 255, 255),  # Magenta
            (0, 255, 255, 255),  # Cyan
        ]

        for _ in range(count):
            particles.append(Particle(
                x=random.uniform(0, width),
                y=random.uniform(-height, 0),  # Start above screen
                vx=random.uniform(-50, 50),
                vy=random.uniform(100, 300),  # Fall down
                size=random.uniform(3, 10),
                color=random.choice(colors),
                lifetime=random.uniform(2, 5)
            ))

        return particles

    def create_sparkle_particles(
        self,
        count: int,
        width: int,
        height: int
    ) -> List[Particle]:
        """Create sparkle particles"""
        particles = []

        for _ in range(count):
            particles.append(Particle(
                x=random.uniform(0, width),
                y=random.uniform(0, height),
                vx=0,
                vy=0,
                size=random.uniform(2, 6),
                color=(255, 255, 255, 255),  # White sparkles
                lifetime=random.uniform(0.5, 2.0)
            ))

        return particles

    def update_particles(
        self,
        particles: List[Particle],
        dt: float,
        width: int,
        height: int,
        gravity: float = 0.0
    ) -> List[Particle]:
        """
        Update particle positions

        Args:
            particles: List of particles
            dt: Delta time (seconds)
            width: Frame width
            height: Frame height
            gravity: Gravity acceleration

        Returns:
            Updated list of particles (dead particles removed)
        """
        alive_particles = []

        for p in particles:
            # Update age
            p.age += dt

            # Remove dead particles
            if p.age >= p.lifetime:
                continue

            # Update velocity (gravity)
            p.vy += gravity * dt

            # Update position
            p.x += p.vx * dt
            p.y += p.vy * dt

            # Keep if still in bounds (with margin)
            if -100 < p.x < width + 100 and -100 < p.y < height + 100:
                alive_particles.append(p)

        return alive_particles

    def render_particles(
        self,
        frame: np.ndarray,
        particles: List[Particle]
    ) -> np.ndarray:
        """
        Render particles onto frame

        Args:
            frame: Base frame
            particles: Particles to render

        Returns:
            Frame with particles
        """
        img = Image.fromarray(frame)
        draw = ImageDraw.Draw(img, 'RGBA')

        for p in particles:
            # Fade based on age
            alpha = int(255 * (1 - p.age / p.lifetime))
            color = p.color[:3] + (alpha,)

            # Draw particle (circle)
            x, y = int(p.x), int(p.y)
            size = int(p.size)

            draw.ellipse(
                (x - size, y - size, x + size, y + size),
                fill=color
            )

        return np.array(img.convert('RGB'))


# Easing functions for smoother transitions

def ease_in_out(t: float) -> float:
    """Ease in-out function"""
    if t < 0.5:
        return 2 * t * t
    else:
        return 1 - 2 * (1 - t) * (1 - t)


def ease_in(t: float) -> float:
    """Ease in function"""
    return t * t


def ease_out(t: float) -> float:
    """Ease out function"""
    return 1 - (1 - t) * (1 - t)


def ease_linear(t: float) -> float:
    """Linear easing (no easing)"""
    return t


EASING_FUNCTIONS = {
    "ease-in-out": ease_in_out,
    "ease-in": ease_in,
    "ease-out": ease_out,
    "linear": ease_linear,
}


def apply_easing(progress: float, easing: str = "ease-in-out") -> float:
    """Apply easing function to progress value"""
    func = EASING_FUNCTIONS.get(easing, ease_linear)
    return func(np.clip(progress, 0.0, 1.0))
