"""
Viewer Voting System

This package implements real-time viewer voting for AI Council debates.

Modules:
- voting_api: Vote submission, aggregation, and statistics
- gamification: Points, achievements, and leaderboards
"""

from .voting_api import (
    VoteType,
    VotePosition,
    Vote,
    VoteStats,
    VotingManager,
    get_voting_manager
)

from .gamification import (
    AchievementType,
    Achievement,
    ReputationTier,
    UserProfile,
    LeaderboardEntry,
    GamificationManager,
    get_gamification_manager,
    ACHIEVEMENTS,
    REPUTATION_TIERS
)

__all__ = [
    # Voting API
    'VoteType',
    'VotePosition',
    'Vote',
    'VoteStats',
    'VotingManager',
    'get_voting_manager',

    # Gamification
    'AchievementType',
    'Achievement',
    'ReputationTier',
    'UserProfile',
    'LeaderboardEntry',
    'GamificationManager',
    'get_gamification_manager',
    'ACHIEVEMENTS',
    'REPUTATION_TIERS',
]

__version__ = "0.4.0-alpha"
