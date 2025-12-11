"""
Blockchain integration module for AI Council System.

This module provides blockchain-based functionality including:
- Verifiable randomness (Chainlink VRF, Pyth Entropy)
- Smart contracts for council selection and voting (Solana)
- Token mechanics (staking, rewards, governance)
- On-chain data integration

Submodules:
-----------
- rng: Random number generation using blockchain sources
- contracts: Smart contract interfaces and deployment
- token: Token mechanics and staking
- integrations: Blockchain client integrations

Example:
--------
    from blockchain.rng import HybridRNG
    from blockchain.token import StakingManager

    # Get verifiable random selection
    rng = HybridRNG()
    selected = await rng.get_random_selection(agents, 5)

    # Stake tokens for voting power
    staking = StakingManager()
    await staking.stake_tokens(wallet, 1000)
"""

__version__ = "0.3.0-alpha"
__author__ = "AI Council System Team"

from typing import Optional

# Will be populated as modules are implemented
__all__ = [
    'HybridRNG',
    'ChainlinkVRFProvider',
    'PythEntropyProvider',
    'StakingManager',
    'TokenManager',
    'SolanaClient',
]


def is_blockchain_enabled() -> bool:
    """
    Check if blockchain functionality is enabled.

    Returns:
        bool: True if blockchain is configured and enabled
    """
    import os
    return os.getenv('BLOCKCHAIN_ENABLED', 'false').lower() == 'true'


def get_network() -> str:
    """
    Get the configured blockchain network.

    Returns:
        str: Network name (devnet, testnet, mainnet)
    """
    import os
    return os.getenv('BLOCKCHAIN_NETWORK', 'devnet')
