"""
AI Agents Module

Core agent implementation for AI Council System debates.
"""

from .agent import (
    Agent,
    AgentState,
    Personality,
    DebateContext,
    AgentResponse,
    Vote,
)

from .llm_provider import (
    LLMProvider,
    LLMConfig,
    LLMProviderType,
    LLMProviderFactory,
    ClaudeProvider,
    GPTProvider,
    GrokProvider,
    MockLLMProvider,
)

from .memory import (
    MemoryManager,
    Memory,
)

from .personalities import (
    PERSONALITIES,
    get_personality,
    get_all_personalities,
    get_personality_names,
    create_custom_personality,
)

__all__ = [
    # Agent
    "Agent",
    "AgentState",
    "Personality",
    "DebateContext",
    "AgentResponse",
    "Vote",
    # LLM Provider
    "LLMProvider",
    "LLMConfig",
    "LLMProviderType",
    "LLMProviderFactory",
    "ClaudeProvider",
    "GPTProvider",
    "GrokProvider",
    "MockLLMProvider",
    # Memory
    "MemoryManager",
    "Memory",
    # Personalities
    "PERSONALITIES",
    "get_personality",
    "get_all_personalities",
    "get_personality_names",
    "create_custom_personality",
]

__version__ = "0.1.0"
