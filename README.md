# a-recursive-root: Z Cartridge Development Framework

## 🎯 Repository Purpose

**a-recursive-root** is a Z Cartridge framework repository providing reproducible development environments, governance standards, and organizational infrastructure for software projects. It serves as a foundation for creating well-structured, maintainable codebases with built-in best practices.

## 📋 What is a Z Cartridge?

A Z Cartridge is a standardized project structure that provides:
- **Reproducible Environments**: Consistent development setups across teams
- **Governance Frameworks**: Security policies, code ownership, compliance
- **Documentation Architecture**: Structured knowledge management
- **Container Definitions**: Portable deployment configurations
- **Workspace Management**: Organized project hierarchies

## 🏗️ Z Cartridge Structure

```
a-recursive-root/
├── ai/                      # AI agent configurations and roles
├── archive/                 # Historical archives and documentation
│   ├── curated/            # Curated papers and prototypes
│   ├── snapshots/          # Point-in-time backups
│   └── yearly/             # Annual archives
├── bin/                     # Executable scripts
├── cloud/                   # Cloud infrastructure configurations
├── containers/              # Container definitions (Docker, etc.)
│   ├── base/               # Base container images
│   ├── languages/          # Language-specific containers
│   └── services/           # Service containers
├── data/                    # Data catalog and policies
├── docs/                    # Documentation
│   ├── architecture/       # System architecture docs
│   └── academic/           # Academic resources
├── environment/             # Environment configurations
├── governance/              # Governance frameworks and policies
├── integrations/            # Third-party integrations
├── observability/           # Monitoring and observability
├── provenance/              # SBOM, attestations, checksums
├── scripts/                 # Build and deployment scripts
├── templates/               # Project templates
├── tools/                   # Development tools
└── workspace/               # Active development workspace
    └── projects/           # Individual projects
```

## 🔧 Manifest-Driven Configuration

The Z Cartridge uses `manifest.yml` to define:
- **Slots**: Key directory locations ($Z_ROOT, $Z_SCRIPTS, $Z_ARCHIVE, etc.)
- **Workflows**: Bootstrap, hydrate, build, and release processes
- **Guardrails**: Required files, license allowlists, test coverage requirements
- **Provenance**: SBOM, attestations, and checksums for security
- **Ontology**: Schema and glossary for knowledge management

## 🎯 Use Cases

### 1. Project Foundation
Start new projects with production-ready structure, governance, and tooling built-in.

### 2. Organizational Standards
Enforce consistent practices across multiple projects and teams.

### 3. Historical Archive
Maintain comprehensive project history, documentation, and decision records.

### 4. Research & Development
Curate papers, prototypes, and experimental code in organized archives.

## 🤝 Contributing

This repository follows Z Cartridge governance standards. See `governance/` for contribution guidelines and policies.

## 📄 License

See individual project licenses in `licenses/` directory.

---

## 📜 Historical Archive: AI Council Development

**Note**: This repository previously served as the development foundation for the AI Council System project. That project has now been **successfully migrated** to its own repository: **[ai-council--coliseum](https://github.com/ivviiviivvi/ai-council--coliseum)**.

### Historical Branch

The complete AI Council codebase (28,500+ lines across Phases 1-4) is preserved in branch:  
**`claude/phase4-advanced-features-011CUSN6Nu1tuVpbLu9gZBhc`**

This branch contains:
- ✅ Complete Phases 1-3 (foundation, production features, blockchain)
- ✅ Phase 4.3 (real-time viewer voting with gamification)
- Production-ready code and comprehensive documentation

### Repository Split

As of December 2025, the projects are separated:

| Repository | Purpose | Status |
|------------|---------|--------|
| **a-recursive-root** | Z Cartridge framework & historical archive | Active (this repo) |
| **ai-council--coliseum** | AI Council production platform | Active development |

### For Complete AI Council History

See archived documentation:
- **REPOSITORY_HISTORY.md**: Complete project evolution
- **archive/curated/MAIN_BRANCH_ORIGIN.md**: Main branch genesis
- **PHASE_3_COMPLETE.md** & **PHASE_4_SESSION_SUMMARY.md**: Phase completion records

**Active development of AI Council continues at**: https://github.com/ivviiviivvi/ai-council--coliseum

---

**Repository Role**: Z Cartridge Framework & Historical Archive  
**Last Updated**: December 15, 2025  
**Version**: 0.1.0-alpha
