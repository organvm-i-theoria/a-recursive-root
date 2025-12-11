#!/usr/bin/env python3
"""
Blockchain Integration Demo

Demonstrates the full blockchain-integrated AI Council System:
- Verifiable random agent selection (Chainlink VRF)
- On-chain council session recording
- On-chain vote recording and tallying
- Proof generation and verification

This demo works in mock mode by default (no blockchain required).
Set SOLANA_MOCK_MODE=false to use real blockchain.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from blockchain.rng import HybridRNG, RNGSource
from blockchain.integrations import SolanaClient, VoteOption
from core.agents import Agent, get_personality, create_mock_llm
from core.events import Event, EventCategory


async def main():
    print("=" * 70)
    print("AI COUNCIL SYSTEM - BLOCKCHAIN INTEGRATION DEMO")
    print("=" * 70)
    print()

    # Step 1: Initialize blockchain clients
    print("Step 1: Initializing blockchain clients...")
    print("-" * 70)

    solana_client = SolanaClient(network='devnet')
    health = await solana_client.health_check()

    print(f"Solana Client:")
    print(f"  Network: {health['network']}")
    print(f"  RPC URL: {health['rpc_url']}")
    print(f"  Connected: {health['is_healthy']}")
    print(f"  Latency: {health['latency_ms']}ms")
    print(f"  Mock Mode: {health['mock_mode']}")
    print()

    # Step 2: Create event and agents
    print("Step 2: Creating event and AI agents...")
    print("-" * 70)

    # Create test event
    event = Event(
        event_id="event_001",
        source="twitter",
        category=EventCategory.TECHNOLOGY,
        content="Breaking: Major AI breakthrough announced. Implications for society?",
        timestamp="2025-10-24T10:00:00Z",
        metadata={"importance": 0.9}
    )

    print(f"Event: {event.content}")
    print()

    # Create diverse AI agents
    personalities = ['pragmatist', 'idealist', 'skeptic', 'optimist', 'contrarian']
    agents = []

    for i, personality in enumerate(personalities):
        agent = Agent(
            agent_id=f"agent_{i+1}",
            name=f"Agent {i+1}",
            personality=get_personality(personality),
            llm_provider=create_mock_llm()
        )
        agents.append(agent)

    print(f"Created {len(agents)} diverse AI agents:")
    for agent in agents:
        print(f"  - {agent.name}: {agent.personality.traits['base_type']}")
    print()

    # Step 3: Verifiable Random Selection
    print("Step 3: Selecting council members with verifiable randomness...")
    print("-" * 70)

    rng = HybridRNG()

    # Select 5 agents using blockchain RNG
    selection_result = await rng.get_random_selection(
        options=agents,
        count=5,
        use_blockchain=True
    )

    selected_agents = selection_result.selected_items

    print(f"Random Selection:")
    print(f"  Source: {selection_result.source.value}")
    print(f"  Verifiable: {selection_result.is_verifiable}")
    print(f"  Request ID: {selection_result.request_id}")
    print(f"  Timestamp: {selection_result.timestamp}")
    print()

    print(f"Selected Council Members:")
    for agent in selected_agents:
        print(f"  ✓ {agent.name} ({agent.personality.traits['base_type']})")
    print()

    # Verify selection
    is_valid = await rng.verify_selection(selection_result)
    print(f"Selection Verification: {'✅ Valid' if is_valid else '❌ Invalid'}")
    print()

    # Step 4: Record selection on-chain
    print("Step 4: Recording council selection on-chain...")
    print("-" * 70)

    session_id = "council_blockchain_demo"

    # Initialize council session on Solana
    session_address = await solana_client.council_selection.initialize_session(
        session_id=session_id,
        required_agents=len(selected_agents),
        diversity_required=True
    )

    print(f"Council Session:")
    print(f"  Session ID: {session_id}")
    print(f"  On-chain Address: {session_address}")
    print()

    # Request VRF on-chain
    if selection_result.source == RNGSource.CHAINLINK_VRF:
        vrf_tx = await solana_client.council_selection.request_vrf(
            session_id=session_id,
            vrf_seed=selection_result.metadata.get('seed', 0)
        )
        print(f"VRF Request Transaction: {vrf_tx}")
        print()

    # Record selected agents on-chain
    agent_ids = [agent.agent_id for agent in selected_agents]
    selection_tx = await solana_client.council_selection.select_agents(
        session_id=session_id,
        agent_ids=agent_ids
    )

    print(f"Agent Selection Transaction: {selection_tx}")
    print()

    # Verify on-chain
    on_chain_valid = await solana_client.council_selection.verify_selection(session_id)
    print(f"On-Chain Verification: {'✅ Valid' if on_chain_valid else '❌ Invalid'}")
    print()

    # Step 5: Conduct debate
    print("Step 5: Conducting council debate...")
    print("-" * 70)

    debate_topic = "Should AI development be regulated to prevent misuse?"

    # Initialize debate on-chain
    debate_id = "debate_blockchain_demo"
    debate_address = await solana_client.voting.initialize_debate(
        debate_id=debate_id,
        topic=debate_topic,
        max_rounds=2
    )

    print(f"Debate Session:")
    print(f"  Debate ID: {debate_id}")
    print(f"  Topic: {debate_topic}")
    print(f"  On-chain Address: {debate_address}")
    print()

    # Each agent generates a response and votes
    print("Agent Responses and Votes:")
    print()

    for agent in selected_agents:
        # Generate response
        response = await agent.generate_response(debate_topic, [])

        # Generate vote
        vote = await agent.vote(debate_topic, [])

        # Map vote to blockchain VoteOption
        vote_mapping = {
            "Strong Support": VoteOption.SUPPORT,
            "Support with Caution": VoteOption.SUPPORT,
            "Oppose": VoteOption.OPPOSE,
            "Strong Opposition": VoteOption.OPPOSE,
            "Neutral": VoteOption.NEUTRAL,
            "Abstain": VoteOption.ABSTAIN,
        }
        blockchain_vote = vote_mapping.get(vote['position'], VoteOption.NEUTRAL)

        # Record vote on-chain
        vote_tx = await solana_client.voting.cast_vote(
            debate_id=debate_id,
            agent_id=agent.agent_id,
            vote_option=blockchain_vote,
            confidence=int(vote['confidence'] * 100),
            reasoning=vote['reasoning'][:128]  # Limit reasoning length
        )

        print(f"🎤 {agent.name}:")
        print(f"   Position: {vote['position']}")
        print(f"   Confidence: {vote['confidence']:.2f}")
        print(f"   Reasoning: {vote['reasoning'][:100]}...")
        print(f"   On-chain TX: {vote_tx}")
        print()

    # Step 6: Tally votes on-chain
    print("Step 6: Tallying votes on blockchain...")
    print("-" * 70)

    tally_result = await solana_client.voting.tally_votes(debate_id)

    print(f"Final Results (On-Chain):")
    print(f"  Outcome: {tally_result['outcome']}")
    print(f"  Support Score: {tally_result['support_score']}")
    print(f"  Oppose Score: {tally_result['oppose_score']}")
    print(f"  Neutral Score: {tally_result['neutral_score']}")
    print(f"  Total Votes: {tally_result['total_votes']}")
    print()

    # Get on-chain session data
    session_data = await solana_client.council_selection.get_session(session_id)
    debate_data = await solana_client.voting.get_debate(debate_id)

    print(f"On-Chain Verification:")
    print(f"  Council Session Status: {session_data.status.value}")
    print(f"  Debate Status: {debate_data.status.value}")
    print(f"  Votes Tallied: {debate_data.votes_tallied}")
    print()

    # Step 7: Generate proof package
    print("Step 7: Generating verifiable proof package...")
    print("-" * 70)

    proof_package = {
        "session": {
            "session_id": session_id,
            "on_chain_address": session_address,
            "selection_source": selection_result.source.value,
            "selection_verified": is_valid,
            "selected_agents": agent_ids,
        },
        "debate": {
            "debate_id": debate_id,
            "on_chain_address": debate_address,
            "topic": debate_topic,
            "total_votes": tally_result['total_votes'],
            "outcome": tally_result['outcome'],
        },
        "randomness": {
            "request_id": selection_result.request_id,
            "timestamp": selection_result.timestamp.isoformat(),
            "is_verifiable": selection_result.is_verifiable,
        }
    }

    print("Verifiable Proof Package:")
    for section, data in proof_package.items():
        print(f"\n  {section.upper()}:")
        for key, value in data.items():
            print(f"    {key}: {value}")
    print()

    # Summary
    print("=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print()
    print("✅ Successfully demonstrated:")
    print("  1. Verifiable random council selection (Chainlink VRF)")
    print("  2. On-chain council session recording (Solana)")
    print("  3. AI agent debate with diverse perspectives")
    print("  4. On-chain vote recording (Solana)")
    print("  5. On-chain vote tallying and outcome determination")
    print("  6. Full proof package generation")
    print()

    # RNG statistics
    print("Blockchain RNG Statistics:")
    stats = rng.get_stats()
    for source, data in stats.items():
        print(f"  {source}:")
        print(f"    Requests: {data['total_requests']}")
        print(f"    Success Rate: {data['success_rate']}")
    print()

    print("All operations recorded on blockchain and fully verifiable!")
    print()


if __name__ == "__main__":
    asyncio.run(main())
