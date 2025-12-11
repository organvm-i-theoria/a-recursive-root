"""
Staking Manager for AI Council Token.

Implements time-weighted staking mechanism with voting power calculations.
"""

import logging
import os
from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum

logger = logging.getLogger(__name__)


class LockPeriod(Enum):
    """Lock period options for staking."""
    NO_LOCK = 0          # 1.0x multiplier
    WEEK = 7             # 1.2x multiplier
    MONTH = 30           # 1.5x multiplier
    QUARTER = 90         # 2.0x multiplier
    HALF_YEAR = 180      # 3.0x multiplier


@dataclass
class StakeInfo:
    """Information about a user's stake."""
    wallet: str
    amount: Decimal                    # Staked amount
    stake_timestamp: datetime          # When staked
    lock_days: int                     # Lock period in days
    unlock_timestamp: datetime         # When can unstake
    time_multiplier: float             # Current multiplier
    voting_power: Decimal              # Calculated voting power
    rewards_earned: Decimal            # Accumulated rewards
    participation_boost: float         # Participation bonus
    is_locked: bool                    # Currently locked


@dataclass
class UnstakeInfo:
    """Information about an unstake operation."""
    wallet: str
    amount: Decimal
    penalty_applied: bool
    penalty_amount: Decimal
    final_amount: Decimal
    timestamp: datetime


class StakingManager:
    """
    Manages token staking with time-weighted voting power.

    Features:
    - Multiple lock period options
    - Time-weighted voting power multipliers
    - Penalty for early unstaking
    - Participation bonuses
    - Automatic reward accumulation

    Example:
        staking = StakingManager()

        # Stake with 30-day lock
        await staking.stake(wallet, amount=1000, lock_days=30)

        # Check voting power
        power = await staking.calculate_voting_power(wallet)

        # Unstake after lock period
        await staking.unstake(wallet, amount=500)
    """

    # Lock period multipliers
    MULTIPLIERS = {
        0: 1.0,      # No lock
        7: 1.2,      # 1 week
        30: 1.5,     # 1 month
        90: 2.0,     # 3 months
        180: 3.0,    # 6 months
    }

    # Staking parameters
    MIN_STAKE = 100              # Minimum 100 ACT
    MAX_STAKE = 10_000_000       # Max 10M ACT (1% of supply)
    UNSTAKE_PENALTY = 0.10       # 10% penalty for force unstake
    PARTICIPATION_BOOST = 0.10   # 10% boost for active participation

    def __init__(
        self,
        token_manager=None,
        network: str = "devnet"
    ):
        """
        Initialize Staking Manager.

        Args:
            token_manager: TokenManager instance (optional)
            network: Solana network
        """
        self.network = network
        self.token_manager = token_manager

        # Mock mode
        self.mock_mode = os.getenv('SOLANA_MOCK_MODE', 'true').lower() == 'true'

        # Mock storage
        if self.mock_mode:
            logger.warning("Staking Manager running in MOCK MODE")
            self._stakes: Dict[str, StakeInfo] = {}
            self._total_staked = Decimal(0)
            self._total_voting_power = Decimal(0)
        else:
            logger.info(f"Staking Manager initialized on {network}")

    async def stake(
        self,
        wallet: str,
        amount: Decimal,
        lock_days: int = 0
    ) -> StakeInfo:
        """
        Stake tokens with optional lock period.

        Args:
            wallet: Wallet address
            amount: Amount to stake
            lock_days: Lock period in days (0, 7, 30, 90, 180)

        Returns:
            StakeInfo: Stake information

        Example:
            stake = await staking.stake(wallet, Decimal(1000), lock_days=30)
        """
        # Validate amount
        if amount < self.MIN_STAKE:
            raise ValueError(f"Minimum stake is {self.MIN_STAKE} ACT")

        if amount > self.MAX_STAKE:
            raise ValueError(f"Maximum stake is {self.MAX_STAKE} ACT")

        # Validate lock period
        if lock_days not in self.MULTIPLIERS:
            raise ValueError(f"Invalid lock period. Must be one of: {list(self.MULTIPLIERS.keys())}")

        # Check if wallet has sufficient balance
        if self.token_manager:
            balance = await self.token_manager.get_balance(wallet)
            if balance < amount:
                raise ValueError(f"Insufficient balance: {balance} < {amount}")

        stake_timestamp = datetime.now()
        unlock_timestamp = stake_timestamp + timedelta(days=lock_days)
        time_multiplier = self.MULTIPLIERS[lock_days]
        voting_power = amount * Decimal(time_multiplier)

        if self.mock_mode:
            # Get existing stake or create new
            if wallet in self._stakes:
                existing = self._stakes[wallet]
                # Add to existing stake
                new_amount = existing.amount + amount
                new_voting_power = new_amount * Decimal(time_multiplier)

                stake_info = StakeInfo(
                    wallet=wallet,
                    amount=new_amount,
                    stake_timestamp=stake_timestamp,
                    lock_days=max(lock_days, existing.lock_days),  # Use longer lock
                    unlock_timestamp=max(unlock_timestamp, existing.unlock_timestamp),
                    time_multiplier=time_multiplier,
                    voting_power=new_voting_power,
                    rewards_earned=existing.rewards_earned,
                    participation_boost=existing.participation_boost,
                    is_locked=(unlock_timestamp > datetime.now())
                )
            else:
                stake_info = StakeInfo(
                    wallet=wallet,
                    amount=amount,
                    stake_timestamp=stake_timestamp,
                    lock_days=lock_days,
                    unlock_timestamp=unlock_timestamp,
                    time_multiplier=time_multiplier,
                    voting_power=voting_power,
                    rewards_earned=Decimal(0),
                    participation_boost=0.0,
                    is_locked=(lock_days > 0)
                )

            self._stakes[wallet] = stake_info
            self._total_staked += amount
            self._total_voting_power += voting_power

            logger.info(f"Staked {amount} ACT for {wallet} with {lock_days}d lock (multiplier: {time_multiplier}x)")

            return stake_info

        # TODO: Implement real on-chain staking
        raise NotImplementedError("Real staking not implemented")

    async def unstake(
        self,
        wallet: str,
        amount: Decimal,
        force: bool = False
    ) -> UnstakeInfo:
        """
        Unstake tokens.

        Args:
            wallet: Wallet address
            amount: Amount to unstake
            force: Force unstake before lock period (applies penalty)

        Returns:
            UnstakeInfo: Unstake details with penalty info

        Example:
            # Normal unstake (after lock period)
            info = await staking.unstake(wallet, Decimal(500))

            # Force unstake (10% penalty)
            info = await staking.unstake(wallet, Decimal(500), force=True)
        """
        if self.mock_mode:
            if wallet not in self._stakes:
                raise ValueError(f"No stake found for wallet {wallet}")

            stake = self._stakes[wallet]

            if amount > stake.amount:
                raise ValueError(f"Unstake amount exceeds staked: {amount} > {stake.amount}")

            # Check if locked
            now = datetime.now()
            is_locked = now < stake.unlock_timestamp

            penalty_applied = False
            penalty_amount = Decimal(0)
            final_amount = amount

            if is_locked and not force:
                raise ValueError(
                    f"Stake is locked until {stake.unlock_timestamp}. "
                    f"Use force=True to unstake with {self.UNSTAKE_PENALTY * 100}% penalty"
                )

            if is_locked and force:
                # Apply penalty
                penalty_applied = True
                penalty_amount = amount * Decimal(self.UNSTAKE_PENALTY)
                final_amount = amount - penalty_amount

                logger.warning(
                    f"Force unstake penalty applied: {penalty_amount} ACT "
                    f"({self.UNSTAKE_PENALTY * 100}%)"
                )

            # Update stake
            stake.amount -= amount
            stake.voting_power = stake.amount * Decimal(stake.time_multiplier)

            # Update totals
            self._total_staked -= amount
            self._total_voting_power -= (amount * Decimal(stake.time_multiplier))

            # Remove stake if fully unstaked
            if stake.amount == 0:
                del self._stakes[wallet]

            unstake_info = UnstakeInfo(
                wallet=wallet,
                amount=amount,
                penalty_applied=penalty_applied,
                penalty_amount=penalty_amount,
                final_amount=final_amount,
                timestamp=now
            )

            logger.info(f"Unstaked {amount} ACT for {wallet}, received {final_amount} ACT")

            return unstake_info

        raise NotImplementedError("Real unstaking not implemented")

    async def get_stake_info(self, wallet: str) -> Optional[StakeInfo]:
        """
        Get stake information for a wallet.

        Args:
            wallet: Wallet address

        Returns:
            Optional[StakeInfo]: Stake info if exists

        Example:
            stake = await staking.get_stake_info(wallet)
            if stake:
                print(f"Voting power: {stake.voting_power}")
        """
        if self.mock_mode:
            return self._stakes.get(wallet)

        raise NotImplementedError("Real stake retrieval not implemented")

    async def calculate_voting_power(self, wallet: str) -> Decimal:
        """
        Calculate current voting power for a wallet.

        Args:
            wallet: Wallet address

        Returns:
            Decimal: Voting power

        Example:
            power = await staking.calculate_voting_power(wallet)
        """
        stake = await self.get_stake_info(wallet)

        if not stake:
            return Decimal(0)

        # Base voting power from stake
        voting_power = stake.voting_power

        # Apply participation boost if active
        if stake.participation_boost > 0:
            boost_amount = voting_power * Decimal(stake.participation_boost)
            voting_power += boost_amount

        return voting_power

    def get_time_multiplier(self, lock_days: int) -> float:
        """
        Get multiplier for a lock period.

        Args:
            lock_days: Lock period in days

        Returns:
            float: Multiplier value

        Example:
            multiplier = staking.get_time_multiplier(30)  # 1.5x
        """
        return self.MULTIPLIERS.get(lock_days, 1.0)

    async def get_total_staked(self) -> Decimal:
        """
        Get total amount staked across all users.

        Returns:
            Decimal: Total staked amount

        Example:
            total = await staking.get_total_staked()
        """
        if self.mock_mode:
            return self._total_staked

        raise NotImplementedError("Real total staked not implemented")

    async def get_total_voting_power(self) -> Decimal:
        """
        Get total voting power across all users.

        Returns:
            Decimal: Total voting power

        Example:
            total_power = await staking.get_total_voting_power()
        """
        if self.mock_mode:
            return self._total_voting_power

        raise NotImplementedError("Real total voting power not implemented")

    async def get_staking_ratio(self) -> float:
        """
        Get ratio of staked tokens to circulating supply.

        Returns:
            float: Staking ratio (0.0 to 1.0)

        Example:
            ratio = await staking.get_staking_ratio()
            print(f"Staking ratio: {ratio * 100}%")
        """
        if not self.token_manager:
            return 0.0

        circulating = await self.token_manager.get_circulating_supply()
        total_staked = await self.get_total_staked()

        if circulating == 0:
            return 0.0

        return float(total_staked / circulating)

    async def apply_participation_boost(
        self,
        wallet: str,
        boost: float = PARTICIPATION_BOOST
    ) -> StakeInfo:
        """
        Apply participation boost to a user's stake.

        Args:
            wallet: Wallet address
            boost: Boost percentage (default 10%)

        Returns:
            StakeInfo: Updated stake info

        Example:
            # Reward active participant with 10% boost
            stake = await staking.apply_participation_boost(wallet)
        """
        if self.mock_mode:
            if wallet not in self._stakes:
                raise ValueError(f"No stake found for wallet {wallet}")

            stake = self._stakes[wallet]
            stake.participation_boost = boost

            logger.info(f"Applied {boost * 100}% participation boost to {wallet}")

            return stake

        raise NotImplementedError("Real participation boost not implemented")

    async def get_all_stakes(self) -> List[StakeInfo]:
        """
        Get all active stakes.

        Returns:
            List[StakeInfo]: All stakes

        Example:
            stakes = await staking.get_all_stakes()
            for stake in stakes:
                print(f"{stake.wallet}: {stake.amount} ACT")
        """
        if self.mock_mode:
            return list(self._stakes.values())

        raise NotImplementedError("Real stake listing not implemented")

    async def calculate_average_lock_period(self) -> float:
        """
        Calculate average lock period across all stakes.

        Returns:
            float: Average lock period in days

        Example:
            avg_lock = await staking.calculate_average_lock_period()
        """
        if self.mock_mode:
            if not self._stakes:
                return 0.0

            total_weighted_lock = 0.0
            total_amount = Decimal(0)

            for stake in self._stakes.values():
                total_weighted_lock += float(stake.amount) * stake.lock_days
                total_amount += stake.amount

            if total_amount == 0:
                return 0.0

            return total_weighted_lock / float(total_amount)

        raise NotImplementedError("Real average lock calculation not implemented")

    async def get_staking_stats(self) -> Dict[str, any]:
        """
        Get comprehensive staking statistics.

        Returns:
            Dict with staking metrics

        Example:
            stats = await staking.get_staking_stats()
            print(f"Total stakers: {stats['total_stakers']}")
        """
        stakes = await self.get_all_stakes()
        total_staked = await self.get_total_staked()
        total_voting_power = await self.get_total_voting_power()
        avg_lock = await self.calculate_average_lock_period()
        staking_ratio = await self.get_staking_ratio()

        return {
            "total_stakers": len(stakes),
            "total_staked": float(total_staked),
            "total_voting_power": float(total_voting_power),
            "average_lock_period_days": avg_lock,
            "staking_ratio": staking_ratio,
            "stakes_by_lock_period": self._get_stakes_by_lock_period(stakes)
        }

    def _get_stakes_by_lock_period(self, stakes: List[StakeInfo]) -> Dict[int, int]:
        """Count stakes by lock period."""
        distribution = {days: 0 for days in self.MULTIPLIERS.keys()}

        for stake in stakes:
            distribution[stake.lock_days] += 1

        return distribution
