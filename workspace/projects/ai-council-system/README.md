# AI Council System

**Version**: 0.1.0-alpha
**Status**: Phase 1 - Foundation Development
**Location**: `/workspace/projects/ai-council-system/`

## Project Overview

A decentralized 24/7 live streaming platform where AI agents form organizational bodies to debate real-time events, with user participation through cryptocurrency mechanisms.

## Project Structure

```
ai-council-system/
├── core/                    # Core system components
│   ├── agents/             # AI agent runtime and implementations
│   ├── council/            # Council formation & debate management
│   ├── events/             # Real-time event ingestion system
│   └── rng/                # Random number generation
├── blockchain/             # Blockchain integration layer
│   ├── contracts/          # Smart contracts (Solidity)
│   ├── rng/                # On-chain RNG (Chainlink VRF, Pyth)
│   └── token/              # Token mechanics and economics
├── streaming/              # Live streaming infrastructure
│   ├── visuals/            # Generative visual engine
│   ├── audio/              # Audio synthesis (TTS)
│   └── broadcast/          # Stream composition & distribution
├── web/                    # Web application
│   ├── frontend/           # React/Next.js application
│   ├── backend/            # API server
│   └── api/                # External API integrations
├── swarm/                  # Swarm orchestration system
│   ├── orchestrator/       # Swarm coordination logic
│   ├── roles/              # Role definitions
│   └── assemblies/         # Assembly templates
└── tests/                  # Test suites
```

## Development Status

### Phase 1: Foundation (Current)
- [x] Project structure setup
- [x] Core architecture documentation
- [x] Swarm orchestration framework
- [x] Role and assembly system
- [ ] AI agent framework
- [ ] Event ingestion prototype

## Quick Start

See individual component READMEs for detailed setup:
- [Swarm System](./swarm/README.md)
- [AI Agents](./core/agents/README.md) _(coming soon)_
- [Event Ingestion](./core/events/README.md) _(coming soon)_

## Architecture

See `/docs/architecture/` for detailed architecture documentation:
- [System Architecture](../../../docs/architecture/system-architecture.md)
- [Component Architecture](../../../docs/architecture/component-architecture.md)

## Contributing

This is a solo development project with swarm-assisted development. See the main repository README for contribution guidelines.

## License

TBD - Pending legal review

---

**Project Root**: `/workspace/projects/ai-council-system/`
**Repository**: a-recursive-root (Z Cartridge)
**Last Updated**: October 23, 2025
