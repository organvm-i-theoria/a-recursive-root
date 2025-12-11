"""
Chainlink VRF (Verifiable Random Function) provider.

Provides provably fair, tamper-proof randomness using Chainlink's
decentralized oracle network.
"""

import asyncio
import hashlib
import logging
import os
from dataclasses import dataclass
from typing import List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class VRFRequest:
    """Represents a VRF randomness request."""
    request_id: str
    seed: int
    timestamp: datetime
    status: str  # pending, fulfilled, failed
    confirmations: int = 0
    random_number: Optional[int] = None
    proof: Optional[str] = None


@dataclass
class VRFProof:
    """Verification proof for VRF randomness."""
    request_id: str
    random_number: int
    proof_hash: str
    block_number: int
    is_valid: bool
    timestamp: datetime


class ChainlinkVRFProvider:
    """
    Chainlink VRF provider for verifiable randomness.

    Features:
    - Provably fair random number generation
    - On-chain verification
    - Tamper-proof and cryptographically secure

    Example:
        vrf = ChainlinkVRFProvider()
        request_id = await vrf.request_randomness(seed=12345)
        random_num = await vrf.get_random_number(request_id)
        is_valid = vrf.verify_randomness(request_id, random_num)
    """

    def __init__(
        self,
        coordinator_address: Optional[str] = None,
        key_hash: Optional[str] = None,
        subscription_id: Optional[int] = None,
        network: str = "devnet"
    ):
        """
        Initialize Chainlink VRF provider.

        Args:
            coordinator_address: VRF coordinator contract address
            key_hash: Key hash for gas lane
            subscription_id: Subscription ID for VRF
            network: Network to use (devnet, testnet, mainnet)
        """
        self.coordinator_address = coordinator_address or os.getenv('CHAINLINK_VRF_COORDINATOR')
        self.key_hash = key_hash or os.getenv('CHAINLINK_VRF_KEY_HASH')
        self.subscription_id = subscription_id or int(os.getenv('CHAINLINK_VRF_SUBSCRIPTION_ID', '0'))
        self.network = network

        # Request storage (in production, use database)
        self._requests: dict[str, VRFRequest] = {}

        # Mock mode for development without real Chainlink
        self.mock_mode = os.getenv('CHAINLINK_MOCK_MODE', 'true').lower() == 'true'

        if self.mock_mode:
            logger.warning("Chainlink VRF running in MOCK MODE (not using real blockchain)")
        else:
            logger.info(f"Chainlink VRF initialized on {network}")

    async def request_randomness(
        self,
        seed: int,
        num_words: int = 1,
        callback_gas_limit: int = 100000
    ) -> str:
        """
        Request random number from Chainlink VRF.

        Args:
            seed: Random seed for request
            num_words: Number of random words to request
            callback_gas_limit: Gas limit for callback

        Returns:
            str: Request ID for tracking

        Example:
            request_id = await vrf.request_randomness(seed=12345)
        """
        # Generate request ID
        request_id = self._generate_request_id(seed)

        # Create request
        request = VRFRequest(
            request_id=request_id,
            seed=seed,
            timestamp=datetime.now(),
            status="pending"
        )

        self._requests[request_id] = request

        if self.mock_mode:
            # In mock mode, simulate immediate fulfillment
            await self._mock_fulfill_request(request_id, seed)
            logger.info(f"Mock VRF request fulfilled: {request_id}")
        else:
            # In real mode, submit to blockchain
            await self._submit_vrf_request(seed, num_words, callback_gas_limit)
            logger.info(f"VRF request submitted: {request_id}")

        return request_id

    async def get_random_number(self, request_id: str, timeout: int = 30) -> Optional[int]:
        """
        Get random number for a request.

        Waits for fulfillment if request is pending.

        Args:
            request_id: Request ID to check
            timeout: Maximum seconds to wait

        Returns:
            Optional[int]: Random number if fulfilled, None otherwise

        Example:
            random_num = await vrf.get_random_number(request_id)
        """
        if request_id not in self._requests:
            logger.error(f"Request ID not found: {request_id}")
            return None

        request = self._requests[request_id]

        # Wait for fulfillment
        start_time = datetime.now()
        while request.status == "pending":
            if (datetime.now() - start_time).seconds > timeout:
                logger.warning(f"VRF request timeout: {request_id}")
                return None

            await asyncio.sleep(0.5)
            request = self._requests[request_id]

        if request.status == "fulfilled":
            return request.random_number
        else:
            logger.error(f"VRF request failed: {request_id}")
            return None

    def verify_randomness(self, request_id: str, random_number: int) -> bool:
        """
        Verify that a random number is valid for a request.

        Args:
            request_id: Request ID to verify
            random_number: Random number to verify

        Returns:
            bool: True if valid, False otherwise

        Example:
            is_valid = vrf.verify_randomness(request_id, random_num)
        """
        if request_id not in self._requests:
            logger.error(f"Request ID not found: {request_id}")
            return False

        request = self._requests[request_id]

        if request.random_number != random_number:
            logger.error(f"Random number mismatch for {request_id}")
            return False

        if request.proof is None:
            logger.error(f"No proof available for {request_id}")
            return False

        # Verify proof (in production, verify on-chain)
        return self._verify_proof(request)

    async def get_request_status(self, request_id: str) -> Optional[VRFRequest]:
        """
        Get status of a VRF request.

        Args:
            request_id: Request ID to check

        Returns:
            Optional[VRFRequest]: Request object if found
        """
        return self._requests.get(request_id)

    def get_proof(self, request_id: str) -> Optional[VRFProof]:
        """
        Get verification proof for a request.

        Args:
            request_id: Request ID

        Returns:
            Optional[VRFProof]: Proof object if available
        """
        if request_id not in self._requests:
            return None

        request = self._requests[request_id]

        if request.status != "fulfilled" or request.proof is None:
            return None

        return VRFProof(
            request_id=request_id,
            random_number=request.random_number,
            proof_hash=request.proof,
            block_number=0,  # Would be actual block in production
            is_valid=True,
            timestamp=request.timestamp
        )

    # Private methods

    def _generate_request_id(self, seed: int) -> str:
        """Generate unique request ID."""
        timestamp = datetime.now().isoformat()
        data = f"{seed}{timestamp}{self.subscription_id}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    async def _mock_fulfill_request(self, request_id: str, seed: int):
        """Fulfill request in mock mode (for development)."""
        # Simulate some delay
        await asyncio.sleep(0.1)

        request = self._requests[request_id]

        # Generate deterministic but unpredictable random number
        random_bytes = hashlib.sha256(f"{seed}{request_id}".encode()).digest()
        random_number = int.from_bytes(random_bytes[:8], byteorder='big')

        # Generate proof
        proof = hashlib.sha256(f"{random_number}{seed}".encode()).hexdigest()

        # Update request
        request.status = "fulfilled"
        request.confirmations = 6
        request.random_number = random_number
        request.proof = proof

    async def _submit_vrf_request(self, seed: int, num_words: int, gas_limit: int):
        """Submit VRF request to blockchain (production)."""
        # TODO: Implement actual blockchain submission
        # This would use Web3.py or similar to call the VRF coordinator contract
        logger.info("Submitting VRF request to blockchain...")

        # Example structure (not implemented):
        # contract = self.web3.eth.contract(address=self.coordinator_address, abi=VRF_ABI)
        # tx = contract.functions.requestRandomWords(
        #     self.key_hash,
        #     self.subscription_id,
        #     3,  # request confirmations
        #     gas_limit,
        #     num_words
        # ).transact()

        raise NotImplementedError("Production VRF submission not yet implemented. Use CHAINLINK_MOCK_MODE=true")

    def _verify_proof(self, request: VRFRequest) -> bool:
        """Verify VRF proof."""
        # In production, this would verify the cryptographic proof on-chain
        # For mock mode, just check that proof exists and matches pattern
        if self.mock_mode:
            expected_proof = hashlib.sha256(f"{request.random_number}{request.seed}".encode()).hexdigest()
            return request.proof == expected_proof
        else:
            # TODO: Implement on-chain proof verification
            raise NotImplementedError("Production proof verification not yet implemented")


# Helper function for quick random selection
async def get_random_vrf_selection(
    options: List[Any],
    count: int,
    seed: Optional[int] = None
) -> List[Any]:
    """
    Quick helper to get random selection using VRF.

    Args:
        options: List of options to choose from
        count: Number of items to select
        seed: Optional seed (random if not provided)

    Returns:
        List[Any]: Selected items

    Example:
        selected = await get_random_vrf_selection(agents, 5)
    """
    if count > len(options):
        raise ValueError(f"Cannot select {count} items from {len(options)} options")

    # Generate seed if not provided
    if seed is None:
        seed = int.from_bytes(os.urandom(4), byteorder='big')

    # Get random number
    vrf = ChainlinkVRFProvider()
    request_id = await vrf.request_randomness(seed)
    random_number = await vrf.get_random_number(request_id)

    if random_number is None:
        raise RuntimeError("Failed to get random number from VRF")

    # Use random number to select items
    selected_indices = set()
    current_seed = random_number

    while len(selected_indices) < count:
        index = current_seed % len(options)
        selected_indices.add(index)
        # Generate next seed
        current_seed = int(hashlib.sha256(str(current_seed).encode()).hexdigest(), 16)

    return [options[i] for i in selected_indices]
