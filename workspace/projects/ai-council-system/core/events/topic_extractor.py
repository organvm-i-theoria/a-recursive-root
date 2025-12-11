"""
Topic Extractor - Extract debate topics from events

Analyzes events and generates debate topics with multiple perspectives.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from .event import ProcessedEvent, DebateTopic, EventCategory

logger = logging.getLogger(__name__)


class TopicExtractor:
    """
    Extracts debate topics from processed events

    Clusters related events, identifies controversial issues,
    and generates balanced debate topics.
    """

    def __init__(self):
        self.topics_generated = 0
        self.event_clusters: Dict[str, List[ProcessedEvent]] = defaultdict(list)

    async def extract_topics(
        self,
        events: List[ProcessedEvent],
        limit: int = 10,
        min_controversy: float = 0.5
    ) -> List[DebateTopic]:
        """
        Extract debate topics from events

        Args:
            events: Processed events to analyze
            limit: Maximum number of topics to generate
            min_controversy: Minimum controversy score

        Returns:
            List of DebateTopic objects
        """
        logger.info(f"Extracting topics from {len(events)} events")

        # Cluster related events
        clusters = await self._cluster_events(events)

        # Generate topics from clusters
        topics = []
        for cluster_key, cluster_events in clusters.items():
            if len(cluster_events) < 2:  # Need multiple events for debate
                continue

            topic = await self._generate_topic(cluster_events)

            # Filter by controversy
            if topic.controversy_score >= min_controversy:
                topics.append(topic)

        # Sort by importance and controversy
        topics.sort(
            key=lambda t: (t.importance_score + t.controversy_score) / 2,
            reverse=True
        )

        self.topics_generated += len(topics[:limit])
        logger.info(f"Generated {len(topics[:limit])} topics")

        return topics[:limit]

    async def _cluster_events(
        self,
        events: List[ProcessedEvent]
    ) -> Dict[str, List[ProcessedEvent]]:
        """
        Cluster related events

        Groups events by shared keywords and categories.
        """
        clusters = defaultdict(list)

        for event in events:
            # Create cluster key from category and top keywords
            top_keywords = event.keywords[:3] if event.keywords else []
            cluster_key = f"{event.category.value}_{'_'.join(top_keywords)}"

            clusters[cluster_key].append(event)

        # Also cluster by shared entities
        entity_clusters = defaultdict(list)
        for event in events:
            for entity in event.entities:
                if entity.entity_type in ["ORG", "PERSON", "GPE"]:
                    entity_clusters[entity.text].append(event)

        # Merge entity clusters with significant overlap
        for entity_text, entity_events in entity_clusters.items():
            if len(entity_events) >= 2:
                cluster_key = f"entity_{entity_text.replace(' ', '_')}"
                clusters[cluster_key].extend(entity_events)

        logger.debug(f"Created {len(clusters)} event clusters")
        return clusters

    async def _generate_topic(
        self,
        events: List[ProcessedEvent]
    ) -> DebateTopic:
        """Generate debate topic from event cluster"""
        # Calculate aggregate importance
        avg_importance = sum(e.importance_score for e in events) / len(events)

        # Calculate controversy (based on sentiment variance)
        sentiments = [e.sentiment for e in events]
        sentiment_variance = self._calculate_variance(sentiments)
        controversy = min(1.0, sentiment_variance * 2)  # Normalize

        # Get common category
        categories = [e.category for e in events]
        category = max(set(categories), key=categories.count)

        # Generate title from events
        title = await self._generate_title(events)

        # Generate description
        description = await self._generate_description(events)

        # Extract perspectives
        perspectives = await self._extract_perspectives(events)

        # Collect background info
        background = await self._collect_background(events)

        # Generate topic ID
        topic_id = self._generate_topic_id(events)

        topic = DebateTopic(
            topic_id=topic_id,
            title=title,
            description=description,
            category=category,
            perspectives=perspectives,
            source_events=[e.event_id for e in events],
            background_info=background,
            importance_score=avg_importance,
            controversy_score=controversy,
            metadata={
                "event_count": len(events),
                "avg_sentiment": sum(sentiments) / len(sentiments),
            }
        )

        return topic

    async def _generate_title(self, events: List[ProcessedEvent]) -> str:
        """Generate topic title from events"""
        # Get most common keywords across events
        all_keywords = []
        for event in events:
            all_keywords.extend(event.keywords[:3])

        keyword_freq = defaultdict(int)
        for kw in all_keywords:
            keyword_freq[kw] += 1

        # Get top keywords
        top_keywords = sorted(
            keyword_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        # Get most important event title as base
        most_important = max(events, key=lambda e: e.importance_score)

        # Combine into debate question
        keywords_str = ", ".join([kw for kw, _ in top_keywords])

        # Create question format
        title = f"Should we {keywords_str}?"

        # Or use event title if it's already good
        if "?" in most_important.title or any(
            word in most_important.title.lower()
            for word in ["should", "will", "can", "how"]
        ):
            title = most_important.title

        return title[:200]  # Limit length

    async def _generate_description(
        self,
        events: List[ProcessedEvent]
    ) -> str:
        """Generate topic description from events"""
        # Summarize key events
        summaries = []

        # Get up to 3 most important events
        top_events = sorted(
            events,
            key=lambda e: e.importance_score,
            reverse=True
        )[:3]

        for event in top_events:
            summaries.append(event.description[:150])

        description = " ".join(summaries)
        return description[:500]  # Limit length

    async def _extract_perspectives(
        self,
        events: List[ProcessedEvent]
    ) -> List[str]:
        """Extract debate perspectives from events"""
        # Analyze sentiment distribution
        sentiments = [e.sentiment for e in events]
        avg_sentiment = sum(sentiments) / len(sentiments)

        perspectives = []

        # Base perspectives on sentiment and category
        if avg_sentiment > 0.2:
            perspectives.append("Supportive")
            perspectives.append("Cautiously Optimistic")
        elif avg_sentiment < -0.2:
            perspectives.append("Critical")
            perspectives.append("Reform-Focused")
        else:
            perspectives.append("Neutral/Analytical")

        # Add opposing perspective for balance
        if "Supportive" in perspectives:
            perspectives.append("Skeptical")
        elif "Critical" in perspectives:
            perspectives.append("Defensive")

        # Add category-specific perspectives
        category = events[0].category
        category_perspectives = {
            EventCategory.POLITICS: ["Conservative", "Progressive"],
            EventCategory.TECHNOLOGY: ["Technologist", "Humanist"],
            EventCategory.ECONOMICS: ["Free Market", "Regulated"],
            EventCategory.CRYPTO: ["Maximalist", "Skeptic"],
            EventCategory.AI: ["Accelerationist", "Safety-Focused"],
        }

        if category in category_perspectives:
            perspectives.extend(category_perspectives[category])

        # Return unique perspectives
        return list(set(perspectives))[:5]

    async def _collect_background(
        self,
        events: List[ProcessedEvent]
    ) -> Dict[str, Any]:
        """Collect background information"""
        # Aggregate entities
        all_entities = []
        for event in events:
            all_entities.extend(event.entities)

        # Get unique entities by type
        entities_by_type = defaultdict(list)
        seen = set()
        for entity in all_entities:
            if entity.text not in seen:
                entities_by_type[entity.entity_type].append(entity.text)
                seen.add(entity.text)

        # Collect source URLs
        sources = [e.source_url for e in events if e.source_url]

        return {
            "entities": dict(entities_by_type),
            "sources": sources[:10],
            "timeframe": {
                "start": min(e.event_timestamp for e in events if e.event_timestamp).isoformat() if any(e.event_timestamp for e in events) else None,
                "end": max(e.event_timestamp for e in events if e.event_timestamp).isoformat() if any(e.event_timestamp for e in events) else None,
            },
            "event_count": len(events),
        }

    def _generate_topic_id(self, events: List[ProcessedEvent]) -> str:
        """Generate unique topic ID"""
        import hashlib

        # Hash event IDs to create unique topic ID
        event_ids = "".join(sorted([e.event_id for e in events]))
        topic_hash = hashlib.md5(event_ids.encode()).hexdigest()[:8]

        timestamp = int(datetime.utcnow().timestamp())
        return f"topic_{timestamp}_{topic_hash}"

    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values"""
        if not values:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5  # Standard deviation

    def get_stats(self) -> Dict[str, Any]:
        """Get extractor statistics"""
        return {
            "topics_generated": self.topics_generated,
            "active_clusters": len(self.event_clusters),
        }
