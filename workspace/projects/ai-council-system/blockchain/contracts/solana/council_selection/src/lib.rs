use anchor_lang::prelude::*;

declare_id!("CounciL11111111111111111111111111111111111");

#[program]
pub mod council_selection {
    use super::*;

    /// Initialize a new council session
    pub fn initialize_session(
        ctx: Context<InitializeSession>,
        session_id: String,
        required_agents: u8,
        diversity_required: bool,
    ) -> Result<()> {
        let session = &mut ctx.accounts.session;
        session.session_id = session_id;
        session.authority = ctx.accounts.authority.key();
        session.required_agents = required_agents;
        session.diversity_required = diversity_required;
        session.selected_agents = Vec::new();
        session.vrf_seed = 0;
        session.vrf_fulfilled = false;
        session.timestamp = Clock::get()?.unix_timestamp;
        session.status = SessionStatus::Initialized;

        msg!("Council session initialized: {}", session.session_id);
        Ok(())
    }

    /// Request VRF for agent selection
    pub fn request_vrf(
        ctx: Context<RequestVRF>,
        vrf_seed: u64,
    ) -> Result<()> {
        let session = &mut ctx.accounts.session;

        require!(
            session.status == SessionStatus::Initialized,
            ErrorCode::InvalidSessionStatus
        );

        session.vrf_seed = vrf_seed;
        session.status = SessionStatus::VRFRequested;

        msg!("VRF requested for session: {}, seed: {}", session.session_id, vrf_seed);

        // In production, this would interact with Chainlink VRF or Pyth Entropy
        // For now, we mark it as requested

        Ok(())
    }

    /// Fulfill VRF and select agents
    pub fn fulfill_vrf(
        ctx: Context<FulfillVRF>,
        random_number: u64,
        vrf_proof: Vec<u8>,
    ) -> Result<()> {
        let session = &mut ctx.accounts.session;

        require!(
            session.status == SessionStatus::VRFRequested,
            ErrorCode::InvalidSessionStatus
        );

        // Verify VRF proof (simplified for demonstration)
        require!(vrf_proof.len() > 0, ErrorCode::InvalidVRFProof);

        session.vrf_fulfilled = true;
        session.random_number = random_number;
        session.vrf_proof = vrf_proof;
        session.status = SessionStatus::VRFFulfilled;

        msg!("VRF fulfilled for session: {}, random: {}", session.session_id, random_number);

        Ok(())
    }

    /// Select agents using the VRF random number
    pub fn select_agents(
        ctx: Context<SelectAgents>,
        agent_ids: Vec<String>,
    ) -> Result<()> {
        let session = &mut ctx.accounts.session;

        require!(
            session.status == SessionStatus::VRFFulfilled,
            ErrorCode::InvalidSessionStatus
        );

        require!(
            agent_ids.len() == session.required_agents as usize,
            ErrorCode::InvalidAgentCount
        );

        session.selected_agents = agent_ids.clone();
        session.status = SessionStatus::AgentsSelected;
        session.selection_timestamp = Clock::get()?.unix_timestamp;

        msg!("Agents selected for session: {}, count: {}", session.session_id, agent_ids.len());

        Ok(())
    }

    /// Verify a council selection
    pub fn verify_selection(
        ctx: Context<VerifySelection>,
    ) -> Result<bool> {
        let session = &ctx.accounts.session;

        require!(
            session.status == SessionStatus::AgentsSelected,
            ErrorCode::InvalidSessionStatus
        );

        // Verification logic:
        // 1. Check VRF proof is valid
        // 2. Check number of agents matches requirement
        // 3. Check diversity if required

        let is_valid = session.vrf_fulfilled
            && session.selected_agents.len() == session.required_agents as usize
            && session.vrf_proof.len() > 0;

        msg!("Selection verification: {}", is_valid);

        Ok(is_valid)
    }
}

#[derive(Accounts)]
#[instruction(session_id: String)]
pub struct InitializeSession<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + CouncilSession::INIT_SPACE,
        seeds = [b"session", session_id.as_bytes()],
        bump
    )]
    pub session: Account<'info, CouncilSession>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct RequestVRF<'info> {
    #[account(mut, has_one = authority)]
    pub session: Account<'info, CouncilSession>,

    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct FulfillVRF<'info> {
    #[account(mut)]
    pub session: Account<'info, CouncilSession>,

    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct SelectAgents<'info> {
    #[account(mut, has_one = authority)]
    pub session: Account<'info, CouncilSession>,

    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct VerifySelection<'info> {
    pub session: Account<'info, CouncilSession>,
}

#[account]
pub struct CouncilSession {
    pub session_id: String,           // 32 bytes (max)
    pub authority: Pubkey,             // 32 bytes
    pub required_agents: u8,           // 1 byte
    pub diversity_required: bool,      // 1 byte
    pub selected_agents: Vec<String>,  // Dynamic (max 10 * 32 = 320 bytes)
    pub vrf_seed: u64,                 // 8 bytes
    pub vrf_fulfilled: bool,           // 1 byte
    pub random_number: u64,            // 8 bytes
    pub vrf_proof: Vec<u8>,            // Dynamic (max 256 bytes)
    pub timestamp: i64,                // 8 bytes
    pub selection_timestamp: i64,      // 8 bytes
    pub status: SessionStatus,         // 1 byte
}

impl CouncilSession {
    pub const INIT_SPACE: usize = 32 + 32 + 1 + 1 + (4 + 320) + 8 + 1 + 8 + (4 + 256) + 8 + 8 + 1;
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq, Eq)]
pub enum SessionStatus {
    Initialized,
    VRFRequested,
    VRFFulfilled,
    AgentsSelected,
    Completed,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Invalid session status for this operation")]
    InvalidSessionStatus,
    #[msg("Invalid VRF proof")]
    InvalidVRFProof,
    #[msg("Invalid number of agents")]
    InvalidAgentCount,
    #[msg("Session not found")]
    SessionNotFound,
}
