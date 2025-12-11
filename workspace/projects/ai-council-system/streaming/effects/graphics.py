"""
Graphics Compositor

Real-time graphics overlay system for video composition including lower thirds,
topic banners, timers, and multi-layer text rendering.
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, List, Optional, Dict, Any
import logging

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class LayoutPosition(str, Enum):
    """Predefined layout positions"""
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    CENTER_LEFT = "center_left"
    CENTER = "center"
    CENTER_RIGHT = "center_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"


class TextAlignment(str, Enum):
    """Text alignment options"""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class FontWeight(str, Enum):
    """Font weight options"""
    LIGHT = "light"
    REGULAR = "regular"
    BOLD = "bold"
    BLACK = "black"


@dataclass
class TextStyle:
    """
    Text styling configuration

    Defines appearance properties for rendered text including font, color,
    size, and effects.
    """
    font_family: str = "Arial"
    font_size: int = 48
    font_weight: FontWeight = FontWeight.REGULAR
    color: Tuple[int, int, int] = (255, 255, 255)
    alpha: int = 255
    outline_width: int = 0
    outline_color: Tuple[int, int, int] = (0, 0, 0)
    shadow_offset: Tuple[int, int] = (0, 0)
    shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 128)
    alignment: TextAlignment = TextAlignment.LEFT
    line_spacing: float = 1.2
    letter_spacing: int = 0

    def copy(self) -> 'TextStyle':
        """Create a copy of this style"""
        return TextStyle(
            font_family=self.font_family,
            font_size=self.font_size,
            font_weight=self.font_weight,
            color=self.color,
            alpha=self.alpha,
            outline_width=self.outline_width,
            outline_color=self.outline_color,
            shadow_offset=self.shadow_offset,
            shadow_color=self.shadow_color,
            alignment=self.alignment,
            line_spacing=self.line_spacing,
            letter_spacing=self.letter_spacing
        )


@dataclass
class GraphicsLayer:
    """
    Graphics layer for compositing

    Represents a single compositing layer with content, position, and effects.
    """
    name: str
    z_index: int = 0
    position: Tuple[int, int] = (0, 0)
    size: Tuple[int, int] = (100, 100)
    alpha: float = 1.0
    visible: bool = True
    blend_mode: str = "normal"  # "normal", "multiply", "screen", "overlay"
    content: Optional[np.ndarray] = None

    def __lt__(self, other: 'GraphicsLayer') -> bool:
        """Compare layers by z_index for sorting"""
        return self.z_index < other.z_index


class GraphicsCompositor:
    """
    Graphics compositor for real-time video overlays

    Manages multiple graphics layers including text, shapes, and images.
    Provides high-level API for creating lower thirds, banners, timers,
    and other on-screen graphics.
    """

    def __init__(self, width: int = 1920, height: int = 1080):
        """
        Initialize graphics compositor

        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels

        Raises:
            ImportError: If PIL/Pillow not available
        """
        if not PIL_AVAILABLE:
            raise ImportError("PIL/Pillow and numpy required for graphics")

        self.width = width
        self.height = height
        self.layers: Dict[str, GraphicsLayer] = {}
        self.font_cache: Dict[str, ImageFont.FreeTypeFont] = {}

        # Default fonts to try
        self.default_fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "Arial.ttf",
            "arial.ttf",
        ]

        logger.info(f"Graphics compositor initialized ({width}x{height})")

    # ========== FONT MANAGEMENT ==========

    def _get_font_key(self, family: str, size: int, weight: FontWeight) -> str:
        """Generate cache key for font"""
        return f"{family}_{size}_{weight.value}"

    def load_font(
        self,
        family: str,
        size: int,
        weight: FontWeight = FontWeight.REGULAR
    ) -> ImageFont.FreeTypeFont:
        """
        Load and cache a font

        Args:
            family: Font family name or path
            size: Font size in points
            weight: Font weight

        Returns:
            Loaded font object
        """
        cache_key = self._get_font_key(family, size, weight)

        if cache_key in self.font_cache:
            return self.font_cache[cache_key]

        # Try to load the specified font
        font = None
        try:
            font = ImageFont.truetype(family, size)
        except (IOError, OSError):
            # Try default fonts
            for default_font in self.default_fonts:
                try:
                    font = ImageFont.truetype(default_font, size)
                    logger.debug(f"Using fallback font: {default_font}")
                    break
                except (IOError, OSError):
                    continue

        # Fall back to default font if all else fails
        if font is None:
            logger.warning(f"Could not load font {family}, using default")
            font = ImageFont.load_default()

        self.font_cache[cache_key] = font
        return font

    # ========== TEXT RENDERING ==========

    def render_text(
        self,
        text: str,
        style: TextStyle,
        max_width: Optional[int] = None
    ) -> Image.Image:
        """
        Render text with styling

        Args:
            text: Text to render
            style: Text style configuration
            max_width: Maximum width (for wrapping)

        Returns:
            PIL Image with rendered text
        """
        # Load font
        font = self.load_font(style.font_family, style.font_size, style.font_weight)

        # Wrap text if needed
        lines = self._wrap_text(text, font, max_width) if max_width else [text]

        # Calculate dimensions
        line_height = int(style.font_size * style.line_spacing)
        total_height = line_height * len(lines)

        # Calculate max width
        text_width = 0
        for line in lines:
            bbox = font.getbbox(line)
            text_width = max(text_width, bbox[2] - bbox[0])

        # Add padding for effects
        padding = max(
            style.outline_width * 2,
            abs(style.shadow_offset[0]) + 10,
            abs(style.shadow_offset[1]) + 10
        )

        canvas_width = text_width + padding * 2
        canvas_height = total_height + padding * 2

        # Create image with transparency
        img = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Render each line
        y = padding
        for line in lines:
            # Calculate x position based on alignment
            bbox = font.getbbox(line)
            line_width = bbox[2] - bbox[0]

            if style.alignment == TextAlignment.CENTER:
                x = (canvas_width - line_width) // 2
            elif style.alignment == TextAlignment.RIGHT:
                x = canvas_width - line_width - padding
            else:  # LEFT
                x = padding

            # Render shadow
            if style.shadow_offset != (0, 0):
                shadow_x = x + style.shadow_offset[0]
                shadow_y = y + style.shadow_offset[1]
                draw.text(
                    (shadow_x, shadow_y),
                    line,
                    font=font,
                    fill=style.shadow_color
                )

            # Render outline
            if style.outline_width > 0:
                for ox in range(-style.outline_width, style.outline_width + 1):
                    for oy in range(-style.outline_width, style.outline_width + 1):
                        if ox != 0 or oy != 0:
                            draw.text(
                                (x + ox, y + oy),
                                line,
                                font=font,
                                fill=style.outline_color + (style.alpha,)
                            )

            # Render main text
            draw.text(
                (x, y),
                line,
                font=font,
                fill=style.color + (style.alpha,)
            )

            y += line_height

        return img

    def _wrap_text(
        self,
        text: str,
        font: ImageFont.FreeTypeFont,
        max_width: int
    ) -> List[str]:
        """
        Wrap text to fit within max width

        Args:
            text: Text to wrap
            font: Font to use for measurements
            max_width: Maximum line width

        Returns:
            List of wrapped lines
        """
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines if lines else [text]

    # ========== LOWER THIRDS ==========

    def create_lower_third(
        self,
        name: str,
        title: str,
        subtitle: Optional[str] = None,
        position: LayoutPosition = LayoutPosition.BOTTOM_LEFT,
        background_color: Tuple[int, int, int, int] = (0, 0, 0, 180),
        accent_color: Tuple[int, int, int, int] = (0, 120, 255, 255)
    ) -> GraphicsLayer:
        """
        Create a lower third graphic

        Args:
            name: Layer name
            title: Main title text
            subtitle: Optional subtitle text
            position: Position on screen
            background_color: Background color (RGBA)
            accent_color: Accent bar color (RGBA)

        Returns:
            GraphicsLayer with lower third content
        """
        # Dimensions
        width = 600
        height = 120 if subtitle else 80
        accent_width = 8

        # Create canvas
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw background
        draw.rectangle(
            [(accent_width, 0), (width, height)],
            fill=background_color
        )

        # Draw accent bar
        draw.rectangle(
            [(0, 0), (accent_width, height)],
            fill=accent_color
        )

        # Render title
        title_style = TextStyle(
            font_size=36,
            font_weight=FontWeight.BOLD,
            color=(255, 255, 255),
            alignment=TextAlignment.LEFT
        )
        title_img = self.render_text(title, title_style, max_width=width - 40)

        # Paste title
        title_x = accent_width + 20
        title_y = 15 if subtitle else (height - title_img.height) // 2
        img.paste(title_img, (title_x, title_y), title_img)

        # Render subtitle if provided
        if subtitle:
            subtitle_style = TextStyle(
                font_size=24,
                color=(200, 200, 200),
                alignment=TextAlignment.LEFT
            )
            subtitle_img = self.render_text(subtitle, subtitle_style, max_width=width - 40)
            img.paste(subtitle_img, (title_x, 60), subtitle_img)

        # Calculate screen position
        screen_pos = self._calculate_position(position, width, height)

        # Create layer
        layer = GraphicsLayer(
            name=name,
            z_index=10,
            position=screen_pos,
            size=(width, height),
            content=np.array(img)
        )

        return layer

    # ========== TOPIC BANNERS ==========

    def create_topic_banner(
        self,
        name: str,
        topic: str,
        position: LayoutPosition = LayoutPosition.TOP_CENTER,
        background_color: Tuple[int, int, int, int] = (20, 20, 40, 220),
        border_color: Tuple[int, int, int, int] = (100, 150, 255, 255)
    ) -> GraphicsLayer:
        """
        Create a topic banner

        Args:
            name: Layer name
            topic: Topic text
            position: Position on screen
            background_color: Background color (RGBA)
            border_color: Border color (RGBA)

        Returns:
            GraphicsLayer with banner content
        """
        # Dimensions
        max_width = 1600
        height = 80
        border_width = 3

        # Render text to get actual width
        text_style = TextStyle(
            font_size=42,
            font_weight=FontWeight.BOLD,
            color=(255, 255, 255),
            alignment=TextAlignment.CENTER
        )
        text_img = self.render_text(topic, text_style, max_width=max_width - 60)

        # Adjust banner width to text
        width = min(max_width, text_img.width + 60)

        # Create canvas
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw border
        draw.rectangle(
            [(0, 0), (width - 1, height - 1)],
            fill=background_color,
            outline=border_color,
            width=border_width
        )

        # Paste text (centered)
        text_x = (width - text_img.width) // 2
        text_y = (height - text_img.height) // 2
        img.paste(text_img, (text_x, text_y), text_img)

        # Calculate screen position
        screen_pos = self._calculate_position(position, width, height)

        # Create layer
        layer = GraphicsLayer(
            name=name,
            z_index=20,
            position=screen_pos,
            size=(width, height),
            content=np.array(img)
        )

        return layer

    # ========== TIMER DISPLAYS ==========

    def create_timer(
        self,
        name: str,
        time_text: str,
        position: LayoutPosition = LayoutPosition.TOP_RIGHT,
        background_color: Tuple[int, int, int, int] = (40, 40, 40, 200),
        text_color: Tuple[int, int, int] = (255, 255, 255),
        warning_threshold: Optional[float] = None,
        warning_color: Tuple[int, int, int] = (255, 100, 0)
    ) -> GraphicsLayer:
        """
        Create a timer display

        Args:
            name: Layer name
            time_text: Time string (e.g., "2:30")
            position: Position on screen
            background_color: Background color (RGBA)
            text_color: Text color
            warning_threshold: Time in seconds to trigger warning color
            warning_color: Warning text color

        Returns:
            GraphicsLayer with timer content
        """
        # Dimensions
        width = 140
        height = 70

        # Determine if warning
        is_warning = False
        if warning_threshold is not None:
            try:
                parts = time_text.split(':')
                seconds = int(parts[-1])
                if len(parts) > 1:
                    seconds += int(parts[-2]) * 60
                is_warning = seconds <= warning_threshold
            except (ValueError, IndexError):
                pass

        # Create canvas
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw background with rounded corners
        self._draw_rounded_rectangle(
            draw,
            [(0, 0), (width, height)],
            radius=10,
            fill=background_color
        )

        # Render time text
        timer_style = TextStyle(
            font_size=38,
            font_weight=FontWeight.BOLD,
            color=warning_color if is_warning else text_color,
            alignment=TextAlignment.CENTER
        )
        time_img = self.render_text(time_text, timer_style)

        # Paste text (centered)
        text_x = (width - time_img.width) // 2
        text_y = (height - time_img.height) // 2
        img.paste(time_img, (text_x, text_y), time_img)

        # Calculate screen position
        screen_pos = self._calculate_position(position, width, height)

        # Create layer
        layer = GraphicsLayer(
            name=name,
            z_index=30,
            position=screen_pos,
            size=(width, height),
            content=np.array(img)
        )

        return layer

    # ========== LAYER MANAGEMENT ==========

    def add_layer(self, layer: GraphicsLayer):
        """
        Add a graphics layer

        Args:
            layer: Layer to add
        """
        self.layers[layer.name] = layer
        logger.debug(f"Added layer: {layer.name} (z={layer.z_index})")

    def remove_layer(self, name: str) -> bool:
        """
        Remove a graphics layer

        Args:
            name: Layer name

        Returns:
            True if layer was removed, False if not found
        """
        if name in self.layers:
            del self.layers[name]
            logger.debug(f"Removed layer: {name}")
            return True
        return False

    def get_layer(self, name: str) -> Optional[GraphicsLayer]:
        """
        Get a layer by name

        Args:
            name: Layer name

        Returns:
            GraphicsLayer or None if not found
        """
        return self.layers.get(name)

    def update_layer_alpha(self, name: str, alpha: float):
        """
        Update layer transparency

        Args:
            name: Layer name
            alpha: Alpha value (0.0 to 1.0)
        """
        if name in self.layers:
            self.layers[name].alpha = np.clip(alpha, 0.0, 1.0)

    def update_layer_position(self, name: str, position: Tuple[int, int]):
        """
        Update layer position

        Args:
            name: Layer name
            position: New (x, y) position
        """
        if name in self.layers:
            self.layers[name].position = position

    def set_layer_visibility(self, name: str, visible: bool):
        """
        Set layer visibility

        Args:
            name: Layer name
            visible: Visibility flag
        """
        if name in self.layers:
            self.layers[name].visible = visible

    # ========== COMPOSITING ==========

    def composite(self, base_frame: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Composite all layers onto base frame

        Args:
            base_frame: Base frame to composite onto (or black background)

        Returns:
            Composited frame
        """
        # Create or use base
        if base_frame is None:
            result = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        else:
            result = base_frame.copy()

        # Convert to PIL for easier compositing
        result_img = Image.fromarray(result).convert('RGBA')

        # Sort layers by z-index
        sorted_layers = sorted(
            [layer for layer in self.layers.values() if layer.visible],
            key=lambda l: l.z_index
        )

        # Composite each layer
        for layer in sorted_layers:
            if layer.content is None:
                continue

            # Create layer image
            layer_img = Image.fromarray(layer.content).convert('RGBA')

            # Apply alpha
            if layer.alpha < 1.0:
                # Adjust alpha channel
                alpha = layer_img.split()[3]
                alpha = alpha.point(lambda p: int(p * layer.alpha))
                layer_img.putalpha(alpha)

            # Paste onto result
            result_img.paste(layer_img, layer.position, layer_img)

        # Convert back to RGB numpy array
        return np.array(result_img.convert('RGB'))

    # ========== HELPER METHODS ==========

    def _calculate_position(
        self,
        position: LayoutPosition,
        width: int,
        height: int
    ) -> Tuple[int, int]:
        """
        Calculate screen coordinates from layout position

        Args:
            position: Layout position enum
            width: Element width
            height: Element height

        Returns:
            (x, y) coordinates
        """
        margin = 20

        # Horizontal
        if position.value.endswith('_left'):
            x = margin
        elif position.value.endswith('_right'):
            x = self.width - width - margin
        else:  # center
            x = (self.width - width) // 2

        # Vertical
        if position.value.startswith('top_'):
            y = margin
        elif position.value.startswith('bottom_'):
            y = self.height - height - margin
        else:  # center
            y = (self.height - height) // 2

        return (x, y)

    def _draw_rounded_rectangle(
        self,
        draw: ImageDraw.ImageDraw,
        box: List[Tuple[int, int]],
        radius: int,
        fill: Optional[Tuple[int, int, int, int]] = None,
        outline: Optional[Tuple[int, int, int, int]] = None,
        width: int = 1
    ):
        """
        Draw a rounded rectangle

        Args:
            draw: ImageDraw object
            box: Bounding box [(x1, y1), (x2, y2)]
            radius: Corner radius
            fill: Fill color (RGBA)
            outline: Outline color (RGBA)
            width: Outline width
        """
        x1, y1 = box[0]
        x2, y2 = box[1]

        # Draw rounded rectangle using arcs
        draw.rounded_rectangle(
            [(x1, y1), (x2, y2)],
            radius=radius,
            fill=fill,
            outline=outline,
            width=width
        )

    def clear_all_layers(self):
        """Remove all layers"""
        self.layers.clear()
        logger.debug("Cleared all layers")

    def get_layer_count(self) -> int:
        """Get number of layers"""
        return len(self.layers)

    def get_visible_layer_count(self) -> int:
        """Get number of visible layers"""
        return sum(1 for layer in self.layers.values() if layer.visible)
