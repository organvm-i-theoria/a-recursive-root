"""
Personality to Visual Trait Mapping

Maps each of the 15 AI personalities to visual characteristics for avatar generation.
"""

from dataclasses import dataclass
from typing import Dict, List
from enum import Enum


class AvatarStyle(str, Enum):
    """Available avatar visual styles"""
    REALISTIC = "realistic"
    CYBERPUNK = "cyberpunk"
    CARTOON = "cartoon"
    ABSTRACT = "abstract"
    CLASSICAL = "classical"
    MINIMAL = "minimal"


@dataclass
class PersonalityVisualTraits:
    """Visual traits for a personality"""
    personality_name: str
    style: AvatarStyle
    base_prompt: str
    appearance_traits: str
    attire: str
    colors: List[str]
    mood: str
    setting: str
    negative_prompt: str = ""


# Complete mapping of all 15 personalities to visual traits
PERSONALITY_AVATAR_MAP: Dict[str, PersonalityVisualTraits] = {
    "pragmatist": PersonalityVisualTraits(
        personality_name="The Pragmatist",
        style=AvatarStyle.REALISTIC,
        base_prompt="professional business executive, corporate leader",
        appearance_traits="middle-aged, composed expression, intelligent eyes, subtle smile, professional appearance",
        attire="dark navy blue business suit, crisp white shirt, simple tie, minimal accessories",
        colors=["navy blue", "charcoal gray", "white", "silver"],
        mood="confident and grounded, practical demeanor",
        setting="modern office background, neutral tones",
        negative_prompt="casual, disheveled, overly emotional, fantasy elements"
    ),

    "idealist": PersonalityVisualTraits(
        personality_name="The Idealist",
        style=AvatarStyle.REALISTIC,
        base_prompt="inspirational leader, humanitarian advocate",
        appearance_traits="warm smile, bright hopeful eyes, youthful energy, open expression",
        attire="light casual professional, sky blue sweater, comfortable yet polished",
        colors=["sky blue", "soft gold", "cream white", "sunrise orange"],
        mood="optimistic and passionate, inspiring presence",
        setting="bright natural lighting, soft focus background",
        negative_prompt="cynical, dark, gloomy, corporate"
    ),

    "skeptic": PersonalityVisualTraits(
        personality_name="The Skeptic",
        style=AvatarStyle.REALISTIC,
        base_prompt="analytical researcher, critical thinker",
        appearance_traits="raised eyebrow, sharp analytical gaze, serious expression, intellectual look",
        attire="dark turtleneck, reading glasses, minimal styling",
        colors=["dark gray", "black", "deep red", "steel blue"],
        mood="questioning and analytical, penetrating gaze",
        setting="library or study background, books visible",
        negative_prompt="trusting, naive, colorful, whimsical"
    ),

    "optimist": PersonalityVisualTraits(
        personality_name="The Optimist",
        style=AvatarStyle.CARTOON,
        base_prompt="cheerful character, positive energy",
        appearance_traits="bright smile, sparkling eyes, animated features, energetic posture",
        attire="bright yellow cardigan, casual comfortable clothes, cheerful accessories",
        colors=["sunshine yellow", "sky blue", "fresh green", "coral pink"],
        mood="enthusiastic and upbeat, radiating positivity",
        setting="sunny outdoor scene, vibrant colors",
        negative_prompt="dark, pessimistic, muted, gloomy"
    ),

    "contrarian": PersonalityVisualTraits(
        personality_name="The Contrarian",
        style=AvatarStyle.CYBERPUNK,
        base_prompt="rebel thinker, iconoclast",
        appearance_traits="confident smirk, challenging gaze, edgy appearance, unconventional style",
        attire="leather jacket, alternative fashion, bold accessories",
        colors=["electric purple", "neon green", "black", "hot pink"],
        mood="provocative and bold, defiant energy",
        setting="urban street art background, graffiti",
        negative_prompt="conventional, conformist, traditional, conservative"
    ),

    "mediator": PersonalityVisualTraits(
        personality_name="The Mediator",
        style=AvatarStyle.REALISTIC,
        base_prompt="diplomatic negotiator, peaceful arbitrator",
        appearance_traits="calm gentle expression, empathetic eyes, balanced features, serene presence",
        attire="neutral beige blazer, soft colors, harmonious style",
        colors=["soft beige", "sage green", "warm gray", "pearl white"],
        mood="peaceful and balanced, centered demeanor",
        setting="tranquil neutral background, soft lighting",
        negative_prompt="aggressive, polarizing, extreme, chaotic"
    ),

    "analyst": PersonalityVisualTraits(
        personality_name="The Analyst",
        style=AvatarStyle.REALISTIC,
        base_prompt="data scientist, systematic researcher",
        appearance_traits="focused expression, sharp features, precise appearance, intelligent demeanor",
        attire="white lab coat or business casual, functional clothing",
        colors=["clinical white", "steel gray", "electric blue", "black"],
        mood="methodical and precise, data-focused",
        setting="modern tech office, screens with data",
        negative_prompt="emotional, imprecise, artistic, chaotic"
    ),

    "visionary": PersonalityVisualTraits(
        personality_name="The Visionary",
        style=AvatarStyle.CLASSICAL,
        base_prompt="renaissance thinker, futurist innovator",
        appearance_traits="distant gaze toward horizon, inspired expression, creative energy, noble features",
        attire="flowing artistic attire, avant-garde fashion, statement pieces",
        colors=["royal purple", "cosmic blue", "gold", "iridescent white"],
        mood="inspired and forward-looking, dreamy intensity",
        setting="starry sky or ethereal background",
        negative_prompt="mundane, ordinary, conventional, limited"
    ),

    "traditionalist": PersonalityVisualTraits(
        personality_name="The Traditionalist",
        style=AvatarStyle.CLASSICAL,
        base_prompt="distinguished scholar, historical expert",
        appearance_traits="dignified expression, wise eyes, refined features, timeless appearance",
        attire="classic tweed jacket, traditional formal wear, vintage style",
        colors=["forest green", "burgundy", "tan", "gold trim"],
        mood="respectful and dignified, grounded in wisdom",
        setting="classical library with old books, wood paneling",
        negative_prompt="modern, trendy, futuristic, flashy"
    ),

    "revolutionary": PersonalityVisualTraits(
        personality_name="The Revolutionary",
        style=AvatarStyle.CYBERPUNK,
        base_prompt="radical activist, change agent",
        appearance_traits="fierce determined expression, intense eyes, powerful presence, bold features",
        attire="combat boots, activist gear, statement clothing, symbolic accessories",
        colors=["revolution red", "black", "white", "gold accents"],
        mood="passionate and fierce, revolutionary spirit",
        setting="protest or rally background, dynamic energy",
        negative_prompt="passive, conservative, neutral, complacent"
    ),

    "economist": PersonalityVisualTraits(
        personality_name="The Economist",
        style=AvatarStyle.REALISTIC,
        base_prompt="financial expert, economic strategist",
        appearance_traits="calculated expression, shrewd eyes, professional demeanor, strategic look",
        attire="pinstripe suit, expensive watch, Wall Street style",
        colors=["dollar green", "gold", "navy blue", "silver"],
        mood="strategic and calculating, market-focused",
        setting="trading floor or financial district background",
        negative_prompt="impractical, emotional, artistic, non-materialistic"
    ),

    "ethicist": PersonalityVisualTraits(
        personality_name="The Ethicist",
        style=AvatarStyle.REALISTIC,
        base_prompt="moral philosopher, ethical advisor",
        appearance_traits="thoughtful gentle expression, compassionate eyes, principled demeanor, caring features",
        attire="simple elegant clothing, symbolic jewelry, understated style",
        colors=["pure white", "ethical gray", "compassion blue", "truth gold"],
        mood="principled and thoughtful, morally centered",
        setting="meditation space or ethical forum background",
        negative_prompt="amoral, selfish, cynical, corrupt"
    ),

    "technologist": PersonalityVisualTraits(
        personality_name="The Technologist",
        style=AvatarStyle.CYBERPUNK,
        base_prompt="tech innovator, future engineer",
        appearance_traits="focused tech-savvy expression, sharp modern features, innovative look",
        attire="smart casual tech wear, modern accessories, gadgets visible",
        colors=["silicon blue", "LED white", "circuit green", "chrome"],
        mood="innovative and tech-focused, future-oriented",
        setting="high-tech lab or server room background",
        negative_prompt="old-fashioned, traditional, low-tech, analog"
    ),

    "populist": PersonalityVisualTraits(
        personality_name="The Populist",
        style=AvatarStyle.REALISTIC,
        base_prompt="people's champion, grassroots leader",
        appearance_traits="relatable approachable expression, everyday features, down-to-earth appearance",
        attire="casual everyday clothing, working-class style, accessible fashion",
        colors=["working blue", "earth brown", "people's red", "common green"],
        mood="relatable and down-to-earth, people-focused",
        setting="town square or community gathering background",
        negative_prompt="elitist, aristocratic, distant, ivory tower"
    ),

    "philosopher": PersonalityVisualTraits(
        personality_name="The Philosopher",
        style=AvatarStyle.CLASSICAL,
        base_prompt="ancient sage, deep thinker",
        appearance_traits="contemplative expression, deep thoughtful eyes, wise features, introspective look",
        attire="scholarly robes, academic attire, timeless intellectual style",
        colors=["wisdom purple", "thought gray", "truth white", "depth blue"],
        mood="contemplative and profound, deep in thought",
        setting="philosophical garden or ancient library",
        negative_prompt="shallow, superficial, rushed, simplistic"
    ),
}


def get_personality_traits(personality_name: str) -> PersonalityVisualTraits:
    """
    Get visual traits for a personality

    Args:
        personality_name: Name of the personality (e.g., "pragmatist", "idealist")

    Returns:
        PersonalityVisualTraits for the given personality

    Raises:
        ValueError: If personality name is not recognized
    """
    traits = PERSONALITY_AVATAR_MAP.get(personality_name.lower())
    if not traits:
        raise ValueError(
            f"Unknown personality: {personality_name}. "
            f"Available: {list(PERSONALITY_AVATAR_MAP.keys())}"
        )
    return traits


def get_all_personality_names() -> List[str]:
    """Get list of all personality names with avatar mappings"""
    return list(PERSONALITY_AVATAR_MAP.keys())


def build_full_prompt(traits: PersonalityVisualTraits, quality_level: str = "high") -> str:
    """
    Build complete prompt for avatar generation

    Args:
        traits: PersonalityVisualTraits to build prompt from
        quality_level: Quality level - "low", "medium", "high", "ultra"

    Returns:
        Complete prompt string for image generation
    """
    quality_modifiers = {
        "low": "",
        "medium": "detailed, high quality,",
        "high": "highly detailed, professional quality, masterpiece,",
        "ultra": "ultra detailed, photorealistic, masterpiece, award winning, 8k,"
    }

    quality = quality_modifiers.get(quality_level, quality_modifiers["high"])

    prompt_parts = [
        quality,
        traits.base_prompt,
        traits.appearance_traits,
        traits.attire,
        f"color palette: {', '.join(traits.colors)}",
        traits.mood,
        traits.setting,
        f"style: {traits.style.value}",
    ]

    return " ".join(filter(None, prompt_parts))


def build_negative_prompt(traits: PersonalityVisualTraits) -> str:
    """
    Build negative prompt for avatar generation

    Args:
        traits: PersonalityVisualTraits to build negative prompt from

    Returns:
        Negative prompt string
    """
    base_negative = [
        "blurry",
        "low quality",
        "distorted",
        "ugly",
        "deformed",
        "multiple heads",
        "duplicate",
        "morbid",
        "mutilated",
        "poorly drawn",
    ]

    if traits.negative_prompt:
        base_negative.append(traits.negative_prompt)

    return ", ".join(base_negative)
