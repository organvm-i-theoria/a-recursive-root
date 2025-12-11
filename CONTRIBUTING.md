# Contributing to a-recursive-root

Thank you for your interest in contributing to the a-recursive-root project! This document provides guidelines and information to help you contribute effectively.

## Table of Contents

- [Getting Started](#getting-started)
- [Repository Structure](#repository-structure)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)
- [Communication](#communication)

## Getting Started

This repository is built on the **Z Cartridge framework**, which provides:
- Reproducible development environments
- Governance policies and standards
- Documentation architecture
- Container definitions
- Workspace management

### Prerequisites

- Git
- Python 3.10+
- Docker Desktop (with WSL 2 on Windows)
- VS Code (recommended)

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ivi374/a-recursive-root.git
   cd a-recursive-root
   ```

2. **Explore the documentation:**
   - Read the [README.md](README.md) for project overview
   - Check [ARCHITECTURE.md](ARCHITECTURE.md) for structural details
   - Review relevant docs in the `/docs` directory

## Repository Structure

```
a-recursive-root/
├── ai/                    # AI-related configurations and agents
│   ├── agents/           # Agent specifications, playbooks, pipelines
│   └── prompts/          # Prompt templates
├── archive/              # Historical data and archived projects
├── bin/                  # Executable scripts
├── cloud/                # Cloud infrastructure configurations
├── containers/           # Container definitions and Docker files
├── data/                 # Data files and datasets
├── docs/                 # Documentation
│   ├── technical/        # Technical documentation
│   └── user/             # User-facing documentation
├── environment/          # Environment configurations
├── governance/           # Governance policies and procedures
├── integrations/         # Third-party integrations
├── licenses/             # License information
├── observability/        # Monitoring and logging configurations
├── provenance/           # Data provenance tracking
├── research/             # Research notes and papers
├── scripts/              # Utility scripts
├── secrets/              # Secret management (encrypted)
├── swarm/                # Swarm orchestration system
├── templates/            # Project templates
├── tools/                # Development tools
└── workspace/            # Active workspace projects
```

## Development Workflow

### Branching Strategy

We follow a feature branch workflow:

1. **Branch naming conventions:**
   - Feature: `feature/description` or `username/feature-description`
   - Bug fix: `fix/description` or `username/fix-description`
   - Documentation: `docs/description` or `username/docs-description`
   - AI-generated: `copilot/description` or `claude/description`

2. **Create a new branch:**
   ```bash
   git checkout -b your-username/feature-description
   ```

3. **Make your changes:**
   - Write clear, concise commit messages
   - Keep commits focused and atomic
   - Test your changes locally

4. **Push your branch:**
   ```bash
   git push -u origin your-username/feature-description
   ```

### Working with AI Assistants

This repository welcomes contributions from AI coding assistants (GitHub Copilot, Claude, etc.). When working with AI:

1. **Branch naming:** Use prefixes like `copilot/` or `claude/` for AI-generated branches
2. **PR description:** Clearly indicate AI assistance in the PR description
3. **Review carefully:** Always review AI-generated code before committing
4. **Test thoroughly:** Ensure AI-generated code passes all tests

## Pull Request Process

1. **Before submitting:**
   - Ensure your code follows the project's code style
   - Run all tests and ensure they pass
   - Update documentation if needed
   - Add or update tests for new features

2. **PR Description:**
   - Provide a clear title summarizing the change
   - Describe what changed and why
   - Reference any related issues (e.g., "Fixes #123")
   - Include screenshots for UI changes
   - Note any breaking changes

3. **Review Process:**
   - At least one maintainer review is required
   - Address feedback promptly
   - Keep the PR focused (avoid scope creep)
   - Rebase if requested to maintain a clean history

4. **After Approval:**
   - Maintainers will merge your PR
   - Your branch will be deleted automatically

## Code Style

### Python

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints where appropriate
- Write docstrings for classes and functions
- Keep functions small and focused

### Documentation

- Use Markdown for documentation files
- Keep line length to ~80-100 characters for readability
- Use proper heading hierarchy
- Include code examples where helpful

### Commit Messages

Follow the conventional commits format:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example:**
```
feat(swarm): add task decomposition strategy

Implemented hierarchical task decomposition for complex workflows.
This allows better parallelization of agent tasks.

Fixes #42
```

## Communication

### Asking Questions

- **GitHub Issues:** For bug reports and feature requests
- **GitHub Discussions:** For general questions and discussions
- **Pull Request Comments:** For specific code-related questions

### Reporting Issues

When reporting issues, please include:

1. **Description:** Clear description of the problem
2. **Steps to reproduce:** Detailed steps to recreate the issue
3. **Expected behavior:** What you expected to happen
4. **Actual behavior:** What actually happened
5. **Environment:** OS, Python version, relevant tool versions
6. **Screenshots:** If applicable

### Feature Requests

When requesting features:

1. **Use case:** Describe the problem you're trying to solve
2. **Proposed solution:** Your idea for how to solve it
3. **Alternatives:** Other solutions you've considered
4. **Additional context:** Any other relevant information

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## License

By contributing to this project, you agree that your contributions will be licensed under the project's license.

## Questions?

If you have questions about contributing, feel free to:
- Open an issue with the `question` label
- Start a discussion in GitHub Discussions
- Reach out to the maintainers

Thank you for contributing to a-recursive-root! 🚀
