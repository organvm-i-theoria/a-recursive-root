"""
Event - Core event models and data structures

Defines event types and structures for the ingestion system.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EventSource(Enum):
    """Event source types"""
    TWITTER = "twitter"
    NEWS_API = "news_api"
    RSS = "rss"
    WEBHOOK = "webhook"
    MANUAL = "manual"


class EventCategory(Enum):
    """Event categories for classification"""
    POLITICS = "politics"
    TECHNOLOGY = "technology"
    ECONOMICS = "economics"
    SCIENCE = "science"
    CULTURE = "culture"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    CRYPTO = "crypto"
    AI = "ai"
    WORLD = "world"
    OTHER = "other"


class EventPriority(Enum):
    """Event priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Entity:
    """Named entity extracted from event"""
    text: str
    entity_type: str  # "PERSON", "ORG", "GPE", "EVENT", etc.
    confidence: float = 1.0


@dataclass
class RawEvent:
    """Raw event from external source"""
    source: EventSource
    content: str
    url: Optional[str] = None
    author: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "source": self.source.value,
            "content": self.content,
            "url": self.url,
            "author": self.author,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class ProcessedEvent:
    """Processed and enriched event"""
    event_id: str
    title: str
    description: str
    category: EventCategory
    priority: EventPriority
    importance_score: float  # 0.0-1.0
    sentiment: float  # -1.0 to 1.0 (negative to positive)
    entities: List[Entity]
    keywords: List[str]
    source: EventSource
    source_url: Optional[str] = None
    author: Optional[str] = None
    ingestion_timestamp: datetime = field(default_factory=datetime.utcnow)
    event_timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "event_id": self.event_id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "priority": self.priority.value,
            "importance_score": self.importance_score,
            "sentiment": self.sentiment,
            "entities": [
                {"text": e.text, "type": e.entity_type, "confidence": e.confidence}
                for e in self.entities
            ],
            "keywords": self.keywords,
            "source": self.source.value,
            "source_url": self.source_url,
            "author": self.author,
            "ingestion_timestamp": self.ingestion_timestamp.isoformat(),
            "event_timestamp": self.event_timestamp.isoformat() if self.event_timestamp else None,
            "metadata": self.metadata,
        }


@dataclass
class DebateTopic:
    """Debate topic extracted from events"""
    topic_id: str
    title: str
    description: str
    category: EventCategory
    perspectives: List[str]
    source_events: List[str]  # Event IDs
    background_info: Dict[str, Any]
    importance_score: float
    controversy_score: float  # How controversial/debatable
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "topic_id": self.topic_id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "perspectives": self.perspectives,
            "source_events": self.source_events,
            "background_info": self.background_info,
            "importance_score": self.importance_score,
            "controversy_score": self.controversy_score,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class EventStatistics:
    """Statistics for event ingestion"""
    total_ingested: int = 0
    total_processed: int = 0
    total_topics_extracted: int = 0
    events_by_source: Dict[str, int] = field(default_factory=dict)
    events_by_category: Dict[str, int] = field(default_factory=dict)
    avg_importance_score: float = 0.0
    avg_sentiment: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "total_ingested": self.total_ingested,
            "total_processed": self.total_processed,
            "total_topics_extracted": self.total_topics_extracted,
            "events_by_source": self.events_by_source,
            "events_by_category": self.events_by_category,
            "avg_importance_score": self.avg_importance_score,
            "avg_sentiment": self.avg_sentiment,
        }
