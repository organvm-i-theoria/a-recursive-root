"""
Viewer Voting Integration with Council System

This module integrates viewer votes with the AI Council debate system,
allowing viewer participation in debates and consensus building.
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# Import from web backend (viewer voting)
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../web/backend'))

from voting.voting_api import VotingManager, VoteType, VotePosition, get_voting_manager
from voting.gamification import GamificationManager, get_gamification_manager

# Mock mode flag
MOCK_MODE = os.getenv('VIEWER_INTEGRATION_MOCK_MODE', 'true').lower() == 'true'

logger = logging.getLogger(__name__)


@dataclass
class HybridVoteResult:
    """Combined result from agent and viewer votes"""
    debate_id: str
    round_number: int
    final_outcome: VotePosition
    agent_outcome: VotePosition
    viewer_outcome: VotePosition
    agent_votes: int
    viewer_votes: int
    agent_weight: float
    viewer_weight: float
    final_support_score: float
    final_oppose_score: float
    consensus_level: float
    timestamp: datetime


class ViewerIntegrationManager:
    """
    Manages integration between viewer voting and council debates

    Features:
    - Open debates for viewer voting
    - Collect and aggregate viewer votes
    - Combine viewer and agent votes with configurable weights
    - Track viewer engagement and influence
    - Award gamification points
    """

    def __init__(
        self,
        voting_manager: Optional[VotingManager] = None,
        gamification_manager: Optional[GamificationManager] = None
    ):
        self.voting_manager = voting_manager or get_voting_manager()
        self.gamification_manager = gamification_manager or get_gamification_manager()
        self.mock_mode = MOCK_MODE

        # Default weights for combining votes
        self.agent_weight = 0.7  # Agents have 70% influence
        self.viewer_weight = 0.3  # Viewers have 30% influence

        logger.info(f"ViewerIntegrationManager initialized (mock_mode={self.mock_mode})")

    def set_vote_weights(self, agent_weight: float, viewer_weight: float):
        """
        Set weights for combining agent and viewer votes

        Args:
            agent_weight: Weight for agent votes (0.0 to 1.0)
            viewer_weight: Weight for viewer votes (0.0 to 1.0)

        Raises:
            ValueError: If weights don't sum to 1.0
        """
        if agent_weight + viewer_weight != 1.0:
            raise ValueError("agent_weight + viewer_weight must equal 1.0")

        self.agent_weight = agent_weight
        self.viewer_weight = viewer_weight

        logger.info(f"Vote weights updated: agents={agent_weight}, viewers={viewer_weight}")

    async def open_debate_for_voting(
        self,
        debate_id: str,
        topic: str,
        description: str,
        vote_type: VoteType = VoteType.BINARY
    ):
        """
        Open a debate for viewer voting

        Args:
            debate_id: Debate session ID
            topic: Debate topic
            description: Debate description
            vote_type: Type of voting (binary, scaled, etc.)
        """
        logger.info(f"Opened debate {debate_id} for viewer voting: {topic}")

        # In production, would:
        # - Create voting session in database
        # - Send WebSocket notification to viewers
        # - Update frontend to show voting UI

        if self.mock_mode:
            logger.info(f"Mock mode: Debate {debate_id} opened for {vote_type.value} voting")

    async def submit_viewer_vote(
        self,
        user_id: str,
        debate_id: str,
        round_number: int,
        position: VotePosition,
        confidence: float = 0.5,
        reasoning: Optional[str] = None,
        topic_category: Optional[str] = None
    ):
        """
        Submit a viewer vote

        Args:
            user_id: Viewer user ID
            debate_id: Debate session ID
            round_number: Debate round number
            position: Vote position (support/oppose/etc)
            confidence: Confidence level (0.0 to 1.0)
            reasoning: Optional reasoning
            topic_category: Category of debate topic

        Returns:
            Vote object
        """
        # Submit vote
        vote = await self.voting_manager.submit_vote(
            user_id=user_id,
            debate_id=debate_id,
            round_number=round_number,
            vote_type=VoteType.BINARY,
            position=position,
            confidence=confidence,
            reasoning=reasoning
        )

        # Record for gamification
        await self.gamification_manager.record_vote(
            user_id=user_id,
            topic_category=topic_category or "general",
            has_reasoning=bool(reasoning)
        )

        logger.info(f"Viewer vote submitted: {user_id} -> {position.value} on {debate_id}")

        return vote

    async def calculate_hybrid_result(
        self,
        debate_id: str,
        round_number: int,
        agent_votes: Dict[str, VotePosition]
    ) -> HybridVoteResult:
        """
        Calculate combined result from agent and viewer votes

        Args:
            debate_id: Debate session ID
            round_number: Debate round number
            agent_votes: Dictionary of agent_id -> VotePosition

        Returns:
            HybridVoteResult with combined outcome
        """
        # Get weighted outcome
        result = await self.voting_manager.calculate_weighted_outcome(
            debate_id=debate_id,
            agent_votes=agent_votes,
            agent_weight=self.agent_weight,
            viewer_weight=self.viewer_weight
        )

        # Determine agent-only outcome
        agent_support = sum(1 for v in agent_votes.values() if v == VotePosition.SUPPORT)
        agent_oppose = sum(1 for v in agent_votes.values() if v == VotePosition.OPPOSE)

        if agent_support > agent_oppose:
            agent_outcome = VotePosition.SUPPORT
        elif agent_oppose > agent_support:
            agent_outcome = VotePosition.OPPOSE
        else:
            agent_outcome = VotePosition.NEUTRAL

        # Get viewer stats
        viewer_stats = await self.voting_manager.get_stats(debate_id)

        if viewer_stats:
            if viewer_stats.support_votes > viewer_stats.oppose_votes:
                viewer_outcome = VotePosition.SUPPORT
            elif viewer_stats.oppose_votes > viewer_stats.support_votes:
                viewer_outcome = VotePosition.OPPOSE
            else:
                viewer_outcome = VotePosition.NEUTRAL
        else:
            viewer_outcome = VotePosition.NEUTRAL

        # Create result
        hybrid_result = HybridVoteResult(
            debate_id=debate_id,
            round_number=round_number,
            final_outcome=result['outcome'],
            agent_outcome=agent_outcome,
            viewer_outcome=viewer_outcome,
            agent_votes=result['agent_votes'],
            viewer_votes=result['viewer_votes'],
            agent_weight=self.agent_weight,
            viewer_weight=self.viewer_weight,
            final_support_score=result['final_support_score'],
            final_oppose_score=result['final_oppose_score'],
            consensus_level=result.get('consensus_level', 0.0),
            timestamp=datetime.now()
        )

        logger.info(f"Hybrid result calculated: {hybrid_result.final_outcome.value} "
                   f"(agents: {agent_outcome.value}, viewers: {viewer_outcome.value})")

        return hybrid_result

    async def finalize_debate_voting(
        self,
        debate_id: str,
        final_outcome: VotePosition
    ):
        """
        Finalize voting and award gamification points

        Args:
            debate_id: Debate session ID
            final_outcome: Final debate outcome
        """
        # Get all viewer votes
        votes = await self.voting_manager.get_debate_votes(debate_id)

        # Get stats for determining majority
        stats = await self.voting_manager.get_stats(debate_id)

        if not stats:
            logger.info(f"No viewer votes for debate {debate_id}")
            return

        # Determine majority position
        if stats.support_votes > stats.oppose_votes:
            majority_position = VotePosition.SUPPORT
        elif stats.oppose_votes > stats.support_votes:
            majority_position = VotePosition.OPPOSE
        else:
            majority_position = VotePosition.NEUTRAL

        # Award points for accurate predictions
        for vote in votes:
            user_vote_matched = (vote.position == final_outcome)
            user_voted_with_majority = (vote.position == majority_position)

            await self.gamification_manager.record_prediction_outcome(
                user_id=vote.user_id,
                user_vote_matched=user_vote_matched,
                user_voted_with_majority=user_voted_with_majority
            )

        logger.info(f"Finalized voting for debate {debate_id}: {len(votes)} votes processed")

    async def get_viewer_stats(self, debate_id: str) -> Dict:
        """Get viewer voting statistics for a debate"""
        stats = await self.voting_manager.get_stats(debate_id)

        if not stats:
            return {
                "total_votes": 0,
                "support_percentage": 0.0,
                "oppose_percentage": 0.0,
                "consensus_level": 0.0,
                "vote_velocity": 0.0
            }

        return {
            "total_votes": stats.total_votes,
            "support_votes": stats.support_votes,
            "oppose_votes": stats.oppose_votes,
            "neutral_votes": stats.neutral_votes,
            "support_percentage": stats.support_percentage,
            "oppose_percentage": stats.oppose_percentage,
            "consensus_level": stats.consensus_level,
            "avg_confidence": stats.avg_confidence,
            "vote_velocity": stats.vote_velocity,
            "top_reasons": stats.top_reasons
        }

    async def get_user_profile(self, user_id: str) -> Dict:
        """Get user gamification profile"""
        profile = await self.gamification_manager.get_profile(user_id)

        if not profile:
            return {"error": "User not found"}

        return profile.to_dict()

    async def get_leaderboard(self, limit: int = 100, sort_by: str = "points") -> List[Dict]:
        """Get viewer leaderboard"""
        entries = await self.gamification_manager.get_leaderboard(limit, sort_by)
        return [entry.to_dict() for entry in entries]


# Singleton instance
_viewer_integration_manager = None


def get_viewer_integration_manager() -> ViewerIntegrationManager:
    """Get singleton ViewerIntegrationManager instance"""
    global _viewer_integration_manager
    if _viewer_integration_manager is None:
        _viewer_integration_manager = ViewerIntegrationManager()
    return _viewer_integration_manager
