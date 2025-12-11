"""
Scene Management System

Manages different scenes in the debate flow with automatic transitions and timing.
"""

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Callable, Any
import logging
import time

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

logger = logging.getLogger(__name__)


class SceneType(str, Enum):
    """Available scene types"""
    INTRO = "intro"
    DEBATE_ROUND = "debate_round"
    VOTING = "voting"
    RESULTS = "results"
    OUTRO = "outro"
    TRANSITION = "transition"
    IDLE = "idle"


@dataclass
class SceneElement:
    """Element within a scene"""
    element_type: str  # "logo", "title", "subtitle", "avatar", "timer", etc.
    position: tuple  # (x, y)
    size: tuple  # (width, height)
    content: Any  # Element content (text, image path, etc.)
    animation: Optional[str] = None  # Animation name
    duration: Optional[float] = None  # Element duration (None = scene duration)
    layer: int = 0  # Z-index for layering


@dataclass
class SceneConfig:
    """Configuration for a scene"""
    scene_type: SceneType
    duration: Optional[float] = None  # None = indefinite
    elements: List[SceneElement] = field(default_factory=list)
    background: str = "solid"  # "solid", "gradient", "image", "animated"
    background_color: tuple = (30, 30, 30)  # RGB
    music: Optional[str] = None  # Background music file
    transition_in: str = "fade"  # Transition when entering scene
    transition_out: str = "fade"  # Transition when exiting scene
    transition_duration: float = 1.0  # Transition duration in seconds
    auto_advance: bool = False  # Auto advance to next scene
    next_scene: Optional[SceneType] = None


class Scene:
    """
    Represents a single scene in the broadcast

    A scene contains elements (graphics, text, avatars) and manages their lifecycle.
    """

    def __init__(self, config: SceneConfig):
        """
        Initialize scene

        Args:
            config: Scene configuration
        """
        self.config = config
        self.start_time: Optional[float] = None
        self.elapsed_time: float = 0.0
        self.is_active: bool = False
        self.elements_by_layer: Dict[int, List[SceneElement]] = {}

        # Organize elements by layer
        for element in config.elements:
            layer = element.layer
            if layer not in self.elements_by_layer:
                self.elements_by_layer[layer] = []
            self.elements_by_layer[layer].append(element)

    def start(self):
        """Start the scene"""
        self.start_time = time.time()
        self.is_active = True
        logger.info(f"Scene {self.config.scene_type.value} started")

    def stop(self):
        """Stop the scene"""
        self.is_active = False
        logger.info(f"Scene {self.config.scene_type.value} stopped after {self.elapsed_time:.1f}s")

    def update(self, dt: float) -> bool:
        """
        Update scene state

        Args:
            dt: Delta time since last update

        Returns:
            True if scene should continue, False if complete
        """
        if not self.is_active:
            return False

        self.elapsed_time += dt

        # Check if scene duration expired
        if self.config.duration and self.elapsed_time >= self.config.duration:
            if self.config.auto_advance:
                return False  # Scene complete, advance

        return True

    def get_active_elements(self) -> List[SceneElement]:
        """Get elements that should be displayed at current time"""
        active = []

        for layer in sorted(self.elements_by_layer.keys()):
            for element in self.elements_by_layer[layer]:
                # Check if element should be active
                if element.duration is None or self.elapsed_time < element.duration:
                    active.append(element)

        return active

    def get_progress(self) -> float:
        """Get scene progress (0.0 to 1.0)"""
        if self.config.duration is None:
            return 0.0
        return min(1.0, self.elapsed_time / self.config.duration)


class SceneManager:
    """
    Manages scene transitions and the overall debate flow

    Handles automatic scene progression, transitions, and timing.
    """

    def __init__(self):
        """Initialize scene manager"""
        self.scenes: Dict[SceneType, SceneConfig] = {}
        self.current_scene: Optional[Scene] = None
        self.scene_history: List[SceneType] = []
        self.transition_progress: float = 0.0
        self.is_transitioning: bool = False

        # Initialize default scenes
        self._create_default_scenes()

    def _create_default_scenes(self):
        """Create default scene configurations"""

        # INTRO SCENE
        self.scenes[SceneType.INTRO] = SceneConfig(
            scene_type=SceneType.INTRO,
            duration=5.0,
            elements=[
                SceneElement(
                    element_type="logo",
                    position=(960, 400),  # Center of 1920x1080
                    size=(400, 400),
                    content="ai_council_logo.png",
                    animation="fade_in",
                    layer=1
                ),
                SceneElement(
                    element_type="title",
                    position=(960, 700),
                    size=(800, 100),
                    content="AI COUNCIL DEBATE",
                    animation="slide_up",
                    layer=2
                ),
                SceneElement(
                    element_type="subtitle",
                    position=(960, 800),
                    size=(600, 60),
                    content="Where AI Minds Collide",
                    animation="fade_in",
                    duration=4.0,
                    layer=2
                ),
            ],
            background="gradient",
            background_color=(20, 40, 80),
            music="intro_theme.mp3",
            transition_out="zoom_in",
            auto_advance=True,
            next_scene=SceneType.DEBATE_ROUND
        )

        # DEBATE ROUND SCENE
        self.scenes[SceneType.DEBATE_ROUND] = SceneConfig(
            scene_type=SceneType.DEBATE_ROUND,
            duration=None,  # Managed by debate system
            elements=[
                SceneElement(
                    element_type="topic_banner",
                    position=(960, 50),
                    size=(1600, 80),
                    content="",  # Set dynamically
                    layer=3
                ),
                SceneElement(
                    element_type="timer",
                    position=(1800, 50),
                    size=(100, 80),
                    content="0:00",
                    layer=3
                ),
                SceneElement(
                    element_type="agent_avatars",
                    position=(960, 900),
                    size=(1600, 200),
                    content="avatar_grid",
                    layer=2
                ),
            ],
            background="solid",
            background_color=(30, 30, 30),
            transition_in="slide_up",
            transition_out="fade"
        )

        # VOTING SCENE
        self.scenes[SceneType.VOTING] = SceneConfig(
            scene_type=SceneType.VOTING,
            duration=10.0,
            elements=[
                SceneElement(
                    element_type="title",
                    position=(960, 200),
                    size=(800, 100),
                    content="VOTING",
                    animation="fade_in",
                    layer=3
                ),
                SceneElement(
                    element_type="vote_results",
                    position=(960, 540),
                    size=(1200, 600),
                    content="vote_visualization",
                    animation="slide_in",
                    layer=2
                ),
                SceneElement(
                    element_type="agent_cards",
                    position=(960, 900),
                    size=(1600, 150),
                    content="agent_vote_cards",
                    layer=1
                ),
            ],
            background="gradient",
            background_color=(40, 20, 60),
            transition_in="wipe_up",
            transition_out="fade",
            auto_advance=True,
            next_scene=SceneType.RESULTS
        )

        # RESULTS SCENE
        self.scenes[SceneType.RESULTS] = SceneConfig(
            scene_type=SceneType.RESULTS,
            duration=8.0,
            elements=[
                SceneElement(
                    element_type="winner_spotlight",
                    position=(960, 300),
                    size=(600, 400),
                    content="",  # Set dynamically
                    animation="zoom_in",
                    layer=3
                ),
                SceneElement(
                    element_type="vote_distribution",
                    position=(960, 700),
                    size=(800, 200),
                    content="distribution_chart",
                    layer=2
                ),
                SceneElement(
                    element_type="statistics",
                    position=(1500, 540),
                    size=(400, 600),
                    content="debate_stats",
                    layer=1
                ),
            ],
            background="celebration",
            background_color=(50, 20, 50),
            transition_in="fade",
            transition_out="zoom_out",
            auto_advance=True,
            next_scene=SceneType.OUTRO
        )

        # OUTRO SCENE
        self.scenes[SceneType.OUTRO] = SceneConfig(
            scene_type=SceneType.OUTRO,
            duration=5.0,
            elements=[
                SceneElement(
                    element_type="thank_you",
                    position=(960, 400),
                    size=(800, 200),
                    content="Thank You for Watching",
                    animation="fade_in",
                    layer=2
                ),
                SceneElement(
                    element_type="next_debate",
                    position=(960, 600),
                    size=(600, 100),
                    content="Next Debate: 24 hours",
                    animation="fade_in",
                    duration=4.0,
                    layer=1
                ),
                SceneElement(
                    element_type="social_links",
                    position=(960, 800),
                    size=(800, 100),
                    content="@AICouncilDebate",
                    layer=1
                ),
            ],
            background="gradient",
            background_color=(20, 20, 40),
            music="outro_theme.mp3",
            transition_in="fade",
            auto_advance=False
        )

        # IDLE SCENE (for between debates)
        self.scenes[SceneType.IDLE] = SceneConfig(
            scene_type=SceneType.IDLE,
            duration=None,
            elements=[
                SceneElement(
                    element_type="title",
                    position=(960, 400),
                    size=(800, 150),
                    content="Stand By...",
                    layer=1
                ),
                SceneElement(
                    element_type="countdown",
                    position=(960, 600),
                    size=(400, 100),
                    content="Next debate in: --:--",
                    layer=1
                ),
            ],
            background="solid",
            background_color=(20, 20, 20)
        )

    def get_scene(self, scene_type: SceneType) -> SceneConfig:
        """
        Get scene configuration

        Args:
            scene_type: Type of scene to get

        Returns:
            SceneConfig for the requested scene

        Raises:
            ValueError: If scene type not found
        """
        if scene_type not in self.scenes:
            raise ValueError(f"Scene type {scene_type.value} not configured")
        return self.scenes[scene_type]

    def add_scene(self, config: SceneConfig):
        """Add or update a scene configuration"""
        self.scenes[config.scene_type] = config
        logger.info(f"Added scene: {config.scene_type.value}")

    def start_scene(self, scene_type: SceneType) -> Scene:
        """
        Start a new scene

        Args:
            scene_type: Type of scene to start

        Returns:
            Active Scene instance
        """
        # Stop current scene
        if self.current_scene:
            self.current_scene.stop()

        # Get scene config
        config = self.get_scene(scene_type)

        # Create and start new scene
        self.current_scene = Scene(config)
        self.current_scene.start()

        # Track history
        self.scene_history.append(scene_type)

        logger.info(f"Started scene: {scene_type.value}")

        return self.current_scene

    async def transition_to_scene(
        self,
        scene_type: SceneType,
        transition_type: Optional[str] = None
    ):
        """
        Transition to a new scene

        Args:
            scene_type: Scene to transition to
            transition_type: Override default transition
        """
        if not self.current_scene:
            self.start_scene(scene_type)
            return

        # Use current scene's transition_out or override
        if transition_type is None:
            transition_type = self.current_scene.config.transition_out

        # Mark as transitioning
        self.is_transitioning = True
        self.transition_progress = 0.0

        # Get transition duration
        duration = self.current_scene.config.transition_duration

        # Simulate transition (in real implementation, would render frames)
        steps = int(duration * 30)  # 30 FPS
        for i in range(steps + 1):
            self.transition_progress = i / steps
            await asyncio.sleep(1.0 / 30)

        # Start new scene
        self.is_transitioning = False
        self.start_scene(scene_type)

    def update(self, dt: float) -> bool:
        """
        Update current scene

        Args:
            dt: Delta time since last update

        Returns:
            True if scene is still active, False if complete
        """
        if not self.current_scene:
            return False

        # Update scene
        is_active = self.current_scene.update(dt)

        # Check for auto-advance
        if not is_active and self.current_scene.config.auto_advance:
            next_scene = self.current_scene.config.next_scene
            if next_scene:
                logger.info(f"Auto-advancing to {next_scene.value}")
                # Note: Would call transition_to_scene in async context
                return False

        return is_active

    def get_current_scene(self) -> Optional[Scene]:
        """Get current active scene"""
        return self.current_scene

    def get_scene_progress(self) -> float:
        """Get current scene progress (0.0 to 1.0)"""
        if not self.current_scene:
            return 0.0
        return self.current_scene.get_progress()

    def get_scene_history(self) -> List[SceneType]:
        """Get list of scenes that have been shown"""
        return self.scene_history.copy()

    def reset(self):
        """Reset scene manager to initial state"""
        if self.current_scene:
            self.current_scene.stop()

        self.current_scene = None
        self.scene_history = []
        self.is_transitioning = False
        self.transition_progress = 0.0

        logger.info("Scene manager reset")


# Pre-defined scene templates for quick setup

def create_debate_flow() -> List[SceneType]:
    """Create standard debate scene flow"""
    return [
        SceneType.INTRO,
        SceneType.DEBATE_ROUND,  # Can repeat for multiple rounds
        SceneType.VOTING,
        SceneType.RESULTS,
        SceneType.OUTRO,
    ]


def create_quick_debate_flow() -> List[SceneType]:
    """Create quick debate flow (no intro/outro)"""
    return [
        SceneType.DEBATE_ROUND,
        SceneType.VOTING,
        SceneType.RESULTS,
    ]


def create_continuous_stream_flow() -> List[SceneType]:
    """Create continuous streaming flow"""
    return [
        SceneType.INTRO,
        SceneType.DEBATE_ROUND,
        SceneType.VOTING,
        SceneType.RESULTS,
        SceneType.IDLE,  # Wait for next debate
    ]
