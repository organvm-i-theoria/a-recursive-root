# GitHub Copilot Instructions

## Project Overview

This repository contains the **AI Council System** - a decentralized 24/7 live streaming platform where AI agents form organizational bodies to debate real-time events, with user participation through cryptocurrency mechanisms. The project is built on the **Z Cartridge framework**, which provides reproducible development environments, governance policies, and documentation architecture.

## Repository Structure

The repository follows the Z Cartridge organizational pattern:

- **`ai/`** - AI agent implementations and prompt templates
- **`workspace/`** - Active development workspace with projects, repos, and artifacts
- **`docs/`** - Documentation including architecture, technical specs, and runbooks
- **`governance/`** - Policies, standards, and license management
- **`scripts/`** - Build, deployment, and maintenance scripts
- **`environment/`** - Environment variable catalogs and mappings
- **`containers/`** - Container definitions and configurations
- **`cloud/`** - Cloud infrastructure and deployment configurations
- **`swarm/`** - Swarm orchestration system for multi-agent coordination
- **`templates/`** - Project templates and boilerplates
- **`provenance/`** - SBOM, attestations, and checksums
- **`archive/`** - Historical records and deprecated code

## Coding Standards

### General Principles

1. **Minimal Changes**: Make the smallest possible changes to achieve the goal
2. **Reproducibility**: All changes must maintain reproducibility standards
3. **Documentation**: Update documentation for any architectural changes
4. **Governance**: Follow policies in `governance/policies/`
5. **Provenance**: Maintain SBOM and attestation records for dependencies

### Code Style

- Follow existing code conventions in each language
- Use descriptive variable and function names
- Add comments only when necessary to explain complex logic
- Maintain consistent indentation (see `.editorconfig`)

### File Organization

- Place new scripts in `scripts/` directory
- Store documentation in appropriate `docs/` subdirectories
- Keep environment configurations in `environment/`
- Archive deprecated code in `archive/` instead of deleting

## Development Workflow

### Before Making Changes

1. Review relevant documentation in `docs/`
2. Check existing patterns in the codebase
3. Verify compliance with governance policies
4. Understand the Z Cartridge slot system (see `manifest.yml`)

### Testing

- Test coverage minimum: 80% (per `manifest.yml` guardrails)
- CI workflow includes placeholder for tests (`npm test || true` in `.github/workflows/main.yml`)
  - Note: `|| true` allows CI to pass even when tests fail, indicating testing is not fully implemented
- Test framework is not fully implemented yet - follow existing patterns when adding tests

### Build Process

Use the scripts in `scripts/` directory:
- `bootstrap` - Initialize the environment
- `hydrate` - Load dependencies and configurations
- `build` - Build the project
- `release` - Release the project

Additional scripts available:
- `verify` - Run verification checks (utility script, not part of core manifest workflows)
- `verify-archive` - Verify archive integrity

## Key Technologies

- **AI/LLM**: Claude, GPT-4, Grok APIs
- **Blockchain**: Ethereum + Solana hybrid
- **Frontend**: Next.js, React, TailwindCSS (planned)
- **Backend**: Node.js, Python (FastAPI)
- **Database**: PostgreSQL, Redis
- **Containers**: Docker/Podman

## Important Considerations

### Governance & Compliance

- **License Allowlist**: Only MIT and Apache-2.0 licenses (per `manifest.yml`)
- **Required Files**: Always maintain README.md, manifest.yml, and environment/variables/catalog.yml
- **ADR**: Document architectural decisions in workspace with "Architecture Decision Record" header
- **Prompts**: Maintain prompt templates in `ai/prompts/` with "Prompt Template" designation

### Legal & Ethical

- Be mindful of gambling regulations (UIGEA compliance)
- Consider securities law for token mechanics (Howey Test)
- Implement content moderation for user-generated content
- Ensure GDPR and EU AI Act compliance

### Security

- Never commit secrets or credentials
- Use `secrets/` directory patterns (with .gitignore)
- Validate all external inputs
- Follow secure coding practices for blockchain interactions

## Swarm Orchestration

This project uses a swarm-assisted development model:
- Multiple AI agents may work in coordination
- Follow assembly definitions in `swarm/assemblies/`
- Respect role specifications in `swarm/roles/`
- Coordinate through the swarm orchestrator

## Phase-Based Development

Current Phase: **Phase 1 - Foundation Architecture**

When making changes, consider:
- Current phase priorities and goals
- Planned features for future phases
- Compatibility with existing architecture
- Migration path for phase transitions

## Documentation Requirements

When making significant changes:
1. Update relevant docs in `docs/` directory
2. Add/update ADRs in workspace for architectural decisions
3. Update README.md if changing project structure
4. Maintain provenance records (SBOM, attestations)
5. Document any new environment variables in `environment/variables/`

## Common Patterns

### Adding New Dependencies

1. Verify license compatibility (MIT or Apache-2.0 only)
2. Update provenance/sbom.yaml
3. Add to appropriate package manager file
4. Document in relevant documentation

### Creating New Scripts

1. Place in `scripts/` directory
2. Follow naming conventions of existing scripts
3. Make executable: `chmod +x`
4. Update manifest.yml if adding new workflow commands

### Adding AI Prompts

1. Create in `ai/prompts/` directory
2. Include "Prompt Template" designation
3. Document purpose and usage
4. Follow existing prompt card format

## CI/CD Pipeline

GitHub Actions workflows in `.github/workflows/`:
- **main.yml**: CI pipeline for build, test, SBOM generation
- **governance.yml**: Validates ADR, prompts, and environment mappings

Ensure all changes pass these checks before merging.

## Getting Started for Copilot

When assisting with this repository:
1. Understand the Z Cartridge framework context
2. Maintain the slot-based organization structure
3. Follow governance policies strictly
4. Consider multi-phase development roadmap
5. Respect the swarm-assisted development model
6. Prioritize reproducibility and provenance
7. Document architectural decisions appropriately

## Questions or Clarifications

For questions about:
- **Z Cartridge**: See `docs/` directory for cartridge documentation
- **Architecture**: Check `docs/architecture/` and workspace ADRs
- **Governance**: Review `governance/policies/` and `governance/standards/`
- **Build System**: See `manifest.yml` and `scripts/` directory
- **Project Vision**: Refer to README.md for current phase and goals
