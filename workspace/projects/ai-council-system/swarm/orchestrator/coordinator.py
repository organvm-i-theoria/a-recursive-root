"""
Swarm Coordinator - Main orchestration logic for AI agent swarms

This module coordinates multiple AI agents working together as a swarm to accomplish
complex tasks through role-based collaboration and assembly execution.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import logging

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """
    Enumeration of the possible statuses for an assembly execution.
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionContext:
    """
    Contains the context for a single assembly execution.

    Attributes:
        task_id: A unique identifier for the task.
        input_data: A dictionary containing the input data for the task.
        constraints: A dictionary of constraints for the task execution.
        timeout: An optional timedelta object specifying the maximum execution time.
        metadata: An optional dictionary for storing arbitrary metadata.
    """
    task_id: str
    input_data: Dict[str, Any]
    constraints: Dict[str, Any]
    timeout: Optional[timedelta] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Role:
    """
    Defines a role that can be assigned to an agent within the swarm.

    Attributes:
        name: The name of the role.
        capabilities: A list of capabilities required for this role.
        responsibilities: A list of responsibilities for this role.
        dependencies: A list of other roles that this role depends on.
    """
    name: str
    capabilities: List[str]
    responsibilities: List[str]
    dependencies: List[str]

    def can_fulfill(self, requirements: List[str]) -> bool:
        """
        Checks if the role has all the specified capabilities.

        Args:
            requirements: A list of required capability strings.

        Returns:
            True if the role has all the required capabilities, False otherwise.
        """
        return all(req in self.capabilities for req in requirements)


@dataclass
class Agent:
    """
    Represents an AI agent within the swarm.

    Attributes:
        agent_id: A unique identifier for the agent.
        name: The name of the agent.
        capabilities: A list of capabilities that this agent possesses.
        current_role: The role currently assigned to the agent, if any.
        status: The current status of the agent (e.g., "available", "assigned").
    """
    agent_id: str
    name: str
    capabilities: List[str]
    current_role: Optional[Role] = None
    status: str = "available"

    def assign_role(self, role: Role) -> bool:
        """
        Assigns a role to the agent if the agent has the required capabilities.

        Args:
            role: The role to assign to the agent.

        Returns:
            True if the role was successfully assigned, False otherwise.
        """
        if self.can_perform_role(role):
            self.current_role = role
            self.status = "assigned"
            return True
        return False

    def can_perform_role(self, role: Role) -> bool:
        """
        Checks if the agent has the necessary capabilities to perform a given role.

        Args:
            role: The role to check against.

        Returns:
            True if the agent can perform the role, False otherwise.
        """
        return all(cap in self.capabilities for cap in role.capabilities[:3])


@dataclass
class Workflow:
    """
    Defines the workflow for an assembly, including the sequence of steps.

    Attributes:
        steps: A list of dictionaries, where each dictionary defines a step in the workflow.
        parallel_execution: A boolean indicating whether steps can be executed in parallel.
        error_handling: The error handling strategy to use (e.g., "stop", "continue", "retry").
    """
    steps: List[Dict[str, Any]]
    parallel_execution: bool = False
    error_handling: str = "stop"  # stop, continue, retry


@dataclass
class SuccessCriteria:
    """
    Defines the criteria for the successful completion of an assembly.

    Attributes:
        required_outputs: A list of output keys that must be present for the assembly to be considered successful.
        quality_threshold: A float representing the minimum quality score for success.
        timeout: An optional timedelta for the maximum allowed execution time.
        validation_rules: A list of rules for validating the output.
    """
    required_outputs: List[str]
    quality_threshold: float = 0.8
    timeout: Optional[timedelta] = None
    validation_rules: List[str] = None

    def __post_init__(self):
        if self.validation_rules is None:
            self.validation_rules = []


@dataclass
class Assembly:
    """
    Defines a swarm assembly, which is a configuration for a specific task.

    Attributes:
        name: The name of the assembly.
        description: A description of the assembly's purpose.
        roles: A list of roles required for this assembly.
        workflow: The workflow definition for this assembly.
        success_criteria: The success criteria for this assembly.
        version: The version of the assembly.
    """
    name: str
    description: str
    roles: List[Role]
    workflow: Workflow
    success_criteria: SuccessCriteria
    version: str = "1.0.0"


@dataclass
class Contribution:
    """
    Represents an agent's contribution to an assembly execution.

    Attributes:
        agent_id: The ID of the contributing agent.
        role_name: The name of the role the agent was playing.
        outputs: A dictionary of outputs produced by the agent.
        duration: The duration of the agent's work.
        quality_score: A score representing the quality of the agent's contribution.
    """
    agent_id: str
    role_name: str
    outputs: Dict[str, Any]
    duration: timedelta
    quality_score: float = 0.0


@dataclass
class AssemblyResult:
    """
    Contains the results of an assembly execution.

    Attributes:
        assembly_name: The name of the assembly that was executed.
        status: The final status of the execution.
        outputs: A dictionary of the final outputs of the assembly.
        agent_contributions: A dictionary mapping agent IDs to their contributions.
        duration: The total duration of the assembly execution.
        error_message: An optional error message if the execution failed.
        started_at: The timestamp when the execution started.
        completed_at: The timestamp when the execution completed.
    """
    assembly_name: str
    status: ExecutionStatus
    outputs: Dict[str, Any]
    agent_contributions: Dict[str, Contribution]
    duration: timedelta
    error_message: Optional[str] = None
    started_at: datetime = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.utcnow()


@dataclass
class RoleRequirements:
    """
    Specifies the requirements for role assignment in an assembly.

    Attributes:
        required_roles: A list of role names that are required.
        min_capabilities: A dictionary mapping capability names to the minimum number of agents required with that capability.
    """
    required_roles: List[str]
    min_capabilities: Dict[str, int]


class SwarmCoordinator:
    """
    The main coordinator for all swarm operations.

    This class manages the lifecycle of assemblies, including agent assignment,
    workflow execution, and result aggregation.
    """

    def __init__(self):
        """
        Initializes the SwarmCoordinator.
        """
        self.active_assemblies: Dict[str, Assembly] = {}
        self.available_agents: List[Agent] = []
        self.execution_history: List[AssemblyResult] = []

    async def execute_assembly(
        self,
        assembly: Assembly,
        context: ExecutionContext
    ) -> AssemblyResult:
        """
        Executes a given swarm assembly.

        This method orchestrates the entire lifecycle of an assembly execution,
        from role assignment to result validation.

        Args:
            assembly: The assembly to execute.
            context: The execution context for this assembly.

        Returns:
            An AssemblyResult object containing the results of the execution.
        """
        logger.info(f"Starting assembly execution: {assembly.name}")
        start_time = datetime.utcnow()

        try:
            # Register assembly as active
            self.active_assemblies[context.task_id] = assembly

            # Assign roles to agents
            role_assignments = await self._assign_roles(assembly.roles)
            if not role_assignments:
                raise ValueError("Failed to assign all required roles")

            logger.info(f"Assigned {len(role_assignments)} roles")

            # Execute workflow
            outputs = await self._execute_workflow(
                assembly.workflow,
                role_assignments,
                context
            )

            # Collect contributions
            contributions = await self._collect_contributions(role_assignments)

            # Validate results
            success = self._validate_results(outputs, assembly.success_criteria)

            duration = datetime.utcnow() - start_time

            result = AssemblyResult(
                assembly_name=assembly.name,
                status=ExecutionStatus.COMPLETED if success else ExecutionStatus.FAILED,
                outputs=outputs,
                agent_contributions=contributions,
                duration=duration,
                started_at=start_time,
                completed_at=datetime.utcnow()
            )

            self.execution_history.append(result)
            logger.info(f"Assembly {assembly.name} completed with status: {result.status}")

            return result

        except Exception as e:
            logger.error(f"Assembly execution failed: {str(e)}")
            duration = datetime.utcnow() - start_time

            result = AssemblyResult(
                assembly_name=assembly.name,
                status=ExecutionStatus.FAILED,
                outputs={},
                agent_contributions={},
                duration=duration,
                error_message=str(e),
                started_at=start_time,
                completed_at=datetime.utcnow()
            )
            self.execution_history.append(result)
            return result
        finally:
            # Clean up
            if context.task_id in self.active_assemblies:
                del self.active_assemblies[context.task_id]

    async def assign_roles(
        self,
        agents: List[Agent],
        requirements: RoleRequirements
    ) -> Dict[Agent, Role]:
        """
        Assigns roles to available agents based on a set of requirements.

        Args:
            agents: A list of available agents.
            requirements: The role requirements to be fulfilled.

        Returns:
            A dictionary mapping each assigned agent to their assigned role.
        """
        assignments = {}

        # Sort agents by capability match
        for role_name in requirements.required_roles:
            best_agent = None
            best_score = 0

            for agent in agents:
                if agent in assignments:
                    continue

                score = self._calculate_role_fitness(agent, role_name)
                if score > best_score:
                    best_score = score
                    best_agent = agent

            if best_agent:
                # Create role and assign
                role = Role(
                    name=role_name,
                    capabilities=[],
                    responsibilities=[],
                    dependencies=[]
                )
                assignments[best_agent] = role

        return assignments

    async def _assign_roles(self, roles: List[Role]) -> Dict[str, Agent]:
        """
        Internal method to handle the logic of assigning roles to agents.

        Args:
            roles: A list of roles to be assigned.

        Returns:
            A dictionary mapping role names to the agents assigned to them.
        """
        assignments = {}
        available = self.available_agents.copy()

        for role in roles:
            # Find best agent for this role
            best_agent = None
            best_score = 0

            for agent in available:
                if agent.can_perform_role(role):
                    score = len(set(agent.capabilities) & set(role.capabilities))
                    if score > best_score:
                        best_score = score
                        best_agent = agent

            if best_agent:
                best_agent.assign_role(role)
                assignments[role.name] = best_agent
                available.remove(best_agent)
            else:
                logger.warning(f"No suitable agent found for role: {role.name}")

        return assignments

    async def _execute_workflow(
        self,
        workflow: Workflow,
        role_assignments: Dict[str, Agent],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Executes the workflow of an assembly.

        Args:
            workflow: The workflow to execute.
            role_assignments: A dictionary mapping role names to assigned agents.
            context: The execution context.

        Returns:
            A dictionary containing the outputs of the workflow execution.
        """
        outputs = {}

        if workflow.parallel_execution:
            # Execute steps in parallel
            tasks = [
                self._execute_step(step, role_assignments, context)
                for step in workflow.steps
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Step {i} failed: {result}")
                    if workflow.error_handling == "stop":
                        raise result
                else:
                    outputs.update(result)
        else:
            # Execute steps sequentially
            for step in workflow.steps:
                try:
                    result = await self._execute_step(step, role_assignments, context)
                    outputs.update(result)
                except Exception as e:
                    logger.error(f"Step failed: {e}")
                    if workflow.error_handling == "stop":
                        raise

        return outputs

    async def _execute_step(
        self,
        step: Dict[str, Any],
        role_assignments: Dict[str, Agent],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Executes a single step in a workflow.

        Note: This is a placeholder implementation. In a real implementation, this
        method would delegate the task to the assigned agent.

        Args:
            step: The workflow step to execute.
            role_assignments: A dictionary mapping role names to assigned agents.
            context: The execution context.

        Returns:
            A dictionary containing the output of the step.
        """
        role_name = step.get("role")
        action = step.get("action")

        logger.info(f"Executing step: {action} with role: {role_name}")

        # Simulate execution
        await asyncio.sleep(0.1)

        return {f"{role_name}_{action}": "completed"}

    async def _collect_contributions(
        self,
        role_assignments: Dict[str, Agent]
    ) -> Dict[str, Contribution]:
        """
        Collects the contributions from all agents involved in an assembly.

        Args:
            role_assignments: A dictionary mapping role names to assigned agents.

        Returns:
            A dictionary mapping agent IDs to their contributions.
        """
        contributions = {}

        for role_name, agent in role_assignments.items():
            contribution = Contribution(
                agent_id=agent.agent_id,
                role_name=role_name,
                outputs={},
                duration=timedelta(seconds=1),
                quality_score=0.85
            )
            contributions[agent.agent_id] = contribution

        return contributions

    def _validate_results(
        self,
        outputs: Dict[str, Any],
        criteria: SuccessCriteria
    ) -> bool:
        """
        Validates the results of an assembly execution against its success criteria.

        Args:
            outputs: The outputs of the assembly execution.
            criteria: The success criteria for the assembly.

        Returns:
            True if the results are valid, False otherwise.
        """
        # Check all required outputs are present
        for required in criteria.required_outputs:
            if required not in outputs:
                logger.warning(f"Missing required output: {required}")
                return False

        # Additional validation could be added here
        return True

    def _calculate_role_fitness(self, agent: Agent, role_name: str) -> float:
        """
        Calculates how well an agent is suited for a given role.

        Note: This is a placeholder implementation. A real implementation would
        use a more sophisticated matching algorithm.

        Args:
            agent: The agent to evaluate.
            role_name: The name of the role to evaluate against.

        Returns:
            A fitness score between 0.0 and 1.0.
        """
        return 0.5

    def register_agent(self, agent: Agent) -> None:
        """
        Registers a new agent with the coordinator, making it available for assignments.

        Args:
            agent: The agent to register.
        """
        if agent not in self.available_agents:
            self.available_agents.append(agent)
            logger.info(f"Registered agent: {agent.name}")

    def unregister_agent(self, agent_id: str) -> None:
        """
        Unregisters an agent from the coordinator.

        Args:
            agent_id: The ID of the agent to unregister.
        """
        self.available_agents = [
            a for a in self.available_agents
            if a.agent_id != agent_id
        ]
        logger.info(f"Unregistered agent: {agent_id}")

    def get_active_assemblies(self) -> List[str]:
        """
        Gets a list of the names of all currently active assemblies.

        Returns:
            A list of active assembly names.
        """
        return list(self.active_assemblies.keys())

    def get_execution_history(self) -> List[AssemblyResult]:
        """
        Gets the execution history of all completed assemblies.

        Returns:
            A list of AssemblyResult objects.
        """
        return self.execution_history.copy()
