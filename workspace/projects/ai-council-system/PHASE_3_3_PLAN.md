# Phase 3.3: Token Mechanics - Implementation Plan

**Date**: October 24, 2025
**Status**: In Progress
**Target**: Complete token economics system with staking and rewards

---

## Overview

Phase 3.3 implements the token economics layer for the AI Council System, enabling:
- **Governance Token**: SPL token for platform participation
- **Staking Mechanism**: Lock tokens for voting power and rewards
- **Reward Distribution**: Automated reward allocation for participants
- **Token-Weighted Voting**: Voting power based on staked tokens
- **Governance System**: Community-driven decision making

---

## Token Economics Design

### Token Specifications

```yaml
Token Name: AI Council Token (ACT)
Symbol: ACT
Decimals: 9
Total Supply: 1,000,000,000 ACT (1 billion)
Chain: Solana (SPL Token)

Distribution:
  - Community Rewards: 40% (400M)
  - Team & Development: 20% (200M)
  - Treasury/DAO: 20% (200M)
  - Initial Liquidity: 10% (100M)
  - Ecosystem Partners: 10% (100M)
```

### Staking Model

**Time-Weighted Voting Power**:
```
voting_power = staked_amount * time_multiplier

time_multiplier:
  - 0-7 days: 1.0x
  - 7-30 days: 1.2x
  - 30-90 days: 1.5x
  - 90-180 days: 2.0x
  - 180+ days: 3.0x
```

**Lock Periods**:
- No lock: Unstake anytime (1.0x multiplier)
- 7 days: 1.2x multiplier
- 30 days: 1.5x multiplier
- 90 days: 2.0x multiplier
- 180 days: 3.0x multiplier

**Unstaking**:
- Immediate unstake: Forfeit 10% penalty
- Wait lock period: No penalty
- Rewards continue during lock period

### Reward System

**Reward Sources**:
1. Platform fees (debate participation fees)
2. Token inflation (max 5% annual)
3. Governance treasury allocations

**Reward Distribution**:
```python
user_reward = total_rewards * (user_voting_power / total_voting_power)
```

**Reward Frequency**:
- Daily snapshots of voting power
- Weekly reward distribution
- Compounding available (auto-stake rewards)

**Reward Boosters**:
- Active participation: +10%
- Long-term staking: +20%
- Governance voting: +15%

### Governance

**Proposal Types**:
1. Parameter changes (voting thresholds, rewards, etc.)
2. Treasury spending
3. Protocol upgrades
4. New feature activation

**Voting Requirements**:
- Minimum stake: 1,000 ACT
- Quorum: 10% of total voting power
- Approval: 66% of votes
- Voting period: 7 days
- Timelock: 3 days after approval

---

## Architecture

```
blockchain/token/
├── __init__.py
├── README.md
├── token_manager.py          # Token operations
├── staking.py                 # Staking mechanism
├── rewards.py                 # Reward distribution
├── governance.py              # Governance system
└── economics.py               # Economic calculations

blockchain/contracts/solana/
└── staking/                   # Staking smart contract
    ├── Cargo.toml
    └── src/
        └── lib.rs

examples/
└── token_demo.py              # Token mechanics demo

tests/blockchain/
├── test_token_manager.py
├── test_staking.py
└── test_rewards.py
```

---

## Implementation Details

### 1. Token Manager

**Responsibilities**:
- SPL token creation and minting
- Token transfers
- Balance checking
- Supply management
- Burn operations

**Key Functions**:
```python
class TokenManager:
    async def create_token(name, symbol, decimals, supply)
    async def mint_tokens(recipient, amount)
    async def transfer(from_wallet, to_wallet, amount)
    async def burn(wallet, amount)
    async def get_balance(wallet)
    async def get_total_supply()
```

### 2. Staking Manager

**Responsibilities**:
- Stake token operations
- Lock period enforcement
- Voting power calculation
- Unstaking with penalty/timelock

**Key Functions**:
```python
class StakingManager:
    async def stake(wallet, amount, lock_days)
    async def unstake(wallet, amount, force=False)
    async def get_stake_info(wallet)
    async def calculate_voting_power(wallet)
    async def get_time_multiplier(stake_timestamp, lock_days)
    async def apply_unstake_penalty(wallet, amount)
```

### 3. Rewards Distributor

**Responsibilities**:
- Calculate rewards per user
- Distribute rewards
- Track reward history
- Apply boosters

**Key Functions**:
```python
class RewardsDistributor:
    async def calculate_user_reward(wallet, total_rewards)
    async def distribute_rewards(reward_pool)
    async def get_reward_history(wallet)
    async def calculate_boosters(wallet)
    async def claim_rewards(wallet)
```

### 4. Governance System

**Responsibilities**:
- Create proposals
- Vote on proposals
- Execute approved proposals
- Track voting history

**Key Functions**:
```python
class GovernanceManager:
    async def create_proposal(title, description, proposal_type)
    async def vote_on_proposal(proposal_id, vote, voting_power)
    async def check_quorum(proposal_id)
    async def execute_proposal(proposal_id)
    async def get_proposal_status(proposal_id)
```

---

## Smart Contract: Staking Program

### Program Structure

```rust
#[program]
pub mod staking {
    // Initialize staking pool
    pub fn initialize_pool(
        total_supply: u64,
        reward_rate: u64,
    ) -> Result<()>

    // Stake tokens
    pub fn stake(
        amount: u64,
        lock_days: u32,
    ) -> Result<()>

    // Unstake tokens
    pub fn unstake(
        amount: u64,
        force: bool,
    ) -> Result<()>

    // Claim rewards
    pub fn claim_rewards() -> Result<()>

    // Calculate voting power
    pub fn get_voting_power(
        user: Pubkey,
    ) -> Result<u64>
}

#[account]
pub struct StakingPool {
    pub authority: Pubkey,
    pub token_mint: Pubkey,
    pub total_staked: u64,
    pub total_voting_power: u64,
    pub reward_rate: u64,
    pub last_update: i64,
}

#[account]
pub struct UserStake {
    pub owner: Pubkey,
    pub amount: u64,
    pub stake_timestamp: i64,
    pub lock_days: u32,
    pub rewards_earned: u64,
    pub voting_power: u64,
}
```

### Account Relationships

```
StakingPool (PDA)
    ├─ Token Vault (Associated Token Account)
    │  └─ Holds all staked tokens
    │
    └─ User Stakes (PDAs, seeds: [b"stake", user_pubkey])
       ├─ UserStake for User A
       ├─ UserStake for User B
       └─ UserStake for User C
```

---

## Integration with Existing System

### 1. Token-Weighted Voting

Update voting program to consider voting power:

```python
# Before (Phase 3.2)
async def cast_vote(debate_id, agent_id, vote_option):
    # Each vote has equal weight
    pass

# After (Phase 3.3)
async def cast_vote(debate_id, agent_id, vote_option, wallet):
    # Get voting power from staking
    voting_power = await staking.calculate_voting_power(wallet)

    # Weight vote by voting power
    weighted_vote = vote_option * voting_power

    # Record on-chain
    await voting_client.cast_weighted_vote(
        debate_id, agent_id, vote_option, voting_power
    )
```

### 2. Reward AI Agents

Distribute rewards to AI agents based on participation:

```python
async def distribute_agent_rewards(session_id):
    # Get all participating agents
    session = await council_client.get_session(session_id)
    agents = session.selected_agents

    # Calculate rewards based on contribution
    total_pool = calculate_session_reward_pool()

    for agent in agents:
        # Agents earn based on quality and participation
        agent_share = calculate_agent_contribution(agent, session)
        reward = total_pool * agent_share

        # Distribute to agent wallet
        await rewards.distribute(agent.wallet, reward)
```

### 3. Staking Requirements

Add staking requirements for participation:

```python
async def form_council(topic, size=5):
    # Check if user has minimum stake
    user_stake = await staking.get_stake_info(user_wallet)

    if user_stake.amount < MIN_STAKE_FOR_COUNCIL:
        raise ValueError(f"Minimum stake required: {MIN_STAKE_FOR_COUNCIL} ACT")

    # Form council as normal
    council = await council_manager.form_council(size)

    # User's voting power affects outcome weight
    user_voting_power = await staking.calculate_voting_power(user_wallet)

    return council, user_voting_power
```

---

## Testing Strategy

### Unit Tests

```python
# test_token_manager.py
async def test_create_token()
async def test_mint_tokens()
async def test_transfer()
async def test_burn()

# test_staking.py
async def test_stake_tokens()
async def test_unstake_tokens()
async def test_voting_power_calculation()
async def test_time_multiplier()
async def test_unstake_penalty()

# test_rewards.py
async def test_reward_calculation()
async def test_reward_distribution()
async def test_reward_boosters()
async def test_claim_rewards()
```

### Integration Tests

```python
async def test_full_staking_cycle():
    # 1. Stake tokens
    # 2. Wait for lock period
    # 3. Participate in governance
    # 4. Earn rewards
    # 5. Claim rewards
    # 6. Unstake tokens

async def test_token_weighted_voting():
    # 1. Multiple users stake different amounts
    # 2. Cast votes with different voting power
    # 3. Verify outcome weighted correctly

async def test_reward_distribution():
    # 1. Multiple stakers
    # 2. Different lock periods
    # 3. Distribute rewards
    # 4. Verify proportional distribution
```

---

## Security Considerations

### 1. Reentrancy Protection

```rust
// Prevent reentrancy attacks in unstake
#[account(mut)]
pub user_stake: Account<'info, UserStake>,

// Update state before transfer
user_stake.amount -= amount;
user_stake.voting_power = calculate_voting_power(user_stake);

// Then transfer tokens
token::transfer(ctx, amount)?;
```

### 2. Integer Overflow Protection

```rust
// Use checked math
let new_total = total_staked
    .checked_add(amount)
    .ok_or(ErrorCode::MathOverflow)?;
```

### 3. Access Control

```rust
// Only stake owner can unstake
require!(
    user_stake.owner == ctx.accounts.user.key(),
    ErrorCode::Unauthorized
);
```

### 4. Time Manipulation Protection

```rust
// Use on-chain clock
let current_time = Clock::get()?.unix_timestamp;
require!(
    current_time >= user_stake.unlock_time,
    ErrorCode::StillLocked
);
```

---

## Economic Parameters

### Initial Configuration

```yaml
Staking:
  min_stake: 100 ACT
  max_stake: 10,000,000 ACT (1% of supply)
  lock_periods: [0, 7, 30, 90, 180] # days
  unstake_penalty: 10% # for immediate unstake

Rewards:
  annual_inflation: 5% # max
  distribution_frequency: 7 # days
  min_claim_amount: 1 ACT
  auto_compound: true # optional

Governance:
  min_proposal_stake: 10,000 ACT
  quorum: 10% # of total voting power
  approval_threshold: 66% # of votes
  voting_period: 7 # days
  timelock: 3 # days

Boosters:
  active_participation: 10%
  long_term_staking: 20%
  governance_voting: 15%
```

### Tokenomics Model

```
Year 1:
  - Circulating: 500M ACT (50% of supply)
  - Staked: 200M ACT (40% of circulating)
  - Rewards: 50M ACT (5% inflation)

Year 2:
  - Circulating: 600M ACT
  - Staked: 300M ACT (50% of circulating)
  - Rewards: 30M ACT (3% inflation)

Year 3+:
  - Inflation reduces to 2% annually
  - Sustainable long-term model
```

---

## Deployment Plan

### Phase 1: Token Creation
1. Deploy SPL token contract
2. Mint initial supply to treasury
3. Set up token accounts

### Phase 2: Staking Deployment
1. Deploy staking program
2. Initialize staking pool
3. Fund reward pool

### Phase 3: Integration
1. Update voting contracts
2. Deploy governance contracts
3. Integrate with council system

### Phase 4: Testing
1. Devnet testing (2 weeks)
2. Testnet beta (4 weeks)
3. Security audit
4. Mainnet deployment

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Staking Ratio | >40% | Staked / Circulating Supply |
| Active Stakers | >1,000 | Unique staker addresses |
| Avg Lock Period | >30 days | Weighted average |
| Governance Participation | >20% | Voters / Eligible |
| Reward Claims | >80% | Claims / Eligible |
| TVL (Total Value Locked) | >$1M | Staked value in USD |

---

## Risks and Mitigation

### Risk 1: Low Staking Participation
**Mitigation**:
- Attractive APY (15-30%)
- Progressive multipliers
- Additional boosters
- Community incentives

### Risk 2: Token Price Volatility
**Mitigation**:
- Gradual unlocks
- Buyback mechanism
- Treasury stabilization
- Diverse liquidity pools

### Risk 3: Smart Contract Vulnerabilities
**Mitigation**:
- Professional audit
- Bug bounty program
- Gradual rollout
- Emergency pause function

### Risk 4: Whale Manipulation
**Mitigation**:
- Max stake limits (1% of supply)
- Voting power caps
- Time-weighted power
- Quadratic voting option

---

## Phase 3.3 Completion Criteria

- ✅ Token manager implemented
- ✅ Staking mechanism functional
- ✅ Reward distribution automated
- ✅ Governance system operational
- ✅ Staking smart contract deployed
- ✅ Integration with voting system
- ✅ Comprehensive tests passing
- ✅ Documentation complete
- ✅ Demo application functional
- ✅ Security review completed

---

**Next**: Begin implementation of token economics system

Let's build! 🚀
