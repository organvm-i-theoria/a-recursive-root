"""
Avatar Cache System

Caches generated avatars to avoid regenerating the same avatar multiple times.
"""

import asyncio
import hashlib
import json
import os
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, List
import logging

from .generator import GeneratedAvatar, AvatarProvider, AvatarSize

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry metadata"""
    personality: str
    provider: str
    size: str
    prompt_hash: str
    filepath: str
    created_at: float
    last_accessed: float
    access_count: int
    file_size: int  # bytes

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'CacheEntry':
        """Create from dictionary"""
        return cls(**data)


class AvatarCache:
    """
    Cache manager for generated avatars

    Features:
    - Persistent file-based cache
    - LRU eviction policy
    - Automatic cache size management
    - Metadata tracking
    """

    def __init__(
        self,
        cache_dir: str = "./avatar_cache",
        max_size_mb: int = 500,
        max_age_days: int = 30,
        enable_compression: bool = False,
    ):
        """
        Initialize avatar cache

        Args:
            cache_dir: Directory for cache storage
            max_size_mb: Maximum cache size in megabytes
            max_age_days: Maximum age of cached items in days
            enable_compression: Enable image compression (future feature)
        """
        self.cache_dir = Path(cache_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_age_seconds = max_age_days * 24 * 3600
        self.enable_compression = enable_compression

        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Metadata file
        self.metadata_file = self.cache_dir / "cache_metadata.json"

        # In-memory metadata
        self.metadata: Dict[str, CacheEntry] = {}

        # Load existing cache
        self._load_metadata()

        logger.info(f"Avatar cache initialized at {self.cache_dir}")
        logger.info(f"Cache entries: {len(self.metadata)}")

    def _load_metadata(self):
        """Load cache metadata from disk"""
        if not self.metadata_file.exists():
            logger.info("No existing cache metadata found")
            return

        try:
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)

            self.metadata = {
                key: CacheEntry.from_dict(entry)
                for key, entry in data.items()
            }

            # Verify files exist
            missing_files = []
            for key, entry in self.metadata.items():
                if not Path(entry.filepath).exists():
                    missing_files.append(key)

            # Remove missing files from metadata
            for key in missing_files:
                del self.metadata[key]

            if missing_files:
                logger.warning(f"Removed {len(missing_files)} cache entries with missing files")
                self._save_metadata()

        except Exception as e:
            logger.error(f"Error loading cache metadata: {e}")
            self.metadata = {}

    def _save_metadata(self):
        """Save cache metadata to disk"""
        try:
            data = {key: entry.to_dict() for key, entry in self.metadata.items()}

            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving cache metadata: {e}")

    def _generate_cache_key(
        self,
        personality: str,
        provider: AvatarProvider,
        size: AvatarSize,
        prompt: str
    ) -> str:
        """Generate unique cache key"""
        # Create hash of relevant parameters
        key_data = f"{personality}_{provider.value}_{size.value}_{prompt}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _generate_filepath(self, cache_key: str) -> str:
        """Generate filepath for cache key"""
        return str(self.cache_dir / f"{cache_key}.png")

    async def get(
        self,
        personality: str,
        provider: AvatarProvider,
        size: AvatarSize,
        prompt: str
    ) -> Optional[GeneratedAvatar]:
        """
        Get avatar from cache

        Args:
            personality: Personality name
            provider: Avatar provider
            size: Avatar size
            prompt: Generation prompt

        Returns:
            GeneratedAvatar if cached, None otherwise
        """
        cache_key = self._generate_cache_key(personality, provider, size, prompt)

        if cache_key not in self.metadata:
            logger.debug(f"Cache miss for {personality}")
            return None

        entry = self.metadata[cache_key]

        # Check if file exists
        if not Path(entry.filepath).exists():
            logger.warning(f"Cache file missing: {entry.filepath}")
            del self.metadata[cache_key]
            self._save_metadata()
            return None

        # Check age
        age = time.time() - entry.created_at
        if age > self.max_age_seconds:
            logger.info(f"Cache entry expired: {personality}")
            await self.delete(cache_key)
            return None

        # Load avatar
        try:
            with open(entry.filepath, 'rb') as f:
                image_data = f.read()

            # Update access stats
            entry.last_accessed = time.time()
            entry.access_count += 1
            self._save_metadata()

            logger.debug(f"Cache hit for {personality}")

            return GeneratedAvatar(
                personality=personality,
                image_data=image_data,
                prompt=prompt,
                provider=provider,
                size=size,
                metadata=entry.to_dict()
            )

        except Exception as e:
            logger.error(f"Error loading cached avatar: {e}")
            return None

    async def put(
        self,
        avatar: GeneratedAvatar,
        prompt: str
    ):
        """
        Store avatar in cache

        Args:
            avatar: Generated avatar to cache
            prompt: Generation prompt used
        """
        cache_key = self._generate_cache_key(
            avatar.personality,
            avatar.provider,
            avatar.size,
            prompt
        )

        filepath = self._generate_filepath(cache_key)

        try:
            # Save avatar file
            with open(filepath, 'wb') as f:
                f.write(avatar.image_data)

            # Create cache entry
            entry = CacheEntry(
                personality=avatar.personality,
                provider=avatar.provider.value,
                size=avatar.size.value,
                prompt_hash=hashlib.md5(prompt.encode()).hexdigest(),
                filepath=filepath,
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                file_size=len(avatar.image_data)
            )

            self.metadata[cache_key] = entry
            self._save_metadata()

            logger.info(f"Cached avatar for {avatar.personality}")

            # Check cache size and evict if needed
            await self._evict_if_needed()

        except Exception as e:
            logger.error(f"Error caching avatar: {e}")

    async def delete(self, cache_key: str):
        """Delete cache entry"""
        if cache_key not in self.metadata:
            return

        entry = self.metadata[cache_key]

        # Delete file
        try:
            Path(entry.filepath).unlink(missing_ok=True)
        except Exception as e:
            logger.error(f"Error deleting cache file: {e}")

        # Remove from metadata
        del self.metadata[cache_key]
        self._save_metadata()

        logger.debug(f"Deleted cache entry: {cache_key}")

    async def _evict_if_needed(self):
        """Evict old entries if cache is too large"""
        total_size = sum(entry.file_size for entry in self.metadata.values())

        if total_size <= self.max_size_bytes:
            return

        logger.info(f"Cache size ({total_size / 1024 / 1024:.1f}MB) exceeds limit, evicting...")

        # Sort by LRU (least recently used)
        entries = sorted(
            self.metadata.items(),
            key=lambda x: x[1].last_accessed
        )

        # Evict until under limit
        for cache_key, entry in entries:
            if total_size <= self.max_size_bytes:
                break

            await self.delete(cache_key)
            total_size -= entry.file_size
            logger.info(f"Evicted {entry.personality}")

    async def clear(self):
        """Clear all cached avatars"""
        for cache_key in list(self.metadata.keys()):
            await self.delete(cache_key)

        logger.info("Cache cleared")

    async def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_size = sum(entry.file_size for entry in self.metadata.values())
        total_accesses = sum(entry.access_count for entry in self.metadata.values())

        oldest_entry = None
        if self.metadata:
            oldest_entry = min(self.metadata.values(), key=lambda x: x.created_at)

        return {
            "total_entries": len(self.metadata),
            "total_size_mb": total_size / 1024 / 1024,
            "max_size_mb": self.max_size_bytes / 1024 / 1024,
            "utilization": total_size / self.max_size_bytes if self.max_size_bytes > 0 else 0,
            "total_accesses": total_accesses,
            "avg_accesses": total_accesses / len(self.metadata) if self.metadata else 0,
            "oldest_entry_age_days": (time.time() - oldest_entry.created_at) / 86400 if oldest_entry else 0,
        }

    async def list_entries(self, personality: Optional[str] = None) -> List[CacheEntry]:
        """
        List cache entries

        Args:
            personality: Filter by personality (optional)

        Returns:
            List of cache entries
        """
        entries = list(self.metadata.values())

        if personality:
            entries = [e for e in entries if e.personality.lower() == personality.lower()]

        return sorted(entries, key=lambda x: x.last_accessed, reverse=True)

    async def cleanup_old_entries(self):
        """Remove entries older than max_age"""
        current_time = time.time()
        old_entries = []

        for cache_key, entry in self.metadata.items():
            age = current_time - entry.created_at
            if age > self.max_age_seconds:
                old_entries.append(cache_key)

        for cache_key in old_entries:
            await self.delete(cache_key)

        if old_entries:
            logger.info(f"Cleaned up {len(old_entries)} old cache entries")

        return len(old_entries)


# Singleton cache instance
_cache_instance: Optional[AvatarCache] = None


def get_cache(
    cache_dir: str = "./avatar_cache",
    **kwargs
) -> AvatarCache:
    """Get or create global cache instance"""
    global _cache_instance

    if _cache_instance is None:
        _cache_instance = AvatarCache(cache_dir=cache_dir, **kwargs)

    return _cache_instance


async def cleanup_cache():
    """Cleanup old cache entries (utility function)"""
    cache = get_cache()
    return await cache.cleanup_old_entries()
