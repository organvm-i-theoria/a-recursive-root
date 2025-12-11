"""
Capabilities - Defines agent capabilities and skill matching

Provides capability definitions and utilities for matching
agent skills to role requirements.
"""

from typing import Dict, List, Set
from enum import Enum
from dataclasses import dataclass


class CapabilityLevel(Enum):
    """
    Enumeration of the proficiency levels for a capability.
    """
    NOVICE = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4


@dataclass
class Capability:
    """
    Represents a capability that an agent can possess.

    Attributes:
        name: The name of the capability.
        level: The proficiency level of the agent in this capability.
        related_skills: A list of skills related to this capability.
        description: A description of the capability.
    """
    name: str
    level: CapabilityLevel
    related_skills: List[str]
    description: str


# Core Capability Definitions
CAPABILITY_DEFINITIONS: Dict[str, Dict[str, str]] = {
    # Technical Capabilities
    "coding": {
        "description": "Ability to write code in various programming languages",
        "related_skills": ["python", "typescript", "javascript", "solidity"],
    },
    "architecture": {
        "description": "System design and architectural decision making",
        "related_skills": ["design", "systems_thinking", "scalability"],
    },
    "testing": {
        "description": "Software testing and quality assurance",
        "related_skills": ["qa", "automation", "test_planning"],
    },
    "debugging": {
        "description": "Identify and fix software bugs",
        "related_skills": ["troubleshooting", "analysis", "problem_solving"],
    },
    "documentation": {
        "description": "Create technical documentation",
        "related_skills": ["writing", "technical_writing", "markdown"],
    },

    # Frontend Capabilities
    "frontend": {
        "description": "Frontend development and UI implementation",
        "related_skills": ["react", "css", "html", "javascript"],
    },
    "ui_development": {
        "description": "User interface design and implementation",
        "related_skills": ["ux", "design", "frontend"],
    },
    "react": {
        "description": "React framework development",
        "related_skills": ["javascript", "typescript", "jsx"],
    },

    # Backend Capabilities
    "backend": {
        "description": "Server-side development",
        "related_skills": ["api", "database", "server"],
    },
    "api_development": {
        "description": "REST and GraphQL API development",
        "related_skills": ["backend", "http", "websocket"],
    },
    "database": {
        "description": "Database design and management",
        "related_skills": ["sql", "nosql", "data_modeling"],
    },

    # Blockchain Capabilities
    "blockchain": {
        "description": "Blockchain development and integration",
        "related_skills": ["web3", "smart_contracts", "cryptography"],
    },
    "solidity": {
        "description": "Solidity smart contract development",
        "related_skills": ["ethereum", "smart_contracts", "blockchain"],
    },
    "web3": {
        "description": "Web3 integration and blockchain interaction",
        "related_skills": ["blockchain", "wallets", "tokens"],
    },

    # Research & Analysis
    "research": {
        "description": "Research and investigation",
        "related_skills": ["analysis", "literature_review", "data_collection"],
    },
    "analysis": {
        "description": "Data and information analysis",
        "related_skills": ["critical_thinking", "data_analysis", "statistics"],
    },
    "data_analysis": {
        "description": "Analyze datasets and extract insights",
        "related_skills": ["statistics", "visualization", "python"],
    },

    # Communication & Documentation
    "writing": {
        "description": "Written communication",
        "related_skills": ["technical_writing", "documentation", "editing"],
    },
    "technical_writing": {
        "description": "Technical documentation writing",
        "related_skills": ["documentation", "writing", "clarity"],
    },
    "communication": {
        "description": "Effective communication with stakeholders",
        "related_skills": ["writing", "presentation", "facilitation"],
    },

    # Project Management
    "project_management": {
        "description": "Project planning and execution",
        "related_skills": ["planning", "coordination", "risk_management"],
    },
    "planning": {
        "description": "Strategic and tactical planning",
        "related_skills": ["organization", "scheduling", "prioritization"],
    },
    "coordination": {
        "description": "Team and task coordination",
        "related_skills": ["communication", "organization", "facilitation"],
    },

    # AI Council Specific
    "moderation": {
        "description": "Moderate discussions and debates",
        "related_skills": ["facilitation", "conflict_resolution", "communication"],
    },
    "argumentation": {
        "description": "Construct and present arguments",
        "related_skills": ["reasoning", "logic", "persuasion"],
    },
    "reasoning": {
        "description": "Logical reasoning and critical thinking",
        "related_skills": ["logic", "analysis", "problem_solving"],
    },
    "curation": {
        "description": "Content curation and selection",
        "related_skills": ["analysis", "prioritization", "judgment"],
    },
    "streaming": {
        "description": "Live streaming management",
        "related_skills": ["obs", "audio_video", "broadcasting"],
    },
    "economics": {
        "description": "Economic analysis and modeling",
        "related_skills": ["tokenomics", "game_theory", "mathematics"],
    },
}


class CapabilityMatcher:
    """
    Matches agent capabilities to role requirements.

    This class provides a set of utilities for evaluating how well an agent's
    capabilities align with the requirements of a role.
    """

    def __init__(self):
        """
        Initializes the CapabilityMatcher.
        """
        self.capabilities = CAPABILITY_DEFINITIONS

    def get_capability_info(self, capability: str) -> Dict[str, str]:
        """
        Gets information about a specific capability.

        Args:
            capability: The name of the capability.

        Returns:
            A dictionary containing information about the capability, or an empty dictionary if the capability is not found.
        """
        return self.capabilities.get(capability, {})

    def get_related_capabilities(self, capability: str) -> Set[str]:
        """
        Gets a set of capabilities related to a given capability.

        Args:
            capability: The name of the capability.

        Returns:
            A set of related capability names.
        """
        info = self.get_capability_info(capability)
        related = set(info.get("related_skills", []))

        # Find capabilities that list this one as related
        for cap_name, cap_info in self.capabilities.items():
            if capability in cap_info.get("related_skills", []):
                related.add(cap_name)

        return related

    def calculate_match_score(
        self,
        agent_capabilities: List[str],
        required_capabilities: List[str]
    ) -> float:
        """
        Calculates a match score indicating how well an agent's capabilities match a set of required capabilities.

        The score is a float between 0.0 and 1.0, where 1.0 represents a perfect match.

        Args:
            agent_capabilities: A list of the agent's capabilities.
            required_capabilities: A list of the required capabilities.

        Returns:
            A match score between 0.0 and 1.0.
        """
        if not required_capabilities:
            return 1.0

        # Direct matches
        agent_caps_set = set(agent_capabilities)
        required_set = set(required_capabilities)
        direct_matches = len(agent_caps_set & required_set)

        # Related matches (weighted less)
        related_matches = 0
        for required in required_set - agent_caps_set:
            related = self.get_related_capabilities(required)
            if agent_caps_set & related:
                related_matches += 0.5

        total_matches = direct_matches + related_matches
        max_score = len(required_capabilities)

        return min(1.0, total_matches / max_score) if max_score > 0 else 0.0

    def get_missing_capabilities(
        self,
        agent_capabilities: List[str],
        required_capabilities: List[str]
    ) -> List[str]:
        """
        Gets a list of capabilities that are required but not possessed by the agent.

        Args:
            agent_capabilities: A list of the agent's capabilities.
            required_capabilities: A list of the required capabilities.

        Returns:
            A list of missing capability names.
        """
        agent_set = set(agent_capabilities)
        required_set = set(required_capabilities)
        return list(required_set - agent_set)

    def get_capability_gap(
        self,
        agent_capabilities: List[str],
        required_capabilities: List[str]
    ) -> Dict[str, List[str]]:
        """
        Analyzes the capability gap between an agent and a set of requirements.

        Args:
            agent_capabilities: A list of the agent's capabilities.
            required_capabilities: A list of the required capabilities.

        Returns:
            A dictionary with three keys: "missing", "has", and "related", each containing a list of capability names.
        """
        agent_set = set(agent_capabilities)
        required_set = set(required_capabilities)

        missing = list(required_set - agent_set)
        has = list(required_set & agent_set)

        # Check for related capabilities
        related = {}
        for req in missing:
            related_caps = self.get_related_capabilities(req)
            agent_related = list(agent_set & related_caps)
            if agent_related:
                related[req] = agent_related

        return {
            "missing": missing,
            "has": has,
            "related": related,
        }

    def suggest_training(
        self,
        agent_capabilities: List[str],
        target_role_capabilities: List[str]
    ) -> List[str]:
        """
        Suggests a list of capabilities that an agent should learn to be better suited for a target role.

        Args:
            agent_capabilities: A list of the agent's current capabilities.
            target_role_capabilities: A list of the capabilities required for the target role.

        Returns:
            A prioritized list of suggested capabilities to learn.
        """
        gap = self.get_capability_gap(agent_capabilities, target_role_capabilities)
        missing = gap["missing"]

        # Prioritize capabilities without related skills
        priority = []
        secondary = []

        for cap in missing:
            if cap in gap["related"]:
                secondary.append(cap)  # Has related skills, easier to learn
            else:
                priority.append(cap)  # No related skills, harder to learn

        return priority + secondary

    def can_substitute(
        self,
        agent_capability: str,
        required_capability: str
    ) -> bool:
        """
        Checks if an agent's capability can be used as a substitute for a required capability.

        Args:
            agent_capability: The capability that the agent possesses.
            required_capability: The capability that is required.

        Returns:
            True if the agent's capability can substitute for the required one, False otherwise.
        """
        if agent_capability == required_capability:
            return True

        # Check if they're related
        related = self.get_related_capabilities(required_capability)
        return agent_capability in related

    def rank_agents_for_role(
        self,
        agents: List[Dict[str, any]],
        required_capabilities: List[str]
    ) -> List[tuple]:
        """
        Ranks a list of agents based on their fitness for a role with a given set of required capabilities.

        Args:
            agents: A list of agent dictionaries, where each dictionary has a "capabilities" key.
            required_capabilities: A list of the capabilities required for the role.

        Returns:
            A list of (agent, score) tuples, sorted in descending order of score.
        """
        rankings = []

        for agent in agents:
            agent_caps = agent.get("capabilities", [])
            score = self.calculate_match_score(agent_caps, required_capabilities)
            rankings.append((agent, score))

        # Sort by score descending
        rankings.sort(key=lambda x: x[1], reverse=True)

        return rankings


# Global capability matcher instance
_capability_matcher: CapabilityMatcher = None


def get_capability_matcher() -> CapabilityMatcher:
    """
    Gets the global instance of the CapabilityMatcher.

    Returns:
        The global CapabilityMatcher instance.
    """
    global _capability_matcher
    if _capability_matcher is None:
        _capability_matcher = CapabilityMatcher()
    return _capability_matcher
