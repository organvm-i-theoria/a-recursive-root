# AI Agents Module

**Version**: 0.1.0
**Location**: `/workspace/projects/ai-council-system/core/agents/`

## Overview

The AI Agents module provides the core agent implementation for AI Council System debates. Agents have distinct personalities, memory systems, and can participate in debates through responses and voting.

## Components

### Agent (`agent.py`)
Core agent class with personality, memory, and debate capabilities.

**Key Features**:
- Personality-driven responses
- Memory integration
- Voting logic
- State management
- Response history tracking

### LLM Provider (`llm_provider.py`)
Abstraction layer for multiple LLM providers (Claude, GPT-4, Grok).

**Supported Providers**:
- **Claude**: Anthropic's Claude models
- **GPT**: OpenAI's GPT models
- **Grok**: xAI's Grok models
- **Mock**: Testing provider

### Memory Manager (`memory.py`)
Short-term and long-term memory with semantic search.

**Features**:
- Short-term working memory
- Long-term consolidated storage
- Semantic search and retrieval
- Importance-based retention
- Memory consolidation

### Personalities (`personalities.py`)
15 predefined personality archetypes for diverse debates.

**Available Personalities**:
- Pragmatist, Idealist, Skeptic
- Optimist, Contrarian, Mediator
- Analyst, Visionary, Traditionalist
- Revolutionary, Economist, Ethicist
- Technologist, Populist, Philosopher

## Quick Start

### Basic Agent Creation

```python
from core.agents import Agent, LLMProviderFactory, get_personality, MemoryManager

# Create LLM provider
llm_provider = LLMProviderFactory.create_claude(
    model="claude-3-5-sonnet-20250219",
    api_key="your-api-key"
)

# Get personality
personality = get_personality("pragmatist")

# Create memory manager
memory = MemoryManager(agent_id="agent_001")

# Create agent
agent = Agent(
    agent_id="agent_001",
    personality=personality,
    llm_provider=llm_provider,
    memory_manager=memory
)

# Initialize
await agent.initialize()
```

### Generating Responses

```python
from core.agents import DebateContext

# Set debate context
context = DebateContext(
    topic="Should AI be regulated?",
    description="Debate on AI regulation",
    perspectives=["pro-regulation", "anti-regulation"],
    background_info={},
    participants=["agent_001", "agent_002"],
    rules={}
)

await agent.set_context(context)

# Generate response
response = await agent.respond(
    "What is your position on AI regulation?",
    context=context
)

print(f"Response: {response.content}")
print(f"Confidence: {response.confidence}")
```

### Voting

```python
# Cast vote
vote = await agent.vote(
    options=["Regulate AI heavily", "Light regulation", "No regulation"],
    context=context
)

print(f"Voted for: {vote.option}")
print(f"Reasoning: {vote.reasoning}")
print(f"Weight: {vote.weight}")
```

### Memory Management

```python
# Store memory
await agent.memory_manager.store(
    content="AI regulation is crucial for safety",
    memory_type="fact",
    importance=0.8
)

# Retrieve relevant memories
memories = await agent.memory_manager.retrieve_relevant(
    query="regulation",
    limit=5
)

# Get recent memories
recent = await agent.memory_manager.retrieve_recent(limit=10)

# Get important memories
important = await agent.memory_manager.retrieve_important(
    min_importance=0.7
)
```

## Personalities in Detail

### The Pragmatist
- **Traits**: High analytical (0.9), moderate creativity (0.4)
- **Focus**: Practical solutions and evidence-based approaches
- **Speaking Style**: Direct and concise
- **Best For**: Policy debates, technical discussions

### The Idealist
- **Traits**: High empathy (0.9), high creativity (0.8)
- **Focus**: Vision, principles, greater good
- **Speaking Style**: Inspirational and passionate
- **Best For**: Philosophical debates, ethical discussions

### The Skeptic
- **Traits**: Very high analytical (0.95), very high skepticism (0.95)
- **Focus**: Critical analysis, questioning assumptions
- **Speaking Style**: Analytical and challenging
- **Best For**: Scientific debates, fact-checking

### The Mediator
- **Traits**: Very high empathy (0.95), balanced analytical (0.7)
- **Focus**: Finding common ground and consensus
- **Speaking Style**: Diplomatic and inclusive
- **Best For**: Conflict resolution, synthesizing viewpoints

### Custom Personalities

```python
from core.agents import create_custom_personality

custom = create_custom_personality(
    name="The Data Scientist",
    archetype="scientist",
    traits={
        "analytical": 0.95,
        "creativity": 0.7,
        "empathy": 0.6,
        "skepticism": 0.8,
        "confidence": 0.8,
        "verbosity": 0.6,
    },
    background="A data scientist who relies on statistical analysis",
    speaking_style="Data-driven and precise, citing statistics",
    values=["Evidence", "Statistics", "Reproducibility"],
    biases=["May overemphasize quantitative over qualitative data"]
)
```

## LLM Provider Configuration

### Claude

```python
provider = LLMProviderFactory.create_claude(
    model="claude-3-5-sonnet-20250219",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    default_temperature=0.7,
    default_max_tokens=1000
)
```

### GPT-4

```python
provider = LLMProviderFactory.create_gpt(
    model="gpt-4-turbo",
    api_key=os.getenv("OPENAI_API_KEY"),
    default_temperature=0.7,
    default_max_tokens=1000
)
```

### Grok

```python
provider = LLMProviderFactory.create_grok(
    model="grok-1",
    api_key=os.getenv("XAI_API_KEY"),
    default_temperature=0.7,
    default_max_tokens=1000
)
```

### Mock (Testing)

```python
provider = LLMProviderFactory.create_mock(
    responses=[
        "This is my first response",
        "This is my second response"
    ]
)
```

## Memory System Architecture

### Short-Term Memory
- **Capacity**: 100 entries (configurable)
- **Purpose**: Recent interactions, working memory
- **Retention**: FIFO when at capacity

### Long-Term Memory
- **Capacity**: 10,000 entries (configurable)
- **Purpose**: Important memories, consolidated knowledge
- **Retention**: Importance-based pruning

### Consolidation
- **Trigger**: When short-term reaches 80% capacity
- **Threshold**: Importance >= 0.6 or access_count >= 3
- **Process**: Move important memories to long-term storage

### Semantic Search
```python
# Generate embeddings for memory content
# Calculate relevance using:
# - Embedding similarity (60%)
# - Importance score (30%)
# - Recency factor (10%)
```

## Agent States

```python
class AgentState(Enum):
    IDLE = "idle"           # Ready for new tasks
    THINKING = "thinking"   # Processing input
    RESPONDING = "responding"  # Generating response
    VOTING = "voting"       # Casting vote
    ERROR = "error"         # Error state
```

## Response Generation Flow

1. **Context Setup**: Load debate context and relevant memories
2. **Prompt Building**: Combine personality, context, and prompt
3. **Memory Retrieval**: Fetch relevant past interactions
4. **LLM Generation**: Generate response via LLM provider
5. **Confidence Calculation**: Assess response confidence
6. **Memory Storage**: Store interaction in memory
7. **History Tracking**: Add to response history

## Voting Flow

1. **Vote Prompt**: Build voting prompt with options and context
2. **Decision Generation**: LLM generates vote with reasoning
3. **Parsing**: Extract selected option and reasoning
4. **Weight Calculation**: Calculate vote weight based on conviction
5. **Storage**: Store vote in history and memory

## Best Practices

### Agent Creation
- Always initialize agents before use
- Match personality to debate role
- Configure appropriate LLM provider
- Enable memory for continuity

### Response Generation
- Provide clear debate context
- Use appropriate temperature for task
- Monitor confidence scores
- Review response history

### Memory Management
- Store important interactions
- Set appropriate importance scores
- Periodically review consolidation
- Clear memory when starting fresh context

### Testing
- Use MockLLMProvider for unit tests
- Test with various personalities
- Validate memory retrieval
- Monitor LLM usage statistics

## Performance Considerations

### Memory Usage
- Short-term: ~100 KB per 100 entries
- Long-term: ~10 MB per 10,000 entries
- Embeddings: ~64 bytes per entry (16 floats)

### LLM Costs
- Claude: ~$3 per million input tokens
- GPT-4: ~$10 per million input tokens
- Optimize with caching and batching

### Response Times
- Memory retrieval: <10ms
- LLM generation: 1-5 seconds
- Total response time: 1-6 seconds

## Future Enhancements

### Phase 2
- Multi-agent conversations
- Agent learning from feedback
- Advanced memory consolidation
- Emotion modeling

### Phase 3
- Real-time personality adaptation
- Cross-agent memory sharing
- Advanced reasoning chains
- Self-reflection capabilities

### Phase 4
- Autonomous goal setting
- Complex multi-turn strategies
- Meta-cognitive abilities
- Personality evolution

## Examples

See `/tests/agents/` for comprehensive examples:
- `test_agent_creation.py` - Agent setup and configuration
- `test_debate_participation.py` - Full debate scenarios
- `test_memory_system.py` - Memory operations
- `test_personalities.py` - Personality behaviors

---

**Module Status**: Phase 1 Complete
**Last Updated**: October 23, 2025
**Maintainer**: Development Team
