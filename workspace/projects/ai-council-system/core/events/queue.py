"""
Event Queue - Priority queue for events and topics

Manages event and topic queues with priority-based scheduling.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import deque
import heapq
import logging

from .event import ProcessedEvent, DebateTopic, EventPriority

logger = logging.getLogger(__name__)


class EventQueue:
    """
    Priority queue for processed events

    Events are prioritized by importance and recency.
    """

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.queue: List[tuple] = []  # Heap queue
        self.events_by_id: Dict[str, ProcessedEvent] = {}
        self.total_added = 0
        self.total_removed = 0

    def add(self, event: ProcessedEvent) -> None:
        """Add event to queue"""
        if event.event_id in self.events_by_id:
            logger.debug(f"Event {event.event_id} already in queue")
            return

        # Priority score (negative for max heap behavior)
        priority = -(event.importance_score + self._recency_score(event))

        heapq.heappush(
            self.queue,
            (priority, event.ingestion_timestamp, event.event_id, event)
        )

        self.events_by_id[event.event_id] = event
        self.total_added += 1

        # Prune if over capacity
        if len(self.queue) > self.max_size:
            self._prune_old()

        logger.debug(
            f"Added event {event.event_id} to queue "
            f"(priority: {-priority:.2f}, size: {len(self.queue)})"
        )

    def add_batch(self, events: List[ProcessedEvent]) -> None:
        """Add multiple events"""
        for event in events:
            self.add(event)

        logger.info(f"Added {len(events)} events to queue")

    def get_next(self) -> Optional[ProcessedEvent]:
        """Get highest priority event"""
        while self.queue:
            _, _, event_id, event = heapq.heappop(self.queue)

            # Check if still valid
            if event_id in self.events_by_id:
                del self.events_by_id[event_id]
                self.total_removed += 1
                return event

        return None

    def peek(self, count: int = 1) -> List[ProcessedEvent]:
        """Peek at top N events without removing"""
        results = []
        seen = set()

        for priority, timestamp, event_id, event in sorted(self.queue):
            if event_id in self.events_by_id and event_id not in seen:
                results.append(event)
                seen.add(event_id)

                if len(results) >= count:
                    break

        return results

    def get_by_category(
        self,
        category,
        limit: int = 10
    ) -> List[ProcessedEvent]:
        """Get events by category"""
        events = [
            event for _, _, _, event in self.queue
            if event.category == category and event.event_id in self.events_by_id
        ]

        # Sort by priority
        events.sort(
            key=lambda e: e.importance_score,
            reverse=True
        )

        return events[:limit]

    def get_by_priority(
        self,
        priority: EventPriority,
        limit: int = 10
    ) -> List[ProcessedEvent]:
        """Get events by priority level"""
        events = [
            event for _, _, _, event in self.queue
            if event.priority == priority and event.event_id in self.events_by_id
        ]

        events.sort(
            key=lambda e: e.importance_score,
            reverse=True
        )

        return events[:limit]

    def _recency_score(self, event: ProcessedEvent) -> float:
        """Calculate recency score (0.0-0.3)"""
        age = (datetime.utcnow() - event.ingestion_timestamp).total_seconds()
        hours = age / 3600

        # Decay over 24 hours
        recency = max(0.0, 0.3 * (1.0 - hours / 24))
        return recency

    def _prune_old(self) -> None:
        """Remove oldest/lowest priority events"""
        # Rebuild queue with top events only
        sorted_queue = sorted(self.queue)
        keep = sorted_queue[:self.max_size]

        # Update structures
        self.queue = keep
        heapq.heapify(self.queue)

        # Update events dict
        keep_ids = {event_id for _, _, event_id, _ in keep}
        self.events_by_id = {
            event_id: event
            for event_id, event in self.events_by_id.items()
            if event_id in keep_ids
        }

        logger.info(f"Pruned queue to {len(self.queue)} events")

    def clear(self) -> None:
        """Clear the queue"""
        self.queue.clear()
        self.events_by_id.clear()

    def size(self) -> int:
        """Get current queue size"""
        return len(self.queue)

    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return len(self.queue) == 0

    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return {
            "current_size": len(self.queue),
            "max_size": self.max_size,
            "total_added": self.total_added,
            "total_removed": self.total_removed,
        }


class TopicQueue:
    """
    Priority queue for debate topics

    Topics are prioritized by importance, controversy, and recency.
    """

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.queue: List[tuple] = []
        self.topics_by_id: Dict[str, DebateTopic] = {}
        self.used_topics: set = set()  # Track used topics
        self.total_added = 0
        self.total_used = 0

    def add(self, topic: DebateTopic) -> None:
        """Add topic to queue"""
        if topic.topic_id in self.topics_by_id:
            logger.debug(f"Topic {topic.topic_id} already in queue")
            return

        # Priority score
        priority = -(
            topic.importance_score * 0.5 +
            topic.controversy_score * 0.4 +
            self._recency_score(topic) * 0.1
        )

        heapq.heappush(
            self.queue,
            (priority, topic.created_at, topic.topic_id, topic)
        )

        self.topics_by_id[topic.topic_id] = topic
        self.total_added += 1

        # Prune if over capacity
        if len(self.queue) > self.max_size:
            self._prune_old()

        logger.debug(
            f"Added topic {topic.topic_id} to queue "
            f"(priority: {-priority:.2f})"
        )

    def add_batch(self, topics: List[DebateTopic]) -> None:
        """Add multiple topics"""
        for topic in topics:
            self.add(topic)

        logger.info(f"Added {len(topics)} topics to queue")

    def get_next(self, mark_used: bool = True) -> Optional[DebateTopic]:
        """Get highest priority topic"""
        while self.queue:
            _, _, topic_id, topic = heapq.heappop(self.queue)

            # Skip used topics
            if topic_id in self.used_topics:
                continue

            # Check if still valid
            if topic_id in self.topics_by_id:
                del self.topics_by_id[topic_id]

                if mark_used:
                    self.used_topics.add(topic_id)
                    self.total_used += 1

                return topic

        return None

    def peek(self, count: int = 1) -> List[DebateTopic]:
        """Peek at top N topics without removing"""
        results = []
        seen = set()

        for priority, timestamp, topic_id, topic in sorted(self.queue):
            if (
                topic_id in self.topics_by_id
                and topic_id not in self.used_topics
                and topic_id not in seen
            ):
                results.append(topic)
                seen.add(topic_id)

                if len(results) >= count:
                    break

        return results

    def get_by_category(
        self,
        category,
        limit: int = 5
    ) -> List[DebateTopic]:
        """Get topics by category"""
        topics = [
            topic for _, _, _, topic in self.queue
            if (
                topic.category == category
                and topic.topic_id in self.topics_by_id
                and topic.topic_id not in self.used_topics
            )
        ]

        topics.sort(
            key=lambda t: (t.importance_score + t.controversy_score) / 2,
            reverse=True
        )

        return topics[:limit]

    def mark_used(self, topic_id: str) -> None:
        """Mark topic as used"""
        self.used_topics.add(topic_id)
        self.total_used += 1

    def _recency_score(self, topic: DebateTopic) -> float:
        """Calculate recency score"""
        age = (datetime.utcnow() - topic.created_at).total_seconds()
        hours = age / 3600

        # Decay over 48 hours
        recency = max(0.0, 1.0 - hours / 48)
        return recency

    def _prune_old(self) -> None:
        """Remove oldest/lowest priority topics"""
        sorted_queue = sorted(self.queue)
        keep = sorted_queue[:self.max_size]

        self.queue = keep
        heapq.heapify(self.queue)

        keep_ids = {topic_id for _, _, topic_id, _ in keep}
        self.topics_by_id = {
            topic_id: topic
            for topic_id, topic in self.topics_by_id.items()
            if topic_id in keep_ids
        }

        logger.info(f"Pruned topic queue to {len(self.queue)}")

    def clear(self) -> None:
        """Clear the queue"""
        self.queue.clear()
        self.topics_by_id.clear()
        # Don't clear used_topics to prevent reuse

    def size(self) -> int:
        """Get current queue size"""
        return len(self.queue)

    def available_count(self) -> int:
        """Get count of unused topics"""
        return sum(
            1 for _, _, topic_id, _ in self.queue
            if topic_id not in self.used_topics
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return {
            "current_size": len(self.queue),
            "available_topics": self.available_count(),
            "used_topics": len(self.used_topics),
            "max_size": self.max_size,
            "total_added": self.total_added,
            "total_used": self.total_used,
        }
