"""
Result Aggregator - Combines outputs from multiple agents

Aggregates, synthesizes, and validates results from multiple agents
working on decomposed tasks within an assembly.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AggregationStrategy(Enum):
    """
    Enumeration of the strategies for aggregating results from multiple agents.
    """
    MERGE = "merge"  # Merge all outputs
    VOTE = "vote"  # Use majority voting
    CONSENSUS = "consensus"  # Require consensus
    WEIGHTED = "weighted"  # Weighted combination
    BEST = "best"  # Select best result
    SEQUENTIAL = "sequential"  # Sequential pipeline


@dataclass
class AgentOutput:
    """
    Represents the output from a single agent for a given task.

    Attributes:
        agent_id: The ID of the agent that produced the output.
        role_name: The name of the role the agent was playing.
        output_data: A dictionary containing the agent's output.
        confidence: A score representing the agent's confidence in its output.
        metadata: A dictionary for storing arbitrary metadata.
        timestamp: The timestamp of when the output was generated.
    """
    agent_id: str
    role_name: str
    output_data: Dict[str, Any]
    confidence: float
    metadata: Dict[str, Any]
    timestamp: str

    def validate(self) -> bool:
        """
        Validates the agent's output.

        Returns:
            True if the output is valid, False otherwise.
        """
        if not self.output_data:
            return False
        if self.confidence < 0 or self.confidence > 1:
            return False
        return True


@dataclass
class AggregatedResult:
    """
    Represents the aggregated result from multiple agents.

    Attributes:
        outputs: The final, aggregated outputs.
        contributing_agents: A list of IDs of the agents who contributed to the result.
        confidence: The overall confidence in the aggregated result.
        strategy_used: The aggregation strategy that was used.
        conflicts: A list of any conflicts that were detected during aggregation.
        metadata: A dictionary for storing arbitrary metadata.
    """
    outputs: Dict[str, Any]
    contributing_agents: List[str]
    confidence: float
    strategy_used: AggregationStrategy
    conflicts: List[Dict[str, Any]]
    metadata: Dict[str, Any]


@dataclass
class ValidationResult:
    """
    Represents the result of a validation check on an aggregated result.

    Attributes:
        is_valid: A boolean indicating whether the result is valid.
        errors: A list of any errors that were found.
        warnings: A list of any warnings that were found.
        quality_score: A score representing the quality of the result.
    """
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    quality_score: float


class ResultAggregator:
    """
    Aggregates results from multiple agents using various strategies.

    This class provides methods for combining the outputs of multiple agents,
    resolving conflicts, and validating the final results.
    """

    def __init__(self):
        """
        Initializes the ResultAggregator.
        """
        self.aggregation_strategies = {
            AggregationStrategy.MERGE: self._merge_strategy,
            AggregationStrategy.VOTE: self._vote_strategy,
            AggregationStrategy.CONSENSUS: self._consensus_strategy,
            AggregationStrategy.WEIGHTED: self._weighted_strategy,
            AggregationStrategy.BEST: self._best_strategy,
            AggregationStrategy.SEQUENTIAL: self._sequential_strategy,
        }

    async def aggregate(
        self,
        agent_outputs: List[AgentOutput],
        strategy: AggregationStrategy = AggregationStrategy.MERGE,
        config: Optional[Dict[str, Any]] = None
    ) -> AggregatedResult:
        """
        Aggregates the outputs from multiple agents using a specified strategy.

        Args:
            agent_outputs: A list of AgentOutput objects.
            strategy: The aggregation strategy to use.
            config: An optional dictionary of configuration for the aggregation strategy.

        Returns:
            An AggregatedResult object containing the combined outputs.
        """
        logger.info(
            f"Aggregating {len(agent_outputs)} outputs "
            f"using strategy: {strategy.value}"
        )

        # Validate inputs
        valid_outputs = [out for out in agent_outputs if out.validate()]
        if len(valid_outputs) < len(agent_outputs):
            logger.warning(
                f"Filtered out {len(agent_outputs) - len(valid_outputs)} "
                f"invalid outputs"
            )

        if not valid_outputs:
            logger.error("No valid outputs to aggregate")
            return self._empty_result(strategy)

        # Select and execute strategy
        strategy_func = self.aggregation_strategies.get(strategy)
        if not strategy_func:
            logger.warning(f"Unknown strategy {strategy}, using MERGE")
            strategy_func = self._merge_strategy

        config = config or {}
        result = await strategy_func(valid_outputs, config)

        logger.info(
            f"Aggregation complete. "
            f"Confidence: {result.confidence:.2f}, "
            f"Conflicts: {len(result.conflicts)}"
        )

        return result

    async def validate_result(
        self,
        result: AggregatedResult,
        requirements: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validates an aggregated result against a set of requirements.

        Args:
            result: The aggregated result to validate.
            requirements: A dictionary of validation requirements.

        Returns:
            A ValidationResult object.
        """
        errors = []
        warnings = []
        quality_score = result.confidence

        # Check required outputs
        required_keys = requirements.get("required_outputs", [])
        for key in required_keys:
            if key not in result.outputs:
                errors.append(f"Missing required output: {key}")

        # Check conflicts
        if result.conflicts and len(result.conflicts) > 0:
            conflict_threshold = requirements.get("max_conflicts", 3)
            if len(result.conflicts) > conflict_threshold:
                errors.append(
                    f"Too many conflicts: {len(result.conflicts)} "
                    f"(max: {conflict_threshold})"
                )
            else:
                warnings.append(f"Found {len(result.conflicts)} conflicts")

        # Check confidence threshold
        min_confidence = requirements.get("min_confidence", 0.7)
        if result.confidence < min_confidence:
            errors.append(
                f"Confidence {result.confidence:.2f} "
                f"below threshold {min_confidence}"
            )

        # Adjust quality score based on issues
        quality_score -= len(errors) * 0.1
        quality_score -= len(warnings) * 0.05
        quality_score = max(0.0, min(1.0, quality_score))

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            quality_score=quality_score
        )

    async def resolve_conflicts(
        self,
        conflicts: List[Dict[str, Any]],
        strategy: str = "majority"
    ) -> Dict[str, Any]:
        """
        Resolves conflicts between agent outputs.

        Args:
            conflicts: A list of conflicts to resolve.
            strategy: The resolution strategy to use (e.g., "majority", "weighted", "manual").

        Returns:
            A dictionary representing the resolved output.
        """
        if not conflicts:
            return {}

        if strategy == "majority":
            return self._resolve_by_majority(conflicts)
        elif strategy == "weighted":
            return self._resolve_by_weight(conflicts)
        elif strategy == "confidence":
            return self._resolve_by_confidence(conflicts)
        else:
            logger.warning(f"Unknown resolution strategy: {strategy}")
            return conflicts[0] if conflicts else {}

    # Aggregation Strategy Implementations

    async def _merge_strategy(
        self,
        outputs: List[AgentOutput],
        config: Dict[str, Any]
    ) -> AggregatedResult:
        """
        Merges all agent outputs into a single result.

        Args:
            outputs: A list of agent outputs.
            config: The configuration for the merge strategy.

        Returns:
            An AggregatedResult object.
        """
        merged = {}
        conflicts = []

        for output in outputs:
            for key, value in output.output_data.items():
                if key in merged and merged[key] != value:
                    # Conflict detected
                    conflicts.append({
                        "key": key,
                        "values": [merged[key], value],
                        "agents": [
                            next(
                                o.agent_id for o in outputs
                                if key in o.output_data and o.output_data[key] == merged[key]
                            ),
                            output.agent_id
                        ]
                    })
                merged[key] = value

        avg_confidence = sum(o.confidence for o in outputs) / len(outputs) if outputs else 0.0

        return AggregatedResult(
            outputs=merged,
            contributing_agents=[o.agent_id for o in outputs],
            confidence=avg_confidence,
            strategy_used=AggregationStrategy.MERGE,
            conflicts=conflicts,
            metadata={"num_outputs": len(outputs)}
        )

    async def _vote_strategy(
        self,
        outputs: List[AgentOutput],
        config: Dict[str, Any]
    ) -> AggregatedResult:
        """
        Uses majority voting to determine the final output for each key.

        Args:
            outputs: A list of agent outputs.
            config: The configuration for the vote strategy.

        Returns:
            An AggregatedResult object.
        """
        votes: Dict[str, Dict[Any, int]] = {}
        all_keys = set()

        # Collect votes
        for output in outputs:
            all_keys.update(output.output_data.keys())
            for key, value in output.output_data.items():
                if key not in votes:
                    votes[key] = {}
                value_str = str(value)
                votes[key][value_str] = votes[key].get(value_str, 0) + 1

        # Determine winners
        result = {}
        conflicts = []
        for key in all_keys:
            if key in votes:
                sorted_votes = sorted(
                    votes[key].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                if len(sorted_votes) > 1 and sorted_votes[0][1] == sorted_votes[1][1]:
                    # Tie - conflict
                    conflicts.append({
                        "key": key,
                        "values": [v[0] for v in sorted_votes[:2]],
                        "votes": [v[1] for v in sorted_votes[:2]]
                    })
                result[key] = sorted_votes[0][0]

        # Calculate confidence based on vote strength
        total_votes = sum(sum(v.values()) for v in votes.values())
        winning_votes = sum(max(v.values()) for v in votes.values()) if votes else 0
        confidence = winning_votes / total_votes if total_votes > 0 else 0.0

        return AggregatedResult(
            outputs=result,
            contributing_agents=[o.agent_id for o in outputs],
            confidence=confidence,
            strategy_used=AggregationStrategy.VOTE,
            conflicts=conflicts,
            metadata={"total_votes": total_votes}
        )

    async def _consensus_strategy(
        self,
        outputs: List[AgentOutput],
        config: Dict[str, Any]
    ) -> AggregatedResult:
        """
        Requires consensus among all agents for an output to be included.

        Args:
            outputs: A list of agent outputs.
            config: The configuration for the consensus strategy.

        Returns:
            An AggregatedResult object.
        """
        if not outputs:
            return self._empty_result(AggregationStrategy.CONSENSUS)

        # Use first output as baseline
        consensus = outputs[0].output_data.copy()
        conflicts = []

        # Check all outputs match
        for output in outputs[1:]:
            for key, value in output.output_data.items():
                if key in consensus:
                    if consensus[key] != value:
                        conflicts.append({
                            "key": key,
                            "values": [consensus[key], value],
                            "agents": [outputs[0].agent_id, output.agent_id]
                        })
                        # Remove from consensus if disagreement
                        del consensus[key]

        # Confidence is 1.0 if perfect consensus, 0.0 if no agreement
        all_keys = set()
        for output in outputs:
            all_keys.update(output.output_data.keys())

        confidence = len(consensus) / len(all_keys) if all_keys else 0.0

        return AggregatedResult(
            outputs=consensus,
            contributing_agents=[o.agent_id for o in outputs],
            confidence=confidence,
            strategy_used=AggregationStrategy.CONSENSUS,
            conflicts=conflicts,
            metadata={"consensus_keys": len(consensus)}
        )

    async def _weighted_strategy(
        self,
        outputs: List[AgentOutput],
        config: Dict[str, Any]
    ) -> AggregatedResult:
        """
        Weights outputs by the confidence score of each agent.

        Args:
            outputs: A list of agent outputs.
            config: The configuration for the weighted strategy.

        Returns:
            An AggregatedResult object.
        """
        weighted = {}
        weights: Dict[str, List[tuple]] = {}  # key -> [(value, weight)]

        for output in outputs:
            for key, value in output.output_data.items():
                if key not in weights:
                    weights[key] = []
                weights[key].append((value, output.confidence))

        # Select highest weighted value for each key
        for key, value_weights in weights.items():
            weighted[key] = max(value_weights, key=lambda x: x[1])[0]

        # Average confidence weighted by contributions
        total_weight = sum(o.confidence for o in outputs)
        confidence = total_weight / len(outputs) if outputs else 0.0

        return AggregatedResult(
            outputs=weighted,
            contributing_agents=[o.agent_id for o in outputs],
            confidence=confidence,
            strategy_used=AggregationStrategy.WEIGHTED,
            conflicts=[],
            metadata={"total_weight": total_weight}
        )

    async def _best_strategy(
        self,
        outputs: List[AgentOutput],
        config: Dict[str, Any]
    ) -> AggregatedResult:
        """
        Selects the best output based on the highest confidence score.

        Args:
            outputs: A list of agent outputs.
            config: The configuration for the best strategy.

        Returns:
            An AggregatedResult object.
        """
        if not outputs:
            return self._empty_result(AggregationStrategy.BEST)

        best = max(outputs, key=lambda o: o.confidence)

        return AggregatedResult(
            outputs=best.output_data,
            contributing_agents=[best.agent_id],
            confidence=best.confidence,
            strategy_used=AggregationStrategy.BEST,
            conflicts=[],
            metadata={"selected_agent": best.agent_id}
        )

    async def _sequential_strategy(
        self,
        outputs: List[AgentOutput],
        config: Dict[str, Any]
    ) -> AggregatedResult:
        """
        Processes outputs sequentially, allowing later outputs to override earlier ones.

        Args:
            outputs: A list of agent outputs.
            config: The configuration for the sequential strategy.

        Returns:
            An AggregatedResult object.
        """
        result = {}

        # Process in order, allowing later outputs to override
        for output in outputs:
            result.update(output.output_data)

        avg_confidence = sum(o.confidence for o in outputs) / len(outputs) if outputs else 0.0

        return AggregatedResult(
            outputs=result,
            contributing_agents=[o.agent_id for o in outputs],
            confidence=avg_confidence,
            strategy_used=AggregationStrategy.SEQUENTIAL,
            conflicts=[],
            metadata={"pipeline_length": len(outputs)}
        )

    # Conflict Resolution Helpers

    def _resolve_by_majority(self, conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolves conflicts by majority rule.

        Note: This is a simplified implementation.

        Args:
            conflicts: A list of conflicts to resolve.

        Returns:
            A dictionary of resolved values.
        """
        return {c["key"]: c["values"][0] for c in conflicts}

    def _resolve_by_weight(self, conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolves conflicts by weighted voting.

        Note: This is a simplified implementation.

        Args:
            conflicts: A list of conflicts to resolve.

        Returns:
            A dictionary of resolved values.
        """
        return {c["key"]: c["values"][0] for c in conflicts}

    def _resolve_by_confidence(self, conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolves conflicts by agent confidence.

        Note: This is a simplified implementation.

        Args:
            conflicts: A list of conflicts to resolve.

        Returns:
            A dictionary of resolved values.
        """
        return {c["key"]: c["values"][0] for c in conflicts}

    def _empty_result(self, strategy: AggregationStrategy) -> AggregatedResult:
        """
        Creates an empty AggregatedResult.

        Args:
            strategy: The aggregation strategy that was attempted.

        Returns:
            An empty AggregatedResult object.
        """
        return AggregatedResult(
            outputs={},
            contributing_agents=[],
            confidence=0.0,
            strategy_used=strategy,
            conflicts=[],
            metadata={}
        )
