# Viewer Voting System

Real-time viewer participation system for AI Council debates with gamification features.

## Overview

The Viewer Voting System allows viewers to participate in AI Council debates by casting votes, viewing real-time statistics, earning points and achievements, and competing on leaderboards. Viewer votes are combined with AI agent votes using configurable weights to determine final debate outcomes.

## Features

### Core Voting Features
- ✅ **Multiple Vote Types**: Binary (support/oppose), scaled (1-5), ranked, confidence-based
- ✅ **Real-Time Aggregation**: Live vote counting and statistics
- ✅ **Hybrid Outcomes**: Combine agent and viewer votes with configurable weights
- ✅ **Fraud Prevention**: Rate limiting, IP tracking, duplicate detection
- ✅ **Vote Analytics**: Consensus levels, vote velocity, confidence scoring

### Gamification Features
- ✅ **Points System**: Earn points for voting and accurate predictions
- ✅ **13 Achievements**: From "First Vote" to "Dedication Legend"
- ✅ **6 Reputation Tiers**: Newcomer → Legend
- ✅ **Voting Streaks**: Daily streak tracking
- ✅ **Leaderboards**: Rank by points, votes, accuracy, or achievements
- ✅ **Badges**: Visual representation of accomplishments

## Architecture

### Module Structure

```
web/backend/voting/
├── __init__.py              # Package exports
├── voting_api.py            # Core voting functionality
├── gamification.py          # Points, achievements, leaderboards
└── README.md                # This file

core/council/
└── viewer_integration.py    # Integration with debate system

examples/
└── viewer_voting_demo.py    # Comprehensive demo
```

### Key Classes

#### voting_api.py

- **`Vote`**: Individual vote data structure
- **`VoteStats`**: Aggregated voting statistics
- **`VotingManager`**: Core voting management
  - Submit votes
  - Aggregate statistics
  - Calculate hybrid outcomes
  - Rate limiting

#### gamification.py

- **`Achievement`**: Achievement definition
- **`UserProfile`**: User gamification data
- **`LeaderboardEntry`**: Leaderboard ranking
- **`GamificationManager`**: Gamification management
  - Track points and achievements
  - Manage streaks
  - Generate leaderboards

#### viewer_integration.py

- **`HybridVoteResult`**: Combined agent+viewer outcome
- **`ViewerIntegrationManager`**: Integration layer
  - Open debates for voting
  - Submit viewer votes
  - Calculate hybrid results
  - Award gamification points

## Usage Examples

### Basic Vote Submission

```python
from web.backend.voting import get_voting_manager, VoteType, VotePosition

voting_mgr = get_voting_manager()

# Submit a vote
vote = await voting_mgr.submit_vote(
    user_id="user123",
    debate_id="debate_ai_regulation",
    round_number=1,
    vote_type=VoteType.BINARY,
    position=VotePosition.SUPPORT,
    confidence=0.85,
    reasoning="Strong safeguards are necessary for public benefit"
)

print(f"Vote submitted: {vote.vote_id}")
```

### Get Vote Statistics

```python
# Get debate statistics
stats = await voting_mgr.get_stats("debate_ai_regulation")

print(f"Total votes: {stats.total_votes}")
print(f"Support: {stats.support_percentage:.1f}%")
print(f"Oppose: {stats.oppose_percentage:.1f}%")
print(f"Consensus level: {stats.consensus_level:.0%}")
```

### Hybrid Outcome (Agents + Viewers)

```python
from core.council.viewer_integration import get_viewer_integration_manager

viewer_mgr = get_viewer_integration_manager()

# Set weights (70% agents, 30% viewers)
viewer_mgr.set_vote_weights(agent_weight=0.7, viewer_weight=0.3)

# Agent votes
agent_votes = {
    "agent_1": VotePosition.SUPPORT,
    "agent_2": VotePosition.OPPOSE,
    "agent_3": VotePosition.SUPPORT,
}

# Calculate hybrid result
result = await viewer_mgr.calculate_hybrid_result(
    debate_id="debate_ai_regulation",
    round_number=1,
    agent_votes=agent_votes
)

print(f"Final outcome: {result.final_outcome.value}")
print(f"Support score: {result.final_support_score:.2%}")
print(f"Oppose score: {result.final_oppose_score:.2%}")
```

### Gamification

```python
from web.backend.voting import get_gamification_manager

gamification_mgr = get_gamification_manager()

# Get user profile
profile = await gamification_mgr.get_profile("user123")

print(f"Points: {profile.points}")
print(f"Reputation: {profile.reputation_tier.value}")
print(f"Achievements: {len(profile.achievements)}")
print(f"Current streak: {profile.current_streak} days")
print(f"Accuracy: {profile.accuracy_rate:.1f}%")

# Get leaderboard
leaderboard = await gamification_mgr.get_leaderboard(limit=10, sort_by="points")

for entry in leaderboard:
    print(f"#{entry.rank} {entry.user_id}: {entry.points} points")
```

## Vote Types

### Binary Voting
Most common type - support or oppose a position.

```python
vote = await voting_mgr.submit_vote(
    user_id="user123",
    debate_id="debate_id",
    round_number=1,
    vote_type=VoteType.BINARY,
    position=VotePosition.SUPPORT,  # or OPPOSE, NEUTRAL, ABSTAIN
    confidence=0.8
)
```

### Scaled Voting
Rate on a 1-5 scale.

```python
vote = await voting_mgr.submit_vote(
    user_id="user123",
    debate_id="debate_id",
    round_number=1,
    vote_type=VoteType.SCALED,
    position=VotePosition.SUPPORT,
    scaled_value=4  # 1-5 scale
)
```

### Ranked Voting
Rank multiple options by preference.

```python
vote = await voting_mgr.submit_vote(
    user_id="user123",
    debate_id="debate_id",
    round_number=1,
    vote_type=VoteType.RANKED,
    position=VotePosition.SUPPORT,
    ranked_options=["option_a", "option_c", "option_b"]
)
```

### Confidence-Based Voting
Include confidence level with vote.

```python
vote = await voting_mgr.submit_vote(
    user_id="user123",
    debate_id="debate_id",
    round_number=1,
    vote_type=VoteType.CONFIDENCE,
    position=VotePosition.SUPPORT,
    confidence=0.95  # 0.0 to 1.0
)
```

## Achievements

### Available Achievements

| Achievement | Description | Points | Tier |
|-------------|-------------|--------|------|
| 🎯 First Participant | Cast your first vote | 10 | 1 |
| 📊 Getting Started | Cast 10 total votes | 20 | 1 |
| 🏆 Engaged Citizen | Cast 100 total votes | 100 | 2 |
| 💎 Super Voter | Cast 1000 total votes | 500 | 4 |
| 🔥 Weekly Regular | Vote 7 consecutive days | 50 | 2 |
| ⭐ Monthly Champion | Vote 30 consecutive days | 200 | 3 |
| 👑 Dedication Legend | Vote 100 consecutive days | 1000 | 5 |
| 🔮 Oracle | Vote matched final outcome | 25 | 2 |
| 🤝 Consensus Builder | Vote with majority 10 times | 50 | 2 |
| 🎭 Contrarian | Vote against majority 10 times | 50 | 2 |
| 🐦 Early Bird | Be among first 10 voters | 15 | 1 |
| 💭 Thoughtful Participant | Provide reasoning for 50 votes | 75 | 2 |
| 🌐 Diverse Interests | Vote on 10 different topics | 40 | 2 |

### Reputation Tiers

| Tier | Points Required |
|------|----------------|
| Newcomer | 0 |
| Contributor | 100 |
| Regular | 500 |
| Expert | 1,000 |
| Authority | 5,000 |
| Legend | 10,000 |

## Statistics and Analytics

### Vote Statistics

```python
stats = await voting_mgr.get_stats(debate_id)

# Access various metrics
total_votes = stats.total_votes
support_pct = stats.support_percentage
oppose_pct = stats.oppose_percentage
consensus = stats.consensus_level  # 0.0 to 1.0 (higher = more agreement)
avg_confidence = stats.avg_confidence
vote_velocity = stats.vote_velocity  # Votes per minute
top_reasons = stats.top_reasons  # Most common reasoning
```

### Consensus Level

The consensus level measures how unified the voting is:
- **High (>0.7)**: Strong agreement
- **Medium (0.4-0.7)**: Moderate agreement
- **Low (<0.4)**: Division/controversy

Calculated using the Gini coefficient to measure vote distribution inequality.

## Fraud Prevention

### Rate Limiting
- Default: 5 votes per minute per user
- Tracked using rolling time window
- Customizable limits

```python
# Rate limiting is automatic
vote = await voting_mgr.submit_vote(...)  # May raise ValueError if limit exceeded
```

### IP Tracking
- IP addresses are hashed (not stored in plaintext)
- Used to detect duplicate voting
- User agents also tracked

```python
vote = await voting_mgr.submit_vote(
    user_id="user123",
    debate_id="debate_id",
    # ... other params ...
    ip_address="192.168.1.1",  # Will be hashed
    user_agent="Mozilla/5.0 ..."  # Will be hashed
)
```

## Configuration

### Mock Mode

Enable mock mode for development (enabled by default):

```bash
export VIEWER_VOTING_MOCK_MODE=true
export GAMIFICATION_MOCK_MODE=true
export VIEWER_INTEGRATION_MOCK_MODE=true
```

### Vote Weights

Configure how agent and viewer votes are weighted:

```python
viewer_mgr = get_viewer_integration_manager()

# Default: 70% agents, 30% viewers
viewer_mgr.set_vote_weights(agent_weight=0.7, viewer_weight=0.3)

# Equal weight
viewer_mgr.set_vote_weights(agent_weight=0.5, viewer_weight=0.5)

# Viewer-dominant
viewer_mgr.set_vote_weights(agent_weight=0.3, viewer_weight=0.7)
```

## Running the Demo

```bash
cd workspace/projects/ai-council-system
python examples/viewer_voting_demo.py
```

The demo shows:
1. Opening a debate for voting
2. Submitting 10 viewer votes
3. Displaying vote statistics
4. Simulating agent votes
5. Calculating hybrid outcome
6. Awarding gamification points
7. Showing user profiles and achievements
8. Displaying leaderboard
9. Advanced analytics

## Integration with Council System

The viewer voting system integrates seamlessly with the core debate system:

```python
from core.council.viewer_integration import get_viewer_integration_manager

viewer_mgr = get_viewer_integration_manager()

# 1. Open debate for voting
await viewer_mgr.open_debate_for_voting(
    debate_id=session_id,
    topic=debate_topic,
    description=debate_description
)

# 2. Viewers cast votes during debate
# (handled by WebSocket/API endpoints in production)

# 3. After agents vote, calculate hybrid result
hybrid_result = await viewer_mgr.calculate_hybrid_result(
    debate_id=session_id,
    round_number=current_round,
    agent_votes=agent_vote_dict
)

# 4. Use hybrid result as final outcome
final_outcome = hybrid_result.final_outcome

# 5. Finalize and award points
await viewer_mgr.finalize_debate_voting(
    debate_id=session_id,
    final_outcome=final_outcome
)
```

## API Endpoints (Production)

In production, these REST and WebSocket endpoints would be exposed:

### REST Endpoints

```
POST   /api/debates/{debate_id}/votes          # Submit vote
GET    /api/debates/{debate_id}/votes/stats    # Get statistics
GET    /api/users/{user_id}/profile            # Get user profile
GET    /api/users/{user_id}/votes              # Get user's votes
GET    /api/leaderboard                        # Get leaderboard
```

### WebSocket

```
WS     /api/debates/{debate_id}/votes/live     # Real-time vote updates
```

Example WebSocket events:
```json
{
  "event": "vote_cast",
  "data": {
    "total_votes": 157,
    "support_votes": 92,
    "oppose_votes": 65,
    "support_percentage": 58.6,
    "oppose_percentage": 41.4
  }
}
```

## Performance Considerations

- Vote aggregation is O(n) where n = number of votes
- Statistics are cached and updated incrementally
- Rate limiting uses memory-efficient rolling window
- IP/user agent hashing provides privacy without storage overhead
- Leaderboard queries are optimized with in-memory sorting

## Future Enhancements

- [ ] Persistent storage (database integration)
- [ ] WebSocket implementation for real-time updates
- [ ] Frontend React components
- [ ] Vote verification with blockchain
- [ ] Machine learning for fraud detection
- [ ] Advanced analytics dashboard
- [ ] Vote delegation (proxy voting)
- [ ] Weighted voting based on expertise
- [ ] Vote prediction markets

## See Also

- `examples/viewer_voting_demo.py` - Complete working demo
- `core/council/debate.py` - Debate orchestration
- `web/backend/server.py` - API server
- `PHASE_4_PLAN.md` - Full Phase 4 roadmap

---

**Version**: 0.4.0-alpha
**Status**: ✅ Phase 4.3 Complete
**Mock Mode**: Fully supported
