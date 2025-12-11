# Documentation Directory

This directory contains all project documentation, organized by audience and purpose.

## Structure

```
docs/
├── technical/          # Developer-focused documentation
│   ├── software-stack-deep-dive_20251023.md
│   └── ...
└── user/              # User-facing documentation
    ├── ai-handoff-user-summary_20251023.md
    └── ...
```

## Documentation Types

### Technical Documentation (`/docs/technical/`)

Developer-focused documentation including:
- **Architecture guides:** System design and structure
- **API documentation:** Endpoint specifications
- **Setup guides:** Development environment setup
- **Integration guides:** Third-party service integration
- **Deployment guides:** Production deployment procedures
- **Troubleshooting:** Common issues and solutions

**Audience:** Developers, DevOps engineers, technical contributors

### User Documentation (`/docs/user/`)

User-facing documentation including:
- **User guides:** How to use the platform
- **Getting started:** Onboarding documentation
- **FAQ:** Frequently asked questions
- **Tutorials:** Step-by-step walkthroughs
- **Reference:** Quick reference materials
- **AI handoff summaries:** Context for AI assistants

**Audience:** End users, AI assistants, non-technical stakeholders

## Writing Documentation

### Style Guide

- **Clear and concise:** Get to the point quickly
- **Use examples:** Show, don't just tell
- **Structure well:** Use headings, lists, and formatting
- **Link appropriately:** Reference related docs
- **Keep updated:** Update docs when code changes

### Markdown Standards

- Use ATX-style headers (`#`, `##`, `###`)
- Include table of contents for long documents
- Use code blocks with language specification
- Add alt text to images
- Keep line length reasonable (~80-100 characters)

### File Naming

- Use descriptive names: `setup-guide.md` not `doc1.md`
- Use hyphens for spaces: `api-reference.md`
- Add dates for versioned docs: `architecture-2025-10-23.md`
- Use lowercase letters

## Contributing Documentation

### Adding New Documentation

1. **Determine audience:** Technical or user-facing?
2. **Choose location:** Place in appropriate subdirectory
3. **Use templates:** Check `/templates` for doc templates
4. **Follow standards:** Adhere to style guide above
5. **Link from index:** Update this README if needed

### Updating Existing Documentation

1. **Check for accuracy:** Ensure content is still valid
2. **Preserve history:** For significant changes, consider versioning
3. **Update links:** Fix any broken references
4. **Test examples:** Verify code examples still work
5. **Note changes:** Update changelog if applicable

## Documentation Tools

### Recommended Tools

- **Markdown editor:** VS Code with Markdown extensions
- **Linters:** markdownlint for style checking
- **Generators:** Sphinx, MkDocs for static sites
- **Diagrams:** Mermaid, draw.io for architecture diagrams

### Local Preview

To preview documentation locally:
```bash
# Using Python http.server
cd docs
python -m http.server 8000

# Or use a Markdown previewer in your editor
```

## Key Documents

### Repository Documentation

- **[README.md](../README.md)** - Project overview
- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - Architecture documentation
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Contribution guidelines
- **[NAVIGATION.md](../NAVIGATION.md)** - Repository navigation
- **[CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)** - Community guidelines

### Technical Documentation

Located in `/docs/technical/`:
- Software stack documentation
- Setup and configuration guides
- Deployment procedures
- API specifications

### User Documentation

Located in `/docs/user/`:
- User guides and tutorials
- Getting started materials
- AI assistant context
- FAQ and troubleshooting

## Documentation Standards

### Must Have

- [ ] Clear title and purpose
- [ ] Table of contents (for docs > 3 sections)
- [ ] Code examples (where applicable)
- [ ] Last updated date
- [ ] Related links

### Should Have

- [ ] Prerequisites listed
- [ ] Step-by-step instructions
- [ ] Screenshots or diagrams
- [ ] Common issues section
- [ ] Links to related docs

### Nice to Have

- [ ] Video tutorials
- [ ] Interactive examples
- [ ] PDF version
- [ ] Multiple language support
- [ ] Searchable index

## Maintenance

### Review Schedule

- **Weekly:** Check for broken links
- **Monthly:** Review and update getting started docs
- **Quarterly:** Full documentation audit
- **Per release:** Update version-specific docs

### Deprecation Process

When deprecating documentation:
1. Mark as deprecated in title
2. Add deprecation notice at top
3. Link to replacement doc
4. Move to `/archive` after grace period
5. Update all incoming links

## Questions?

- **About writing docs:** See [CONTRIBUTING.md](../CONTRIBUTING.md)
- **About structure:** See [ARCHITECTURE.md](../ARCHITECTURE.md)
- **About navigation:** See [NAVIGATION.md](../NAVIGATION.md)
- **General questions:** Open a GitHub Discussion

---

**For more information:** See [Repository Navigation Guide](../NAVIGATION.md)
