"""
Base template system for experiment protocols.

Provides abstract base class and registry for experiment templates.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Type
from pydantic import BaseModel, Field
from datetime import datetime

from kosmos.models.experiment import (
    ExperimentProtocol,
    ExperimentType,
    ProtocolStep,
    Variable,
    ControlGroup,
    ResourceRequirements,
    StatisticalTestSpec,
    ValidationCheck,
)
from kosmos.models.hypothesis import Hypothesis


class TemplateMetadata(BaseModel):
    """Metadata about an experiment template."""
    name: str = Field(..., description="Unique template name")
    version: str = Field(default="1.0.0", description="Template version")
    experiment_type: ExperimentType
    domain: Optional[str] = None  # None means general-purpose

    title: str = Field(..., description="Human-readable title")
    description: str = Field(..., min_length=50, description="Template description")

    # Applicability
    suitable_for: List[str] = Field(default_factory=list, description="Types of hypotheses this works for")
    requirements: List[str] = Field(default_factory=list, description="Prerequisites for using this template")

    # Quality metrics
    complexity_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Template complexity (0=simple, 1=advanced)")
    rigor_score: float = Field(default=0.7, ge=0.0, le=1.0, description="Expected scientific rigor")

    # Authorship
    author: str = Field(default="kosmos", description="Template author")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    # Usage statistics (tracked by registry)
    times_used: int = Field(default=0, ge=0)
    avg_success_rate: Optional[float] = Field(None, ge=0.0, le=1.0)


class TemplateCustomizationParams(BaseModel):
    """Parameters for customizing a template to a specific hypothesis."""
    hypothesis: Hypothesis

    # Override defaults
    sample_size: Optional[int] = None
    control_groups: Optional[List[str]] = None
    statistical_tests: Optional[List[str]] = None

    # Resource constraints
    max_cost_usd: Optional[float] = None
    max_duration_days: Optional[float] = None
    max_compute_hours: Optional[float] = None

    # Additional customization
    custom_variables: Optional[Dict[str, Any]] = None
    custom_steps: Optional[List[Dict[str, Any]]] = None
    additional_context: Optional[Dict[str, Any]] = None


class TemplateValidationResult(BaseModel):
    """Result of template validation."""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Add a validation error."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add a validation warning."""
        self.warnings.append(message)

    def add_suggestion(self, message: str) -> None:
        """Add a suggestion for improvement."""
        self.suggestions.append(message)


class TemplateBase(ABC):
    """
    Abstract base class for experiment templates.

    All experiment templates must inherit from this class and implement
    the required methods.

    Example:
        ```python
        class TTestTemplate(TemplateBase):
            def __init__(self):
                super().__init__(
                    name="t_test_comparison",
                    experiment_type=ExperimentType.DATA_ANALYSIS,
                    title="T-Test Comparison Template"
                )

            def generate_protocol(
                self,
                params: TemplateCustomizationParams
            ) -> ExperimentProtocol:
                # Generate protocol for t-test comparison
                pass

            def is_applicable(self, hypothesis: Hypothesis) -> bool:
                # Check if hypothesis is suitable for t-test
                return "compare" in hypothesis.statement.lower()
        ```
    """

    def __init__(
        self,
        name: str,
        experiment_type: ExperimentType,
        title: str,
        description: str = "",
        domain: Optional[str] = None,
        version: str = "1.0.0",
        **kwargs
    ):
        """Initialize template with metadata."""
        self.metadata = TemplateMetadata(
            name=name,
            version=version,
            experiment_type=experiment_type,
            domain=domain,
            title=title,
            description=description or f"Template for {title}",
            **kwargs
        )

    @abstractmethod
    def generate_protocol(
        self,
        params: TemplateCustomizationParams
    ) -> ExperimentProtocol:
        """
        Generate an experiment protocol from this template.

        Args:
            params: Customization parameters including hypothesis

        Returns:
            Complete experiment protocol

        Raises:
            ValueError: If parameters are invalid or incompatible
        """
        pass

    @abstractmethod
    def is_applicable(self, hypothesis: Hypothesis) -> bool:
        """
        Check if this template is suitable for the given hypothesis.

        Args:
            hypothesis: Hypothesis to check

        Returns:
            True if template can be used for this hypothesis
        """
        pass

    def validate_template(self) -> TemplateValidationResult:
        """
        Validate the template structure and content.

        Returns:
            Validation result with errors/warnings/suggestions
        """
        result = TemplateValidationResult(is_valid=True)

        # Validate metadata
        if not self.metadata.name:
            result.add_error("Template must have a name")

        if not self.metadata.title:
            result.add_error("Template must have a title")

        if len(self.metadata.description) < 20:
            result.add_warning("Template description should be more detailed (20+ chars)")

        # Validate experiment type
        if not isinstance(self.metadata.experiment_type, ExperimentType):
            result.add_error("Template must specify valid experiment type")

        return result

    def estimate_resources(
        self,
        params: TemplateCustomizationParams
    ) -> ResourceRequirements:
        """
        Estimate resource requirements for this template.

        Default implementation provides basic estimates.
        Override in subclasses for template-specific estimation.

        Args:
            params: Customization parameters

        Returns:
            Resource requirements estimate
        """
        # Default estimates by experiment type
        defaults = {
            ExperimentType.COMPUTATIONAL: {
                "compute_hours": 24.0,
                "memory_gb": 8.0,
                "estimated_duration_days": 2.0,
                "estimated_cost_usd": 10.0,
            },
            ExperimentType.DATA_ANALYSIS: {
                "compute_hours": 4.0,
                "memory_gb": 4.0,
                "estimated_duration_days": 1.0,
                "estimated_cost_usd": 2.0,
            },
            ExperimentType.LITERATURE_SYNTHESIS: {
                "compute_hours": 1.0,
                "memory_gb": 2.0,
                "estimated_duration_days": 0.5,
                "estimated_cost_usd": 5.0,  # Mostly API costs
                "api_calls_estimated": 50,
            },
        }

        base = defaults.get(self.metadata.experiment_type, {})

        return ResourceRequirements(
            compute_hours=base.get("compute_hours"),
            memory_gb=base.get("memory_gb"),
            estimated_duration_days=base.get("estimated_duration_days"),
            estimated_cost_usd=base.get("estimated_cost_usd"),
            api_calls_estimated=base.get("api_calls_estimated"),
            gpu_required=False,
            required_libraries=self.get_required_libraries(),
            can_parallelize=False,
        )

    def get_required_libraries(self) -> List[str]:
        """
        Get list of Python libraries required by this template.

        Returns:
            List of library names (e.g., ["numpy", "scipy", "pandas"])
        """
        # Common libraries for all templates
        common = ["numpy", "pandas"]

        # Add experiment-type specific libraries
        type_specific = {
            ExperimentType.DATA_ANALYSIS: ["scipy", "scikit-learn", "statsmodels"],
            ExperimentType.COMPUTATIONAL: ["numpy", "scipy"],
            ExperimentType.LITERATURE_SYNTHESIS: ["anthropic"],  # For Claude API
        }

        return common + type_specific.get(self.metadata.experiment_type, [])

    def get_default_control_groups(
        self,
        hypothesis: Hypothesis
    ) -> List[ControlGroup]:
        """
        Get default control groups for this template.

        Override in subclasses to provide template-specific controls.

        Args:
            hypothesis: Hypothesis being tested

        Returns:
            List of control group specifications
        """
        # Default: single baseline control group
        return [
            ControlGroup(
                name="baseline_control",
                description="Baseline control group for comparison",
                variables={},
                rationale="Standard baseline comparison to test hypothesis",
            )
        ]

    def get_applicability_score(self, hypothesis: Hypothesis) -> float:
        """
        Score how well this template applies to the hypothesis.

        Args:
            hypothesis: Hypothesis to score

        Returns:
            Score from 0.0 (not applicable) to 1.0 (perfect match)
        """
        if not self.is_applicable(hypothesis):
            return 0.0

        # Check if experiment type matches suggested types
        if self.metadata.experiment_type in hypothesis.suggested_experiment_types:
            return 0.9

        # Check domain match
        if self.metadata.domain and self.metadata.domain.lower() == hypothesis.domain.lower():
            return 0.7

        return 0.5  # Applicable but not ideal match

    def __str__(self) -> str:
        """String representation of template."""
        return f"<{self.__class__.__name__}: {self.metadata.name} ({self.metadata.experiment_type.value})>"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"{self.__class__.__name__}(name='{self.metadata.name}', "
            f"type={self.metadata.experiment_type.value}, "
            f"version={self.metadata.version})"
        )


class TemplateRegistry:
    """
    Registry for discovering and managing experiment templates.

    Provides central location for template registration and lookup.

    Example:
        ```python
        # Register templates
        registry = TemplateRegistry()
        registry.register(TTestTemplate())
        registry.register(CorrelationTemplate())

        # Find best template for hypothesis
        template = registry.find_best_template(hypothesis)

        # Get all templates of a type
        data_templates = registry.get_templates_by_type(ExperimentType.DATA_ANALYSIS)
        ```
    """

    def __init__(self):
        """Initialize empty template registry."""
        self._templates: Dict[str, TemplateBase] = {}
        self._templates_by_type: Dict[ExperimentType, List[str]] = {
            ExperimentType.COMPUTATIONAL: [],
            ExperimentType.DATA_ANALYSIS: [],
            ExperimentType.LITERATURE_SYNTHESIS: [],
        }
        self._templates_by_domain: Dict[str, List[str]] = {}

    def register(self, template: TemplateBase) -> None:
        """
        Register a template in the registry.

        Args:
            template: Template to register

        Raises:
            ValueError: If template name already registered or template invalid
        """
        # Validate template
        validation = template.validate_template()
        if not validation.is_valid:
            raise ValueError(f"Invalid template: {', '.join(validation.errors)}")

        # Check for duplicate name
        if template.metadata.name in self._templates:
            raise ValueError(f"Template '{template.metadata.name}' already registered")

        # Register template
        self._templates[template.metadata.name] = template

        # Add to type index
        self._templates_by_type[template.metadata.experiment_type].append(template.metadata.name)

        # Add to domain index
        if template.metadata.domain:
            domain = template.metadata.domain.lower()
            if domain not in self._templates_by_domain:
                self._templates_by_domain[domain] = []
            self._templates_by_domain[domain].append(template.metadata.name)

    def unregister(self, template_name: str) -> None:
        """
        Remove a template from the registry.

        Args:
            template_name: Name of template to remove
        """
        if template_name not in self._templates:
            return

        template = self._templates[template_name]

        # Remove from type index
        self._templates_by_type[template.metadata.experiment_type].remove(template_name)

        # Remove from domain index
        if template.metadata.domain:
            domain = template.metadata.domain.lower()
            if domain in self._templates_by_domain:
                self._templates_by_domain[domain].remove(template_name)

        # Remove from main registry
        del self._templates[template_name]

    def get_template(self, name: str) -> Optional[TemplateBase]:
        """
        Get a template by name.

        Args:
            name: Template name

        Returns:
            Template or None if not found
        """
        return self._templates.get(name)

    def get_templates_by_type(
        self,
        experiment_type: ExperimentType
    ) -> List[TemplateBase]:
        """
        Get all templates for an experiment type.

        Args:
            experiment_type: Type of experiment

        Returns:
            List of matching templates
        """
        names = self._templates_by_type.get(experiment_type, [])
        return [self._templates[name] for name in names]

    def get_templates_by_domain(self, domain: str) -> List[TemplateBase]:
        """
        Get all templates for a domain.

        Args:
            domain: Scientific domain

        Returns:
            List of matching templates
        """
        names = self._templates_by_domain.get(domain.lower(), [])
        return [self._templates[name] for name in names]

    def find_applicable_templates(
        self,
        hypothesis: Hypothesis,
        experiment_type: Optional[ExperimentType] = None
    ) -> List[TemplateBase]:
        """
        Find all templates applicable to a hypothesis.

        Args:
            hypothesis: Hypothesis to find templates for
            experiment_type: Optionally filter by experiment type

        Returns:
            List of applicable templates sorted by applicability score
        """
        # Get candidate templates
        if experiment_type:
            candidates = self.get_templates_by_type(experiment_type)
        else:
            candidates = list(self._templates.values())

        # Filter to applicable and score
        applicable = []
        for template in candidates:
            if template.is_applicable(hypothesis):
                score = template.get_applicability_score(hypothesis)
                applicable.append((score, template))

        # Sort by score (descending)
        applicable.sort(key=lambda x: x[0], reverse=True)

        return [template for score, template in applicable]

    def find_best_template(
        self,
        hypothesis: Hypothesis,
        experiment_type: Optional[ExperimentType] = None
    ) -> Optional[TemplateBase]:
        """
        Find the best template for a hypothesis.

        Args:
            hypothesis: Hypothesis to find template for
            experiment_type: Optionally filter by experiment type

        Returns:
            Best matching template or None if none applicable
        """
        applicable = self.find_applicable_templates(hypothesis, experiment_type)
        return applicable[0] if applicable else None

    def list_all_templates(self) -> List[TemplateMetadata]:
        """
        Get metadata for all registered templates.

        Returns:
            List of template metadata objects
        """
        return [template.metadata for template in self._templates.values()]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            Dictionary with registry stats
        """
        return {
            "total_templates": len(self._templates),
            "by_type": {
                exp_type.value: len(names)
                for exp_type, names in self._templates_by_type.items()
            },
            "by_domain": {
                domain: len(names)
                for domain, names in self._templates_by_domain.items()
            },
            "domains_covered": list(self._templates_by_domain.keys()),
        }

    def __len__(self) -> int:
        """Number of registered templates."""
        return len(self._templates)

    def __contains__(self, template_name: str) -> bool:
        """Check if template is registered."""
        return template_name in self._templates

    def __iter__(self):
        """Iterate over all templates."""
        return iter(self._templates.values())


# Global template registry instance
_global_registry: Optional[TemplateRegistry] = None


def get_template_registry() -> TemplateRegistry:
    """
    Get the global template registry.

    Returns:
        Global TemplateRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = TemplateRegistry()
    return _global_registry


def register_template(template: TemplateBase) -> None:
    """
    Register a template in the global registry.

    Args:
        template: Template to register
    """
    registry = get_template_registry()
    registry.register(template)
