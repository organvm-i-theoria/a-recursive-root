# Scripts Directory

This directory contains utility scripts for the Z Cartridge project.

## Core Workflow Scripts

These scripts are referenced in `manifest.yml` and are part of the core workflow:

- **bootstrap** - Initialize the development environment
- **hydrate** - Load dependencies and configurations
- **build** - Build the project
- **release** - Release the project

## Utility Scripts

- **backup** - Backup important files and configurations
- **verify** - Run verification checks
- **verify-archive** - Verify archive integrity
- **install_ai_clis.sh** - Install AI command-line interfaces (OpenAI, Anthropic, GitHub Copilot)

## Tools

### Sub-Issue Suggester (`suggest_sub_issues.py`)

Analyzes GitHub issues and suggests how to break them down into multiple manageable sub-issues using the swarm orchestrator's task decomposition system.

**Quick Start:**
```bash
python3 scripts/suggest_sub_issues.py "Issue Title" --type development
```

**Full Documentation:** See [docs/tools/sub-issue-suggester.md](../docs/tools/sub-issue-suggester.md)

**Features:**
- Supports 6 task types: development, research, analysis, testing, documentation, architecture
- Generates GitHub-ready markdown with suggested sub-issues
- Includes dependency tracking and critical path analysis
- Provides effort estimates in story points

**Example:**
```bash
# Suggest sub-issues for a development task
python3 scripts/suggest_sub_issues.py \
  "Implement user authentication" \
  --description "Add JWT-based auth" \
  --type development \
  --output sub-issues.md
```

## Usage Notes

- All scripts should be run from the repository root directory
- Python scripts require Python 3.7+
- Shell scripts should be executable (use `chmod +x` if needed)
- See individual script documentation for specific requirements

## Adding New Scripts

When adding new scripts:

1. Place the script in this directory
2. Make it executable if it's a shell script: `chmod +x script_name`
3. Update this README with a brief description
4. If it's a core workflow script, update `manifest.yml`
5. Add detailed documentation in `docs/` if needed
