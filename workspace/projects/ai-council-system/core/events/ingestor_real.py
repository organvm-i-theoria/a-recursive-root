"""
Real Event Ingestors - Production implementations with actual API calls

Requires appropriate API keys and libraries installed.
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

from .event import RawEvent, EventSource
from .ingestor import EventIngestor

logger = logging.getLogger(__name__)


class RealTwitterIngestor(EventIngestor):
    """
    Real Twitter/X API ingestor

    Requires: pip install tweepy
    Requires: Twitter API v2 keys (Bearer token or OAuth)
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(EventSource.TWITTER, config)
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Twitter client"""
        try:
            import tweepy

            # Check for API keys
            api_key = self.config.get("api_key")
            bearer_token = self.config.get("bearer_token")

            if bearer_token:
                # Use Bearer token (simpler, recommended for v2)
                self.client = tweepy.Client(
                    bearer_token=bearer_token,
                    wait_on_rate_limit=True
                )
            elif api_key:
                # Use OAuth 1.0a
                api_secret = self.config.get("api_secret")
                access_token = self.config.get("access_token")
                access_secret = self.config.get("access_secret")

                if not all([api_secret, access_token, access_secret]):
                    raise ValueError(
                        "OAuth 1.0a requires: api_key, api_secret, "
                        "access_token, access_secret"
                    )

                self.client = tweepy.Client(
                    consumer_key=api_key,
                    consumer_secret=api_secret,
                    access_token=access_token,
                    access_token_secret=access_secret,
                    wait_on_rate_limit=True
                )
            else:
                raise ValueError("Twitter API key or bearer token required")

            logger.info("Twitter client initialized successfully")

        except ImportError:
            logger.error(
                "tweepy library not installed. "
                "Install with: pip install tweepy"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {e}")
            raise

    async def fetch_events(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[RawEvent]:
        """Fetch tweets from Twitter API"""
        if not self.client:
            raise RuntimeError("Twitter client not initialized")

        logger.debug(f"Fetching tweets (keywords: {self.keywords})")

        events = []
        limit = limit or 10

        try:
            # Build query from keywords
            keywords = self.config.get("keywords", [])
            hashtags = self.config.get("hashtags", [])

            if not keywords and not hashtags:
                logger.warning("No keywords or hashtags configured")
                return events

            # Combine into query
            query_parts = []
            if keywords:
                query_parts.extend(keywords)
            if hashtags:
                query_parts.extend(hashtags)

            query = " OR ".join(query_parts)

            # Calculate start time
            start_time = since or (datetime.utcnow() - timedelta(hours=1))

            # Search recent tweets
            response = self.client.search_recent_tweets(
                query=query,
                max_results=min(limit, 100),  # API limit is 100
                start_time=start_time.isoformat() + "Z",
                tweet_fields=["created_at", "author_id", "public_metrics", "entities"],
                expansions=["author_id"],
                user_fields=["username"]
            )

            if not response.data:
                logger.debug("No tweets found")
                return events

            # Create user lookup
            users = {}
            if response.includes and "users" in response.includes:
                users = {u.id: u.username for u in response.includes["users"]}

            # Process tweets
            for tweet in response.data:
                author = users.get(tweet.author_id, "unknown")
                metrics = tweet.public_metrics or {}

                event = RawEvent(
                    source=EventSource.TWITTER,
                    content=tweet.text,
                    url=f"https://twitter.com/{author}/status/{tweet.id}",
                    author=f"@{author}",
                    timestamp=tweet.created_at,
                    metadata={
                        "tweet_id": str(tweet.id),
                        "likes": metrics.get("like_count", 0),
                        "retweets": metrics.get("retweet_count", 0),
                        "replies": metrics.get("reply_count", 0),
                        "hashtags": [
                            tag["tag"]
                            for tag in (tweet.entities or {}).get("hashtags", [])
                        ] if tweet.entities else [],
                    }
                )
                events.append(event)

            logger.info(f"Fetched {len(events)} tweets from Twitter")

        except Exception as e:
            logger.error(f"Error fetching tweets: {e}")
            # Don't raise - allow partial failures

        return events


class RealNewsAPIIngestor(EventIngestor):
    """
    Real News API ingestor

    Requires: pip install newsapi-python
    Requires: News API key from newsapi.org
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(EventSource.NEWS_API, config)
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize News API client"""
        try:
            from newsapi import NewsApiClient

            api_key = self.config.get("api_key")
            if not api_key:
                raise ValueError("News API key required")

            self.client = NewsApiClient(api_key=api_key)
            logger.info("News API client initialized successfully")

        except ImportError:
            logger.error(
                "newsapi-python library not installed. "
                "Install with: pip install newsapi-python"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to initialize News API client: {e}")
            raise

    async def fetch_events(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[RawEvent]:
        """Fetch news articles from News API"""
        if not self.client:
            raise RuntimeError("News API client not initialized")

        logger.debug(f"Fetching news articles (sources: {self.sources})")

        events = []
        limit = limit or 10

        try:
            # Get config
            sources = self.config.get("sources", [])
            categories = self.config.get("categories", [])
            keywords = self.config.get("keywords", [])

            # Calculate date range
            since = since or (datetime.utcnow() - timedelta(days=1))
            from_date = since.strftime("%Y-%m-%d")

            # Fetch articles
            # Note: News API is synchronous, we'll run in executor
            loop = asyncio.get_event_loop()

            if keywords:
                # Search by keywords
                query = " OR ".join(keywords)
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.get_everything(
                        q=query,
                        sources=",".join(sources) if sources else None,
                        from_param=from_date,
                        language="en",
                        sort_by="relevancy",
                        page_size=limit
                    )
                )
            elif sources:
                # Get top headlines from sources
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.get_top_headlines(
                        sources=",".join(sources),
                        page_size=limit
                    )
                )
            elif categories:
                # Get top headlines by category
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.get_top_headlines(
                        category=categories[0],  # API accepts one category
                        language="en",
                        page_size=limit
                    )
                )
            else:
                logger.warning("No search criteria configured")
                return events

            # Process articles
            if response["status"] == "ok" and response["articles"]:
                for article in response["articles"][:limit]:
                    # Parse published date
                    published = article.get("publishedAt")
                    if published:
                        try:
                            published = datetime.fromisoformat(
                                published.replace("Z", "+00:00")
                            )
                        except:
                            published = datetime.utcnow()
                    else:
                        published = datetime.utcnow()

                    # Combine title and description
                    title = article.get("title", "")
                    description = article.get("description", "")
                    content = f"{title}. {description}" if description else title

                    event = RawEvent(
                        source=EventSource.NEWS_API,
                        content=content,
                        url=article.get("url"),
                        author=article.get("author"),
                        timestamp=published,
                        metadata={
                            "source_name": article.get("source", {}).get("name"),
                            "title": title,
                            "image_url": article.get("urlToImage"),
                        }
                    )
                    events.append(event)

                logger.info(f"Fetched {len(events)} articles from News API")

        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            # Don't raise - allow partial failures

        return events


class RealRSSIngestor(EventIngestor):
    """
    Real RSS feed ingestor

    Requires: pip install feedparser
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(EventSource.RSS, config)
        self.feed_urls = config.get("feed_urls", [])

    async def fetch_events(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[RawEvent]:
        """Fetch items from RSS feeds"""
        try:
            import feedparser
        except ImportError:
            logger.error(
                "feedparser library not installed. "
                "Install with: pip install feedparser"
            )
            return []

        logger.debug(f"Fetching from {len(self.feed_urls)} RSS feeds")

        events = []
        limit = limit or 10
        since = since or (datetime.utcnow() - timedelta(days=1))

        for feed_url in self.feed_urls:
            try:
                # Parse feed (synchronous)
                loop = asyncio.get_event_loop()
                feed = await loop.run_in_executor(
                    None,
                    feedparser.parse,
                    feed_url
                )

                # Process entries
                for entry in feed.entries[:limit]:
                    # Parse published date
                    published = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        try:
                            import time
                            published = datetime.fromtimestamp(
                                time.mktime(entry.published_parsed)
                            )
                        except:
                            pass

                    if not published:
                        published = datetime.utcnow()

                    # Skip if too old
                    if published < since:
                        continue

                    # Get content
                    title = entry.get("title", "")
                    summary = entry.get("summary", "")
                    content = f"{title}. {summary}" if summary else title

                    event = RawEvent(
                        source=EventSource.RSS,
                        content=content,
                        url=entry.get("link"),
                        author=entry.get("author"),
                        timestamp=published,
                        metadata={
                            "feed_url": feed_url,
                            "feed_title": feed.feed.get("title", ""),
                        }
                    )
                    events.append(event)

                logger.debug(f"Fetched {len(events)} items from {feed_url}")

            except Exception as e:
                logger.error(f"Error fetching RSS feed {feed_url}: {e}")
                continue

        logger.info(f"Fetched {len(events)} total items from RSS feeds")
        return events


# Factory functions
def create_real_twitter(config: Dict[str, Any]) -> RealTwitterIngestor:
    """Create real Twitter ingestor"""
    return RealTwitterIngestor(config)


def create_real_news_api(config: Dict[str, Any]) -> RealNewsAPIIngestor:
    """Create real News API ingestor"""
    return RealNewsAPIIngestor(config)


def create_real_rss(config: Dict[str, Any]) -> RealRSSIngestor:
    """Create real RSS ingestor"""
    return RealRSSIngestor(config)
