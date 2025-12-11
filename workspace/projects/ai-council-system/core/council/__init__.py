"""
Council Module - AI Council formation and debate management

Manages council formation, debate sessions, and outcomes.
"""

from .council import (
    Council,
    CouncilStatus,
    CouncilManager,
)

from .debate import (
    DebateSession,
    SessionState,
    Round,
    RoundType,
    DebateSessionManager,
)

__all__ = [
    # Council
    "Council",
    "CouncilStatus",
    "CouncilManager",
    # Debate
    "DebateSession",
    "SessionState",
    "Round",
    "RoundType",
    "DebateSessionManager",
]

__version__ = "0.1.0"
