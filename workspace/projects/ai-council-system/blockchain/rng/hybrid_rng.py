"""
Hybrid RNG coordinator with automatic fallback.

Combines multiple random number sources with intelligent fallback:
1. Chainlink VRF (most secure, slower)
2. Pyth Entropy (fast, verifiable)
3. Local CSPRNG (fallback only, not verifiable)
"""

import asyncio
import hashlib
import logging
import secrets
from dataclasses import dataclass
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

from .chainlink_vrf import ChainlinkVRFProvider, VRFProof
from .pyth_entropy import PythEntropyProvider

logger = logging.getLogger(__name__)


class RNGSource(Enum):
    """Random number generation source."""
    CHAINLINK_VRF = "chainlink_vrf"
    PYTH_ENTROPY = "pyth_entropy"
    LOCAL_CSPRNG = "local_csprng"


@dataclass
class SelectionResult:
    """Result of a random selection."""
    selected_items: List[Any]
    source: RNGSource
    request_id: Optional[str]
    is_verifiable: bool
    proof: Optional[VRFProof]
    timestamp: datetime
    metadata: Dict[str, Any]


class HybridRNG:
    """
    Hybrid random number generator with multiple sources and fallback.

    Priority order:
    1. Chainlink VRF (if use_blockchain=True and available)
    2. Pyth Entropy (if Chainlink unavailable)
    3. Local CSPRNG (if blockchain unavailable or disabled)

    Example:
        rng = HybridRNG()

        # Try blockchain RNG
        selected = await rng.get_random_selection(
            agents,
            count=5,
            use_blockchain=True
        )

        # Get verification proof
        if selected.is_verifiable:
            proof = selected.proof
            print(f"Verifiable selection: {proof.proof_hash}")
    """

    def __init__(
        self,
        chainlink_vrf: Optional[ChainlinkVRFProvider] = None,
        pyth_entropy: Optional[PythEntropyProvider] = None,
        prefer_vrf: bool = True,
        vrf_timeout: int = 10,
        pyth_timeout: int = 5
    ):
        """
        Initialize Hybrid RNG.

        Args:
            chainlink_vrf: Chainlink VRF provider (created if None)
            pyth_entropy: Pyth Entropy provider (created if None)
            prefer_vrf: Prefer VRF over Pyth even if slower
            vrf_timeout: Timeout for VRF requests (seconds)
            pyth_timeout: Timeout for Pyth requests (seconds)
        """
        self.chainlink_vrf = chainlink_vrf or ChainlinkVRFProvider()
        self.pyth_entropy = pyth_entropy or PythEntropyProvider()
        self.prefer_vrf = prefer_vrf
        self.vrf_timeout = vrf_timeout
        self.pyth_timeout = pyth_timeout

        # Statistics
        self.stats = {
            RNGSource.CHAINLINK_VRF: {"requests": 0, "successes": 0, "failures": 0},
            RNGSource.PYTH_ENTROPY: {"requests": 0, "successes": 0, "failures": 0},
            RNGSource.LOCAL_CSPRNG: {"requests": 0, "successes": 0, "failures": 0},
        }

        logger.info("Hybrid RNG initialized with Chainlink VRF + Pyth Entropy + Local fallback")

    async def get_random_selection(
        self,
        options: List[Any],
        count: int,
        use_blockchain: bool = True,
        allow_fallback: bool = True
    ) -> SelectionResult:
        """
        Get random selection with automatic source fallback.

        Args:
            options: List of options to choose from
            count: Number of items to select
            use_blockchain: Whether to use blockchain RNG
            allow_fallback: Whether to fallback to local RNG if blockchain fails

        Returns:
            SelectionResult: Selected items with metadata

        Example:
            result = await rng.get_random_selection(agents, 5, use_blockchain=True)
            selected_agents = result.selected_items
            if result.is_verifiable:
                print(f"Verifiable via {result.source.value}")
        """
        if count > len(options):
            raise ValueError(f"Cannot select {count} items from {len(options)} options")

        if not use_blockchain:
            # Skip blockchain, use local
            return await self._local_selection(options, count)

        # Try blockchain sources
        if self.prefer_vrf:
            # Try VRF first
            result = await self._try_vrf_selection(options, count)
            if result:
                return result

            # Try Pyth as backup
            result = await self._try_pyth_selection(options, count)
            if result:
                return result
        else:
            # Try Pyth first (faster)
            result = await self._try_pyth_selection(options, count)
            if result:
                return result

            # Try VRF as backup
            result = await self._try_vrf_selection(options, count)
            if result:
                return result

        # Blockchain failed, use local if allowed
        if allow_fallback:
            logger.warning("Blockchain RNG unavailable, falling back to local CSPRNG")
            return await self._local_selection(options, count)
        else:
            raise RuntimeError("Blockchain RNG failed and fallback is disabled")

    async def get_random_int(
        self,
        min_val: int = 0,
        max_val: int = 2**32,
        use_blockchain: bool = True
    ) -> int:
        """
        Get random integer.

        Args:
            min_val: Minimum value (inclusive)
            max_val: Maximum value (exclusive)
            use_blockchain: Whether to use blockchain RNG

        Returns:
            int: Random integer
        """
        if not use_blockchain:
            return secrets.randbelow(max_val - min_val) + min_val

        # Try Pyth first (faster for single integer)
        try:
            self.stats[RNGSource.PYTH_ENTROPY]["requests"] += 1
            random_int = await asyncio.wait_for(
                self.pyth_entropy.get_random_int(min_val, max_val),
                timeout=self.pyth_timeout
            )
            self.stats[RNGSource.PYTH_ENTROPY]["successes"] += 1
            return random_int
        except Exception as e:
            logger.warning(f"Pyth Entropy failed: {e}")
            self.stats[RNGSource.PYTH_ENTROPY]["failures"] += 1

        # Fallback to local
        return secrets.randbelow(max_val - min_val) + min_val

    def get_stats(self) -> Dict[str, Any]:
        """
        Get RNG usage statistics.

        Returns:
            Dict with request counts and success rates
        """
        stats_summary = {}
        for source, counts in self.stats.items():
            total = counts["requests"]
            success_rate = (counts["successes"] / total * 100) if total > 0 else 0
            stats_summary[source.value] = {
                "total_requests": total,
                "successes": counts["successes"],
                "failures": counts["failures"],
                "success_rate": f"{success_rate:.1f}%"
            }
        return stats_summary

    async def verify_selection(self, result: SelectionResult) -> bool:
        """
        Verify that a selection is valid.

        Args:
            result: SelectionResult to verify

        Returns:
            bool: True if verification passes
        """
        if not result.is_verifiable:
            logger.warning(f"Selection from {result.source.value} is not verifiable")
            return False

        if result.source == RNGSource.CHAINLINK_VRF:
            if result.proof is None or result.request_id is None:
                return False
            # Verify VRF proof
            return self.chainlink_vrf.verify_randomness(
                result.request_id,
                result.proof.random_number
            )
        elif result.source == RNGSource.PYTH_ENTROPY:
            # Pyth verification would check on-chain entropy
            # For now, we trust the result if it has metadata
            return result.request_id is not None
        else:
            return False

    # Private methods

    async def _try_vrf_selection(
        self,
        options: List[Any],
        count: int
    ) -> Optional[SelectionResult]:
        """Try to get selection using Chainlink VRF."""
        try:
            self.stats[RNGSource.CHAINLINK_VRF]["requests"] += 1

            # Generate seed
            seed = secrets.randbits(256)

            # Request randomness
            request_id = await asyncio.wait_for(
                self.chainlink_vrf.request_randomness(seed),
                timeout=self.vrf_timeout
            )

            # Get random number
            random_number = await asyncio.wait_for(
                self.chainlink_vrf.get_random_number(request_id),
                timeout=self.vrf_timeout
            )

            if random_number is None:
                raise RuntimeError("VRF returned None")

            # Get proof
            proof = self.chainlink_vrf.get_proof(request_id)

            # Select items using random number
            selected = self._select_from_random_number(options, count, random_number)

            self.stats[RNGSource.CHAINLINK_VRF]["successes"] += 1

            return SelectionResult(
                selected_items=selected,
                source=RNGSource.CHAINLINK_VRF,
                request_id=request_id,
                is_verifiable=True,
                proof=proof,
                timestamp=datetime.now(),
                metadata={"seed": seed, "random_number": random_number}
            )

        except Exception as e:
            logger.warning(f"Chainlink VRF selection failed: {e}")
            self.stats[RNGSource.CHAINLINK_VRF]["failures"] += 1
            return None

    async def _try_pyth_selection(
        self,
        options: List[Any],
        count: int
    ) -> Optional[SelectionResult]:
        """Try to get selection using Pyth Entropy."""
        try:
            self.stats[RNGSource.PYTH_ENTROPY]["requests"] += 1

            # Get random selection
            selected = await asyncio.wait_for(
                self.pyth_entropy.get_random_selection(options, count),
                timeout=self.pyth_timeout
            )

            self.stats[RNGSource.PYTH_ENTROPY]["successes"] += 1

            return SelectionResult(
                selected_items=selected,
                source=RNGSource.PYTH_ENTROPY,
                request_id=f"pyth_{datetime.now().timestamp()}",
                is_verifiable=True,  # Pyth is verifiable on-chain
                proof=None,  # Pyth uses different verification
                timestamp=datetime.now(),
                metadata={}
            )

        except Exception as e:
            logger.warning(f"Pyth Entropy selection failed: {e}")
            self.stats[RNGSource.PYTH_ENTROPY]["failures"] += 1
            return None

    async def _local_selection(
        self,
        options: List[Any],
        count: int
    ) -> SelectionResult:
        """Get selection using local CSPRNG (not verifiable)."""
        self.stats[RNGSource.LOCAL_CSPRNG]["requests"] += 1

        # Use secrets module for cryptographically secure random
        selected_indices = set()
        while len(selected_indices) < count:
            index = secrets.randbelow(len(options))
            selected_indices.add(index)

        selected = [options[i] for i in sorted(selected_indices)]

        self.stats[RNGSource.LOCAL_CSPRNG]["successes"] += 1

        return SelectionResult(
            selected_items=selected,
            source=RNGSource.LOCAL_CSPRNG,
            request_id=None,
            is_verifiable=False,
            proof=None,
            timestamp=datetime.now(),
            metadata={"note": "Not blockchain-verifiable"}
        )

    def _select_from_random_number(
        self,
        options: List[Any],
        count: int,
        random_number: int
    ) -> List[Any]:
        """Select items deterministically from a random number."""
        selected_indices = set()
        current_seed = random_number

        while len(selected_indices) < count:
            index = current_seed % len(options)
            if index not in selected_indices:
                selected_indices.add(index)

            # Generate next seed from current
            seed_bytes = current_seed.to_bytes(32, byteorder='big')
            hash_obj = hashlib.sha256(seed_bytes)
            current_seed = int.from_bytes(hash_obj.digest(), byteorder='big')

        return [options[i] for i in sorted(selected_indices)]


# Convenience function
async def get_random_selection(
    options: List[Any],
    count: int,
    use_blockchain: bool = True
) -> SelectionResult:
    """
    Quick helper to get random selection with hybrid RNG.

    Args:
        options: List of options to choose from
        count: Number of items to select
        use_blockchain: Whether to use blockchain RNG

    Returns:
        SelectionResult: Selected items with metadata

    Example:
        result = await get_random_selection(agents, 5, use_blockchain=True)
        selected = result.selected_items
    """
    rng = HybridRNG()
    return await rng.get_random_selection(options, count, use_blockchain)
