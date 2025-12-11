"""
Task Decomposer - Breaks down complex tasks into manageable subtasks

Analyzes complex tasks and decomposes them into smaller, manageable units
that can be assigned to individual agents or agent groups.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """
    Enumeration of the types of tasks that can be decomposed.
    """
    DEVELOPMENT = "development"
    RESEARCH = "research"
    ANALYSIS = "analysis"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    ARCHITECTURE = "architecture"


class TaskPriority(Enum):
    """
    Enumeration of the priority levels for tasks.
    """
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class TaskDependency:
    """
    Represents a dependency between two tasks.

    Attributes:
        task_id: The ID of the task that this task depends on.
        dependency_type: The type of dependency (e.g., "blocks", "requires", "suggests").
    """
    task_id: str
    dependency_type: str  # "blocks", "requires", "suggests"


@dataclass
class Task:
    """
    Represents a single, decomposed task.

    Attributes:
        task_id: A unique identifier for the task.
        title: The title of the task.
        description: A description of the task.
        task_type: The type of the task.
        priority: The priority of the task.
        estimated_effort: The estimated effort required to complete the task.
        required_capabilities: A list of capabilities required to perform the task.
        dependencies: A list of dependencies for this task.
        acceptance_criteria: A list of criteria that must be met for the task to be considered complete.
        metadata: A dictionary for storing arbitrary metadata.
    """
    task_id: str
    title: str
    description: str
    task_type: TaskType
    priority: TaskPriority
    estimated_effort: int  # in story points or hours
    required_capabilities: List[str]
    dependencies: List[TaskDependency]
    acceptance_criteria: List[str]
    metadata: Dict[str, Any]

    def is_ready(self, completed_tasks: set) -> bool:
        """
        Checks if the task is ready to be executed based on its dependencies.

        Args:
            completed_tasks: A set of IDs of tasks that have already been completed.

        Returns:
            True if the task is ready to be executed, False otherwise.
        """
        for dep in self.dependencies:
            if dep.dependency_type == "blocks" and dep.task_id not in completed_tasks:
                return False
        return True


@dataclass
class DecompositionResult:
    """
    Contains the results of a task decomposition.

    Attributes:
        original_task: The original task description.
        subtasks: A list of the decomposed subtasks.
        execution_order: A list of lists, representing batches of tasks that can be executed in parallel.
        estimated_total_effort: The total estimated effort for all subtasks.
        critical_path: A list of task IDs representing the critical path of the decomposition.
    """
    original_task: str
    subtasks: List[Task]
    execution_order: List[List[str]]  # List of task batches
    estimated_total_effort: int
    critical_path: List[str]


class TaskDecomposer:
    """
    Decomposes complex tasks into smaller, manageable subtasks.

    This class uses a strategy pattern to decompose tasks based on their type.
    """

    def __init__(self):
        """
        Initializes the TaskDecomposer.
        """
        self.task_counter = 0
        self.decomposition_strategies = {
            TaskType.DEVELOPMENT: self._decompose_development_task,
            TaskType.RESEARCH: self._decompose_research_task,
            TaskType.ANALYSIS: self._decompose_analysis_task,
            TaskType.TESTING: self._decompose_testing_task,
            TaskType.DOCUMENTATION: self._decompose_documentation_task,
            TaskType.ARCHITECTURE: self._decompose_architecture_task,
        }

    async def decompose_task(
        self,
        task_description: str,
        task_type: TaskType,
        context: Optional[Dict[str, Any]] = None
    ) -> DecompositionResult:
        """
        Decomposes a complex task into a set of smaller subtasks.

        Args:
            task_description: A high-level description of the task to be decomposed.
            task_type: The type of the task.
            context: An optional dictionary of additional context for the decomposition.

        Returns:
            A DecompositionResult object containing the subtasks and execution plan.
        """
        logger.info(f"Decomposing {task_type.value} task: {task_description}")

        context = context or {}

        # Select appropriate decomposition strategy
        strategy = self.decomposition_strategies.get(task_type)
        if not strategy:
            logger.warning(f"No strategy for task type: {task_type}")
            return self._default_decomposition(task_description, task_type)

        # Execute strategy
        subtasks = await strategy(task_description, context)

        # Build execution order based on dependencies
        execution_order = self._build_execution_order(subtasks)

        # Calculate critical path
        critical_path = self._calculate_critical_path(subtasks, execution_order)

        # Calculate total effort
        total_effort = sum(task.estimated_effort for task in subtasks)

        result = DecompositionResult(
            original_task=task_description,
            subtasks=subtasks,
            execution_order=execution_order,
            estimated_total_effort=total_effort,
            critical_path=critical_path
        )

        logger.info(
            f"Decomposed into {len(subtasks)} subtasks, "
            f"total effort: {total_effort}"
        )

        return result

    async def _decompose_development_task(
        self,
        description: str,
        context: Dict[str, Any]
    ) -> List[Task]:
        """
        Decomposes a development task into a sequence of subtasks.

        Args:
            description: The description of the development task.
            context: The context for the decomposition.

        Returns:
            A list of decomposed tasks.
        """
        subtasks = []

        # Common development task breakdown
        phases = [
            ("design", "Design component architecture", ["architecture", "design"], 3),
            ("implement", "Implement core functionality", ["coding", "development"], 5),
            ("test", "Write and execute tests", ["testing", "qa"], 3),
            ("integrate", "Integrate with existing system", ["integration", "development"], 2),
            ("document", "Write documentation", ["documentation", "writing"], 2),
        ]

        for i, (phase_id, title, capabilities, effort) in enumerate(phases):
            task = Task(
                task_id=self._generate_task_id(phase_id),
                title=f"{title}: {description}",
                description=f"{title} phase of: {description}",
                task_type=TaskType.DEVELOPMENT,
                priority=TaskPriority.HIGH,
                estimated_effort=effort,
                required_capabilities=capabilities,
                dependencies=self._create_sequential_dependencies(i, phases),
                acceptance_criteria=[f"Complete {title.lower()}"],
                metadata={"phase": phase_id}
            )
            subtasks.append(task)

        return subtasks

    async def _decompose_research_task(
        self,
        description: str,
        context: Dict[str, Any]
    ) -> List[Task]:
        """
        Decomposes a research task into a sequence of subtasks.

        Args:
            description: The description of the research task.
            context: The context for the decomposition.

        Returns:
            A list of decomposed tasks.
        """
        subtasks = []

        research_phases = [
            ("survey", "Literature survey", ["research", "analysis"], 2),
            ("collect", "Data collection", ["research", "data"], 3),
            ("analyze", "Data analysis", ["analysis", "statistics"], 4),
            ("synthesize", "Synthesize findings", ["research", "writing"], 2),
            ("report", "Write research report", ["documentation", "writing"], 3),
        ]

        for i, (phase_id, title, capabilities, effort) in enumerate(research_phases):
            task = Task(
                task_id=self._generate_task_id(phase_id),
                title=f"{title}: {description}",
                description=f"{title} for research task: {description}",
                task_type=TaskType.RESEARCH,
                priority=TaskPriority.MEDIUM,
                estimated_effort=effort,
                required_capabilities=capabilities,
                dependencies=self._create_sequential_dependencies(i, research_phases),
                acceptance_criteria=[f"Complete {title.lower()}"],
                metadata={"phase": phase_id}
            )
            subtasks.append(task)

        return subtasks

    async def _decompose_analysis_task(
        self,
        description: str,
        context: Dict[str, Any]
    ) -> List[Task]:
        """
        Decomposes an analysis task into a sequence of subtasks.

        Args:
            description: The description of the analysis task.
            context: The context for the decomposition.

        Returns:
            A list of decomposed tasks.
        """
        subtasks = []

        analysis_phases = [
            ("scope", "Define analysis scope", ["analysis", "planning"], 2),
            ("gather", "Gather data/information", ["research", "data"], 3),
            ("process", "Process and clean data", ["data", "analysis"], 3),
            ("analyze", "Perform analysis", ["analysis", "statistics"], 4),
            ("visualize", "Create visualizations", ["visualization", "data"], 2),
            ("report", "Write analysis report", ["documentation", "writing"], 2),
        ]

        for i, (phase_id, title, capabilities, effort) in enumerate(analysis_phases):
            task = Task(
                task_id=self._generate_task_id(phase_id),
                title=f"{title}: {description}",
                description=f"{title} for: {description}",
                task_type=TaskType.ANALYSIS,
                priority=TaskPriority.MEDIUM,
                estimated_effort=effort,
                required_capabilities=capabilities,
                dependencies=self._create_sequential_dependencies(i, analysis_phases),
                acceptance_criteria=[f"Complete {title.lower()}"],
                metadata={"phase": phase_id}
            )
            subtasks.append(task)

        return subtasks

    async def _decompose_testing_task(
        self,
        description: str,
        context: Dict[str, Any]
    ) -> List[Task]:
        """
        Decomposes a testing task into a sequence of subtasks.

        Args:
            description: The description of the testing task.
            context: The context for the decomposition.

        Returns:
            A list of decomposed tasks.
        """
        subtasks = []

        testing_phases = [
            ("plan", "Create test plan", ["testing", "planning"], 2),
            ("unit", "Write unit tests", ["testing", "coding"], 3),
            ("integration", "Write integration tests", ["testing", "coding"], 3),
            ("e2e", "Write end-to-end tests", ["testing", "qa"], 2),
            ("execute", "Execute test suite", ["testing", "qa"], 2),
            ("report", "Generate test report", ["documentation", "testing"], 1),
        ]

        for i, (phase_id, title, capabilities, effort) in enumerate(testing_phases):
            task = Task(
                task_id=self._generate_task_id(phase_id),
                title=f"{title}: {description}",
                description=f"{title} for: {description}",
                task_type=TaskType.TESTING,
                priority=TaskPriority.HIGH,
                estimated_effort=effort,
                required_capabilities=capabilities,
                dependencies=self._create_sequential_dependencies(i, testing_phases),
                acceptance_criteria=[f"Complete {title.lower()}"],
                metadata={"phase": phase_id}
            )
            subtasks.append(task)

        return subtasks

    async def _decompose_documentation_task(
        self,
        description: str,
        context: Dict[str, Any]
    ) -> List[Task]:
        """
        Decomposes a documentation task into a sequence of subtasks.

        Args:
            description: The description of the documentation task.
            context: The context for the decomposition.

        Returns:
            A list of decomposed tasks.
        """
        subtasks = []

        doc_phases = [
            ("outline", "Create documentation outline", ["documentation", "planning"], 1),
            ("draft", "Write first draft", ["documentation", "writing"], 3),
            ("review", "Review and refine", ["documentation", "editing"], 2),
            ("examples", "Add code examples", ["documentation", "coding"], 2),
            ("finalize", "Finalize documentation", ["documentation", "writing"], 1),
        ]

        for i, (phase_id, title, capabilities, effort) in enumerate(doc_phases):
            task = Task(
                task_id=self._generate_task_id(phase_id),
                title=f"{title}: {description}",
                description=f"{title} for: {description}",
                task_type=TaskType.DOCUMENTATION,
                priority=TaskPriority.MEDIUM,
                estimated_effort=effort,
                required_capabilities=capabilities,
                dependencies=self._create_sequential_dependencies(i, doc_phases),
                acceptance_criteria=[f"Complete {title.lower()}"],
                metadata={"phase": phase_id}
            )
            subtasks.append(task)

        return subtasks

    async def _decompose_architecture_task(
        self,
        description: str,
        context: Dict[str, Any]
    ) -> List[Task]:
        """
        Decomposes an architecture task into a sequence of subtasks.

        Args:
            description: The description of the architecture task.
            context: The context for the decomposition.

        Returns:
            A list of decomposed tasks.
        """
        subtasks = []

        arch_phases = [
            ("requirements", "Gather requirements", ["architecture", "analysis"], 2),
            ("design", "Design system architecture", ["architecture", "design"], 4),
            ("document", "Document architecture", ["documentation", "architecture"], 3),
            ("review", "Architecture review", ["architecture", "review"], 2),
            ("refine", "Refine based on feedback", ["architecture", "design"], 2),
        ]

        for i, (phase_id, title, capabilities, effort) in enumerate(arch_phases):
            task = Task(
                task_id=self._generate_task_id(phase_id),
                title=f"{title}: {description}",
                description=f"{title} for: {description}",
                task_type=TaskType.ARCHITECTURE,
                priority=TaskPriority.CRITICAL,
                estimated_effort=effort,
                required_capabilities=capabilities,
                dependencies=self._create_sequential_dependencies(i, arch_phases),
                acceptance_criteria=[f"Complete {title.lower()}"],
                metadata={"phase": phase_id}
            )
            subtasks.append(task)

        return subtasks

    def _default_decomposition(
        self,
        description: str,
        task_type: TaskType
    ) -> DecompositionResult:
        """
        A fallback decomposition strategy for when a specific strategy is not available.

        Args:
            description: The description of the task.
            task_type: The type of the task.

        Returns:
            A DecompositionResult with a single, general-purpose task.
        """
        task = Task(
            task_id=self._generate_task_id("default"),
            title=description,
            description=description,
            task_type=task_type,
            priority=TaskPriority.MEDIUM,
            estimated_effort=5,
            required_capabilities=["general"],
            dependencies=[],
            acceptance_criteria=["Complete task"],
            metadata={}
        )

        return DecompositionResult(
            original_task=description,
            subtasks=[task],
            execution_order=[[task.task_id]],
            estimated_total_effort=5,
            critical_path=[task.task_id]
        )

    def _build_execution_order(self, subtasks: List[Task]) -> List[List[str]]:
        """
        Builds an execution order for a list of subtasks, respecting their dependencies.

        Args:
            subtasks: A list of tasks to be ordered.

        Returns:
            A list of lists, where each inner list represents a batch of tasks that can be executed in parallel.
        """
        completed = set()
        execution_order = []

        while len(completed) < len(subtasks):
            # Find tasks that can be executed (all dependencies met)
            batch = []
            for task in subtasks:
                if task.task_id not in completed and task.is_ready(completed):
                    batch.append(task.task_id)

            if not batch:
                # Circular dependency or error
                logger.error("Cannot determine execution order - circular dependency?")
                break

            execution_order.append(batch)
            completed.update(batch)

        return execution_order

    def _calculate_critical_path(
        self,
        subtasks: List[Task],
        execution_order: List[List[str]]
    ) -> List[str]:
        """
        Calculates the critical path for a set of tasks.

        Note: This is a simplified implementation that takes the longest task from each batch.

        Args:
            subtasks: A list of all subtasks.
            execution_order: The execution order of the tasks.

        Returns:
            A list of task IDs representing the critical path.
        """
        path = []
        for batch in execution_order:
            # Find task with highest effort in each batch
            batch_tasks = [t for t in subtasks if t.task_id in batch]
            if batch_tasks:
                longest = max(batch_tasks, key=lambda t: t.estimated_effort)
                path.append(longest.task_id)

        return path

    def _create_sequential_dependencies(
        self,
        current_index: int,
        phases: List[tuple]
    ) -> List[TaskDependency]:
        """
        Creates a sequential dependency on the previous phase.

        Args:
            current_index: The index of the current phase.
            phases: A list of all phases.

        Returns:
            A list containing a single dependency on the previous phase, or an empty list if this is the first phase.
        """
        if current_index == 0:
            return []

        prev_phase_id = phases[current_index - 1][0]
        return [
            TaskDependency(
                task_id=self._generate_task_id(prev_phase_id),
                dependency_type="blocks"
            )
        ]

    def _generate_task_id(self, prefix: str) -> str:
        """
        Generates a unique task ID.

        Args:
            prefix: The prefix for the task ID.

        Returns:
            A unique task ID string.
        """
        self.task_counter += 1
        return f"{prefix}_{self.task_counter:04d}"
