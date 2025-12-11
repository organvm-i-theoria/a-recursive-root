"""
AI Council System - Core Package

Provides core functionality for AI agent debates, council formation,
and real-time event processing.
"""

__version__ = "0.1.0"

from .agents.base_agent import BaseAgent, AgentPersonality
from .agents.debate_agent import DebateAgent
from .council.council import Council, DebateSession
from .events.event_ingestion import EventIngester, Event

__all__ = [
    "BaseAgent",
    "AgentPersonality",
    "DebateAgent",
    "Council",
    "DebateSession",
    "EventIngester",
    "Event",
]
