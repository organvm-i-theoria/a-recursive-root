"""Tests for AI agents"""

import pytest
import asyncio
from core.agents.base_agent import AgentConfig, AgentPersonality
from core.agents.debate_agent import DebateAgent


@pytest.mark.asyncio
async def test_agent_creation():
    """Test creating an agent"""
    config = AgentConfig(
        name="TestAgent",
        personality=AgentPersonality.OPTIMIST,
        expertise_areas=["testing"],
    )

    agent = DebateAgent(config, provider="mock")

    assert agent.name == "TestAgent"
    assert agent.personality == AgentPersonality.OPTIMIST
    assert agent.agent_id is not None


@pytest.mark.asyncio
async def test_agent_form_opinion():
    """Test agent forming an opinion"""
    config = AgentConfig(
        name="OpinionAgent",
        personality=AgentPersonality.PRAGMATIST,
    )

    agent = DebateAgent(config, provider="mock")

    opinion = await agent.form_opinion(
        topic="AI Regulation",
        facts=["AI is growing rapidly", "Regulation is being discussed"],
        previous_arguments=[]
    )

    assert "stance" in opinion
    assert "argument" in opinion
    assert "confidence" in opinion
    assert opinion["agent_name"] == "OpinionAgent"


@pytest.mark.asyncio
async def test_agent_response():
    """Test agent responding to argument"""
    config = AgentConfig(
        name="ResponderAgent",
        personality=AgentPersonality.CONTRARIAN,
    )

    agent = DebateAgent(config, provider="mock")

    response = await agent.respond_to_argument(
        original_argument="This is a good idea",
        opponent_name="OtherAgent",
        debate_context={"topic": "Test Topic"}
    )

    assert isinstance(response, str)
    assert len(response) > 0
    assert agent.total_contributions == 1


def test_agent_stats():
    """Test getting agent statistics"""
    config = AgentConfig(
        name="StatsAgent",
        personality=AgentPersonality.MODERATE,
    )

    agent = DebateAgent(config, provider="mock")
    stats = agent.get_stats()

    assert stats["name"] == "StatsAgent"
    assert stats["personality"] == "moderate"
    assert stats["total_contributions"] == 0
    assert stats["debate_wins"] == 0
