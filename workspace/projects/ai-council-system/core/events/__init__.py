"""
Event Ingestion Module

Real-time event ingestion, processing, and topic extraction for AI Council debates.
"""

from .event import (
    RawEvent,
    ProcessedEvent,
    DebateTopic,
    Entity,
    EventSource,
    EventCategory,
    EventPriority,
    EventStatistics,
)

from .ingestor import (
    EventIngestor,
    TwitterIngestor,
    NewsAPIIngestor,
    RSSIngestor,
    WebhookIngestor,
    IngestorFactory,
)

from .processor import EventProcessor

from .topic_extractor import TopicExtractor

from .queue import EventQueue, TopicQueue

__all__ = [
    # Event Models
    "RawEvent",
    "ProcessedEvent",
    "DebateTopic",
    "Entity",
    "EventSource",
    "EventCategory",
    "EventPriority",
    "EventStatistics",
    # Ingestors
    "EventIngestor",
    "TwitterIngestor",
    "NewsAPIIngestor",
    "RSSIngestor",
    "WebhookIngestor",
    "IngestorFactory",
    # Processing
    "EventProcessor",
    "TopicExtractor",
    # Queues
    "EventQueue",
    "TopicQueue",
]

__version__ = "0.1.0"
