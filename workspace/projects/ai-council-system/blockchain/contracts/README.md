# Smart Contracts Module

**Status**: Phase 3.2 Complete
**Version**: 0.3.0-alpha

---

## Overview

This module contains Solana smart contracts (programs) for the AI Council System. Written in Rust using the Anchor framework, these programs enable:

- **Verifiable Council Selection**: On-chain recording of agent selection with VRF proof
- **Transparent Voting**: Immutable vote recording and tallying
- **Proof Generation**: Cryptographic proofs for all council operations

---

## Architecture

```
blockchain/contracts/
├── solana/
│   ├── council_selection/        # Council selection program
│   │   ├── Cargo.toml
│   │   └── src/
│   │       └── lib.rs            # Main program (Anchor)
│   │
│   ├── voting/                    # On-chain voting program
│   │   ├── Cargo.toml
│   │   └── src/
│   │       └── lib.rs            # Main program (Anchor)
│   │
│   └── deployment/                # Deployment scripts
│       ├── Anchor.toml           # Anchor configuration
│       └── deploy.sh             # Deployment script
│
└── README.md                      # This file
```

---

## Programs

### 1. Council Selection Program

**Program ID**: `CounciL11111111111111111111111111111111111` (devnet)

**Purpose**: Record and verify council member selection with VRF randomness.

**Instructions**:

```rust
// Initialize a new council session
pub fn initialize_session(
    session_id: String,
    required_agents: u8,
    diversity_required: bool,
) -> Result<()>

// Request VRF for randomness
pub fn request_vrf(
    vrf_seed: u64,
) -> Result<()>

// Fulfill VRF with random number and proof
pub fn fulfill_vrf(
    random_number: u64,
    vrf_proof: Vec<u8>,
) -> Result<()>

// Record selected agents
pub fn select_agents(
    agent_ids: Vec<String>,
) -> Result<()>

// Verify selection is valid
pub fn verify_selection() -> Result<bool>
```

**Accounts**:

```rust
pub struct CouncilSession {
    pub session_id: String,           // Unique session identifier
    pub authority: Pubkey,             // Session authority
    pub required_agents: u8,           // Number of agents required
    pub diversity_required: bool,      // Diversity enforcement
    pub selected_agents: Vec<String>,  // Selected agent IDs
    pub vrf_seed: u64,                 // VRF seed
    pub vrf_fulfilled: bool,           // VRF fulfillment status
    pub random_number: u64,            // Random number from VRF
    pub vrf_proof: Vec<u8>,            // Cryptographic proof
    pub timestamp: i64,                // Creation timestamp
    pub selection_timestamp: i64,      // Selection timestamp
    pub status: SessionStatus,         // Current status
}
```

---

### 2. Voting Program

**Program ID**: `Voting11111111111111111111111111111111111` (devnet)

**Purpose**: Record and tally votes on-chain with transparency.

**Instructions**:

```rust
// Initialize a debate session
pub fn initialize_debate(
    debate_id: String,
    topic: String,
    max_rounds: u8,
) -> Result<()>

// Cast a vote
pub fn cast_vote(
    agent_id: String,
    vote_option: VoteOption,
    confidence: u8,
    reasoning: String,
) -> Result<()>

// Tally all votes
pub fn tally_votes() -> Result<()>

// Close debate (emergency)
pub fn close_debate() -> Result<()>

// Get vote results
pub fn get_results() -> Result<VoteResults>
```

**Accounts**:

```rust
pub struct Debate {
    pub debate_id: String,             // Unique debate identifier
    pub topic: String,                 // Debate topic
    pub authority: Pubkey,             // Debate authority
    pub max_rounds: u8,                // Maximum rounds
    pub current_round: u8,             // Current round
    pub votes: Vec<Vote>,              // All votes
    pub timestamp: i64,                // Creation timestamp
    pub completion_timestamp: i64,     // Completion timestamp
    pub status: DebateStatus,          // Current status
    pub outcome: Option<VoteOption>,   // Final outcome
    pub support_score: u16,            // Support score
    pub oppose_score: u16,             // Oppose score
    pub neutral_score: u16,            // Neutral score
    pub votes_tallied: bool,           // Tallied flag
}

pub struct Vote {
    pub agent_id: String,              // Voting agent
    pub vote_option: VoteOption,       // Vote choice
    pub confidence: u8,                // Confidence (0-100)
    pub reasoning: String,             // Vote reasoning
    pub timestamp: i64,                // Vote timestamp
}
```

---

## Development

### Prerequisites

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

# Install Anchor
cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
avm install latest
avm use latest
```

### Building

```bash
# Build council selection program
cd blockchain/contracts/solana/council_selection
anchor build

# Build voting program
cd blockchain/contracts/solana/voting
anchor build
```

### Testing

```bash
# Test council selection
cd blockchain/contracts/solana/council_selection
anchor test

# Test voting
cd blockchain/contracts/solana/voting
anchor test
```

---

## Deployment

### Devnet Deployment

```bash
# Run deployment script
cd blockchain/contracts/solana/deployment
./deploy.sh devnet

# Script will output program IDs - add to .env:
# COUNCIL_SELECTION_PROGRAM_ID=...
# VOTING_PROGRAM_ID=...
```

### Manual Deployment

```bash
# Set Solana to devnet
solana config set --url devnet

# Request airdrop for deployment
solana airdrop 2

# Deploy council selection
cd blockchain/contracts/solana/council_selection
anchor deploy --provider.cluster devnet

# Deploy voting
cd blockchain/contracts/solana/voting
anchor deploy --provider.cluster devnet
```

### Testnet/Mainnet

```bash
# Use deployment script with network parameter
./deploy.sh testnet   # For testnet
./deploy.sh mainnet   # For mainnet (requires security audit!)
```

---

## Usage from Python

### Initialize Clients

```python
from blockchain.integrations import SolanaClient

# Connect to Solana
client = SolanaClient(network='devnet')
```

### Council Selection

```python
# Initialize session
session_addr = await client.council_selection.initialize_session(
    session_id="council_123",
    required_agents=5,
    diversity_required=True
)

# Request VRF
vrf_tx = await client.council_selection.request_vrf(
    session_id="council_123",
    vrf_seed=12345
)

# Fulfill VRF (called by oracle)
fulfill_tx = await client.council_selection.fulfill_vrf(
    session_id="council_123",
    random_number=987654,
    vrf_proof=proof_bytes
)

# Record selected agents
select_tx = await client.council_selection.select_agents(
    session_id="council_123",
    agent_ids=["agent1", "agent2", "agent3", "agent4", "agent5"]
)

# Verify selection
is_valid = await client.council_selection.verify_selection("council_123")
```

### Voting

```python
from blockchain.integrations import VoteOption

# Initialize debate
debate_addr = await client.voting.initialize_debate(
    debate_id="debate_123",
    topic="Should AI be regulated?",
    max_rounds=3
)

# Cast votes
vote_tx = await client.voting.cast_vote(
    debate_id="debate_123",
    agent_id="agent1",
    vote_option=VoteOption.SUPPORT,
    confidence=85,
    reasoning="Strong evidence supports regulation"
)

# Tally votes
results = await client.voting.tally_votes("debate_123")

print(f"Outcome: {results['outcome']}")
print(f"Support: {results['support_score']}")
print(f"Oppose: {results['oppose_score']}")
```

---

## Security Considerations

### 1. Authority Validation

All instructions validate the authority (signer):

```rust
#[account(mut, has_one = authority)]
pub session: Account<'info, CouncilSession>,

pub authority: Signer<'info>,
```

### 2. State Machine Validation

Programs enforce valid state transitions:

```rust
require!(
    session.status == SessionStatus::Initialized,
    ErrorCode::InvalidSessionStatus
);
```

### 3. Input Validation

All inputs are validated:

```rust
require!(
    confidence <= 100,
    ErrorCode::InvalidConfidence
);
```

### 4. Duplicate Prevention

Prevents duplicate votes:

```rust
let existing_vote = debate.votes.iter().find(|v| v.agent_id == agent_id);
require!(existing_vote.is_none(), ErrorCode::AlreadyVoted);
```

---

## Gas Costs (Devnet)

| Operation | Typical Cost | Notes |
|-----------|--------------|-------|
| Initialize Session | ~0.00001 SOL | One-time per session |
| Request VRF | ~0.000005 SOL | Per request |
| Select Agents | ~0.00001 SOL | Per selection |
| Initialize Debate | ~0.00001 SOL | One-time per debate |
| Cast Vote | ~0.000005 SOL | Per vote |
| Tally Votes | ~0.00001 SOL | One-time per debate |

**Total for full flow**: ~0.00005 SOL (~$0.01 at current prices)

---

## Error Codes

### Council Selection Errors

```rust
InvalidSessionStatus      // Invalid state for operation
InvalidVRFProof          // VRF proof verification failed
InvalidAgentCount        // Wrong number of agents
SessionNotFound          // Session doesn't exist
```

### Voting Errors

```rust
DebateNotActive          // Debate is not active
InvalidConfidence        // Confidence not 0-100
AlreadyVoted            // Agent already voted
NoVotes                 // No votes to tally
VotesNotTallied         // Votes not yet tallied
```

---

## Monitoring

### View Program Logs

```bash
# Watch program logs
solana logs CounciL11111111111111111111111111111111111
solana logs Voting11111111111111111111111111111111111
```

### Check Account Data

```bash
# View session account
solana account <session_pubkey>

# View debate account
solana account <debate_pubkey>
```

### Explorer Links

- **Devnet**: https://explorer.solana.com/?cluster=devnet
- **Testnet**: https://explorer.solana.com/?cluster=testnet
- **Mainnet**: https://explorer.solana.com

---

## Upgrading Programs

### Upgrade Authority

Programs are upgradeable only by the deployment authority:

```bash
# Build new version
anchor build

# Upgrade program
solana program deploy \
  --program-id <program_id> \
  --upgrade-authority <authority_keypair> \
  target/deploy/program.so
```

### Version Migration

When upgrading:
1. Test thoroughly on devnet
2. Announce upgrade to users
3. Deploy to testnet
4. Final testing
5. Deploy to mainnet
6. Verify functionality

---

## Roadmap

### Current (Phase 3.2) ✅
- Council selection with VRF
- On-chain voting
- Proof verification
- Basic deployment

### Future (Phase 3.3+)
- Token-weighted voting
- Staking integration
- Multi-sig authority
- Governance proposals
- Cross-chain bridging

---

## Resources

- [Anchor Documentation](https://www.anchor-lang.com)
- [Solana Documentation](https://docs.solana.com)
- [Solana Program Library](https://spl.solana.com)
- [Anchor Examples](https://github.com/coral-xyz/anchor/tree/master/tests)

---

**Status**: ✅ Phase 3.2 Complete - Smart Contracts Deployed

**Next**: Phase 3.3 - Token Mechanics and Staking
