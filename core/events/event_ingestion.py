"""
Event Ingestion System - Real-time topic and event processing

Ingests events from various sources (Twitter, news feeds, manual input)
and processes them for council debates.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import asyncio
import random

logger = logging.getLogger(__name__)


class EventSource(Enum):
    """Sources for debate topics"""
    TWITTER = "twitter"
    NEWS = "news"
    REDDIT = "reddit"
    MANUAL = "manual"
    RSS = "rss"
    CRYPTO_FEED = "crypto_feed"


class EventCategory(Enum):
    """Categories of events"""
    POLITICS = "politics"
    TECHNOLOGY = "technology"
    ECONOMICS = "economics"
    SOCIAL = "social"
    SCIENCE = "science"
    ENTERTAINMENT = "entertainment"
    CRYPTO = "crypto"
    AI = "ai"
    OTHER = "other"


@dataclass
class Event:
    """Represents a real-time event for debate"""
    event_id: str
    title: str
    description: str
    source: EventSource
    category: EventCategory
    timestamp: datetime
    url: Optional[str] = None
    facts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance_score: float = 0.5  # 0.0-1.0

    def to_debate_topic(self) -> str:
        """Convert event to debate topic"""
        return f"{self.title}: {self.description}"


class EventIngester:
    """
    Ingests and processes events from multiple sources

    Provides a unified interface for getting debate-worthy topics
    from various real-time sources.
    """

    def __init__(self):
        self.active_sources: List[EventSource] = []
        self.event_queue: List[Event] = []
        self.processed_events: List[Event] = []
        self.source_handlers = {
            EventSource.MANUAL: self._fetch_manual_events,
            EventSource.CRYPTO_FEED: self._fetch_crypto_events,
            EventSource.NEWS: self._fetch_news_events,
            EventSource.TWITTER: self._fetch_twitter_events,
        }

    def enable_source(self, source: EventSource) -> None:
        """Enable an event source"""
        if source not in self.active_sources:
            self.active_sources.append(source)
            logger.info(f"Enabled event source: {source.value}")

    def disable_source(self, source: EventSource) -> None:
        """Disable an event source"""
        if source in self.active_sources:
            self.active_sources.remove(source)
            logger.info(f"Disabled event source: {source.value}")

    async def fetch_events(self, limit: int = 10) -> List[Event]:
        """
        Fetch events from all active sources

        Args:
            limit: Maximum number of events to fetch

        Returns:
            List of events
        """
        all_events = []

        for source in self.active_sources:
            handler = self.source_handlers.get(source)
            if handler:
                try:
                    events = await handler(limit=limit)
                    all_events.extend(events)
                    logger.info(f"Fetched {len(events)} events from {source.value}")
                except Exception as e:
                    logger.error(f"Error fetching from {source.value}: {e}")

        # Sort by importance and timestamp
        all_events.sort(key=lambda e: (e.importance_score, e.timestamp), reverse=True)

        # Add to queue
        self.event_queue.extend(all_events[:limit])

        return all_events[:limit]

    async def get_next_event(self) -> Optional[Event]:
        """Get next event from queue"""
        if not self.event_queue:
            await self.fetch_events()

        if self.event_queue:
            event = self.event_queue.pop(0)
            self.processed_events.append(event)
            return event

        return None

    def add_manual_event(
        self,
        title: str,
        description: str,
        category: EventCategory = EventCategory.OTHER,
        facts: Optional[List[str]] = None
    ) -> Event:
        """
        Manually add an event for debate

        Args:
            title: Event title
            description: Event description
            category: Event category
            facts: Optional list of facts

        Returns:
            Created event
        """
        event = Event(
            event_id=f"manual_{datetime.utcnow().timestamp()}",
            title=title,
            description=description,
            source=EventSource.MANUAL,
            category=category,
            timestamp=datetime.utcnow(),
            facts=facts or [],
            importance_score=0.7,
        )

        self.event_queue.append(event)
        logger.info(f"Added manual event: {title}")

        return event

    async def _fetch_manual_events(self, limit: int = 10) -> List[Event]:
        """Fetch manually created events (already in queue)"""
        return []

    async def _fetch_crypto_events(self, limit: int = 10) -> List[Event]:
        """Fetch cryptocurrency-related events"""
        # Mock implementation - in production would connect to real crypto feeds
        mock_events = [
            {
                "title": "Bitcoin Volatility Spike",
                "description": "Bitcoin experiences 15% price swing in 24 hours amid regulatory uncertainty",
                "facts": [
                    "Bitcoin dropped from $102,000 to $87,000",
                    "Trading volume increased 300%",
                    "Market liquidations exceeded $2 billion",
                ],
                "importance": 0.9,
            },
            {
                "title": "New DeFi Protocol Launch",
                "description": "Major decentralized finance protocol launches with innovative yield mechanism",
                "facts": [
                    "Protocol offers 50% APY on stablecoin deposits",
                    "Smart contracts audited by three firms",
                    "TVL reached $100M in first 24 hours",
                ],
                "importance": 0.6,
            },
            {
                "title": "Memecoin Mania Returns",
                "description": "New memecoin reaches $100M market cap in under 1 hour on Pump.fun",
                "facts": [
                    "Token created by anonymous developer",
                    "97% of similar tokens fail within 24 hours",
                    "Current memecoin trend shows high risk",
                ],
                "importance": 0.5,
            },
        ]

        events = []
        for i, data in enumerate(mock_events[:limit]):
            event = Event(
                event_id=f"crypto_{i}_{datetime.utcnow().timestamp()}",
                title=data["title"],
                description=data["description"],
                source=EventSource.CRYPTO_FEED,
                category=EventCategory.CRYPTO,
                timestamp=datetime.utcnow(),
                facts=data["facts"],
                importance_score=data["importance"],
            )
            events.append(event)

        return events

    async def _fetch_news_events(self, limit: int = 10) -> List[Event]:
        """Fetch news events"""
        # Mock implementation
        mock_events = [
            {
                "title": "AI Regulation Bill Proposed",
                "description": "New legislation aims to regulate AI development and deployment",
                "category": EventCategory.POLITICS,
                "facts": [
                    "Bill requires AI systems to be auditable",
                    "Penalties up to $10M for violations",
                    "Industry leaders divided on approach",
                ],
                "importance": 0.8,
            },
            {
                "title": "Breakthrough in Quantum Computing",
                "description": "Research team achieves quantum advantage in practical application",
                "category": EventCategory.SCIENCE,
                "facts": [
                    "1000x faster than classical computers for specific task",
                    "Uses new error correction technique",
                    "Could impact cryptography significantly",
                ],
                "importance": 0.75,
            },
        ]

        events = []
        for i, data in enumerate(mock_events[:limit]):
            event = Event(
                event_id=f"news_{i}_{datetime.utcnow().timestamp()}",
                title=data["title"],
                description=data["description"],
                source=EventSource.NEWS,
                category=data["category"],
                timestamp=datetime.utcnow(),
                facts=data["facts"],
                importance_score=data["importance"],
            )
            events.append(event)

        return events

    async def _fetch_twitter_events(self, limit: int = 10) -> List[Event]:
        """Fetch trending Twitter topics"""
        # Mock implementation - would use Twitter API in production
        logger.info("Twitter integration not yet implemented, using mock data")
        return []

    def get_queue_size(self) -> int:
        """Get number of events in queue"""
        return len(self.event_queue)

    def get_processed_count(self) -> int:
        """Get number of processed events"""
        return len(self.processed_events)

    def clear_queue(self) -> None:
        """Clear event queue"""
        self.event_queue.clear()
        logger.info("Event queue cleared")
