"""Economics Calculator for tokenomics modeling."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class TokenomicsModel:
    year: int
    circulating_supply: Decimal
    staked: Decimal
    staking_ratio: float
    rewards_distributed: Decimal
    inflation_rate: float
    average_apy: float


class EconomicsCalculator:
    TOTAL_SUPPLY = Decimal(1_000_000_000)

    def __init__(self):
        self.models = []

    def project_year(self, year: int, staking_ratio: float = 0.4, inflation: float = 0.05) -> TokenomicsModel:
        circulating = self.TOTAL_SUPPLY * Decimal(0.5 + (year * 0.1))
        staked = circulating * Decimal(staking_ratio)
        rewards = circulating * Decimal(inflation)

        model = TokenomicsModel(
            year=year,
            circulating_supply=circulating,
            staked=staked,
            staking_ratio=staking_ratio,
            rewards_distributed=rewards,
            inflation_rate=inflation,
            average_apy=(inflation / staking_ratio * 100) if staking_ratio > 0 else 0
        )

        self.models.append(model)
        return model

    def calculate_sustainable_apy(self, staking_ratio: float, inflation: float) -> float:
        if staking_ratio == 0:
            return 0.0
        return (inflation / staking_ratio) * 100
