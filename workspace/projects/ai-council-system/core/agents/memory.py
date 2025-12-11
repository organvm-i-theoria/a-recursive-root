"""
Memory Manager - Agent memory and context management

Provides short-term and long-term memory for AI agents with
semantic search and retrieval capabilities.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class Memory:
    """Represents a single memory entry"""
    memory_id: str
    content: str
    memory_type: str  # "conversation", "event", "fact", "experience"
    importance: float  # 0.0-1.0
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None  # For semantic search
    access_count: int = 0
    last_accessed: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "memory_type": self.memory_type,
            "importance": self.importance,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
        }


class MemoryManager:
    """
    Manages agent memory with short-term and long-term storage

    Provides semantic search, importance-based retention, and
    memory consolidation.
    """

    def __init__(
        self,
        agent_id: str,
        short_term_capacity: int = 100,
        long_term_capacity: int = 10000,
        consolidation_threshold: float = 0.6
    ):
        self.agent_id = agent_id
        self.short_term_capacity = short_term_capacity
        self.long_term_capacity = long_term_capacity
        self.consolidation_threshold = consolidation_threshold

        # Short-term memory (recent events, working memory)
        self.short_term: deque = deque(maxlen=short_term_capacity)

        # Long-term memory (important events, consolidated knowledge)
        self.long_term: List[Memory] = []

        # Memory index for fast retrieval
        self.memory_index: Dict[str, Memory] = {}

        # Statistics
        self.total_stored = 0
        self.total_retrieved = 0
        self.consolidation_count = 0

    async def initialize(self) -> None:
        """Initialize memory manager"""
        logger.info(f"Initializing memory manager for agent {self.agent_id}")
        # Could load persisted memories here

    async def store(
        self,
        content: str,
        memory_type: str = "conversation",
        importance: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Memory:
        """
        Store new memory

        Args:
            content: Memory content
            memory_type: Type of memory
            importance: Importance score (calculated if not provided)
            metadata: Additional metadata

        Returns:
            Created Memory object
        """
        # Calculate importance if not provided
        if importance is None:
            importance = await self._calculate_importance(content, memory_type)

        # Create memory entry
        memory_id = f"{self.agent_id}_{self.total_stored}"
        memory = Memory(
            memory_id=memory_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )

        # Generate embedding for semantic search (placeholder)
        # In production, would use actual embedding model
        memory.embedding = await self._generate_embedding(content)

        # Add to short-term memory
        self.short_term.append(memory)
        self.memory_index[memory_id] = memory
        self.total_stored += 1

        logger.debug(
            f"Stored memory {memory_id}: {content[:50]}... "
            f"(importance: {importance:.2f})"
        )

        # Check if consolidation is needed
        if len(self.short_term) >= self.short_term_capacity * 0.8:
            await self._consolidate_memories()

        return memory

    async def retrieve_relevant(
        self,
        query: str,
        limit: int = 5,
        min_importance: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories for a query

        Args:
            query: Query text
            limit: Maximum number of memories to return
            min_importance: Minimum importance threshold

        Returns:
            List of relevant memories
        """
        self.total_retrieved += 1

        # Generate query embedding
        query_embedding = await self._generate_embedding(query)

        # Search all memories
        all_memories = list(self.short_term) + self.long_term
        scored_memories = []

        for memory in all_memories:
            if memory.importance < min_importance:
                continue

            # Calculate relevance score
            relevance = await self._calculate_relevance(
                query_embedding,
                memory.embedding,
                memory
            )

            scored_memories.append((memory, relevance))

        # Sort by relevance and recency
        scored_memories.sort(
            key=lambda x: (x[1], x[0].timestamp),
            reverse=True
        )

        # Update access statistics
        results = []
        for memory, relevance in scored_memories[:limit]:
            memory.access_count += 1
            memory.last_accessed = datetime.utcnow()

            results.append({
                "content": memory.content,
                "type": memory.memory_type,
                "importance": memory.importance,
                "relevance": relevance,
                "timestamp": memory.timestamp.isoformat(),
                "metadata": memory.metadata,
            })

        logger.debug(f"Retrieved {len(results)} relevant memories for query")
        return results

    async def retrieve_recent(
        self,
        limit: int = 10,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve most recent memories"""
        memories = list(self.short_term)

        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]

        # Sort by timestamp descending
        memories.sort(key=lambda m: m.timestamp, reverse=True)

        return [
            {
                "content": m.content,
                "type": m.memory_type,
                "importance": m.importance,
                "timestamp": m.timestamp.isoformat(),
            }
            for m in memories[:limit]
        ]

    async def retrieve_important(
        self,
        limit: int = 10,
        min_importance: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Retrieve most important memories"""
        all_memories = list(self.short_term) + self.long_term

        important = [
            m for m in all_memories
            if m.importance >= min_importance
        ]

        important.sort(key=lambda m: m.importance, reverse=True)

        return [
            {
                "content": m.content,
                "type": m.memory_type,
                "importance": m.importance,
                "timestamp": m.timestamp.isoformat(),
            }
            for m in important[:limit]
        ]

    async def _consolidate_memories(self) -> None:
        """
        Consolidate short-term memories into long-term storage

        Moves important memories from short-term to long-term storage
        and prunes less important ones.
        """
        logger.debug("Consolidating memories...")

        # Get consolidation candidates (important or frequently accessed)
        candidates = []
        for memory in self.short_term:
            if (
                memory.importance >= self.consolidation_threshold
                or memory.access_count >= 3
            ):
                candidates.append(memory)

        # Move to long-term storage
        for memory in candidates:
            if memory not in self.long_term:
                self.long_term.append(memory)

        # Sort long-term by importance
        self.long_term.sort(key=lambda m: m.importance, reverse=True)

        # Prune if over capacity
        if len(self.long_term) > self.long_term_capacity:
            self.long_term = self.long_term[:self.long_term_capacity]

        self.consolidation_count += 1
        logger.info(
            f"Consolidated {len(candidates)} memories to long-term storage. "
            f"Total long-term: {len(self.long_term)}"
        )

    async def _calculate_importance(
        self,
        content: str,
        memory_type: str
    ) -> float:
        """Calculate importance score for memory"""
        # Simplified importance calculation
        # Production would use more sophisticated methods

        base_importance = {
            "conversation": 0.5,
            "event": 0.6,
            "fact": 0.7,
            "experience": 0.6,
        }.get(memory_type, 0.5)

        # Adjust based on content
        if len(content) > 200:  # Longer content might be more important
            base_importance += 0.1

        # Keywords that indicate importance
        important_keywords = ["important", "critical", "key", "significant", "vote"]
        for keyword in important_keywords:
            if keyword.lower() in content.lower():
                base_importance += 0.1
                break

        return min(1.0, base_importance)

    async def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for semantic search

        Placeholder implementation. Production would use:
        - OpenAI embeddings
        - Sentence transformers
        - Custom embedding model
        """
        # Mock embedding - just hash-based for now
        # In production: use actual embedding model
        import hashlib
        hash_bytes = hashlib.md5(text.encode()).digest()
        embedding = [float(b) / 255.0 for b in hash_bytes[:16]]
        return embedding

    async def _calculate_relevance(
        self,
        query_embedding: List[float],
        memory_embedding: List[float],
        memory: Memory
    ) -> float:
        """
        Calculate relevance score between query and memory

        Uses cosine similarity of embeddings plus recency and importance
        """
        # Cosine similarity (simplified)
        if not query_embedding or not memory_embedding:
            similarity = 0.5
        else:
            dot_product = sum(a * b for a, b in zip(query_embedding, memory_embedding))
            magnitude_q = sum(a * a for a in query_embedding) ** 0.5
            magnitude_m = sum(b * b for b in memory_embedding) ** 0.5

            if magnitude_q > 0 and magnitude_m > 0:
                similarity = dot_product / (magnitude_q * magnitude_m)
            else:
                similarity = 0.0

        # Adjust for recency (newer memories get slight boost)
        age = (datetime.utcnow() - memory.timestamp).total_seconds() / 3600  # hours
        recency_factor = max(0.0, 1.0 - (age / 168))  # Decay over a week

        # Combine similarity, importance, and recency
        relevance = (
            similarity * 0.6 +
            memory.importance * 0.3 +
            recency_factor * 0.1
        )

        return relevance

    async def clear_short_term(self) -> None:
        """Clear short-term memory"""
        self.short_term.clear()
        logger.info("Cleared short-term memory")

    async def clear_all(self) -> None:
        """Clear all memories"""
        self.short_term.clear()
        self.long_term.clear()
        self.memory_index.clear()
        logger.warning("Cleared all memories")

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "agent_id": self.agent_id,
            "short_term_count": len(self.short_term),
            "long_term_count": len(self.long_term),
            "total_stored": self.total_stored,
            "total_retrieved": self.total_retrieved,
            "consolidation_count": self.consolidation_count,
        }

    async def close(self) -> None:
        """Close memory manager and persist state"""
        logger.info(
            f"Closing memory manager. Stats: {self.get_stats()}"
        )
        # Could persist memories to disk/database here
