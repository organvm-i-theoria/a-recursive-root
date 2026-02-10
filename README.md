[![ORGAN-I: Theory](https://img.shields.io/badge/ORGAN--I-Theory-1a237e?style=flat-square)](https://github.com/organvm-i-theoria)
[![Python](https://img.shields.io/badge/python-3.11+-3776ab?style=flat-square&logo=python&logoColor=white)]()
[![Status: Prototype](https://img.shields.io/badge/status-prototype-yellow?style=flat-square)]()

# A Recursive Root

**AI Council System — multi-agent debate architecture with personality archetypes, LLM integration, and structured deliberation for emergent collective intelligence.**

> What if disagreement were a feature, not a failure? What if you could engineer a system where opposing viewpoints don't cancel each other out but instead produce insight that none of the participants could have reached alone?

`a-recursive-root` is a Python prototype that explores these questions through a multi-agent debate system. Multiple AI agents — each with a distinct personality archetype and reasoning style — engage in structured deliberation on any topic, producing synthesized positions through formal voting mechanisms. The system treats debate not as rhetoric but as **epistemology**: a method of knowing through structured disagreement.

This repository sits within **ORGAN-I (Theoria)**, the theoretical research arm of the eight-organ system. Its concern is foundational: how do recursive structures of disagreement produce emergent consensus? The AI Council is the working prototype of that inquiry.

---

## Problem Statement: Collective Intelligence Through Structured Disagreement

Single-perspective reasoning — whether from a human or an LLM — carries inherent blind spots. The standard approach to AI-assisted reasoning asks one model to generate one answer. But intelligence at scale has always been **dialogical**: peer review, parliamentary debate, adversarial collaboration, jury deliberation. These processes work not despite disagreement but *because* of it.

The AI Council System formalizes this insight. Rather than asking "What does one agent think?", it asks: **"What emerges when agents with fundamentally different reasoning dispositions are forced to confront the same question under structured rules?"**

This is a theory-first project. The goal is not to build a product but to explore a question: can multi-agent deliberation architectures produce reasoning that is qualitatively different from — and potentially superior to — single-agent generation?

---

## The AI Council Model

### Agent Personality Archetypes

Each council agent embodies a distinct epistemic disposition. These are not cosmetic labels — they shape how the agent frames problems, weighs evidence, and responds to opposing arguments:

| Archetype | Disposition | Reasoning Tendency |
|-----------|-------------|-------------------|
| **Optimist** | Possibility-oriented | Seeks opportunity, highlights potential upside, imagines best cases |
| **Pessimist** | Risk-oriented | Identifies failure modes, stress-tests assumptions, anticipates downsides |
| **Pragmatist** | Implementation-oriented | Asks "Will this actually work?", grounds discussion in constraints |
| **Visionary** | Horizon-oriented | Thinks in long arcs, connects to broader patterns, challenges incrementalism |
| **Analyst** | Evidence-oriented | Demands data, decomposes claims, flags unsupported assertions |
| **Devil's Advocate** | Contrarian-oriented | Deliberately opposes emerging consensus to test its robustness |

These archetypes are defined in `core/agents/debate_agent.py` and are instantiated with system prompts that condition the underlying LLM to reason from that perspective consistently.

### Debate Formats

The system supports three structured deliberation formats, each suited to different kinds of questions:

- **Roundtable** — All agents speak in sequence across multiple rounds. Each agent sees all previous contributions and must engage with (not just ignore) opposing positions. Best for open-ended exploration.
- **One-on-One** — Two agents with opposing dispositions debate directly. A moderator agent summarizes. Best for binary decisions or sharpening a specific tension.
- **Panel** — A subset of agents presents positions to a designated evaluator agent. Best for structured assessment where you want a clear judgment.

### Voting and Synthesis

After deliberation, agents cast votes with confidence scores. The system produces a synthesis that identifies:
- Points of consensus (where archetypes converge despite different reasoning paths)
- Persistent disagreements (where the question genuinely resists resolution)
- Conditional positions (where agreement depends on specific assumptions)

This output is more useful than a single answer because it **maps the epistemic landscape** of a question rather than collapsing it to one position.

---

## Architecture

The working core of the system is a Python package under `core/`:

```
core/
├── agents/
│   ├── base_agent.py          # Abstract base: personality, memory, response generation
│   └── debate_agent.py        # LLM-backed agent with provider abstraction
├── council/
│   └── council.py             # Orchestration: debate flow, turn management, synthesis
├── events/
│   └── event_ingestion.py     # Event bus for debate events (turns, votes, outcomes)
├── llm/
│   ├── openai_provider.py     # OpenAI GPT integration
│   ├── anthropic_provider.py  # Anthropic Claude integration
│   └── mock_provider.py       # Deterministic mock for testing without API keys
└── formats/
    ├── roundtable.py          # Multi-agent sequential deliberation
    ├── one_on_one.py          # Dyadic debate with moderator
    └── panel.py               # Panel presentation to evaluator
```

Key design decisions:
- **Provider abstraction** — LLM backends are swappable. The mock provider allows full debate execution without API keys, which makes the system testable and explorable without cost.
- **Abstract base agent** — `BaseAgent` defines the personality/memory/response interface. `DebateAgent` implements it with LLM providers. This separation means you can implement non-LLM agents (rule-based, retrieval-augmented, etc.) against the same interface.
- **Event-driven debate flow** — Debate turns, votes, and outcomes emit events, allowing observation and logging of the deliberation process.

---

## Quick Start

The system runs with Python 3.11+. No API keys are required for the demo — it uses the mock provider.

```bash
# Clone
git clone https://github.com/organvm-i-theoria/a-recursive-root.git
cd a-recursive-root

# Install dependencies (if any are listed in requirements.txt)
pip install -r requirements.txt 2>/dev/null || true

# Run the demo — mock provider, no API keys needed
python demo.py
```

The demo instantiates a council of agents with different archetypes, runs a roundtable debate on a sample topic, and prints the deliberation transcript with voting results.

To run with a live LLM provider:

```bash
# Set your API key
export OPENAI_API_KEY="sk-..."
# or
export ANTHROPIC_API_KEY="sk-ant-..."

# Run with live provider
python main.py --provider openai --topic "Should AI systems be designed to disagree with each other?"
```

---

## The Z Cartridge Framework

The repository's outer structure follows the "Z Cartridge" framework — a directory-template scaffold with placeholders for governance, containers, environment configuration, observability, and workspace organization. This scaffold is **aspirational infrastructure**. Most of these directories contain placeholder READMEs and no functional code:

```
├── .cartridge/        # Framework metadata
├── containers/        # Docker/container specs (placeholder)
├── environment/       # Environment configuration (placeholder)
├── governance/        # Project governance docs (placeholder)
├── observability/     # Monitoring/logging specs (placeholder)
├── workspace/         # Workspace organization
│   └── projects/
│       └── ai-council-system/  # Mirror of core/ council system
└── core/              # ← The working code lives here
```

The Z Cartridge scaffold represents an intention to grow the project into a full-stack system with containerization, observability, and formal governance. That intention is real but not yet realized. The intellectual substance of this repository is in `core/`, `main.py`, and `demo.py`.

There are also stubs for a **blockchain integration layer** (for immutable debate records) and a **streaming/avatar system** (for real-time visual debate). These are conceptual placeholders — no functional code exists for either.

---

## What Works vs. What's Aspirational

**Working (Prototype):**
- Multi-agent debate execution with mock LLM provider
- Six personality archetypes with distinct reasoning prompts
- Three debate formats (roundtable, one-on-one, panel)
- Voting and confidence scoring
- LLM provider abstraction (OpenAI, Anthropic, Mock)
- Event ingestion for debate observation
- CLI entry points (`main.py`, `demo.py`)

**Aspirational (Stubs/Placeholders):**
- Blockchain integration for immutable debate records
- Streaming/avatar system for visual debate
- Next.js frontend
- Full Z Cartridge scaffold (containers, observability, governance)
- Formal Python packaging (no `setup.py` or `pyproject.toml`)
- Test suite
- LICENSE file

This honesty matters. The prototype demonstrates the *concept* — that structured multi-agent deliberation is architecturally tractable and produces interesting outputs. The aspirational features represent where the concept could go, not where it is.

---

## Roadmap

**Near-term (Silver Sprint):**
- Add formal Python packaging (`pyproject.toml`)
- Write unit tests for agent base class and council orchestration
- Add a LICENSE file (likely MIT or Apache 2.0)
- Clean up placeholder directories — remove or document explicitly

**Medium-term:**
- Debate transcript export (JSON, Markdown)
- Retrieval-augmented agents (agents that can cite sources)
- Debate quality metrics (convergence rate, argument diversity, consensus stability)
- Integration with ORGAN-I's other theory repos (recursive-engine, recursive-ontology)

**Long-term (if the prototype validates):**
- Persistent debate memory across sessions
- Web interface for debate configuration and observation
- Cross-council deliberation (councils of councils — recursive structure)

---

## Cross-References

This repository is part of **ORGAN-I (Theoria)** — the theoretical research organ exploring epistemology, recursion, and ontological frameworks.

Related repositories in ORGAN-I:
- [`recursive-engine`](https://github.com/organvm-i-theoria/recursive-engine) — Core recursive system engine; the foundational architecture that informs this project's recursive deliberation model
- [`recursive-ontology`](https://github.com/organvm-i-theoria/recursive-ontology) — Formal ontology for recursive systems; provides the conceptual vocabulary for understanding agent-system relationships
- [`a-i-council--coliseum`](https://github.com/organvm-i-theoria/a-i-council--coliseum) — Related council architecture explorations

The broader eight-organ system:
- [ORGAN-I: Theoria](https://github.com/organvm-i-theoria) — Theory (this organ)
- [ORGAN-II: Poiesis](https://github.com/organvm-ii-poiesis) — Art and generative works
- [ORGAN-III: Ergon](https://github.com/organvm-iii-ergon) — Commerce and products
- [ORGAN-IV: Taxis](https://github.com/organvm-iv-taxis) — Orchestration and governance
- [Meta-ORGANVM](https://github.com/meta-organvm) — Umbrella organization

---

## Open Issues

This repository has [5 open issues](https://github.com/organvm-i-theoria/a-recursive-root/issues), including structural cleanup ("Diagnose Repo Root Chaos") that reflects the tension between the Z Cartridge scaffold ambitions and the working AI Council core. Contributions that help resolve this structural tension are welcome.

---

## Author

**[@4444J99](https://github.com/4444J99)** / Part of [ORGAN-I: Theoria](https://github.com/organvm-i-theoria)

---

*Last updated: February 2026*
