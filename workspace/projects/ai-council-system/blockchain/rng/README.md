# Random Number Generation (RNG) Module

**Status**: Phase 3.1 Complete
**Version**: 0.3.0-alpha

---

## Overview

This module provides verifiable, blockchain-based random number generation for the AI Council System. It combines multiple entropy sources with intelligent fallback to ensure both security and availability.

### Key Features

- **Chainlink VRF**: Provably fair, tamper-proof randomness
- **Pyth Entropy**: High-frequency entropy with <1s latency
- **Hybrid Coordinator**: Automatic fallback between sources
- **Mock Mode**: Development without blockchain dependencies
- **Verification**: On-chain proof verification

---

## Quick Start

### Basic Usage

```python
from blockchain.rng import HybridRNG

# Initialize RNG
rng = HybridRNG()

# Get random selection (tries blockchain, falls back to local if needed)
result = await rng.get_random_selection(
    options=available_agents,
    count=5,
    use_blockchain=True
)

# Access selected items
selected_agents = result.selected_items

# Check if verifiable on-chain
if result.is_verifiable:
    print(f"Verifiable via {result.source.value}")
    if result.proof:
        print(f"VRF Proof: {result.proof.proof_hash}")
```

### Quick Selection Helper

```python
from blockchain.rng import get_random_selection

# One-liner for random selection
result = await get_random_selection(agents, count=5)
selected = result.selected_items
```

---

## Architecture

```
blockchain/rng/
├── __init__.py              # Module exports
├── chainlink_vrf.py         # Chainlink VRF provider
├── pyth_entropy.py          # Pyth Entropy provider
├── hybrid_rng.py            # Hybrid coordinator
└── README.md                # This file
```

### Flow Diagram

```
User Request
     │
     ├─ use_blockchain=True?
     │  │
     │  ├─ Yes → Try Chainlink VRF (prefer_vrf=True)
     │  │        │
     │  │        ├─ Success → Return with VRF proof ✅
     │  │        │
     │  │        └─ Fail → Try Pyth Entropy
     │  │                  │
     │  │                  ├─ Success → Return with Pyth entropy ✅
     │  │                  │
     │  │                  └─ Fail → Fallback to local CSPRNG
     │  │
     │  └─ No → Use local CSPRNG directly
     │
     └─ Return SelectionResult
```

---

## Providers

### 1. Chainlink VRF

**Best for**: High-security selections where proof is required

**Characteristics**:
- Latency: 2-5 seconds
- Security: Cryptographic proof
- Verifiability: On-chain proof verification
- Cost: ~$0.002 per request (mainnet)

**Example**:
```python
from blockchain.rng import ChainlinkVRFProvider

vrf = ChainlinkVRFProvider()

# Request randomness
request_id = await vrf.request_randomness(seed=12345)

# Get random number (waits for fulfillment)
random_num = await vrf.get_random_number(request_id)

# Verify proof
is_valid = vrf.verify_randomness(request_id, random_num)

# Get proof for external verification
proof = vrf.get_proof(request_id)
```

**Configuration**:
```bash
# .env
CHAINLINK_VRF_COORDINATOR=0x...
CHAINLINK_VRF_KEY_HASH=0x...
CHAINLINK_VRF_SUBSCRIPTION_ID=123
CHAINLINK_MOCK_MODE=false  # Set to true for development
```

### 2. Pyth Entropy

**Best for**: Fast selections where speed matters

**Characteristics**:
- Latency: <1 second
- Security: On-chain entropy
- Verifiability: Solana on-chain
- Cost: Minimal (~$0.0001 per request)

**Example**:
```python
from blockchain.rng import PythEntropyProvider

pyth = PythEntropyProvider()

# Get random bytes
random_bytes = await pyth.get_random_bytes(32)

# Get random integer
random_int = await pyth.get_random_int(0, 100)

# Get random selection
selected = await pyth.get_random_selection(options, count=5)
```

**Configuration**:
```bash
# .env
PYTH_NETWORK_ENDPOINT=https://xc-mainnet.pyth.network
PYTH_MOCK_MODE=false  # Set to true for development
```

### 3. Hybrid RNG (Recommended)

**Best for**: Production use with automatic fallback

**Characteristics**:
- Tries blockchain first, falls back if needed
- Configurable priority (VRF vs Pyth)
- Statistics tracking
- Error resilience

**Example**:
```python
from blockchain.rng import HybridRNG

rng = HybridRNG(
    prefer_vrf=True,      # Try VRF before Pyth
    vrf_timeout=10,       # Wait up to 10s for VRF
    pyth_timeout=5        # Wait up to 5s for Pyth
)

# Get selection with automatic fallback
result = await rng.get_random_selection(
    options=agents,
    count=5,
    use_blockchain=True,
    allow_fallback=True  # Fallback to local if blockchain fails
)

# Check usage statistics
stats = rng.get_stats()
print(stats)
# {
#   'chainlink_vrf': {'total_requests': 10, 'success_rate': '90.0%'},
#   'pyth_entropy': {'total_requests': 5, 'success_rate': '100.0%'},
#   'local_csprng': {'total_requests': 1, 'success_rate': '100.0%'}
# }
```

---

## SelectionResult Object

Every selection returns a `SelectionResult` with metadata:

```python
@dataclass
class SelectionResult:
    selected_items: List[Any]      # The selected items
    source: RNGSource               # Which provider was used
    request_id: Optional[str]       # Request ID (if blockchain)
    is_verifiable: bool             # Can be verified on-chain?
    proof: Optional[VRFProof]       # VRF proof (if using Chainlink)
    timestamp: datetime             # When selection occurred
    metadata: Dict[str, Any]        # Additional metadata
```

**Example**:
```python
result = await rng.get_random_selection(agents, 5)

print(f"Selected {len(result.selected_items)} agents")
print(f"Source: {result.source.value}")
print(f"Verifiable: {result.is_verifiable}")

if result.is_verifiable:
    # Can prove this selection is fair
    proof_data = {
        "request_id": result.request_id,
        "timestamp": result.timestamp.isoformat(),
        "source": result.source.value
    }

    if result.proof:
        proof_data["vrf_proof"] = result.proof.proof_hash

    # Store or publish proof
    await store_proof(proof_data)
```

---

## Integration Examples

### With Council Manager

```python
from core.council import CouncilManager
from blockchain.rng import HybridRNG

# Initialize council manager with blockchain RNG
rng = HybridRNG()
council_mgr = CouncilManager(rng_provider=rng)

# Form council with verifiable randomness
result = await council_mgr.form_council_with_proof(size=5)

# Get agents and proof
agents = result.selected_items
proof = result.proof

# Record selection on-chain (if using blockchain)
if result.is_verifiable:
    await blockchain_client.record_selection(
        agents=[a.id for a in agents],
        proof=proof
    )
```

### With Event Prioritization

```python
from blockchain.rng import HybridRNG

rng = HybridRNG()

# Randomly select which events to process
priority_events = await rng.get_random_selection(
    options=all_events,
    count=10,
    use_blockchain=True
)

# Process selected events
for event in priority_events.selected_items:
    await process_event(event)
```

---

## Mock Mode (Development)

For development without blockchain access, both providers support mock mode:

```bash
# .env
CHAINLINK_MOCK_MODE=true
PYTH_MOCK_MODE=true
```

**Mock mode behavior**:
- Chainlink VRF: Generates deterministic randomness with simulated proofs
- Pyth Entropy: Generates deterministic entropy from hashes
- No network calls
- Instant results (<100ms)
- Suitable for testing and development

**Differences from production**:
- Not verifiable on actual blockchain
- Deterministic (same seed = same result)
- No gas costs
- No network latency

---

## Verification

### Verify VRF Selection

```python
from blockchain.rng import ChainlinkVRFProvider

vrf = ChainlinkVRFProvider()

# After getting a selection
request_id = "abc123..."
random_number = 1234567890

# Verify the random number is valid
is_valid = vrf.verify_randomness(request_id, random_number)

if is_valid:
    print("✅ Selection is provably fair")
else:
    print("❌ Verification failed - possible tampering")
```

### Verify Hybrid Selection

```python
from blockchain.rng import HybridRNG

rng = HybridRNG()

# Get selection
result = await rng.get_random_selection(agents, 5)

# Verify it
is_valid = await rng.verify_selection(result)

if is_valid:
    print("✅ Selection verified")
else:
    print("❌ Verification failed")
```

---

## Testing

### Unit Tests

```bash
# Test Chainlink VRF
pytest tests/blockchain/rng/test_chainlink_vrf.py -v

# Test Pyth Entropy
pytest tests/blockchain/rng/test_pyth_entropy.py -v

# Test Hybrid RNG
pytest tests/blockchain/rng/test_hybrid_rng.py -v
```

### Example Tests

```python
# tests/blockchain/rng/test_hybrid_rng.py

import pytest
from blockchain.rng import HybridRNG

@pytest.mark.asyncio
async def test_hybrid_rng_selection():
    rng = HybridRNG()
    options = list(range(100))

    result = await rng.get_random_selection(options, count=5)

    assert len(result.selected_items) == 5
    assert all(item in options for item in result.selected_items)
    assert result.source in [RNGSource.CHAINLINK_VRF, RNGSource.PYTH_ENTROPY, RNGSource.LOCAL_CSPRNG]

@pytest.mark.asyncio
async def test_vrf_verification():
    from blockchain.rng import ChainlinkVRFProvider

    vrf = ChainlinkVRFProvider()
    request_id = await vrf.request_randomness(12345)
    random_num = await vrf.get_random_number(request_id)

    assert vrf.verify_randomness(request_id, random_num)
```

---

## Performance

### Benchmarks

| Operation | Mock Mode | Devnet | Mainnet |
|-----------|-----------|--------|---------|
| Chainlink VRF | <100ms | 2-5s | 2-5s |
| Pyth Entropy | <50ms | <1s | <1s |
| Local CSPRNG | <1ms | <1ms | <1ms |
| Hybrid (blockchain success) | <100ms | 1-5s | 1-5s |
| Hybrid (with fallback) | <100ms | <2s | <2s |

### Gas Costs (Mainnet)

| Operation | Chainlink (ETH) | Pyth (SOL) |
|-----------|-----------------|------------|
| VRF Request | ~0.001 ETH (~$2) | N/A |
| Entropy Fetch | N/A | ~0.000005 SOL (~$0.0001) |

---

## Security Considerations

### 1. Always Verify Proofs

```python
# ❌ BAD: Don't trust without verification
random_num = await vrf.get_random_number(request_id)
selected_index = random_num % len(options)  # DON'T DO THIS

# ✅ GOOD: Verify before using
random_num = await vrf.get_random_number(request_id)
if vrf.verify_randomness(request_id, random_num):
    selected_index = random_num % len(options)  # Safe
else:
    raise ValueError("Invalid randomness!")
```

### 2. Don't Expose Seeds

```python
# ❌ BAD: Predictable seed
seed = 12345  # Always the same

# ✅ GOOD: Cryptographically secure seed
import secrets
seed = secrets.randbits(256)
```

### 3. Use Blockchain for Important Selections

```python
# For critical selections (council members, winners)
result = await rng.get_random_selection(
    agents,
    count=5,
    use_blockchain=True,      # ✅ Use blockchain
    allow_fallback=False      # ✅ Don't fallback
)

# For non-critical selections (event ordering)
result = await rng.get_random_selection(
    events,
    count=10,
    use_blockchain=False  # Local is fine
)
```

---

## Troubleshooting

### VRF Request Timeout

**Problem**: VRF requests taking too long

**Solutions**:
1. Check VRF subscription has funds
2. Increase timeout: `HybridRNG(vrf_timeout=30)`
3. Check network congestion
4. Ensure coordinator address is correct

### Pyth Connection Failed

**Problem**: Cannot connect to Pyth Network

**Solutions**:
1. Check endpoint URL is correct
2. Check network connectivity
3. Try alternative endpoint
4. Enable mock mode for development

### Fallback to Local Too Often

**Problem**: Blockchain RNG always failing

**Solutions**:
1. Check provider configuration
2. Enable mock mode for development
3. Check network connectivity
4. Review provider logs for errors

---

## Roadmap

### Current (Phase 3.1) ✅
- Chainlink VRF provider
- Pyth Entropy provider
- Hybrid RNG coordinator
- Mock mode for development

### Future (Phase 3.2+)
- Ethereum support
- Multiple VRF providers
- Randomness caching
- Advanced verification
- Cross-chain randomness

---

## Resources

- [Chainlink VRF Documentation](https://docs.chain.link/vrf)
- [Pyth Network Documentation](https://docs.pyth.network)
- [Verifiable Random Functions Explained](https://en.wikipedia.org/wiki/Verifiable_random_function)

---

**Status**: ✅ Phase 3.1 Complete - RNG Integration Functional

**Next**: Phase 3.2 - Smart Contracts
