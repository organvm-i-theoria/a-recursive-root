#!/usr/bin/env python3
"""
AI Council System - Quick Demo

Quick demonstration of the AI Council debate system.
"""

import asyncio
import logging

from core.agents.base_agent import AgentConfig, AgentPersonality
from core.agents.debate_agent import DebateAgent
from core.council.council import Council, DebateFormat
from core.events.event_ingestion import EventCategory
from core.visualization import StreamOutput

# Simple logging setup
logging.basicConfig(level=logging.WARNING)


async def run_demo():
    """Run a quick demonstration"""
    print("\n" + "="*80)
    print("🎙️  AI COUNCIL SYSTEM - DEMONSTRATION")
    print("="*80 + "\n")

    print("Setting up the AI Council...")

    # Create council
    council = Council(name="Demo Council")

    # Create diverse agents
    agents = [
        DebateAgent(AgentConfig(
            name="Optimist",
            personality=AgentPersonality.OPTIMIST,
            expertise_areas=["innovation"],
        ), provider="mock"),

        DebateAgent(AgentConfig(
            name="Skeptic",
            personality=AgentPersonality.PESSIMIST,
            expertise_areas=["risk analysis"],
        ), provider="mock"),

        DebateAgent(AgentConfig(
            name="Pragmatist",
            personality=AgentPersonality.PRAGMATIST,
            expertise_areas=["implementation"],
        ), provider="mock"),
    ]

    for agent in agents:
        council.add_agent(agent)

    print(f"✓ Created {len(agents)} AI agents with diverse personalities\n")

    # Create a sample event
    from core.events.event_ingestion import Event, EventSource
    from datetime import datetime

    event = Event(
        event_id="demo_1",
        title="The Future of AI Governance",
        description="Should AI systems be regulated by government bodies or remain self-governed by the tech industry?",
        source=EventSource.MANUAL,
        category=EventCategory.POLITICS,
        timestamp=datetime.utcnow(),
        facts=[
            "Current AI development is largely unregulated",
            "EU has proposed comprehensive AI regulation (AI Act)",
            "Tech companies advocate for self-regulation",
            "Public concern about AI safety is increasing",
        ],
        importance_score=0.9,
    )

    print(f"Topic: {event.title}")
    print(f"Question: {event.description}\n")
    print("Starting debate...\n")

    # Create output handler
    output = StreamOutput(log_to_file=False)

    # Start debate
    session = await council.start_debate(
        event=event,
        format=DebateFormat.ROUNDTABLE,
        num_agents=3,
        max_rounds=3
    )

    output.start_session(session)

    # Run opening round
    await council._opening_round(session)
    for round in session.rounds:
        output.output_round(round, session)

    # Run one main round
    await council._debate_round(session, 1)
    new_rounds = session.rounds[-3:]
    for round in new_rounds:
        output.output_round(round, session)

    # Closing statements
    await council._closing_round(session)
    new_rounds = session.rounds[-3:]
    for round in new_rounds:
        output.output_round(round, session)

    # Voting
    voting_result = await council._conduct_voting(session)
    session.voting_result = voting_result

    output.output_voting(voting_result)
    output.output_summary(session)

    print("\n" + "="*80)
    print("✓ Demo complete!")
    print("="*80 + "\n")

    print("💡 Next steps:")
    print("  1. Set OPENAI_API_KEY or ANTHROPIC_API_KEY for real AI responses")
    print("  2. Run: python main.py --topic 'Your debate topic'")
    print("  3. Try continuous mode: python main.py --continuous --num-debates 5")
    print("  4. Explore the code in core/ directory")
    print("\n")


if __name__ == "__main__":
    asyncio.run(run_demo())
