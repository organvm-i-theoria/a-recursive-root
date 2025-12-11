"""
Expression Engine

Maps sentiment and emotional states to avatar expressions and animations.
"""

import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SentimentType(str, Enum):
    """Sentiment categories"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"
    AGREEING = "agreeing"
    DISAGREEING = "disagreeing"
    QUESTIONING = "questioning"
    ASSERTIVE = "assertive"
    CONTEMPLATIVE = "contemplative"


class Expression(str, Enum):
    """Available facial expressions"""
    # Positive
    SMILING = "smiling"
    ENTHUSIASTIC = "enthusiastic"
    NODDING = "nodding"
    FRIENDLY = "friendly"

    # Negative
    FROWNING = "frowning"
    CONCERNED = "concerned"
    SKEPTICAL = "skeptical"
    DISAPPROVING = "disapproving"

    # Neutral
    THOUGHTFUL = "thoughtful"
    LISTENING = "listening"
    ANALYTICAL = "analytical"
    CALM = "calm"

    # Confident
    ASSERTIVE = "assertive"
    DIRECT_GAZE = "direct_gaze"
    UPRIGHT = "upright"
    COMMANDING = "commanding"

    # Uncertain
    PONDERING = "pondering"
    HESITANT = "hesitant"
    QUESTIONING = "questioning"
    DOUBTFUL = "doubtful"


# Sentiment to expression mapping
SENTIMENT_EXPRESSION_MAP: Dict[SentimentType, List[Expression]] = {
    SentimentType.POSITIVE: [
        Expression.SMILING,
        Expression.NODDING,
        Expression.ENTHUSIASTIC,
        Expression.FRIENDLY,
    ],
    SentimentType.NEGATIVE: [
        Expression.FROWNING,
        Expression.CONCERNED,
        Expression.SKEPTICAL,
        Expression.DISAPPROVING,
    ],
    SentimentType.NEUTRAL: [
        Expression.THOUGHTFUL,
        Expression.LISTENING,
        Expression.ANALYTICAL,
        Expression.CALM,
    ],
    SentimentType.CONFIDENT: [
        Expression.ASSERTIVE,
        Expression.DIRECT_GAZE,
        Expression.UPRIGHT,
        Expression.COMMANDING,
    ],
    SentimentType.UNCERTAIN: [
        Expression.PONDERING,
        Expression.HESITANT,
        Expression.QUESTIONING,
        Expression.DOUBTFUL,
    ],
    SentimentType.AGREEING: [
        Expression.NODDING,
        Expression.SMILING,
        Expression.FRIENDLY,
    ],
    SentimentType.DISAGREEING: [
        Expression.FROWNING,
        Expression.SKEPTICAL,
        Expression.DISAPPROVING,
    ],
    SentimentType.QUESTIONING: [
        Expression.QUESTIONING,
        Expression.PONDERING,
        Expression.THOUGHTFUL,
    ],
    SentimentType.ASSERTIVE: [
        Expression.ASSERTIVE,
        Expression.DIRECT_GAZE,
        Expression.COMMANDING,
    ],
    SentimentType.CONTEMPLATIVE: [
        Expression.THOUGHTFUL,
        Expression.ANALYTICAL,
        Expression.PONDERING,
    ],
}


@dataclass
class AnimationFrame:
    """Single frame of expression animation"""
    expression: Expression
    intensity: float  # 0.0 to 1.0
    duration: float  # seconds
    transition: str = "ease-in-out"  # CSS-style transition


@dataclass
class ExpressionSequence:
    """Sequence of expressions for an animation"""
    frames: List[AnimationFrame]
    total_duration: float
    loop: bool = False


class ExpressionEngine:
    """
    Engine for mapping sentiment to avatar expressions

    Handles sentiment analysis and generates appropriate facial expressions
    and animations for avatars during debates.
    """

    def __init__(
        self,
        default_intensity: float = 0.7,
        transition_duration: float = 0.5,
    ):
        """
        Initialize expression engine

        Args:
            default_intensity: Default expression intensity (0.0-1.0)
            transition_duration: Default transition time between expressions
        """
        self.default_intensity = default_intensity
        self.transition_duration = transition_duration

        # Expression duration map (in seconds)
        self.expression_durations = {
            Expression.SMILING: 2.0,
            Expression.ENTHUSIASTIC: 1.5,
            Expression.NODDING: 1.0,
            Expression.FROWNING: 2.0,
            Expression.SKEPTICAL: 2.5,
            Expression.THOUGHTFUL: 3.0,
            Expression.ASSERTIVE: 2.0,
            Expression.PONDERING: 3.5,
            Expression.QUESTIONING: 2.0,
        }

    def get_expression_for_sentiment(
        self,
        sentiment: SentimentType,
        confidence: float = 0.5,
        personality: Optional[str] = None,
    ) -> Expression:
        """
        Get appropriate expression for sentiment

        Args:
            sentiment: Sentiment type
            confidence: Confidence level (affects intensity)
            personality: Personality name (affects expression choice)

        Returns:
            Expression enum
        """
        expressions = SENTIMENT_EXPRESSION_MAP.get(sentiment, [Expression.CALM])

        # Personality-specific expression preferences
        if personality:
            expressions = self._filter_by_personality(expressions, personality)

        # Choose expression based on confidence
        # Higher confidence -> more intense expressions
        if confidence > 0.8 and len(expressions) > 1:
            return expressions[0]  # Most intense
        elif confidence < 0.3 and Expression.HESITANT in expressions:
            return Expression.HESITANT
        else:
            return expressions[0] if expressions else Expression.CALM

    def _filter_by_personality(
        self,
        expressions: List[Expression],
        personality: str
    ) -> List[Expression]:
        """Filter expressions based on personality traits"""
        personality_preferences = {
            "pragmatist": [Expression.ANALYTICAL, Expression.CALM, Expression.THOUGHTFUL],
            "idealist": [Expression.ENTHUSIASTIC, Expression.SMILING, Expression.FRIENDLY],
            "skeptic": [Expression.SKEPTICAL, Expression.QUESTIONING, Expression.ANALYTICAL],
            "optimist": [Expression.SMILING, Expression.ENTHUSIASTIC, Expression.NODDING],
            "contrarian": [Expression.SKEPTICAL, Expression.DISAPPROVING, Expression.QUESTIONING],
            "mediator": [Expression.CALM, Expression.LISTENING, Expression.FRIENDLY],
            "analyst": [Expression.ANALYTICAL, Expression.THOUGHTFUL, Expression.PONDERING],
            "visionary": [Expression.ENTHUSIASTIC, Expression.ASSERTIVE, Expression.COMMANDING],
            "traditionalist": [Expression.CALM, Expression.THOUGHTFUL, Expression.SKEPTICAL],
            "revolutionary": [Expression.ASSERTIVE, Expression.COMMANDING, Expression.FROWNING],
            "economist": [Expression.ANALYTICAL, Expression.SKEPTICAL, Expression.ASSERTIVE],
            "ethicist": [Expression.THOUGHTFUL, Expression.CONCERNED, Expression.CALM],
            "technologist": [Expression.ENTHUSIASTIC, Expression.ANALYTICAL, Expression.ASSERTIVE],
            "populist": [Expression.FRIENDLY, Expression.ASSERTIVE, Expression.SMILING],
            "philosopher": [Expression.CONTEMPLATIVE, Expression.PONDERING, Expression.THOUGHTFUL],
        }

        preferred = personality_preferences.get(personality.lower(), [])

        # Prefer personality-matched expressions
        filtered = [e for e in expressions if e in preferred]
        return filtered if filtered else expressions

    async def create_expression_animation(
        self,
        sentiment: SentimentType,
        duration: float,
        confidence: float = 0.5,
        personality: Optional[str] = None,
    ) -> ExpressionSequence:
        """
        Create animated expression sequence

        Args:
            sentiment: Base sentiment
            duration: Total animation duration
            confidence: Confidence level
            personality: Personality name

        Returns:
            ExpressionSequence with animated frames
        """
        base_expression = self.get_expression_for_sentiment(
            sentiment, confidence, personality
        )

        # Calculate intensity based on confidence
        intensity = min(1.0, self.default_intensity + (confidence * 0.3))

        # Create simple 3-frame animation: intro -> hold -> outro
        frames = [
            # Fade in
            AnimationFrame(
                expression=base_expression,
                intensity=intensity * 0.5,
                duration=self.transition_duration,
                transition="ease-in",
            ),
            # Hold
            AnimationFrame(
                expression=base_expression,
                intensity=intensity,
                duration=duration - (2 * self.transition_duration),
                transition="linear",
            ),
            # Fade out
            AnimationFrame(
                expression=base_expression,
                intensity=intensity * 0.5,
                duration=self.transition_duration,
                transition="ease-out",
            ),
        ]

        return ExpressionSequence(
            frames=frames,
            total_duration=duration,
            loop=False,
        )

    def analyze_text_sentiment(self, text: str) -> Tuple[SentimentType, float]:
        """
        Analyze text to determine sentiment

        This is a simple keyword-based analyzer.
        For production, use actual NLP/sentiment analysis models.

        Args:
            text: Text to analyze

        Returns:
            Tuple of (SentimentType, confidence)
        """
        text_lower = text.lower()

        # Keyword-based sentiment detection
        positive_keywords = [
            "agree", "yes", "excellent", "great", "wonderful",
            "support", "benefit", "advantage", "positive", "good"
        ]
        negative_keywords = [
            "disagree", "no", "terrible", "bad", "wrong",
            "oppose", "problem", "issue", "concern", "negative"
        ]
        questioning_keywords = [
            "?", "why", "how", "what if", "perhaps", "maybe",
            "question", "wonder", "unsure"
        ]
        confident_keywords = [
            "certain", "definitely", "absolutely", "clearly",
            "obviously", "undoubtedly", "proven", "fact"
        ]

        # Count matches
        positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
        negative_count = sum(1 for kw in negative_keywords if kw in text_lower)
        questioning_count = sum(1 for kw in questioning_keywords if kw in text_lower)
        confident_count = sum(1 for kw in confident_keywords if kw in text_lower)

        # Determine dominant sentiment
        counts = {
            SentimentType.POSITIVE: positive_count,
            SentimentType.NEGATIVE: negative_count,
            SentimentType.QUESTIONING: questioning_count,
            SentimentType.CONFIDENT: confident_count,
        }

        max_sentiment = max(counts.items(), key=lambda x: x[1])

        if max_sentiment[1] == 0:
            return SentimentType.NEUTRAL, 0.5

        # Calculate confidence based on keyword density
        total_words = len(text.split())
        confidence = min(1.0, max_sentiment[1] / max(1, total_words / 10))

        return max_sentiment[0], confidence

    def get_speaking_animation(
        self,
        personality: str,
        text_length: int,
        sentiment: Optional[SentimentType] = None,
    ) -> ExpressionSequence:
        """
        Get animation for speaking/presenting

        Args:
            personality: Personality name
            text_length: Length of text being spoken
            sentiment: Optional sentiment override

        Returns:
            ExpressionSequence for speaking animation
        """
        # Estimate duration based on text length (rough: 150 words per minute)
        words = text_length / 5  # Rough word count
        duration = (words / 150) * 60  # seconds

        if not sentiment:
            sentiment = SentimentType.ASSERTIVE

        # Create multi-frame animation with micro-expressions
        base_expression = self.get_expression_for_sentiment(
            sentiment, 0.7, personality
        )

        frames = []
        num_segments = max(3, int(duration / 2))  # Change expression every 2 seconds

        for i in range(num_segments):
            segment_duration = duration / num_segments
            intensity = 0.6 + (i % 2) * 0.2  # Alternate intensity

            frames.append(AnimationFrame(
                expression=base_expression,
                intensity=intensity,
                duration=segment_duration,
                transition="ease-in-out",
            ))

        return ExpressionSequence(
            frames=frames,
            total_duration=duration,
            loop=False,
        )

    def get_listening_animation(self, personality: str, duration: float) -> ExpressionSequence:
        """
        Get animation for listening (when not speaking)

        Args:
            personality: Personality name
            duration: Animation duration

        Returns:
            ExpressionSequence for listening animation
        """
        base_expression = self.get_expression_for_sentiment(
            SentimentType.NEUTRAL, 0.5, personality
        )

        # Subtle animation - occasional micro-expressions
        frames = [
            AnimationFrame(
                expression=Expression.LISTENING,
                intensity=0.5,
                duration=duration * 0.7,
                transition="linear",
            ),
            AnimationFrame(
                expression=Expression.THOUGHTFUL,
                intensity=0.6,
                duration=duration * 0.3,
                transition="ease-in-out",
            ),
        ]

        return ExpressionSequence(
            frames=frames,
            total_duration=duration,
            loop=True,
        )


# Convenience functions

def create_expression_engine(**kwargs) -> ExpressionEngine:
    """Create default expression engine"""
    return ExpressionEngine(**kwargs)


async def get_expression_for_text(
    text: str,
    personality: str,
    engine: Optional[ExpressionEngine] = None
) -> Expression:
    """
    Get expression for given text

    Args:
        text: Text to analyze
        personality: Personality name
        engine: Optional ExpressionEngine instance

    Returns:
        Expression enum
    """
    if not engine:
        engine = ExpressionEngine()

    sentiment, confidence = engine.analyze_text_sentiment(text)
    return engine.get_expression_for_sentiment(sentiment, confidence, personality)
