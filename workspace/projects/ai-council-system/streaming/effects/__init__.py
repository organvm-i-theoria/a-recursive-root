"""
Advanced Video Effects System for AI Council

Provides professional broadcast-quality video effects including transitions,
overlays, scene management, and data visualizations.

Components:
    - library: Effect implementations (transitions, overlays, particles)
    - scenes: Scene management and automation
    - graphics: Real-time graphics and text overlays
    - transitions: Transition engine for smooth scene changes
    - visualizations: Data visualization (charts, meters, tallies)

Usage:
    from streaming.effects import SceneManager, TransitionEngine, GraphicsCompositor

    # Create scene manager
    scene_manager = SceneManager()
    scene = scene_manager.get_scene('debate_round')

    # Apply transition
    transition = TransitionEngine()
    frame = await transition.apply('fade', frame_a, frame_b, progress=0.5)

    # Add graphics overlay
    graphics = GraphicsCompositor()
    frame = graphics.add_lower_third(frame, "The Pragmatist", "System Architect")
"""

from .library import (
    EffectType,
    TransitionEffect,
    OverlayEffect,
    ParticleEffect,
    EffectLibrary,
)

from .scenes import (
    SceneType,
    Scene,
    SceneElement,
    SceneManager,
    SceneConfig,
)

from .graphics import (
    GraphicsCompositor,
    TextStyle,
    GraphicsLayer,
    LayoutPosition,
)

from .transitions import (
    TransitionEngine,
    TransitionType,
    TransitionConfig,
    EasingFunction,
)

from .visualizations import (
    DataVisualizer,
    ChartType,
    VoteVisualization,
    MetricsDisplay,
)

__all__ = [
    # Library
    'EffectType',
    'TransitionEffect',
    'OverlayEffect',
    'ParticleEffect',
    'EffectLibrary',

    # Scenes
    'SceneType',
    'Scene',
    'SceneElement',
    'SceneManager',
    'SceneConfig',

    # Graphics
    'GraphicsCompositor',
    'TextStyle',
    'GraphicsLayer',
    'LayoutPosition',

    # Transitions
    'TransitionEngine',
    'TransitionType',
    'TransitionConfig',
    'EasingFunction',

    # Visualizations
    'DataVisualizer',
    'ChartType',
    'VoteVisualization',
    'MetricsDisplay',
]

__version__ = '1.0.0'
