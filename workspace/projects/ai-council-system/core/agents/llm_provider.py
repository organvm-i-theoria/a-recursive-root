"""
LLM Provider - Abstraction layer for multiple LLM providers

Provides unified interface for Claude, GPT-4, Grok, and other LLMs.
"""

from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator, Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging
import asyncio

logger = logging.getLogger(__name__)


class LLMProviderType(Enum):
    """Supported LLM providers"""
    CLAUDE = "claude"
    GPT = "gpt"
    GROK = "grok"
    MOCK = "mock"  # For testing


@dataclass
class LLMConfig:
    """Configuration for LLM provider"""
    provider_type: LLMProviderType
    model: str
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    default_temperature: float = 0.7
    default_max_tokens: int = 1000
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0


@dataclass
class LLMUsage:
    """Token usage statistics"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class LLMResponse:
    """Response from LLM provider"""
    content: str
    model: str
    usage: Optional[LLMUsage] = None
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = None


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers

    Provides unified interface for different LLM APIs.
    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self.request_count = 0
        self.total_tokens = 0

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate completion from prompt

        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific parameters

        Returns:
            Generated text
        """
        pass

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream completion from prompt

        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Provider-specific parameters

        Yields:
            Text chunks as they're generated
        """
        pass

    async def generate_with_retry(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate with automatic retry on failure"""
        attempts = 0
        last_error = None

        while attempts < self.config.retry_attempts:
            try:
                return await self.generate(prompt, temperature, max_tokens, **kwargs)
            except Exception as e:
                attempts += 1
                last_error = e
                logger.warning(
                    f"LLM generation attempt {attempts} failed: {e}"
                )

                if attempts < self.config.retry_attempts:
                    await asyncio.sleep(self.config.retry_delay * attempts)

        raise last_error

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "provider": self.config.provider_type.value,
            "model": self.config.model,
            "request_count": self.request_count,
            "total_tokens": self.total_tokens,
        }

    def _get_temperature(self, temperature: Optional[float]) -> float:
        """Get temperature with fallback to default"""
        return temperature if temperature is not None else self.config.default_temperature

    def _get_max_tokens(self, max_tokens: Optional[int]) -> int:
        """Get max tokens with fallback to default"""
        return max_tokens if max_tokens is not None else self.config.default_max_tokens


class ClaudeProvider(LLMProvider):
    """
    Anthropic Claude provider

    Uses Anthropic's API for Claude models.
    """

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = None  # Would initialize Anthropic client here

    async def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate using Claude"""
        logger.debug(f"Claude generation request: {len(prompt)} chars")

        # Placeholder implementation
        # Real implementation would use anthropic library:
        # from anthropic import AsyncAnthropic
        # client = AsyncAnthropic(api_key=self.config.api_key)
        # message = await client.messages.create(
        #     model=self.config.model,
        #     max_tokens=self._get_max_tokens(max_tokens),
        #     temperature=self._get_temperature(temperature),
        #     messages=[{"role": "user", "content": prompt}]
        # )
        # return message.content[0].text

        self.request_count += 1
        return f"[Claude {self.config.model} response to: {prompt[:50]}...]"

    async def stream(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream using Claude"""
        # Placeholder implementation
        # Real implementation would stream from Anthropic API

        response = await self.generate(prompt, temperature, max_tokens, **kwargs)
        words = response.split()

        for word in words:
            yield word + " "
            await asyncio.sleep(0.01)


class GPTProvider(LLMProvider):
    """
    OpenAI GPT provider

    Uses OpenAI's API for GPT models.
    """

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = None  # Would initialize OpenAI client here

    async def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate using GPT"""
        logger.debug(f"GPT generation request: {len(prompt)} chars")

        # Placeholder implementation
        # Real implementation would use openai library:
        # from openai import AsyncOpenAI
        # client = AsyncOpenAI(api_key=self.config.api_key)
        # response = await client.chat.completions.create(
        #     model=self.config.model,
        #     messages=[{"role": "user", "content": prompt}],
        #     temperature=self._get_temperature(temperature),
        #     max_tokens=self._get_max_tokens(max_tokens)
        # )
        # return response.choices[0].message.content

        self.request_count += 1
        return f"[GPT {self.config.model} response to: {prompt[:50]}...]"

    async def stream(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream using GPT"""
        # Placeholder implementation
        response = await self.generate(prompt, temperature, max_tokens, **kwargs)
        words = response.split()

        for word in words:
            yield word + " "
            await asyncio.sleep(0.01)


class GrokProvider(LLMProvider):
    """
    xAI Grok provider

    Uses xAI's API for Grok models.
    """

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = None  # Would initialize xAI client here

    async def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate using Grok"""
        logger.debug(f"Grok generation request: {len(prompt)} chars")

        # Placeholder implementation
        # Real implementation would use xAI API

        self.request_count += 1
        return f"[Grok {self.config.model} response to: {prompt[:50]}...]"

    async def stream(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream using Grok"""
        # Placeholder implementation
        response = await self.generate(prompt, temperature, max_tokens, **kwargs)
        words = response.split()

        for word in words:
            yield word + " "
            await asyncio.sleep(0.01)


class MockLLMProvider(LLMProvider):
    """
    Mock LLM provider for testing

    Returns predefined responses without calling external APIs.
    """

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.responses = []
        self.response_index = 0

    def set_responses(self, responses: list[str]):
        """Set predefined responses for testing"""
        self.responses = responses
        self.response_index = 0

    async def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate mock response"""
        self.request_count += 1

        if self.responses and self.response_index < len(self.responses):
            response = self.responses[self.response_index]
            self.response_index += 1
            return response

        # Default mock response
        return f"Mock response to: {prompt[:100]}..."

    async def stream(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream mock response"""
        response = await self.generate(prompt, temperature, max_tokens, **kwargs)
        words = response.split()

        for word in words:
            yield word + " "
            await asyncio.sleep(0.001)  # Fast for testing


class LLMProviderFactory:
    """Factory for creating LLM providers"""

    @staticmethod
    def create(config: LLMConfig) -> LLMProvider:
        """Create provider based on configuration"""
        providers = {
            LLMProviderType.CLAUDE: ClaudeProvider,
            LLMProviderType.GPT: GPTProvider,
            LLMProviderType.GROK: GrokProvider,
            LLMProviderType.MOCK: MockLLMProvider,
        }

        provider_class = providers.get(config.provider_type)
        if not provider_class:
            raise ValueError(f"Unknown provider type: {config.provider_type}")

        return provider_class(config)

    @staticmethod
    def create_claude(
        model: str = "claude-3-5-sonnet-20250219",
        api_key: Optional[str] = None,
        **kwargs
    ) -> ClaudeProvider:
        """Convenience method to create Claude provider"""
        config = LLMConfig(
            provider_type=LLMProviderType.CLAUDE,
            model=model,
            api_key=api_key,
            **kwargs
        )
        return ClaudeProvider(config)

    @staticmethod
    def create_gpt(
        model: str = "gpt-4-turbo",
        api_key: Optional[str] = None,
        **kwargs
    ) -> GPTProvider:
        """Convenience method to create GPT provider"""
        config = LLMConfig(
            provider_type=LLMProviderType.GPT,
            model=model,
            api_key=api_key,
            **kwargs
        )
        return GPTProvider(config)

    @staticmethod
    def create_grok(
        model: str = "grok-1",
        api_key: Optional[str] = None,
        **kwargs
    ) -> GrokProvider:
        """Convenience method to create Grok provider"""
        config = LLMConfig(
            provider_type=LLMProviderType.GROK,
            model=model,
            api_key=api_key,
            **kwargs
        )
        return GrokProvider(config)

    @staticmethod
    def create_mock(responses: Optional[list[str]] = None) -> MockLLMProvider:
        """Convenience method to create mock provider"""
        config = LLMConfig(
            provider_type=LLMProviderType.MOCK,
            model="mock-model"
        )
        provider = MockLLMProvider(config)
        if responses:
            provider.set_responses(responses)
        return provider
