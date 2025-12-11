# Repository Navigation Guide

This guide helps you quickly find what you're looking for in the a-recursive-root repository.

## 📑 Quick Links

### Essential Documentation
- **[README.md](README.md)** - Project overview and quick start
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed architecture documentation
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** - Community guidelines
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes

### Getting Started
1. Read the [README.md](README.md) for project overview
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) to understand structure
3. Check [CONTRIBUTING.md](CONTRIBUTING.md) before making changes
4. Browse [/docs/technical/](docs/technical/) for deep dives

## 📂 Directory Guide

### Development & Workspace

**[/workspace/](workspace/)** - Active development projects
- Main area for current work
- Contains the AI Council System project
- Work-in-progress features

**[/tools/](tools/)** - Development utilities
- Helper scripts and tools
- Code generators
- Analysis utilities

**[/scripts/](scripts/)** - Automation scripts
- Setup and installation scripts
- Build scripts
- Deployment automation
- Maintenance tasks

**[/bin/](bin/)** - Executable commands
- CLI tools
- Command-line utilities
- Can be added to PATH

### AI & Intelligence

**[/ai/](ai/)** - AI-related configurations
- `/ai/agents/` - Agent definitions
  - `/specs/` - Agent specifications
  - `/playbooks/` - Agent workflows  
  - `/pipelines/` - Processing pipelines
- `/ai/prompts/` - Prompt templates

**[/swarm/](swarm/)** - Swarm orchestration
- Assembly definitions
- Orchestrator logic
- Role specifications
- Task management

**[/data/](data/)** - Data management
- Datasets
- Data schemas
- Processing scripts
- Sample data

### Documentation

**[/docs/](docs/)** - Documentation hub
- `/docs/technical/` - Developer documentation
- `/docs/user/` - User guides
- API documentation
- Architecture decision records

**[/research/](research/)** - Research materials
- Papers and articles
- Proof-of-concepts
- Experimental results
- Literature reviews

**[/archive/](archive/)** - Historical data
- `/archive/yearly/` - Organized by year
- `/archive/curated/` - Important items
- Legacy projects
- Migration guides

### Configuration & Governance

**[/environment/](environment/)** - Environment configs
- Development settings
- Staging configurations
- Production configs
- Environment templates

**[/governance/](governance/)** - Policies & procedures
- Development standards
- Review processes
- Compliance requirements
- Decision frameworks

**[/templates/](templates/)** - Reusable templates
- Project templates
- Configuration templates
- Documentation templates
- CI/CD templates

### Infrastructure

**[/containers/](containers/)** - Container definitions
- Dockerfiles
- Docker Compose files
- Container orchestration
- Build contexts

**[/cloud/](cloud/)** - Cloud infrastructure
- Terraform configurations
- CloudFormation templates
- Provider scripts
- Infrastructure diagrams

**[/integrations/](integrations/)** - Third-party integrations
- API clients
- Webhook handlers
- Authentication configs
- Integration tests

**[/observability/](observability/)** - Monitoring & logging
- Log configurations
- Metrics definitions
- Alert rules
- Dashboard configs

### Security & Compliance

**[/secrets/](secrets/)** - Secret management
- Encrypted API keys
- Certificates (encrypted)
- Private keys (encrypted)
- Access tokens (encrypted)
- ⚠️ **Never commit unencrypted secrets!**

**[/licenses/](licenses/)** - License information
- Project licenses
- Third-party licenses
- Attribution files
- Compliance docs

**[/provenance/](provenance/)** - Data provenance
- Data lineage tracking
- Transformation logs
- Source attribution
- Quality metrics

## 🔍 Finding What You Need

### I want to...

#### **Understand the project**
- Start: [README.md](README.md)
- Then: [ARCHITECTURE.md](ARCHITECTURE.md)
- Deep dive: [/docs/technical/](docs/technical/)

#### **Contribute code**
- Read: [CONTRIBUTING.md](CONTRIBUTING.md)
- Check: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Work in: [/workspace/](workspace/)

#### **Set up my environment**
- Check: [/environment/](environment/)
- Use: [/containers/](containers/) for Docker
- Run: [/scripts/](scripts/) for setup

#### **Add a new feature**
- Start: [/workspace/](workspace/)
- Template: [/templates/](templates/)
- Document: [/docs/](docs/)
- Test: Write tests in project directory

#### **Deploy to cloud**
- Config: [/cloud/](cloud/)
- Containers: [/containers/](containers/)
- Secrets: [/secrets/](secrets/) (encrypted)

#### **Work with AI agents**
- Specs: [/ai/agents/specs/](ai/agents/specs/)
- Prompts: [/ai/prompts/](ai/prompts/)
- Orchestration: [/swarm/](swarm/)

#### **Find documentation**
- Technical: [/docs/technical/](docs/technical/)
- User: [/docs/user/](docs/user/)
- Research: [/research/](research/)
- Archive: [/archive/](archive/)

#### **Report a bug or request a feature**
- Open an issue on GitHub
- Include relevant links from this guide
- Follow the issue template

## 🗺️ Common Workflows

### Starting a New Feature

1. Read [CONTRIBUTING.md](CONTRIBUTING.md)
2. Create a branch: `git checkout -b your-name/feature-name`
3. Work in [/workspace/](workspace/)
4. Update [/docs/](docs/) if needed
5. Add tests
6. Submit a PR

### Setting Up Development Environment

1. Clone the repository
2. Check [/environment/](environment/) for configs
3. Run scripts from [/scripts/](scripts/)
4. Use containers from [/containers/](containers/)
5. Configure secrets in [/secrets/](secrets/) (encrypted)

### Adding Documentation

1. Technical docs → [/docs/technical/](docs/technical/)
2. User guides → [/docs/user/](docs/user/)
3. Research → [/research/](research/)
4. Update [README.md](README.md) if needed

### Working with AI Agents

1. Define specs in [/ai/agents/specs/](ai/agents/specs/)
2. Create prompts in [/ai/prompts/](ai/prompts/)
3. Configure orchestration in [/swarm/](swarm/)
4. Test with data from [/data/](data/)

## 📞 Getting Help

### Questions?
- **General:** GitHub Discussions
- **Bugs:** GitHub Issues
- **Features:** GitHub Issues with `enhancement` label
- **Architecture:** Check [ARCHITECTURE.md](ARCHITECTURE.md) first

### Need to...
- **Understand structure:** Read [ARCHITECTURE.md](ARCHITECTURE.md)
- **Contribute:** See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Report issues:** Use GitHub Issues
- **Discuss ideas:** Use GitHub Discussions

## 🎯 Repository Principles

### Organization
- **Modular:** Each directory has a specific purpose
- **Self-documenting:** Structure makes intent clear
- **Consistent:** Patterns are repeated throughout
- **Navigable:** Easy to find what you need

### Documentation
- **Comprehensive:** Everything is documented
- **Up-to-date:** Docs are versioned with code
- **Accessible:** Easy to find and understand
- **Examples:** Includes code samples

### Collaboration
- **Open:** Welcomes contributions
- **Clear:** Guidelines are well-defined
- **Supportive:** Community is helpful
- **Inclusive:** All contributors welcome

---

**Last Updated:** October 25, 2025

For more information, see:
- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture details
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
