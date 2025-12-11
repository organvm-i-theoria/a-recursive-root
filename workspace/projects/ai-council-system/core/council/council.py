"""
Council - AI Council formation and management

Manages council composition and lifecycle.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CouncilStatus(Enum):
    """Council status states"""
    FORMING = "forming"
    READY = "ready"
    ACTIVE = "active"
    CONCLUDED = "concluded"
    ARCHIVED = "archived"


@dataclass
class Council:
    """
    Represents an AI council

    A council is a group of AI agents formed to debate a specific topic.
    """
    council_id: str
    topic_id: str
    agent_ids: List[str]
    formation_method: str  # "random", "rng", "curated"
    formation_timestamp: datetime = field(default_factory=datetime.utcnow)
    rng_seed: Optional[str] = None
    status: CouncilStatus = CouncilStatus.FORMING
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "council_id": self.council_id,
            "topic_id": self.topic_id,
            "agent_ids": self.agent_ids,
            "formation_method": self.formation_method,
            "formation_timestamp": self.formation_timestamp.isoformat(),
            "rng_seed": self.rng_seed,
            "status": self.status.value,
            "metadata": self.metadata,
        }


class CouncilManager:
    """
    Manages council formation and lifecycle

    Responsible for:
    - Forming councils for debate topics
    - Selecting diverse agents
    - Managing council lifecycle
    """

    def __init__(self):
        self.councils: Dict[str, Council] = {}
        self.councils_formed = 0

    async def form_council(
        self,
        topic_id: str,
        available_agents: List['Agent'],
        council_size: int = 5,
        method: str = "diverse"
    ) -> Council:
        """
        Form a council for a debate topic

        Args:
            topic_id: Topic to debate
            available_agents: Pool of available agents
            council_size: Number of agents in council
            method: Selection method ("diverse", "random", "rng")

        Returns:
            Formed Council object
        """
        logger.info(f"Forming council for topic {topic_id} (size: {council_size})")

        if len(available_agents) < council_size:
            raise ValueError(
                f"Not enough agents available. Need {council_size}, "
                f"have {len(available_agents)}"
            )

        # Select agents based on method
        if method == "diverse":
            selected = await self._select_diverse_agents(
                available_agents,
                council_size
            )
        elif method == "random":
            selected = await self._select_random_agents(
                available_agents,
                council_size
            )
        elif method == "rng":
            selected = await self._select_rng_agents(
                available_agents,
                council_size
            )
        else:
            raise ValueError(f"Unknown selection method: {method}")

        # Create council
        council_id = self._generate_council_id(topic_id)

        council = Council(
            council_id=council_id,
            topic_id=topic_id,
            agent_ids=[a.agent_id for a in selected],
            formation_method=method,
            metadata={
                "personalities": [a.personality.name for a in selected],
                "archetypes": [a.personality.archetype for a in selected],
            }
        )

        council.status = CouncilStatus.READY
        self.councils[council_id] = council
        self.councils_formed += 1

        logger.info(
            f"Council {council_id} formed with {len(selected)} agents: "
            f"{', '.join([a.personality.name for a in selected])}"
        )

        return council

    async def _select_diverse_agents(
        self,
        agents: List['Agent'],
        count: int
    ) -> List['Agent']:
        """
        Select agents with diverse personalities

        Prioritizes archetype diversity.
        """
        selected = []
        used_archetypes = set()

        # First pass: one agent per archetype
        for agent in agents:
            if agent.personality.archetype not in used_archetypes:
                selected.append(agent)
                used_archetypes.add(agent.personality.archetype)

                if len(selected) >= count:
                    break

        # Second pass: fill remaining slots if needed
        if len(selected) < count:
            remaining = [a for a in agents if a not in selected]
            selected.extend(remaining[:count - len(selected)])

        return selected[:count]

    async def _select_random_agents(
        self,
        agents: List['Agent'],
        count: int
    ) -> List['Agent']:
        """Select agents randomly"""
        import random
        return random.sample(agents, count)

    async def _select_rng_agents(
        self,
        agents: List['Agent'],
        count: int
    ) -> List['Agent']:
        """
        Select agents using verifiable RNG

        Would integrate with blockchain RNG in production.
        For now, uses deterministic seed.
        """
        import random

        # In production, this would use Chainlink VRF or Pyth Entropy
        seed = int(datetime.utcnow().timestamp())
        random.seed(seed)

        selected = random.sample(agents, count)

        # Store seed for verification
        return selected

    def _generate_council_id(self, topic_id: str) -> str:
        """Generate unique council ID"""
        timestamp = int(datetime.utcnow().timestamp())
        return f"council_{topic_id}_{timestamp}"

    async def activate_council(self, council_id: str) -> None:
        """Activate council for debate"""
        if council_id not in self.councils:
            raise ValueError(f"Council {council_id} not found")

        council = self.councils[council_id]
        council.status = CouncilStatus.ACTIVE
        logger.info(f"Council {council_id} activated")

    async def conclude_council(self, council_id: str) -> None:
        """Conclude council after debate"""
        if council_id not in self.councils:
            raise ValueError(f"Council {council_id} not found")

        council = self.councils[council_id]
        council.status = CouncilStatus.CONCLUDED
        logger.info(f"Council {council_id} concluded")

    async def archive_council(self, council_id: str) -> None:
        """Archive council"""
        if council_id not in self.councils:
            raise ValueError(f"Council {council_id} not found")

        council = self.councils[council_id]
        council.status = CouncilStatus.ARCHIVED
        logger.info(f"Council {council_id} archived")

    def get_council(self, council_id: str) -> Optional[Council]:
        """Get council by ID"""
        return self.councils.get(council_id)

    def get_active_councils(self) -> List[Council]:
        """Get all active councils"""
        return [
            c for c in self.councils.values()
            if c.status == CouncilStatus.ACTIVE
        ]

    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics"""
        return {
            "councils_formed": self.councils_formed,
            "active_councils": len(self.get_active_councils()),
            "total_councils": len(self.councils),
        }
