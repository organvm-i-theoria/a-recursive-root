# Token Economics Module

**Status**: Phase 3.3 Complete
**Version**: 0.3.3-alpha

---

## Overview

Complete token economics system for the AI Council platform featuring:
- **AI Council Token (ACT)**: SPL governance token
- **Time-Weighted Staking**: Lock periods with voting power multipliers
- **Automated Rewards**: Weekly distribution with boosters
- **Governance System**: Proposal creation and weighted voting
- **Economic Modeling**: Sustainability projections

---

## Quick Start

```python
from blockchain.token import TokenManager, StakingManager, RewardsDistributor

# Create token
token_mgr = TokenManager()
token = await token_mgr.create_token("AI Council Token", "ACT", 9, 1_000_000_000)

# Stake tokens (30-day lock = 1.5x multiplier)
staking = StakingManager(token_mgr)
stake = await staking.stake(wallet, amount=1000, lock_days=30)

# Distribute rewards
rewards = RewardsDistributor(staking)
results = await rewards.distribute_rewards(reward_pool=10000)
```

---

## Token Specifications

| Property | Value |
|----------|-------|
| **Name** | AI Council Token |
| **Symbol** | ACT |
| **Decimals** | 9 |
| **Total Supply** | 1,000,000,000 ACT |
| **Chain** | Solana (SPL Token) |

### Distribution
- Community Rewards: 40% (400M)
- Team & Development: 20% (200M)
- Treasury/DAO: 20% (200M)
- Initial Liquidity: 10% (100M)
- Ecosystem Partners: 10% (100M)

---

## Modules

### 1. TokenManager (`token_manager.py`)

SPL token operations and management.

```python
token_mgr = TokenManager()

# Create token
token = await token_mgr.create_token("AI Council Token", "ACT", 9, 1_000_000_000)

# Mint to address
await token_mgr.mint_tokens(recipient, 1000)

# Transfer
await token_mgr.transfer(from_wallet, to_wallet, 500)

# Check balance
balance = await token_mgr.get_balance(wallet)
```

### 2. StakingManager (`staking.py`)

Time-weighted staking with voting power.

**Lock Periods & Multipliers**:
- No lock (0 days): 1.0x
- 1 week (7 days): 1.2x
- 1 month (30 days): 1.5x
- 3 months (90 days): 2.0x
- 6 months (180 days): 3.0x

```python
staking = StakingManager(token_mgr)

# Stake with lock period
stake = await staking.stake(wallet, Decimal(1000), lock_days=30)
print(f"Voting power: {stake.voting_power}")  # 1000 * 1.5 = 1500

# Unstake after lock period
await staking.unstake(wallet, Decimal(500))

# Force unstake (10% penalty)
await staking.unstake(wallet, Decimal(500), force=True)
```

### 3. RewardsDistributor (`rewards.py`)

Automated reward distribution with boosters.

**Reward Boosters**:
- Active Participation: +10%
- Long-term Staking: +20%
- Governance Voting: +15%

```python
rewards = RewardsDistributor(staking, token_mgr)

# Apply boosters
await rewards.apply_booster(wallet, RewardBooster.ACTIVE_PARTICIPATION)

# Distribute weekly rewards
results = await rewards.distribute_rewards(reward_pool=Decimal(10000))

# Claim rewards
claimed = await rewards.claim_rewards(wallet, auto_stake=True, lock_days=30)
```

### 4. GovernanceManager (`governance.py`)

Proposal creation and voting.

**Parameters**:
- Min Proposal Stake: 10,000 ACT
- Quorum: 10% of voting power
- Approval: 66% of votes
- Voting Period: 7 days
- Timelock: 3 days

```python
governance = GovernanceManager(staking)

# Create proposal
proposal = await governance.create_proposal(
    wallet,
    "Increase rewards",
    "Proposal to increase staking rewards by 20%"
)

# Vote (weighted by voting power)
await governance.vote(proposal.proposal_id, wallet, VoteType.FOR)

# Finalize
status = await governance.finalize_proposal(proposal.proposal_id)
```

### 5. EconomicsCalculator (`economics.py`)

Tokenomics modeling and projections.

```python
economics = EconomicsCalculator()

# Project year 1
model = economics.project_year(year=1, staking_ratio=0.4, inflation=0.05)
print(f"Average APY: {model.average_apy}%")

# Calculate sustainable APY
apy = economics.calculate_sustainable_apy(staking_ratio=0.4, inflation=0.05)
```

---

## Complete Example

See `examples/token_demo.py` for a comprehensive demonstration:

```bash
cd workspace/projects/ai-council-system
python examples/token_demo.py
```

**Demo includes**:
1. Token creation and distribution
2. Multi-user staking with various lock periods
3. Reward distribution with boosters
4. Governance proposal and voting
5. Economic projections
6. Unstaking scenarios

---

## Economics

### Staking Formula

```
voting_power = staked_amount × time_multiplier × (1 + participation_boost)

time_multiplier:
  0 days:   1.0x
  7 days:   1.2x
  30 days:  1.5x
  90 days:  2.0x
  180 days: 3.0x
```

### Reward Formula

```
user_reward = total_rewards × (user_voting_power / total_voting_power)

With boosters:
  final_reward = base_reward × (1 + sum(active_boosters))

Max boosters: +45% (10% + 20% + 15%)
```

### APY Calculation

```
APY = (inflation_rate / staking_ratio) × 100

Example (40% staking, 5% inflation):
  APY = (0.05 / 0.40) × 100 = 12.5% base

With 3.0x multiplier and max boosters:
  Effective APY ≈ 54% (12.5% × 3.0 × 1.45)
```

---

## Integration with Council System

### Token-Weighted Voting

```python
# Get user's voting power
voting_power = await staking.calculate_voting_power(wallet)

# Cast weighted vote in debate
await voting_client.cast_vote(
    debate_id,
    agent_id,
    vote_option,
    voting_power  # Vote weight based on staked tokens
)
```

### Staking Requirements

```python
# Require minimum stake for council participation
MIN_STAKE_FOR_COUNCIL = Decimal(1000)

stake = await staking.get_stake_info(user_wallet)
if stake.amount < MIN_STAKE_FOR_COUNCIL:
    raise ValueError(f"Minimum {MIN_STAKE_FOR_COUNCIL} ACT stake required")
```

### Agent Rewards

```python
# Reward AI agents for participation
session_reward_pool = Decimal(1000)

for agent in participating_agents:
    contribution_share = calculate_agent_contribution(agent)
    reward = session_reward_pool * contribution_share

    await token_mgr.transfer(treasury_wallet, agent.wallet, reward)
```

---

## Testing

```bash
# Run token mechanics tests
pytest tests/blockchain/test_token_manager.py -v
pytest tests/blockchain/test_staking.py -v
pytest tests/blockchain/test_rewards.py -v

# Run integration tests
pytest tests/blockchain/test_token_integration.py -v
```

---

## Configuration

Add to `.env`:

```bash
# Token Configuration
TOKEN_MINT_ADDRESS=your_token_mint_address
STAKING_POOL_ADDRESS=your_staking_pool_address

# Economic Parameters
ANNUAL_INFLATION_RATE=0.05
DISTRIBUTION_FREQUENCY_DAYS=7
MIN_CLAIM_AMOUNT=1

# Governance
MIN_PROPOSAL_STAKE=10000
QUORUM_PERCENTAGE=0.10
APPROVAL_THRESHOLD=0.66
```

---

## API Reference

### TokenManager

| Method | Description |
|--------|-------------|
| `create_token()` | Create new SPL token |
| `mint_tokens()` | Mint to address |
| `transfer()` | Transfer between wallets |
| `burn()` | Burn tokens |
| `get_balance()` | Get wallet balance |
| `get_total_supply()` | Get total supply |
| `get_circulating_supply()` | Get circulating supply |

### StakingManager

| Method | Description |
|--------|-------------|
| `stake()` | Stake with lock period |
| `unstake()` | Unstake tokens |
| `get_stake_info()` | Get stake details |
| `calculate_voting_power()` | Calculate voting power |
| `get_total_staked()` | Total staked |
| `get_staking_ratio()` | Staking ratio |

### RewardsDistributor

| Method | Description |
|--------|-------------|
| `calculate_user_reward()` | Calculate user reward |
| `distribute_rewards()` | Distribute to all |
| `claim_rewards()` | Claim accumulated |
| `apply_booster()` | Apply reward booster |
| `calculate_apy()` | Calculate APY |

### GovernanceManager

| Method | Description |
|--------|-------------|
| `create_proposal()` | Create proposal |
| `vote()` | Vote on proposal |
| `finalize_proposal()` | Finalize and execute |

---

## Status

**Phase 3.3 Complete**: ✅ All token mechanics implemented and tested

**Next**: Integration with council voting and deployment to Solana

---

**Total Code**: ~1,500 lines across 7 modules
