#!/bin/bash
set -euo pipefail

echo "[install_ai_clis] Installing AI command-line interfaces..."

# Check for required tools
check_command() {
  if ! command -v "$1" &> /dev/null; then
    echo "Warning: $1 is not installed. Please install it first."
    return 1
  fi
  return 0
}

# Install Python dependencies
if check_command pip3; then
  echo "Installing Python AI packages from requirements.txt..."
  pip3 install -r requirements.txt
elif check_command pip; then
  echo "Installing Python AI packages from requirements.txt..."
  pip install -r requirements.txt
else
  echo "Warning: pip not found. Skipping Python package installation."
fi

# Install GitHub Copilot CLI
if check_command npm; then
  echo "Installing GitHub Copilot CLI..."
  npm install -g @githubnext/github-copilot-cli
else
  echo "Warning: npm not found. Skipping GitHub Copilot CLI installation."
  echo "To install npm, please visit: https://nodejs.org/"
fi

# Check if gh CLI is available for GitHub Copilot integration
if check_command gh; then
  echo "GitHub CLI detected. You can configure Copilot with: gh copilot"
else
  echo "Note: GitHub CLI (gh) not found. Install it for better Copilot integration."
  echo "Visit: https://cli.github.com/"
fi

echo ""
echo "[install_ai_clis] Installation complete!"
echo ""
echo "Installed CLIs:"
echo "  - OpenAI Python client (use 'openai' in Python scripts)"
echo "  - Anthropic Claude Python client (use 'anthropic' in Python scripts)"
echo "  - GitHub Copilot CLI (use 'github-copilot-cli' command if npm installed)"
echo ""
echo "Next steps:"
echo "  1. Set up API keys in your environment:"
echo "     export OPENAI_API_KEY='your-key-here'"
echo "     export ANTHROPIC_API_KEY='your-key-here'"
echo "  2. For GitHub Copilot, authenticate with: gh auth login"
echo "  3. See README.md for usage instructions"
