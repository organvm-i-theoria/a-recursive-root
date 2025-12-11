# Blockchain Integration Module

**Status**: Phase 3 Implementation
**Version**: 0.3.0-alpha

---

## Overview

This module integrates blockchain technology into the AI Council System to provide:

- **Verifiable Randomness**: Using Chainlink VRF and Pyth Entropy for provably fair council selection
- **On-Chain Voting**: Immutable, transparent voting records on Solana blockchain
- **Token Economics**: Governance tokens, staking mechanisms, and reward distribution
- **Real-Time Data**: Price feeds and market data from Pyth Network

---

## Architecture

```
blockchain/
├── rng/                          # Random Number Generation
│   ├── chainlink_vrf.py         # Chainlink VRF provider
│   ├── pyth_entropy.py          # Pyth Entropy provider
│   ├── hybrid_rng.py            # Hybrid RNG coordinator
│   └── README.md
│
├── contracts/                    # Smart Contracts
│   ├── solana/                  # Solana programs
│   │   ├── council_selection/   # Agent selection contract
│   │   ├── voting/              # On-chain voting
│   │   └── staking/             # Token staking
│   └── README.md
│
├── token/                        # Token Mechanics
│   ├── token_manager.py         # Token operations
│   ├── staking.py               # Staking logic
│   ├── rewards.py               # Reward distribution
│   └── README.md
│
├── integrations/                 # Blockchain Clients
│   ├── solana_client.py         # Solana connection
│   ├── web3_provider.py         # Web3 provider
│   └── README.md
│
└── __init__.py
```

---

## Quick Start

### Installation

```bash
# Install blockchain dependencies
pip install solana anchorpy solders base58 web3 eth-account

# Install Solana CLI (for development)
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

# Install Anchor framework (for smart contracts)
cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

Required environment variables:

```bash
# Enable blockchain features
BLOCKCHAIN_ENABLED=true
BLOCKCHAIN_NETWORK=devnet

# Solana
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_WALLET_PRIVATE_KEY=your_private_key

# Chainlink VRF
CHAINLINK_VRF_COORDINATOR=0x...
CHAINLINK_VRF_KEY_HASH=0x...

# Pyth Network
PYTH_NETWORK_ENDPOINT=https://xc-mainnet.pyth.network
```

### Basic Usage

```python
from blockchain.rng import HybridRNG
from blockchain.token import StakingManager

# Initialize blockchain RNG
rng = HybridRNG(use_blockchain=True)

# Get verifiable random selection
selected_agents = await rng.get_random_selection(
    available_agents,
    count=5,
    use_blockchain=True
)

# Verify the selection on-chain
verification = await rng.verify_selection(selected_agents)
print(f"Selection verified: {verification.is_valid}")
print(f"VRF proof: {verification.proof}")

# Stake tokens for voting power
staking = StakingManager()
receipt = await staking.stake_tokens(
    user_wallet="your_wallet_address",
    amount=1000
)
print(f"Staked {receipt.amount} tokens")
print(f"Voting power: {receipt.voting_power}")
```

---

## Modules

### 1. RNG Module (`blockchain/rng/`)

Provides verifiable randomness for council selection and event prioritization.

**Key Classes**:
- `ChainlinkVRFProvider`: Chainlink VRF integration
- `PythEntropyProvider`: Pyth Entropy integration
- `HybridRNG`: Coordinator with automatic fallback

**Example**:
```python
from blockchain.rng import HybridRNG

rng = HybridRNG()

# Request verifiable random selection
selected = await rng.get_random_selection(
    options=available_agents,
    count=5,
    use_blockchain=True
)

# Get selection proof (for verification)
proof = await rng.get_selection_proof(selected)
```

See: [blockchain/rng/README.md](rng/README.md)

---

### 2. Contracts Module (`blockchain/contracts/`)

Smart contracts for on-chain operations.

**Solana Programs**:
- `council_selection`: Agent selection with VRF
- `voting`: On-chain vote recording and tallying
- `staking`: Token staking and reward distribution

**Example**:
```python
from blockchain.integrations import SolanaClient

client = SolanaClient()

# Record selection on-chain
tx = await client.record_council_selection(
    session_id="debate_123",
    selected_agents=agent_ids,
    vrf_proof=proof
)

print(f"Recorded on-chain: {tx.signature}")
```

See: [blockchain/contracts/README.md](contracts/README.md)

---

### 3. Token Module (`blockchain/token/`)

Token economics, staking, and rewards.

**Key Classes**:
- `TokenManager`: Token operations and transfers
- `StakingManager`: Stake/unstake with voting power calculation
- `RewardsDistributor`: Reward distribution logic

**Example**:
```python
from blockchain.token import StakingManager

staking = StakingManager()

# Stake tokens
await staking.stake_tokens(wallet, 1000)

# Check voting power
power = staking.calculate_voting_power(wallet)
print(f"Voting power: {power}")

# Unstake (with timelock)
await staking.unstake_tokens(wallet, 500)
```

See: [blockchain/token/README.md](token/README.md)

---

### 4. Integrations Module (`blockchain/integrations/`)

Blockchain client connections.

**Key Classes**:
- `SolanaClient`: Solana RPC client wrapper
- `Web3Provider`: Ethereum/Web3 provider (future)

**Example**:
```python
from blockchain.integrations import SolanaClient

client = SolanaClient(network='devnet')

# Check connection
is_connected = await client.is_connected()
print(f"Connected to Solana: {is_connected}")

# Get balance
balance = await client.get_balance(wallet_address)
print(f"Balance: {balance} SOL")
```

See: [blockchain/integrations/README.md](integrations/README.md)

---

## Integration with Existing System

### Council Selection

**Before (Phase 2)**:
```python
from core.council import CouncilManager

council_mgr = CouncilManager()
agents = await council_mgr.form_council(size=5)
```

**After (Phase 3)**:
```python
from core.council import CouncilManager
from blockchain.rng import HybridRNG

# Initialize with blockchain RNG
council_mgr = CouncilManager(rng_provider=HybridRNG())

# Form council with verifiable randomness
agents = await council_mgr.form_council(
    size=5,
    use_blockchain=True  # Use Chainlink VRF
)

# Get verification proof
proof = await council_mgr.get_selection_proof()
```

### Voting

**Before (Phase 2)**:
```python
from core.council import DebateSessionManager

session = DebateSessionManager(...)
votes = await session.collect_votes()
outcome = session.tally_votes(votes)
```

**After (Phase 3)**:
```python
from core.council import DebateSessionManager

session = DebateSessionManager(
    ...,
    record_votes_on_chain=True
)

# Votes automatically recorded on-chain
votes = await session.collect_votes()

# Tally with on-chain verification
outcome = await session.tally_votes(votes)

# Get on-chain receipt
receipt = await session.get_vote_receipt()
print(f"Votes recorded at: {receipt.block_height}")
```

---

## Security Considerations

### Private Key Management

**Never commit private keys!**

Use one of these methods:
1. Environment variables (development)
2. Hardware wallets (production)
3. Key management services (AWS KMS, HashiCorp Vault)

```python
# Good: Load from environment
import os
private_key = os.getenv('SOLANA_WALLET_PRIVATE_KEY')

# Bad: Hardcoded in code
private_key = "abc123..."  # NEVER DO THIS
```

### RNG Verification

Always verify VRF proofs:

```python
from blockchain.rng import ChainlinkVRFProvider

vrf = ChainlinkVRFProvider()

# Get random number
random_num = await vrf.get_random_number(request_id)

# CRITICAL: Verify before using
if not vrf.verify_randomness(request_id, random_num):
    raise ValueError("VRF proof invalid!")

# Safe to use
selected_index = random_num % len(options)
```

### Smart Contract Security

- All contracts undergo professional audit before mainnet
- Formal verification for critical functions
- Gradual rollout: devnet → testnet → mainnet
- Emergency pause mechanisms

---

## Testing

### Unit Tests

```bash
# Test RNG providers
pytest tests/blockchain/test_rng.py -v

# Test smart contracts
pytest tests/blockchain/test_contracts.py -v

# Test token mechanics
pytest tests/blockchain/test_token.py -v
```

### Integration Tests

```bash
# Full blockchain integration
pytest tests/integration/test_blockchain_integration.py -v
```

### Load Tests

```bash
# High-volume voting test
pytest tests/load/test_blockchain_performance.py -v
```

---

## Deployment

### Devnet (Development)

```bash
# Set network to devnet
export BLOCKCHAIN_NETWORK=devnet
export SOLANA_RPC_URL=https://api.devnet.solana.com

# Deploy contracts
cd blockchain/contracts/solana
anchor build
anchor deploy
```

### Testnet (Staging)

```bash
# Set network to testnet
export BLOCKCHAIN_NETWORK=testnet
export SOLANA_RPC_URL=https://api.testnet.solana.com

# Run full test suite
pytest tests/ -v

# Deploy
anchor deploy --provider.cluster testnet
```

### Mainnet (Production)

```bash
# IMPORTANT: Complete security audit first!

# Set network to mainnet
export BLOCKCHAIN_NETWORK=mainnet
export SOLANA_RPC_URL=https://api.mainnet-beta.solana.com

# Use hardware wallet
# Double-check all configurations
# Deploy with caution
anchor deploy --provider.cluster mainnet
```

---

## Monitoring

### Key Metrics

Track these metrics in production:

```python
from blockchain.integrations import SolanaClient

client = SolanaClient()

# RPC connection health
latency = await client.get_latency()
is_healthy = await client.health_check()

# Transaction success rate
success_rate = await client.get_tx_success_rate()

# Gas costs
avg_cost = await client.get_average_tx_cost()
```

### Alerts

Set up alerts for:
- RPC connection failures
- Transaction failures >1%
- Unusual gas costs
- VRF request timeouts
- Smart contract errors

---

## Troubleshooting

### Connection Issues

```python
# Test Solana connection
from blockchain.integrations import SolanaClient

client = SolanaClient()
health = await client.health_check()

if not health.is_healthy:
    print(f"Connection issue: {health.error}")
    print("Check your RPC URL and network connectivity")
```

### VRF Not Fulfilling

```python
# Check VRF request status
from blockchain.rng import ChainlinkVRFProvider

vrf = ChainlinkVRFProvider()
status = await vrf.get_request_status(request_id)

print(f"Status: {status.state}")
print(f"Confirmations: {status.confirmations}")

# If stuck, check:
# 1. VRF subscription funded?
# 2. Gas price too low?
# 3. Request expired?
```

### Transaction Failing

```python
# Get detailed error
try:
    tx = await client.send_transaction(...)
except Exception as e:
    print(f"Transaction failed: {e}")
    print(f"Logs: {e.logs}")

# Common issues:
# - Insufficient balance
# - Invalid account
# - Program error
# - Network congestion
```

---

## Performance

### Expected Latencies

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Chainlink VRF Request | 2-5 seconds | Depends on network |
| Pyth Entropy | <1 second | Direct on-chain |
| Solana Transaction | 0.4-1 second | Single confirmation |
| Vote Recording | <2 seconds | Including confirmation |
| Token Staking | <2 seconds | Single transaction |

### Gas Costs (Solana)

| Operation | Typical Cost | Notes |
|-----------|--------------|-------|
| Council Selection | ~0.000005 SOL | ~$0.0001 |
| Vote Recording | ~0.000005 SOL | ~$0.0001 |
| Token Transfer | ~0.000005 SOL | ~$0.0001 |
| Staking | ~0.00001 SOL | ~$0.0002 |

---

## Roadmap

### Phase 3.1: RNG Integration (Week 1) ✅
- Chainlink VRF provider
- Pyth Entropy provider
- Hybrid RNG coordinator
- Council selection integration

### Phase 3.2: Smart Contracts (Week 2) ⏳
- Solana council selection program
- On-chain voting program
- Contract deployment

### Phase 3.3: Token Mechanics (Week 3) ⏳
- Token creation
- Staking implementation
- Reward distribution

### Phase 3.4: Integration (Week 4) ⏳
- Full system integration
- Testing and auditing
- Documentation finalization

---

## Resources

### Documentation
- [Solana Documentation](https://docs.solana.com)
- [Anchor Framework](https://www.anchor-lang.com)
- [Chainlink VRF](https://docs.chain.link/vrf)
- [Pyth Network](https://docs.pyth.network)

### Tools
- [Solana Explorer](https://explorer.solana.com)
- [Anchor Playground](https://beta.solpg.io)
- [Solana CLI](https://docs.solana.com/cli)

### Community
- [Solana Discord](https://discord.gg/solana)
- [Anchor Discord](https://discord.gg/anchor)
- [Chainlink Discord](https://discord.gg/chainlink)

---

## License

MIT License - See LICENSE file for details

---

**Phase 3 Status**: 🚧 In Progress

**Next**: Implement RNG providers (Chainlink VRF, Pyth Entropy)
