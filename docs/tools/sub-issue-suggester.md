# Sub-Issue Suggester

## Overview

The Sub-Issue Suggester is a tool that analyzes GitHub issues and suggests how to break them down into multiple manageable sub-issues. It uses the swarm orchestrator's task decomposition system to intelligently decompose complex tasks based on their type and context.

## Features

- **Automated Task Breakdown**: Automatically decomposes issues into logical phases and subtasks
- **Multiple Task Types**: Supports different decomposition strategies for:
  - Development tasks
  - Research tasks
  - Analysis tasks
  - Testing tasks
  - Documentation tasks
  - Architecture tasks
- **Dependency Management**: Identifies dependencies between sub-issues
- **Critical Path Analysis**: Highlights tasks on the critical path
- **Effort Estimation**: Provides story point estimates for each sub-issue
- **GitHub-Ready Format**: Outputs markdown formatted for GitHub issues

## Usage

### Basic Usage

```bash
python3 scripts/suggest_sub_issues.py "Issue Title"
```

### With Description

```bash
python3 scripts/suggest_sub_issues.py "Implement user authentication" \
  --description "Add JWT-based authentication with login, logout, and token refresh"
```

### Specify Task Type

```bash
python3 scripts/suggest_sub_issues.py "Research ML architectures" \
  --type research
```

### Save to File

```bash
python3 scripts/suggest_sub_issues.py "Build CI/CD pipeline" \
  --type development \
  --output sub-issues.md
```

## Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `title` | - | Issue title (required) | - |
| `--description` | `-d` | Issue description/body | "" |
| `--type` | `-t` | Task type | "development" |
| `--output` | `-o` | Output file path | stdout |

## Task Types

### Development
Breaks down development work into:
1. Design component architecture
2. Implement core functionality
3. Write and execute tests
4. Integrate with existing system
5. Write documentation

### Research
Breaks down research work into:
1. Literature survey
2. Data collection
3. Data analysis
4. Synthesize findings
5. Write research report

### Analysis
Breaks down analysis work into:
1. Define analysis scope
2. Gather data/information
3. Process and clean data
4. Perform analysis
5. Create visualizations
6. Write analysis report

### Testing
Breaks down testing work into:
1. Create test plan
2. Write unit tests
3. Write integration tests
4. Write end-to-end tests
5. Execute test suite
6. Generate test report

### Documentation
Breaks down documentation work into:
1. Create documentation outline
2. Write first draft
3. Review and refine
4. Add code examples
5. Finalize documentation

### Architecture
Breaks down architecture work into:
1. Gather requirements
2. Design system architecture
3. Document architecture
4. Architecture review
5. Refine based on feedback

## Output Format

The tool generates a markdown document with:

- **Summary**: Parent issue, total effort, number of subtasks
- **Phases**: Organized by execution order
- **Sub-issue Details**: For each subtask:
  - Title and description
  - Estimated effort (story points)
  - Priority level
  - Required capabilities
  - Acceptance criteria
  - Dependencies
  - Suggested labels
- **Execution Summary**: Recommended execution order and critical path

## Examples

### Example 1: Development Task

```bash
python3 scripts/suggest_sub_issues.py \
  "Implement user authentication system" \
  --description "Add JWT-based authentication with login, logout, and token refresh" \
  --type development
```

Output includes 5 phases covering design, implementation, testing, integration, and documentation.

### Example 2: Research Task

```bash
python3 scripts/suggest_sub_issues.py \
  "Research blockchain scalability solutions" \
  --type research
```

Output includes 5 phases covering literature survey, data collection, analysis, synthesis, and reporting.

### Example 3: Documentation Task

```bash
python3 scripts/suggest_sub_issues.py \
  "Create API documentation" \
  --type documentation
```

Output includes 5 phases covering outline, draft, review, examples, and finalization.

## Integration with GitHub

The output is formatted as markdown and can be:

1. **Copy-pasted** directly into a GitHub issue comment
2. **Used as a template** for creating individual sub-issues
3. **Saved to a file** and linked from the main issue

## Technical Details

### Dependencies

The tool relies on the swarm orchestrator's `TaskDecomposer` class:
- Located at: `swarm/orchestrator/task_decomposer.py`
- Provides intelligent task breakdown strategies
- Handles dependency management
- Calculates critical paths

### Task Metadata

Each suggested sub-issue includes:
- **Task ID**: Unique identifier (e.g., `design_0001`)
- **Task Type**: Original task type
- **Priority**: Based on task criticality
- **Capabilities**: Required skills/tools
- **Dependencies**: Blocking relationships
- **Metadata**: Additional context (phase, etc.)

## Best Practices

1. **Review Suggestions**: Always review and customize the suggestions for your specific context
2. **Adjust Estimates**: Modify effort estimates based on your team's experience
3. **Add Context**: Enhance generated descriptions with project-specific details
4. **Track Progress**: Use suggested labels to organize and track sub-issues
5. **Respect Dependencies**: Follow the recommended execution order

## Limitations

- Suggestions are based on generic patterns for each task type
- Does not have project-specific context
- Effort estimates are approximate
- May need customization for complex or unique tasks
- Does not create actual GitHub issues (manual creation required)

## Future Enhancements

Potential improvements:
- Direct GitHub API integration for automatic issue creation
- AI-powered context analysis for better suggestions
- Custom decomposition strategies per project
- Integration with project management tools
- Historical data learning for better estimates

## Support

For issues or questions about the Sub-Issue Suggester:
- Check the [task_decomposer.py](../../swarm/orchestrator/task_decomposer.py) source
- Review the [swarm orchestrator documentation](../../swarm/README.md)
- Open a GitHub issue for bug reports or feature requests
