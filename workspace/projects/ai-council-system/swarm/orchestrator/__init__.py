"""
Swarm Orchestrator Module

Provides core orchestration capabilities for AI agent swarms,
including coordination, task decomposition, and result aggregation.
"""

from .coordinator import (
    SwarmCoordinator,
    Assembly,
    AssemblyResult,
    ExecutionContext,
    ExecutionStatus,
    Role,
    Agent,
    Workflow,
    SuccessCriteria,
    Contribution,
    RoleRequirements,
)

from .task_decomposer import (
    TaskDecomposer,
    Task,
    TaskType,
    TaskPriority,
    TaskDependency,
    DecompositionResult,
)

from .result_aggregator import (
    ResultAggregator,
    AggregationStrategy,
    AgentOutput,
    AggregatedResult,
    ValidationResult,
)

__all__ = [
    # Coordinator
    "SwarmCoordinator",
    "Assembly",
    "AssemblyResult",
    "ExecutionContext",
    "ExecutionStatus",
    "Role",
    "Agent",
    "Workflow",
    "SuccessCriteria",
    "Contribution",
    "RoleRequirements",
    # Task Decomposer
    "TaskDecomposer",
    "Task",
    "TaskType",
    "TaskPriority",
    "TaskDependency",
    "DecompositionResult",
    # Result Aggregator
    "ResultAggregator",
    "AggregationStrategy",
    "AgentOutput",
    "AggregatedResult",
    "ValidationResult",
]

__version__ = "0.1.0"
