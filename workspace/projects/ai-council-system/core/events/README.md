# Event Ingestion System

**Version**: 0.1.0
**Location**: `/workspace/projects/ai-council-system/core/events/`

## Overview

The Event Ingestion System captures real-time events from multiple sources, processes and enriches them, and extracts debate topics for AI council sessions.

## Architecture

```
Events Pipeline:
1. Ingestor → Fetch raw events from sources
2. Processor → Classify, enrich, and score events
3. Topic Extractor → Generate debate topics from events
4. Queue → Priority-based topic selection
```

## Components

### Event Ingestors (`ingestor.py`)
Fetch events from external sources.

**Supported Sources**:
- **Twitter**: Tweets via Twitter API
- **News API**: News articles from newsapi.org
- **RSS**: RSS/Atom feed items
- **Webhook**: Custom webhook events

### Event Processor (`processor.py`)
Process and enrich raw events.

**Processing Steps**:
1. Classification (11 categories)
2. Entity extraction (NER)
3. Sentiment analysis
4. Importance scoring
5. Keyword extraction
6. Priority assignment

### Topic Extractor (`topic_extractor.py`)
Extract debate topics from events.

**Features**:
- Event clustering
- Perspective identification
- Controversy scoring
- Background information collection

### Event Queue (`queue.py`)
Priority queues for events and topics.

**Queue Types**:
- **EventQueue**: Processed events (max 1000)
- **TopicQueue**: Debate topics (max 100)

## Quick Start

### Basic Event Ingestion

```python
from core.events import (
    IngestorFactory,
    EventProcessor,
    TopicExtractor,
    EventQueue,
    TopicQueue
)

# Create ingestors
twitter = IngestorFactory.create_twitter(
    api_key="your-key",
    keywords=["AI", "crypto", "politics"]
)

news = IngestorFactory.create_news_api(
    api_key="your-key",
    sources=["techcrunch", "bbc-news"]
)

# Create processor and queues
processor = EventProcessor()
event_queue = EventQueue(max_size=1000)
topic_queue = TopicQueue(max_size=100)

# Fetch and process events
raw_events = await twitter.fetch_events(limit=10)
processed_events = await processor.process_batch(raw_events)

# Add to queue
event_queue.add_batch(processed_events)

# Extract topics
extractor = TopicExtractor()
topics = await extractor.extract_topics(
    processed_events,
    limit=5,
    min_controversy=0.6
)

# Add to topic queue
topic_queue.add_batch(topics)

# Get next topic for debate
next_topic = topic_queue.get_next()
print(f"Next debate: {next_topic.title}")
```

### Continuous Polling

```python
# Define callback for new events
async def handle_events(raw_events):
    # Process events
    processed = await processor.process_batch(raw_events)
    event_queue.add_batch(processed)

    # Extract topics if enough events
    if event_queue.size() >= 10:
        recent_events = event_queue.peek(10)
        topics = await extractor.extract_topics(recent_events)
        topic_queue.add_batch(topics)

# Start polling
await twitter.start_polling(
    interval_seconds=60,
    callback=handle_events
)

# Let it run...
await asyncio.sleep(3600)

# Stop polling
await twitter.stop_polling()
```

## Event Categories

```python
class EventCategory(Enum):
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
```

## Event Priority

Events are assigned priority based on importance score:

| Score | Priority |
|-------|----------|
| 0.8+ | CRITICAL |
| 0.6-0.8 | HIGH |
| 0.4-0.6 | MEDIUM |
| <0.4 | LOW |

## Importance Scoring

Importance is calculated from:
- **Source credibility** (0.1-0.2): News API > RSS > Twitter
- **Category weight** (0.05-0.15): Crypto/AI weighted higher
- **Engagement** (0.0-0.2): Likes, retweets, shares
- **Keywords** (0.0-0.1): Presence of important keywords
- **Base score** (0.5): Starting point

## Topic Extraction

### Clustering Algorithm

Events are clustered by:
1. **Category + Keywords**: Same category and shared keywords
2. **Named Entities**: Shared organizations, people, or locations
3. **Minimum cluster size**: 2+ events

### Controversy Scoring

Controversy is based on sentiment variance:
- High variance in sentiment → High controversy
- Polarized events make better debates
- Score range: 0.0-1.0

### Perspective Generation

Perspectives are generated based on:
- Sentiment distribution
- Event category
- Predefined category perspectives

Example perspectives:
- **Politics**: Conservative, Progressive
- **Technology**: Technologist, Humanist
- **Economics**: Free Market, Regulated
- **Crypto**: Maximalist, Skeptic
- **AI**: Accelerationist, Safety-Focused

## Configuration Examples

### Twitter Ingestor

```python
twitter_config = {
    "api_key": "your-key",
    "keywords": ["AI", "regulation", "cryptocurrency"],
    "hashtags": ["#AIethics", "#crypto"],
    "accounts": ["@elonmusk", "@vitalikbuterin"]
}

twitter = IngestorFactory.create_twitter(**twitter_config)
```

### News API Ingestor

```python
news_config = {
    "api_key": "your-key",
    "sources": ["techcrunch", "bbc-news", "reuters"],
    "categories": ["technology", "business"],
    "keywords": ["artificial intelligence", "blockchain"]
}

news = IngestorFactory.create_news_api(**news_config)
```

### RSS Ingestor

```python
rss_config = {
    "feed_urls": [
        "https://blog.openai.com/rss/",
        "https://blog.anthropic.com/rss/",
        "https://coindesk.com/arc/outboundfeeds/rss/"
    ]
}

rss = IngestorFactory.create_rss(**rss_config)
```

## Processing Pipeline Example

```python
# Full pipeline
async def process_pipeline():
    # 1. Ingest
    raw_events = []
    raw_events.extend(await twitter.fetch_events(limit=20))
    raw_events.extend(await news.fetch_events(limit=10))
    raw_events.extend(await rss.fetch_events(limit=5))

    print(f"Ingested {len(raw_events)} raw events")

    # 2. Process
    processed = await processor.process_batch(raw_events)
    print(f"Processed {len(processed)} events")

    # 3. Queue
    event_queue.add_batch(processed)
    print(f"Event queue size: {event_queue.size()}")

    # 4. Extract topics
    topics = await extractor.extract_topics(
        processed,
        limit=5,
        min_controversy=0.5
    )
    print(f"Extracted {len(topics)} topics")

    # 5. Queue topics
    topic_queue.add_batch(topics)
    print(f"Topic queue size: {topic_queue.size()}")

    # 6. Get next topic
    next_topic = topic_queue.get_next()
    if next_topic:
        print(f"\nNext debate topic:")
        print(f"Title: {next_topic.title}")
        print(f"Perspectives: {', '.join(next_topic.perspectives)}")
        print(f"Importance: {next_topic.importance_score:.2f}")
        print(f"Controversy: {next_topic.controversy_score:.2f}")

await process_pipeline()
```

## Queue Operations

### EventQueue

```python
queue = EventQueue(max_size=1000)

# Add events
queue.add(processed_event)
queue.add_batch(events)

# Get next event (highest priority)
event = queue.get_next()

# Peek without removing
top_events = queue.peek(count=10)

# Filter by category
tech_events = queue.get_by_category(EventCategory.TECHNOLOGY, limit=5)

# Filter by priority
critical = queue.get_by_priority(EventPriority.CRITICAL, limit=5)

# Stats
stats = queue.get_stats()
print(f"Queue size: {stats['current_size']}")
print(f"Total added: {stats['total_added']}")
```

### TopicQueue

```python
queue = TopicQueue(max_size=100)

# Add topics
queue.add(topic)
queue.add_batch(topics)

# Get next topic (marks as used)
topic = queue.get_next()

# Peek without using
top_topics = queue.peek(count=5)

# Get by category
ai_topics = queue.get_by_category(EventCategory.AI, limit=3)

# Stats
stats = queue.get_stats()
print(f"Available topics: {stats['available_topics']}")
print(f"Used topics: {stats['used_topics']}")
```

## Statistics and Monitoring

```python
# Ingestor stats
twitter_stats = twitter.get_stats()
print(f"Twitter: {twitter_stats['events_fetched']} events fetched")

# Processor stats
proc_stats = processor.get_stats()
print(f"Processed: {proc_stats['processed_count']} events")

# Extractor stats
ext_stats = extractor.get_stats()
print(f"Topics generated: {ext_stats['topics_generated']}")

# Queue stats
eq_stats = event_queue.get_stats()
tq_stats = topic_queue.get_stats()

print(f"Event queue: {eq_stats['current_size']}/{eq_stats['max_size']}")
print(f"Topic queue: {tq_stats['available_topics']} available")
```

## Data Models

### ProcessedEvent

```python
{
    "event_id": "evt_twitter_1729680000_a1b2c3d4",
    "title": "AI Regulation Bill Passes Senate",
    "description": "Full event description...",
    "category": "politics",
    "priority": "high",
    "importance_score": 0.85,
    "sentiment": 0.2,  # Slightly positive
    "entities": [
        {"text": "Senate", "type": "ORG", "confidence": 0.9}
    ],
    "keywords": ["regulation", "senate", "bill"],
    "source": "news_api",
    "source_url": "https://...",
    "metadata": {...}
}
```

### DebateTopic

```python
{
    "topic_id": "topic_1729680000_xyz123",
    "title": "Should AI be heavily regulated?",
    "description": "Recent legislation proposals...",
    "category": "politics",
    "perspectives": ["Pro-regulation", "Anti-regulation", "Moderate"],
    "source_events": ["evt_...", "evt_..."],
    "background_info": {
        "entities": {...},
        "sources": [...],
        "event_count": 5
    },
    "importance_score": 0.82,
    "controversy_score": 0.75,
    "metadata": {...}
}
```

## Best Practices

1. **Polling Intervals**: 30-60 seconds for Twitter, 5-10 minutes for news
2. **Queue Sizes**: 1000 events, 100 topics (adjust based on volume)
3. **Controversy Threshold**: 0.5-0.7 for good debates
4. **Topic Extraction**: Extract after every 10-20 new events
5. **Deduplication**: Check event_id before adding to queue
6. **Error Handling**: Always wrap ingestion in try-catch
7. **Rate Limiting**: Respect API rate limits

## Future Enhancements

### Phase 2
- Advanced NER with spaCy/transformers
- ML-based importance scoring
- Semantic deduplication
- Multi-language support

### Phase 3
- Real-time stream processing (Kafka)
- Trend detection algorithms
- Predictive topic scoring
- User feedback integration

### Phase 4
- Custom event sources
- Advanced clustering (DBSCAN)
- Topic evolution tracking
- Automated fact-checking

---

**Module Status**: Phase 1 Complete
**Last Updated**: October 23, 2025
**Maintainer**: Development Team
