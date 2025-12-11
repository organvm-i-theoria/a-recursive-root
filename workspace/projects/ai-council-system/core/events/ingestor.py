"""
Event Ingestors - Fetch events from various sources

Provides ingestors for Twitter, news APIs, RSS feeds, and webhooks.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging
import asyncio

from .event import RawEvent, EventSource

logger = logging.getLogger(__name__)


class EventIngestor(ABC):
    """
    Abstract base class for event ingestors

    Subclasses implement specific source integrations.
    """

    def __init__(self, source: EventSource, config: Dict[str, Any]):
        self.source = source
        self.config = config
        self.events_fetched = 0
        self.last_fetch: Optional[datetime] = None
        self.is_running = False

    @abstractmethod
    async def fetch_events(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[RawEvent]:
        """
        Fetch events from source

        Args:
            since: Fetch events since this timestamp
            limit: Maximum number of events to fetch

        Returns:
            List of RawEvent objects
        """
        pass

    async def start_polling(
        self,
        interval_seconds: int = 60,
        callback: Optional[callable] = None
    ) -> None:
        """
        Start polling source at regular intervals

        Args:
            interval_seconds: Polling interval in seconds
            callback: Optional callback function for new events
        """
        self.is_running = True
        logger.info(
            f"Started polling {self.source.value} every {interval_seconds}s"
        )

        while self.is_running:
            try:
                events = await self.fetch_events(since=self.last_fetch)

                if events:
                    logger.info(
                        f"Fetched {len(events)} events from {self.source.value}"
                    )
                    self.events_fetched += len(events)

                    if callback:
                        await callback(events)

                self.last_fetch = datetime.utcnow()

            except Exception as e:
                logger.error(f"Error polling {self.source.value}: {e}")

            await asyncio.sleep(interval_seconds)

    async def stop_polling(self) -> None:
        """Stop polling"""
        self.is_running = False
        logger.info(f"Stopped polling {self.source.value}")

    def get_stats(self) -> Dict[str, Any]:
        """Get ingestor statistics"""
        return {
            "source": self.source.value,
            "events_fetched": self.events_fetched,
            "last_fetch": self.last_fetch.isoformat() if self.last_fetch else None,
            "is_running": self.is_running,
        }


class TwitterIngestor(EventIngestor):
    """
    Twitter/X API ingestor

    Fetches tweets based on keywords, hashtags, or accounts.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(EventSource.TWITTER, config)
        self.api_key = config.get("api_key")
        self.keywords = config.get("keywords", [])
        self.hashtags = config.get("hashtags", [])
        self.accounts = config.get("accounts", [])

    async def fetch_events(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[RawEvent]:
        """Fetch tweets"""
        logger.debug(f"Fetching tweets (keywords: {self.keywords})")

        # Placeholder implementation
        # Real implementation would use Twitter API:
        # import tweepy
        # auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        # api = tweepy.API(auth)
        # tweets = api.search_tweets(q=query, count=limit, since_id=since_id)

        # Mock events for now
        events = []

        # Simulate fetching tweets
        if not since:
            since = datetime.utcnow() - timedelta(hours=1)

        # Mock tweet data
        mock_tweets = [
            "Breaking: Major development in AI regulation",
            "Bitcoin reaches new all-time high of $125,000",
            "Tech companies announce new quantum computing breakthrough",
        ]

        for i, tweet in enumerate(mock_tweets[:limit or 3]):
            event = RawEvent(
                source=EventSource.TWITTER,
                content=tweet,
                url=f"https://twitter.com/user/status/{i}",
                author=f"@user{i}",
                timestamp=datetime.utcnow(),
                metadata={
                    "likes": 100 + i * 50,
                    "retweets": 20 + i * 10,
                    "hashtags": ["#AI", "#tech"],
                }
            )
            events.append(event)

        return events


class NewsAPIIngestor(EventIngestor):
    """
    News API ingestor

    Fetches news articles from newsapi.org or similar services.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(EventSource.NEWS_API, config)
        self.api_key = config.get("api_key")
        self.sources = config.get("sources", [])
        self.categories = config.get("categories", [])
        self.keywords = config.get("keywords", [])

    async def fetch_events(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[RawEvent]:
        """Fetch news articles"""
        logger.debug(f"Fetching news articles (sources: {self.sources})")

        # Placeholder implementation
        # Real implementation would use News API:
        # from newsapi import NewsApiClient
        # newsapi = NewsApiClient(api_key=self.api_key)
        # articles = newsapi.get_everything(
        #     q=keywords,
        #     sources=sources,
        #     from_param=since,
        #     page_size=limit
        # )

        events = []

        # Mock news data
        mock_articles = [
            {
                "title": "AI Regulation Bill Passes Senate",
                "description": "New legislation sets framework for AI governance",
                "url": "https://news.example.com/ai-regulation",
                "author": "Jane Reporter",
                "source": "Tech News Daily",
            },
            {
                "title": "Cryptocurrency Market Surge Continues",
                "description": "Bitcoin and Ethereum reach new highs amid institutional adoption",
                "url": "https://news.example.com/crypto-surge",
                "author": "John Analyst",
                "source": "Crypto Times",
            },
        ]

        for article in mock_articles[:limit or 2]:
            event = RawEvent(
                source=EventSource.NEWS_API,
                content=f"{article['title']}. {article['description']}",
                url=article["url"],
                author=article["author"],
                timestamp=datetime.utcnow(),
                metadata={
                    "source_name": article["source"],
                    "title": article["title"],
                }
            )
            events.append(event)

        return events


class RSSIngestor(EventIngestor):
    """
    RSS feed ingestor

    Fetches items from RSS/Atom feeds.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(EventSource.RSS, config)
        self.feed_urls = config.get("feed_urls", [])

    async def fetch_events(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[RawEvent]:
        """Fetch RSS feed items"""
        logger.debug(f"Fetching from {len(self.feed_urls)} RSS feeds")

        # Placeholder implementation
        # Real implementation would use feedparser:
        # import feedparser
        # for feed_url in self.feed_urls:
        #     feed = feedparser.parse(feed_url)
        #     for entry in feed.entries:
        #         # Process entry

        events = []

        # Mock RSS data
        mock_items = [
            {
                "title": "New AI Model Achieves Human-Level Performance",
                "summary": "Researchers announce breakthrough in language understanding",
                "link": "https://blog.example.com/ai-breakthrough",
            }
        ]

        for item in mock_items[:limit or 1]:
            event = RawEvent(
                source=EventSource.RSS,
                content=f"{item['title']}. {item['summary']}",
                url=item["link"],
                timestamp=datetime.utcnow(),
                metadata={"feed_url": "https://blog.example.com/feed"}
            )
            events.append(event)

        return events


class WebhookIngestor(EventIngestor):
    """
    Webhook ingestor

    Receives events via webhook POSTs.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(EventSource.WEBHOOK, config)
        self.pending_events: List[RawEvent] = []
        self.webhook_port = config.get("port", 8080)

    async def receive_webhook(self, data: Dict[str, Any]) -> None:
        """
        Receive webhook data

        Args:
            data: Webhook payload
        """
        event = RawEvent(
            source=EventSource.WEBHOOK,
            content=data.get("content", ""),
            url=data.get("url"),
            author=data.get("author"),
            timestamp=datetime.utcnow(),
            metadata=data.get("metadata", {})
        )

        self.pending_events.append(event)
        logger.info(f"Received webhook event: {event.content[:50]}...")

    async def fetch_events(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[RawEvent]:
        """Fetch pending webhook events"""
        events = self.pending_events.copy()
        self.pending_events.clear()

        if limit:
            events = events[:limit]

        return events


class IngestorFactory:
    """Factory for creating event ingestors"""

    @staticmethod
    def create(source: EventSource, config: Dict[str, Any]) -> EventIngestor:
        """Create ingestor for source"""
        ingestors = {
            EventSource.TWITTER: TwitterIngestor,
            EventSource.NEWS_API: NewsAPIIngestor,
            EventSource.RSS: RSSIngestor,
            EventSource.WEBHOOK: WebhookIngestor,
        }

        ingestor_class = ingestors.get(source)
        if not ingestor_class:
            raise ValueError(f"No ingestor for source: {source}")

        return ingestor_class(config)

    @staticmethod
    def create_twitter(
        api_key: str,
        keywords: List[str],
        **kwargs
    ) -> TwitterIngestor:
        """Create Twitter ingestor"""
        config = {
            "api_key": api_key,
            "keywords": keywords,
            **kwargs
        }
        return TwitterIngestor(config)

    @staticmethod
    def create_news_api(
        api_key: str,
        sources: Optional[List[str]] = None,
        **kwargs
    ) -> NewsAPIIngestor:
        """Create News API ingestor"""
        config = {
            "api_key": api_key,
            "sources": sources or [],
            **kwargs
        }
        return NewsAPIIngestor(config)

    @staticmethod
    def create_rss(
        feed_urls: List[str],
        **kwargs
    ) -> RSSIngestor:
        """Create RSS ingestor"""
        config = {
            "feed_urls": feed_urls,
            **kwargs
        }
        return RSSIngestor(config)

    @staticmethod
    def create_webhook(
        port: int = 8080,
        **kwargs
    ) -> WebhookIngestor:
        """Create webhook ingestor"""
        config = {
            "port": port,
            **kwargs
        }
        return WebhookIngestor(config)
