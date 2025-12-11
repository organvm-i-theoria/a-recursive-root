#!/usr/bin/env python3
"""
Simple test runner for AI Council System
Run this to verify the system is working without needing pytest installed
"""

import asyncio
import sys

print("="*80)
print("AI Council System - Basic Test Suite")
print("="*80)
print()

# Test 1: Import core modules
print("Test 1: Importing core modules...")
try:
    from core.agents.base_agent import AgentConfig, AgentPersonality
    from core.agents.debate_agent import DebateAgent
    from core.council.council import Council, DebateFormat
    from core.events.event_ingestion import EventIngester, EventSource
    print("✓ All core modules imported successfully")
except Exception as e:
    print(f"✗ Failed to import modules: {e}")
    sys.exit(1)

# Test 2: Create agent
print("\nTest 2: Creating AI agent...")
try:
    config = AgentConfig(
        name="TestAgent",
        personality=AgentPersonality.OPTIMIST,
        expertise_areas=["testing"],
    )
    agent = DebateAgent(config, provider="mock")
    assert agent.name == "TestAgent"
    assert agent.personality == AgentPersonality.OPTIMIST
    print("✓ Agent created successfully")
except Exception as e:
    print(f"✗ Failed to create agent: {e}")
    sys.exit(1)

# Test 3: Create council
print("\nTest 3: Creating council...")
try:
    council = Council(name="Test Council")
    council.add_agent(agent)
    assert council.get_agent_count() == 1
    print("✓ Council created and agent added")
except Exception as e:
    print(f"✗ Failed to create council: {e}")
    sys.exit(1)

# Test 4: Create event ingester
print("\nTest 4: Creating event ingester...")
try:
    ingester = EventIngester()
    ingester.enable_source(EventSource.MANUAL)
    event = ingester.add_manual_event(
        title="Test Event",
        description="A test event"
    )
    assert ingester.get_queue_size() == 1
    print("✓ Event ingester working")
except Exception as e:
    print(f"✗ Failed with event ingester: {e}")
    sys.exit(1)

# Test 5: Run mini debate
print("\nTest 5: Running mini debate...")
async def test_debate():
    try:
        # Create more agents
        agent2 = DebateAgent(AgentConfig(
            name="Agent2",
            personality=AgentPersonality.PESSIMIST,
        ), provider="mock")

        agent3 = DebateAgent(AgentConfig(
            name="Agent3",
            personality=AgentPersonality.PRAGMATIST,
        ), provider="mock")

        council.add_agent(agent2)
        council.add_agent(agent3)

        # Start debate
        session = await council.start_debate(
            event=event,
            format=DebateFormat.ROUNDTABLE,
            num_agents=2,
            max_rounds=2
        )

        # Run one round
        await council._opening_round(session)

        assert len(session.rounds) > 0
        print("✓ Mini debate executed successfully")

    except Exception as e:
        print(f"✗ Failed to run debate: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

asyncio.run(test_debate())

# All tests passed
print("\n" + "="*80)
print("✓ All basic tests passed!")
print("="*80)
print("\nThe system is working correctly!")
print("\nTo run full tests with pytest:")
print("  pip install pytest pytest-asyncio")
print("  pytest tests/ -v")
print()
