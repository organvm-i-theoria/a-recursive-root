#!/bin/bash
# Deployment script for AI Council Solana programs
# Usage: ./deploy.sh [devnet|testnet|mainnet]

set -e

NETWORK=${1:-devnet}

echo "====================================="
echo "AI Council Solana Program Deployment"
echo "====================================="
echo "Network: $NETWORK"
echo ""

# Check for required tools
if ! command -v anchor &> /dev/null; then
    echo "Error: Anchor CLI not found. Install from https://www.anchor-lang.com/docs/installation"
    exit 1
fi

if ! command -v solana &> /dev/null; then
    echo "Error: Solana CLI not found. Install from https://docs.solana.com/cli/install-solana-cli-tools"
    exit 1
fi

# Set Solana network
echo "Setting Solana cluster to $NETWORK..."
solana config set --url $(solana-cluster-url $NETWORK)

# Check balance
BALANCE=$(solana balance | awk '{print $1}')
echo "Wallet balance: $BALANCE SOL"

if (( $(echo "$BALANCE < 2" | bc -l) )); then
    echo "Warning: Low SOL balance. You may need more for deployment."
    if [ "$NETWORK" == "devnet" ]; then
        echo "Request airdrop: solana airdrop 2"
    fi
fi

echo ""
echo "Building programs..."
echo ""

# Build council selection program
echo "Building council_selection program..."
cd ../council_selection
anchor build

# Build voting program
echo "Building voting program..."
cd ../voting
anchor build

echo ""
echo "Deploying programs to $NETWORK..."
echo ""

# Deploy council selection
echo "Deploying council_selection..."
cd ../council_selection
COUNCIL_PROGRAM_ID=$(anchor deploy --provider.cluster $NETWORK | grep "Program Id:" | awk '{print $3}')
echo "Council Selection Program ID: $COUNCIL_PROGRAM_ID"

# Deploy voting
echo "Deploying voting..."
cd ../voting
VOTING_PROGRAM_ID=$(anchor deploy --provider.cluster $NETWORK | grep "Program Id:" | awk '{print $3}')
echo "Voting Program ID: $VOTING_PROGRAM_ID"

echo ""
echo "====================================="
echo "Deployment Complete!"
echo "====================================="
echo ""
echo "Add these to your .env file:"
echo ""
echo "COUNCIL_SELECTION_PROGRAM_ID=$COUNCIL_PROGRAM_ID"
echo "VOTING_PROGRAM_ID=$VOTING_PROGRAM_ID"
echo "BLOCKCHAIN_NETWORK=$NETWORK"
echo "SOLANA_RPC_URL=$(solana config get | grep 'RPC URL' | awk '{print $3}')"
echo ""
echo "Next steps:"
echo "1. Update .env with program IDs above"
echo "2. Run integration tests: pytest tests/blockchain/"
echo "3. Test with examples: python examples/blockchain_demo.py"
echo ""
