"""
Base Agent - Foundation for AI Council Agents

Provides the base class for all AI agents participating in council debates.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import logging
import uuid

logger = logging.getLogger(__name__)


class AgentPersonality(Enum):
    """Different personality archetypes for debate agents"""
    OPTIMIST = "optimist"
    PESSIMIST = "pessimist"
    PRAGMATIST = "pragmatist"
    IDEALIST = "idealist"
    CONTRARIAN = "contrarian"
    MODERATE = "moderate"
    RADICAL = "radical"
    CONSERVATIVE = "conservative"
    PROGRESSIVE = "progressive"


@dataclass
class AgentConfig:
    """Configuration for an AI agent"""
    name: str
    personality: AgentPersonality
    model: str = "gpt-4"  # Default LLM model
    temperature: float = 0.7
    max_tokens: int = 500
    backstory: Optional[str] = None
    expertise_areas: List[str] = field(default_factory=list)
    bias_level: float = 0.5  # 0.0 = neutral, 1.0 = heavily biased
    debating_style: str = "analytical"  # analytical, emotional, humorous, aggressive


class BaseAgent(ABC):
    """
    Base class for AI agents in the council system

    Provides core functionality for agent identity, state management,
    and interaction with the debate system.
    """

    def __init__(self, config: AgentConfig):
        self.agent_id = str(uuid.uuid4())
        self.config = config
        self.name = config.name
        self.personality = config.personality
        self.conversation_history: List[Dict[str, str]] = []
        self.stance_history: List[Dict[str, Any]] = []
        self.total_contributions = 0
        self.debate_wins = 0
        self.active = True

        logger.info(f"Initialized agent: {self.name} ({self.personality.value})")

    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a response to a prompt

        Args:
            prompt: The input prompt
            context: Additional context for response generation

        Returns:
            Generated response text
        """
        pass

    async def form_opinion(
        self,
        topic: str,
        facts: List[str],
        previous_arguments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Form an opinion on a topic based on facts and previous arguments

        Args:
            topic: The debate topic
            facts: List of factual statements about the topic
            previous_arguments: Previous arguments made in the debate

        Returns:
            Dictionary containing stance, reasoning, and confidence
        """
        context = {
            "topic": topic,
            "facts": facts,
            "previous_arguments": previous_arguments or [],
            "personality": self.personality.value,
            "expertise": self.config.expertise_areas,
        }

        prompt = self._build_opinion_prompt(context)
        response = await self.generate_response(prompt, context)

        opinion = self._parse_opinion_response(response)
        self.stance_history.append(opinion)

        return opinion

    async def respond_to_argument(
        self,
        original_argument: str,
        opponent_name: str,
        debate_context: Dict[str, Any]
    ) -> str:
        """
        Respond to an opponent's argument

        Args:
            original_argument: The argument to respond to
            opponent_name: Name of the opponent
            debate_context: Current debate context

        Returns:
            Counter-argument or response
        """
        context = {
            **debate_context,
            "opponent_argument": original_argument,
            "opponent_name": opponent_name,
            "my_personality": self.personality.value,
        }

        prompt = self._build_response_prompt(context)
        response = await self.generate_response(prompt, context)

        self.total_contributions += 1
        self._add_to_history("response", response)

        return response

    def _build_opinion_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for opinion formation"""
        personality_description = self._get_personality_description()

        prompt = f"""You are {self.name}, an AI agent with a {self.personality.value} personality.

{personality_description}

Topic: {context['topic']}

Facts:
{self._format_list(context['facts'])}

"""

        if context.get('expertise'):
            prompt += f"Your areas of expertise: {', '.join(context['expertise'])}\n\n"

        if context.get('previous_arguments'):
            prompt += f"""Previous arguments in this debate:
{self._format_list(context['previous_arguments'])}

"""

        if self.config.backstory:
            prompt += f"Your background: {self.config.backstory}\n\n"

        prompt += """Based on the above, form your opinion on this topic. Provide:
1. Your stance (support/oppose/neutral)
2. Your main argument (2-3 sentences)
3. Your confidence level (0.0-1.0)

Format your response as:
STANCE: [your stance]
ARGUMENT: [your argument]
CONFIDENCE: [0.0-1.0]
"""

        return prompt

    def _build_response_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for responding to arguments"""
        personality_description = self._get_personality_description()

        prompt = f"""You are {self.name}, an AI agent with a {self.personality.value} personality participating in a live debate.

{personality_description}

Current debate topic: {context.get('topic', 'Unknown')}

{context['opponent_name']} just argued:
"{context['opponent_argument']}"

Your task: Respond to this argument in character. You may:
- Counter their points
- Provide additional evidence
- Ask critical questions
- Find common ground
- Escalate or de-escalate as fits your personality

Keep your response concise (2-4 sentences) and engaging for a live stream audience.

Your response:
"""

        return prompt

    def _get_personality_description(self) -> str:
        """Get description of agent's personality"""
        descriptions = {
            AgentPersonality.OPTIMIST: "You tend to see the positive side of issues and believe in progress and improvement.",
            AgentPersonality.PESSIMIST: "You tend to be skeptical and focus on potential problems and risks.",
            AgentPersonality.PRAGMATIST: "You focus on practical solutions and real-world feasibility.",
            AgentPersonality.IDEALIST: "You are driven by principles and ideals, even if they seem impractical.",
            AgentPersonality.CONTRARIAN: "You naturally question consensus and take opposing viewpoints.",
            AgentPersonality.MODERATE: "You seek balance and compromise between different perspectives.",
            AgentPersonality.RADICAL: "You advocate for fundamental, transformative change.",
            AgentPersonality.CONSERVATIVE: "You value tradition, stability, and incremental change.",
            AgentPersonality.PROGRESSIVE: "You push for reform and forward-thinking solutions.",
        }

        return descriptions.get(self.personality, "You engage thoughtfully with topics.")

    def _parse_opinion_response(self, response: str) -> Dict[str, Any]:
        """Parse structured opinion from response"""
        opinion = {
            "stance": "neutral",
            "argument": response,
            "confidence": 0.5,
            "agent_id": self.agent_id,
            "agent_name": self.name,
        }

        # Try to parse structured format
        lines = response.strip().split('\n')
        for line in lines:
            if line.startswith("STANCE:"):
                opinion["stance"] = line.replace("STANCE:", "").strip().lower()
            elif line.startswith("ARGUMENT:"):
                opinion["argument"] = line.replace("ARGUMENT:", "").strip()
            elif line.startswith("CONFIDENCE:"):
                try:
                    opinion["confidence"] = float(line.replace("CONFIDENCE:", "").strip())
                except ValueError:
                    pass

        return opinion

    def _add_to_history(self, message_type: str, content: str) -> None:
        """Add message to conversation history"""
        self.conversation_history.append({
            "type": message_type,
            "content": content,
            "agent": self.name,
        })

    def _format_list(self, items: List[str]) -> str:
        """Format list of items for prompt"""
        return '\n'.join(f"- {item}" for item in items)

    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "personality": self.personality.value,
            "total_contributions": self.total_contributions,
            "debate_wins": self.debate_wins,
            "active": self.active,
        }

    def reset_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history.clear()
        logger.info(f"Reset history for agent: {self.name}")
