"""
Real LLM Provider Implementations

Production-ready implementations with actual API calls.
Requires: anthropic, openai libraries
"""

import asyncio
import logging
from typing import Optional, AsyncIterator, Dict, Any

from .llm_provider import (
    LLMProvider,
    LLMConfig,
    LLMProviderType,
    LLMUsage,
    LLMResponse,
)

logger = logging.getLogger(__name__)


class RealClaudeProvider(LLMProvider):
    """
    Anthropic Claude provider with real API calls

    Requires: pip install anthropic
    """

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Anthropic client"""
        try:
            from anthropic import AsyncAnthropic

            if not self.config.api_key:
                raise ValueError("Anthropic API key not provided")

            self.client = AsyncAnthropic(
                api_key=self.config.api_key,
                timeout=self.config.timeout,
            )
            logger.info("Anthropic client initialized successfully")

        except ImportError:
            logger.error(
                "anthropic library not installed. "
                "Install with: pip install anthropic"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise

    async def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate completion using Claude"""
        if not self.client:
            raise RuntimeError("Anthropic client not initialized")

        logger.debug(f"Claude generation request: {len(prompt)} chars")

        try:
            message = await self.client.messages.create(
                model=self.config.model,
                max_tokens=self._get_max_tokens(max_tokens),
                temperature=self._get_temperature(temperature),
                messages=[{"role": "user", "content": prompt}],
            )

            self.request_count += 1
            self.total_tokens += message.usage.input_tokens + message.usage.output_tokens

            content = message.content[0].text

            logger.debug(
                f"Claude response: {len(content)} chars, "
                f"tokens: {message.usage.total_tokens}"
            )

            return content

        except Exception as e:
            logger.error(f"Claude generation failed: {e}")
            raise

    async def stream(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream completion using Claude"""
        if not self.client:
            raise RuntimeError("Anthropic client not initialized")

        try:
            async with self.client.messages.stream(
                model=self.config.model,
                max_tokens=self._get_max_tokens(max_tokens),
                temperature=self._get_temperature(temperature),
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                async for text in stream.text_stream:
                    yield text

            self.request_count += 1

        except Exception as e:
            logger.error(f"Claude streaming failed: {e}")
            raise


class RealGPTProvider(LLMProvider):
    """
    OpenAI GPT provider with real API calls

    Requires: pip install openai
    """

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize OpenAI client"""
        try:
            from openai import AsyncOpenAI

            if not self.config.api_key:
                raise ValueError("OpenAI API key not provided")

            self.client = AsyncOpenAI(
                api_key=self.config.api_key,
                timeout=self.config.timeout,
            )
            logger.info("OpenAI client initialized successfully")

        except ImportError:
            logger.error(
                "openai library not installed. "
                "Install with: pip install openai"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    async def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate completion using GPT"""
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")

        logger.debug(f"GPT generation request: {len(prompt)} chars")

        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self._get_temperature(temperature),
                max_tokens=self._get_max_tokens(max_tokens),
            )

            self.request_count += 1
            self.total_tokens += response.usage.total_tokens

            content = response.choices[0].message.content

            logger.debug(
                f"GPT response: {len(content)} chars, "
                f"tokens: {response.usage.total_tokens}"
            )

            return content

        except Exception as e:
            logger.error(f"GPT generation failed: {e}")
            raise

    async def stream(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream completion using GPT"""
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")

        try:
            stream = await self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self._get_temperature(temperature),
                max_tokens=self._get_max_tokens(max_tokens),
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

            self.request_count += 1

        except Exception as e:
            logger.error(f"GPT streaming failed: {e}")
            raise


class RealGrokProvider(LLMProvider):
    """
    xAI Grok provider with real API calls

    Note: xAI API similar to OpenAI format
    Requires: pip install openai (uses OpenAI-compatible client)
    """

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize xAI client"""
        try:
            from openai import AsyncOpenAI

            if not self.config.api_key:
                raise ValueError("xAI API key not provided")

            # xAI uses OpenAI-compatible API
            self.client = AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self.config.api_base_url or "https://api.x.ai/v1",
                timeout=self.config.timeout,
            )
            logger.info("xAI Grok client initialized successfully")

        except ImportError:
            logger.error(
                "openai library not installed. "
                "Install with: pip install openai"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to initialize xAI client: {e}")
            raise

    async def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate completion using Grok"""
        if not self.client:
            raise RuntimeError("xAI client not initialized")

        logger.debug(f"Grok generation request: {len(prompt)} chars")

        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self._get_temperature(temperature),
                max_tokens=self._get_max_tokens(max_tokens),
            )

            self.request_count += 1
            if response.usage:
                self.total_tokens += response.usage.total_tokens

            content = response.choices[0].message.content

            logger.debug(f"Grok response: {len(content)} chars")

            return content

        except Exception as e:
            logger.error(f"Grok generation failed: {e}")
            raise

    async def stream(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream completion using Grok"""
        if not self.client:
            raise RuntimeError("xAI client not initialized")

        try:
            stream = await self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self._get_temperature(temperature),
                max_tokens=self._get_max_tokens(max_tokens),
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

            self.request_count += 1

        except Exception as e:
            logger.error(f"Grok streaming failed: {e}")
            raise


# Factory functions for real providers
def create_real_claude(
    api_key: str,
    model: str = "claude-3-5-sonnet-20250219",
    **kwargs
) -> RealClaudeProvider:
    """Create real Claude provider"""
    config = LLMConfig(
        provider_type=LLMProviderType.CLAUDE,
        model=model,
        api_key=api_key,
        **kwargs
    )
    return RealClaudeProvider(config)


def create_real_gpt(
    api_key: str,
    model: str = "gpt-4-turbo",
    **kwargs
) -> RealGPTProvider:
    """Create real GPT provider"""
    config = LLMConfig(
        provider_type=LLMProviderType.GPT,
        model=model,
        api_key=api_key,
        **kwargs
    )
    return RealGPTProvider(config)


def create_real_grok(
    api_key: str,
    model: str = "grok-1",
    **kwargs
) -> RealGrokProvider:
    """Create real Grok provider"""
    config = LLMConfig(
        provider_type=LLMProviderType.GROK,
        model=model,
        api_key=api_key,
        **kwargs
    )
    return RealGrokProvider(config)
