# AI Council System - Quick Start Guide

Welcome to the AI Council System! This guide will help you get started with running AI agent debates.

## 🚀 Quick Start (2 minutes)

### 1. Setup

```bash
# Run the setup script
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

### 2. Run Demo

```bash
# Run the demonstration
python demo.py
```

This will run a quick debate between 3 AI agents on "The Future of AI Governance" in MOCK mode (no API keys required).

### 3. Run Custom Debate

```bash
# Run a debate on your own topic
python main.py --topic "Should cryptocurrencies replace traditional banking?"
```

## 🔧 Configuration

### Using Real AI Models

The system supports OpenAI and Anthropic AI models. Set your API key:

```bash
# For OpenAI (GPT-4, GPT-3.5)
export OPENAI_API_KEY='your-openai-api-key'

# Or for Anthropic (Claude)
export ANTHROPIC_API_KEY='your-anthropic-api-key'
```

Then run with the specific provider:

```bash
python main.py --provider openai --topic "Your topic"
python main.py --provider anthropic --topic "Your topic"
```

### Command Line Options

```bash
python main.py --help

Options:
  --provider {auto,openai,anthropic,mock}
                        LLM provider to use (default: auto-detect)
  --agents AGENTS       Number of agents to create (default: 4)
  --topic TOPIC         Specific topic to debate (optional)
  --continuous          Run multiple debates continuously
  --num-debates NUM     Number of debates in continuous mode (default: 3)
```

## 📊 Usage Examples

### Single Debate

```bash
# Simple debate with auto-detected provider
python main.py --topic "Universal Basic Income: Pros and Cons"

# With specific provider and more agents
python main.py --provider openai --agents 5 --topic "Climate Change Solutions"
```

### Continuous Mode

```bash
# Run 5 consecutive debates on different topics
python main.py --continuous --num-debates 5

# Continuous with specific provider
python main.py --provider anthropic --continuous --num-debates 3
```

### Mock Mode (No API Keys)

```bash
# Run without API keys (uses simulated responses)
python main.py --provider mock --topic "Any topic you want"
```

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=core --cov-report=html

# Run specific test file
pytest tests/test_agents.py -v
```

## 📁 Project Structure

```
.
├── core/                   # Core system components
│   ├── agents/            # AI agent implementations
│   ├── council/           # Council and debate management
│   ├── events/            # Event ingestion system
│   └── visualization.py   # Output formatting
├── tests/                 # Test suite
├── main.py               # Main application
├── demo.py               # Quick demonstration
├── requirements.txt      # Python dependencies
└── setup.sh             # Setup script
```

## 🎯 What the System Does

1. **Creates AI Agents**: Initializes multiple AI agents with different personalities (Optimist, Pessimist, Pragmatist, etc.)

2. **Ingests Events**: Fetches debate topics from various sources (manual, crypto feeds, news, etc.)

3. **Orchestrates Debates**: Runs structured debates with:
   - Opening statements
   - Cross-debate rounds
   - Closing arguments
   - Voting

4. **Outputs Results**: Displays formatted debate transcripts with color coding and statistics

## 🔍 Agent Personalities

The system includes diverse agent personalities:

- **Optimist (Prometheus)**: Focuses on opportunities and positive outcomes
- **Pessimist (Cassandra)**: Highlights risks and potential problems
- **Pragmatist (Athena)**: Focuses on practical, real-world solutions
- **Contrarian (Socrates)**: Questions assumptions and challenges consensus
- **Moderate (Oracle)**: Seeks balance and compromise
- **Radical (Catalyst)**: Pushes for transformative change

## 📝 Output

Debates are displayed in the console with:
- Color-coded speakers
- Round-by-round arguments
- Voting results with visualizations
- Agent statistics and leaderboards

Logs are also saved to:
- `output/debate_[session_id].log` - Individual debate transcripts
- `ai_council.log` - System logs

## 🛠️ Development

### Adding New Agents

```python
from core.agents.base_agent import AgentConfig, AgentPersonality
from core.agents.debate_agent import DebateAgent

config = AgentConfig(
    name="MyAgent",
    personality=AgentPersonality.PRAGMATIST,
    expertise_areas=["economics", "technology"],
    temperature=0.7,
)

agent = DebateAgent(config, provider="auto")
```

### Adding Manual Events

```python
from core.events.event_ingestion import EventIngester, EventCategory

ingester = EventIngester()
event = ingester.add_manual_event(
    title="Your Topic",
    description="Detailed description",
    category=EventCategory.TECHNOLOGY,
    facts=["Fact 1", "Fact 2", "Fact 3"]
)
```

## 🐛 Troubleshooting

### Import Errors

Make sure you've activated the virtual environment:
```bash
source venv/bin/activate
```

### API Errors

- Check your API key is set correctly
- Verify you have credits/quota available
- Try using mock mode: `--provider mock`

### Module Not Found

Reinstall dependencies:
```bash
pip install -r requirements.txt
```

## 📚 Next Steps

1. **Explore the Code**: Check out the `core/` directory to understand the architecture
2. **Customize Agents**: Modify agent personalities and configurations
3. **Add Event Sources**: Integrate real-time data feeds (Twitter, RSS, etc.)
4. **Build Streaming**: Add live streaming output for platforms like Twitch/YouTube
5. **Blockchain Integration**: Implement on-chain RNG and token mechanics

## 🤝 Contributing

This is a prototype system. Areas for improvement:
- Real-time event ingestion from APIs
- Streaming video/audio output
- Blockchain integration
- Web interface
- Advanced debate strategies
- Multi-language support

## 📄 License

See LICENSE file for details.

---

**Need Help?** Check the main README.md or create an issue on GitHub.
