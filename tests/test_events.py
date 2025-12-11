"""Tests for event ingestion system"""

import pytest
import asyncio

from core.events.event_ingestion import (
    EventIngester,
    EventSource,
    EventCategory,
    Event
)


@pytest.fixture
def ingester():
    """Create event ingester"""
    return EventIngester()


def test_ingester_creation(ingester):
    """Test creating ingester"""
    assert ingester.get_queue_size() == 0
    assert len(ingester.active_sources) == 0


def test_enable_source(ingester):
    """Test enabling event source"""
    ingester.enable_source(EventSource.MANUAL)

    assert EventSource.MANUAL in ingester.active_sources


def test_add_manual_event(ingester):
    """Test adding manual event"""
    event = ingester.add_manual_event(
        title="Test Event",
        description="A test event",
        category=EventCategory.TECHNOLOGY,
        facts=["Fact 1", "Fact 2"]
    )

    assert event.title == "Test Event"
    assert event.category == EventCategory.TECHNOLOGY
    assert len(event.facts) == 2
    assert ingester.get_queue_size() == 1


@pytest.mark.asyncio
async def test_fetch_crypto_events(ingester):
    """Test fetching crypto events"""
    ingester.enable_source(EventSource.CRYPTO_FEED)

    events = await ingester.fetch_events(limit=5)

    assert len(events) > 0
    assert all(e.category == EventCategory.CRYPTO for e in events if e.source == EventSource.CRYPTO_FEED)


@pytest.mark.asyncio
async def test_get_next_event(ingester):
    """Test getting next event"""
    ingester.add_manual_event(
        title="Event 1",
        description="First event",
    )

    event = await ingester.get_next_event()

    assert event is not None
    assert event.title == "Event 1"
    assert ingester.get_processed_count() == 1


def test_event_to_debate_topic():
    """Test converting event to debate topic"""
    from datetime import datetime

    event = Event(
        event_id="test",
        title="AI Ethics",
        description="Should AI be regulated?",
        source=EventSource.MANUAL,
        category=EventCategory.POLITICS,
        timestamp=datetime.utcnow(),
    )

    topic = event.to_debate_topic()

    assert "AI Ethics" in topic
    assert "Should AI be regulated?" in topic
