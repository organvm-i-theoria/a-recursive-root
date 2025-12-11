#!/usr/bin/env python3
"""
AI Council System - Main Application

Entry point for the AI Council debate system.
"""

import asyncio
import logging
import argparse
import sys
from datetime import datetime
from typing import List

from core.agents.base_agent import AgentConfig, AgentPersonality
from core.agents.debate_agent import DebateAgent
from core.council.council import Council, DebateFormat
from core.events.event_ingestion import EventIngester, EventSource, EventCategory
from core.visualization import StreamOutput

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ai_council.log')
    ]
)

logger = logging.getLogger(__name__)


class AICouncilApp:
    """Main application for AI Council System"""

    def __init__(self, provider: str = "auto", num_agents: int = 4):
        self.provider = provider
        self.num_agents = num_agents
        self.council = Council(name="The AI Council")
        self.event_ingester = EventIngester()
        self.output = StreamOutput()

        logger.info(f"Initialized AI Council App with {num_agents} agents")

    def setup_agents(self) -> None:
        """Create and configure debate agents"""
        logger.info("Setting up debate agents...")

        # Define agent configurations
        agent_configs = [
            AgentConfig(
                name="Prometheus",
                personality=AgentPersonality.OPTIMIST,
                backstory="A forward-thinking agent who believes in progress and innovation",
                expertise_areas=["technology", "innovation", "future trends"],
                temperature=0.8,
            ),
            AgentConfig(
                name="Cassandra",
                personality=AgentPersonality.PESSIMIST,
                backstory="A cautious agent who focuses on risks and potential downsides",
                expertise_areas=["risk analysis", "security", "ethics"],
                temperature=0.7,
            ),
            AgentConfig(
                name="Athena",
                personality=AgentPersonality.PRAGMATIST,
                backstory="A practical agent focused on real-world implementation",
                expertise_areas=["implementation", "engineering", "operations"],
                temperature=0.6,
            ),
            AgentConfig(
                name="Socrates",
                personality=AgentPersonality.CONTRARIAN,
                backstory="A questioning agent who challenges assumptions",
                expertise_areas=["philosophy", "logic", "critical thinking"],
                temperature=0.9,
            ),
            AgentConfig(
                name="Oracle",
                personality=AgentPersonality.MODERATE,
                backstory="A balanced agent seeking compromise and consensus",
                expertise_areas=["mediation", "analysis", "synthesis"],
                temperature=0.5,
            ),
            AgentConfig(
                name="Catalyst",
                personality=AgentPersonality.RADICAL,
                backstory="A revolutionary agent pushing for transformative change",
                expertise_areas=["disruption", "transformation", "vision"],
                temperature=0.9,
            ),
        ]

        # Create agents up to num_agents
        for config in agent_configs[:self.num_agents]:
            agent = DebateAgent(config, provider=self.provider)
            self.council.add_agent(agent)
            logger.info(f"Created agent: {agent.name} ({agent.personality.value})")

    def setup_event_sources(self) -> None:
        """Configure event sources"""
        logger.info("Setting up event sources...")

        # Enable available sources
        self.event_ingester.enable_source(EventSource.MANUAL)
        self.event_ingester.enable_source(EventSource.CRYPTO_FEED)
        self.event_ingester.enable_source(EventSource.NEWS)

        logger.info(f"Enabled {len(self.event_ingester.active_sources)} event sources")

    async def run_single_debate(self, topic: str = None) -> None:
        """Run a single debate session"""
        logger.info("Starting single debate session...")

        # Get or create event
        if topic:
            event = self.event_ingester.add_manual_event(
                title=topic,
                description=f"Debate on: {topic}",
                category=EventCategory.OTHER,
                facts=[]
            )
        else:
            event = await self.event_ingester.get_next_event()

        if not event:
            logger.error("No event available for debate")
            return

        # Start debate
        session = await self.council.start_debate(
            event=event,
            format=DebateFormat.ROUNDTABLE,
            num_agents=min(3, self.council.get_agent_count()),
            max_rounds=4
        )

        # Output session start
        self.output.start_session(session)

        # Run debate with live output
        await self._run_debate_with_output(session)

        # Show results
        if session.voting_result:
            self.output.output_voting(session.voting_result)

        self.output.output_summary(session)

        # Show leaderboard
        leaderboard = self.council.get_leaderboard()
        if leaderboard:
            self.output.output_leaderboard(leaderboard)

    async def run_continuous(self, num_debates: int = 3) -> None:
        """Run multiple consecutive debates"""
        logger.info(f"Starting continuous mode with {num_debates} debates...")

        for i in range(num_debates):
            logger.info(f"\n{'='*80}\nDEBATE {i+1} of {num_debates}\n{'='*80}\n")
            await self.run_single_debate()
            await asyncio.sleep(2)  # Brief pause between debates

        logger.info("Continuous mode complete")

    async def _run_debate_with_output(self, session) -> None:
        """Run debate and output rounds in real-time"""
        # Opening round
        await self.council._opening_round(session)
        for round in session.rounds:
            self.output.output_round(round, session)
            await asyncio.sleep(0.5)

        # Main rounds
        for round_num in range(1, session.max_rounds):
            await self.council._debate_round(session, round_num)

            # Output new rounds
            new_rounds = session.rounds[-(len(session.participating_agents)):]
            for round in new_rounds:
                self.output.output_round(round, session)
                await asyncio.sleep(0.5)

        # Closing round
        await self.council._closing_round(session)
        new_rounds = session.rounds[-(len(session.participating_agents)):]
        for round in new_rounds:
            self.output.output_round(round, session)
            await asyncio.sleep(0.5)

        # Voting
        voting_result = await self.council._conduct_voting(session)
        session.voting_result = voting_result
        session.ended_at = datetime.utcnow()

        # Add to history
        self.council.session_history.append(session)


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI Council Debate System")

    parser.add_argument(
        "--provider",
        choices=["auto", "openai", "anthropic", "mock"],
        default="auto",
        help="LLM provider to use (default: auto-detect)"
    )

    parser.add_argument(
        "--agents",
        type=int,
        default=4,
        help="Number of agents to create (default: 4)"
    )

    parser.add_argument(
        "--topic",
        type=str,
        help="Specific topic to debate (optional)"
    )

    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Run multiple debates continuously"
    )

    parser.add_argument(
        "--num-debates",
        type=int,
        default=3,
        help="Number of debates in continuous mode (default: 3)"
    )

    args = parser.parse_args()

    # Create app
    app = AICouncilApp(provider=args.provider, num_agents=args.agents)

    # Setup
    app.setup_agents()
    app.setup_event_sources()

    # Run
    try:
        if args.continuous:
            await app.run_continuous(num_debates=args.num_debates)
        else:
            await app.run_single_debate(topic=args.topic)

        logger.info("AI Council session complete!")

    except KeyboardInterrupt:
        logger.info("\nSession interrupted by user")
    except Exception as e:
        logger.error(f"Error during execution: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
