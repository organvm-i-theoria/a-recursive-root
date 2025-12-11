#!/usr/bin/env python3
"""
Token Economics Demo

Demonstrates the complete token mechanics system:
- Token creation and management
- Staking with time-weighted voting power
- Reward distribution with boosters
- Governance proposals and voting
- Economic projections

This demo works in mock mode by default (no blockchain required).
"""

import asyncio
import sys
from pathlib import Path
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).parent.parent))

from blockchain.token import (
    TokenManager, StakingManager, RewardsDistributor,
    GovernanceManager, EconomicsCalculator,
    LockPeriod, RewardBooster, VoteType
)


async def main():
    print("=" * 70)
    print("AI COUNCIL TOKEN ECONOMICS DEMO")
    print("=" * 70)
    print()

    # Step 1: Token Creation
    print("Step 1: Creating AI Council Token (ACT)")
    print("-" * 70)

    token_mgr = TokenManager()

    token = await token_mgr.create_token(
        name="AI Council Token",
        symbol="ACT",
        decimals=9,
        total_supply=1_000_000_000
    )

    print(f"Token Created:")
    print(f"  Name: {token.name}")
    print(f"  Symbol: {token.symbol}")
    print(f"  Decimals: {token.decimals}")
    print(f"  Total Supply: {token.total_supply:,}")
    print(f"  Mint Address: {token.mint_address}")
    print()

    # Distribute initial allocation
    print("Distributing initial token allocation...")
    allocations = await token_mgr.distribute_initial_allocation()
    print(f"Allocated to {len(allocations)} categories")
    print()

    # Step 2: Create test wallets and mint tokens
    print("Step 2: Setting up test wallets")
    print("-" * 70)

    wallets = {
        "alice": "wallet_alice",
        "bob": "wallet_bob",
        "charlie": "wallet_charlie",
        "diana": "wallet_diana",
        "eve": "wallet_eve"
    }

    # Mint tokens to each wallet
    for name, wallet in wallets.items():
        amount = 10000 if name != "alice" else 50000  # Alice gets more for proposal
        await token_mgr.mint_tokens(wallet, amount)
        balance = await token_mgr.get_balance(wallet)
        print(f"  {name.capitalize()}: {balance} ACT")
    print()

    # Step 3: Staking with different lock periods
    print("Step 3: Staking tokens with various lock periods")
    print("-" * 70)

    staking = StakingManager(token_mgr)

    stake_configs = {
        "alice": (Decimal(20000), 180),   # 6 months lock (3.0x)
        "bob": (Decimal(5000), 90),       # 3 months lock (2.0x)
        "charlie": (Decimal(3000), 30),   # 1 month lock (1.5x)
        "diana": (Decimal(2000), 7),      # 1 week lock (1.2x)
        "eve": (Decimal(1000), 0),        # No lock (1.0x)
    }

    for name, (amount, lock_days) in stake_configs.items():
        wallet = wallets[name]
        stake_info = await staking.stake(wallet, amount, lock_days)

        print(f"{name.capitalize()}'s stake:")
        print(f"  Amount: {stake_info.amount} ACT")
        print(f"  Lock period: {lock_days} days")
        print(f"  Multiplier: {stake_info.time_multiplier}x")
        print(f"  Voting power: {stake_info.voting_power}")
        print(f"  Unlocks: {stake_info.unlock_timestamp.strftime('%Y-%m-%d')}")
        print()

    # Display staking statistics
    stats = await staking.get_staking_stats()
    print(f"Staking Statistics:")
    print(f"  Total stakers: {stats['total_stakers']}")
    print(f"  Total staked: {stats['total_staked']:,.0f} ACT")
    print(f"  Total voting power: {stats['total_voting_power']:,.0f}")
    print(f"  Average lock period: {stats['average_lock_period_days']:.1f} days")
    print(f"  Staking ratio: {stats['staking_ratio'] * 100:.1f}%")
    print()

    # Step 4: Reward distribution
    print("Step 4: Distributing weekly rewards")
    print("-" * 70)

    rewards = RewardsDistributor(staking, token_mgr)

    # Apply boosters to active participants
    await rewards.apply_booster(wallets["alice"], RewardBooster.LONG_TERM_STAKING)
    await rewards.apply_booster(wallets["alice"], RewardBooster.GOVERNANCE_VOTING)
    await rewards.apply_booster(wallets["bob"], RewardBooster.ACTIVE_PARTICIPATION)

    print("Applied reward boosters:")
    print("  Alice: Long-term staking (20%) + Governance voting (15%)")
    print("  Bob: Active participation (10%)")
    print()

    # Distribute rewards
    reward_pool = Decimal(10000)  # 10,000 ACT weekly
    print(f"Distributing {reward_pool:,} ACT to all stakers...")
    print()

    distribution_results = await rewards.distribute_rewards(reward_pool, auto_compound=False)

    print(f"Reward Distribution Results:")
    for result in distribution_results:
        name = [n for n, w in wallets.items() if w == result.wallet][0]
        print(f"  {name.capitalize()}:")
        print(f"    Base reward: {result.base_reward:.2f} ACT")
        print(f"    Boosters: {[f'{k} (+{v*100:.0f}%)' for k, v in result.boosters_applied.items()]}")
        print(f"    Total boost: {result.total_boost * 100:.0f}%")
        print(f"    Final reward: {result.final_reward:.2f} ACT")
        print()

    # Calculate APY
    print("Estimated APY by lock period:")
    for lock_days in [0, 7, 30, 90, 180]:
        apy = await rewards.calculate_apy(lock_days, include_boosters=True)
        print(f"  {lock_days:3d} days: {apy:6.2f}% (with max boosters)")
    print()

    # Step 5: Governance
    print("Step 5: Governance proposal and voting")
    print("-" * 70)

    governance = GovernanceManager(staking)

    # Alice creates a proposal
    proposal = await governance.create_proposal(
        wallet=wallets["alice"],
        title="Increase staking rewards by 20%",
        description="Proposal to increase weekly staking rewards from 10,000 to 12,000 ACT"
    )

    print(f"Proposal Created:")
    print(f"  ID: {proposal.proposal_id}")
    print(f"  Title: {proposal.title}")
    print(f"  Proposer: Alice")
    print(f"  Voting ends: {proposal.voting_ends.strftime('%Y-%m-%d')}")
    print(f"  Quorum required: {proposal.quorum_required:,.0f} voting power")
    print(f"  Approval threshold: {proposal.approval_threshold * 100}%")
    print()

    # Everyone votes
    votes = {
        "alice": VoteType.FOR,
        "bob": VoteType.FOR,
        "charlie": VoteType.AGAINST,
        "diana": VoteType.FOR,
        "eve": VoteType.ABSTAIN
    }

    print("Voting:")
    for name, vote_type in votes.items():
        wallet = wallets[name]
        voting_power = await staking.calculate_voting_power(wallet)
        await governance.vote(proposal.proposal_id, wallet, vote_type)
        print(f"  {name.capitalize()}: {vote_type.value.upper()} (power: {voting_power:,.0f})")
    print()

    # Finalize proposal
    status = await governance.finalize_proposal(proposal.proposal_id)

    print(f"Proposal Results:")
    print(f"  Status: {status.value.upper()}")
    print(f"  Votes FOR: {proposal.votes_for:,.0f}")
    print(f"  Votes AGAINST: {proposal.votes_against:,.0f}")
    print(f"  Votes ABSTAIN: {proposal.votes_abstain:,.0f}")
    print(f"  Total votes: {proposal.votes_for + proposal.votes_against + proposal.votes_abstain:,.0f}")
    print()

    # Step 6: Economic projections
    print("Step 6: Tokenomics projections")
    print("-" * 70)

    economics = EconomicsCalculator()

    print("5-Year Economic Projection:")
    print()

    for year in range(1, 6):
        inflation = max(0.05 - (year - 1) * 0.01, 0.02)  # Decreasing inflation
        model = economics.project_year(year, staking_ratio=0.4, inflation=inflation)

        print(f"Year {year}:")
        print(f"  Circulating Supply: {model.circulating_supply:,.0f} ACT")
        print(f"  Staked: {model.staked:,.0f} ACT ({model.staking_ratio * 100:.0f}%)")
        print(f"  Rewards Distributed: {model.rewards_distributed:,.0f} ACT")
        print(f"  Inflation Rate: {model.inflation_rate * 100:.1f}%")
        print(f"  Average APY: {model.average_apy:.2f}%")
        print()

    # Step 7: Unstaking demo
    print("Step 7: Unstaking demonstration")
    print("-" * 70)

    # Eve unstakes (no lock, no penalty)
    print("Eve unstaking (no lock period):")
    unstake_info = await staking.unstake(wallets["eve"], Decimal(500))
    print(f"  Amount unstaked: {unstake_info.amount} ACT")
    print(f"  Penalty applied: {unstake_info.penalty_applied}")
    print(f"  Final amount: {unstake_info.final_amount} ACT")
    print()

    # Charlie tries force unstake (penalty)
    print("Charlie force unstaking (locked for 30 days):")
    unstake_info = await staking.unstake(wallets["charlie"], Decimal(1000), force=True)
    print(f"  Amount unstaked: {unstake_info.amount} ACT")
    print(f"  Penalty applied: {unstake_info.penalty_applied}")
    print(f"  Penalty amount: {unstake_info.penalty_amount} ACT ({StakingManager.UNSTAKE_PENALTY * 100:.0f}%)")
    print(f"  Final amount: {unstake_info.final_amount} ACT")
    print()

    # Final statistics
    print("=" * 70)
    print("FINAL STATISTICS")
    print("=" * 70)

    token_info = await token_mgr.get_token_info()
    final_stats = await staking.get_staking_stats()
    total_rewards = await rewards.get_total_rewards_distributed()

    print(f"Token:")
    print(f"  Total Supply: {token_info.total_supply:,}")
    print(f"  Circulating: {token_info.circulating_supply:,}")
    print()

    print(f"Staking:")
    print(f"  Active Stakers: {final_stats['total_stakers']}")
    print(f"  Total Staked: {final_stats['total_staked']:,.0f} ACT")
    print(f"  Total Voting Power: {final_stats['total_voting_power']:,.0f}")
    print(f"  Staking Ratio: {final_stats['staking_ratio'] * 100:.2f}%")
    print()

    print(f"Rewards:")
    print(f"  Total Distributed: {total_rewards:,.2f} ACT")
    print(f"  Distribution Periods: {len(await rewards.get_period_history())}")
    print()

    print(f"Governance:")
    print(f"  Active Proposals: 1")
    print(f"  Proposal Status: {status.value.upper()}")
    print()

    print("=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print()

    print("✅ Successfully demonstrated:")
    print("  1. Token creation and distribution")
    print("  2. Multi-tier staking with time multipliers")
    print("  3. Proportional reward distribution with boosters")
    print("  4. Governance proposal and weighted voting")
    print("  5. Economic projections and sustainability")
    print("  6. Unstaking with and without penalties")
    print()

    print("All token mechanics functional and ready for integration!")
    print()


if __name__ == "__main__":
    asyncio.run(main())
