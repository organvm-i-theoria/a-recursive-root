[![ORGAN-I: Theory](https://img.shields.io/badge/ORGAN--I-Theory-1a237e?style=flat-square)](https://github.com/organvm-i-theoria) [![Python 3.11+](https://img.shields.io/badge/python-3.11+-3776ab?style=flat-square&logo=python&logoColor=white)]() [![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](governance/licenses/MIT.md) [![Status: Prototype](https://img.shields.io/badge/status-prototype-yellow?style=flat-square)]()

# A Recursive Root

**Multi-agent deliberation architecture that treats structured disagreement as an epistemic method — nine personality archetypes, three debate formats, swappable LLM backends, and event-driven synthesis for emergent collective intelligence.**

*The name "A Recursive Root" points to the project's foundational claim: that intelligence recurses. A root that is recursive is a starting point that contains its own elaboration — a seed whose growth pattern is already encoded in its origin. In the Western philosophical tradition, this is anamnesis (Plato) or the self-unfolding of Geist (Hegel). In computer science, it is the fixed-point combinator. This repository is the root of a recursive inquiry: can multi-agent systems, by debating themselves, produce insight that no single agent could reach alone?*

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Core Concepts](#core-concepts)
  - [Personality Archetypes as Epistemic Dispositions](#personality-archetypes-as-epistemic-dispositions)
  - [The Deliberation Protocol](#the-deliberation-protocol)
  - [Emergent Intelligence Through Structured Disagreement](#emergent-intelligence-through-structured-disagreement)
  - [LLM Provider Abstraction](#llm-provider-abstraction)
  - [Event-Driven Debate Ingestion](#event-driven-debate-ingestion)
- [Architecture](#architecture)
  - [System Design](#system-design)
  - [Agent Structure](#agent-structure)
  - [Debate Flow](#debate-flow)
  - [The Z Cartridge Scaffold](#the-z-cartridge-scaffold)
- [Installation & Usage](#installation--usage)
- [Examples](#examples)
  - [Example 1: Three-Agent Roundtable on AI Governance](#example-1-three-agent-roundtable-on-ai-governance)
  - [Example 2: Custom Agent Configuration with Named Archetypes](#example-2-custom-agent-configuration-with-named-archetypes)
  - [Example 3: Programmatic Council with Live LLM Provider](#example-3-programmatic-council-with-live-llm-provider)
- [Downstream Implementation](#downstream-implementation)
- [Validation](#validation)
- [Roadmap](#roadmap)
- [Cross-References](#cross-references)
- [Contributing](#contributing)
- [License](#license)
- [Author & Contact](#author--contact)

---

## Problem Statement

Single-perspective reasoning — whether from a human expert or a frontier LLM — carries inherent blind spots. The standard approach to AI-assisted reasoning asks one model to generate one answer. But intelligence at scale has always been **dialogical**: peer review, parliamentary debate, adversarial collaboration, jury deliberation, the Socratic elenchus. These processes produce better outcomes not despite disagreement but *because of it*.

The AI Council System formalizes this insight into a working architecture. Rather than asking "What does one agent think?", it asks: **"What emerges when agents with fundamentally different epistemic dispositions are forced to confront the same question under structured rules?"**

Current multi-agent frameworks (AutoGen, CrewAI, LangGraph) optimize for task decomposition — splitting a problem into subtasks and assigning them to specialists. This is useful, but it is not deliberation. Deliberation requires that agents hold *incompatible positions* and be forced to engage with each other's reasoning. The intellectual gap this project fills is the gap between **multi-agent orchestration** (agents cooperating on a task) and **multi-agent deliberation** (agents contesting a question).

This is a theory-first project within ORGAN-I (Theoria). The goal is not to ship a product but to explore a question: can structured multi-agent disagreement produce reasoning that is qualitatively different from — and potentially superior to — single-agent generation? The prototype says yes, provisionally. The research continues.

---

## Core Concepts

### Personality Archetypes as Epistemic Dispositions

Each council agent embodies a distinct epistemic disposition defined as an `AgentPersonality` enum. These are not cosmetic labels — they condition the underlying LLM's system prompt and shape how the agent frames problems, weighs evidence, and responds to opposition:

| Archetype | Disposition | Reasoning Tendency |
|-----------|-------------|-------------------|
| **Optimist** | Possibility-oriented | Sees opportunity, highlights potential upside, imagines best cases |
| **Pessimist** | Risk-oriented | Identifies failure modes, stress-tests assumptions, anticipates downsides |
| **Pragmatist** | Implementation-oriented | Asks "Will this actually work?", grounds discussion in constraints |
| **Idealist** | Principle-oriented | Driven by values and ideals, even when they seem impractical |
| **Contrarian** | Opposition-oriented | Deliberately opposes emerging consensus to test its robustness |
| **Moderate** | Balance-oriented | Seeks compromise, finds merit in multiple viewpoints |
| **Radical** | Transformation-oriented | Advocates for fundamental change, challenges incrementalism |
| **Conservative** | Stability-oriented | Values tradition, caution, and incremental change |
| **Progressive** | Reform-oriented | Pushes for forward-thinking solutions and systemic reform |

These archetypes are defined in `core/agents/base_agent.py` as an enum and mapped to natural-language personality descriptions that become part of each agent's system prompt:

```python
class AgentPersonality(Enum):
    OPTIMIST = "optimist"
    PESSIMIST = "pessimist"
    PRAGMATIST = "pragmatist"
    IDEALIST = "idealist"
    CONTRARIAN = "contrarian"
    MODERATE = "moderate"
    RADICAL = "radical"
    CONSERVATIVE = "conservative"
    PROGRESSIVE = "progressive"
```

The extended personality system in `workspace/projects/ai-council-system/core/agents/personalities.py` provides 15 richer archetypes — Philosopher, Ethicist, Technologist, Economist, Revolutionary, Mediator, and others — each defined with numerical trait vectors (analytical, creativity, empathy, skepticism, confidence, verbosity), backstories, speaking styles, explicit values, and documented biases. This dual-layer design means the core `AgentPersonality` enum is lightweight enough for the prototype while the extended `PERSONALITIES` dictionary supports arbitrarily rich characterization for production use.

### The Deliberation Protocol

The council supports four structured debate formats, each suited to different kinds of questions:

- **Roundtable** (`DebateFormat.ROUNDTABLE`) — All agents speak in sequence across multiple rounds. Each agent sees all previous contributions and must engage with (not merely acknowledge) opposing positions. Best for open-ended exploration where you want the full epistemic landscape mapped.

- **One-on-One** (`DebateFormat.ONE_ON_ONE`) — Two agents with opposing dispositions debate directly while a moderator agent summarizes. Best for binary decisions or sharpening a specific tension between two perspectives.

- **Panel** (`DebateFormat.PANEL`) — A subset of agents presents positions to a designated evaluator. Best for structured assessment where you want a clear judgment rendered.

- **Free-for-All** (`DebateFormat.FREE_FOR_ALL`) — Unmoderated discussion where agents respond to whichever previous argument they find most salient. Best for discovering unexpected argument trajectories.

The debate lifecycle follows a state machine: `INITIALIZING -> OPENING -> DEBATING -> VOTING -> CONCLUDED` (or `ERROR`). Each transition is logged, and every round emits structured data that can be observed, replayed, or fed into downstream analysis.

### Emergent Intelligence Through Structured Disagreement

After deliberation, agents cast votes with confidence scores and optional reasoning. The system produces a synthesis that identifies:

- **Points of consensus** — where archetypes converge despite fundamentally different reasoning paths, suggesting robust conclusions.
- **Persistent disagreements** — where the question genuinely resists resolution, suggesting that the disagreement is structural rather than accidental.
- **Conditional positions** — where agreement depends on specific assumptions being true, revealing the decision's sensitivity to context.

This output is more useful than a single answer because it **maps the epistemic landscape** of a question rather than collapsing it to one position. A hiring manager reading this output sees not "the answer" but "the argument space" — which positions are defensible, which are contested, and where the real uncertainty lives.

The voting system tracks per-agent confidence, vote weight, and reasoning. The `VotingResult` dataclass computes a winner, total votes, and a consensus-level metric (winner's proportion of total weight), providing a quantitative summary of how contested or settled the question turned out to be.

### LLM Provider Abstraction

The `DebateAgent` class implements a clean provider abstraction layer. LLM backends are fully swappable at agent instantiation:

```python
# Auto-detect from environment variables
agent = DebateAgent(config, provider="auto")

# Explicit provider selection
agent_openai = DebateAgent(config, provider="openai")
agent_claude = DebateAgent(config, provider="anthropic")
agent_mock = DebateAgent(config, provider="mock")
```

The auto-detection logic checks for `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` in the environment, falling back gracefully to the mock provider if neither is found. This means the system is always runnable — you never need an API key to explore the architecture, run tests, or demonstrate the debate flow. The mock provider generates personality-appropriate responses using rule-based templates: optimists support, pessimists oppose, pragmatists equivocate, contrarians dissent.

If a live provider fails mid-debate (network error, rate limit, malformed response), the agent falls back to mock generation rather than crashing the session. This resilience-by-default design means a debate always completes, even under degraded conditions.

### Event-Driven Debate Ingestion

The `EventIngester` class provides a unified interface for sourcing debate topics from multiple feeds:

```python
class EventSource(Enum):
    TWITTER = "twitter"
    NEWS = "news"
    REDDIT = "reddit"
    MANUAL = "manual"
    RSS = "rss"
    CRYPTO_FEED = "crypto_feed"
```

Each event carries a title, description, source attribution, category tag (politics, technology, economics, AI, crypto, etc.), a list of factual claims, an importance score, and optional metadata. Events are queued by importance and timestamp, ensuring the council always debates the most significant available topic.

The manual event source allows programmatic injection of arbitrary debate topics, making the system useful as a structured reasoning tool for any question — not just real-time news. The crypto and news feeds currently use mock data generators that produce realistic events for demonstration purposes.

---

## Architecture

### System Design

The working core is a Python package under `core/` with four modules:

```
core/
├── __init__.py
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Abstract base: personality, memory, opinion formation, response
│   └── debate_agent.py        # Concrete agent with LLM provider abstraction + mock client
├── council/
│   ├── __init__.py
│   └── council.py             # Council orchestration: agent selection, debate lifecycle, voting
├── events/
│   ├── __init__.py
│   └── event_ingestion.py     # Event sourcing: multi-feed ingestion, queuing, topic conversion
├── rng/
│   └── __init__.py            # Random number generation (stub for future verifiable randomness)
└── visualization.py           # Output formatting: console colors, file logging, session summaries
```

A parallel, more elaborate implementation exists under `workspace/projects/ai-council-system/` with additional modules for streaming (avatar generation, TTS, background compositing), blockchain integration (Solana smart contracts for immutable debate records), swarm orchestration (multi-council coordination), and a Next.js web frontend. These are aspirational — structurally present, functionally placeholder. The authoritative working code is in `core/`.

### Agent Structure

The agent hierarchy follows a clean abstract-base pattern:

```
BaseAgent (ABC)
├── agent_id: UUID
├── config: AgentConfig
│   ├── name, personality, model, temperature, max_tokens
│   ├── backstory, expertise_areas
│   └── bias_level (0.0-1.0), debating_style
├── conversation_history: List[Dict]
├── stance_history: List[Dict]
├── form_opinion(topic, facts, previous_arguments) -> Dict[stance, argument, confidence]
├── respond_to_argument(argument, opponent_name, context) -> str
└── generate_response(prompt, context) -> str  [abstract]

DebateAgent(BaseAgent)
├── provider: str ("openai" | "anthropic" | "mock")
├── client: AsyncOpenAI | AsyncAnthropic | MockLLMClient
├── _detect_provider() -> str
├── _generate_openai(prompt, context) -> str
├── _generate_anthropic(prompt, context) -> str
└── _generate_mock(prompt, context) -> str
```

`AgentConfig` is a dataclass that bundles all agent parameters: name, personality enum, LLM model string, temperature, max tokens, optional backstory, expertise areas, bias level (0.0 neutral to 1.0 heavy), and debating style (analytical, emotional, humorous, aggressive). This configuration object is the single point of control for an agent's character.

### Debate Flow

A complete debate session proceeds through these phases:

1. **Agent Selection** — The council selects participants from its agent pool, optionally ensuring personality diversity (no two agents with the same archetype).

2. **Opening Round** — Each agent calls `form_opinion()`, which builds a personality-conditioned prompt, sends it to the LLM provider, and parses the structured response into stance/argument/confidence.

3. **Debate Rounds** (configurable, default 4) — Each agent selects a random opponent from the previous round's speakers and calls `respond_to_argument()`, generating a rebuttal conditioned on the opponent's statement and the agent's own personality.

4. **Closing Round** — Each agent generates a final summary statement.

5. **Voting** — Mock voting assigns randomized scores weighted by contribution count. In production, this would use the extended voting system with weighted confidence and explicit reasoning.

6. **Synthesis** — The `VotingResult` identifies the winner, total votes, and confidence ratio. The `DebateFormatter` renders a full transcript with color-coded rounds, voting bar charts, and a session summary.

### The Z Cartridge Scaffold

The repository's outer structure follows a "Z Cartridge" directory-template framework with placeholders for governance, containers, environment configuration, observability, and workspace organization. This scaffold represents intentional infrastructure — where the project aims to grow — but most of these directories currently contain only placeholder READMEs. The intellectual substance lives in `core/`, `main.py`, `demo.py`, and the test suite.

---

## Installation & Usage

**Requirements:** Python 3.11+. No API keys required for the demo.

```bash
# Clone
git clone https://github.com/organvm-i-theoria/a-recursive-root.git
cd a-recursive-root

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the demo — mock provider, no API keys needed
python demo.py

# Run with CLI arguments
python main.py --provider mock --topic "Should recursion be the foundation of all intelligence?"

# Run continuous mode (multiple debates)
python main.py --continuous --num-debates 5 --agents 4

# Run with a live LLM
export OPENAI_API_KEY="sk-..."
python main.py --provider openai --topic "Is consciousness computable?"

# Or with Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
python main.py --provider anthropic --topic "Should AI systems be designed to disagree?"
```

**CLI Arguments:**

| Flag | Default | Description |
|------|---------|-------------|
| `--provider` | `auto` | LLM backend: `openai`, `anthropic`, `mock`, or `auto` |
| `--agents` | `4` | Number of agents in the council (max 6) |
| `--topic` | *(from event feed)* | Specific debate topic |
| `--continuous` | `false` | Run multiple debates sequentially |
| `--num-debates` | `3` | Number of debates in continuous mode |

**Running Tests:**

```bash
pytest tests/ -v
```

---

## Examples

### Example 1: Three-Agent Roundtable on AI Governance

The built-in demo (`demo.py`) instantiates three agents — Optimist, Skeptic, Pragmatist — and runs a roundtable on "The Future of AI Governance":

```bash
python demo.py
```

Output (abbreviated, using mock provider):

```
========================================
AI COUNCIL DEBATE SESSION
========================================
Topic: The Future of AI Governance
Participants: Optimist (optimist), Skeptic (pessimist), Pragmatist (pragmatist)
Format: roundtable | Max Rounds: 3

--- OPENING STATEMENT - Optimist ---
STANCE: support
ARGUMENT: I believe this represents a positive development that could lead to
beneficial outcomes. We should carefully consider all perspectives before proceeding.
CONFIDENCE: 0.8

--- OPENING STATEMENT - Skeptic ---
STANCE: oppose
ARGUMENT: I have concerns about the potential risks and unintended consequences
of this approach. We should carefully consider all perspectives before proceeding.
CONFIDENCE: 0.7

--- OPENING STATEMENT - Pragmatist ---
STANCE: neutral
ARGUMENT: I see merit in both perspectives and believe we need more information
to make a determination.
CONFIDENCE: 0.6

--- ROUND 1 - Optimist -> Skeptic ---
I appreciate your perspective, but I think we should focus on the opportunities
here rather than the obstacles.

--- VOTING RESULTS ---
Winner: Pragmatist (47 votes, 38.2%)
Total Votes: 123
```

### Example 2: Custom Agent Configuration with Named Archetypes

The `main.py` entry point creates six named agents with mythological identities, each mapped to a personality archetype and given a backstory and expertise areas:

```python
from core.agents.base_agent import AgentConfig, AgentPersonality
from core.agents.debate_agent import DebateAgent
from core.council.council import Council

council = Council(name="Philosophy Council")

# Prometheus: the optimist who stole fire for humanity
prometheus = DebateAgent(AgentConfig(
    name="Prometheus",
    personality=AgentPersonality.OPTIMIST,
    backstory="A forward-thinking agent who believes in progress and innovation",
    expertise_areas=["technology", "innovation", "future trends"],
    temperature=0.8,
), provider="mock")

# Cassandra: the pessimist cursed to see disasters no one believes
cassandra = DebateAgent(AgentConfig(
    name="Cassandra",
    personality=AgentPersonality.PESSIMIST,
    backstory="A cautious agent who focuses on risks and potential downsides",
    expertise_areas=["risk analysis", "security", "ethics"],
    temperature=0.7,
), provider="mock")

# Socrates: the contrarian who questions everything
socrates = DebateAgent(AgentConfig(
    name="Socrates",
    personality=AgentPersonality.CONTRARIAN,
    backstory="A questioning agent who challenges assumptions",
    expertise_areas=["philosophy", "logic", "critical thinking"],
    temperature=0.9,
), provider="mock")

council.add_agent(prometheus)
council.add_agent(cassandra)
council.add_agent(socrates)
```

The mythological naming is deliberate: it makes the agents' dispositions immediately legible. Prometheus is optimistic because that is who Prometheus *is*. Cassandra warns because she must. Socrates questions because the unexamined argument is not worth debating.

### Example 3: Programmatic Council with Live LLM Provider

For researchers who want to run councils programmatically and capture structured output:

```python
import asyncio
from core.council.council import Council, DebateFormat
from core.events.event_ingestion import Event, EventSource, EventCategory
from datetime import datetime

async def run_research_debate():
    council = Council(name="Research Council")
    # ... add agents ...

    event = Event(
        event_id="research_001",
        title="Recursive Self-Improvement in AI Systems",
        description="Can an AI system meaningfully improve its own reasoning "
                    "architecture, or is recursive self-improvement a "
                    "philosophical impossibility?",
        source=EventSource.MANUAL,
        category=EventCategory.AI,
        timestamp=datetime.utcnow(),
        facts=[
            "No AI system has demonstrated unbounded self-improvement",
            "Current LLMs can critique and revise their own outputs",
            "Goedel's incompleteness theorems constrain formal self-reference",
            "Biological evolution is a form of recursive self-improvement",
        ],
        importance_score=0.95,
    )

    session = await council.start_debate(
        event=event,
        format=DebateFormat.ROUNDTABLE,
        num_agents=4,
        max_rounds=5
    )
    completed = await council.run_debate(session)

    # Structured output
    print(completed.get_transcript())
    print(f"Winner: {completed.voting_result.winner_agent}")
    print(f"Consensus: {completed.voting_result.confidence:.1%}")

asyncio.run(run_research_debate())
```

---

## Downstream Implementation

The AI Council System is a **theory prototype** within ORGAN-I (Theoria). Its concepts flow downstream through the organ system:

- **ORGAN-II (Poiesis)** — The deliberation transcripts and personality archetypes inform generative art projects in [organvm-ii-poiesis](https://github.com/organvm-ii-poiesis). The `metasystem-master` project draws on the same recursive-systems vocabulary that structures this council's debate model.

- **ORGAN-III (Ergon)** — If the deliberation architecture proves robust enough for production use, it would be productized through [organvm-iii-ergon](https://github.com/organvm-iii-ergon) as a structured-reasoning API or decision-support tool.

- **ORGAN-IV (Taxis)** — The governance and orchestration patterns (agent selection, state machine lifecycle, voting protocols) inform the orchestration work in [organvm-iv-taxis](https://github.com/organvm-iv-taxis), particularly the `agentic-titan` multi-agent coordination framework.

The dependency flow respects the invariant: I -> II -> III only. ORGAN-III never depends on ORGAN-II; ORGAN-II never depends on ORGAN-III. Theory flows forward; it does not flow back.

---

## Validation

**What works (prototype-validated):**

- Multi-agent debate execution across all four formats with mock LLM provider
- Nine personality archetypes with distinct, prompt-conditioned reasoning styles
- LLM provider abstraction with graceful fallback (OpenAI, Anthropic, Mock)
- Event ingestion from manual, news, and crypto feeds (mock data)
- Voting with confidence scoring and winner determination
- Console output with color-coded transcripts, voting bars, and leaderboards
- File-based debate logging for session replay
- Agent statistics tracking (contributions, wins, history)
- Test suite covering agent creation, opinion formation, debate execution, and leaderboard

**What is aspirational (structurally present, not yet functional):**

- Blockchain integration for immutable debate records (Solana contracts in `workspace/`)
- Streaming/avatar system for visual real-time debate (compositor + TTS stubs)
- Next.js web frontend for debate observation and configuration
- Full Z Cartridge scaffold (containers, observability, governance)
- Formal Python packaging (`pyproject.toml` or `setup.py`)
- Extended personality system integration with core debate loop

This distinction matters. The prototype demonstrates that structured multi-agent deliberation is architecturally tractable and produces interesting output. The aspirational features represent where the concept could go, not where it is today.

---

## Roadmap

**Near-term (Silver Sprint):**
- Add formal Python packaging with `pyproject.toml`
- Integrate extended personality system (`PERSONALITIES` dict) into core debate loop
- Add MIT LICENSE file at repo root
- Clean up or explicitly document placeholder directories
- Expand test coverage for event ingestion and visualization

**Medium-term:**
- Debate transcript export (JSON, Markdown, structured data)
- Retrieval-augmented agents that can cite sources during debate
- Debate quality metrics: convergence rate, argument diversity index, consensus stability over rounds
- Cross-council deliberation — councils of councils, recursive structure
- Integration with `recursive-engine` for shared recursive-systems primitives

**Long-term (if the prototype validates):**
- Persistent debate memory across sessions (agent learning)
- Web interface for debate configuration, observation, and replay
- Live LLM provider benchmarking — do different models produce systematically different debate dynamics?
- Academic paper: "Structured Disagreement as Epistemic Method in Multi-Agent LLM Systems"

---

## Cross-References

This repository is part of **ORGAN-I (Theoria)** — the theoretical research organ exploring epistemology, recursion, and ontological frameworks.

**Related ORGAN-I repositories:**

| Repository | Relationship |
|-----------|-------------|
| [`recursive-engine`](https://github.com/organvm-i-theoria/recursive-engine) | Core recursive system engine; provides the foundational architecture that informs this project's recursive deliberation model |
| [`recursive-ontology`](https://github.com/organvm-i-theoria/recursive-ontology) | Formal ontology for recursive systems; supplies the conceptual vocabulary for understanding agent-system relationships |
| [`a-i-council--coliseum`](https://github.com/organvm-i-theoria/a-i-council--coliseum) | Related council architecture explorations and earlier prototypes |

**The eight-organ system:**

| Organ | Domain | Organization |
|-------|--------|-------------|
| I | Theory | [organvm-i-theoria](https://github.com/organvm-i-theoria) *(this organ)* |
| II | Art | [organvm-ii-poiesis](https://github.com/organvm-ii-poiesis) |
| III | Commerce | [organvm-iii-ergon](https://github.com/organvm-iii-ergon) |
| IV | Orchestration | [organvm-iv-taxis](https://github.com/organvm-iv-taxis) |
| V | Public Process | [organvm-v-logos](https://github.com/organvm-v-logos) |
| VI | Community | [organvm-vi-koinonia](https://github.com/organvm-vi-koinonia) |
| VII | Distribution | [organvm-vii-kerygma](https://github.com/organvm-vii-kerygma) |
| VIII | Meta | [meta-organvm](https://github.com/meta-organvm) |

---

## Contributing

Contributions are welcome. This is a theory-first project, so contributions that deepen the intellectual foundations are valued as highly as code improvements.

**High-value contribution areas:**
- Expanding the personality archetype system with new dispositions and trait vectors
- Implementing debate quality metrics (argument diversity, convergence analysis)
- Adding new debate formats (Socratic dialogue, Oxford-style, fishbowl)
- Improving the mock provider to generate more realistic personality-differentiated responses
- Writing tests for edge cases (single-agent debates, all-same-personality councils)
- Connecting the extended personality system to the core debate loop

**Process:** Fork, branch, PR. Keep PRs focused and atomic. Describe the "why" in your PR description.

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community standards.

---

## License

MIT. See [`governance/licenses/MIT.md`](governance/licenses/MIT.md).

---

## Author & Contact

**[@4444J99](https://github.com/4444J99)** — Part of [ORGAN-I: Theoria](https://github.com/organvm-i-theoria)

This repository is one node in an eight-organ creative-institutional system. For the broader context, see [meta-organvm](https://github.com/meta-organvm).

---

*Last updated: February 2026*
