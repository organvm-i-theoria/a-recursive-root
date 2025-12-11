"""
Rewards Distributor for AI Council Token.

Handles reward calculations and distribution to stakers.
"""

import logging
import os
from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum

logger = logging.getLogger(__name__)


class RewardBooster(Enum):
    """Reward booster types."""
    ACTIVE_PARTICIPATION = "active_participation"     # 10%
    LONG_TERM_STAKING = "long_term_staking"          # 20%
    GOVERNANCE_VOTING = "governance_voting"           # 15%


@dataclass
class RewardInfo:
    """Information about rewards for a user."""
    wallet: str
    base_reward: Decimal               # Base reward amount
    boosters_applied: Dict[str, float] # Applied boosters
    total_boost: float                 # Total boost percentage
    final_reward: Decimal              # Final reward after boosters
    distribution_date: datetime        # When distributed
    auto_compounded: bool              # Whether auto-staked


@dataclass
class RewardPeriod:
    """Information about a reward distribution period."""
    period_id: str
    start_date: datetime
    end_date: datetime
    total_rewards: Decimal
    total_distributed: Decimal
    participants: int
    average_reward: Decimal


class RewardsDistributor:
    """
    Manages reward distribution for staked tokens.

    Features:
    - Proportional reward distribution based on voting power
    - Multiple reward boosters
    - Weekly distribution cycles
    - Auto-compounding option
    - Reward history tracking

    Example:
        rewards = RewardsDistributor(staking_manager)

        # Distribute weekly rewards
        results = await rewards.distribute_rewards(reward_pool=10000)

        # Calculate user's reward
        reward = await rewards.calculate_user_reward(wallet, total_rewards=10000)

        # Claim rewards
        await rewards.claim_rewards(wallet)
    """

    # Reward parameters
    ANNUAL_INFLATION_RATE = 0.05  # 5% max
    DISTRIBUTION_FREQUENCY_DAYS = 7
    MIN_CLAIM_AMOUNT = Decimal(1)

    # Booster percentages
    BOOSTERS = {
        RewardBooster.ACTIVE_PARTICIPATION: 0.10,  # 10%
        RewardBooster.LONG_TERM_STAKING: 0.20,     # 20%
        RewardBooster.GOVERNANCE_VOTING: 0.15,     # 15%
    }

    def __init__(
        self,
        staking_manager,
        token_manager=None,
        network: str = "devnet"
    ):
        """
        Initialize Rewards Distributor.

        Args:
            staking_manager: StakingManager instance
            token_manager: TokenManager instance (optional)
            network: Solana network
        """
        self.staking_manager = staking_manager
        self.token_manager = token_manager
        self.network = network

        # Mock mode
        self.mock_mode = os.getenv('SOLANA_MOCK_MODE', 'true').lower() == 'true'

        if self.mock_mode:
            logger.warning("Rewards Distributor running in MOCK MODE")
            self._reward_history: Dict[str, List[RewardInfo]] = {}
            self._unclaimed_rewards: Dict[str, Decimal] = {}
            self._period_history: List[RewardPeriod] = []
            self._user_boosters: Dict[str, List[RewardBooster]] = {}
        else:
            logger.info(f"Rewards Distributor initialized on {network}")

    async def calculate_user_reward(
        self,
        wallet: str,
        total_rewards: Decimal
    ) -> Decimal:
        """
        Calculate reward for a user based on their voting power.

        Formula: user_reward = total_rewards * (user_voting_power / total_voting_power)

        Args:
            wallet: Wallet address
            total_rewards: Total reward pool

        Returns:
            Decimal: User's reward amount

        Example:
            reward = await rewards.calculate_user_reward(wallet, Decimal(10000))
        """
        # Get user's voting power
        user_voting_power = await self.staking_manager.calculate_voting_power(wallet)

        if user_voting_power == 0:
            return Decimal(0)

        # Get total voting power
        total_voting_power = await self.staking_manager.get_total_voting_power()

        if total_voting_power == 0:
            return Decimal(0)

        # Calculate proportional reward
        reward_share = user_voting_power / total_voting_power
        base_reward = total_rewards * reward_share

        # Apply boosters
        boosters_applied = await self.get_active_boosters(wallet)
        total_boost = sum(self.BOOSTERS[booster] for booster in boosters_applied)

        if total_boost > 0:
            boost_amount = base_reward * Decimal(total_boost)
            final_reward = base_reward + boost_amount
        else:
            final_reward = base_reward

        logger.debug(
            f"Calculated reward for {wallet}: {final_reward} ACT "
            f"(base: {base_reward}, boost: {total_boost * 100}%)"
        )

        return final_reward

    async def distribute_rewards(
        self,
        reward_pool: Decimal,
        auto_compound: bool = True
    ) -> List[RewardInfo]:
        """
        Distribute rewards to all stakers.

        Args:
            reward_pool: Total rewards to distribute
            auto_compound: Whether to auto-stake rewards

        Returns:
            List[RewardInfo]: Distribution results for each user

        Example:
            results = await rewards.distribute_rewards(Decimal(10000))
            for result in results:
                print(f"{result.wallet}: {result.final_reward} ACT")
        """
        if self.mock_mode:
            # Get all stakers
            stakes = await self.staking_manager.get_all_stakes()

            if not stakes:
                logger.warning("No stakers found for reward distribution")
                return []

            distribution_results = []
            total_distributed = Decimal(0)

            for stake in stakes:
                wallet = stake.wallet

                # Calculate reward
                base_reward = await self.calculate_user_reward(wallet, reward_pool)

                # Get boosters
                boosters_applied = await self.get_active_boosters(wallet)
                boost_dict = {booster.value: self.BOOSTERS[booster] for booster in boosters_applied}
                total_boost = sum(boost_dict.values())

                # Calculate final reward with boosters
                boost_amount = base_reward * Decimal(total_boost)
                final_reward = base_reward + boost_amount

                # Record reward
                reward_info = RewardInfo(
                    wallet=wallet,
                    base_reward=base_reward,
                    boosters_applied=boost_dict,
                    total_boost=total_boost,
                    final_reward=final_reward,
                    distribution_date=datetime.now(),
                    auto_compounded=auto_compound
                )

                # Add to unclaimed or auto-compound
                if auto_compound:
                    # Auto-stake the reward
                    await self.staking_manager.stake(
                        wallet,
                        final_reward,
                        lock_days=stake.lock_days  # Same lock period
                    )
                    logger.info(f"Auto-compounded {final_reward} ACT for {wallet}")
                else:
                    # Add to unclaimed
                    if wallet not in self._unclaimed_rewards:
                        self._unclaimed_rewards[wallet] = Decimal(0)
                    self._unclaimed_rewards[wallet] += final_reward

                # Save to history
                if wallet not in self._reward_history:
                    self._reward_history[wallet] = []
                self._reward_history[wallet].append(reward_info)

                distribution_results.append(reward_info)
                total_distributed += final_reward

            # Record period
            period = RewardPeriod(
                period_id=f"period_{datetime.now().strftime('%Y%m%d')}",
                start_date=datetime.now() - timedelta(days=self.DISTRIBUTION_FREQUENCY_DAYS),
                end_date=datetime.now(),
                total_rewards=reward_pool,
                total_distributed=total_distributed,
                participants=len(stakes),
                average_reward=total_distributed / len(stakes) if stakes else Decimal(0)
            )

            self._period_history.append(period)

            logger.info(
                f"Distributed {total_distributed} ACT to {len(stakes)} stakers "
                f"(avg: {period.average_reward} ACT per user)"
            )

            return distribution_results

        raise NotImplementedError("Real reward distribution not implemented")

    async def claim_rewards(
        self,
        wallet: str,
        auto_stake: bool = False,
        lock_days: int = 0
    ) -> Decimal:
        """
        Claim accumulated rewards.

        Args:
            wallet: Wallet address
            auto_stake: Whether to stake claimed rewards
            lock_days: Lock period if auto-staking

        Returns:
            Decimal: Amount claimed

        Example:
            # Claim to wallet
            claimed = await rewards.claim_rewards(wallet)

            # Claim and stake
            claimed = await rewards.claim_rewards(wallet, auto_stake=True, lock_days=30)
        """
        if self.mock_mode:
            unclaimed = self._unclaimed_rewards.get(wallet, Decimal(0))

            if unclaimed < self.MIN_CLAIM_AMOUNT:
                raise ValueError(
                    f"Unclaimed rewards ({unclaimed}) below minimum claim amount ({self.MIN_CLAIM_AMOUNT})"
                )

            # Claim
            if auto_stake:
                # Stake the rewards
                await self.staking_manager.stake(wallet, unclaimed, lock_days)
                logger.info(f"Claimed and staked {unclaimed} ACT for {wallet}")
            else:
                # Transfer to wallet (in real implementation)
                logger.info(f"Claimed {unclaimed} ACT to {wallet}")

            # Reset unclaimed
            self._unclaimed_rewards[wallet] = Decimal(0)

            return unclaimed

        raise NotImplementedError("Real reward claiming not implemented")

    async def get_unclaimed_rewards(self, wallet: str) -> Decimal:
        """
        Get amount of unclaimed rewards for a wallet.

        Args:
            wallet: Wallet address

        Returns:
            Decimal: Unclaimed reward amount

        Example:
            unclaimed = await rewards.get_unclaimed_rewards(wallet)
        """
        if self.mock_mode:
            return self._unclaimed_rewards.get(wallet, Decimal(0))

        raise NotImplementedError("Real unclaimed rewards check not implemented")

    async def get_reward_history(
        self,
        wallet: str,
        limit: int = 10
    ) -> List[RewardInfo]:
        """
        Get reward history for a wallet.

        Args:
            wallet: Wallet address
            limit: Maximum number of records

        Returns:
            List[RewardInfo]: Reward history

        Example:
            history = await rewards.get_reward_history(wallet)
            for reward in history:
                print(f"{reward.distribution_date}: {reward.final_reward} ACT")
        """
        if self.mock_mode:
            history = self._reward_history.get(wallet, [])
            return history[-limit:] if limit else history

        raise NotImplementedError("Real reward history not implemented")

    async def get_active_boosters(self, wallet: str) -> List[RewardBooster]:
        """
        Get active reward boosters for a wallet.

        Args:
            wallet: Wallet address

        Returns:
            List[RewardBooster]: Active boosters

        Example:
            boosters = await rewards.get_active_boosters(wallet)
        """
        if self.mock_mode:
            return self._user_boosters.get(wallet, [])

        raise NotImplementedError("Real booster check not implemented")

    async def apply_booster(
        self,
        wallet: str,
        booster: RewardBooster
    ) -> None:
        """
        Apply a reward booster to a user.

        Args:
            wallet: Wallet address
            booster: Booster to apply

        Example:
            # Reward active participant
            await rewards.apply_booster(wallet, RewardBooster.ACTIVE_PARTICIPATION)
        """
        if self.mock_mode:
            if wallet not in self._user_boosters:
                self._user_boosters[wallet] = []

            if booster not in self._user_boosters[wallet]:
                self._user_boosters[wallet].append(booster)

                logger.info(
                    f"Applied {booster.value} booster (+{self.BOOSTERS[booster] * 100}%) to {wallet}"
                )

            return

        raise NotImplementedError("Real booster application not implemented")

    async def remove_booster(
        self,
        wallet: str,
        booster: RewardBooster
    ) -> None:
        """
        Remove a reward booster from a user.

        Args:
            wallet: Wallet address
            booster: Booster to remove

        Example:
            await rewards.remove_booster(wallet, RewardBooster.ACTIVE_PARTICIPATION)
        """
        if self.mock_mode:
            if wallet in self._user_boosters:
                if booster in self._user_boosters[wallet]:
                    self._user_boosters[wallet].remove(booster)
                    logger.info(f"Removed {booster.value} booster from {wallet}")

            return

        raise NotImplementedError("Real booster removal not implemented")

    async def calculate_apy(
        self,
        lock_days: int,
        include_boosters: bool = True
    ) -> float:
        """
        Calculate APY for a given lock period.

        Args:
            lock_days: Lock period in days
            include_boosters: Whether to include potential boosters

        Returns:
            float: APY percentage

        Example:
            apy = await rewards.calculate_apy(30, include_boosters=True)
            print(f"30-day APY: {apy}%")
        """
        # Base APY from inflation
        base_apy = self.ANNUAL_INFLATION_RATE * 100

        # Time multiplier boost
        multiplier = self.staking_manager.get_time_multiplier(lock_days)
        multiplier_boost = (multiplier - 1.0) * 100

        if include_boosters:
            # Maximum possible boost
            max_boost = sum(self.BOOSTERS.values()) * 100
            total_apy = base_apy + multiplier_boost + max_boost
        else:
            total_apy = base_apy + multiplier_boost

        return total_apy

    async def get_period_history(self, limit: int = 10) -> List[RewardPeriod]:
        """
        Get historical reward distribution periods.

        Args:
            limit: Maximum number of periods

        Returns:
            List[RewardPeriod]: Period history

        Example:
            periods = await rewards.get_period_history()
            for period in periods:
                print(f"{period.period_id}: {period.total_distributed} ACT distributed")
        """
        if self.mock_mode:
            return self._period_history[-limit:] if limit else self._period_history

        raise NotImplementedError("Real period history not implemented")

    async def get_total_rewards_distributed(self) -> Decimal:
        """
        Get total rewards distributed all-time.

        Returns:
            Decimal: Total distributed

        Example:
            total = await rewards.get_total_rewards_distributed()
        """
        if self.mock_mode:
            return sum(period.total_distributed for period in self._period_history)

        raise NotImplementedError("Real total rewards not implemented")

    async def calculate_boosters(self, wallet: str) -> Dict[str, float]:
        """
        Calculate all applicable boosters for a wallet.

        Args:
            wallet: Wallet address

        Returns:
            Dict[str, float]: Booster name -> percentage

        Example:
            boosters = await rewards.calculate_boosters(wallet)
        """
        active_boosters = await self.get_active_boosters(wallet)

        return {
            booster.value: self.BOOSTERS[booster]
            for booster in active_boosters
        }
