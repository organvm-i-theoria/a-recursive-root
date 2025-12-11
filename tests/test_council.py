"""Tests for Council system"""

import pytest
import asyncio
from datetime import datetime

from core.agents.base_agent import AgentConfig, AgentPersonality
from core.agents.debate_agent import DebateAgent
from core.council.council import Council, DebateFormat
from core.events.event_ingestion import Event, EventSource, EventCategory


@pytest.fixture
def council():
    """Create a test council"""
    return Council(name="Test Council")


@pytest.fixture
def agents():
    """Create test agents"""
    configs = [
        AgentConfig(name="Agent1", personality=AgentPersonality.OPTIMIST),
        AgentConfig(name="Agent2", personality=AgentPersonality.PESSIMIST),
        AgentConfig(name="Agent3", personality=AgentPersonality.PRAGMATIST),
    ]

    return [DebateAgent(config, provider="mock") for config in configs]


@pytest.fixture
def sample_event():
    """Create a sample event"""
    return Event(
        event_id="test_1",
        title="Test Topic",
        description="A test debate topic",
        source=EventSource.MANUAL,
        category=EventCategory.OTHER,
        timestamp=datetime.utcnow(),
        facts=["Fact 1", "Fact 2"],
    )


def test_council_creation(council):
    """Test creating a council"""
    assert council.name == "Test Council"
    assert council.get_agent_count() == 0


def test_add_agents(council, agents):
    """Test adding agents to council"""
    for agent in agents:
        council.add_agent(agent)

    assert council.get_agent_count() == 3


def test_select_agents(council, agents):
    """Test agent selection for debate"""
    for agent in agents:
        council.add_agent(agent)

    selected = council.select_agents_for_debate(
        event=None,
        num_agents=2,
        ensure_diversity=True
    )

    assert len(selected) == 2
    assert selected[0].personality != selected[1].personality


@pytest.mark.asyncio
async def test_start_debate(council, agents, sample_event):
    """Test starting a debate"""
    for agent in agents:
        council.add_agent(agent)

    session = await council.start_debate(
        event=sample_event,
        format=DebateFormat.ROUNDTABLE,
        num_agents=2,
        max_rounds=3
    )

    assert session is not None
    assert len(session.participating_agents) == 2
    assert session.event.title == "Test Topic"
    assert session.max_rounds == 3


@pytest.mark.asyncio
async def test_run_debate(council, agents, sample_event):
    """Test running a complete debate"""
    for agent in agents:
        council.add_agent(agent)

    session = await council.start_debate(
        event=sample_event,
        format=DebateFormat.ROUNDTABLE,
        num_agents=2,
        max_rounds=2
    )

    completed_session = await council.run_debate(session)

    assert completed_session.ended_at is not None
    assert len(completed_session.rounds) > 0
    assert completed_session.voting_result is not None


def test_leaderboard(council, agents):
    """Test getting leaderboard"""
    for agent in agents:
        council.add_agent(agent)

    # Simulate some wins
    agents[0].debate_wins = 5
    agents[1].debate_wins = 3
    agents[2].debate_wins = 1

    leaderboard = council.get_leaderboard()

    assert len(leaderboard) == 3
    assert leaderboard[0][1] == 5  # Highest wins first
    assert leaderboard[0][0] == "Agent1"
