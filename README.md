# Z Cartridge

This cartridge defines a complete and reproducible environment for your projects.  It
includes a manifest that maps local directories to their upstream counterparts,
governance policies, environment definitions, cloud docking metadata and
documentation.  The contents of this tree are intentionally self‑describing so
that it can be plugged into any host and rehydrated into a development
environment without guesswork.

## AI Command-Line Interfaces

This repository includes scripts and documentation to help you install and configure common AI command-line interfaces.

### Supported AI CLIs

- **OpenAI CLI** - Python client for OpenAI's APIs (GPT-4, GPT-3.5, DALL-E, etc.)
- **Anthropic Claude** - Python client for Claude AI models
- **GitHub Copilot CLI** - Command-line interface for GitHub Copilot

### Installation

Run the installation script to set up all AI CLIs:

```bash
./scripts/install_ai_clis.sh
```

This script will:
1. Install Python dependencies from `requirements.txt` (OpenAI and Anthropic clients)
2. Install GitHub Copilot CLI via npm (if Node.js is available)
3. Check for GitHub CLI and provide setup instructions

### Prerequisites

- **Python 3.7+** with pip (for OpenAI and Anthropic clients)
- **Node.js and npm** (for GitHub Copilot CLI)
- **GitHub CLI** (optional, for enhanced Copilot integration)

### Configuration

After installation, configure your API keys:

```bash
# OpenAI API key
export OPENAI_API_KEY='your-openai-api-key'

# Anthropic API key
export ANTHROPIC_API_KEY='your-anthropic-api-key'
```

For GitHub Copilot, authenticate with:

```bash
gh auth login
```

### Usage Examples

**OpenAI (Python):**
```python
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

**Anthropic Claude (Python):**
```python
from anthropic import Anthropic
client = Anthropic()
message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)
```

**GitHub Copilot CLI:**
```bash
# Get shell command suggestions
github-copilot-cli what-the-shell "list all files modified in the last week"

# Get git command suggestions
github-copilot-cli git-assist "undo last commit but keep changes"
```

### Manual Installation

If you prefer to install components individually:

**Python packages:**
```bash
pip install -r requirements.txt
```

**GitHub Copilot CLI:**
```bash
npm install -g @githubnext/github-copilot-cli
```
# AI Council System - Development Repository

[![License](https://img.shields.io/badge/license-TBD-blue.svg)](LICENSE)
[![Phase](https://img.shields.io/badge/phase-Foundation-yellow.svg)](#development-phases)
[![Status](https://img.shields.io/badge/status-Prototype-orange.svg)](#project-status)

## 🎯 Project Vision

A decentralized 24/7 live streaming platform where AI agents form organizational bodies to debate real-time events, with user participation through cryptocurrency mechanisms.

## 📑 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed architecture and design overview
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Guidelines for contributors
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** - Community guidelines
- **[/docs](docs/)** - Technical and user documentation

## 🚀 Quick Start

1. **Read the documentation:**
   - Start with [ARCHITECTURE.md](ARCHITECTURE.md) to understand the structure
   - Review [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines

2. **Explore the repository:**
   ```bash
   git clone https://github.com/ivi374/a-recursive-root.git
   cd a-recursive-root
   ```

3. **Navigate the structure:**
   - `/workspace` - Active development projects
   - `/docs` - Documentation
   - `/ai` - AI agents and prompts
   - `/swarm` - Orchestration system

## 📋 Current Phase: Phase 1 - Foundation Architecture

### Project Status

- **Phase**: Foundation & Planning
- **Developer**: Solo (Swarm-Assisted)
- **Start Date**: October 14, 2025
- **Repository**: Development Prototype
- **Framework**: Z Cartridge

## 🏗️ Architecture Overview

```
ai-council-system/
├── core/                    # Core system components
│   ├── agents/             # AI agent implementations
│   ├── council/            # Council formation & management
│   ├── events/             # Real-time event ingestion
│   └── rng/                # Random number generation
├── blockchain/             # Blockchain integration
│   ├── contracts/          # Smart contracts
│   ├── rng/                # On-chain RNG (Chainlink VRF, Pyth)
│   └── token/              # Token mechanics
├── streaming/              # Live streaming components
│   ├── visuals/            # Generative visuals
│   ├── audio/              # Audio synthesis
│   └── broadcast/          # Stream management
├── web/                    # Website & frontend
│   ├── frontend/           # React/Next.js app
│   ├── backend/            # API server
│   └── api/                # External API integrations
├── swarm/                  # Swarm orchestration system
│   ├── assemblies/         # Assembly definitions
│   ├── orchestrator/       # Swarm coordinator
│   └── roles/              # Role specifications
├── governance/             # Governance frameworks
├── tests/                  # Testing suite
└── docs/                   # Documentation
```

## 🚀 Development Phases

### Phase 1: Foundation (Current)

- [x] Project setup
- [x] README update
- [ ] Core architecture definition
- [ ] Swarm orchestrator implementation
- [ ] Basic AI agent framework
- [ ] Event ingestion prototype

### Phase 2: Prototyping

- [ ] Website launch
- [ ] Twitter presence
- [ ] Token creation (pump.fun)
- [ ] Basic live stream setup

### Phase 3: Core Implementation

- [ ] AI council debates
- [ ] Blockchain RNG integration
- [ ] User interaction mechanics
- [ ] Cryptocurrency rewards

### Phase 4: Advanced Features

- [ ] Generative visuals
- [ ] Advanced betting mechanics
- [ ] Governance implementation
- [ ] Multi-chain support

### Phase 5: Launch & Scale

- [ ] Public beta
- [ ] Community building
- [ ] 24/7 operations
- [ ] Platform expansion

## ⚠️ Legal & Ethical Considerations

### Immediate Concerns

1. **Gambling Regulations**: Betting mechanics require compliance with UIGEA, state laws
2. **Securities Law**: Token may be classified as security (Howey Test)
3. **Content Liability**: NSFW content creates platform risks
4. **International Compliance**: EU AI Act, GDPR, etc.

### Mitigation Strategy

- Start with entertainment-focused MVP (no gambling)
- Implement robust content moderation
- Consult legal counsel before token launch
- Build compliance frameworks from day one

## 🛠️ Technology Stack

### Core Technologies

- **AI/LLM**: Claude, GPT-4, Grok (via APIs)
- **Blockchain**: Ethereum + Solana hybrid
- **RNG**: Chainlink VRF, Pyth Entropy, Quantum (future)
- **Streaming**: OBS, RTMP, Twitch/YouTube APIs
- **Frontend**: Next.js, React, TailwindCSS
- **Backend**: Node.js, Python (FastAPI)
- **Database**: PostgreSQL, Redis (caching)

### Development Tools

- **Version Control**: Git/GitHub
- **CI/CD**: GitHub Actions
- **Testing**: Jest, Pytest, Hardhat
- **Monitoring**: Prometheus, Grafana

## 📊 Key Metrics & Data Points

### Market Context (October 2025)

- Bitcoin: $102,000 (from $123,000 peak)
- Liquidations: $19 billion
- Memecoin failure rate: 97-99%
- Pump.fun successes: 293 tokens >$1M profit

### Target Metrics

- Stream uptime: 99.9% (24/7)
- Concurrent viewers: 1,000+ (Phase 5)
- Token holders: 10,000+ (Phase 5)
- Daily transactions: 5,000+ (Phase 5)

## 🤝 Contributing

We welcome contributions from both human developers and AI coding assistants!

### How to Contribute

1. **Read the guidelines:** Check out [CONTRIBUTING.md](CONTRIBUTING.md) for detailed information
2. **Follow the Code of Conduct:** Review [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
3. **Understand the architecture:** Read [ARCHITECTURE.md](ARCHITECTURE.md)
4. **Submit your changes:** Create a pull request with clear description

### AI-Assisted Development

This repository actively uses AI coding assistants (GitHub Copilot, Claude, etc.):
- Use branch prefixes like `copilot/` or `claude/` for AI-generated work
- Clearly indicate AI assistance in PR descriptions
- Review AI-generated code thoroughly before committing

For more details, see the [Contributing Guide](CONTRIBUTING.md).

## 📄 License

TBD - Pending legal review

## 🔗 Links

- Website: TBD
- Twitter: TBD
- Discord: TBD
- Token: TBD

---

**Last Updated**: October 23, 2025
**Version**: 0.1.0-alpha

## 📚 Z Cartridge Foundation

This repository is built on the **Z Cartridge framework**, providing:
- **Reproducible Development Environments:** Consistent setup across machines
- **Governance Policies and Standards:** Clear guidelines and procedures
- **Documentation Architecture:** Structured documentation approach
- **Container Definitions:** Docker and containerization support
- **Workspace Management:** Organized project structure

### Repository Structure

```
a-recursive-root/
├── ai/                    # AI agents, prompts, and configurations
├── workspace/             # Active development projects
├── swarm/                 # Orchestration and coordination
├── docs/                  # Technical and user documentation
├── environment/           # Environment configurations
├── governance/            # Policies and procedures
├── containers/            # Docker and container configs
├── cloud/                 # Cloud infrastructure
├── integrations/          # Third-party integrations
├── tools/                 # Development utilities
├── scripts/               # Automation scripts
├── bin/                   # Executable commands
├── templates/             # Reusable templates
├── data/                  # Datasets and data sources
├── research/              # Research materials
├── archive/               # Historical data
├── secrets/               # Secret management (encrypted)
├── licenses/              # License information
├── provenance/            # Data provenance tracking
└── observability/         # Monitoring and logging
```

For detailed architecture information, see [ARCHITECTURE.md](ARCHITECTURE.md).
