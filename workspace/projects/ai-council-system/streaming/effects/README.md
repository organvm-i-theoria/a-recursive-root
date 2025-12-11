# Advanced Video Effects System

**Version**: 1.0.0
**Status**: ✅ Complete (Phase 4.2)

---

## Overview

The Advanced Video Effects System provides professional broadcast-quality video effects for the AI Council platform, including transitions, overlays, scene management, graphics composition, and data visualizations.

### Features

🎬 **Professional Transitions**
- 13 transition types (fade, wipe, slide, zoom, rotate, etc.)
- Configurable easing functions
- Frame interpolation
- Custom duration and timing

🎨 **Visual Effects**
- Vignette, blur, glow, grain
- Chromatic aberration
- Layer blending modes
- Alpha compositing

✨ **Particle Systems**
- Confetti, sparkles, snow, fireflies
- Physics-based animation
- Customizable colors and lifetimes

📊 **Data Visualizations**
- Bar charts, pie charts, gauges
- Vote tallies and distributions
- Confidence meters
- Animated counters
- Real-time metrics displays

🎭 **Scene Management**
- 6 predefined scene types
- Automatic flow control
- Element lifecycle management
- Transition coordination

📺 **Graphics Overlays**
- Lower thirds (name/title banners)
- Topic banners
- Timers with warning states
- Multi-layer compositing
- Professional text rendering

---

## Architecture

```
streaming/effects/
├── __init__.py          # Package exports
├── library.py           # Core effects (transitions, overlays, particles)
├── scenes.py           # Scene management and flow
├── graphics.py         # Graphics compositor (text, overlays)
├── transitions.py      # Transition engine wrapper
├── visualizations.py   # Data visualization system
└── README.md           # This file
```

---

## Quick Start

### 1. Transitions

```python
from streaming.effects import TransitionEngine, TransitionType
import numpy as np

# Create frames
frame_a = np.zeros((1080, 1920, 3), dtype=np.uint8)  # Black
frame_b = np.ones((1080, 1920, 3), dtype=np.uint8) * 255  # White

# Apply transition
engine = TransitionEngine()
result = await engine.apply_transition(
    frame_a, frame_b,
    TransitionType.FADE,
    progress=0.5  # 50% through transition
)
```

### 2. Graphics Overlays

```python
from streaming.effects import GraphicsCompositor, LayoutPosition

compositor = GraphicsCompositor()

# Create lower third
lower_third = compositor.create_lower_third(
    name="speaker",
    title="The Pragmatist",
    subtitle="System Architect"
)
compositor.add_layer(lower_third)

# Composite onto video frame
result = compositor.composite(video_frame)
```

### 3. Data Visualizations

```python
from streaming.effects import DataVisualizer

visualizer = DataVisualizer()

# Create vote chart
vote_data = {"Support": 45, "Oppose": 30, "Neutral": 25}
chart = visualizer.create_bar_chart(
    data=vote_data,
    title="Vote Distribution",
    width=800,
    height=500
)
```

### 4. Scene Management

```python
from streaming.effects import SceneManager, SceneType

manager = SceneManager()

# Start intro scene
scene = manager.start_scene(SceneType.INTRO)

# Auto-transition to next scene
await manager.transition_to_scene(SceneType.DEBATE_ROUND)
```

---

## Components

### 1. Effects Library (`library.py`)

Core visual effects implementation.

#### Transitions

**Available Types:**
- `FADE` - Cross-fade between frames
- `WIPE_LEFT/RIGHT/UP/DOWN` - Directional wipes
- `SLIDE_LEFT/RIGHT/UP/DOWN` - Sliding transitions
- `ZOOM_IN/OUT` - Zoom transitions
- `ROTATE` - Rotating transition
- `CROSS_FADE` - Advanced cross-fade

```python
from streaming.effects import EffectLibrary

library = EffectLibrary()

# Apply fade
result = library.apply_fade(frame_a, frame_b, progress=0.5)

# Apply wipe
result = library.apply_wipe(frame_a, frame_b, progress=0.7, direction="left")

# Apply zoom
result = library.apply_zoom(frame_a, frame_b, progress=0.3, zoom_in=True)
```

#### Overlay Effects

```python
# Vignette
result = library.apply_vignette(frame, intensity=0.5)

# Blur
result = library.apply_blur(frame, intensity=0.7)

# Glow
result = library.apply_glow(frame, intensity=0.6, color=(255, 255, 255))

# Film grain
result = library.apply_grain(frame, intensity=0.4)
```

#### Particle Systems

```python
# Create confetti particles
particles = library.create_confetti_particles(
    count=100,
    width=1920,
    height=1080
)

# Update physics (60 FPS)
particles = library.update_particles(
    particles,
    dt=1/60,
    width=1920,
    height=1080,
    gravity=980  # pixels/s²
)

# Render onto frame
result = library.render_particles(frame, particles)
```

#### Easing Functions

```python
from streaming.effects.library import apply_easing

# Available easing functions
progress = apply_easing(0.5, "ease-in-out")  # Smooth S-curve
progress = apply_easing(0.5, "ease-in")      # Accelerate
progress = apply_easing(0.5, "ease-out")     # Decelerate
progress = apply_easing(0.5, "linear")       # Constant speed
```

---

### 2. Scene Manager (`scenes.py`)

Manages debate flow and scene transitions.

#### Scene Types

- `INTRO` - Opening sequence (5s, auto-advance)
- `DEBATE_ROUND` - Main debate scene (indefinite)
- `VOTING` - Voting phase (10s, auto-advance)
- `RESULTS` - Results display (8s, auto-advance)
- `OUTRO` - Closing sequence (5s)
- `IDLE` - Between debates (indefinite)

#### Usage

```python
from streaming.effects import SceneManager, SceneType, create_debate_flow

manager = SceneManager()

# Get scene configuration
config = manager.get_scene(SceneType.INTRO)
print(f"Duration: {config.duration}s")
print(f"Elements: {len(config.elements)}")

# Start a scene
scene = manager.start_scene(SceneType.INTRO)

# Update scene (game loop)
while manager.update(dt=1/30):  # 30 FPS
    # Render current scene
    pass

# Transition to next scene
await manager.transition_to_scene(
    SceneType.DEBATE_ROUND,
    transition_type="zoom_in"
)
```

#### Custom Scenes

```python
from streaming.effects import SceneConfig, SceneElement

custom_scene = SceneConfig(
    scene_type=SceneType.DEBATE_ROUND,
    duration=None,  # Indefinite
    elements=[
        SceneElement(
            element_type="topic_banner",
            position=(960, 50),
            size=(1600, 80),
            content="Should AI Be Regulated?",
            layer=3
        ),
    ],
    background="solid",
    background_color=(30, 30, 30),
    transition_in="fade",
    transition_out="slide_up"
)

manager.add_scene(custom_scene)
```

---

### 3. Graphics Compositor (`graphics.py`)

Professional text and graphic overlays.

#### Lower Thirds

```python
compositor = GraphicsCompositor()

lower_third = compositor.create_lower_third(
    name="speaker",
    title="The Pragmatist",
    subtitle="System Architect",
    position=LayoutPosition.BOTTOM_LEFT,
    background_color=(0, 0, 0, 180),  # Semi-transparent black
    accent_color=(0, 120, 255, 255)   # Blue accent bar
)

compositor.add_layer(lower_third)
```

#### Topic Banners

```python
banner = compositor.create_topic_banner(
    name="topic",
    topic="Should AI Be Heavily Regulated?",
    position=LayoutPosition.TOP_CENTER,
    background_color=(20, 20, 40, 220),
    border_color=(100, 150, 255, 255)
)

compositor.add_layer(banner)
```

#### Timers

```python
timer = compositor.create_timer(
    name="timer",
    time_text="2:30",
    position=LayoutPosition.TOP_RIGHT,
    background_color=(40, 40, 40, 200),
    text_color=(255, 255, 255),
    warning_threshold=30,  # Turn orange below 30s
    warning_color=(255, 100, 0)
)

compositor.add_layer(timer)
```

#### Text Rendering

```python
from streaming.effects import TextStyle, FontWeight, TextAlignment

style = TextStyle(
    font_size=48,
    font_weight=FontWeight.BOLD,
    color=(255, 255, 255),
    alpha=255,
    outline_width=2,
    outline_color=(0, 0, 0),
    shadow_offset=(3, 3),
    shadow_color=(0, 0, 0, 128),
    alignment=TextAlignment.CENTER
)

text_img = compositor.render_text("AI Council Debate", style, max_width=800)
```

#### Layer Management

```python
# Add layer
compositor.add_layer(layer)

# Update layer properties
compositor.update_layer_alpha("speaker", 0.8)
compositor.update_layer_position("timer", (1800, 50))
compositor.set_layer_visibility("banner", False)

# Remove layer
compositor.remove_layer("speaker")

# Composite all visible layers
result = compositor.composite(base_frame)
```

---

### 4. Transition Engine (`transitions.py`)

High-level transition API.

```python
from streaming.effects import TransitionEngine, TransitionType, EasingFunction

engine = TransitionEngine()

# Apply transition with easing
result = await engine.apply_transition(
    frame_a,
    frame_b,
    transition_type=TransitionType.FADE,
    progress=0.5,
    easing=EasingFunction.EASE_IN_OUT
)

# Create animated transition sequence
frames = await engine.create_transition_sequence(
    frame_a,
    frame_b,
    transition_type=TransitionType.SLIDE_LEFT,
    duration=1.0,  # seconds
    fps=30
)

# Interpolate between frames at specific time
result = await engine.interpolate(
    frame_a,
    frame_b,
    transition_type=TransitionType.ZOOM_IN,
    time=0.5,  # seconds
    total_duration=2.0  # seconds
)
```

**Available Easing Functions:**
- `LINEAR` - Constant speed
- `EASE_IN` - Accelerate
- `EASE_OUT` - Decelerate
- `EASE_IN_OUT` - S-curve (smooth)
- `EASE_IN_QUAD/CUBIC/QUART/QUINT` - Polynomial curves
- `EASE_OUT_QUAD/CUBIC/QUART/QUINT`
- `EASE_IN_OUT_QUAD/CUBIC/QUART/QUINT`

---

### 5. Data Visualizations (`visualizations.py`)

Charts and metrics for debate data.

#### Bar Charts

```python
visualizer = DataVisualizer()

vote_data = {
    "Support": 45,
    "Oppose": 30,
    "Neutral": 15,
    "Abstain": 10
}

chart = visualizer.create_bar_chart(
    data=vote_data,
    title="Vote Distribution",
    width=800,
    height=500,
    colors=[(0, 120, 255), (255, 60, 60), (180, 180, 180), (120, 120, 120)]
)
```

#### Pie/Donut Charts

```python
pie = visualizer.create_pie_chart(
    data=vote_data,
    title="Vote Breakdown",
    width=600,
    height=600,
    donut=True,  # Donut chart
    donut_ratio=0.6
)
```

#### Gauges

```python
gauge = visualizer.create_gauge(
    value=75,
    max_value=100,
    label="Consensus Level",
    width=400,
    height=400,
    color=(0, 200, 100),
    warning_threshold=30,  # Turn orange below 30
    danger_threshold=10    # Turn red below 10
)
```

#### Confidence Meters

```python
meter = visualizer.create_confidence_meter(
    confidence=0.85,
    label="Agent Confidence",
    width=300,
    height=60
)
```

#### Vote Visualizations

```python
vote_viz = visualizer.create_vote_visualization(
    vote_data,
    show_percentages=True,
    show_counts=True,
    width=600,
    height=400
)
```

#### Metrics Display

```python
metrics = {
    "Total Votes": "1,247",
    "Consensus": "67%",
    "Duration": "12:34",
    "Participants": "5"
}

display = visualizer.create_metrics_display(
    metrics,
    title="Debate Statistics",
    width=400,
    height=600
)
```

#### Animated Counters

```python
# Create counter that animates from 0 to 1247
counter = visualizer.create_animated_counter(
    start_value=0,
    end_value=1247,
    duration=2.0,  # seconds
    prefix="Votes: "
)

# Render at specific time
frame = visualizer.render_counter(counter, elapsed_time=1.0)
```

---

## Integration with Debate System

### Complete Broadcast Pipeline

```python
from streaming.effects import (
    SceneManager,
    GraphicsCompositor,
    TransitionEngine,
    DataVisualizer,
)
from streaming.avatars import AvatarCompositor, LayoutMode

# Initialize components
scene_manager = SceneManager()
graphics = GraphicsCompositor()
transitions = TransitionEngine()
visualizer = DataVisualizer()
avatar_comp = AvatarCompositor(layout=LayoutMode.CAROUSEL)

# Start debate flow
scene = scene_manager.start_scene(SceneType.INTRO)

# Main loop
while True:
    # Update scene
    if not scene_manager.update(dt=1/30):
        # Scene complete, transition to next
        if scene.config.auto_advance and scene.config.next_scene:
            await scene_manager.transition_to_scene(scene.config.next_scene)

    # Get current scene
    current_scene = scene_manager.get_current_scene()

    # Render based on scene type
    if current_scene.config.scene_type == SceneType.DEBATE_ROUND:
        # Add graphics overlays
        graphics.add_layer(graphics.create_topic_banner("topic", debate_topic))
        graphics.add_layer(graphics.create_timer("timer", format_time(elapsed)))

        # Composite avatars
        frame = avatar_comp.overlay_multiple_avatars(
            base_frame,
            agent_avatars,
            active_speaker=current_speaker_index
        )

        # Add graphics
        frame = graphics.composite(frame)

    elif current_scene.config.scene_type == SceneType.VOTING:
        # Create vote visualization
        vote_viz = visualizer.create_vote_visualization(vote_data)

        # Composite everything
        frame = graphics.composite(base_frame)
        # Paste vote viz onto frame...

    # Stream frame...
```

---

## Performance Considerations

### Frame Rate

- Target: **30 FPS** for smooth playback
- Transition rendering: ~33ms per frame budget
- Graphics compositing: ~10-15ms overhead
- Data visualization: Pre-render and cache

### Optimization Tips

1. **Cache rendered graphics**
   ```python
   # Render once
   lower_third = compositor.create_lower_third(...)
   compositor.add_layer(lower_third)

   # Reuse for many frames
   for frame in video_stream:
       result = compositor.composite(frame)
   ```

2. **Pre-render visualizations**
   ```python
   # Render chart once
   chart = visualizer.create_bar_chart(vote_data)

   # Paste onto multiple frames
   ```

3. **Limit particle count**
   ```python
   # Good for 30 FPS
   particles = library.create_confetti_particles(count=100)

   # Too many for real-time
   # particles = library.create_confetti_particles(count=1000)
   ```

4. **Use appropriate image sizes**
   ```python
   # Full HD
   compositor = GraphicsCompositor(1920, 1080)

   # Or lower resolution for faster processing
   compositor = GraphicsCompositor(1280, 720)
   ```

---

## Best Practices

### 1. Scene Flow

```python
# DO: Use predefined scene flows
flow = create_debate_flow()  # [INTRO, DEBATE, VOTING, RESULTS, OUTRO]

# DON'T: Manually manage every transition
```

### 2. Layer Organization

```python
# DO: Use appropriate z-index layers
lower_third.z_index = 10   # Bottom
banner.z_index = 20        # Middle
timer.z_index = 30         # Top

# DON'T: Use same z-index for everything
```

### 3. Transition Selection

```python
# DO: Match transitions to content
intro → debate: zoom_in  # Energetic entry
debate → voting: wipe_up  # Clean separation
results → outro: fade     # Gentle exit

# DON'T: Use jarring transitions
```

### 4. Graphics Readability

```python
# DO: High contrast text
TextStyle(
    color=(255, 255, 255),
    outline_width=2,
    outline_color=(0, 0, 0)
)

# DON'T: Low contrast
TextStyle(color=(180, 180, 180))  # Hard to read
```

---

## Demo Application

Run the comprehensive demo:

```bash
cd /workspace/projects/ai-council-system
python examples/effects_demo.py
```

**Demo includes:**
1. All 13 transition types
2. Overlay effects (vignette, blur, glow, grain)
3. Particle systems (confetti, sparkles)
4. Graphics overlays (lower thirds, banners, timers)
5. Data visualizations (bar, pie, gauge)
6. Scene management flow
7. Integrated broadcast pipeline

**Output:** `demo_output/effects_*.png`

---

## Dependencies

```
# Core
Pillow>=10.2.0
numpy>=1.24.0

# Optional (for enhanced features)
opencv-python>=4.9.0  # Video processing
```

---

## API Reference Summary

### EffectLibrary
- `apply_fade(frame_a, frame_b, progress)` - Fade transition
- `apply_wipe(frame_a, frame_b, progress, direction)` - Wipe transition
- `apply_slide(frame_a, frame_b, progress, direction)` - Slide transition
- `apply_zoom(frame_a, frame_b, progress, zoom_in)` - Zoom transition
- `apply_vignette(frame, intensity)` - Vignette overlay
- `apply_blur(frame, intensity)` - Blur overlay
- `apply_glow(frame, intensity, color)` - Glow overlay
- `apply_grain(frame, intensity)` - Film grain
- `create_confetti_particles(count, width, height)` - Confetti
- `render_particles(frame, particles)` - Render particles

### SceneManager
- `get_scene(scene_type)` - Get scene config
- `add_scene(config)` - Add custom scene
- `start_scene(scene_type)` - Start a scene
- `transition_to_scene(scene_type, transition)` - Transition
- `update(dt)` - Update scene state
- `get_current_scene()` - Get active scene

### GraphicsCompositor
- `create_lower_third(name, title, subtitle)` - Lower third
- `create_topic_banner(name, topic)` - Topic banner
- `create_timer(name, time_text)` - Timer display
- `render_text(text, style, max_width)` - Render text
- `add_layer(layer)` - Add graphics layer
- `composite(base_frame)` - Composite all layers

### DataVisualizer
- `create_bar_chart(data, title, width, height)` - Bar chart
- `create_pie_chart(data, title, width, height)` - Pie chart
- `create_gauge(value, max_value, label)` - Gauge
- `create_confidence_meter(confidence, label)` - Confidence meter
- `create_vote_visualization(data)` - Vote display
- `create_metrics_display(metrics, title)` - Metrics panel

---

## Future Enhancements

- [ ] 3D transitions (cube rotate, flip)
- [ ] Chroma keying (green screen)
- [ ] Advanced particle physics
- [ ] Motion blur effects
- [ ] Real-time GPU acceleration
- [ ] Custom shader support

---

**Last Updated**: Phase 4.2 Complete
**Version**: 1.0.0
**Status**: ✅ Production Ready
