"""
Event Processor - Process and enrich raw events

Classifies events, extracts entities, calculates importance, and enriches metadata.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
import re

from .event import (
    RawEvent,
    ProcessedEvent,
    EventCategory,
    EventPriority,
    Entity,
    EventSource,
)

logger = logging.getLogger(__name__)


class EventProcessor:
    """
    Processes and enriches raw events

    Performs classification, entity extraction, sentiment analysis,
    and importance scoring.
    """

    def __init__(self):
        self.processed_count = 0
        self.category_keywords = self._build_category_keywords()

    async def process(self, raw_event: RawEvent) -> ProcessedEvent:
        """
        Process raw event into enriched event

        Args:
            raw_event: Raw event from ingestor

        Returns:
            ProcessedEvent with enrichment
        """
        # Generate event ID
        event_id = self._generate_event_id(raw_event)

        # Extract title and description
        title, description = self._extract_title_description(raw_event.content)

        # Classify event
        category = await self._classify_event(raw_event.content)

        # Calculate importance score
        importance = await self._calculate_importance(raw_event, category)

        # Determine priority
        priority = self._determine_priority(importance)

        # Analyze sentiment
        sentiment = await self._analyze_sentiment(raw_event.content)

        # Extract entities
        entities = await self._extract_entities(raw_event.content)

        # Extract keywords
        keywords = await self._extract_keywords(raw_event.content)

        processed = ProcessedEvent(
            event_id=event_id,
            title=title,
            description=description,
            category=category,
            priority=priority,
            importance_score=importance,
            sentiment=sentiment,
            entities=entities,
            keywords=keywords,
            source=raw_event.source,
            source_url=raw_event.url,
            author=raw_event.author,
            ingestion_timestamp=datetime.utcnow(),
            event_timestamp=raw_event.timestamp,
            metadata=raw_event.metadata.copy()
        )

        self.processed_count += 1
        logger.debug(
            f"Processed event {event_id}: {title} "
            f"(category: {category.value}, importance: {importance:.2f})"
        )

        return processed

    async def process_batch(
        self,
        raw_events: List[RawEvent]
    ) -> List[ProcessedEvent]:
        """Process multiple events"""
        processed = []

        for raw_event in raw_events:
            try:
                processed_event = await self.process(raw_event)
                processed.append(processed_event)
            except Exception as e:
                logger.error(f"Error processing event: {e}")

        logger.info(f"Processed {len(processed)}/{len(raw_events)} events")
        return processed

    def _generate_event_id(self, raw_event: RawEvent) -> str:
        """Generate unique event ID"""
        import hashlib

        content_hash = hashlib.md5(
            raw_event.content.encode()
        ).hexdigest()[:8]

        timestamp = int(raw_event.timestamp.timestamp())
        return f"evt_{raw_event.source.value}_{timestamp}_{content_hash}"

    def _extract_title_description(self, content: str) -> tuple[str, str]:
        """Extract title and description from content"""
        # Split on period or newline
        parts = re.split(r'[.\n]', content, maxsplit=1)

        if len(parts) == 2:
            title = parts[0].strip()
            description = parts[1].strip()
        else:
            title = content[:100] + "..." if len(content) > 100 else content
            description = content

        return title, description

    async def _classify_event(self, content: str) -> EventCategory:
        """
        Classify event into category

        Uses keyword matching (simplified).
        Production would use ML classification.
        """
        content_lower = content.lower()

        # Score each category
        scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > 0:
                scores[category] = score

        # Return category with highest score
        if scores:
            best_category = max(scores.items(), key=lambda x: x[1])[0]
            return EventCategory[best_category.upper()]

        return EventCategory.OTHER

    async def _calculate_importance(
        self,
        raw_event: RawEvent,
        category: EventCategory
    ) -> float:
        """
        Calculate importance score (0.0-1.0)

        Factors:
        - Source credibility
        - Engagement metrics
        - Category weight
        - Keyword presence
        - Recency
        """
        score = 0.5  # Base score

        # Source weight
        source_weights = {
            EventSource.NEWS_API: 0.2,
            EventSource.TWITTER: 0.1,
            EventSource.RSS: 0.15,
            EventSource.WEBHOOK: 0.1,
        }
        score += source_weights.get(raw_event.source, 0.1)

        # Category weight
        category_weights = {
            EventCategory.POLITICS: 0.1,
            EventCategory.TECHNOLOGY: 0.1,
            EventCategory.ECONOMICS: 0.1,
            EventCategory.CRYPTO: 0.15,
            EventCategory.AI: 0.15,
        }
        score += category_weights.get(category, 0.05)

        # Engagement metrics (for Twitter)
        if raw_event.source == EventSource.TWITTER:
            likes = raw_event.metadata.get("likes", 0)
            retweets = raw_event.metadata.get("retweets", 0)
            engagement = (likes + retweets * 2) / 1000
            score += min(0.2, engagement * 0.1)

        # Important keywords
        important_keywords = [
            "breaking", "urgent", "crisis", "major", "significant",
            "announced", "revealed", "confirmed", "official"
        ]
        content_lower = raw_event.content.lower()
        keyword_count = sum(1 for kw in important_keywords if kw in content_lower)
        score += min(0.1, keyword_count * 0.03)

        return min(1.0, score)

    def _determine_priority(self, importance: float) -> EventPriority:
        """Determine priority from importance score"""
        if importance >= 0.8:
            return EventPriority.CRITICAL
        elif importance >= 0.6:
            return EventPriority.HIGH
        elif importance >= 0.4:
            return EventPriority.MEDIUM
        else:
            return EventPriority.LOW

    async def _analyze_sentiment(self, content: str) -> float:
        """
        Analyze sentiment (-1.0 to 1.0)

        Simplified implementation using keyword matching.
        Production would use sentiment analysis models.
        """
        positive_words = [
            "good", "great", "excellent", "positive", "success",
            "achievement", "breakthrough", "win", "celebrate", "amazing"
        ]

        negative_words = [
            "bad", "terrible", "negative", "failure", "crisis",
            "disaster", "problem", "concern", "worry", "alarming"
        ]

        content_lower = content.lower()
        words = content_lower.split()

        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)

        total = positive_count + negative_count
        if total == 0:
            return 0.0

        sentiment = (positive_count - negative_count) / total
        return max(-1.0, min(1.0, sentiment))

    async def _extract_entities(self, content: str) -> List[Entity]:
        """
        Extract named entities

        Simplified implementation using patterns.
        Production would use NER models (spaCy, etc.)
        """
        entities = []

        # Simple pattern matching for common entities
        # Organizations (capitalized multi-word)
        org_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
        orgs = re.findall(org_pattern, content)
        for org in orgs[:5]:  # Limit to 5
            entities.append(Entity(
                text=org,
                entity_type="ORG",
                confidence=0.7
            ))

        # Currencies/Crypto
        crypto_pattern = r'\b(Bitcoin|Ethereum|BTC|ETH|crypto|cryptocurrency)\b'
        cryptos = re.findall(crypto_pattern, content, re.IGNORECASE)
        for crypto in cryptos[:3]:
            entities.append(Entity(
                text=crypto,
                entity_type="CRYPTO",
                confidence=0.9
            ))

        # Numbers with units (could be money, metrics, etc.)
        number_pattern = r'\$?[\d,]+\.?\d*\s*(?:billion|million|thousand|%)?'
        numbers = re.findall(number_pattern, content)
        for num in numbers[:3]:
            entities.append(Entity(
                text=num,
                entity_type="QUANTITY",
                confidence=0.8
            ))

        return entities

    async def _extract_keywords(self, content: str) -> List[str]:
        """
        Extract important keywords

        Simplified implementation using word frequency.
        Production would use TF-IDF or keyword extraction models.
        """
        # Remove common words (stopwords)
        stopwords = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at",
            "to", "for", "of", "with", "by", "from", "as", "is", "was",
            "are", "were", "been", "be", "have", "has", "had", "do",
            "does", "did", "will", "would", "could", "should", "may",
            "might", "can", "this", "that", "these", "those", "i", "you",
            "he", "she", "it", "we", "they", "them", "their", "what",
            "which", "who", "when", "where", "why", "how"
        }

        # Extract words
        words = re.findall(r'\b[a-z]+\b', content.lower())

        # Filter stopwords and short words
        keywords = [
            w for w in words
            if w not in stopwords and len(w) > 3
        ]

        # Count frequency
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Get top keywords
        top_keywords = sorted(
            word_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return [word for word, freq in top_keywords]

    def _build_category_keywords(self) -> Dict[str, List[str]]:
        """Build keyword mappings for categories"""
        return {
            "politics": [
                "president", "congress", "senate", "election", "vote",
                "government", "policy", "legislation", "bill", "law"
            ],
            "technology": [
                "tech", "software", "hardware", "computer", "digital",
                "internet", "app", "platform", "startup", "innovation"
            ],
            "economics": [
                "economy", "market", "stock", "trade", "gdp", "inflation",
                "recession", "growth", "finance", "economic"
            ],
            "science": [
                "research", "study", "scientist", "discovery", "experiment",
                "university", "lab", "findings", "published", "journal"
            ],
            "crypto": [
                "bitcoin", "ethereum", "crypto", "blockchain", "btc", "eth",
                "defi", "nft", "coin", "token", "wallet"
            ],
            "ai": [
                "ai", "artificial intelligence", "machine learning", "ml",
                "neural", "model", "llm", "gpt", "chatbot", "algorithm"
            ],
            "sports": [
                "game", "team", "player", "score", "win", "championship",
                "league", "coach", "season", "match"
            ],
            "entertainment": [
                "movie", "film", "show", "series", "actor", "music",
                "album", "concert", "celebrity", "award"
            ],
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics"""
        return {
            "processed_count": self.processed_count,
        }
