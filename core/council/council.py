"""
Council - AI Agent Council Management and Debate Orchestration

Manages councils of AI agents, orchestrates debates, and tracks results.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import asyncio
import random

from ..agents.base_agent import BaseAgent
from ..events.event_ingestion import Event

logger = logging.getLogger(__name__)


class DebateFormat(Enum):
    """Different debate formats"""
    ROUNDTABLE = "roundtable"  # All agents discuss together
    ONE_ON_ONE = "one_on_one"  # Two agents debate
    PANEL = "panel"  # Structured panel discussion
    FREE_FOR_ALL = "free_for_all"  # Unmoderated discussion


@dataclass
class DebateRound:
    """Represents a single round of debate"""
    round_number: int
    speaker: BaseAgent
    statement: str
    responding_to: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    reactions: Dict[str, str] = field(default_factory=dict)


@dataclass
class VotingResult:
    """Results of audience/agent voting"""
    topic: str
    votes: Dict[str, int]  # stance -> count
    winner_agent: Optional[str] = None
    winning_stance: Optional[str] = None
    total_votes: int = 0
    confidence: float = 0.0


@dataclass
class DebateSession:
    """Complete debate session"""
    session_id: str
    event: Event
    participating_agents: List[BaseAgent]
    debate_format: DebateFormat
    rounds: List[DebateRound] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    voting_result: Optional[VotingResult] = None
    max_rounds: int = 5
    round_duration: timedelta = timedelta(seconds=30)

    def add_round(self, round: DebateRound) -> None:
        """Add a debate round"""
        self.rounds.append(round)

    def is_complete(self) -> bool:
        """Check if debate is complete"""
        return len(self.rounds) >= self.max_rounds or self.ended_at is not None

    def get_transcript(self) -> str:
        """Get formatted transcript of debate"""
        lines = [
            f"=== DEBATE SESSION ===",
            f"Topic: {self.event.title}",
            f"Started: {self.started_at}",
            f"Format: {self.debate_format.value}",
            f"Participants: {', '.join(a.name for a in self.participating_agents)}",
            "",
            "=== DEBATE ROUNDS ===",
        ]

        for round in self.rounds:
            lines.append(f"\n--- Round {round.round_number} ---")
            lines.append(f"[{round.timestamp.strftime('%H:%M:%S')}] {round.speaker.name}:")
            lines.append(f"  {round.statement}")

        if self.voting_result:
            lines.append("\n=== VOTING RESULTS ===")
            lines.append(f"Winner: {self.voting_result.winner_agent or 'No clear winner'}")
            lines.append(f"Votes: {self.voting_result.votes}")

        return '\n'.join(lines)


class Council:
    """
    AI Council - Manages agent debates and discussions

    Orchestrates multi-agent debates on real-time topics,
    manages voting, and produces engaging content for streaming.
    """

    def __init__(self, name: str = "AI Council"):
        self.name = name
        self.agents: List[BaseAgent] = []
        self.active_session: Optional[DebateSession] = None
        self.session_history: List[DebateSession] = []
        self.moderator_enabled = True

    def add_agent(self, agent: BaseAgent) -> None:
        """Add an agent to the council"""
        if agent not in self.agents:
            self.agents.append(agent)
            logger.info(f"Added agent {agent.name} to council {self.name}")

    def remove_agent(self, agent_id: str) -> None:
        """Remove an agent from the council"""
        self.agents = [a for a in self.agents if a.agent_id != agent_id]

    def get_agent_count(self) -> int:
        """Get number of agents in council"""
        return len(self.agents)

    def select_agents_for_debate(
        self,
        event: Event,
        num_agents: int = 3,
        ensure_diversity: bool = True
    ) -> List[BaseAgent]:
        """
        Select agents for a debate

        Args:
            event: The event to debate
            num_agents: Number of agents to select
            ensure_diversity: Whether to ensure personality diversity

        Returns:
            List of selected agents
        """
        if len(self.agents) < num_agents:
            logger.warning(f"Not enough agents ({len(self.agents)}) for debate, need {num_agents}")
            return self.agents

        if ensure_diversity:
            # Select agents with different personalities
            selected = []
            personalities_used = set()

            for agent in self.agents:
                if agent.personality not in personalities_used:
                    selected.append(agent)
                    personalities_used.add(agent.personality)

                if len(selected) >= num_agents:
                    break

            # If not enough diverse agents, fill with random
            if len(selected) < num_agents:
                remaining = [a for a in self.agents if a not in selected]
                selected.extend(random.sample(remaining, min(num_agents - len(selected), len(remaining))))

            return selected[:num_agents]
        else:
            return random.sample(self.agents, min(num_agents, len(self.agents)))

    async def start_debate(
        self,
        event: Event,
        format: DebateFormat = DebateFormat.ROUNDTABLE,
        num_agents: int = 3,
        max_rounds: int = 5
    ) -> DebateSession:
        """
        Start a new debate session

        Args:
            event: Event to debate
            format: Debate format
            num_agents: Number of participating agents
            max_rounds: Maximum number of debate rounds

        Returns:
            Created debate session
        """
        if self.active_session and not self.active_session.is_complete():
            logger.warning("Active session exists, ending it first")
            await self.end_debate()

        # Select agents
        participants = self.select_agents_for_debate(event, num_agents)

        # Create session
        session = DebateSession(
            session_id=f"debate_{datetime.utcnow().timestamp()}",
            event=event,
            participating_agents=participants,
            debate_format=format,
            max_rounds=max_rounds,
        )

        self.active_session = session

        logger.info(
            f"Started debate on '{event.title}' with {len(participants)} agents"
        )

        return session

    async def run_debate(self, session: Optional[DebateSession] = None) -> DebateSession:
        """
        Run a complete debate session

        Args:
            session: Session to run (uses active session if None)

        Returns:
            Completed session
        """
        if session is None:
            session = self.active_session

        if not session:
            raise ValueError("No active debate session")

        logger.info(f"Running debate: {session.event.title}")

        # Opening round - each agent forms initial opinion
        await self._opening_round(session)

        # Main debate rounds
        for round_num in range(1, session.max_rounds):
            await self._debate_round(session, round_num)

            if session.is_complete():
                break

        # Closing round - final statements
        await self._closing_round(session)

        # Voting
        voting_result = await self._conduct_voting(session)
        session.voting_result = voting_result

        # End session
        session.ended_at = datetime.utcnow()
        self.session_history.append(session)

        logger.info(f"Debate completed: {session.session_id}")

        return session

    async def _opening_round(self, session: DebateSession) -> None:
        """Opening round where agents form initial opinions"""
        logger.info("Opening round: agents forming opinions")

        for agent in session.participating_agents:
            opinion = await agent.form_opinion(
                topic=session.event.to_debate_topic(),
                facts=session.event.facts,
                previous_arguments=[]
            )

            round = DebateRound(
                round_number=0,
                speaker=agent,
                statement=opinion["argument"],
            )

            session.add_round(round)
            logger.info(f"{agent.name} ({opinion['stance']}): {opinion['argument']}")

    async def _debate_round(self, session: DebateSession, round_num: int) -> None:
        """Execute a debate round with cross-talk"""
        logger.info(f"Debate round {round_num}")

        # Get previous statements
        previous_rounds = session.rounds[-len(session.participating_agents):]

        # Each agent responds to another agent's argument
        for i, agent in enumerate(session.participating_agents):
            # Select another agent's argument to respond to
            other_agents = [a for a in session.participating_agents if a != agent]
            opponent = random.choice(other_agents)

            # Find opponent's last statement
            opponent_rounds = [r for r in previous_rounds if r.speaker == opponent]
            opponent_statement = opponent_rounds[-1].statement if opponent_rounds else "the previous arguments"

            # Generate response
            debate_context = {
                "topic": session.event.to_debate_topic(),
                "facts": session.event.facts,
                "round_number": round_num,
            }

            response = await agent.respond_to_argument(
                original_argument=opponent_statement,
                opponent_name=opponent.name,
                debate_context=debate_context
            )

            round = DebateRound(
                round_number=round_num,
                speaker=agent,
                statement=response,
                responding_to=opponent.name,
            )

            session.add_round(round)
            logger.info(f"{agent.name} -> {opponent.name}: {response}")

            # Small delay for realism
            await asyncio.sleep(0.5)

    async def _closing_round(self, session: DebateSession) -> None:
        """Closing statements from each agent"""
        logger.info("Closing round: final statements")

        for agent in session.participating_agents:
            # Generate closing statement
            prompt = f"""This is your final statement in the debate on: {session.event.title}

Summarize your position in 1-2 sentences and make your strongest final argument.

Your closing statement:"""

            closing = await agent.generate_response(prompt)

            round = DebateRound(
                round_number=session.max_rounds,
                speaker=agent,
                statement=closing,
            )

            session.add_round(round)
            logger.info(f"{agent.name} (closing): {closing}")

    async def _conduct_voting(self, session: DebateSession) -> VotingResult:
        """Conduct voting on debate winner"""
        logger.info("Conducting vote")

        # Simple mock voting based on agent contributions and personality
        votes = {}

        for agent in session.participating_agents:
            # Count agent's contributions
            agent_rounds = [r for r in session.rounds if r.speaker == agent]
            contribution_count = len(agent_rounds)

            # Simple scoring (in real system would be much more sophisticated)
            vote_count = random.randint(10, 100) + (contribution_count * 5)
            votes[agent.name] = vote_count

        total_votes = sum(votes.values())
        winner_name = max(votes.items(), key=lambda x: x[1])[0]
        winner_agent = next((a for a in session.participating_agents if a.name == winner_name), None)

        if winner_agent:
            winner_agent.debate_wins += 1

        result = VotingResult(
            topic=session.event.title,
            votes=votes,
            winner_agent=winner_name,
            total_votes=total_votes,
            confidence=max(votes.values()) / total_votes,
        )

        logger.info(f"Voting complete. Winner: {winner_name} with {votes[winner_name]} votes")

        return result

    async def end_debate(self) -> Optional[DebateSession]:
        """End the active debate"""
        if not self.active_session:
            return None

        session = self.active_session
        session.ended_at = datetime.utcnow()

        self.session_history.append(session)
        self.active_session = None

        logger.info(f"Ended debate session: {session.session_id}")

        return session

    def get_session_count(self) -> int:
        """Get number of completed sessions"""
        return len(self.session_history)

    def get_agent_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all agents"""
        return [agent.get_stats() for agent in self.agents]

    def get_leaderboard(self) -> List[Tuple[str, int]]:
        """Get agent leaderboard by debate wins"""
        stats = [(agent.name, agent.debate_wins) for agent in self.agents]
        stats.sort(key=lambda x: x[1], reverse=True)
        return stats
