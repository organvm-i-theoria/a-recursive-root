"""
Debate Agent - AI agent with LLM integration for debates

Implements the BaseAgent with actual LLM providers (OpenAI, Anthropic, or Mock).
"""

from typing import Dict, Optional, Any
import os
import logging
from .base_agent import BaseAgent, AgentConfig

logger = logging.getLogger(__name__)


class DebateAgent(BaseAgent):
    """
    AI debate agent with LLM integration

    Supports multiple LLM providers:
    - OpenAI (GPT-4, GPT-3.5)
    - Anthropic (Claude)
    - Mock (for testing without API keys)
    """

    def __init__(self, config: AgentConfig, provider: str = "auto"):
        """
        Initialize debate agent

        Args:
            config: Agent configuration
            provider: LLM provider ("openai", "anthropic", "mock", or "auto")
        """
        super().__init__(config)

        self.provider = provider
        self.client = None

        if provider == "auto":
            self.provider = self._detect_provider()

        self._initialize_client()

    def _detect_provider(self) -> str:
        """Detect which provider to use based on available API keys"""
        if os.getenv("OPENAI_API_KEY"):
            logger.info("Detected OpenAI API key, using OpenAI provider")
            return "openai"
        elif os.getenv("ANTHROPIC_API_KEY"):
            logger.info("Detected Anthropic API key, using Anthropic provider")
            return "anthropic"
        else:
            logger.warning("No API keys found, using mock provider")
            return "mock"

    def _initialize_client(self) -> None:
        """Initialize LLM client based on provider"""
        if self.provider == "openai":
            self._initialize_openai()
        elif self.provider == "anthropic":
            self._initialize_anthropic()
        elif self.provider == "mock":
            self._initialize_mock()
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _initialize_openai(self) -> None:
        """Initialize OpenAI client"""
        try:
            from openai import AsyncOpenAI
            api_key = os.getenv("OPENAI_API_KEY")

            if not api_key:
                logger.warning("OPENAI_API_KEY not found, falling back to mock")
                self.provider = "mock"
                self._initialize_mock()
                return

            self.client = AsyncOpenAI(api_key=api_key)
            logger.info(f"Initialized OpenAI client for {self.name}")

        except ImportError:
            logger.warning("openai package not installed, falling back to mock")
            self.provider = "mock"
            self._initialize_mock()

    def _initialize_anthropic(self) -> None:
        """Initialize Anthropic client"""
        try:
            from anthropic import AsyncAnthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")

            if not api_key:
                logger.warning("ANTHROPIC_API_KEY not found, falling back to mock")
                self.provider = "mock"
                self._initialize_mock()
                return

            self.client = AsyncAnthropic(api_key=api_key)
            logger.info(f"Initialized Anthropic client for {self.name}")

        except ImportError:
            logger.warning("anthropic package not installed, falling back to mock")
            self.provider = "mock"
            self._initialize_mock()

    def _initialize_mock(self) -> None:
        """Initialize mock client for testing"""
        self.client = MockLLMClient(self.config)
        logger.info(f"Initialized mock client for {self.name}")

    async def generate_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate response using configured LLM provider

        Args:
            prompt: Input prompt
            context: Additional context

        Returns:
            Generated response
        """
        try:
            if self.provider == "openai":
                return await self._generate_openai(prompt, context)
            elif self.provider == "anthropic":
                return await self._generate_anthropic(prompt, context)
            elif self.provider == "mock":
                return await self._generate_mock(prompt, context)
            else:
                raise ValueError(f"Unknown provider: {self.provider}")

        except Exception as e:
            logger.error(f"Error generating response for {self.name}: {e}")
            # Fallback to mock on error
            if self.provider != "mock":
                logger.info("Falling back to mock provider")
                return await self._generate_mock(prompt, context)
            raise

    async def _generate_openai(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate response using OpenAI"""
        messages = [{"role": "user", "content": prompt}]

        response = await self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        return response.choices[0].message.content

    async def _generate_anthropic(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate response using Anthropic Claude"""
        # Map model names
        model_map = {
            "gpt-4": "claude-3-opus-20240229",
            "gpt-3.5-turbo": "claude-3-sonnet-20240229",
        }

        model = model_map.get(self.config.model, "claude-3-sonnet-20240229")

        response = await self.client.messages.create(
            model=model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text

    async def _generate_mock(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate response using mock client"""
        return await self.client.generate(prompt, context, self.personality)


class MockLLMClient:
    """
    Mock LLM client for testing without API keys

    Generates personality-appropriate responses based on simple rules.
    """

    def __init__(self, config: AgentConfig):
        self.config = config

    async def generate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]],
        personality
    ) -> str:
        """Generate mock response based on personality"""
        # Extract what we're responding to
        is_opinion = "Form your opinion" in prompt or "STANCE:" in prompt
        is_response = "just argued:" in prompt

        name = self.config.name
        personality_val = personality.value

        if is_opinion:
            return self._generate_mock_opinion(personality, context)
        elif is_response:
            return self._generate_mock_response(personality, context, prompt)
        else:
            return f"This is {name} ({personality_val}) responding to your prompt."

    def _generate_mock_opinion(self, personality, context) -> str:
        """Generate mock opinion"""
        from .base_agent import AgentPersonality

        stances = {
            AgentPersonality.OPTIMIST: ("support", 0.8),
            AgentPersonality.PESSIMIST: ("oppose", 0.7),
            AgentPersonality.PRAGMATIST: ("neutral", 0.6),
            AgentPersonality.IDEALIST: ("support", 0.9),
            AgentPersonality.CONTRARIAN: ("oppose", 0.75),
            AgentPersonality.MODERATE: ("neutral", 0.5),
            AgentPersonality.RADICAL: ("support", 0.85),
            AgentPersonality.CONSERVATIVE: ("oppose", 0.7),
            AgentPersonality.PROGRESSIVE: ("support", 0.8),
        }

        stance, confidence = stances.get(personality, ("neutral", 0.5))

        arguments = {
            "support": "I believe this represents a positive development that could lead to beneficial outcomes.",
            "oppose": "I have concerns about the potential risks and unintended consequences of this approach.",
            "neutral": "I see merit in both perspectives and believe we need more information to make a determination.",
        }

        return f"""STANCE: {stance}
ARGUMENT: {arguments[stance]} We should carefully consider all perspectives before proceeding.
CONFIDENCE: {confidence}"""

    def _generate_mock_response(self, personality, context, prompt) -> str:
        """Generate mock response to argument"""
        from .base_agent import AgentPersonality

        responses = {
            AgentPersonality.OPTIMIST: "I appreciate your perspective, but I think we should focus on the opportunities here rather than the obstacles.",
            AgentPersonality.PESSIMIST: "That's a nice thought, but we need to be realistic about the challenges and potential for failure.",
            AgentPersonality.PRAGMATIST: "Let's ground this discussion in practical terms and focus on what's actually achievable.",
            AgentPersonality.IDEALIST: "We shouldn't compromise our principles just because something seems difficult.",
            AgentPersonality.CONTRARIAN: "I respectfully disagree with that entire premise. Let me offer an alternative view.",
            AgentPersonality.MODERATE: "I think there's truth in what you're saying, but we should also consider the opposing viewpoint.",
            AgentPersonality.RADICAL: "That's far too incremental. We need to think bigger and push for fundamental transformation.",
            AgentPersonality.CONSERVATIVE: "We should be very cautious about making changes without fully understanding the implications.",
            AgentPersonality.PROGRESSIVE: "We need to move forward boldly rather than being held back by outdated thinking.",
        }

        return responses.get(personality, "That's an interesting point worth considering.")
