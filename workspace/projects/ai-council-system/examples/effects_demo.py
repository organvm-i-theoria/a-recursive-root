#!/usr/bin/env python3
"""
Advanced Video Effects Demo

Demonstrates the AI Council advanced video effects system:
- 13 transition effects with easing functions
- Overlay effects (vignette, blur, glow, grain)
- Particle systems (confetti, sparkles)
- Graphics overlays (lower thirds, banners, timers)
- Data visualizations (charts, gauges, vote displays)
- Scene management (full debate flow)
- Complete integrated workflow
"""

import asyncio
import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from streaming.effects import (
    EffectLibrary,
    SceneManager,
    SceneType,
    GraphicsCompositor,
    LayoutPosition,
    TextStyle,
    FontWeight,
    TransitionEngine,
    TransitionType,
    TransitionConfig,
    EasingFunction,
    DataVisualizer,
    ChartType,
    ChartData,
)

try:
    from PIL import Image
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("WARNING: PIL not available. Install with: pip install Pillow numpy")


def create_test_frame(color: tuple, text: str = "") -> np.ndarray:
    """Create a test frame with solid color and optional text"""
    frame = np.ones((1080, 1920, 3), dtype=np.uint8)
    frame[:, :, 0] = color[0]
    frame[:, :, 1] = color[1]
    frame[:, :, 2] = color[2]

    if text and PIL_AVAILABLE:
        img = Image.fromarray(frame)
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)

        # Try to load a font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        except:
            font = ImageFont.load_default()

        # Draw text centered
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (1920 - text_width) // 2
        y = (1080 - text_height) // 2

        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        frame = np.array(img)

    return frame


async def demo_transitions():
    """Demo 1: All 13 transition types"""
    print("\n" + "=" * 70)
    print("DEMO 1: Transition Effects (13 Types)")
    print("=" * 70 + "\n")

    if not PIL_AVAILABLE:
        print("⚠️  Skipping (PIL not available)\n")
        return

    # Create transition engine
    engine = TransitionEngine()

    # Create test frames
    frame_a = create_test_frame((50, 50, 150), "FRAME A")
    frame_b = create_test_frame((150, 50, 50), "FRAME B")

    # Test all transition types
    transitions = [
        (TransitionType.FADE, "Fade transition"),
        (TransitionType.CROSS_FADE, "Cross-fade transition"),
        (TransitionType.WIPE_LEFT, "Wipe left"),
        (TransitionType.WIPE_RIGHT, "Wipe right"),
        (TransitionType.WIPE_UP, "Wipe up"),
        (TransitionType.WIPE_DOWN, "Wipe down"),
        (TransitionType.SLIDE_LEFT, "Slide left"),
        (TransitionType.SLIDE_RIGHT, "Slide right"),
        (TransitionType.SLIDE_UP, "Slide up"),
        (TransitionType.SLIDE_DOWN, "Slide down"),
        (TransitionType.ZOOM_IN, "Zoom in"),
        (TransitionType.ZOOM_OUT, "Zoom out"),
        (TransitionType.ROTATE, "Rotate transition"),
    ]

    Path("demo_output").mkdir(exist_ok=True)

    for i, (transition_type, description) in enumerate(transitions, 1):
        print(f"{i}. {description}")

        # Create transition config
        config = TransitionConfig(
            transition_type=transition_type,
            duration=1.0,
            easing=EasingFunction.EASE_IN_OUT
        )

        # Apply transition at 50% progress
        result = engine.apply_transition(frame_a, frame_b, config, progress=0.5)

        # Save result
        output_file = f"demo_output/effects_transition_{transition_type.value}.png"
        img = Image.fromarray(result)
        img.save(output_file)
        print(f"   ✓ Saved to: {output_file}\n")

    print(f"✅ Generated {len(transitions)} transition effects\n")


async def demo_overlays():
    """Demo 2: Overlay effects"""
    print("\n" + "=" * 70)
    print("DEMO 2: Overlay Effects")
    print("=" * 70 + "\n")

    if not PIL_AVAILABLE:
        print("⚠️  Skipping (PIL not available)\n")
        return

    # Create effect library
    lib = EffectLibrary()

    # Create base frame
    base_frame = create_test_frame((80, 120, 160), "Base Frame")

    Path("demo_output").mkdir(exist_ok=True)

    # Test overlay effects
    overlays = [
        ("vignette", lambda f: lib.apply_vignette(f, intensity=0.7)),
        ("blur", lambda f: lib.apply_blur(f, intensity=0.5)),
        ("glow", lambda f: lib.apply_glow(f, intensity=0.6, color=(100, 150, 255))),
        ("grain", lambda f: lib.apply_grain(f, intensity=0.3)),
    ]

    for i, (name, apply_func) in enumerate(overlays, 1):
        print(f"{i}. {name.capitalize()} effect")

        # Apply effect
        result = apply_func(base_frame.copy())

        # Save result
        output_file = f"demo_output/effects_overlay_{name}.png"
        img = Image.fromarray(result)
        img.save(output_file)
        print(f"   ✓ Saved to: {output_file}\n")

    print(f"✅ Generated {len(overlays)} overlay effects\n")


async def demo_particles():
    """Demo 3: Particle systems"""
    print("\n" + "=" * 70)
    print("DEMO 3: Particle Systems")
    print("=" * 70 + "\n")

    if not PIL_AVAILABLE:
        print("⚠️  Skipping (PIL not available)\n")
        return

    # Create effect library
    lib = EffectLibrary()

    # Create base frame
    base_frame = create_test_frame((40, 40, 60), "")

    Path("demo_output").mkdir(exist_ok=True)

    # 1. Confetti particles
    print("1. Confetti particles")
    particles = lib.create_confetti_particles(100, 1920, 1080)

    # Update particles a few times
    for _ in range(20):
        particles = lib.update_particles(particles, 0.05, 1920, 1080, gravity=300)

    # Render particles
    result = lib.render_particles(base_frame.copy(), particles)
    output_file = "demo_output/effects_particles_confetti.png"
    img = Image.fromarray(result)
    img.save(output_file)
    print(f"   ✓ Saved to: {output_file}\n")

    # 2. Sparkle particles
    print("2. Sparkle particles")
    particles = lib.create_sparkle_particles(150, 1920, 1080)
    result = lib.render_particles(base_frame.copy(), particles)
    output_file = "demo_output/effects_particles_sparkles.png"
    img = Image.fromarray(result)
    img.save(output_file)
    print(f"   ✓ Saved to: {output_file}\n")

    print("✅ Generated 2 particle effects\n")


async def demo_graphics():
    """Demo 4: Graphics overlays"""
    print("\n" + "=" * 70)
    print("DEMO 4: Graphics Overlays")
    print("=" * 70 + "\n")

    if not PIL_AVAILABLE:
        print("⚠️  Skipping (PIL not available)\n")
        return

    # Create graphics compositor
    compositor = GraphicsCompositor(1920, 1080)

    # Create base frame
    base_frame = create_test_frame((30, 30, 30), "")

    Path("demo_output").mkdir(exist_ok=True)

    # 1. Lower third
    print("1. Lower third graphic")
    lower_third = compositor.create_lower_third(
        name="speaker_lt",
        title="The Pragmatist",
        subtitle="System Architect",
        position=LayoutPosition.BOTTOM_LEFT
    )
    compositor.add_layer(lower_third)
    result = compositor.composite(base_frame.copy())
    compositor.remove_layer("speaker_lt")

    output_file = "demo_output/effects_graphics_lower_third.png"
    img = Image.fromarray(result)
    img.save(output_file)
    print(f"   ✓ Saved to: {output_file}\n")

    # 2. Topic banner
    print("2. Topic banner")
    banner = compositor.create_topic_banner(
        name="topic",
        topic="Should AI be regulated by governments?",
        position=LayoutPosition.TOP_CENTER
    )
    compositor.add_layer(banner)
    result = compositor.composite(base_frame.copy())
    compositor.remove_layer("topic")

    output_file = "demo_output/effects_graphics_banner.png"
    img = Image.fromarray(result)
    img.save(output_file)
    print(f"   ✓ Saved to: {output_file}\n")

    # 3. Timer
    print("3. Timer display")
    timer = compositor.create_timer(
        name="timer",
        time_text="2:30",
        position=LayoutPosition.TOP_RIGHT
    )
    compositor.add_layer(timer)
    result = compositor.composite(base_frame.copy())
    compositor.remove_layer("timer")

    output_file = "demo_output/effects_graphics_timer.png"
    img = Image.fromarray(result)
    img.save(output_file)
    print(f"   ✓ Saved to: {output_file}\n")

    # 4. Combined graphics
    print("4. Combined graphics overlay")
    compositor.add_layer(lower_third)
    compositor.add_layer(banner)
    compositor.add_layer(timer)
    result = compositor.composite(base_frame.copy())

    output_file = "demo_output/effects_graphics_combined.png"
    img = Image.fromarray(result)
    img.save(output_file)
    print(f"   ✓ Saved to: {output_file}\n")

    print("✅ Generated 4 graphics overlays\n")


async def demo_visualizations():
    """Demo 5: Data visualizations"""
    print("\n" + "=" * 70)
    print("DEMO 5: Data Visualizations")
    print("=" * 70 + "\n")

    if not PIL_AVAILABLE:
        print("⚠️  Skipping (PIL not available)\n")
        return

    # Create visualizer
    visualizer = DataVisualizer(1200, 800)

    Path("demo_output").mkdir(exist_ok=True)

    # Test data
    vote_data = ChartData(
        labels=["Support", "Oppose", "Neutral"],
        values=[45, 30, 25],
        title="Vote Distribution"
    )

    agent_data = ChartData(
        labels=["Pragmatist", "Idealist", "Skeptic", "Visionary", "Mediator"],
        values=[85, 72, 91, 68, 79],
        title="Agent Performance Scores"
    )

    # 1. Horizontal bar chart
    print("1. Horizontal bar chart (vote distribution)")
    img = visualizer.render_horizontal_bar_chart(vote_data, animation_progress=1.0)
    output_file = "demo_output/effects_viz_hbar.png"
    img.save(output_file)
    print(f"   ✓ Saved to: {output_file}\n")

    # 2. Vertical bar chart
    print("2. Vertical bar chart (agent scores)")
    img = visualizer.render_bar_chart(agent_data, animation_progress=1.0)
    output_file = "demo_output/effects_viz_vbar.png"
    img.save(output_file)
    print(f"   ✓ Saved to: {output_file}\n")

    # 3. Pie chart
    print("3. Pie chart (vote distribution)")
    img = visualizer.render_pie_chart(vote_data, animation_progress=1.0)
    output_file = "demo_output/effects_viz_pie.png"
    img.save(output_file)
    print(f"   ✓ Saved to: {output_file}\n")

    # 4. Donut chart
    print("4. Donut chart (vote distribution)")
    img = visualizer.render_pie_chart(vote_data, donut=True, animation_progress=1.0)
    output_file = "demo_output/effects_viz_donut.png"
    img.save(output_file)
    print(f"   ✓ Saved to: {output_file}\n")

    # 5. Gauge
    print("5. Gauge chart (consensus level)")
    img = visualizer.render_gauge(
        value=75,
        max_value=100,
        label="Consensus Level",
        animation_progress=1.0
    )
    output_file = "demo_output/effects_viz_gauge.png"
    img.save(output_file)
    print(f"   ✓ Saved to: {output_file}\n")

    # 6. Confidence meter
    print("6. Confidence meter")
    img = visualizer.render_confidence_meter(
        confidence=0.85,
        agent_name="The Pragmatist",
        animation_progress=1.0
    )
    output_file = "demo_output/effects_viz_confidence.png"
    img.save(output_file)
    print(f"   ✓ Saved to: {output_file}\n")

    # 7. Metrics display
    print("7. Metrics display")
    metrics = {
        "Total Votes": 1247,
        "Consensus": "68%",
        "Duration": "8:45",
        "Viewers": "3.2K"
    }
    img = visualizer.render_metrics_display(metrics)
    output_file = "demo_output/effects_viz_metrics.png"
    img.save(output_file)
    print(f"   ✓ Saved to: {output_file}\n")

    print("✅ Generated 7 data visualizations\n")


async def demo_scene_management():
    """Demo 6: Scene management"""
    print("\n" + "=" * 70)
    print("DEMO 6: Scene Management (Full Debate Flow)")
    print("=" * 70 + "\n")

    # Create scene manager
    manager = SceneManager()

    # Show all available scenes
    print("Available scenes:")
    scenes = [
        SceneType.INTRO,
        SceneType.DEBATE_ROUND,
        SceneType.VOTING,
        SceneType.RESULTS,
        SceneType.OUTRO,
        SceneType.IDLE
    ]

    for i, scene_type in enumerate(scenes, 1):
        config = manager.get_scene(scene_type)
        print(f"{i}. {scene_type.value.upper()}")
        print(f"   Duration: {config.duration}s" if config.duration else "   Duration: Indefinite")
        print(f"   Elements: {len(config.elements)}")
        print(f"   Background: {config.background}")
        print(f"   Transition in: {config.transition_in}")
        print(f"   Transition out: {config.transition_out}")
        if config.auto_advance:
            print(f"   Auto-advance to: {config.next_scene.value if config.next_scene else 'None'}")
        print()

    # Simulate scene flow
    print("Simulating debate scene flow:\n")

    flow_scenes = [
        (SceneType.INTRO, 5.0),
        (SceneType.DEBATE_ROUND, 3.0),
        (SceneType.VOTING, 10.0),
        (SceneType.RESULTS, 8.0),
        (SceneType.OUTRO, 5.0),
    ]

    for scene_type, duration in flow_scenes:
        scene = manager.start_scene(scene_type)
        print(f"▶ Started: {scene_type.value.upper()}")

        # Simulate scene running
        elapsed = 0.0
        dt = 0.5
        while elapsed < duration:
            scene.update(dt)
            elapsed += dt

        scene.stop()
        print(f"  Elapsed: {scene.elapsed_time:.1f}s")
        print(f"  Progress: {scene.get_progress() * 100:.0f}%")
        print()

    # Show scene history
    print("Scene history:")
    for i, scene_type in enumerate(manager.get_scene_history(), 1):
        print(f"  {i}. {scene_type.value}")

    print("\n✅ Scene management demo complete\n")


async def demo_integrated_workflow():
    """Demo 7: Complete integrated workflow"""
    print("\n" + "=" * 70)
    print("DEMO 7: Integrated Workflow (Complete Broadcast)")
    print("=" * 70 + "\n")

    if not PIL_AVAILABLE:
        print("⚠️  Skipping (PIL not available)\n")
        return

    print("Simulating a complete broadcast workflow:\n")

    # Initialize all components
    effect_lib = EffectLibrary()
    transition_engine = TransitionEngine()
    compositor = GraphicsCompositor(1920, 1080)
    visualizer = DataVisualizer(1200, 800)
    scene_manager = SceneManager()

    Path("demo_output").mkdir(exist_ok=True)

    # Scene 1: Intro
    print("1. INTRO SCENE")
    print("   - Create intro frame with title")
    intro_frame = create_test_frame((20, 40, 80), "AI COUNCIL")
    output_file = "demo_output/effects_workflow_01_intro.png"
    Image.fromarray(intro_frame).save(output_file)
    print(f"   ✓ Saved: {output_file}\n")

    # Scene 2: Debate round with graphics
    print("2. DEBATE ROUND SCENE")
    print("   - Add topic banner")
    print("   - Add timer")
    print("   - Add lower third for speaker")

    debate_frame = create_test_frame((30, 30, 30), "")

    # Add graphics
    compositor.clear_all_layers()
    banner = compositor.create_topic_banner(
        "topic", "Should AI replace human judges?", LayoutPosition.TOP_CENTER
    )
    timer = compositor.create_timer("timer", "5:00", LayoutPosition.TOP_RIGHT)
    lower_third = compositor.create_lower_third(
        "speaker", "The Idealist", "Moral Philosopher", LayoutPosition.BOTTOM_LEFT
    )

    compositor.add_layer(banner)
    compositor.add_layer(timer)
    compositor.add_layer(lower_third)

    debate_frame = compositor.composite(debate_frame)
    output_file = "demo_output/effects_workflow_02_debate.png"
    Image.fromarray(debate_frame).save(output_file)
    print(f"   ✓ Saved: {output_file}\n")

    # Scene 3: Transition to voting
    print("3. TRANSITION TO VOTING")
    print("   - Apply wipe transition")

    voting_base = create_test_frame((40, 20, 60), "")
    config = TransitionConfig(
        transition_type=TransitionType.WIPE_UP,
        duration=1.0,
        easing=EasingFunction.EASE_IN_OUT
    )
    transition_frame = transition_engine.apply_transition(
        debate_frame, voting_base, config, progress=0.5
    )
    output_file = "demo_output/effects_workflow_03_transition.png"
    Image.fromarray(transition_frame).save(output_file)
    print(f"   ✓ Saved: {output_file}\n")

    # Scene 4: Voting results
    print("4. VOTING RESULTS SCENE")
    print("   - Generate vote visualization")
    print("   - Add confetti particles")

    # Create vote visualization
    vote_data = ChartData(
        labels=["Support", "Oppose", "Neutral"],
        values=[52, 38, 10],
        title="Final Vote Results"
    )
    vote_viz = visualizer.render_pie_chart(vote_data, width=800, height=600, donut=True)

    # Convert to numpy and resize/position
    vote_viz_array = np.array(vote_viz.convert('RGB'))

    # Add particles for celebration
    particles = effect_lib.create_confetti_particles(200, 1920, 1080)
    for _ in range(30):
        particles = effect_lib.update_particles(particles, 0.03, 1920, 1080, gravity=400)

    # Composite everything
    voting_frame = create_test_frame((30, 30, 40), "")

    # Add visualization (centered)
    viz_h, viz_w = vote_viz_array.shape[:2]
    y_offset = (1080 - viz_h) // 2
    x_offset = (1920 - viz_w) // 2
    voting_frame[y_offset:y_offset+viz_h, x_offset:x_offset+viz_w] = vote_viz_array

    # Add particles
    voting_frame = effect_lib.render_particles(voting_frame, particles)

    output_file = "demo_output/effects_workflow_04_results.png"
    Image.fromarray(voting_frame).save(output_file)
    print(f"   ✓ Saved: {output_file}\n")

    # Scene 5: Outro with fade
    print("5. OUTRO SCENE")
    print("   - Apply fade transition")

    outro_frame = create_test_frame((20, 20, 40), "THANK YOU")
    config = TransitionConfig(
        transition_type=TransitionType.FADE,
        duration=1.5,
        easing=EasingFunction.EASE_OUT
    )
    outro_transition = transition_engine.apply_transition(
        voting_frame, outro_frame, config, progress=0.7
    )
    output_file = "demo_output/effects_workflow_05_outro.png"
    Image.fromarray(outro_transition).save(output_file)
    print(f"   ✓ Saved: {output_file}\n")

    print("✅ Complete broadcast workflow generated\n")
    print("Workflow summary:")
    print("  - 5 scenes created")
    print("  - 3 graphics overlays")
    print("  - 2 transitions")
    print("  - 1 data visualization")
    print("  - 200 particle effects")
    print("  - All output saved to demo_output/\n")


async def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  AI COUNCIL EFFECTS SYSTEM - COMPREHENSIVE DEMO".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    try:
        # Run all demos
        await demo_transitions()
        await demo_overlays()
        await demo_particles()
        await demo_graphics()
        await demo_visualizations()
        await demo_scene_management()
        await demo_integrated_workflow()

        print("\n" + "=" * 70)
        print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nOutput files saved to: ./demo_output/")
        print("\nGenerated files:")
        print("  - 13 transition effects")
        print("  - 4 overlay effects")
        print("  - 2 particle systems")
        print("  - 4 graphics overlays")
        print("  - 7 data visualizations")
        print("  - 5 workflow stages")
        print("\nTotal: 35+ demo output files")
        print("\nNext steps:")
        print("  - Integrate with debate system")
        print("  - Add real-time streaming")
        print("  - Customize scene templates")
        print("  - Experiment with easing functions")
        print()

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
