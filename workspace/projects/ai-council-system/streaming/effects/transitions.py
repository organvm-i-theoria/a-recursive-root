"""
Transition Engine

High-level wrapper for video transitions using the effects library.
Provides simplified API for applying smooth transitions with easing functions.
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, List, Optional, Callable, Dict
import logging

try:
    from PIL import Image
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from .library import EffectLibrary, apply_easing

logger = logging.getLogger(__name__)


class TransitionType(str, Enum):
    """Available transition types"""
    # Fade transitions
    FADE = "fade"
    CROSS_FADE = "cross_fade"

    # Wipe transitions
    WIPE_LEFT = "wipe_left"
    WIPE_RIGHT = "wipe_right"
    WIPE_UP = "wipe_up"
    WIPE_DOWN = "wipe_down"

    # Slide transitions
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"

    # Zoom transitions
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"

    # Special transitions
    ROTATE = "rotate"
    DISSOLVE = "dissolve"
    PIXELATE = "pixelate"
    BLUR_THROUGH = "blur_through"


class EasingFunction(str, Enum):
    """Easing function types"""
    LINEAR = "linear"
    EASE_IN = "ease-in"
    EASE_OUT = "ease-out"
    EASE_IN_OUT = "ease-in-out"
    EASE_IN_CUBIC = "ease-in-cubic"
    EASE_OUT_CUBIC = "ease-out-cubic"
    EASE_IN_OUT_CUBIC = "ease-in-out-cubic"
    EASE_IN_EXPO = "ease-in-expo"
    EASE_OUT_EXPO = "ease-out-expo"
    BOUNCE = "bounce"
    ELASTIC = "elastic"


@dataclass
class TransitionConfig:
    """
    Configuration for a transition

    Defines all parameters needed to execute a smooth transition between
    two video frames or scenes.
    """
    transition_type: TransitionType
    duration: float  # seconds
    easing: EasingFunction = EasingFunction.EASE_IN_OUT
    reverse: bool = False
    fps: int = 30

    # Type-specific parameters
    parameters: Dict[str, any] = field(default_factory=dict)

    def get_total_frames(self) -> int:
        """Calculate total number of frames in transition"""
        return int(self.duration * self.fps)


class TransitionEngine:
    """
    High-level transition engine

    Provides simplified API for applying various transitions between frames
    using the effects library. Handles frame interpolation and easing.
    """

    def __init__(self):
        """
        Initialize transition engine

        Raises:
            ImportError: If PIL/Pillow not available
        """
        if not PIL_AVAILABLE:
            raise ImportError("PIL/Pillow and numpy required for transitions")

        self.effect_lib = EffectLibrary()
        self.easing_functions = self._create_easing_functions()

        logger.info("Transition engine initialized")

    # ========== EASING FUNCTIONS ==========

    def _create_easing_functions(self) -> Dict[str, Callable[[float], float]]:
        """Create dictionary of easing functions"""
        return {
            EasingFunction.LINEAR: self._ease_linear,
            EasingFunction.EASE_IN: self._ease_in,
            EasingFunction.EASE_OUT: self._ease_out,
            EasingFunction.EASE_IN_OUT: self._ease_in_out,
            EasingFunction.EASE_IN_CUBIC: self._ease_in_cubic,
            EasingFunction.EASE_OUT_CUBIC: self._ease_out_cubic,
            EasingFunction.EASE_IN_OUT_CUBIC: self._ease_in_out_cubic,
            EasingFunction.EASE_IN_EXPO: self._ease_in_expo,
            EasingFunction.EASE_OUT_EXPO: self._ease_out_expo,
            EasingFunction.BOUNCE: self._ease_bounce,
            EasingFunction.ELASTIC: self._ease_elastic,
        }

    @staticmethod
    def _ease_linear(t: float) -> float:
        """Linear easing (no easing)"""
        return t

    @staticmethod
    def _ease_in(t: float) -> float:
        """Quadratic ease in"""
        return t * t

    @staticmethod
    def _ease_out(t: float) -> float:
        """Quadratic ease out"""
        return 1 - (1 - t) * (1 - t)

    @staticmethod
    def _ease_in_out(t: float) -> float:
        """Quadratic ease in-out"""
        if t < 0.5:
            return 2 * t * t
        else:
            return 1 - 2 * (1 - t) * (1 - t)

    @staticmethod
    def _ease_in_cubic(t: float) -> float:
        """Cubic ease in"""
        return t * t * t

    @staticmethod
    def _ease_out_cubic(t: float) -> float:
        """Cubic ease out"""
        return 1 - (1 - t) ** 3

    @staticmethod
    def _ease_in_out_cubic(t: float) -> float:
        """Cubic ease in-out"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - 4 * (1 - t) ** 3

    @staticmethod
    def _ease_in_expo(t: float) -> float:
        """Exponential ease in"""
        return 0 if t == 0 else math.pow(2, 10 * (t - 1))

    @staticmethod
    def _ease_out_expo(t: float) -> float:
        """Exponential ease out"""
        return 1 if t == 1 else 1 - math.pow(2, -10 * t)

    @staticmethod
    def _ease_bounce(t: float) -> float:
        """Bounce easing"""
        if t < 1 / 2.75:
            return 7.5625 * t * t
        elif t < 2 / 2.75:
            t -= 1.5 / 2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5 / 2.75:
            t -= 2.25 / 2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625 / 2.75
            return 7.5625 * t * t + 0.984375

    @staticmethod
    def _ease_elastic(t: float) -> float:
        """Elastic easing"""
        if t == 0 or t == 1:
            return t
        return math.pow(2, -10 * t) * math.sin((t - 0.075) * (2 * math.pi) / 0.3) + 1

    def apply_easing(self, progress: float, easing: EasingFunction) -> float:
        """
        Apply easing function to progress

        Args:
            progress: Linear progress (0.0 to 1.0)
            easing: Easing function to apply

        Returns:
            Eased progress value
        """
        progress = np.clip(progress, 0.0, 1.0)
        easing_func = self.easing_functions.get(easing, self._ease_linear)
        return easing_func(progress)

    # ========== TRANSITION APPLICATION ==========

    def apply_transition(
        self,
        frame_a: np.ndarray,
        frame_b: np.ndarray,
        config: TransitionConfig,
        progress: float
    ) -> np.ndarray:
        """
        Apply transition between two frames

        Args:
            frame_a: Starting frame
            frame_b: Ending frame
            config: Transition configuration
            progress: Transition progress (0.0 to 1.0)

        Returns:
            Transitioned frame
        """
        # Apply easing
        eased_progress = self.apply_easing(progress, config.easing)

        # Reverse if needed
        if config.reverse:
            eased_progress = 1.0 - eased_progress

        # Apply transition based on type
        if config.transition_type == TransitionType.FADE:
            return self._apply_fade(frame_a, frame_b, eased_progress)

        elif config.transition_type == TransitionType.CROSS_FADE:
            return self._apply_cross_fade(frame_a, frame_b, eased_progress)

        elif config.transition_type in [
            TransitionType.WIPE_LEFT,
            TransitionType.WIPE_RIGHT,
            TransitionType.WIPE_UP,
            TransitionType.WIPE_DOWN
        ]:
            direction = config.transition_type.value.split('_')[1]
            return self._apply_wipe(frame_a, frame_b, eased_progress, direction)

        elif config.transition_type in [
            TransitionType.SLIDE_LEFT,
            TransitionType.SLIDE_RIGHT,
            TransitionType.SLIDE_UP,
            TransitionType.SLIDE_DOWN
        ]:
            direction = config.transition_type.value.split('_')[1]
            return self._apply_slide(frame_a, frame_b, eased_progress, direction)

        elif config.transition_type == TransitionType.ZOOM_IN:
            return self._apply_zoom(frame_a, frame_b, eased_progress, zoom_in=True)

        elif config.transition_type == TransitionType.ZOOM_OUT:
            return self._apply_zoom(frame_a, frame_b, eased_progress, zoom_in=False)

        elif config.transition_type == TransitionType.ROTATE:
            return self._apply_rotate(frame_a, frame_b, eased_progress)

        elif config.transition_type == TransitionType.DISSOLVE:
            return self._apply_dissolve(frame_a, frame_b, eased_progress)

        elif config.transition_type == TransitionType.PIXELATE:
            return self._apply_pixelate(frame_a, frame_b, eased_progress)

        elif config.transition_type == TransitionType.BLUR_THROUGH:
            return self._apply_blur_through(frame_a, frame_b, eased_progress)

        else:
            logger.warning(f"Unknown transition type: {config.transition_type}")
            return self._apply_fade(frame_a, frame_b, eased_progress)

    # ========== TRANSITION IMPLEMENTATIONS ==========

    def _apply_fade(
        self,
        frame_a: np.ndarray,
        frame_b: np.ndarray,
        progress: float
    ) -> np.ndarray:
        """Apply fade transition"""
        return self.effect_lib.apply_fade(frame_a, frame_b, progress)

    def _apply_cross_fade(
        self,
        frame_a: np.ndarray,
        frame_b: np.ndarray,
        progress: float
    ) -> np.ndarray:
        """Apply cross-fade transition"""
        return self.effect_lib.apply_fade(frame_a, frame_b, progress)

    def _apply_wipe(
        self,
        frame_a: np.ndarray,
        frame_b: np.ndarray,
        progress: float,
        direction: str
    ) -> np.ndarray:
        """Apply wipe transition"""
        return self.effect_lib.apply_wipe(frame_a, frame_b, progress, direction)

    def _apply_slide(
        self,
        frame_a: np.ndarray,
        frame_b: np.ndarray,
        progress: float,
        direction: str
    ) -> np.ndarray:
        """Apply slide transition"""
        return self.effect_lib.apply_slide(frame_a, frame_b, progress, direction)

    def _apply_zoom(
        self,
        frame_a: np.ndarray,
        frame_b: np.ndarray,
        progress: float,
        zoom_in: bool
    ) -> np.ndarray:
        """Apply zoom transition"""
        return self.effect_lib.apply_zoom(frame_a, frame_b, progress, zoom_in)

    def _apply_rotate(
        self,
        frame_a: np.ndarray,
        frame_b: np.ndarray,
        progress: float
    ) -> np.ndarray:
        """Apply rotate transition"""
        return self.effect_lib.apply_rotate(frame_a, frame_b, progress)

    def _apply_dissolve(
        self,
        frame_a: np.ndarray,
        frame_b: np.ndarray,
        progress: float
    ) -> np.ndarray:
        """
        Apply dissolve transition (fade with grain)

        Args:
            frame_a: Starting frame
            frame_b: Ending frame
            progress: Transition progress

        Returns:
            Dissolved frame
        """
        # Basic cross-fade
        result = self.effect_lib.apply_fade(frame_a, frame_b, progress)

        # Add grain during middle of transition
        grain_intensity = 1.0 - abs(progress - 0.5) * 2
        if grain_intensity > 0:
            result = self.effect_lib.apply_grain(result, grain_intensity * 0.3)

        return result

    def _apply_pixelate(
        self,
        frame_a: np.ndarray,
        frame_b: np.ndarray,
        progress: float
    ) -> np.ndarray:
        """
        Apply pixelate transition

        Args:
            frame_a: Starting frame
            frame_b: Ending frame
            progress: Transition progress

        Returns:
            Pixelated transition frame
        """
        h, w = frame_a.shape[:2]

        # Pixelate more in the middle of transition
        pixel_size = int(1 + (1 - abs(progress - 0.5) * 2) * 20)

        # Determine which frame to use
        if progress < 0.5:
            frame = frame_a
        else:
            frame = frame_b

        # Downsample
        small_h = max(1, h // pixel_size)
        small_w = max(1, w // pixel_size)

        img = Image.fromarray(frame)
        img_small = img.resize((small_w, small_h), Image.Resampling.NEAREST)
        img_pixelated = img_small.resize((w, h), Image.Resampling.NEAREST)

        result = np.array(img_pixelated)

        # Blend with target at edges
        if progress < 0.3:
            blend = progress / 0.3
            result = self.effect_lib.apply_fade(frame_a, result, blend)
        elif progress > 0.7:
            blend = (progress - 0.7) / 0.3
            result = self.effect_lib.apply_fade(result, frame_b, blend)

        return result

    def _apply_blur_through(
        self,
        frame_a: np.ndarray,
        frame_b: np.ndarray,
        progress: float
    ) -> np.ndarray:
        """
        Apply blur-through transition

        Args:
            frame_a: Starting frame
            frame_b: Ending frame
            progress: Transition progress

        Returns:
            Blurred transition frame
        """
        # Blur more in the middle
        blur_amount = 1.0 - abs(progress - 0.5) * 2

        # Determine which frame to use
        if progress < 0.5:
            frame = frame_a
            blend_progress = progress * 2
        else:
            frame = frame_b
            blend_progress = (progress - 0.5) * 2

        # Apply blur
        if blur_amount > 0:
            blurred = self.effect_lib.apply_blur(frame, blur_amount)
        else:
            blurred = frame

        return blurred

    # ========== FRAME INTERPOLATION ==========

    def generate_transition_frames(
        self,
        frame_a: np.ndarray,
        frame_b: np.ndarray,
        config: TransitionConfig
    ) -> List[np.ndarray]:
        """
        Generate all frames for a transition

        Args:
            frame_a: Starting frame
            frame_b: Ending frame
            config: Transition configuration

        Returns:
            List of transitioned frames
        """
        frames = []
        total_frames = config.get_total_frames()

        for i in range(total_frames + 1):
            progress = i / total_frames if total_frames > 0 else 1.0
            frame = self.apply_transition(frame_a, frame_b, config, progress)
            frames.append(frame)

        logger.debug(f"Generated {len(frames)} transition frames")
        return frames

    def interpolate_frames(
        self,
        frame_a: np.ndarray,
        frame_b: np.ndarray,
        count: int,
        easing: EasingFunction = EasingFunction.LINEAR
    ) -> List[np.ndarray]:
        """
        Interpolate frames between two frames using simple blending

        Args:
            frame_a: Starting frame
            frame_b: Ending frame
            count: Number of frames to generate (including start and end)
            easing: Easing function to apply

        Returns:
            List of interpolated frames
        """
        if count < 2:
            return [frame_a]

        frames = []
        for i in range(count):
            progress = i / (count - 1)
            eased_progress = self.apply_easing(progress, easing)
            frame = self.effect_lib.apply_fade(frame_a, frame_b, eased_progress)
            frames.append(frame)

        return frames

    # ========== PRESET TRANSITIONS ==========

    def create_quick_fade(self, duration: float = 0.5) -> TransitionConfig:
        """Create a quick fade transition preset"""
        return TransitionConfig(
            transition_type=TransitionType.FADE,
            duration=duration,
            easing=EasingFunction.EASE_IN_OUT
        )

    def create_slow_fade(self, duration: float = 2.0) -> TransitionConfig:
        """Create a slow fade transition preset"""
        return TransitionConfig(
            transition_type=TransitionType.FADE,
            duration=duration,
            easing=EasingFunction.EASE_IN_OUT
        )

    def create_slide_transition(
        self,
        direction: str = "left",
        duration: float = 1.0
    ) -> TransitionConfig:
        """
        Create a slide transition preset

        Args:
            direction: Slide direction ("left", "right", "up", "down")
            duration: Transition duration

        Returns:
            TransitionConfig
        """
        transition_map = {
            "left": TransitionType.SLIDE_LEFT,
            "right": TransitionType.SLIDE_RIGHT,
            "up": TransitionType.SLIDE_UP,
            "down": TransitionType.SLIDE_DOWN,
        }

        transition_type = transition_map.get(
            direction.lower(),
            TransitionType.SLIDE_LEFT
        )

        return TransitionConfig(
            transition_type=transition_type,
            duration=duration,
            easing=EasingFunction.EASE_IN_OUT_CUBIC
        )

    def create_zoom_transition(
        self,
        zoom_in: bool = True,
        duration: float = 1.0
    ) -> TransitionConfig:
        """
        Create a zoom transition preset

        Args:
            zoom_in: True for zoom in, False for zoom out
            duration: Transition duration

        Returns:
            TransitionConfig
        """
        return TransitionConfig(
            transition_type=TransitionType.ZOOM_IN if zoom_in else TransitionType.ZOOM_OUT,
            duration=duration,
            easing=EasingFunction.EASE_IN_OUT
        )

    def create_dramatic_transition(self, duration: float = 1.5) -> TransitionConfig:
        """Create a dramatic transition with elastic easing"""
        return TransitionConfig(
            transition_type=TransitionType.ZOOM_IN,
            duration=duration,
            easing=EasingFunction.ELASTIC
        )
