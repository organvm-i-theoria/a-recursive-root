"""
Avatar Generation System for AI Council

This module provides AI-generated visual avatars for council debate agents,
with sentiment-based expressions and video composition capabilities.

Components:
    - generator: Avatar generation using Stable Diffusion, DALL-E, Midjourney
    - expressions: Sentiment-to-expression mapping and animation
    - compositor: Video overlay and composition
    - cache: Avatar caching and management
    - personality_mapping: Personality to visual trait mapping

Usage:
    from streaming.avatars import AvatarGenerator, AvatarCompositor

    generator = AvatarGenerator(provider='stable_diffusion')
    avatar = await generator.generate_avatar('Pragmatist')

    compositor = AvatarCompositor()
    frame = await compositor.overlay_avatar(video_frame, avatar, position='top-left')
"""

from .generator import (
    AvatarGenerator,
    AvatarProvider,
    AvatarStyle,
    GeneratedAvatar,
)

from .expressions import (
    ExpressionEngine,
    Expression,
    SentimentType,
    AnimationFrame,
)

from .compositor import (
    AvatarCompositor,
    LayoutMode,
    OverlayPosition,
    CompositorConfig,
)

from .cache import (
    AvatarCache,
    CacheEntry,
)

from .personality_mapping import (
    PersonalityVisualTraits,
    get_personality_traits,
    PERSONALITY_AVATAR_MAP,
)

__all__ = [
    # Generator
    'AvatarGenerator',
    'AvatarProvider',
    'AvatarStyle',
    'GeneratedAvatar',

    # Expressions
    'ExpressionEngine',
    'Expression',
    'SentimentType',
    'AnimationFrame',

    # Compositor
    'AvatarCompositor',
    'LayoutMode',
    'OverlayPosition',
    'CompositorConfig',

    # Cache
    'AvatarCache',
    'CacheEntry',

    # Personality Mapping
    'PersonalityVisualTraits',
    'get_personality_traits',
    'PERSONALITY_AVATAR_MAP',
]

__version__ = '0.1.0'
