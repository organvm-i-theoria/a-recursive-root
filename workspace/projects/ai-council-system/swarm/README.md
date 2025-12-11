# Swarm Orchestration System

**Version**: 0.1.0
**Status**: Phase 1 - Foundation

## Overview

The Swarm Orchestration System coordinates multiple AI agents working together to accomplish complex tasks through role-based collaboration and assembly execution. This system is a core component of the AI Council platform, enabling both development workflows and council debate orchestration.

## Architecture

```
swarm/
├── orchestrator/           # Core orchestration logic
│   ├── coordinator.py     # Main swarm coordinator
│   ├── task_decomposer.py # Task breakdown and planning
│   └── result_aggregator.py # Result synthesis
├── roles/                  # Role definitions and management
│   ├── role_definitions.yaml # Available roles
│   ├── role_loader.py     # Role loading utilities
│   └── capabilities.py    # Capability matching
├── assemblies/            # Assembly definitions
│   ├── templates/         # Assembly templates
│   │   ├── feature_development.yaml
│   │   ├── research_analysis.yaml
│   │   └── council_debate.yaml
│   ├── assembly_loader.py # Assembly loading
│   └── assembly_executor.py # Assembly execution
└── monitoring/            # Health and progress tracking
```

## Core Concepts

### Agents

AI agents are autonomous entities that can perform tasks based on their capabilities. Each agent has:
- **Agent ID**: Unique identifier
- **Capabilities**: List of skills (e.g., "coding", "research", "moderation")
- **Status**: Current state (available, assigned, busy)
- **Role**: Currently assigned role (if any)

### Roles

Roles define specific responsibilities and required capabilities within an assembly:
- **Name**: Role identifier
- **Capabilities**: Required skills
- **Responsibilities**: What the role should accomplish
- **Dependencies**: Other roles this role depends on
- **Output Artifacts**: Expected deliverables

### Assemblies

Assemblies are predefined workflows that orchestrate multiple roles to accomplish complex tasks:
- **Roles**: Required roles for the assembly
- **Workflow**: Sequence of steps and actions
- **Success Criteria**: Conditions for successful completion
- **Metadata**: Tags, priority, duration estimates

### Workflows

Workflows define the execution flow within an assembly:
- **Steps**: Ordered or parallel actions
- **Dependencies**: Step prerequisites
- **Error Handling**: How to handle failures
- **Timeouts**: Maximum execution time

## Usage

### Basic Example

```python
from swarm.orchestrator import SwarmCoordinator, ExecutionContext, Agent
from swarm.assemblies import get_assembly

# Initialize coordinator
coordinator = SwarmCoordinator()

# Register agents
coordinator.register_agent(Agent(
    agent_id="agent_001",
    name="Developer Bot",
    capabilities=["coding", "testing", "debugging"]
))

# Load assembly
assembly = get_assembly("feature_development")

# Create execution context
context = ExecutionContext(
    task_id="task_001",
    input_data={
        "feature_requirements": "Add user authentication",
        "existing_architecture": "..."
    },
    constraints={}
)

# Execute assembly
result = await coordinator.execute_assembly(assembly, context)

print(f"Status: {result.status}")
print(f"Outputs: {result.outputs}")
```

### Creating Custom Roles

Roles are defined in `roles/role_definitions.yaml`:

```yaml
custom_role:
  name: "Custom Role"
  description: "Description of the role"
  capabilities:
    - capability1
    - capability2
  responsibilities:
    - "Responsibility 1"
    - "Responsibility 2"
  dependencies:
    - other_role
  skills_required:
    - "Skill 1"
    - "Skill 2"
  output_artifacts:
    - "Artifact 1"
```

### Creating Custom Assemblies

Assemblies are defined in `assemblies/templates/`:

```yaml
name: "custom_assembly"
version: "1.0.0"
description: "Description of assembly"

roles:
  - name: "role_1"
    capabilities: [...]
    responsibilities: [...]

workflow:
  parallel_execution: false
  error_handling: "stop"
  steps:
    - role: "role_1"
      action: "do_something"
      inputs: [...]
      outputs: [...]
      timeout: "1h"

success_criteria:
  required_outputs: [...]
  quality_threshold: 0.85
  timeout: "24h"
```

## Available Roles

### Development
- **architect**: System architecture and design
- **developer**: General software development
- **frontend_developer**: UI/UX development
- **backend_developer**: Server-side development
- **blockchain_developer**: Smart contracts and web3

### Quality Assurance
- **qa_engineer**: Testing and quality assurance
- **security_auditor**: Security audits and vulnerability assessment

### Research & Analysis
- **researcher**: Research and investigation
- **data_analyst**: Data analysis and insights

### Documentation
- **technical_writer**: Technical documentation
- **content_creator**: Marketing and educational content

### Project Management
- **project_manager**: Project coordination
- **product_owner**: Product requirements and prioritization

### AI Council Specific
- **council_moderator**: Debate moderation
- **debate_agent**: Council participation
- **event_curator**: Event selection and curation
- **stream_composer**: Live stream management
- **token_economist**: Token economics design

## Available Assemblies

### Feature Development
End-to-end feature development workflow with architecture, implementation, testing, and documentation.

**Roles**: Architect, Developer, QA Engineer, Technical Writer
**Duration**: 16-24 hours
**Use Case**: Implementing new features

### Research Analysis
Comprehensive research workflow with literature review, data analysis, and report generation.

**Roles**: Researcher, Data Analyst, Technical Writer
**Duration**: 24-32 hours
**Use Case**: Conducting research and generating insights

### Council Debate
Orchestrates AI council debate sessions with topic selection, moderation, and streaming.

**Roles**: Event Curator, Council Moderator, Debate Agents (×5), Stream Composer
**Duration**: 30-60 minutes
**Use Case**: Live debate sessions

## Task Decomposition

The `TaskDecomposer` breaks down complex tasks into manageable subtasks:

```python
from swarm.orchestrator import TaskDecomposer, TaskType

decomposer = TaskDecomposer()

result = await decomposer.decompose_task(
    task_description="Implement user authentication system",
    task_type=TaskType.DEVELOPMENT,
    context={}
)

print(f"Subtasks: {len(result.subtasks)}")
print(f"Execution order: {result.execution_order}")
print(f"Critical path: {result.critical_path}")
```

## Result Aggregation

The `ResultAggregator` combines outputs from multiple agents:

```python
from swarm.orchestrator import ResultAggregator, AggregationStrategy

aggregator = ResultAggregator()

result = await aggregator.aggregate(
    agent_outputs=[...],
    strategy=AggregationStrategy.CONSENSUS
)

print(f"Confidence: {result.confidence}")
print(f"Conflicts: {len(result.conflicts)}")
```

### Aggregation Strategies

- **MERGE**: Combine all outputs
- **VOTE**: Majority voting
- **CONSENSUS**: Require agreement
- **WEIGHTED**: Weight by confidence
- **BEST**: Select highest confidence
- **SEQUENTIAL**: Pipeline processing

## Capability Matching

The `CapabilityMatcher` matches agents to roles:

```python
from swarm.roles import get_capability_matcher

matcher = get_capability_matcher()

score = matcher.calculate_match_score(
    agent_capabilities=["coding", "testing"],
    required_capabilities=["coding", "debugging"]
)

gap = matcher.get_capability_gap(
    agent_capabilities=[...],
    required_capabilities=[...]
)
```

## Monitoring

Track assembly execution and agent health:

```python
# Get active assemblies
active = coordinator.get_active_assemblies()

# Get execution history
history = coordinator.get_execution_history()

# Check agent status
for agent in coordinator.available_agents:
    print(f"{agent.name}: {agent.status}")
```

## Error Handling

Assemblies support different error handling strategies:

- **stop**: Stop execution on first error
- **continue**: Log error and continue with next step
- **retry**: Retry failed step up to N times

```yaml
workflow:
  error_handling: "retry"
  retry_attempts: 3
  retry_delay: "5s"
```

## Best Practices

1. **Role Granularity**: Define roles with clear, focused responsibilities
2. **Assembly Composition**: Prefer composition over monolithic assemblies
3. **Error Handling**: Always define appropriate error handling strategies
4. **Timeouts**: Set realistic timeouts for all steps
5. **Dependencies**: Minimize role dependencies for parallelization
6. **Validation**: Always validate outputs against success criteria
7. **Monitoring**: Track execution metrics and agent health

## Extending the System

### Adding New Capabilities

1. Add capability definition to `roles/capabilities.py`:
```python
"new_capability": {
    "description": "Description",
    "related_skills": ["skill1", "skill2"],
}
```

2. Update role definitions to use new capability
3. Update agents to include new capability if applicable

### Adding New Roles

1. Define role in `roles/role_definitions.yaml`
2. Add role to appropriate category
3. Update assemblies that should use the new role

### Adding New Assemblies

1. Create YAML template in `assemblies/templates/`
2. Define roles, workflow, and success criteria
3. Test assembly with coordinator
4. Document assembly usage

## Testing

```python
# Test role matching
from swarm.roles import get_role_loader

loader = get_role_loader()
role = loader.get_role("developer")
assert role is not None

# Test assembly loading
from swarm.assemblies import get_assembly_loader

loader = get_assembly_loader()
assembly = loader.get_assembly("feature_development")
assert assembly is not None

# Test coordinator
coordinator = SwarmCoordinator()
assert len(coordinator.available_agents) == 0
```

## Future Enhancements

### Phase 2
- Dynamic role creation
- Agent learning and adaptation
- Real-time assembly modification

### Phase 3
- Multi-swarm coordination
- Cross-assembly communication
- Advanced conflict resolution

### Phase 4
- Self-organizing swarms
- Emergent behavior support
- Decentralized orchestration

## References

- [System Architecture](../docs/architecture/system-architecture.md)
- [Component Architecture](../docs/architecture/component-architecture.md)
- [Role Definitions](./roles/role_definitions.yaml)
- [Assembly Templates](./assemblies/templates/)

---

**Last Updated**: October 23, 2025
**Maintainer**: Development Team
