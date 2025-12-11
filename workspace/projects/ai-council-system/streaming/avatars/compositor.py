"""
Avatar Compositor

Composites avatars onto video frames with various layouts and effects.
"""

import io
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple
import logging

try:
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from .generator import GeneratedAvatar
from .expressions import Expression, AnimationFrame

logger = logging.getLogger(__name__)


class LayoutMode(str, Enum):
    """Avatar layout modes"""
    GRID = "grid"  # Grid layout (auto-arranges based on count)
    CAROUSEL = "carousel"  # Horizontal carousel
    SPOTLIGHT = "spotlight"  # Single large avatar with others small
    STACK = "stack"  # Vertical stack
    CIRCLE = "circle"  # Circular arrangement
    CUSTOM = "custom"  # Custom positions


class OverlayPosition(str, Enum):
    """Standard overlay positions"""
    TOP_LEFT = "top-left"
    TOP_CENTER = "top-center"
    TOP_RIGHT = "top-right"
    CENTER_LEFT = "center-left"
    CENTER = "center"
    CENTER_RIGHT = "center-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_CENTER = "bottom-center"
    BOTTOM_RIGHT = "bottom-right"


@dataclass
class CompositorConfig:
    """Configuration for avatar compositor"""
    layout_mode: LayoutMode = LayoutMode.GRID
    avatar_size: int = 200  # pixels
    spacing: int = 20  # pixels between avatars
    border_width: int = 3
    border_color: Tuple[int, int, int] = (255, 255, 255)
    background_alpha: float = 0.0  # 0.0 = transparent, 1.0 = opaque
    show_names: bool = True
    name_font_size: int = 24
    shadow: bool = True
    rounded_corners: bool = True
    corner_radius: int = 20


class AvatarCompositor:
    """
    Compositor for overlaying avatars on video frames

    Handles multiple layout modes, positioning, and visual effects.
    """

    def __init__(self, config: Optional[CompositorConfig] = None):
        """
        Initialize compositor

        Args:
            config: Compositor configuration
        """
        if not PIL_AVAILABLE:
            raise ImportError("PIL/Pillow required for avatar composition. Install: pip install Pillow numpy")

        self.config = config or CompositorConfig()

    async def overlay_single_avatar(
        self,
        frame: np.ndarray,
        avatar: GeneratedAvatar,
        position: OverlayPosition = OverlayPosition.TOP_LEFT,
        expression: Optional[Expression] = None,
    ) -> np.ndarray:
        """
        Overlay single avatar on frame

        Args:
            frame: Video frame as numpy array (H, W, 3) or (H, W, 4)
            avatar: Generated avatar to overlay
            position: Position on frame
            expression: Current expression (for effects)

        Returns:
            Frame with avatar overlaid
        """
        # Convert frame to PIL Image
        frame_img = Image.fromarray(frame)

        # Load avatar
        avatar_img = avatar.to_pil_image()
        if not avatar_img:
            logger.warning("Could not load avatar image")
            return frame

        # Resize avatar
        avatar_img = avatar_img.resize(
            (self.config.avatar_size, self.config.avatar_size),
            Image.Resampling.LANCZOS
        )

        # Apply effects
        avatar_img = self._apply_avatar_effects(avatar_img, expression)

        # Calculate position
        x, y = self._calculate_position(
            frame_img.size,
            (self.config.avatar_size, self.config.avatar_size),
            position
        )

        # Create composite
        if avatar_img.mode == 'RGBA':
            frame_img.paste(avatar_img, (x, y), avatar_img)
        else:
            frame_img.paste(avatar_img, (x, y))

        # Add name if configured
        if self.config.show_names:
            self._draw_name(frame_img, avatar.personality, x, y)

        return np.array(frame_img)

    async def overlay_multiple_avatars(
        self,
        frame: np.ndarray,
        avatars: List[GeneratedAvatar],
        active_speaker: Optional[int] = None,
    ) -> np.ndarray:
        """
        Overlay multiple avatars using configured layout

        Args:
            frame: Video frame
            avatars: List of avatars to overlay
            active_speaker: Index of currently speaking avatar (for emphasis)

        Returns:
            Frame with all avatars overlaid
        """
        if not avatars:
            return frame

        frame_img = Image.fromarray(frame)

        if self.config.layout_mode == LayoutMode.GRID:
            frame_img = self._layout_grid(frame_img, avatars, active_speaker)
        elif self.config.layout_mode == LayoutMode.CAROUSEL:
            frame_img = self._layout_carousel(frame_img, avatars, active_speaker)
        elif self.config.layout_mode == LayoutMode.SPOTLIGHT:
            frame_img = self._layout_spotlight(frame_img, avatars, active_speaker)
        elif self.config.layout_mode == LayoutMode.STACK:
            frame_img = self._layout_stack(frame_img, avatars, active_speaker)
        elif self.config.layout_mode == LayoutMode.CIRCLE:
            frame_img = self._layout_circle(frame_img, avatars, active_speaker)

        return np.array(frame_img)

    def _layout_grid(
        self,
        frame: Image.Image,
        avatars: List[GeneratedAvatar],
        active_speaker: Optional[int]
    ) -> Image.Image:
        """Grid layout - arrange avatars in grid"""
        n = len(avatars)

        # Calculate grid dimensions
        cols = min(5, n)
        rows = (n + cols - 1) // cols

        # Calculate positions
        frame_width, frame_height = frame.size
        grid_width = cols * (self.config.avatar_size + self.config.spacing) - self.config.spacing
        grid_height = rows * (self.config.avatar_size + self.config.spacing) - self.config.spacing

        # Center grid at bottom of frame
        start_x = (frame_width - grid_width) // 2
        start_y = frame_height - grid_height - 50  # 50px margin from bottom

        # Place avatars
        for i, avatar in enumerate(avatars):
            row = i // cols
            col = i % cols

            x = start_x + col * (self.config.avatar_size + self.config.spacing)
            y = start_y + row * (self.config.avatar_size + self.config.spacing)

            # Emphasize active speaker
            size = self.config.avatar_size
            if i == active_speaker:
                size = int(size * 1.2)
                x -= int(size * 0.1)
                y -= int(size * 0.1)

            self._place_avatar(frame, avatar, x, y, size, i == active_speaker)

        return frame

    def _layout_carousel(
        self,
        frame: Image.Image,
        avatars: List[GeneratedAvatar],
        active_speaker: Optional[int]
    ) -> Image.Image:
        """Carousel layout - horizontal row at bottom"""
        frame_width, frame_height = frame.size
        n = len(avatars)

        total_width = n * (self.config.avatar_size + self.config.spacing) - self.config.spacing
        start_x = (frame_width - total_width) // 2
        y = frame_height - self.config.avatar_size - 50

        for i, avatar in enumerate(avatars):
            x = start_x + i * (self.config.avatar_size + self.config.spacing)

            size = self.config.avatar_size
            if i == active_speaker:
                size = int(size * 1.3)
                y_offset = y - 30
            else:
                y_offset = y

            self._place_avatar(frame, avatar, x, y_offset, size, i == active_speaker)

        return frame

    def _layout_spotlight(
        self,
        frame: Image.Image,
        avatars: List[GeneratedAvatar],
        active_speaker: Optional[int]
    ) -> Image.Image:
        """Spotlight layout - large active speaker, small others"""
        frame_width, frame_height = frame.size

        if active_speaker is not None and 0 <= active_speaker < len(avatars):
            # Large center avatar for speaker
            large_size = int(self.config.avatar_size * 2)
            x = (frame_width - large_size) // 2
            y = (frame_height - large_size) // 2

            self._place_avatar(frame, avatars[active_speaker], x, y, large_size, True)

            # Small avatars for others at bottom
            others = [a for i, a in enumerate(avatars) if i != active_speaker]
            if others:
                small_size = int(self.config.avatar_size * 0.6)
                total_width = len(others) * (small_size + self.config.spacing)
                start_x = (frame_width - total_width) // 2
                y = frame_height - small_size - 30

                for i, avatar in enumerate(others):
                    x = start_x + i * (small_size + self.config.spacing)
                    self._place_avatar(frame, avatar, x, y, small_size, False)

        return frame

    def _layout_stack(
        self,
        frame: Image.Image,
        avatars: List[GeneratedAvatar],
        active_speaker: Optional[int]
    ) -> Image.Image:
        """Vertical stack on right side"""
        frame_width, frame_height = frame.size
        n = len(avatars)

        total_height = n * (self.config.avatar_size + self.config.spacing)
        start_y = (frame_height - total_height) // 2
        x = frame_width - self.config.avatar_size - 30

        for i, avatar in enumerate(avatars):
            y = start_y + i * (self.config.avatar_size + self.config.spacing)
            self._place_avatar(frame, avatar, x, y, self.config.avatar_size, i == active_speaker)

        return frame

    def _layout_circle(
        self,
        frame: Image.Image,
        avatars: List[GeneratedAvatar],
        active_speaker: Optional[int]
    ) -> Image.Image:
        """Circular arrangement"""
        import math

        frame_width, frame_height = frame.size
        n = len(avatars)

        # Calculate circle radius
        radius = min(frame_width, frame_height) // 3

        center_x = frame_width // 2
        center_y = frame_height // 2

        for i, avatar in enumerate(avatars):
            angle = (2 * math.pi * i) / n - (math.pi / 2)  # Start from top
            x = center_x + int(radius * math.cos(angle)) - self.config.avatar_size // 2
            y = center_y + int(radius * math.sin(angle)) - self.config.avatar_size // 2

            self._place_avatar(frame, avatar, x, y, self.config.avatar_size, i == active_speaker)

        return frame

    def _place_avatar(
        self,
        frame: Image.Image,
        avatar: GeneratedAvatar,
        x: int,
        y: int,
        size: int,
        is_active: bool
    ):
        """Place single avatar on frame"""
        avatar_img = avatar.to_pil_image()
        if not avatar_img:
            return

        # Resize
        avatar_img = avatar_img.resize((size, size), Image.Resampling.LANCZOS)

        # Apply effects
        if self.config.rounded_corners:
            avatar_img = self._make_circular(avatar_img)

        # Add border for active speaker
        if is_active:
            avatar_img = self._add_border(avatar_img, (255, 215, 0), width=self.config.border_width * 2)
        elif self.config.border_width > 0:
            avatar_img = self._add_border(avatar_img, self.config.border_color, width=self.config.border_width)

        # Add shadow
        if self.config.shadow:
            avatar_img = self._add_shadow(avatar_img)

        # Paste
        if avatar_img.mode == 'RGBA':
            frame.paste(avatar_img, (x, y), avatar_img)
        else:
            frame.paste(avatar_img, (x, y))

        # Add name
        if self.config.show_names:
            self._draw_name(frame, avatar.personality, x, y + size + 5)

    def _apply_avatar_effects(
        self,
        avatar_img: Image.Image,
        expression: Optional[Expression]
    ) -> Image.Image:
        """Apply visual effects based on expression"""
        # Future: Add expression-based effects (glow, blur, etc.)
        return avatar_img

    def _make_circular(self, img: Image.Image) -> Image.Image:
        """Make image circular"""
        # Create circular mask
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + img.size, fill=255)

        # Apply mask
        output = Image.new('RGBA', img.size, (0, 0, 0, 0))
        output.paste(img.convert('RGB'), (0, 0))
        output.putalpha(mask)

        return output

    def _add_border(
        self,
        img: Image.Image,
        color: Tuple[int, int, int],
        width: int
    ) -> Image.Image:
        """Add border to image"""
        size = img.size[0] + width * 2

        bordered = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(bordered)

        # Draw border circle
        draw.ellipse(
            (0, 0, size, size),
            fill=color + (255,),
            outline=color + (255,)
        )

        # Paste original image
        bordered.paste(img, (width, width), img if img.mode == 'RGBA' else None)

        return bordered

    def _add_shadow(self, img: Image.Image) -> Image.Image:
        """Add drop shadow effect"""
        # Simple shadow - create slightly larger dark circle behind
        shadow_offset = 5
        size = img.size[0] + shadow_offset * 2

        shadow = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(shadow)

        # Draw shadow
        draw.ellipse(
            (shadow_offset, shadow_offset, size - shadow_offset, size - shadow_offset),
            fill=(0, 0, 0, 100)
        )

        # Paste avatar on top
        shadow.paste(img, (0, 0), img if img.mode == 'RGBA' else None)

        return shadow

    def _draw_name(self, frame: Image.Image, name: str, x: int, y: int):
        """Draw personality name below avatar"""
        draw = ImageDraw.Draw(frame)

        # Try to load font
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                self.config.name_font_size
            )
        except:
            font = ImageFont.load_default()

        # Get text size
        bbox = draw.textbbox((0, 0), name, font=font)
        text_width = bbox[2] - bbox[0]

        # Center text under avatar
        text_x = x + (self.config.avatar_size - text_width) // 2
        text_y = y

        # Draw text with outline for visibility
        outline_color = (0, 0, 0)
        text_color = (255, 255, 255)

        # Draw outline
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            draw.text((text_x + dx, text_y + dy), name, font=font, fill=outline_color)

        # Draw text
        draw.text((text_x, text_y), name, font=font, fill=text_color)

    def _calculate_position(
        self,
        frame_size: Tuple[int, int],
        avatar_size: Tuple[int, int],
        position: OverlayPosition
    ) -> Tuple[int, int]:
        """Calculate avatar position on frame"""
        frame_w, frame_h = frame_size
        avatar_w, avatar_h = avatar_size

        positions = {
            OverlayPosition.TOP_LEFT: (20, 20),
            OverlayPosition.TOP_CENTER: ((frame_w - avatar_w) // 2, 20),
            OverlayPosition.TOP_RIGHT: (frame_w - avatar_w - 20, 20),
            OverlayPosition.CENTER_LEFT: (20, (frame_h - avatar_h) // 2),
            OverlayPosition.CENTER: ((frame_w - avatar_w) // 2, (frame_h - avatar_h) // 2),
            OverlayPosition.CENTER_RIGHT: (frame_w - avatar_w - 20, (frame_h - avatar_h) // 2),
            OverlayPosition.BOTTOM_LEFT: (20, frame_h - avatar_h - 20),
            OverlayPosition.BOTTOM_CENTER: ((frame_w - avatar_w) // 2, frame_h - avatar_h - 20),
            OverlayPosition.BOTTOM_RIGHT: (frame_w - avatar_w - 20, frame_h - avatar_h - 20),
        }

        return positions.get(position, (20, 20))


def create_compositor(layout: LayoutMode = LayoutMode.GRID, **kwargs) -> AvatarCompositor:
    """Create avatar compositor with configuration"""
    config = CompositorConfig(layout_mode=layout, **kwargs)
    return AvatarCompositor(config)
