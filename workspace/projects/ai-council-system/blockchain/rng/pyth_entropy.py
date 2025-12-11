"""
Pyth Entropy provider for high-frequency random number generation.

Provides fast, on-chain entropy using Pyth Network's entropy service.
Lower latency than Chainlink VRF but still verifiable on-chain.
"""

import asyncio
import hashlib
import logging
import os
from dataclasses import dataclass
from typing import List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class EntropyRequest:
    """Represents a Pyth Entropy request."""
    request_id: str
    timestamp: datetime
    sequence_number: int
    entropy_bytes: Optional[bytes] = None
    status: str = "pending"


class PythEntropyProvider:
    """
    Pyth Entropy provider for fast randomness.

    Features:
    - Lower latency than VRF (~1s vs 2-5s)
    - Still verifiable on-chain
    - Direct access to Solana Pyth program

    Example:
        pyth = PythEntropyProvider()
        random_bytes = await pyth.get_random_bytes(32)
        random_int = await pyth.get_random_int(0, 100)
    """

    def __init__(
        self,
        endpoint: Optional[str] = None,
        network: str = "devnet"
    ):
        """
        Initialize Pyth Entropy provider.

        Args:
            endpoint: Pyth Network endpoint
            network: Network to use (devnet, testnet, mainnet)
        """
        self.endpoint = endpoint or os.getenv('PYTH_NETWORK_ENDPOINT', 'https://xc-mainnet.pyth.network')
        self.network = network

        # Request tracking
        self._requests: dict[str, EntropyRequest] = {}
        self._sequence_number = 0

        # Mock mode for development
        self.mock_mode = os.getenv('PYTH_MOCK_MODE', 'true').lower() == 'true'

        if self.mock_mode:
            logger.warning("Pyth Entropy running in MOCK MODE (not using real blockchain)")
        else:
            logger.info(f"Pyth Entropy initialized on {network}")

    async def get_random_bytes(self, num_bytes: int = 32) -> bytes:
        """
        Get random bytes from Pyth Entropy.

        Args:
            num_bytes: Number of random bytes to generate

        Returns:
            bytes: Random bytes

        Example:
            random_bytes = await pyth.get_random_bytes(32)
        """
        request_id = self._generate_request_id()

        # Create request
        request = EntropyRequest(
            request_id=request_id,
            timestamp=datetime.now(),
            sequence_number=self._sequence_number
        )
        self._sequence_number += 1

        self._requests[request_id] = request

        if self.mock_mode:
            # Mock mode: generate deterministic random bytes
            entropy_bytes = await self._mock_get_entropy(num_bytes, request_id)
            request.entropy_bytes = entropy_bytes
            request.status = "fulfilled"
            logger.debug(f"Mock Pyth entropy generated: {len(entropy_bytes)} bytes")
        else:
            # Production: fetch from Pyth Network
            entropy_bytes = await self._fetch_entropy(num_bytes)
            request.entropy_bytes = entropy_bytes
            request.status = "fulfilled"
            logger.info(f"Pyth entropy fetched: {len(entropy_bytes)} bytes")

        return entropy_bytes

    async def get_random_int(self, min_val: int = 0, max_val: int = 2**32) -> int:
        """
        Get random integer in range.

        Args:
            min_val: Minimum value (inclusive)
            max_val: Maximum value (exclusive)

        Returns:
            int: Random integer in [min_val, max_val)

        Example:
            random_num = await pyth.get_random_int(0, 100)
        """
        # Get random bytes
        random_bytes = await self.get_random_bytes(32)

        # Convert to integer
        random_int = int.from_bytes(random_bytes[:8], byteorder='big')

        # Scale to range
        range_size = max_val - min_val
        scaled_value = (random_int % range_size) + min_val

        return scaled_value

    async def get_random_selection(
        self,
        options: List[Any],
        count: int
    ) -> List[Any]:
        """
        Select random items from options.

        Args:
            options: List of options to choose from
            count: Number of items to select

        Returns:
            List[Any]: Randomly selected items

        Example:
            selected = await pyth.get_random_selection(agents, 5)
        """
        if count > len(options):
            raise ValueError(f"Cannot select {count} items from {len(options)} options")

        # Get random bytes for selection
        num_bytes_needed = count * 8  # 8 bytes per selection
        random_bytes = await self.get_random_bytes(num_bytes_needed)

        # Select indices
        selected_indices = set()
        byte_offset = 0

        while len(selected_indices) < count:
            # Get next random number
            random_int = int.from_bytes(
                random_bytes[byte_offset:byte_offset+8],
                byteorder='big'
            )
            index = random_int % len(options)

            if index not in selected_indices:
                selected_indices.add(index)
                byte_offset += 8

            # If we run out of bytes, get more
            if byte_offset >= len(random_bytes):
                random_bytes = await self.get_random_bytes(num_bytes_needed)
                byte_offset = 0

        return [options[i] for i in sorted(selected_indices)]

    async def get_request_status(self, request_id: str) -> Optional[EntropyRequest]:
        """
        Get status of an entropy request.

        Args:
            request_id: Request ID to check

        Returns:
            Optional[EntropyRequest]: Request object if found
        """
        return self._requests.get(request_id)

    # Private methods

    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        timestamp = datetime.now().isoformat()
        data = f"pyth_entropy_{timestamp}_{self._sequence_number}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    async def _mock_get_entropy(self, num_bytes: int, request_id: str) -> bytes:
        """Generate mock entropy (for development)."""
        # Simulate small delay
        await asyncio.sleep(0.05)

        # Generate deterministic but unpredictable bytes
        seed_data = f"{request_id}{datetime.now().isoformat()}"
        hash_obj = hashlib.sha256(seed_data.encode())

        # Generate enough bytes
        entropy_bytes = b''
        while len(entropy_bytes) < num_bytes:
            entropy_bytes += hash_obj.digest()
            hash_obj = hashlib.sha256(hash_obj.digest())

        return entropy_bytes[:num_bytes]

    async def _fetch_entropy(self, num_bytes: int) -> bytes:
        """Fetch entropy from Pyth Network (production)."""
        # TODO: Implement actual Pyth Network entropy fetching
        # This would use the Pyth SDK to fetch entropy from Solana
        logger.info("Fetching entropy from Pyth Network...")

        # Example structure (not implemented):
        # from pythclient.solana import SolanaClient, SolanaPublicKey
        # solana_client = SolanaClient(endpoint=self.endpoint)
        # entropy = await solana_client.get_entropy()

        raise NotImplementedError("Production Pyth entropy fetching not yet implemented. Use PYTH_MOCK_MODE=true")


# Helper function for quick random selection
async def get_random_pyth_selection(
    options: List[Any],
    count: int
) -> List[Any]:
    """
    Quick helper to get random selection using Pyth Entropy.

    Args:
        options: List of options to choose from
        count: Number of items to select

    Returns:
        List[Any]: Selected items

    Example:
        selected = await get_random_pyth_selection(agents, 5)
    """
    pyth = PythEntropyProvider()
    return await pyth.get_random_selection(options, count)
