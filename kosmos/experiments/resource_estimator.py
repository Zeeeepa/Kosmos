"""
Resource Estimation for Experiments.

Estimates compute, time, and cost requirements for experimental protocols.
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

from kosmos.models.hypothesis import Hypothesis, ExperimentType
from kosmos.models.experiment import (
    ExperimentProtocol,
    ResourceRequirements,
)

logger = logging.getLogger(__name__)


class ComplexityLevel(str, Enum):
    """Complexity level for resource estimation."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class ResourceEstimator:
    """
    Estimates resource requirements for experiments.

    Provides heuristic-based estimates with optional LLM enhancement.

    Example:
        ```python
        estimator = ResourceEstimator()
        resources = estimator.estimate(
            experiment_type=ExperimentType.COMPUTATIONAL,
            hypothesis=hypothesis,
            num_steps=5,
            sample_size=100
        )
        print(f"Cost: ${resources.estimated_cost_usd}")
        print(f"Duration: {resources.estimated_duration_days} days")
        ```
    """

    def __init__(self, use_llm_enhancement: bool = False):
        """
        Initialize resource estimator.

        Args:
            use_llm_enhancement: Whether to use LLM for enhanced estimates
        """
        self.use_llm_enhancement = use_llm_enhancement

        # Base costs (USD)
        self.base_costs = {
            ExperimentType.DATA_ANALYSIS: 2.0,
            ExperimentType.COMPUTATIONAL: 10.0,
            ExperimentType.LITERATURE_SYNTHESIS: 25.0,  # High due to API costs
        }

        # Base compute hours
        self.base_compute = {
            ExperimentType.DATA_ANALYSIS: 2.0,
            ExperimentType.COMPUTATIONAL: 12.0,
            ExperimentType.LITERATURE_SYNTHESIS: 0.5,
        }

        # Base duration (days)
        self.base_duration = {
            ExperimentType.DATA_ANALYSIS: 0.5,
            ExperimentType.COMPUTATIONAL: 1.5,
            ExperimentType.LITERATURE_SYNTHESIS: 3.0,
        }

    def estimate(
        self,
        experiment_type: ExperimentType,
        hypothesis: Optional[Hypothesis] = None,
        protocol: Optional[ExperimentProtocol] = None,
        num_steps: int = 5,
        sample_size: Optional[int] = None,
        complexity: ComplexityLevel = ComplexityLevel.MODERATE
    ) -> ResourceRequirements:
        """
        Estimate resource requirements.

        Args:
            experiment_type: Type of experiment
            hypothesis: Optional hypothesis for context
            protocol: Optional protocol for detailed estimation
            num_steps: Number of protocol steps
            sample_size: Sample size if applicable
            complexity: Complexity level

        Returns:
            ResourceRequirements with estimates
        """
        logger.info(f"Estimating resources for {experiment_type.value} experiment (complexity: {complexity.value})")

        # Get base estimates
        base_cost = self.base_costs.get(experiment_type, 5.0)
        base_compute = self.base_compute.get(experiment_type, 5.0)
        base_duration = self.base_duration.get(experiment_type, 1.0)

        # Apply complexity multipliers
        complexity_multipliers = {
            ComplexityLevel.SIMPLE: 0.5,
            ComplexityLevel.MODERATE: 1.0,
            ComplexityLevel.COMPLEX: 2.0,
            ComplexityLevel.VERY_COMPLEX: 4.0,
        }
        multiplier = complexity_multipliers.get(complexity, 1.0)

        # Adjust for number of steps
        step_multiplier = max(0.5, min(3.0, num_steps / 5.0))

        # Adjust for sample size
        sample_multiplier = 1.0
        if sample_size:
            if sample_size < 50:
                sample_multiplier = 0.8
            elif sample_size > 500:
                sample_multiplier = 1.5
            elif sample_size > 1000:
                sample_multiplier = 2.0

        # Calculate estimates
        compute_hours = base_compute * multiplier * step_multiplier
        estimated_cost = base_cost * multiplier * step_multiplier * sample_multiplier
        duration_days = base_duration * multiplier * step_multiplier

        # Memory estimation (GB)
        memory_gb = self._estimate_memory(experiment_type, sample_size)

        # GPU requirements
        gpu_required = self._requires_gpu(experiment_type, hypothesis)

        # Required libraries
        required_libraries = self._get_required_libraries(experiment_type)

        # Parallelization potential
        can_parallelize = experiment_type == ExperimentType.COMPUTATIONAL
        parallelization_factor = 4 if can_parallelize else None

        # API calls estimate (for literature synthesis)
        api_calls = None
        if experiment_type == ExperimentType.LITERATURE_SYNTHESIS:
            api_calls = self._estimate_api_calls(num_steps, sample_size)

        resources = ResourceRequirements(
            compute_hours=round(compute_hours, 1),
            memory_gb=memory_gb,
            gpu_required=gpu_required,
            gpu_memory_gb=24 if gpu_required else None,
            estimated_cost_usd=round(estimated_cost, 2),
            api_calls_estimated=api_calls,
            estimated_duration_days=round(duration_days, 2),
            required_libraries=required_libraries,
            python_version="3.9+",
            can_parallelize=can_parallelize,
            parallelization_factor=parallelization_factor,
        )

        logger.info(
            f"Estimated resources: ${resources.estimated_cost_usd:.2f}, "
            f"{resources.compute_hours:.1f}h compute, "
            f"{resources.estimated_duration_days:.1f} days"
        )

        return resources

    def _estimate_memory(
        self,
        experiment_type: ExperimentType,
        sample_size: Optional[int]
    ) -> float:
        """Estimate memory requirements (GB)."""
        base_memory = {
            ExperimentType.DATA_ANALYSIS: 4.0,
            ExperimentType.COMPUTATIONAL: 8.0,
            ExperimentType.LITERATURE_SYNTHESIS: 2.0,
        }

        memory = base_memory.get(experiment_type, 4.0)

        # Adjust for sample size
        if sample_size:
            if sample_size > 10000:
                memory *= 2.0
            elif sample_size > 100000:
                memory *= 4.0

        return round(memory, 1)

    def _requires_gpu(
        self,
        experiment_type: ExperimentType,
        hypothesis: Optional[Hypothesis]
    ) -> bool:
        """Determine if GPU is required."""
        if experiment_type != ExperimentType.COMPUTATIONAL:
            return False

        if not hypothesis:
            return False

        # Check for deep learning keywords
        statement = hypothesis.statement.lower()
        ml_keywords = [
            "neural network", "deep learning", "transformer",
            "cnn", "rnn", "lstm", "bert", "gpt",
            "training", "fine-tuning"
        ]

        return any(kw in statement for kw in ml_keywords)

    def _get_required_libraries(self, experiment_type: ExperimentType) -> list:
        """Get required Python libraries."""
        common = ["numpy", "pandas"]

        type_specific = {
            ExperimentType.DATA_ANALYSIS: ["scipy", "statsmodels", "matplotlib", "seaborn"],
            ExperimentType.COMPUTATIONAL: ["numpy", "scipy"],
            ExperimentType.LITERATURE_SYNTHESIS: ["anthropic"],
        }

        return common + type_specific.get(experiment_type, [])

    def _estimate_api_calls(
        self,
        num_steps: int,
        sample_size: Optional[int]
    ) -> int:
        """Estimate number of API calls for literature synthesis."""
        # Base calls for analysis
        base_calls = num_steps * 10

        # Add calls for paper processing
        if sample_size:
            # Assuming sample_size papers to analyze
            base_calls += sample_size * 2  # 2 calls per paper (summary + extraction)

        return base_calls

    def check_availability(
        self,
        requirements: ResourceRequirements,
        available_budget: Optional[float] = None,
        available_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Check if resources are available within constraints.

        Args:
            requirements: Required resources
            available_budget: Available budget (USD)
            available_time: Available time (days)

        Returns:
            Dict with availability status and recommendations
        """
        result = {
            "available": True,
            "warnings": [],
            "blockers": [],
            "recommendations": []
        }

        # Check budget
        if available_budget and requirements.estimated_cost_usd:
            if requirements.estimated_cost_usd > available_budget:
                result["available"] = False
                result["blockers"].append(
                    f"Cost ${requirements.estimated_cost_usd:.2f} exceeds "
                    f"budget ${available_budget:.2f}"
                )
            elif requirements.estimated_cost_usd > available_budget * 0.8:
                result["warnings"].append(
                    f"Cost ${requirements.estimated_cost_usd:.2f} is "
                    f"80%+ of budget ${available_budget:.2f}"
                )

        # Check time
        if available_time and requirements.estimated_duration_days:
            if requirements.estimated_duration_days > available_time:
                result["available"] = False
                result["blockers"].append(
                    f"Duration {requirements.estimated_duration_days:.1f} days exceeds "
                    f"available time {available_time:.1f} days"
                )
            elif requirements.estimated_duration_days > available_time * 0.8:
                result["warnings"].append(
                    f"Duration {requirements.estimated_duration_days:.1f} days is "
                    f"80%+ of available time {available_time:.1f} days"
                )

        # Recommendations
        if requirements.can_parallelize and requirements.compute_hours > 24:
            result["recommendations"].append(
                f"Consider parallelizing across {requirements.parallelization_factor} cores "
                f"to reduce duration"
            )

        if requirements.gpu_required:
            result["recommendations"].append(
                "GPU required - ensure GPU resources are available"
            )

        if requirements.api_calls_estimated and requirements.api_calls_estimated > 100:
            cost_per_call = 0.01  # Rough estimate
            api_cost = requirements.api_calls_estimated * cost_per_call
            result["recommendations"].append(
                f"~{requirements.api_calls_estimated} API calls estimated "
                f"(~${api_cost:.2f} in API costs)"
            )

        return result

    def optimize_resources(
        self,
        requirements: ResourceRequirements,
        max_cost: Optional[float] = None,
        max_duration: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Suggest optimizations to meet constraints.

        Args:
            requirements: Current resource requirements
            max_cost: Maximum cost constraint
            max_duration: Maximum duration constraint

        Returns:
            Dict with optimization suggestions
        """
        suggestions = []

        # Cost optimizations
        if max_cost and requirements.estimated_cost_usd and requirements.estimated_cost_usd > max_cost:
            reduction_needed = requirements.estimated_cost_usd - max_cost

            suggestions.append({
                "type": "cost_reduction",
                "issue": f"Need to reduce cost by ${reduction_needed:.2f}",
                "options": [
                    "Reduce sample size to lower computational cost",
                    "Use simpler statistical methods",
                    "Reduce number of experimental conditions",
                    "Cache and reuse intermediate results"
                ]
            })

        # Duration optimizations
        if max_duration and requirements.estimated_duration_days and requirements.estimated_duration_days > max_duration:
            reduction_needed = requirements.estimated_duration_days - max_duration

            options = []
            if requirements.can_parallelize:
                options.append(
                    f"Parallelize across {requirements.parallelization_factor} cores "
                    f"to reduce duration by ~{requirements.parallelization_factor}x"
                )
            else:
                options.append("Simplify protocol to fewer steps")

            options.extend([
                "Use pre-computed datasets instead of generating new data",
                "Reduce number of replications",
            ])

            suggestions.append({
                "type": "duration_reduction",
                "issue": f"Need to reduce duration by {reduction_needed:.1f} days",
                "options": options
            })

        return {
            "optimizations_needed": len(suggestions) > 0,
            "suggestions": suggestions
        }
