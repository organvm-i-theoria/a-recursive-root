"""
Gamification System for Viewer Voting

This module implements gamification features to increase viewer engagement:
- Reputation and points system
- Achievements and badges
- Voting streaks
- Leaderboards
- Reward mechanisms
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

# Mock mode flag
MOCK_MODE = os.getenv('GAMIFICATION_MOCK_MODE', 'true').lower() == 'true'

logger = logging.getLogger(__name__)


class AchievementType(Enum):
    """Types of achievements users can earn"""
    FIRST_VOTE = "first_vote"
    VOTING_STREAK_7 = "voting_streak_7"
    VOTING_STREAK_30 = "voting_streak_30"
    VOTING_STREAK_100 = "voting_streak_100"
    ACCURATE_PREDICTION = "accurate_prediction"
    VOTE_COUNT_10 = "vote_count_10"
    VOTE_COUNT_100 = "vote_count_100"
    VOTE_COUNT_1000 = "vote_count_1000"
    CONSENSUS_BUILDER = "consensus_builder"
    CONTRARIAN = "contrarian"
    EARLY_VOTER = "early_voter"
    THOUGHTFUL_VOTER = "thoughtful_voter"  # Provides reasoning
    MULTI_TOPIC = "multi_topic"  # Votes on diverse topics


@dataclass
class Achievement:
    """Achievement definition"""
    achievement_type: AchievementType
    name: str
    description: str
    points: int
    badge_icon: str  # Emoji or icon identifier
    tier: int = 1  # Difficulty tier (1=easy, 5=legendary)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['achievement_type'] = self.achievement_type.value
        return data


# Achievement definitions
ACHIEVEMENTS = {
    AchievementType.FIRST_VOTE: Achievement(
        achievement_type=AchievementType.FIRST_VOTE,
        name="First Participant",
        description="Cast your first vote",
        points=10,
        badge_icon="🎯",
        tier=1
    ),
    AchievementType.VOTING_STREAK_7: Achievement(
        achievement_type=AchievementType.VOTING_STREAK_7,
        name="Weekly Regular",
        description="Vote on 7 consecutive days",
        points=50,
        badge_icon="🔥",
        tier=2
    ),
    AchievementType.VOTING_STREAK_30: Achievement(
        achievement_type=AchievementType.VOTING_STREAK_30,
        name="Monthly Champion",
        description="Vote on 30 consecutive days",
        points=200,
        badge_icon="⭐",
        tier=3
    ),
    AchievementType.VOTING_STREAK_100: Achievement(
        achievement_type=AchievementType.VOTING_STREAK_100,
        name="Dedication Legend",
        description="Vote on 100 consecutive days",
        points=1000,
        badge_icon="👑",
        tier=5
    ),
    AchievementType.ACCURATE_PREDICTION: Achievement(
        achievement_type=AchievementType.ACCURATE_PREDICTION,
        name="Oracle",
        description="Your vote matched the final outcome",
        points=25,
        badge_icon="🔮",
        tier=2
    ),
    AchievementType.VOTE_COUNT_10: Achievement(
        achievement_type=AchievementType.VOTE_COUNT_10,
        name="Getting Started",
        description="Cast 10 total votes",
        points=20,
        badge_icon="📊",
        tier=1
    ),
    AchievementType.VOTE_COUNT_100: Achievement(
        achievement_type=AchievementType.VOTE_COUNT_100,
        name="Engaged Citizen",
        description="Cast 100 total votes",
        points=100,
        badge_icon="🏆",
        tier=2
    ),
    AchievementType.VOTE_COUNT_1000: Achievement(
        achievement_type=AchievementType.VOTE_COUNT_1000,
        name="Super Voter",
        description="Cast 1000 total votes",
        points=500,
        badge_icon="💎",
        tier=4
    ),
    AchievementType.CONSENSUS_BUILDER: Achievement(
        achievement_type=AchievementType.CONSENSUS_BUILDER,
        name="Consensus Builder",
        description="Vote with the majority 10 times",
        points=50,
        badge_icon="🤝",
        tier=2
    ),
    AchievementType.CONTRARIAN: Achievement(
        achievement_type=AchievementType.CONTRARIAN,
        name="Contrarian",
        description="Vote against the majority 10 times",
        points=50,
        badge_icon="🎭",
        tier=2
    ),
    AchievementType.EARLY_VOTER: Achievement(
        achievement_type=AchievementType.EARLY_VOTER,
        name="Early Bird",
        description="Be among first 10 voters on a debate",
        points=15,
        badge_icon="🐦",
        tier=1
    ),
    AchievementType.THOUGHTFUL_VOTER: Achievement(
        achievement_type=AchievementType.THOUGHTFUL_VOTER,
        name="Thoughtful Participant",
        description="Provide reasoning for 50 votes",
        points=75,
        badge_icon="💭",
        tier=2
    ),
    AchievementType.MULTI_TOPIC: Achievement(
        achievement_type=AchievementType.MULTI_TOPIC,
        name="Diverse Interests",
        description="Vote on 10 different topic categories",
        points=40,
        badge_icon="🌐",
        tier=2
    ),
}


class ReputationTier(Enum):
    """User reputation tiers"""
    NEWCOMER = "newcomer"
    CONTRIBUTOR = "contributor"
    REGULAR = "regular"
    EXPERT = "expert"
    AUTHORITY = "authority"
    LEGEND = "legend"


# Points required for each tier
REPUTATION_TIERS = {
    ReputationTier.NEWCOMER: 0,
    ReputationTier.CONTRIBUTOR: 100,
    ReputationTier.REGULAR: 500,
    ReputationTier.EXPERT: 1000,
    ReputationTier.AUTHORITY: 5000,
    ReputationTier.LEGEND: 10000,
}


@dataclass
class UserProfile:
    """User gamification profile"""
    user_id: str
    username: Optional[str] = None
    points: int = 0
    reputation_tier: ReputationTier = ReputationTier.NEWCOMER
    achievements: Set[AchievementType] = field(default_factory=set)
    total_votes: int = 0
    accurate_predictions: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    last_vote_date: Optional[datetime] = None
    topics_voted_on: Set[str] = field(default_factory=set)
    consensus_votes: int = 0  # Votes with majority
    contrarian_votes: int = 0  # Votes against majority
    reasoned_votes: int = 0  # Votes with reasoning provided
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = {
            'user_id': self.user_id,
            'username': self.username,
            'points': self.points,
            'reputation_tier': self.reputation_tier.value,
            'achievements': [a.value for a in self.achievements],
            'total_votes': self.total_votes,
            'accurate_predictions': self.accurate_predictions,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'last_vote_date': self.last_vote_date.isoformat() if self.last_vote_date else None,
            'topics_voted_on': list(self.topics_voted_on),
            'consensus_votes': self.consensus_votes,
            'contrarian_votes': self.contrarian_votes,
            'reasoned_votes': self.reasoned_votes,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }
        return data

    @property
    def achievement_count(self) -> int:
        """Number of achievements earned"""
        return len(self.achievements)

    @property
    def accuracy_rate(self) -> float:
        """Prediction accuracy rate"""
        if self.total_votes == 0:
            return 0.0
        return (self.accurate_predictions / self.total_votes) * 100

    @property
    def consensus_rate(self) -> float:
        """Rate of voting with majority"""
        if self.total_votes == 0:
            return 0.0
        return (self.consensus_votes / self.total_votes) * 100

    @property
    def next_tier(self) -> Optional[ReputationTier]:
        """Next reputation tier to achieve"""
        tiers = list(ReputationTier)
        current_index = tiers.index(self.reputation_tier)

        if current_index < len(tiers) - 1:
            return tiers[current_index + 1]
        return None

    @property
    def points_to_next_tier(self) -> Optional[int]:
        """Points needed for next tier"""
        next_tier = self.next_tier
        if next_tier is None:
            return None

        required_points = REPUTATION_TIERS[next_tier]
        return max(0, required_points - self.points)


@dataclass
class LeaderboardEntry:
    """Leaderboard entry"""
    rank: int
    user_id: str
    username: Optional[str]
    points: int
    reputation_tier: ReputationTier
    total_votes: int
    achievement_count: int
    accuracy_rate: float

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['reputation_tier'] = self.reputation_tier.value
        return data


class GamificationManager:
    """
    Manages gamification features for viewer voting

    Features:
    - User profile management
    - Points and reputation tracking
    - Achievement checking and awarding
    - Leaderboards
    - Streak tracking
    """

    def __init__(self):
        self.profiles: Dict[str, UserProfile] = {}
        self.mock_mode = MOCK_MODE

        logger.info(f"GamificationManager initialized (mock_mode={self.mock_mode})")

    async def get_or_create_profile(self, user_id: str, username: Optional[str] = None) -> UserProfile:
        """Get user profile or create if doesn't exist"""
        if user_id not in self.profiles:
            self.profiles[user_id] = UserProfile(
                user_id=user_id,
                username=username
            )
            logger.info(f"Created new profile for user {user_id}")

        return self.profiles[user_id]

    async def record_vote(
        self,
        user_id: str,
        topic_category: str,
        has_reasoning: bool = False
    ) -> List[Achievement]:
        """
        Record a vote and check for achievements

        Args:
            user_id: User identifier
            topic_category: Category of topic voted on
            has_reasoning: Whether vote included reasoning

        Returns:
            List of newly unlocked achievements
        """
        profile = await self.get_or_create_profile(user_id)

        # Update vote count
        profile.total_votes += 1

        # Update topics
        profile.topics_voted_on.add(topic_category)

        # Update reasoning count
        if has_reasoning:
            profile.reasoned_votes += 1

        # Update streak
        today = datetime.now().date()
        if profile.last_vote_date:
            last_vote_date = profile.last_vote_date.date()
            days_since = (today - last_vote_date).days

            if days_since == 0:
                # Same day, no change to streak
                pass
            elif days_since == 1:
                # Consecutive day
                profile.current_streak += 1
                profile.longest_streak = max(profile.longest_streak, profile.current_streak)
            else:
                # Streak broken
                profile.current_streak = 1
        else:
            # First vote ever
            profile.current_streak = 1
            profile.longest_streak = 1

        profile.last_vote_date = datetime.now()
        profile.last_updated = datetime.now()

        # Check for achievements
        new_achievements = await self._check_achievements(profile)

        # Update points from achievements
        for achievement in new_achievements:
            achievement_def = ACHIEVEMENTS[achievement]
            profile.points += achievement_def.points
            logger.info(f"User {user_id} earned {achievement.value}: +{achievement_def.points} points")

        # Update reputation tier
        profile.reputation_tier = self._calculate_tier(profile.points)

        return new_achievements

    async def record_prediction_outcome(
        self,
        user_id: str,
        user_vote_matched: bool,
        user_voted_with_majority: bool
    ):
        """
        Record outcome of a vote prediction

        Args:
            user_id: User identifier
            user_vote_matched: Whether user's vote matched final outcome
            user_voted_with_majority: Whether user voted with the majority
        """
        profile = await self.get_or_create_profile(user_id)

        if user_vote_matched:
            profile.accurate_predictions += 1

            # Award points for accurate prediction
            profile.points += ACHIEVEMENTS[AchievementType.ACCURATE_PREDICTION].points

            # Check if earned achievement
            if AchievementType.ACCURATE_PREDICTION not in profile.achievements:
                profile.achievements.add(AchievementType.ACCURATE_PREDICTION)
                logger.info(f"User {user_id} earned Oracle achievement")

        if user_voted_with_majority:
            profile.consensus_votes += 1
        else:
            profile.contrarian_votes += 1

        # Check for consensus/contrarian achievements
        if profile.consensus_votes >= 10 and AchievementType.CONSENSUS_BUILDER not in profile.achievements:
            profile.achievements.add(AchievementType.CONSENSUS_BUILDER)
            profile.points += ACHIEVEMENTS[AchievementType.CONSENSUS_BUILDER].points

        if profile.contrarian_votes >= 10 and AchievementType.CONTRARIAN not in profile.achievements:
            profile.achievements.add(AchievementType.CONTRARIAN)
            profile.points += ACHIEVEMENTS[AchievementType.CONTRARIAN].points

        profile.last_updated = datetime.now()

        # Update tier
        profile.reputation_tier = self._calculate_tier(profile.points)

    async def _check_achievements(self, profile: UserProfile) -> List[AchievementType]:
        """Check which new achievements user has earned"""
        new_achievements = []

        # First vote
        if profile.total_votes == 1 and AchievementType.FIRST_VOTE not in profile.achievements:
            new_achievements.append(AchievementType.FIRST_VOTE)
            profile.achievements.add(AchievementType.FIRST_VOTE)

        # Vote count milestones
        if profile.total_votes >= 10 and AchievementType.VOTE_COUNT_10 not in profile.achievements:
            new_achievements.append(AchievementType.VOTE_COUNT_10)
            profile.achievements.add(AchievementType.VOTE_COUNT_10)

        if profile.total_votes >= 100 and AchievementType.VOTE_COUNT_100 not in profile.achievements:
            new_achievements.append(AchievementType.VOTE_COUNT_100)
            profile.achievements.add(AchievementType.VOTE_COUNT_100)

        if profile.total_votes >= 1000 and AchievementType.VOTE_COUNT_1000 not in profile.achievements:
            new_achievements.append(AchievementType.VOTE_COUNT_1000)
            profile.achievements.add(AchievementType.VOTE_COUNT_1000)

        # Streaks
        if profile.current_streak >= 7 and AchievementType.VOTING_STREAK_7 not in profile.achievements:
            new_achievements.append(AchievementType.VOTING_STREAK_7)
            profile.achievements.add(AchievementType.VOTING_STREAK_7)

        if profile.current_streak >= 30 and AchievementType.VOTING_STREAK_30 not in profile.achievements:
            new_achievements.append(AchievementType.VOTING_STREAK_30)
            profile.achievements.add(AchievementType.VOTING_STREAK_30)

        if profile.current_streak >= 100 and AchievementType.VOTING_STREAK_100 not in profile.achievements:
            new_achievements.append(AchievementType.VOTING_STREAK_100)
            profile.achievements.add(AchievementType.VOTING_STREAK_100)

        # Thoughtful voter
        if profile.reasoned_votes >= 50 and AchievementType.THOUGHTFUL_VOTER not in profile.achievements:
            new_achievements.append(AchievementType.THOUGHTFUL_VOTER)
            profile.achievements.add(AchievementType.THOUGHTFUL_VOTER)

        # Multi-topic
        if len(profile.topics_voted_on) >= 10 and AchievementType.MULTI_TOPIC not in profile.achievements:
            new_achievements.append(AchievementType.MULTI_TOPIC)
            profile.achievements.add(AchievementType.MULTI_TOPIC)

        return new_achievements

    def _calculate_tier(self, points: int) -> ReputationTier:
        """Calculate reputation tier from points"""
        for tier in reversed(list(ReputationTier)):
            if points >= REPUTATION_TIERS[tier]:
                return tier
        return ReputationTier.NEWCOMER

    async def get_leaderboard(
        self,
        limit: int = 100,
        sort_by: str = "points"
    ) -> List[LeaderboardEntry]:
        """
        Get leaderboard

        Args:
            limit: Maximum number of entries
            sort_by: Sort criterion ("points", "votes", "accuracy", "achievements")

        Returns:
            List of leaderboard entries
        """
        profiles = list(self.profiles.values())

        # Sort
        if sort_by == "points":
            profiles.sort(key=lambda p: p.points, reverse=True)
        elif sort_by == "votes":
            profiles.sort(key=lambda p: p.total_votes, reverse=True)
        elif sort_by == "accuracy":
            profiles.sort(key=lambda p: p.accuracy_rate, reverse=True)
        elif sort_by == "achievements":
            profiles.sort(key=lambda p: p.achievement_count, reverse=True)

        # Create entries
        entries = []
        for rank, profile in enumerate(profiles[:limit], start=1):
            entry = LeaderboardEntry(
                rank=rank,
                user_id=profile.user_id,
                username=profile.username,
                points=profile.points,
                reputation_tier=profile.reputation_tier,
                total_votes=profile.total_votes,
                achievement_count=profile.achievement_count,
                accuracy_rate=profile.accuracy_rate
            )
            entries.append(entry)

        return entries

    async def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile"""
        return self.profiles.get(user_id)


# Singleton instance
_gamification_manager = None


def get_gamification_manager() -> GamificationManager:
    """Get singleton GamificationManager instance"""
    global _gamification_manager
    if _gamification_manager is None:
        _gamification_manager = GamificationManager()
    return _gamification_manager
