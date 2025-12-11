"""
Token Manager for SPL token operations.

Handles creation, minting, transfers, and management of the AI Council Token (ACT).
"""

import logging
import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


@dataclass
class TokenInfo:
    """Information about the AI Council Token."""
    name: str
    symbol: str
    decimals: int
    total_supply: int
    mint_address: str
    mint_authority: Optional[str]
    freeze_authority: Optional[str]
    created_at: datetime
    circulating_supply: int
    metadata: Dict[str, Any]


@dataclass
class TokenAccount:
    """Token account information."""
    address: str
    owner: str
    balance: int
    is_frozen: bool
    created_at: datetime


class TokenManager:
    """
    Manages AI Council Token (ACT) operations.

    Provides comprehensive SPL token functionality including:
    - Token creation and initialization
    - Minting and burning
    - Transfers between wallets
    - Balance checking
    - Supply management

    Example:
        token_mgr = TokenManager()

        # Create token
        token = await token_mgr.create_token(
            name="AI Council Token",
            symbol="ACT",
            decimals=9,
            total_supply=1_000_000_000
        )

        # Mint to address
        await token_mgr.mint_tokens(recipient, 1000)

        # Transfer
        await token_mgr.transfer(from_wallet, to_wallet, 500)
    """

    def __init__(
        self,
        network: str = "devnet",
        token_mint: Optional[str] = None
    ):
        """
        Initialize Token Manager.

        Args:
            network: Solana network (devnet, testnet, mainnet)
            token_mint: Existing token mint address (None to create new)
        """
        self.network = network
        self.token_mint = token_mint or os.getenv('TOKEN_MINT_ADDRESS')

        # Mock mode for development
        self.mock_mode = os.getenv('SOLANA_MOCK_MODE', 'true').lower() == 'true'

        # Token configuration
        self.token_name = "AI Council Token"
        self.token_symbol = "ACT"
        self.token_decimals = 9
        self.total_supply = 1_000_000_000 * (10 ** self.token_decimals)

        # Distribution allocation (in tokens, not including decimals)
        self.allocations = {
            "community_rewards": 400_000_000,
            "team_development": 200_000_000,
            "treasury_dao": 200_000_000,
            "initial_liquidity": 100_000_000,
            "ecosystem_partners": 100_000_000,
        }

        if self.mock_mode:
            logger.warning("Token Manager running in MOCK MODE")
            self._mock_balances: Dict[str, int] = {}
            self._mock_circulating = 500_000_000 * (10 ** self.token_decimals)
        else:
            logger.info(f"Token Manager initialized on {network}")

    async def create_token(
        self,
        name: str,
        symbol: str,
        decimals: int,
        total_supply: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TokenInfo:
        """
        Create a new SPL token.

        Args:
            name: Token name
            symbol: Token symbol (e.g., "ACT")
            decimals: Number of decimals
            total_supply: Total supply (before decimals)
            metadata: Additional metadata

        Returns:
            TokenInfo: Created token information

        Example:
            token = await mgr.create_token("AI Council Token", "ACT", 9, 1_000_000_000)
        """
        if self.mock_mode:
            # Mock token creation
            token_info = TokenInfo(
                name=name,
                symbol=symbol,
                decimals=decimals,
                total_supply=total_supply * (10 ** decimals),
                mint_address=f"mock_mint_{symbol.lower()}",
                mint_authority="mock_authority",
                freeze_authority=None,
                created_at=datetime.now(),
                circulating_supply=0,
                metadata=metadata or {}
            )

            self.token_mint = token_info.mint_address
            logger.info(f"Mock token created: {symbol}")

            return token_info

        # TODO: Implement real SPL token creation
        # from solana.rpc.async_api import AsyncClient
        # from spl.token.async_client import AsyncToken
        # from spl.token.instructions import create_mint

        raise NotImplementedError("Real token creation not implemented. Use SOLANA_MOCK_MODE=true")

    async def mint_tokens(
        self,
        recipient: str,
        amount: int,
        decimals_applied: bool = False
    ) -> str:
        """
        Mint tokens to a recipient.

        Args:
            recipient: Recipient wallet address
            amount: Amount to mint
            decimals_applied: Whether amount already includes decimals

        Returns:
            str: Transaction signature

        Example:
            tx = await mgr.mint_tokens("wallet_address", 1000)
        """
        if not decimals_applied:
            amount = amount * (10 ** self.token_decimals)

        if self.mock_mode:
            # Mock minting
            if recipient not in self._mock_balances:
                self._mock_balances[recipient] = 0

            self._mock_balances[recipient] += amount
            self._mock_circulating += amount

            logger.info(f"Mock minted {amount / (10 ** self.token_decimals)} ACT to {recipient}")

            return f"mock_mint_tx_{recipient}"

        raise NotImplementedError("Real token minting not implemented")

    async def transfer(
        self,
        from_wallet: str,
        to_wallet: str,
        amount: int,
        decimals_applied: bool = False
    ) -> str:
        """
        Transfer tokens between wallets.

        Args:
            from_wallet: Sender wallet address
            to_wallet: Recipient wallet address
            amount: Amount to transfer
            decimals_applied: Whether amount includes decimals

        Returns:
            str: Transaction signature

        Example:
            tx = await mgr.transfer(wallet1, wallet2, 500)
        """
        if not decimals_applied:
            amount = amount * (10 ** self.token_decimals)

        if self.mock_mode:
            # Check balance
            from_balance = self._mock_balances.get(from_wallet, 0)
            if from_balance < amount:
                raise ValueError(f"Insufficient balance: {from_balance} < {amount}")

            # Transfer
            self._mock_balances[from_wallet] -= amount

            if to_wallet not in self._mock_balances:
                self._mock_balances[to_wallet] = 0

            self._mock_balances[to_wallet] += amount

            logger.info(f"Mock transferred {amount / (10 ** self.token_decimals)} ACT from {from_wallet} to {to_wallet}")

            return f"mock_transfer_tx_{from_wallet}_{to_wallet}"

        raise NotImplementedError("Real token transfer not implemented")

    async def burn(
        self,
        wallet: str,
        amount: int,
        decimals_applied: bool = False
    ) -> str:
        """
        Burn tokens (remove from circulation).

        Args:
            wallet: Wallet to burn from
            amount: Amount to burn
            decimals_applied: Whether amount includes decimals

        Returns:
            str: Transaction signature

        Example:
            tx = await mgr.burn(wallet, 100)
        """
        if not decimals_applied:
            amount = amount * (10 ** self.token_decimals)

        if self.mock_mode:
            # Check balance
            balance = self._mock_balances.get(wallet, 0)
            if balance < amount:
                raise ValueError(f"Insufficient balance to burn: {balance} < {amount}")

            # Burn
            self._mock_balances[wallet] -= amount
            self._mock_circulating -= amount

            logger.info(f"Mock burned {amount / (10 ** self.token_decimals)} ACT from {wallet}")

            return f"mock_burn_tx_{wallet}"

        raise NotImplementedError("Real token burning not implemented")

    async def get_balance(
        self,
        wallet: str,
        include_decimals: bool = False
    ) -> Decimal:
        """
        Get token balance for a wallet.

        Args:
            wallet: Wallet address
            include_decimals: Return raw balance with decimals

        Returns:
            Decimal: Token balance

        Example:
            balance = await mgr.get_balance(wallet)
        """
        if self.mock_mode:
            raw_balance = self._mock_balances.get(wallet, 0)

            if include_decimals:
                return Decimal(raw_balance)
            else:
                return Decimal(raw_balance) / Decimal(10 ** self.token_decimals)

        raise NotImplementedError("Real balance check not implemented")

    async def get_total_supply(self, include_decimals: bool = False) -> Decimal:
        """
        Get total token supply.

        Args:
            include_decimals: Return raw supply with decimals

        Returns:
            Decimal: Total supply

        Example:
            supply = await mgr.get_total_supply()
        """
        if include_decimals:
            return Decimal(self.total_supply)
        else:
            return Decimal(self.total_supply) / Decimal(10 ** self.token_decimals)

    async def get_circulating_supply(self, include_decimals: bool = False) -> Decimal:
        """
        Get circulating token supply.

        Args:
            include_decimals: Return raw supply with decimals

        Returns:
            Decimal: Circulating supply

        Example:
            circulating = await mgr.get_circulating_supply()
        """
        if self.mock_mode:
            if include_decimals:
                return Decimal(self._mock_circulating)
            else:
                return Decimal(self._mock_circulating) / Decimal(10 ** self.token_decimals)

        raise NotImplementedError("Real circulating supply check not implemented")

    async def get_token_info(self) -> TokenInfo:
        """
        Get comprehensive token information.

        Returns:
            TokenInfo: Complete token details

        Example:
            info = await mgr.get_token_info()
            print(f"Symbol: {info.symbol}, Supply: {info.total_supply}")
        """
        if self.mock_mode:
            return TokenInfo(
                name=self.token_name,
                symbol=self.token_symbol,
                decimals=self.token_decimals,
                total_supply=self.total_supply,
                mint_address=self.token_mint or "mock_mint_act",
                mint_authority="mock_authority",
                freeze_authority=None,
                created_at=datetime.now(),
                circulating_supply=self._mock_circulating,
                metadata={
                    "description": "AI Council governance token",
                    "allocations": self.allocations
                }
            )

        raise NotImplementedError("Real token info not implemented")

    async def create_token_account(self, owner: str) -> TokenAccount:
        """
        Create associated token account for owner.

        Args:
            owner: Wallet address

        Returns:
            TokenAccount: Created account info

        Example:
            account = await mgr.create_token_account(wallet)
        """
        if self.mock_mode:
            # Initialize balance if needed
            if owner not in self._mock_balances:
                self._mock_balances[owner] = 0

            return TokenAccount(
                address=f"mock_ata_{owner}",
                owner=owner,
                balance=self._mock_balances[owner],
                is_frozen=False,
                created_at=datetime.now()
            )

        raise NotImplementedError("Real token account creation not implemented")

    def format_amount(self, amount: int, decimals_applied: bool = True) -> str:
        """
        Format token amount for display.

        Args:
            amount: Token amount
            decimals_applied: Whether amount includes decimals

        Returns:
            str: Formatted amount (e.g., "1,000.5 ACT")

        Example:
            formatted = mgr.format_amount(1000500000000)  # "1,000.5 ACT"
        """
        if decimals_applied:
            tokens = Decimal(amount) / Decimal(10 ** self.token_decimals)
        else:
            tokens = Decimal(amount)

        # Format with commas and symbol
        return f"{tokens:,.{self.token_decimals}f} {self.token_symbol}".rstrip('0').rstrip('.')

    async def distribute_initial_allocation(self) -> Dict[str, str]:
        """
        Distribute initial token allocation to wallets.

        Returns:
            Dict[str, str]: Allocation name -> transaction signature

        Example:
            txs = await mgr.distribute_initial_allocation()
        """
        if self.mock_mode:
            transactions = {}

            # Mock wallet addresses for each allocation
            allocation_wallets = {
                "community_rewards": "wallet_community",
                "team_development": "wallet_team",
                "treasury_dao": "wallet_treasury",
                "initial_liquidity": "wallet_liquidity",
                "ecosystem_partners": "wallet_ecosystem",
            }

            for allocation_name, amount in self.allocations.items():
                wallet = allocation_wallets[allocation_name]
                tx = await self.mint_tokens(wallet, amount)
                transactions[allocation_name] = tx

                logger.info(f"Allocated {amount:,} ACT to {allocation_name}")

            return transactions

        raise NotImplementedError("Real allocation distribution not implemented")
