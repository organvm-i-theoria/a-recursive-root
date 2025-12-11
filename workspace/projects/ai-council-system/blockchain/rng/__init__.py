"""
Random Number Generation module for blockchain-based verifiable randomness.

This module provides multiple sources of verifiable randomness:
- Chainlink VRF: Industry-standard verifiable random function
- Pyth Entropy: High-frequency entropy source
- Hybrid RNG: Coordinator with automatic fallback

Example:
    from blockchain.rng import HybridRNG

    rng = HybridRNG()
    selected = await rng.get_random_selection(agents, count=5)
"""

from .chainlink_vrf import ChainlinkVRFProvider
from .pyth_entropy import PythEntropyProvider
from .hybrid_rng import HybridRNG

__all__ = [
    'ChainlinkVRFProvider',
    'PythEntropyProvider',
    'HybridRNG',
]
