#!/usr/bin/env python3
"""
Avatar System Demo

Demonstrates the AI Council avatar generation and composition system:
- Avatar generation for all 15 personalities
- Expression mapping based on sentiment
- Video composition with multiple layout modes
- Cache system
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from streaming.avatars import (
    AvatarGenerator,
    AvatarProvider,
    AvatarSize,
    ExpressionEngine,
    SentimentType,
    AvatarCompositor,
    LayoutMode,
    AvatarCache,
    get_personality_traits,
    get_all_personality_names,
)

try:
    from PIL import Image
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("WARNING: PIL not available. Install with: pip install Pillow numpy")


async def demo_avatar_generation():
    """Demo: Generate avatars for all personalities"""
    print("\n" + "=" * 70)
    print("DEMO 1: Avatar Generation")
    print("=" * 70 + "\n")

    # Create generator (using mock for demo)
    generator = AvatarGenerator(
        provider=AvatarProvider.MOCK,
        default_size=AvatarSize.MEDIUM,
        quality="high",
        cache_dir="./demo_avatar_cache"
    )

    # Generate avatars for first 5 personalities
    personalities = get_all_personality_names()[:5]

    print(f"Generating avatars for {len(personalities)} personalities...")
    print()

    avatars = []
    for i, personality in enumerate(personalities, 1):
        print(f"{i}. Generating avatar for '{personality}'...")

        # Get personality traits
        traits = get_personality_traits(personality)
        print(f"   Style: {traits.style.value}")
        print(f"   Colors: {', '.join(traits.colors)}")
        print(f"   Mood: {traits.mood}")

        # Generate avatar
        avatar = await generator.generate_avatar(
            personality=personality,
            size=AvatarSize.MEDIUM
        )

        print(f"   ✓ Generated {len(avatar.image_data)} bytes")
        print()

        avatars.append(avatar)

        # Save to file
        output_file = f"demo_output/avatar_{personality}.png"
        Path("demo_output").mkdir(exist_ok=True)
        avatar.save(output_file)
        print(f"   Saved to: {output_file}\n")

    print(f"✅ Generated {len(avatars)} avatars\n")
    return avatars


async def demo_expression_engine():
    """Demo: Expression mapping and animations"""
    print("\n" + "=" * 70)
    print("DEMO 2: Expression Engine")
    print("=" * 70 + "\n")

    engine = ExpressionEngine()

    # Test different sentiments
    test_cases = [
        ("I strongly agree with this proposal!", "pragmatist"),
        ("This is deeply concerning and problematic.", "skeptic"),
        ("Perhaps we should consider alternative approaches?", "mediator"),
        ("This will revolutionize everything!", "visionary"),
        ("The data clearly shows...", "analyst"),
    ]

    print("Analyzing text sentiment and generating expressions:\n")

    for text, personality in test_cases:
        print(f"Text: \"{text}\"")
        print(f"Personality: {personality}")

        # Analyze sentiment
        sentiment, confidence = engine.analyze_text_sentiment(text)
        print(f"Detected: {sentiment.value} (confidence: {confidence:.2f})")

        # Get expression
        expression = engine.get_expression_for_sentiment(
            sentiment, confidence, personality
        )
        print(f"Expression: {expression.value}")

        # Create animation
        animation = await engine.create_expression_animation(
            sentiment=sentiment,
            duration=3.0,
            confidence=confidence,
            personality=personality
        )

        print(f"Animation: {len(animation.frames)} frames, {animation.total_duration}s")
        print()

    print("✅ Expression analysis complete\n")


async def demo_compositor():
    """Demo: Video composition with multiple layouts"""
    if not PIL_AVAILABLE:
        print("\n⚠️  Skipping compositor demo (PIL not available)\n")
        return

    print("\n" + "=" * 70)
    print("DEMO 3: Avatar Compositor")
    print("=" * 70 + "\n")

    # Generate avatars
    generator = AvatarGenerator(provider=AvatarProvider.MOCK)
    personalities = get_all_personality_names()[:5]

    print(f"Generating {len(personalities)} avatars...")
    avatars = []
    for personality in personalities:
        avatar = await generator.generate_avatar(personality, AvatarSize.MEDIUM)
        avatars.append(avatar)

    print(f"✓ Generated {len(avatars)} avatars\n")

    # Create blank video frame (1920x1080)
    frame = np.ones((1080, 1920, 3), dtype=np.uint8) * 50  # Dark gray background

    # Test different layout modes
    layouts = [
        LayoutMode.GRID,
        LayoutMode.CAROUSEL,
        LayoutMode.SPOTLIGHT,
        LayoutMode.STACK,
        LayoutMode.CIRCLE,
    ]

    Path("demo_output").mkdir(exist_ok=True)

    for layout in layouts:
        print(f"Creating composition with {layout.value} layout...")

        compositor = AvatarCompositor(
            config=CompositorConfig(
                layout_mode=layout,
                avatar_size=150,
                show_names=True,
                rounded_corners=True,
                shadow=True,
            )
        )

        # Overlay avatars (speaker is index 2)
        composed_frame = await compositor.overlay_multiple_avatars(
            frame.copy(),
            avatars,
            active_speaker=2
        )

        # Save composed frame
        output_file = f"demo_output/composition_{layout.value}.png"
        img = Image.fromarray(composed_frame)
        img.save(output_file)
        print(f"✓ Saved to: {output_file}\n")

    print("✅ Compositor demo complete\n")


async def demo_cache_system():
    """Demo: Avatar cache system"""
    print("\n" + "=" * 70)
    print("DEMO 4: Cache System")
    print("=" * 70 + "\n")

    # Create cache
    cache = AvatarCache(
        cache_dir="./demo_avatar_cache",
        max_size_mb=10,
        max_age_days=30
    )

    print("Cache initialized\n")

    # Generate and cache avatars
    generator = AvatarGenerator(provider=AvatarProvider.MOCK)

    for i in range(3):
        personality = "pragmatist"
        print(f"Attempt {i+1}: Generating avatar for '{personality}'...")

        # Try to get from cache first
        cached_avatar = await cache.get(
            personality=personality,
            provider=AvatarProvider.MOCK,
            size=AvatarSize.MEDIUM,
            prompt="test_prompt"
        )

        if cached_avatar:
            print("✓ Retrieved from cache!")
        else:
            print("× Cache miss, generating new avatar...")
            avatar = await generator.generate_avatar(personality)
            await cache.put(avatar, "test_prompt")
            print("✓ Generated and cached")

        print()

    # Show cache stats
    stats = await cache.get_stats()
    print("Cache Statistics:")
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  Total size: {stats['total_size_mb']:.2f} MB")
    print(f"  Utilization: {stats['utilization']*100:.1f}%")
    print(f"  Total accesses: {stats['total_accesses']}")
    print(f"  Avg accesses per entry: {stats['avg_accesses']:.1f}")
    print()

    # List entries
    entries = await cache.list_entries()
    print(f"Cache entries ({len(entries)}):")
    for entry in entries:
        print(f"  - {entry.personality} ({entry.size}) [accessed {entry.access_count} times]")

    print("\n✅ Cache demo complete\n")


async def demo_integrated_workflow():
    """Demo: Complete integrated workflow"""
    print("\n" + "=" * 70)
    print("DEMO 5: Integrated Workflow")
    print("=" * 70 + "\n")

    print("Simulating a complete debate with avatars:\n")

    # Create components
    generator = AvatarGenerator(provider=AvatarProvider.MOCK, cache_dir="./demo_avatar_cache")
    engine = ExpressionEngine()

    # Simulate council debate
    council_members = [
        ("pragmatist", "Let's focus on practical solutions that work."),
        ("idealist", "We must consider the moral implications!"),
        ("skeptic", "I question whether that approach will work."),
        ("visionary", "Imagine the transformative possibilities!"),
        ("mediator", "Perhaps we can find common ground here."),
    ]

    print("📊 Council Debate Simulation\n")

    avatars = []
    for i, (personality, statement) in enumerate(council_members, 1):
        print(f"{i}. {personality.upper()}")
        print(f'   Statement: "{statement}"')

        # Generate avatar
        avatar = await generator.generate_avatar(personality)
        avatars.append(avatar)

        # Analyze sentiment
        sentiment, confidence = engine.analyze_text_sentiment(statement)
        print(f"   Sentiment: {sentiment.value} ({confidence:.2f})")

        # Get expression
        expression = engine.get_expression_for_sentiment(sentiment, confidence, personality)
        print(f"   Expression: {expression.value}")
        print()

    if PIL_AVAILABLE:
        print("Creating debate visualization...")

        # Create video frame
        frame = np.ones((1080, 1920, 3), dtype=np.uint8) * 30

        # Create compositor
        from streaming.avatars.compositor import CompositorConfig
        compositor = AvatarCompositor(
            config=CompositorConfig(
                layout_mode=LayoutMode.CAROUSEL,
                avatar_size=180,
                show_names=True,
                rounded_corners=True,
            )
        )

        # Compose frame with all avatars
        composed = await compositor.overlay_multiple_avatars(
            frame,
            avatars,
            active_speaker=0  # Pragmatist is speaking
        )

        # Save
        Path("demo_output").mkdir(exist_ok=True)
        output_file = "demo_output/debate_visualization.png"
        img = Image.fromarray(composed)
        img.save(output_file)
        print(f"✓ Saved visualization to: {output_file}\n")

    print("✅ Integrated workflow complete\n")


async def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  AI COUNCIL AVATAR SYSTEM - COMPREHENSIVE DEMO".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    try:
        # Run all demos
        await demo_avatar_generation()
        await demo_expression_engine()
        await demo_compositor()
        await demo_cache_system()
        await demo_integrated_workflow()

        print("\n" + "=" * 70)
        print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nOutput files saved to: ./demo_output/")
        print("\nNext steps:")
        print("  - Try different avatar providers (DALL-E, Stable Diffusion)")
        print("  - Integrate with debate system")
        print("  - Add real-time video streaming")
        print("  - Experiment with different layouts and expressions")
        print()

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    # Import here to avoid circular imports
    from streaming.avatars.compositor import CompositorConfig

    exit_code = asyncio.run(main())
    sys.exit(exit_code)
