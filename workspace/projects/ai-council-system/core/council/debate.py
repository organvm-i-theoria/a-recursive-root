"""
Debate - Debate session orchestration

Manages debate sessions, rounds, and outcomes.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import asyncio

logger = logging.getLogger(__name__)


class SessionState(Enum):
    """Debate session states"""
    INITIALIZING = "initializing"
    OPENING = "opening"
    DEBATING = "debating"
    VOTING = "voting"
    CONCLUDED = "concluded"
    ERROR = "error"


class RoundType(Enum):
    """Types of debate rounds"""
    OPENING = "opening"
    REBUTTAL = "rebuttal"
    DISCUSSION = "discussion"
    CLOSING = "closing"


@dataclass
class Round:
    """Represents a debate round"""
    round_number: int
    round_type: RoundType
    responses: List[Dict[str, Any]] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "round_number": self.round_number,
            "round_type": self.round_type.value,
            "responses": self.responses,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }


@dataclass
class DebateSession:
    """
    Represents a debate session

    A session encompasses the full debate from opening to conclusion.
    """
    session_id: str
    council_id: str
    topic: Dict[str, Any]
    participants: List[str]  # Agent IDs
    state: SessionState = SessionState.INITIALIZING
    rounds: List[Round] = field(default_factory=list)
    votes: List[Dict[str, Any]] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    outcome: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "council_id": self.council_id,
            "topic": self.topic,
            "participants": self.participants,
            "state": self.state.value,
            "rounds": [r.to_dict() for r in self.rounds],
            "votes": self.votes,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "outcome": self.outcome,
            "metadata": self.metadata,
        }


class DebateSessionManager:
    """
    Manages debate sessions

    Orchestrates the debate flow:
    1. Opening statements
    2. Multiple discussion rounds
    3. Voting
    4. Conclusion
    """

    def __init__(self):
        self.sessions: Dict[str, DebateSession] = {}
        self.sessions_created = 0

    async def create_session(
        self,
        council_id: str,
        topic: Dict[str, Any],
        agents: List['Agent'],
        config: Optional[Dict[str, Any]] = None
    ) -> DebateSession:
        """
        Create a new debate session

        Args:
            council_id: Council participating in debate
            topic: Debate topic information
            agents: Agents participating in debate
            config: Optional session configuration

        Returns:
            Created DebateSession
        """
        session_id = self._generate_session_id(council_id)

        config = config or {}
        max_rounds = config.get("max_rounds", 3)
        voting_enabled = config.get("voting_enabled", True)

        session = DebateSession(
            session_id=session_id,
            council_id=council_id,
            topic=topic,
            participants=[a.agent_id for a in agents],
            metadata={
                "max_rounds": max_rounds,
                "voting_enabled": voting_enabled,
                "agent_count": len(agents),
            }
        )

        self.sessions[session_id] = session
        self.sessions_created += 1

        logger.info(
            f"Created debate session {session_id} with {len(agents)} participants"
        )

        return session

    async def run_debate(
        self,
        session_id: str,
        agents: List['Agent'],
        context: 'DebateContext'
    ) -> DebateSession:
        """
        Run complete debate session

        Args:
            session_id: Session to run
            agents: Participating agents
            context: Debate context

        Returns:
            Completed session
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        logger.info(f"Starting debate session {session_id}")

        try:
            # Opening statements
            session.state = SessionState.OPENING
            await self._run_opening(session, agents, context)

            # Discussion rounds
            session.state = SessionState.DEBATING
            max_rounds = session.metadata.get("max_rounds", 3)

            for round_num in range(1, max_rounds + 1):
                await self._run_round(session, round_num, agents, context)

            # Voting
            if session.metadata.get("voting_enabled", True):
                session.state = SessionState.VOTING
                await self._run_voting(session, agents, context)

            # Conclude
            session.state = SessionState.CONCLUDED
            session.end_time = datetime.utcnow()
            await self._conclude_debate(session)

            logger.info(f"Debate session {session_id} concluded")

        except Exception as e:
            logger.error(f"Error in debate session {session_id}: {e}")
            session.state = SessionState.ERROR
            raise

        return session

    async def _run_opening(
        self,
        session: DebateSession,
        agents: List['Agent'],
        context: 'DebateContext'
    ) -> None:
        """Run opening statements round"""
        logger.info("Running opening statements")

        opening_round = Round(
            round_number=0,
            round_type=RoundType.OPENING
        )

        prompt = f"Provide your opening statement on: {context.topic}"

        for agent in agents:
            response = await agent.respond(prompt, context)

            opening_round.responses.append({
                "agent_id": agent.agent_id,
                "agent_name": agent.personality.name,
                "content": response.content,
                "confidence": response.confidence,
                "timestamp": datetime.utcnow().isoformat(),
            })

        opening_round.end_time = datetime.utcnow()
        session.rounds.append(opening_round)

        logger.info(f"Opening round completed with {len(opening_round.responses)} statements")

    async def _run_round(
        self,
        session: DebateSession,
        round_number: int,
        agents: List['Agent'],
        context: 'DebateContext'
    ) -> None:
        """Run a discussion round"""
        logger.info(f"Running discussion round {round_number}")

        discussion_round = Round(
            round_number=round_number,
            round_type=RoundType.DISCUSSION
        )

        # Get previous responses for context
        previous_responses = []
        if session.rounds:
            for r in session.rounds:
                previous_responses.extend(r.responses)

        # Each agent responds
        for agent in agents:
            # Build prompt with previous context
            prompt = f"Round {round_number} - Continue the discussion on: {context.topic}\n\n"

            if previous_responses:
                prompt += "Previous points made:\n"
                # Include last 3 responses for context
                for resp in previous_responses[-3:]:
                    prompt += f"- {resp['agent_name']}: {resp['content'][:100]}...\n"

            response = await agent.respond(prompt, context)

            discussion_round.responses.append({
                "agent_id": agent.agent_id,
                "agent_name": agent.personality.name,
                "content": response.content,
                "confidence": response.confidence,
                "timestamp": datetime.utcnow().isoformat(),
            })

        discussion_round.end_time = datetime.utcnow()
        session.rounds.append(discussion_round)

        logger.info(f"Round {round_number} completed")

    async def _run_voting(
        self,
        session: DebateSession,
        agents: List['Agent'],
        context: 'DebateContext'
    ) -> None:
        """Run voting round"""
        logger.info("Running voting round")

        # Get voting options from context
        voting_options = context.perspectives[:3] if context.perspectives else [
            "Support",
            "Neutral",
            "Oppose"
        ]

        for agent in agents:
            vote = await agent.vote(voting_options, context)

            session.votes.append({
                "agent_id": agent.agent_id,
                "agent_name": agent.personality.name,
                "option": vote.option,
                "weight": vote.weight,
                "reasoning": vote.reasoning,
                "confidence": vote.confidence,
                "timestamp": datetime.utcnow().isoformat(),
            })

        logger.info(f"Voting completed with {len(session.votes)} votes")

    async def _conclude_debate(self, session: DebateSession) -> None:
        """Conclude debate and determine outcome"""
        logger.info(f"Concluding debate session {session.session_id}")

        # Tally votes
        vote_tally = {}
        for vote in session.votes:
            option = vote["option"]
            weight = vote["weight"]
            vote_tally[option] = vote_tally.get(option, 0) + weight

        # Determine winner
        if vote_tally:
            winner = max(vote_tally.items(), key=lambda x: x[1])

            session.outcome = {
                "winner": winner[0],
                "vote_distribution": vote_tally,
                "total_votes": len(session.votes),
                "consensus_level": winner[1] / sum(vote_tally.values()),
                "duration": (session.end_time - session.start_time).total_seconds(),
            }

            logger.info(f"Debate outcome: {winner[0]} (weight: {winner[1]:.2f})")

    def _generate_session_id(self, council_id: str) -> str:
        """Generate unique session ID"""
        timestamp = int(datetime.utcnow().timestamp())
        return f"session_{council_id}_{timestamp}"

    async def get_session_transcript(
        self,
        session_id: str
    ) -> str:
        """
        Generate human-readable transcript

        Args:
            session_id: Session to transcribe

        Returns:
            Formatted transcript
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        lines = []
        lines.append("=" * 70)
        lines.append(f"DEBATE TRANSCRIPT - {session.session_id}")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Topic: {session.topic.get('title', 'Unknown')}")
        lines.append(f"Started: {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Participants: {len(session.participants)}")
        lines.append("")

        # Rounds
        for round in session.rounds:
            lines.append("-" * 70)
            lines.append(f"ROUND {round.round_number}: {round.round_type.value.upper()}")
            lines.append("-" * 70)
            lines.append("")

            for response in round.responses:
                lines.append(f"🎤 {response['agent_name']}:")
                lines.append(f"   {response['content']}")
                lines.append(f"   (Confidence: {response['confidence']:.2f})")
                lines.append("")

        # Votes
        if session.votes:
            lines.append("-" * 70)
            lines.append("VOTING RESULTS")
            lines.append("-" * 70)
            lines.append("")

            for vote in session.votes:
                lines.append(f"🗳️  {vote['agent_name']}: {vote['option']}")
                lines.append(f"   Reasoning: {vote['reasoning'][:150]}...")
                lines.append(f"   Weight: {vote['weight']:.2f}")
                lines.append("")

        # Outcome
        if session.outcome:
            lines.append("=" * 70)
            lines.append("OUTCOME")
            lines.append("=" * 70)
            lines.append("")
            lines.append(f"🏆 Winner: {session.outcome['winner']}")
            lines.append(f"📊 Vote Distribution:")
            for option, weight in session.outcome['vote_distribution'].items():
                lines.append(f"   {option}: {weight:.2f}")
            lines.append(f"📈 Consensus Level: {session.outcome['consensus_level']:.1%}")
            lines.append(f"⏱️  Duration: {session.outcome['duration']:.0f}s")
            lines.append("")

        lines.append("=" * 70)
        lines.append("END OF TRANSCRIPT")
        lines.append("=" * 70)

        return "\n".join(lines)

    def get_session(self, session_id: str) -> Optional[DebateSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)

    def get_active_sessions(self) -> List[DebateSession]:
        """Get all active sessions"""
        return [
            s for s in self.sessions.values()
            if s.state in [SessionState.OPENING, SessionState.DEBATING, SessionState.VOTING]
        ]

    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics"""
        return {
            "sessions_created": self.sessions_created,
            "active_sessions": len(self.get_active_sessions()),
            "total_sessions": len(self.sessions),
        }
