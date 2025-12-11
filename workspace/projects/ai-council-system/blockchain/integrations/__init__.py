"""
Blockchain integration clients.

Provides connection and interaction with blockchain networks:
- Solana: Council selection and voting programs
- Ethereum: Future support for multi-chain

Example:
    from blockchain.integrations import SolanaClient

    client = SolanaClient(network='devnet')
    await client.initialize_council_session(session_id, required_agents=5)
"""

from .solana_client import SolanaClient, CouncilSelectionClient, VotingClient

__all__ = [
    'SolanaClient',
    'CouncilSelectionClient',
    'VotingClient',
]
