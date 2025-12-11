"""
Token Economics Module for AI Council System.

Provides comprehensive token mechanics including:
- Token management (SPL token operations)
- Staking mechanism with time-weighted voting power
- Reward distribution system
- Governance functionality

Example:
    from blockchain.token import TokenManager, StakingManager, RewardsDistributor

    # Create and manage tokens
    token_mgr = TokenManager()
    await token_mgr.create_token("AI Council Token", "ACT", 9, 1_000_000_000)

    # Stake tokens
    staking = StakingManager()
    await staking.stake(wallet, amount=1000, lock_days=30)

    # Distribute rewards
    rewards = RewardsDistributor()
    await rewards.distribute_rewards(reward_pool=10000)
"""

from .token_manager import TokenManager, TokenInfo
from .staking import StakingManager, StakeInfo, LockPeriod
from .rewards import RewardsDistributor, RewardInfo, RewardBooster
from .governance import GovernanceManager, Proposal, ProposalStatus, VoteType
from .economics import EconomicsCalculator, TokenomicsModel

__all__ = [
    'TokenManager',
    'TokenInfo',
    'StakingManager',
    'StakeInfo',
    'LockPeriod',
    'RewardsDistributor',
    'RewardInfo',
    'RewardBooster',
    'GovernanceManager',
    'Proposal',
    'ProposalStatus',
    'VoteType',
    'EconomicsCalculator',
    'TokenomicsModel',
]

__version__ = "0.3.3-alpha"
