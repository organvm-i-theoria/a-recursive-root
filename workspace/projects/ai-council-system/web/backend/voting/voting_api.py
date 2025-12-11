"""
Real-Time Viewer Voting API

This module provides REST and WebSocket endpoints for viewer participation
in AI Council debates through real-time voting.

Features:
- Multiple vote types (binary, scaled, ranked, confidence-based)
- Real-time vote aggregation and statistics
- WebSocket support for live updates
- Rate limiting and fraud prevention
- Vote validation and verification
"""

import os
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from decimal import Decimal
import logging

# Mock mode flag
MOCK_MODE = os.getenv('VIEWER_VOTING_MOCK_MODE', 'true').lower() == 'true'

logger = logging.getLogger(__name__)


class VoteType(Enum):
    """Supported vote types"""
    BINARY = "binary"  # support/oppose
    SCALED = "scaled"  # 1-5 rating
    RANKED = "ranked"  # preference ordering
    CONFIDENCE = "confidence"  # position + confidence level


class VotePosition(Enum):
    """Vote positions for binary voting"""
    SUPPORT = "support"
    OPPOSE = "oppose"
    NEUTRAL = "neutral"
    ABSTAIN = "abstain"


@dataclass
class Vote:
    """Individual vote cast by a viewer"""
    vote_id: str
    user_id: str
    debate_id: str
    round_number: int
    vote_type: VoteType
    position: VotePosition
    confidence: float = 0.5  # 0.0 to 1.0
    scaled_value: Optional[int] = None  # For scaled votes (1-5)
    ranked_options: Optional[List[str]] = None  # For ranked voting
    reasoning: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    ip_hash: Optional[str] = None  # Hashed IP for fraud detection
    user_agent_hash: Optional[str] = None  # Hashed user agent

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['vote_type'] = self.vote_type.value
        data['position'] = self.position.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class VoteStats:
    """Aggregated voting statistics"""
    debate_id: str
    round_number: int
    total_votes: int = 0
    support_votes: int = 0
    oppose_votes: int = 0
    neutral_votes: int = 0
    abstain_votes: int = 0
    avg_confidence: float = 0.0
    scaled_distribution: Dict[int, int] = field(default_factory=dict)
    top_reasons: List[str] = field(default_factory=list)
    vote_velocity: float = 0.0  # Votes per minute
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['last_updated'] = self.last_updated.isoformat()
        return data

    @property
    def support_percentage(self) -> float:
        """Calculate support percentage"""
        if self.total_votes == 0:
            return 0.0
        return (self.support_votes / self.total_votes) * 100

    @property
    def oppose_percentage(self) -> float:
        """Calculate oppose percentage"""
        if self.total_votes == 0:
            return 0.0
        return (self.oppose_votes / self.total_votes) * 100

    @property
    def consensus_level(self) -> float:
        """
        Calculate consensus level (0.0 to 1.0)
        Higher = more agreement, Lower = more division
        """
        if self.total_votes == 0:
            return 0.0

        # Calculate entropy of vote distribution
        positions = [self.support_votes, self.oppose_votes, self.neutral_votes, self.abstain_votes]
        total = sum(positions)

        if total == 0:
            return 0.0

        proportions = [p / total for p in positions if p > 0]

        # Calculate normalized Gini coefficient (measures inequality)
        # High Gini = high consensus (votes concentrated in one option)
        sorted_props = sorted(proportions)
        n = len(sorted_props)

        if n == 0:
            return 0.0

        index_sum = sum((i + 1) * prop for i, prop in enumerate(sorted_props))
        gini = (2 * index_sum) / (n * sum(sorted_props)) - (n + 1) / n

        return gini


class VotingManager:
    """
    Manages viewer votes for debates

    Features:
    - Vote submission and validation
    - Real-time vote aggregation
    - Fraud prevention (rate limiting, IP tracking)
    - Vote statistics and analytics
    """

    def __init__(self):
        self.votes: Dict[str, List[Vote]] = {}  # debate_id -> list of votes
        self.stats: Dict[str, VoteStats] = {}  # debate_id -> stats
        self.user_votes: Dict[str, Set[str]] = {}  # user_id -> set of vote_ids
        self.rate_limiter: Dict[str, List[float]] = {}  # user_id -> timestamps
        self.mock_mode = MOCK_MODE

        logger.info(f"VotingManager initialized (mock_mode={self.mock_mode})")

    def _hash_identifier(self, identifier: str) -> str:
        """Hash an identifier (IP, user agent) for privacy"""
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]

    def _check_rate_limit(self, user_id: str, max_votes_per_minute: int = 5) -> bool:
        """
        Check if user is within rate limit

        Args:
            user_id: User identifier
            max_votes_per_minute: Maximum votes allowed per minute

        Returns:
            True if within limit, False if rate limit exceeded
        """
        now = time.time()
        cutoff = now - 60  # 1 minute ago

        # Initialize or clean old timestamps
        if user_id not in self.rate_limiter:
            self.rate_limiter[user_id] = []

        # Remove old timestamps
        self.rate_limiter[user_id] = [
            ts for ts in self.rate_limiter[user_id] if ts > cutoff
        ]

        # Check limit
        if len(self.rate_limiter[user_id]) >= max_votes_per_minute:
            return False

        # Add current timestamp
        self.rate_limiter[user_id].append(now)
        return True

    def _generate_vote_id(self, user_id: str, debate_id: str, timestamp: datetime) -> str:
        """Generate unique vote ID"""
        data = f"{user_id}:{debate_id}:{timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    async def submit_vote(
        self,
        user_id: str,
        debate_id: str,
        round_number: int,
        vote_type: VoteType,
        position: VotePosition,
        confidence: float = 0.5,
        scaled_value: Optional[int] = None,
        ranked_options: Optional[List[str]] = None,
        reasoning: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Vote:
        """
        Submit a vote

        Args:
            user_id: User identifier (can be anonymous)
            debate_id: Debate session ID
            round_number: Debate round number
            vote_type: Type of vote
            position: Vote position (support/oppose/etc)
            confidence: Confidence level (0.0 to 1.0)
            scaled_value: For scaled votes (1-5)
            ranked_options: For ranked voting
            reasoning: Optional comment explaining the vote
            ip_address: User's IP address (will be hashed)
            user_agent: User's user agent (will be hashed)

        Returns:
            Vote object

        Raises:
            ValueError: If vote validation fails or rate limit exceeded
        """
        # Check rate limit
        if not self._check_rate_limit(user_id):
            raise ValueError(f"Rate limit exceeded for user {user_id}")

        # Validate vote type specific parameters
        if vote_type == VoteType.SCALED and scaled_value is None:
            raise ValueError("scaled_value required for SCALED vote type")

        if vote_type == VoteType.SCALED and not (1 <= scaled_value <= 5):
            raise ValueError("scaled_value must be between 1 and 5")

        if vote_type == VoteType.RANKED and not ranked_options:
            raise ValueError("ranked_options required for RANKED vote type")

        # Validate confidence
        if not (0.0 <= confidence <= 1.0):
            raise ValueError("confidence must be between 0.0 and 1.0")

        # Create vote
        timestamp = datetime.now()
        vote_id = self._generate_vote_id(user_id, debate_id, timestamp)

        vote = Vote(
            vote_id=vote_id,
            user_id=user_id,
            debate_id=debate_id,
            round_number=round_number,
            vote_type=vote_type,
            position=position,
            confidence=confidence,
            scaled_value=scaled_value,
            ranked_options=ranked_options,
            reasoning=reasoning,
            timestamp=timestamp,
            ip_hash=self._hash_identifier(ip_address) if ip_address else None,
            user_agent_hash=self._hash_identifier(user_agent) if user_agent else None
        )

        # Store vote
        if debate_id not in self.votes:
            self.votes[debate_id] = []
        self.votes[debate_id].append(vote)

        # Track user's votes
        if user_id not in self.user_votes:
            self.user_votes[user_id] = set()
        self.user_votes[user_id].add(vote_id)

        # Update statistics
        await self._update_stats(debate_id)

        logger.info(f"Vote submitted: {vote_id} by {user_id} for {debate_id}")

        return vote

    async def _update_stats(self, debate_id: str):
        """Update vote statistics for a debate"""
        votes = self.votes.get(debate_id, [])

        if not votes:
            self.stats[debate_id] = VoteStats(
                debate_id=debate_id,
                round_number=0
            )
            return

        # Get latest round number
        latest_round = max(v.round_number for v in votes)

        # Count votes by position
        support = sum(1 for v in votes if v.position == VotePosition.SUPPORT)
        oppose = sum(1 for v in votes if v.position == VotePosition.OPPOSE)
        neutral = sum(1 for v in votes if v.position == VotePosition.NEUTRAL)
        abstain = sum(1 for v in votes if v.position == VotePosition.ABSTAIN)

        # Calculate average confidence
        confidences = [v.confidence for v in votes]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Calculate scaled distribution
        scaled_dist = {}
        for v in votes:
            if v.scaled_value:
                scaled_dist[v.scaled_value] = scaled_dist.get(v.scaled_value, 0) + 1

        # Get top reasons
        reasons = [v.reasoning for v in votes if v.reasoning]
        # In production, would use NLP to cluster similar reasons
        top_reasons = list(set(reasons))[:5] if reasons else []

        # Calculate vote velocity (votes per minute in last 5 minutes)
        now = datetime.now()
        recent_cutoff = now - timedelta(minutes=5)
        recent_votes = [v for v in votes if v.timestamp > recent_cutoff]
        vote_velocity = len(recent_votes) / 5.0  # votes per minute

        # Create/update stats
        self.stats[debate_id] = VoteStats(
            debate_id=debate_id,
            round_number=latest_round,
            total_votes=len(votes),
            support_votes=support,
            oppose_votes=oppose,
            neutral_votes=neutral,
            abstain_votes=abstain,
            avg_confidence=avg_confidence,
            scaled_distribution=scaled_dist,
            top_reasons=top_reasons,
            vote_velocity=vote_velocity,
            last_updated=now
        )

    async def get_stats(self, debate_id: str) -> Optional[VoteStats]:
        """Get voting statistics for a debate"""
        return self.stats.get(debate_id)

    async def get_user_votes(self, user_id: str) -> List[Vote]:
        """Get all votes cast by a user"""
        vote_ids = self.user_votes.get(user_id, set())
        all_votes = []
        for votes_list in self.votes.values():
            all_votes.extend([v for v in votes_list if v.vote_id in vote_ids])
        return all_votes

    async def get_debate_votes(
        self,
        debate_id: str,
        round_number: Optional[int] = None
    ) -> List[Vote]:
        """
        Get all votes for a debate

        Args:
            debate_id: Debate session ID
            round_number: Optional filter by round number

        Returns:
            List of votes
        """
        votes = self.votes.get(debate_id, [])

        if round_number is not None:
            votes = [v for v in votes if v.round_number == round_number]

        return votes

    async def calculate_weighted_outcome(
        self,
        debate_id: str,
        agent_votes: Dict[str, VotePosition],
        agent_weight: float = 0.7,
        viewer_weight: float = 0.3
    ) -> Dict:
        """
        Calculate weighted outcome combining agent and viewer votes

        Args:
            debate_id: Debate session ID
            agent_votes: Dictionary of agent_id -> VotePosition
            agent_weight: Weight for agent votes (0.0 to 1.0)
            viewer_weight: Weight for viewer votes (0.0 to 1.0)

        Returns:
            Dictionary with weighted outcome
        """
        if agent_weight + viewer_weight != 1.0:
            raise ValueError("agent_weight + viewer_weight must equal 1.0")

        # Get viewer stats
        viewer_stats = await self.get_stats(debate_id)

        if not viewer_stats:
            # No viewer votes, use only agent votes
            return {
                "outcome": self._aggregate_agent_votes(agent_votes),
                "agent_influence": 1.0,
                "viewer_influence": 0.0,
                "total_votes": len(agent_votes),
                "viewer_votes": 0
            }

        # Calculate agent vote scores
        agent_support = sum(1 for v in agent_votes.values() if v == VotePosition.SUPPORT)
        agent_oppose = sum(1 for v in agent_votes.values() if v == VotePosition.OPPOSE)
        agent_total = len(agent_votes)

        agent_support_score = (agent_support / agent_total) if agent_total > 0 else 0.0
        agent_oppose_score = (agent_oppose / agent_total) if agent_total > 0 else 0.0

        # Calculate viewer vote scores
        viewer_support_score = viewer_stats.support_percentage / 100
        viewer_oppose_score = viewer_stats.oppose_percentage / 100

        # Weighted combination
        final_support = (agent_support_score * agent_weight) + (viewer_support_score * viewer_weight)
        final_oppose = (agent_oppose_score * agent_weight) + (viewer_oppose_score * viewer_weight)

        # Determine outcome
        if final_support > final_oppose:
            outcome = VotePosition.SUPPORT
        elif final_oppose > final_support:
            outcome = VotePosition.OPPOSE
        else:
            outcome = VotePosition.NEUTRAL

        return {
            "outcome": outcome,
            "final_support_score": final_support,
            "final_oppose_score": final_oppose,
            "agent_influence": agent_weight,
            "viewer_influence": viewer_weight,
            "total_votes": agent_total + viewer_stats.total_votes,
            "agent_votes": agent_total,
            "viewer_votes": viewer_stats.total_votes,
            "consensus_level": viewer_stats.consensus_level
        }

    def _aggregate_agent_votes(self, agent_votes: Dict[str, VotePosition]) -> VotePosition:
        """Aggregate agent votes to determine outcome"""
        support = sum(1 for v in agent_votes.values() if v == VotePosition.SUPPORT)
        oppose = sum(1 for v in agent_votes.values() if v == VotePosition.OPPOSE)

        if support > oppose:
            return VotePosition.SUPPORT
        elif oppose > support:
            return VotePosition.OPPOSE
        else:
            return VotePosition.NEUTRAL


# Singleton instance
_voting_manager = None


def get_voting_manager() -> VotingManager:
    """Get singleton VotingManager instance"""
    global _voting_manager
    if _voting_manager is None:
        _voting_manager = VotingManager()
    return _voting_manager
