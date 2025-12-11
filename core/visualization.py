"""
Visualization - Output formatting for debates

Provides formatted output for console and future streaming integration.
"""

from typing import List, Optional
from datetime import datetime
import logging

from .council.council import DebateSession, DebateRound, VotingResult
from .agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DebateFormatter:
    """
    Formats debate output for various contexts

    Supports console output, logs, and structured data for streaming.
    """

    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors
        self.color_map = {
            "header": "\033[95m",
            "blue": "\033[94m",
            "cyan": "\033[96m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "red": "\033[91m",
            "bold": "\033[1m",
            "underline": "\033[4m",
            "end": "\033[0m",
        }

    def format_session_start(self, session: DebateSession) -> str:
        """Format debate session start"""
        lines = [
            self._colorize("=" * 80, "bold"),
            self._colorize(f"🎙️  AI COUNCIL DEBATE SESSION", "header", "bold"),
            self._colorize("=" * 80, "bold"),
            "",
            self._colorize(f"Topic: {session.event.title}", "cyan", "bold"),
            f"Description: {session.event.description}",
            "",
            self._colorize(f"Participants:", "yellow"),
        ]

        for agent in session.participating_agents:
            personality = agent.personality.value
            lines.append(f"  • {agent.name} ({personality})")

        lines.extend([
            "",
            self._colorize(f"Format: {session.debate_format.value}", "blue"),
            self._colorize(f"Max Rounds: {session.max_rounds}", "blue"),
            self._colorize("=" * 80, "bold"),
            "",
        ])

        return '\n'.join(lines)

    def format_round(self, round: DebateRound, session: DebateSession) -> str:
        """Format a debate round"""
        lines = []

        # Round header
        if round.round_number == 0:
            header = f"📢 OPENING STATEMENT - {round.speaker.name}"
        elif round.round_number >= session.max_rounds:
            header = f"🏁 CLOSING STATEMENT - {round.speaker.name}"
        else:
            header = f"💬 ROUND {round.round_number} - {round.speaker.name}"

            if round.responding_to:
                header += f" → {round.responding_to}"

        lines.append(self._colorize(header, "green", "bold"))
        lines.append(self._colorize("-" * 80, "green"))

        # Statement
        lines.append(f"{round.statement}")
        lines.append("")

        return '\n'.join(lines)

    def format_voting_results(self, result: VotingResult) -> str:
        """Format voting results"""
        lines = [
            "",
            self._colorize("=" * 80, "bold"),
            self._colorize("🗳️  VOTING RESULTS", "header", "bold"),
            self._colorize("=" * 80, "bold"),
            "",
        ]

        # Sort votes
        sorted_votes = sorted(result.votes.items(), key=lambda x: x[1], reverse=True)

        for i, (agent_name, vote_count) in enumerate(sorted_votes):
            percentage = (vote_count / result.total_votes * 100) if result.total_votes > 0 else 0

            if i == 0:
                color = "green"
                prefix = "🏆 "
            elif i == 1:
                color = "yellow"
                prefix = "🥈 "
            elif i == 2:
                color = "blue"
                prefix = "🥉 "
            else:
                color = None
                prefix = "   "

            bar = "█" * int(percentage / 2)
            line = f"{prefix}{agent_name}: {vote_count} votes ({percentage:.1f}%) {bar}"

            lines.append(self._colorize(line, color) if color else line)

        lines.extend([
            "",
            self._colorize(f"Winner: {result.winner_agent}", "green", "bold"),
            self._colorize(f"Total Votes: {result.total_votes}", "blue"),
            self._colorize("=" * 80, "bold"),
        ])

        return '\n'.join(lines)

    def format_session_summary(self, session: DebateSession) -> str:
        """Format complete session summary"""
        duration = (session.ended_at - session.started_at) if session.ended_at else None

        lines = [
            "",
            self._colorize("=" * 80, "bold"),
            self._colorize("📊 DEBATE SESSION SUMMARY", "header", "bold"),
            self._colorize("=" * 80, "bold"),
            "",
            f"Topic: {session.event.title}",
            f"Total Rounds: {len(session.rounds)}",
            f"Duration: {duration}",
            f"Participants: {len(session.participating_agents)}",
            "",
        ]

        # Agent stats
        lines.append(self._colorize("Agent Contributions:", "yellow"))
        for agent in session.participating_agents:
            agent_rounds = [r for r in session.rounds if r.speaker == agent]
            lines.append(f"  • {agent.name}: {len(agent_rounds)} statements")

        lines.append("")
        lines.append(self._colorize("=" * 80, "bold"))

        return '\n'.join(lines)

    def format_leaderboard(self, leaderboard: List[tuple]) -> str:
        """Format agent leaderboard"""
        lines = [
            "",
            self._colorize("=" * 80, "bold"),
            self._colorize("🏆 AGENT LEADERBOARD", "header", "bold"),
            self._colorize("=" * 80, "bold"),
            "",
        ]

        for i, (agent_name, wins) in enumerate(leaderboard, 1):
            if i == 1:
                prefix = "🥇"
                color = "green"
            elif i == 2:
                prefix = "🥈"
                color = "yellow"
            elif i == 3:
                prefix = "🥉"
                color = "blue"
            else:
                prefix = f"{i}."
                color = None

            line = f"{prefix} {agent_name}: {wins} wins"
            lines.append(self._colorize(line, color, "bold") if color else line)

        lines.append(self._colorize("=" * 80, "bold"))

        return '\n'.join(lines)

    def _colorize(self, text: str, *colors: str) -> str:
        """Apply color codes to text"""
        if not self.use_colors:
            return text

        color_codes = ''.join(self.color_map.get(c, '') for c in colors)
        end_code = self.color_map['end']

        return f"{color_codes}{text}{end_code}"


class StreamOutput:
    """
    Output manager for streaming integration

    Handles output to console, logs, and future streaming platforms.
    """

    def __init__(self, log_to_file: bool = True, output_dir: str = "output"):
        self.formatter = DebateFormatter()
        self.log_to_file = log_to_file
        self.output_dir = output_dir
        self.current_session_log: Optional[str] = None

    def start_session(self, session: DebateSession) -> None:
        """Start outputting a session"""
        if self.log_to_file:
            import os
            os.makedirs(self.output_dir, exist_ok=True)
            self.current_session_log = f"{self.output_dir}/debate_{session.session_id}.log"

        output = self.formatter.format_session_start(session)
        self._output(output)

    def output_round(self, round: DebateRound, session: DebateSession) -> None:
        """Output a debate round"""
        output = self.formatter.format_round(round, session)
        self._output(output)

    def output_voting(self, result: VotingResult) -> None:
        """Output voting results"""
        output = self.formatter.format_voting_results(result)
        self._output(output)

    def output_summary(self, session: DebateSession) -> None:
        """Output session summary"""
        output = self.formatter.format_session_summary(session)
        self._output(output)

    def output_leaderboard(self, leaderboard: List[tuple]) -> None:
        """Output agent leaderboard"""
        output = self.formatter.format_leaderboard(leaderboard)
        self._output(output)

    def _output(self, text: str) -> None:
        """Output text to console and optionally to file"""
        print(text)

        if self.log_to_file and self.current_session_log:
            with open(self.current_session_log, 'a') as f:
                # Strip color codes for file output
                clean_text = self._strip_colors(text)
                f.write(clean_text + '\n')

    def _strip_colors(self, text: str) -> str:
        """Remove ANSI color codes from text"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
