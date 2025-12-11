"""
Data Visualization System

Real-time data visualization for debate statistics, vote tallies, and metrics.
Renders charts, graphs, and animated displays.
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, List, Dict, Optional, Any
import logging

try:
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class ChartType(str, Enum):
    """Available chart types"""
    BAR = "bar"
    HORIZONTAL_BAR = "horizontal_bar"
    PIE = "pie"
    DONUT = "donut"
    LINE = "line"
    GAUGE = "gauge"
    PROGRESS = "progress"


class AnimationStyle(str, Enum):
    """Animation styles for visualizations"""
    NONE = "none"
    FADE_IN = "fade_in"
    SLIDE_IN = "slide_in"
    COUNT_UP = "count_up"
    GROW = "grow"
    PULSE = "pulse"


@dataclass
class ChartData:
    """
    Data for chart rendering

    Contains labels, values, and styling information for a chart.
    """
    labels: List[str]
    values: List[float]
    colors: Optional[List[Tuple[int, int, int]]] = None
    title: Optional[str] = None
    subtitle: Optional[str] = None

    def __post_init__(self):
        """Validate and set defaults"""
        if len(self.labels) != len(self.values):
            raise ValueError("Labels and values must have same length")

        # Set default colors if not provided
        if self.colors is None:
            self.colors = self._generate_default_colors(len(self.labels))

    @staticmethod
    def _generate_default_colors(count: int) -> List[Tuple[int, int, int]]:
        """Generate default color palette"""
        palette = [
            (66, 133, 244),   # Blue
            (234, 67, 53),    # Red
            (251, 188, 4),    # Yellow
            (52, 168, 83),    # Green
            (171, 71, 188),   # Purple
            (255, 112, 67),   # Orange
            (0, 172, 193),    # Cyan
            (255, 82, 82),    # Pink
        ]
        # Repeat palette if needed
        return [palette[i % len(palette)] for i in range(count)]


@dataclass
class VoteVisualization:
    """Configuration for vote visualization"""
    chart_type: ChartType = ChartType.HORIZONTAL_BAR
    show_percentages: bool = True
    show_counts: bool = True
    animation: AnimationStyle = AnimationStyle.GROW
    animation_duration: float = 1.0


class DataVisualizer:
    """
    Data visualization system

    Renders various chart types for displaying debate statistics,
    vote tallies, and metrics with optional animations.
    """

    def __init__(self, width: int = 800, height: int = 600):
        """
        Initialize data visualizer

        Args:
            width: Default canvas width
            height: Default canvas height

        Raises:
            ImportError: If PIL/Pillow not available
        """
        if not PIL_AVAILABLE:
            raise ImportError("PIL/Pillow and numpy required for visualizations")

        self.width = width
        self.height = height
        self.font_cache: Dict[int, ImageFont.FreeTypeFont] = {}

        # Default fonts to try
        self.default_fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "Arial.ttf",
        ]

        logger.info(f"Data visualizer initialized ({width}x{height})")

    # ========== FONT MANAGEMENT ==========

    def _load_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Load and cache font"""
        if size in self.font_cache:
            return self.font_cache[size]

        font = None
        for font_path in self.default_fonts:
            try:
                font = ImageFont.truetype(font_path, size)
                break
            except (IOError, OSError):
                continue

        if font is None:
            font = ImageFont.load_default()

        self.font_cache[size] = font
        return font

    # ========== BAR CHARTS ==========

    def render_bar_chart(
        self,
        data: ChartData,
        width: Optional[int] = None,
        height: Optional[int] = None,
        background_color: Tuple[int, int, int] = (30, 30, 30),
        show_values: bool = True,
        animation_progress: float = 1.0
    ) -> Image.Image:
        """
        Render vertical bar chart

        Args:
            data: Chart data
            width: Chart width (None = use default)
            height: Chart height (None = use default)
            background_color: Background color
            show_values: Show value labels
            animation_progress: Animation progress (0.0 to 1.0)

        Returns:
            PIL Image with rendered chart
        """
        w = width or self.width
        h = height or self.height

        # Create canvas
        img = Image.new('RGB', (w, h), background_color)
        draw = ImageDraw.Draw(img)

        # Margins
        margin_top = 60 if data.title else 20
        margin_bottom = 80
        margin_left = 60
        margin_right = 20

        # Chart area
        chart_x = margin_left
        chart_y = margin_top
        chart_w = w - margin_left - margin_right
        chart_h = h - margin_top - margin_bottom

        # Draw title
        if data.title:
            font_title = self._load_font(32)
            title_bbox = draw.textbbox((0, 0), data.title, font=font_title)
            title_w = title_bbox[2] - title_bbox[0]
            draw.text(
                ((w - title_w) // 2, 15),
                data.title,
                fill=(255, 255, 255),
                font=font_title
            )

        # Calculate bar dimensions
        bar_count = len(data.values)
        if bar_count == 0:
            return img

        bar_width = (chart_w - (bar_count - 1) * 10) // bar_count
        max_value = max(data.values) if data.values else 1

        # Draw bars
        font_label = self._load_font(16)
        font_value = self._load_font(20)

        for i, (label, value, color) in enumerate(zip(data.labels, data.values, data.colors)):
            # Calculate bar position
            x = chart_x + i * (bar_width + 10)
            bar_height = int((value / max_value) * chart_h * animation_progress)
            y = chart_y + chart_h - bar_height

            # Draw bar
            draw.rectangle(
                [(x, y), (x + bar_width, chart_y + chart_h)],
                fill=color
            )

            # Draw value on bar
            if show_values and animation_progress > 0.5:
                value_text = f"{value:.0f}"
                value_bbox = draw.textbbox((0, 0), value_text, font=font_value)
                value_w = value_bbox[2] - value_bbox[0]
                draw.text(
                    (x + (bar_width - value_w) // 2, y - 25),
                    value_text,
                    fill=(255, 255, 255),
                    font=font_value
                )

            # Draw label
            label_bbox = draw.textbbox((0, 0), label, font=font_label)
            label_w = label_bbox[2] - label_bbox[0]
            draw.text(
                (x + (bar_width - label_w) // 2, chart_y + chart_h + 10),
                label,
                fill=(200, 200, 200),
                font=font_label
            )

        return img

    def render_horizontal_bar_chart(
        self,
        data: ChartData,
        width: Optional[int] = None,
        height: Optional[int] = None,
        background_color: Tuple[int, int, int] = (30, 30, 30),
        show_values: bool = True,
        animation_progress: float = 1.0
    ) -> Image.Image:
        """
        Render horizontal bar chart

        Args:
            data: Chart data
            width: Chart width
            height: Chart height
            background_color: Background color
            show_values: Show value labels
            animation_progress: Animation progress

        Returns:
            PIL Image with rendered chart
        """
        w = width or self.width
        h = height or self.height

        # Create canvas
        img = Image.new('RGB', (w, h), background_color)
        draw = ImageDraw.Draw(img)

        # Margins
        margin_top = 60 if data.title else 20
        margin_bottom = 20
        margin_left = 150  # Space for labels
        margin_right = 20

        # Chart area
        chart_x = margin_left
        chart_y = margin_top
        chart_w = w - margin_left - margin_right
        chart_h = h - margin_top - margin_bottom

        # Draw title
        if data.title:
            font_title = self._load_font(32)
            title_bbox = draw.textbbox((0, 0), data.title, font=font_title)
            title_w = title_bbox[2] - title_bbox[0]
            draw.text(
                ((w - title_w) // 2, 15),
                data.title,
                fill=(255, 255, 255),
                font=font_title
            )

        # Calculate bar dimensions
        bar_count = len(data.values)
        if bar_count == 0:
            return img

        bar_height = (chart_h - (bar_count - 1) * 10) // bar_count
        max_value = max(data.values) if data.values else 1

        # Draw bars
        font_label = self._load_font(18)
        font_value = self._load_font(20)

        for i, (label, value, color) in enumerate(zip(data.labels, data.values, data.colors)):
            # Calculate bar position
            y = chart_y + i * (bar_height + 10)
            bar_width = int((value / max_value) * chart_w * animation_progress)

            # Draw bar
            draw.rectangle(
                [(chart_x, y), (chart_x + bar_width, y + bar_height)],
                fill=color
            )

            # Draw label (left of bar)
            label_bbox = draw.textbbox((0, 0), label, font=font_label)
            label_h = label_bbox[3] - label_bbox[1]
            draw.text(
                (10, y + (bar_height - label_h) // 2),
                label,
                fill=(255, 255, 255),
                font=font_label
            )

            # Draw value (on or right of bar)
            if show_values and animation_progress > 0.5:
                value_text = f"{value:.0f}"
                value_bbox = draw.textbbox((0, 0), value_text, font=font_value)
                value_w = value_bbox[2] - value_bbox[0]
                value_h = value_bbox[3] - value_bbox[1]

                value_x = chart_x + bar_width + 10
                if bar_width > value_w + 20:
                    value_x = chart_x + bar_width - value_w - 10

                draw.text(
                    (value_x, y + (bar_height - value_h) // 2),
                    value_text,
                    fill=(255, 255, 255),
                    font=font_value
                )

        return img

    # ========== PIE/DONUT CHARTS ==========

    def render_pie_chart(
        self,
        data: ChartData,
        width: Optional[int] = None,
        height: Optional[int] = None,
        background_color: Tuple[int, int, int] = (30, 30, 30),
        donut: bool = False,
        animation_progress: float = 1.0
    ) -> Image.Image:
        """
        Render pie or donut chart

        Args:
            data: Chart data
            width: Chart width
            height: Chart height
            background_color: Background color
            donut: True for donut chart, False for pie
            animation_progress: Animation progress

        Returns:
            PIL Image with rendered chart
        """
        w = width or self.width
        h = height or self.height

        # Create canvas
        img = Image.new('RGB', (w, h), background_color)
        draw = ImageDraw.Draw(img)

        # Draw title
        margin_top = 60 if data.title else 20
        if data.title:
            font_title = self._load_font(32)
            title_bbox = draw.textbbox((0, 0), data.title, font=font_title)
            title_w = title_bbox[2] - title_bbox[0]
            draw.text(
                ((w - title_w) // 2, 15),
                data.title,
                fill=(255, 255, 255),
                font=font_title
            )

        # Calculate chart area
        chart_size = min(w - 40, h - margin_top - 140)
        center_x = w // 2
        center_y = margin_top + chart_size // 2 + 20

        # Calculate total
        total = sum(data.values)
        if total == 0:
            return img

        # Draw slices
        start_angle = -90  # Start at top
        for i, (label, value, color) in enumerate(zip(data.labels, data.values, data.colors)):
            # Calculate angle
            angle = (value / total) * 360 * animation_progress

            # Draw slice
            bbox = [
                center_x - chart_size // 2,
                center_y - chart_size // 2,
                center_x + chart_size // 2,
                center_y + chart_size // 2
            ]

            draw.pieslice(
                bbox,
                start=start_angle,
                end=start_angle + angle,
                fill=color,
                outline=(0, 0, 0),
                width=2
            )

            start_angle += angle

        # Draw donut hole if needed
        if donut:
            hole_size = int(chart_size * 0.5)
            hole_bbox = [
                center_x - hole_size // 2,
                center_y - hole_size // 2,
                center_x + hole_size // 2,
                center_y + hole_size // 2
            ]
            draw.ellipse(hole_bbox, fill=background_color)

        # Draw legend
        legend_y = center_y + chart_size // 2 + 40
        font_legend = self._load_font(16)

        for i, (label, value, color) in enumerate(zip(data.labels, data.values, data.colors)):
            percentage = (value / total) * 100

            # Color box
            box_x = 40 + (i % 2) * (w // 2)
            box_y = legend_y + (i // 2) * 30
            draw.rectangle(
                [(box_x, box_y), (box_x + 20, box_y + 20)],
                fill=color
            )

            # Label
            legend_text = f"{label}: {percentage:.1f}%"
            draw.text(
                (box_x + 30, box_y + 2),
                legend_text,
                fill=(255, 255, 255),
                font=font_legend
            )

        return img

    # ========== GAUGE CHARTS ==========

    def render_gauge(
        self,
        value: float,
        max_value: float,
        label: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        background_color: Tuple[int, int, int] = (30, 30, 30),
        gauge_color: Tuple[int, int, int] = (66, 133, 244),
        animation_progress: float = 1.0
    ) -> Image.Image:
        """
        Render gauge chart

        Args:
            value: Current value
            max_value: Maximum value
            label: Label text
            width: Chart width
            height: Chart height
            background_color: Background color
            gauge_color: Gauge fill color
            animation_progress: Animation progress

        Returns:
            PIL Image with rendered gauge
        """
        w = width or self.width
        h = height or self.height

        # Create canvas
        img = Image.new('RGB', (w, h), background_color)
        draw = ImageDraw.Draw(img)

        # Gauge dimensions
        center_x = w // 2
        center_y = h // 2 + 20
        radius = min(w, h) // 2 - 40

        # Calculate angle
        percentage = min(value / max_value, 1.0) * animation_progress
        angle = percentage * 270  # 270 degree arc

        # Draw background arc
        bbox = [
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius
        ]

        draw.arc(
            bbox,
            start=135,
            end=405,
            fill=(60, 60, 60),
            width=20
        )

        # Draw value arc
        if angle > 0:
            draw.arc(
                bbox,
                start=135,
                end=135 + angle,
                fill=gauge_color,
                width=20
            )

        # Draw value text
        font_value = self._load_font(48)
        value_text = f"{value:.0f}"
        value_bbox = draw.textbbox((0, 0), value_text, font=font_value)
        value_w = value_bbox[2] - value_bbox[0]
        value_h = value_bbox[3] - value_bbox[1]

        draw.text(
            (center_x - value_w // 2, center_y - value_h // 2),
            value_text,
            fill=(255, 255, 255),
            font=font_value
        )

        # Draw label
        font_label = self._load_font(20)
        label_bbox = draw.textbbox((0, 0), label, font=font_label)
        label_w = label_bbox[2] - label_bbox[0]

        draw.text(
            (center_x - label_w // 2, center_y + value_h // 2 + 10),
            label,
            fill=(200, 200, 200),
            font=font_label
        )

        # Draw percentage
        font_pct = self._load_font(24)
        pct_text = f"{percentage * 100:.1f}%"
        pct_bbox = draw.textbbox((0, 0), pct_text, font=font_pct)
        pct_w = pct_bbox[2] - pct_bbox[0]

        draw.text(
            (center_x - pct_w // 2, h - 40),
            pct_text,
            fill=(150, 150, 150),
            font=font_pct
        )

        return img

    # ========== CONFIDENCE METERS ==========

    def render_confidence_meter(
        self,
        confidence: float,
        agent_name: str,
        width: int = 400,
        height: int = 100,
        background_color: Tuple[int, int, int] = (30, 30, 30),
        animation_progress: float = 1.0
    ) -> Image.Image:
        """
        Render confidence meter for an agent

        Args:
            confidence: Confidence value (0.0 to 1.0)
            agent_name: Agent name
            width: Meter width
            height: Meter height
            background_color: Background color
            animation_progress: Animation progress

        Returns:
            PIL Image with confidence meter
        """
        # Create canvas
        img = Image.new('RGB', (width, height), background_color)
        draw = ImageDraw.Draw(img)

        # Meter dimensions
        meter_height = 30
        meter_y = height - meter_height - 10

        # Draw meter background
        draw.rectangle(
            [(10, meter_y), (width - 10, meter_y + meter_height)],
            fill=(50, 50, 50),
            outline=(100, 100, 100),
            width=2
        )

        # Calculate meter fill
        fill_width = int((width - 20) * confidence * animation_progress)

        # Determine color based on confidence
        if confidence < 0.3:
            fill_color = (234, 67, 53)  # Red
        elif confidence < 0.7:
            fill_color = (251, 188, 4)  # Yellow
        else:
            fill_color = (52, 168, 83)  # Green

        # Draw meter fill
        if fill_width > 0:
            draw.rectangle(
                [(10, meter_y), (10 + fill_width, meter_y + meter_height)],
                fill=fill_color
            )

        # Draw agent name
        font_name = self._load_font(20)
        draw.text(
            (10, 10),
            agent_name,
            fill=(255, 255, 255),
            font=font_name
        )

        # Draw confidence percentage
        font_pct = self._load_font(18)
        pct_text = f"{confidence * 100:.0f}%"
        pct_bbox = draw.textbbox((0, 0), pct_text, font=font_pct)
        pct_w = pct_bbox[2] - pct_bbox[0]

        draw.text(
            (width - pct_w - 10, 10),
            pct_text,
            fill=(200, 200, 200),
            font=font_pct
        )

        return img

    # ========== VOTE DISTRIBUTIONS ==========

    def render_vote_distribution(
        self,
        votes: Dict[str, int],
        width: Optional[int] = None,
        height: Optional[int] = None,
        animation_progress: float = 1.0
    ) -> Image.Image:
        """
        Render vote distribution chart

        Args:
            votes: Dictionary mapping agent names to vote counts
            width: Chart width
            height: Chart height
            animation_progress: Animation progress

        Returns:
            PIL Image with vote distribution
        """
        # Convert to ChartData
        data = ChartData(
            labels=list(votes.keys()),
            values=list(votes.values()),
            title="Vote Distribution"
        )

        # Render as horizontal bar chart
        return self.render_horizontal_bar_chart(
            data,
            width=width,
            height=height,
            animation_progress=animation_progress
        )

    # ========== METRICS DISPLAY ==========

    def render_metrics_display(
        self,
        metrics: Dict[str, Any],
        width: int = 400,
        height: int = 300,
        background_color: Tuple[int, int, int] = (30, 30, 30)
    ) -> Image.Image:
        """
        Render debate metrics display

        Args:
            metrics: Dictionary of metric name to value
            width: Display width
            height: Display height
            background_color: Background color

        Returns:
            PIL Image with metrics
        """
        # Create canvas
        img = Image.new('RGB', (width, height), background_color)
        draw = ImageDraw.Draw(img)

        # Fonts
        font_label = self._load_font(18)
        font_value = self._load_font(32)

        # Draw metrics
        y = 20
        for label, value in metrics.items():
            # Draw label
            draw.text(
                (20, y),
                label,
                fill=(150, 150, 150),
                font=font_label
            )

            # Draw value
            value_text = str(value)
            draw.text(
                (20, y + 25),
                value_text,
                fill=(255, 255, 255),
                font=font_value
            )

            # Draw separator line
            y += 75
            if y < height - 20:
                draw.line(
                    [(20, y - 10), (width - 20, y - 10)],
                    fill=(60, 60, 60),
                    width=1
                )

        return img

    # ========== ANIMATED COUNTERS ==========

    def render_animated_counter(
        self,
        value: float,
        target_value: float,
        label: str,
        width: int = 300,
        height: int = 150,
        background_color: Tuple[int, int, int] = (30, 30, 30),
        color: Tuple[int, int, int] = (66, 133, 244)
    ) -> Image.Image:
        """
        Render animated counter

        Args:
            value: Current value (for animation)
            target_value: Target value
            label: Counter label
            width: Counter width
            height: Counter height
            background_color: Background color
            color: Counter color

        Returns:
            PIL Image with counter
        """
        # Create canvas
        img = Image.new('RGB', (width, height), background_color)
        draw = ImageDraw.Draw(img)

        # Draw value
        font_value = self._load_font(64)
        value_text = f"{int(value)}"
        value_bbox = draw.textbbox((0, 0), value_text, font=font_value)
        value_w = value_bbox[2] - value_bbox[0]
        value_h = value_bbox[3] - value_bbox[1]

        draw.text(
            ((width - value_w) // 2, (height - value_h) // 2 - 20),
            value_text,
            fill=color,
            font=font_value
        )

        # Draw label
        font_label = self._load_font(20)
        label_bbox = draw.textbbox((0, 0), label, font=font_label)
        label_w = label_bbox[2] - label_bbox[0]

        draw.text(
            ((width - label_w) // 2, (height - value_h) // 2 + value_h + 10),
            label,
            fill=(200, 200, 200),
            font=font_label
        )

        return img
