"""
Avatar Generator

Generates AI avatars using multiple image generation providers:
- Stable Diffusion (local or API via Replicate/Stability AI)
- DALL-E 3 (OpenAI)
- Mock mode (for testing)
"""

import asyncio
import base64
import io
import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any
from pathlib import Path
import logging

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class AvatarProvider(str, Enum):
    """Available avatar generation providers"""
    STABLE_DIFFUSION = "stable_diffusion"
    DALLE3 = "dalle3"
    REPLICATE = "replicate"
    STABILITY_AI = "stability_ai"
    MOCK = "mock"


class AvatarSize(str, Enum):
    """Standard avatar sizes"""
    SMALL = "256x256"
    MEDIUM = "512x512"
    LARGE = "1024x1024"
    ULTRA = "1536x1536"


@dataclass
class GeneratedAvatar:
    """Result of avatar generation"""
    personality: str
    image_data: bytes  # Raw image bytes (PNG/JPEG)
    prompt: str
    provider: AvatarProvider
    size: AvatarSize
    seed: Optional[int] = None
    metadata: Dict[str, Any] = None

    def save(self, filepath: str):
        """Save avatar to file"""
        with open(filepath, 'wb') as f:
            f.write(self.image_data)

    def to_pil_image(self) -> Optional['Image.Image']:
        """Convert to PIL Image if available"""
        if not PIL_AVAILABLE:
            logger.warning("PIL not available, cannot convert to Image")
            return None
        return Image.open(io.BytesIO(self.image_data))


class AvatarGenerator:
    """
    Multi-provider avatar generator for AI personalities

    Supports multiple image generation backends with automatic fallback.
    """

    def __init__(
        self,
        provider: AvatarProvider = AvatarProvider.MOCK,
        api_key: Optional[str] = None,
        default_size: AvatarSize = AvatarSize.LARGE,
        quality: str = "high",
        cache_dir: Optional[str] = None,
    ):
        """
        Initialize avatar generator

        Args:
            provider: Image generation provider to use
            api_key: API key for the provider (if required)
            default_size: Default avatar size
            quality: Quality level - "low", "medium", "high", "ultra"
            cache_dir: Directory for caching generated avatars
        """
        self.provider = provider
        self.api_key = api_key or os.getenv(self._get_env_key())
        self.default_size = default_size
        self.quality = quality
        self.cache_dir = Path(cache_dir) if cache_dir else None

        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Lazy import of provider-specific modules
        self._client = None
        self._initialize_provider()

    def _get_env_key(self) -> str:
        """Get environment variable name for API key"""
        env_keys = {
            AvatarProvider.DALLE3: "OPENAI_API_KEY",
            AvatarProvider.REPLICATE: "REPLICATE_API_KEY",
            AvatarProvider.STABILITY_AI: "STABILITY_API_KEY",
        }
        return env_keys.get(self.provider, "")

    def _initialize_provider(self):
        """Initialize the selected provider"""
        if self.provider == AvatarProvider.MOCK:
            logger.info("Using MOCK avatar generator")
            return

        if self.provider == AvatarProvider.DALLE3:
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY required for DALL-E 3")
            try:
                import openai
                self._client = openai.AsyncOpenAI(api_key=self.api_key)
                logger.info("Initialized DALL-E 3 provider")
            except ImportError:
                raise ImportError("openai package required for DALL-E 3. Install: pip install openai")

        elif self.provider == AvatarProvider.REPLICATE:
            if not self.api_key:
                raise ValueError("REPLICATE_API_KEY required for Replicate")
            try:
                import replicate
                self._client = replicate.Client(api_token=self.api_key)
                logger.info("Initialized Replicate provider")
            except ImportError:
                raise ImportError("replicate package required. Install: pip install replicate")

        elif self.provider == AvatarProvider.STABILITY_AI:
            if not self.api_key:
                raise ValueError("STABILITY_API_KEY required for Stability AI")
            # Stability AI uses REST API, no client needed
            logger.info("Initialized Stability AI provider")

        elif self.provider == AvatarProvider.STABLE_DIFFUSION:
            logger.info("Using local Stable Diffusion (requires separate setup)")

    async def generate_avatar(
        self,
        personality: str,
        size: Optional[AvatarSize] = None,
        seed: Optional[int] = None,
        custom_prompt: Optional[str] = None,
    ) -> GeneratedAvatar:
        """
        Generate avatar for a personality

        Args:
            personality: Personality name (e.g., "pragmatist")
            size: Avatar size (uses default if not specified)
            seed: Random seed for reproducibility
            custom_prompt: Override default prompt

        Returns:
            GeneratedAvatar instance
        """
        from .personality_mapping import get_personality_traits, build_full_prompt, build_negative_prompt

        size = size or self.default_size
        traits = get_personality_traits(personality)

        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = build_full_prompt(traits, quality_level=self.quality)

        logger.info(f"Generating avatar for {personality} using {self.provider.value}")
        logger.debug(f"Prompt: {prompt}")

        # Generate based on provider
        if self.provider == AvatarProvider.DALLE3:
            image_data = await self._generate_dalle3(prompt, size)
        elif self.provider == AvatarProvider.REPLICATE:
            negative_prompt = build_negative_prompt(traits)
            image_data = await self._generate_replicate(prompt, negative_prompt, size, seed)
        elif self.provider == AvatarProvider.STABILITY_AI:
            negative_prompt = build_negative_prompt(traits)
            image_data = await self._generate_stability(prompt, negative_prompt, size, seed)
        elif self.provider == AvatarProvider.STABLE_DIFFUSION:
            negative_prompt = build_negative_prompt(traits)
            image_data = await self._generate_local_sd(prompt, negative_prompt, size, seed)
        else:  # MOCK
            image_data = await self._generate_mock(personality, size)

        avatar = GeneratedAvatar(
            personality=personality,
            image_data=image_data,
            prompt=prompt,
            provider=self.provider,
            size=size,
            seed=seed,
            metadata={
                "traits": traits.__dict__,
                "quality": self.quality,
            }
        )

        # Cache if enabled
        if self.cache_dir:
            cache_path = self.cache_dir / f"{personality}_{size.value}_{self.provider.value}.png"
            avatar.save(str(cache_path))
            logger.info(f"Cached avatar to {cache_path}")

        return avatar

    async def _generate_dalle3(self, prompt: str, size: AvatarSize) -> bytes:
        """Generate using DALL-E 3"""
        # DALL-E 3 only supports specific sizes
        dalle_size = "1024x1024"  # Default
        if size == AvatarSize.LARGE or size == AvatarSize.ULTRA:
            dalle_size = "1024x1024"

        response = await self._client.images.generate(
            model="dall-e-3",
            prompt=prompt[:4000],  # DALL-E has prompt length limit
            size=dalle_size,
            quality="hd" if self.quality in ["high", "ultra"] else "standard",
            n=1,
            response_format="b64_json",
        )

        image_b64 = response.data[0].b64_json
        image_data = base64.b64decode(image_b64)

        # Resize if needed
        if size != AvatarSize.LARGE and PIL_AVAILABLE:
            image_data = self._resize_image(image_data, size)

        return image_data

    async def _generate_replicate(
        self,
        prompt: str,
        negative_prompt: str,
        size: AvatarSize,
        seed: Optional[int]
    ) -> bytes:
        """Generate using Replicate (SDXL)"""
        width, height = map(int, size.value.split('x'))

        output = await asyncio.to_thread(
            self._client.run,
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "num_outputs": 1,
                "seed": seed,
            }
        )

        # Download image from URL
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(output[0]) as resp:
                return await resp.read()

    async def _generate_stability(
        self,
        prompt: str,
        negative_prompt: str,
        size: AvatarSize,
        seed: Optional[int]
    ) -> bytes:
        """Generate using Stability AI API"""
        import aiohttp

        width, height = map(int, size.value.split('x'))

        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        body = {
            "text_prompts": [
                {"text": prompt, "weight": 1},
                {"text": negative_prompt, "weight": -1},
            ],
            "cfg_scale": 7,
            "height": height,
            "width": width,
            "samples": 1,
            "steps": 30 if self.quality in ["high", "ultra"] else 20,
        }

        if seed:
            body["seed"] = seed

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=body) as resp:
                if resp.status != 200:
                    raise Exception(f"Stability AI API error: {await resp.text()}")

                data = await resp.json()
                image_b64 = data["artifacts"][0]["base64"]
                return base64.b64decode(image_b64)

    async def _generate_local_sd(
        self,
        prompt: str,
        negative_prompt: str,
        size: AvatarSize,
        seed: Optional[int]
    ) -> bytes:
        """Generate using local Stable Diffusion (requires local setup)"""
        # This would require a local SD installation or API endpoint
        # For now, fallback to mock
        logger.warning("Local Stable Diffusion not configured, using mock")
        return await self._generate_mock("local_sd", size)

    async def _generate_mock(self, personality: str, size: AvatarSize) -> bytes:
        """Generate mock avatar (colored rectangle with text)"""
        if not PIL_AVAILABLE:
            # Return minimal PNG if PIL not available
            return self._minimal_png()

        from PIL import Image, ImageDraw, ImageFont

        width, height = map(int, size.value.split('x'))

        # Create colored background based on personality
        color_map = {
            "pragmatist": (41, 72, 121),  # Navy blue
            "idealist": (135, 206, 250),  # Sky blue
            "skeptic": (64, 64, 64),  # Dark gray
            "optimist": (255, 215, 0),  # Gold
            "contrarian": (128, 0, 128),  # Purple
            "mediator": (245, 222, 179),  # Beige
            "analyst": (70, 130, 180),  # Steel blue
            "visionary": (138, 43, 226),  # Blue violet
            "traditionalist": (85, 107, 47),  # Dark olive
            "revolutionary": (220, 20, 60),  # Crimson
            "economist": (34, 139, 34),  # Forest green
            "ethicist": (255, 255, 255),  # White
            "technologist": (0, 191, 255),  # Deep sky blue
            "populist": (139, 69, 19),  # Saddle brown
            "philosopher": (75, 0, 130),  # Indigo
        }

        color = color_map.get(personality.lower(), (128, 128, 128))

        # Create image
        img = Image.new('RGB', (width, height), color)
        draw = ImageDraw.Draw(img)

        # Add text
        text = personality.upper()[:3]
        # Use default font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size=width // 4)
        except:
            font = ImageFont.load_default()

        # Center text
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((width - text_width) // 2, (height - text_height) // 2)

        draw.text(position, text, fill=(255, 255, 255), font=font)

        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()

    def _resize_image(self, image_data: bytes, target_size: AvatarSize) -> bytes:
        """Resize image to target size"""
        if not PIL_AVAILABLE:
            return image_data

        from PIL import Image

        img = Image.open(io.BytesIO(image_data))
        width, height = map(int, target_size.value.split('x'))
        img = img.resize((width, height), Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()

    def _minimal_png(self) -> bytes:
        """Return minimal valid PNG (1x1 transparent pixel)"""
        return base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )


async def create_dalle3_generator(api_key: Optional[str] = None, **kwargs) -> AvatarGenerator:
    """Create DALL-E 3 avatar generator"""
    return AvatarGenerator(provider=AvatarProvider.DALLE3, api_key=api_key, **kwargs)


async def create_replicate_generator(api_key: Optional[str] = None, **kwargs) -> AvatarGenerator:
    """Create Replicate avatar generator"""
    return AvatarGenerator(provider=AvatarProvider.REPLICATE, api_key=api_key, **kwargs)


async def create_mock_generator(**kwargs) -> AvatarGenerator:
    """Create mock avatar generator (for testing)"""
    return AvatarGenerator(provider=AvatarProvider.MOCK, **kwargs)
