"""Governance Manager for AI Council Token."""

import logging
from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum

logger = logging.getLogger(__name__)


class ProposalStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    SUCCEEDED = "succeeded"
    DEFEATED = "defeated"
    QUEUED = "queued"
    EXECUTED = "executed"
    CANCELLED = "cancelled"


class VoteType(Enum):
    FOR = "for"
    AGAINST = "against"
    ABSTAIN = "abstain"


@dataclass
class Proposal:
    proposal_id: str
    title: str
    description: str
    proposer: str
    created_at: datetime
    voting_starts: datetime
    voting_ends: datetime
    status: ProposalStatus
    votes_for: Decimal
    votes_against: Decimal
    votes_abstain: Decimal
    quorum_required: Decimal
    approval_threshold: float
    executed_at: Optional[datetime] = None


class GovernanceManager:
    MIN_PROPOSAL_STAKE = Decimal(10000)
    QUORUM_PERCENTAGE = 0.10  # 10%
    APPROVAL_THRESHOLD = 0.66  # 66%
    VOTING_PERIOD_DAYS = 7
    TIMELOCK_DAYS = 3

    def __init__(self, staking_manager):
        self.staking_manager = staking_manager
        self._proposals: Dict[str, Proposal] = {}
        self._votes: Dict[str, Dict[str, VoteType]] = {}

    async def create_proposal(self, wallet: str, title: str, description: str) -> Proposal:
        stake = await self.staking_manager.get_stake_info(wallet)
        if not stake or stake.amount < self.MIN_PROPOSAL_STAKE:
            raise ValueError(f"Minimum stake of {self.MIN_PROPOSAL_STAKE} required")

        proposal = Proposal(
            proposal_id=f"prop_{len(self._proposals) + 1}",
            title=title,
            description=description,
            proposer=wallet,
            created_at=datetime.now(),
            voting_starts=datetime.now(),
            voting_ends=datetime.now() + timedelta(days=self.VOTING_PERIOD_DAYS),
            status=ProposalStatus.ACTIVE,
            votes_for=Decimal(0),
            votes_against=Decimal(0),
            votes_abstain=Decimal(0),
            quorum_required=await self.staking_manager.get_total_voting_power() * Decimal(self.QUORUM_PERCENTAGE),
            approval_threshold=self.APPROVAL_THRESHOLD
        )

        self._proposals[proposal.proposal_id] = proposal
        self._votes[proposal.proposal_id] = {}
        logger.info(f"Created proposal: {title}")
        return proposal

    async def vote(self, proposal_id: str, wallet: str, vote_type: VoteType) -> None:
        if proposal_id not in self._proposals:
            raise ValueError("Proposal not found")

        proposal = self._proposals[proposal_id]
        voting_power = await self.staking_manager.calculate_voting_power(wallet)

        if voting_power == 0:
            raise ValueError("No voting power")

        self._votes[proposal_id][wallet] = vote_type

        if vote_type == VoteType.FOR:
            proposal.votes_for += voting_power
        elif vote_type == VoteType.AGAINST:
            proposal.votes_against += voting_power
        else:
            proposal.votes_abstain += voting_power

        logger.info(f"{wallet} voted {vote_type.value} on {proposal_id}")

    async def finalize_proposal(self, proposal_id: str) -> ProposalStatus:
        proposal = self._proposals[proposal_id]
        total_votes = proposal.votes_for + proposal.votes_against + proposal.votes_abstain

        if total_votes < proposal.quorum_required:
            proposal.status = ProposalStatus.DEFEATED
            return proposal.status

        if proposal.votes_for / (proposal.votes_for + proposal.votes_against) >= Decimal(proposal.approval_threshold):
            proposal.status = ProposalStatus.SUCCEEDED
        else:
            proposal.status = ProposalStatus.DEFEATED

        return proposal.status
