use anchor_lang::prelude::*;

declare_id!("Voting11111111111111111111111111111111111");

#[program]
pub mod voting {
    use super::*;

    /// Initialize a new debate session for voting
    pub fn initialize_debate(
        ctx: Context<InitializeDebate>,
        debate_id: String,
        topic: String,
        max_rounds: u8,
    ) -> Result<()> {
        let debate = &mut ctx.accounts.debate;
        debate.debate_id = debate_id;
        debate.topic = topic;
        debate.authority = ctx.accounts.authority.key();
        debate.max_rounds = max_rounds;
        debate.current_round = 0;
        debate.votes = Vec::new();
        debate.timestamp = Clock::get()?.unix_timestamp;
        debate.status = DebateStatus::Active;
        debate.votes_tallied = false;

        msg!("Debate initialized: {}", debate.debate_id);
        Ok(())
    }

    /// Record a vote on-chain
    pub fn cast_vote(
        ctx: Context<CastVote>,
        agent_id: String,
        vote_option: VoteOption,
        confidence: u8,
        reasoning: String,
    ) -> Result<()> {
        let debate = &mut ctx.accounts.debate;

        require!(
            debate.status == DebateStatus::Active,
            ErrorCode::DebateNotActive
        );

        require!(
            confidence <= 100,
            ErrorCode::InvalidConfidence
        );

        // Check if agent already voted
        let existing_vote = debate.votes.iter().find(|v| v.agent_id == agent_id);
        require!(existing_vote.is_none(), ErrorCode::AlreadyVoted);

        let vote = Vote {
            agent_id: agent_id.clone(),
            vote_option,
            confidence,
            reasoning: reasoning.clone(),
            timestamp: Clock::get()?.unix_timestamp,
        };

        debate.votes.push(vote);

        msg!(
            "Vote cast by agent: {}, option: {:?}, confidence: {}",
            agent_id,
            vote_option,
            confidence
        );

        Ok(())
    }

    /// Tally votes and determine outcome
    pub fn tally_votes(
        ctx: Context<TallyVotes>,
    ) -> Result<()> {
        let debate = &mut ctx.accounts.debate;

        require!(
            debate.status == DebateStatus::Active,
            ErrorCode::DebateNotActive
        );

        require!(
            debate.votes.len() > 0,
            ErrorCode::NoVotes
        );

        // Calculate weighted votes
        let mut support_score: f64 = 0.0;
        let mut oppose_score: f64 = 0.0;
        let mut neutral_score: f64 = 0.0;

        for vote in &debate.votes {
            let weight = vote.confidence as f64 / 100.0;
            match vote.vote_option {
                VoteOption::Support => support_score += weight,
                VoteOption::Oppose => oppose_score += weight,
                VoteOption::Neutral => neutral_score += weight,
                VoteOption::Abstain => {},
            }
        }

        // Determine winner
        let outcome = if support_score > oppose_score && support_score > neutral_score {
            VoteOption::Support
        } else if oppose_score > support_score && oppose_score > neutral_score {
            VoteOption::Oppose
        } else {
            VoteOption::Neutral
        };

        debate.outcome = Some(outcome);
        debate.support_score = (support_score * 100.0) as u16;
        debate.oppose_score = (oppose_score * 100.0) as u16;
        debate.neutral_score = (neutral_score * 100.0) as u16;
        debate.votes_tallied = true;
        debate.status = DebateStatus::Completed;
        debate.completion_timestamp = Clock::get()?.unix_timestamp;

        msg!(
            "Votes tallied - Support: {}, Oppose: {}, Neutral: {}, Outcome: {:?}",
            debate.support_score,
            debate.oppose_score,
            debate.neutral_score,
            debate.outcome
        );

        Ok(())
    }

    /// Close a debate (emergency stop)
    pub fn close_debate(
        ctx: Context<CloseDebate>,
    ) -> Result<()> {
        let debate = &mut ctx.accounts.debate;
        debate.status = DebateStatus::Closed;

        msg!("Debate closed: {}", debate.debate_id);
        Ok(())
    }

    /// Get vote results
    pub fn get_results(
        ctx: Context<GetResults>,
    ) -> Result<VoteResults> {
        let debate = &ctx.accounts.debate;

        require!(
            debate.votes_tallied,
            ErrorCode::VotesNotTallied
        );

        Ok(VoteResults {
            debate_id: debate.debate_id.clone(),
            outcome: debate.outcome.unwrap(),
            support_score: debate.support_score,
            oppose_score: debate.oppose_score,
            neutral_score: debate.neutral_score,
            total_votes: debate.votes.len() as u16,
        })
    }
}

#[derive(Accounts)]
#[instruction(debate_id: String)]
pub struct InitializeDebate<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + Debate::INIT_SPACE,
        seeds = [b"debate", debate_id.as_bytes()],
        bump
    )]
    pub debate: Account<'info, Debate>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct CastVote<'info> {
    #[account(mut)]
    pub debate: Account<'info, Debate>,

    pub voter: Signer<'info>,
}

#[derive(Accounts)]
pub struct TallyVotes<'info> {
    #[account(mut, has_one = authority)]
    pub debate: Account<'info, Debate>,

    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct CloseDebate<'info> {
    #[account(mut, has_one = authority)]
    pub debate: Account<'info, Debate>,

    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct GetResults<'info> {
    pub debate: Account<'info, Debate>,
}

#[account]
pub struct Debate {
    pub debate_id: String,            // 32 bytes (max)
    pub topic: String,                 // 128 bytes (max)
    pub authority: Pubkey,             // 32 bytes
    pub max_rounds: u8,                // 1 byte
    pub current_round: u8,             // 1 byte
    pub votes: Vec<Vote>,              // Dynamic (max 20 votes * ~200 bytes = 4000 bytes)
    pub timestamp: i64,                // 8 bytes
    pub completion_timestamp: i64,     // 8 bytes
    pub status: DebateStatus,          // 1 byte
    pub outcome: Option<VoteOption>,   // 2 bytes
    pub support_score: u16,            // 2 bytes
    pub oppose_score: u16,             // 2 bytes
    pub neutral_score: u16,            // 2 bytes
    pub votes_tallied: bool,           // 1 byte
}

impl Debate {
    pub const INIT_SPACE: usize = 32 + 128 + 32 + 1 + 1 + (4 + 4000) + 8 + 8 + 1 + 2 + 2 + 2 + 2 + 1;
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct Vote {
    pub agent_id: String,              // 32 bytes (max)
    pub vote_option: VoteOption,       // 1 byte
    pub confidence: u8,                // 1 byte (0-100)
    pub reasoning: String,             // 128 bytes (max)
    pub timestamp: i64,                // 8 bytes
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq, Debug)]
pub enum VoteOption {
    Support,
    Oppose,
    Neutral,
    Abstain,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq, Eq)]
pub enum DebateStatus {
    Active,
    Completed,
    Closed,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct VoteResults {
    pub debate_id: String,
    pub outcome: VoteOption,
    pub support_score: u16,
    pub oppose_score: u16,
    pub neutral_score: u16,
    pub total_votes: u16,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Debate is not active")]
    DebateNotActive,
    #[msg("Invalid confidence value (must be 0-100)")]
    InvalidConfidence,
    #[msg("Agent has already voted")]
    AlreadyVoted,
    #[msg("No votes recorded")]
    NoVotes,
    #[msg("Votes not yet tallied")]
    VotesNotTallied,
}
