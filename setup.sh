#!/bin/bash
# AI Council System - Setup Script

set -e  # Exit on error

echo "================================================"
echo "AI Council System - Setup Script"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || {
    echo "Error: Python 3 not found. Please install Python 3.7 or higher."
    exit 1
}

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate || {
    echo "Error: Failed to activate virtual environment"
    exit 1
}

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✓ Dependencies installed"

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p output
mkdir -p logs
echo "✓ Directories created"

# Check for API keys
echo ""
echo "Checking for API keys..."
if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo ""
    echo "⚠️  WARNING: No API keys found"
    echo ""
    echo "The system will run in MOCK mode (simulated responses)."
    echo ""
    echo "To use real AI models, set one of these environment variables:"
    echo "  export OPENAI_API_KEY='your-key-here'"
    echo "  export ANTHROPIC_API_KEY='your-key-here'"
    echo ""
else
    if [ ! -z "$OPENAI_API_KEY" ]; then
        echo "✓ OpenAI API key found"
    fi
    if [ ! -z "$ANTHROPIC_API_KEY" ]; then
        echo "✓ Anthropic API key found"
    fi
fi

# Make scripts executable
echo ""
echo "Making scripts executable..."
chmod +x main.py demo.py setup.sh

echo ""
echo "================================================"
echo "✓ Setup complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the demo:"
echo "     python demo.py"
echo ""
echo "  3. Run a custom debate:"
echo "     python main.py --topic 'Your topic here'"
echo ""
echo "  4. Run tests:"
echo "     pytest tests/ -v"
echo ""
echo "  5. Run continuous mode:"
echo "     python main.py --continuous --num-debates 3"
echo ""
echo "For more options, run:"
echo "  python main.py --help"
echo ""
