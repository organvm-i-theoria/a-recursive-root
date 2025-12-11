## Avatar Generation System

**Version**: 1.0.0
**Status**: ✅ Complete (Phase 4.1)

---

## Overview

The Avatar Generation System creates unique, AI-generated visual identities for each of the 15 AI Council personalities. It provides sentiment-based expressions, multiple layout modes for video composition, and intelligent caching.

### Features

✨ **Multi-Provider Support**
- DALL-E 3 (OpenAI)
- Stable Diffusion (via Replicate)
- Stability AI API
- Local Stable Diffusion (requires setup)
- Mock mode (for testing)

🎭 **Expression Engine**
- 10+ sentiment types
- 15+ facial expressions
- Personality-specific expression preferences
- Animated expression sequences
- Text sentiment analysis

🎬 **Video Composition**
- 5 layout modes (Grid, Carousel, Spotlight, Stack, Circle)
- Rounded corners and borders
- Active speaker highlighting
- Name labels
- Drop shadows

💾 **Intelligent Cache**
- LRU eviction policy
- Automatic size management
- Metadata tracking
- Fast retrieval

---

## Architecture

```
streaming/avatars/
├── __init__.py           # Package initialization
├── personality_mapping.py # Personality → Visual traits mapping
├── generator.py          # Avatar generation (multi-provider)
├── expressions.py        # Sentiment → Expression mapping
├── compositor.py         # Video overlay and composition
├── cache.py             # Cache management
└── README.md            # This file
```

---

## Quick Start

### 1. Generate Avatars

```python
from streaming.avatars import AvatarGenerator, AvatarProvider, AvatarSize

# Create generator (mock for testing)
generator = AvatarGenerator(
    provider=AvatarProvider.MOCK,
    default_size=AvatarSize.LARGE,
    quality="high"
)

# Generate avatar for a personality
avatar = await generator.generate_avatar("pragmatist")

# Save to file
avatar.save("pragmatist_avatar.png")
```

### 2. Use Real AI Providers

```python
# DALL-E 3 (requires OPENAI_API_KEY)
generator = AvatarGenerator(
    provider=AvatarProvider.DALLE3,
    api_key="your-openai-api-key",
    quality="ultra"
)

# Replicate (requires REPLICATE_API_KEY)
generator = AvatarGenerator(
    provider=AvatarProvider.REPLICATE,
    api_key="your-replicate-api-key"
)
```

### 3. Expression Analysis

```python
from streaming.avatars import ExpressionEngine, SentimentType

engine = ExpressionEngine()

# Analyze text sentiment
text = "I strongly agree with this proposal!"
sentiment, confidence = engine.analyze_text_sentiment(text)

# Get appropriate expression
expression = engine.get_expression_for_sentiment(
    sentiment,
    confidence,
    personality="pragmatist"
)

# Create animation
animation = await engine.create_expression_animation(
    sentiment=sentiment,
    duration=3.0,
    confidence=confidence,
    personality="pragmatist"
)
```

### 4. Video Composition

```python
from streaming.avatars import AvatarCompositor, LayoutMode
import numpy as np

# Create compositor
compositor = AvatarCompositor(
    config=CompositorConfig(
        layout_mode=LayoutMode.GRID,
        avatar_size=200,
        show_names=True,
        rounded_corners=True
    )
)

# Create video frame (1920x1080)
frame = np.ones((1080, 1920, 3), dtype=np.uint8) * 50

# Overlay avatars (index 2 is speaking)
composed = await compositor.overlay_multiple_avatars(
    frame,
    avatars,  # List of GeneratedAvatar
    active_speaker=2
)
```

---

## Personality Visual Traits

Each of the 15 personalities has unique visual characteristics:

| Personality | Style | Primary Colors | Mood |
|------------|-------|---------------|------|
| Pragmatist | Realistic | Navy, Gray, White | Grounded, Professional |
| Idealist | Realistic | Sky Blue, Gold, Cream | Optimistic, Inspiring |
| Skeptic | Realistic | Dark Gray, Black, Red | Analytical, Questioning |
| Optimist | Cartoon | Yellow, Blue, Green | Enthusiastic, Upbeat |
| Contrarian | Cyberpunk | Purple, Neon Green, Pink | Provocative, Bold |
| Mediator | Realistic | Beige, Sage, Gray | Peaceful, Balanced |
| Analyst | Realistic | White, Steel, Blue | Methodical, Precise |
| Visionary | Classical | Purple, Cosmic Blue, Gold | Inspired, Forward-looking |
| Traditionalist | Classical | Forest Green, Burgundy, Tan | Dignified, Respectful |
| Revolutionary | Cyberpunk | Red, Black, Gold | Passionate, Fierce |
| Economist | Realistic | Dollar Green, Gold, Navy | Strategic, Calculating |
| Ethicist | Realistic | White, Gray, Blue, Gold | Principled, Thoughtful |
| Technologist | Cyberpunk | Silicon Blue, LED White, Chrome | Innovative, Tech-focused |
| Populist | Realistic | Working Blue, Earth Brown, Red | Relatable, Down-to-earth |
| Philosopher | Classical | Wisdom Purple, Thought Gray | Contemplative, Profound |

---

## Components

### 1. Personality Mapping

**File**: `personality_mapping.py`

Maps personalities to visual traits for consistent avatar generation.

```python
from streaming.avatars import get_personality_traits, build_full_prompt

# Get traits
traits = get_personality_traits("pragmatist")

# Build generation prompt
prompt = build_full_prompt(traits, quality_level="high")
```

**Key Classes:**
- `PersonalityVisualTraits` - Visual characteristic definition
- `AvatarStyle` - Enum of available styles

### 2. Avatar Generator

**File**: `generator.py`

Generates avatars using multiple AI providers.

```python
from streaming.avatars import (
    AvatarGenerator,
    AvatarProvider,
    AvatarSize,
    GeneratedAvatar
)

# Initialize
generator = AvatarGenerator(
    provider=AvatarProvider.DALLE3,
    default_size=AvatarSize.LARGE,
    quality="high",
    cache_dir="./avatar_cache"
)

# Generate
avatar = await generator.generate_avatar(
    personality="idealist",
    size=AvatarSize.ULTRA,
    seed=42  # For reproducibility
)
```

**Providers:**
- `DALLE3` - OpenAI DALL-E 3 (best quality, slower)
- `REPLICATE` - Stable Diffusion XL via Replicate
- `STABILITY_AI` - Stability AI API
- `STABLE_DIFFUSION` - Local SD (requires setup)
- `MOCK` - Testing/development

**Avatar Sizes:**
- `SMALL` - 256x256
- `MEDIUM` - 512x512
- `LARGE` - 1024x1024
- `ULTRA` - 1536x1536

### 3. Expression Engine

**File**: `expressions.py`

Maps sentiment to facial expressions and animations.

```python
from streaming.avatars import ExpressionEngine, SentimentType, Expression

engine = ExpressionEngine(
    default_intensity=0.7,
    transition_duration=0.5
)

# Get expression for sentiment
expression = engine.get_expression_for_sentiment(
    sentiment=SentimentType.CONFIDENT,
    confidence=0.85,
    personality="analyst"
)

# Create speaking animation
animation = engine.get_speaking_animation(
    personality="visionary",
    text_length=500,
    sentiment=SentimentType.ENTHUSIASTIC
)
```

**Sentiment Types:**
- `POSITIVE`, `NEGATIVE`, `NEUTRAL`
- `CONFIDENT`, `UNCERTAIN`
- `AGREEING`, `DISAGREEING`
- `QUESTIONING`, `ASSERTIVE`, `CONTEMPLATIVE`

**Expressions:**
- Positive: `SMILING`, `ENTHUSIASTIC`, `NODDING`, `FRIENDLY`
- Negative: `FROWNING`, `CONCERNED`, `SKEPTICAL`, `DISAPPROVING`
- Neutral: `THOUGHTFUL`, `LISTENING`, `ANALYTICAL`, `CALM`
- Confident: `ASSERTIVE`, `DIRECT_GAZE`, `UPRIGHT`, `COMMANDING`
- Uncertain: `PONDERING`, `HESITANT`, `QUESTIONING`, `DOUBTFUL`

### 4. Avatar Compositor

**File**: `compositor.py`

Overlays avatars on video frames with multiple layouts.

```python
from streaming.avatars import (
    AvatarCompositor,
    LayoutMode,
    OverlayPosition,
    CompositorConfig
)

config = CompositorConfig(
    layout_mode=LayoutMode.GRID,
    avatar_size=200,
    spacing=20,
    border_width=3,
    border_color=(255, 255, 255),
    show_names=True,
    shadow=True,
    rounded_corners=True,
    corner_radius=20
)

compositor = AvatarCompositor(config)
```

**Layout Modes:**
- `GRID` - Auto-arranged grid (best for 3-9 avatars)
- `CAROUSEL` - Horizontal row at bottom
- `SPOTLIGHT` - Large speaker + small others
- `STACK` - Vertical stack on right side
- `CIRCLE` - Circular arrangement

**Single Avatar Overlay:**
```python
frame = await compositor.overlay_single_avatar(
    frame=video_frame,
    avatar=avatar,
    position=OverlayPosition.TOP_LEFT,
    expression=Expression.SMILING
)
```

**Multiple Avatar Overlay:**
```python
frame = await compositor.overlay_multiple_avatars(
    frame=video_frame,
    avatars=[avatar1, avatar2, avatar3, avatar4, avatar5],
    active_speaker=2  # Highlight 3rd avatar
)
```

### 5. Avatar Cache

**File**: `cache.py`

Persistent cache for generated avatars.

```python
from streaming.avatars import AvatarCache

cache = AvatarCache(
    cache_dir="./avatar_cache",
    max_size_mb=500,
    max_age_days=30
)

# Try to get from cache
cached = await cache.get(
    personality="pragmatist",
    provider=AvatarProvider.DALLE3,
    size=AvatarSize.LARGE,
    prompt="full_prompt_here"
)

# Store in cache
await cache.put(avatar, prompt)

# Get statistics
stats = await cache.get_stats()
print(f"Cache size: {stats['total_size_mb']:.1f} MB")
print(f"Utilization: {stats['utilization']*100:.1f}%")

# Cleanup old entries
removed = await cache.cleanup_old_entries()
```

---

## Demo Application

Run the comprehensive demo:

```bash
cd /workspace/projects/ai-council-system
python examples/avatar_demo.py
```

**Demo includes:**
1. Avatar generation for all personalities
2. Expression engine text analysis
3. Multiple composition layouts
4. Cache system demonstration
5. Integrated workflow simulation

**Output:**
- Generated avatars saved to `demo_output/avatar_*.png`
- Composition examples in `demo_output/composition_*.png`
- Debate visualization in `demo_output/debate_visualization.png`

---

## Integration with Debate System

```python
from core.council import DebateSessionManager
from streaming.avatars import (
    AvatarGenerator,
    ExpressionEngine,
    AvatarCompositor,
    LayoutMode
)

# Initialize components
generator = AvatarGenerator(provider=AvatarProvider.DALLE3)
expression_engine = ExpressionEngine()
compositor = AvatarCompositor(layout=LayoutMode.CAROUSEL)

# Generate avatars for council members
avatars = {}
for agent in council.agents:
    avatars[agent.id] = await generator.generate_avatar(
        personality=agent.personality.archetype
    )

# During debate
for round in debate.rounds:
    for agent_id, response in round.responses.items():
        # Analyze sentiment
        sentiment, conf = expression_engine.analyze_text_sentiment(
            response.content
        )

        # Get expression
        expression = expression_engine.get_expression_for_sentiment(
            sentiment, conf, agent.personality.archetype
        )

        # Compose frame with current expression
        frame = await compositor.overlay_multiple_avatars(
            video_frame,
            [avatars[aid] for aid in agent_ids],
            active_speaker=agent_ids.index(agent_id)
        )

        # Stream frame...
```

---

## Configuration

### Environment Variables

```bash
# For DALL-E 3
export OPENAI_API_KEY="your-openai-api-key"

# For Replicate
export REPLICATE_API_KEY="your-replicate-api-key"

# For Stability AI
export STABILITY_API_KEY="your-stability-api-key"
```

### Generator Configuration

```python
generator = AvatarGenerator(
    provider=AvatarProvider.DALLE3,
    api_key=None,  # Uses environment variable
    default_size=AvatarSize.LARGE,
    quality="high",  # "low", "medium", "high", "ultra"
    cache_dir="./avatar_cache"
)
```

### Compositor Configuration

```python
config = CompositorConfig(
    layout_mode=LayoutMode.GRID,
    avatar_size=200,  # pixels
    spacing=20,  # pixels between avatars
    border_width=3,
    border_color=(255, 255, 255),  # RGB
    background_alpha=0.0,  # 0.0 = transparent
    show_names=True,
    name_font_size=24,
    shadow=True,
    rounded_corners=True,
    corner_radius=20
)
```

---

## Performance Considerations

### Avatar Generation

- **DALL-E 3**: ~10-20 seconds per avatar, highest quality
- **Replicate**: ~3-8 seconds per avatar, good quality
- **Stability AI**: ~2-5 seconds per avatar, fast
- **Mock**: <1 second, testing only

### Caching Strategy

1. Generate avatars once for each personality
2. Cache with quality level in key
3. Reuse cached avatars across sessions
4. Set appropriate `max_age_days` based on update frequency

### Memory Usage

- Single avatar (1024x1024 PNG): ~1-3 MB
- 15 personalities cached: ~15-45 MB
- Cache with 500MB limit: ~100-500 avatars

---

## Best Practices

### 1. Avatar Generation

```python
# DO: Use appropriate quality for use case
generator = AvatarGenerator(
    provider=AvatarProvider.DALLE3,
    quality="high"  # For production streams
)

# DON'T: Use ultra quality for all avatars
# (Slow generation, large files)
```

### 2. Expression Mapping

```python
# DO: Match expressions to personality
expression = engine.get_expression_for_sentiment(
    sentiment, confidence, personality="pragmatist"
)

# DON'T: Use same expression for all personalities
```

### 3. Composition

```python
# DO: Choose layout based on avatar count
if len(avatars) <= 3:
    layout = LayoutMode.CAROUSEL
elif len(avatars) <= 6:
    layout = LayoutMode.GRID
else:
    layout = LayoutMode.STACK

# DON'T: Use fixed layout for all cases
```

### 4. Caching

```python
# DO: Enable caching for production
generator = AvatarGenerator(cache_dir="./avatar_cache")

# DO: Cleanup old entries periodically
await cache.cleanup_old_entries()

# DON'T: Disable caching (wastes API calls/time)
```

---

## Troubleshooting

### Issue: "PIL not available"

```bash
pip install Pillow numpy
```

### Issue: "OPENAI_API_KEY required"

```bash
export OPENAI_API_KEY="your-key"
# Or pass directly
generator = AvatarGenerator(api_key="your-key")
```

### Issue: Slow generation

```bash
# Use mock provider for development
generator = AvatarGenerator(provider=AvatarProvider.MOCK)

# Or enable caching
generator = AvatarGenerator(cache_dir="./cache")
```

### Issue: Cache fills up quickly

```python
# Reduce max size
cache = AvatarCache(max_size_mb=100)

# Or reduce max age
cache = AvatarCache(max_age_days=7)
```

---

## Future Enhancements

### Planned Features

- [ ] Animation interpolation between expressions
- [ ] Voice-synced lip movement
- [ ] Background removal/transparency
- [ ] Custom avatar training (fine-tuned models)
- [ ] Real-time avatar modification
- [ ] WebRTC streaming support
- [ ] GPU acceleration for composition

### Experimental

- Voice cloning integration (Phase 4.6)
- Generative background matching (Phase 4.5)
- Multi-language avatar variations (Phase 4.4)

---

## Dependencies

```
# Core
Pillow>=10.2.0
numpy>=1.24.0

# Providers
openai>=1.12.0  # DALL-E 3
replicate>=0.22.0  # Replicate
aiohttp>=3.9.0  # HTTP client

# Optional
opencv-python>=4.9.0  # Video processing
```

---

## API Reference

See individual module docstrings for detailed API documentation:

- `personality_mapping.py` - Personality traits and prompt building
- `generator.py` - Avatar generation
- `expressions.py` - Expression engine
- `compositor.py` - Video composition
- `cache.py` - Cache management

---

## License

Part of the AI Council System project.

---

**Last Updated**: Phase 4.1 Complete
**Version**: 1.0.0
**Status**: ✅ Production Ready
