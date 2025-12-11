# AI Council System - Examples

**Working prototypes and integration examples**

## 🚀 Quick Start

### Run the Complete Demo

```bash
cd /workspace/projects/ai-council-system
python examples/demo_debate.py
```

This runs a complete end-to-end AI council debate demonstrating all core functionality.

## 📋 Available Examples

### 1. **demo_debate.py** - Complete Working Prototype
**Status**: ✅ Working
**Runtime**: ~30 seconds
**Dependencies**: None (uses mock LLM)

**What it does**:
- Ingests events from mock sources
- Extracts debate topics automatically
- Forms council with 5 diverse AI personalities
- Runs multi-round structured debate
- Collects votes with reasoning
- Generates complete transcript

**Run it**:
```bash
python examples/demo_debate.py
```

**Sample output**:
```
═══════════════════════════════════════════════════════════════════
  🏛️  AI COUNCIL SYSTEM - WORKING PROTOTYPE
═══════════════════════════════════════════════════════════════════

PHASE 1: Event Ingestion & Topic Selection
─────────────────────────────────────────────────────────────────
✅ Fetched 5 events
✅ Processed 5 events
🔥 Selected for debate: Should AI be regulated?

PHASE 2: Council Formation
─────────────────────────────────────────────────────────────────
✅ Created pool of 5 agents
   - The Pragmatist
   - The Idealist
   - The Skeptic
   - The Economist
   - The Visionary
🏛️  Council formed

PHASE 3: Debate Execution
─────────────────────────────────────────────────────────────────
🎤 Opening Statements
🎤 Round 1: Discussion
🎤 Round 2: Discussion
🗳️  Voting Round
✅ Debate completed!

PHASE 4: Results
─────────────────────────────────────────────────────────────────
🏆 Winner: Support with Caution
📊 Vote Distribution:
   Support with Caution: 3.2
   Strong Regulation: 1.8
📈 Consensus Level: 64%
```

### 2. **comprehensive_integration.py** - Component Integration
**Status**: ✅ Working
**Runtime**: ~20 seconds
**Dependencies**: None (uses mock LLM)

**What it does**:
Demonstrates how each component integrates:
- Event ingestion (Twitter, News, RSS)
- Event processing & enrichment
- Topic extraction
- Queue management
- Agent creation & memory
- Debate context setup
- Sample responses & voting
- Statistics tracking

**Run it**:
```bash
python examples/comprehensive_integration.py
```

## 🎯 Usage Patterns

### Pattern 1: Quick Debate
```python
# Minimal setup for a debate
from demo_debate import main
await main()
```

### Pattern 2: Custom Topic
```python
from core.agents import Agent, get_personality, LLMProviderFactory
from core.council import CouncilManager, DebateSessionManager

# Create agents
agents = [
    Agent("agent_1", get_personality("pragmatist"), llm),
    Agent("agent_2", get_personality("idealist"), llm),
    # ... more agents
]

# Form council and debate
council_mgr = CouncilManager()
debate_mgr = DebateSessionManager()

council = await council_mgr.form_council(topic_id, agents, size=5)
session = await debate_mgr.create_session(council.council_id, topic, agents)
result = await debate_mgr.run_debate(session.session_id, agents, context)

# Get transcript
transcript = await debate_mgr.get_session_transcript(session.session_id)
print(transcript)
```

### Pattern 3: With Real LLMs
```python
# Use real Claude/GPT instead of mock
from core.agents import LLMProviderFactory

# Claude
llm = LLMProviderFactory.create_claude(
    model="claude-3-5-sonnet-20250219",
    api_key="your-api-key"
)

# GPT-4
llm = LLMProviderFactory.create_gpt(
    model="gpt-4-turbo",
    api_key="your-api-key"
)

# Create agents with real LLM
agent = Agent(agent_id, personality, llm_provider=llm)
```

### Pattern 4: Live Event Sources
```python
# Use real Twitter/News APIs
twitter = IngestorFactory.create_twitter(
    api_key=os.getenv("TWITTER_API_KEY"),
    keywords=["AI", "regulation"]
)

news = IngestorFactory.create_news_api(
    api_key=os.getenv("NEWS_API_KEY"),
    sources=["techcrunch", "bbc-news"]
)

# Continuous polling
async def handle_events(events):
    processed = await processor.process_batch(events)
    topics = await extractor.extract_topics(processed)
    # Trigger debate on new topics...

await twitter.start_polling(interval_seconds=60, callback=handle_events)
```

## 🔧 Configuration

### Environment Variables

```bash
# Optional: Use real LLM APIs
export ANTHROPIC_API_KEY="your-claude-key"
export OPENAI_API_KEY="your-gpt-key"
export XAI_API_KEY="your-grok-key"

# Optional: Use real event sources
export TWITTER_API_KEY="your-twitter-key"
export NEWS_API_KEY="your-newsapi-key"
```

### Config Files

Create `config.yaml` for custom settings:
```yaml
debate:
  max_rounds: 3
  council_size: 5
  voting_required: true

agents:
  default_temperature: 0.7
  max_tokens: 1000
  memory_capacity: 100

events:
  poll_interval: 60
  min_controversy: 0.5
  queue_size: 1000
```

## 📊 Output Formats

### Console Output
Default: Human-readable text with colors and formatting

### JSON Output
```python
result = await debate_mgr.run_debate(...)
json_output = result.to_dict()
```

### Transcript File
```python
transcript = await debate_mgr.get_session_transcript(session_id)
with open("debate_transcript.txt", "w") as f:
    f.write(transcript)
```

## 🧪 Testing

Run examples with different configurations:

```bash
# Quick test (1 round, 3 agents)
python examples/demo_debate.py --quick

# Extended test (5 rounds, 7 agents)
python examples/demo_debate.py --extended

# Custom topic
python examples/demo_debate.py --topic "Should cryptocurrency be regulated?"

# Specific personalities
python examples/demo_debate.py --agents pragmatist,skeptic,visionary
```

## 🐛 Troubleshooting

### Import Errors
Make sure you're running from the project root:
```bash
cd /workspace/projects/ai-council-system
python examples/demo_debate.py
```

### Module Not Found
Check sys.path includes project root:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Mock LLM Responses
Mock LLM has limited responses. For varied output, either:
1. Add more mock responses
2. Use real LLM API
3. Implement custom response logic

## 📚 Next Steps

1. **Try with real LLMs**: Replace mock with Claude/GPT
2. **Connect live data**: Use real Twitter/News APIs
3. **Add streaming**: Integrate TTS and visual output
4. **Build UI**: Create web interface for debates
5. **Deploy**: Set up production infrastructure

## 💡 Tips

- Start with `demo_debate.py` to see everything working
- Use `comprehensive_integration.py` to understand components
- Modify examples to test your own debate topics
- Check component READMEs for detailed documentation

---

**All examples are ready to run!**
No external dependencies required for basic functionality.
