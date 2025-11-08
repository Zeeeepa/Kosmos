"""
Literature synthesis experiment templates.

Provides templates for systematic reviews and meta-analyses.
"""

from kosmos.models.hypothesis import Hypothesis, ExperimentType
from kosmos.models.experiment import (
    ExperimentProtocol,
    ProtocolStep,
    Variable,
    VariableType,
    ResourceRequirements,
    StatisticalTestSpec,
    StatisticalTest,
)
from kosmos.experiments.templates.base import (
    TemplateBase,
    TemplateCustomizationParams,
    register_template,
)


class SystematicReviewTemplate(TemplateBase):
    """Template for systematic literature reviews."""

    def __init__(self):
        super().__init__(
            name="systematic_review",
            experiment_type=ExperimentType.LITERATURE_SYNTHESIS,
            title="Systematic Review Template",
            description="Systematically search, analyze, and synthesize existing literature.",
            version="1.0.0"
        )
        self.metadata.suitable_for = ["Literature gaps", "State of the art", "Consensus assessment"]
        self.metadata.rigor_score = 0.75

    def is_applicable(self, hypothesis: Hypothesis) -> bool:
        """Check if hypothesis requires literature synthesis."""
        statement = hypothesis.statement.lower()
        keywords = ["literature", "review", "studies show", "research indicates", "consensus", "state of the art"]
        return any(kw in statement for kw in keywords) and ExperimentType.LITERATURE_SYNTHESIS in hypothesis.suggested_experiment_types

    def generate_protocol(self, params: TemplateCustomizationParams) -> ExperimentProtocol:
        """Generate systematic review protocol."""
        hypothesis = params.hypothesis

        steps = [
            ProtocolStep(step_number=1, title="Search Strategy Design", description="Define search terms and databases", action="Create Boolean search query, select databases (arXiv, Semantic Scholar, PubMed), define inclusion/exclusion criteria", expected_duration_minutes=120, library_imports=[]),
            ProtocolStep(step_number=2, title="Literature Search", description="Execute systematic search across databases", action="Run searches on all databases, combine results, remove duplicates, apply initial filters", expected_duration_minutes=180, requires_steps=[1], library_imports=["anthropic"]),
            ProtocolStep(step_number=3, title="Screening and Selection", description="Screen papers for relevance", action="Title/abstract screening (first pass), full-text screening (second pass), document reasons for exclusion", expected_duration_minutes=300, requires_steps=[2], library_imports=["anthropic"]),
            ProtocolStep(step_number=4, title="Data Extraction", description="Extract relevant data from selected papers", action="For each paper: extract methodology, findings, limitations, quality assessment (risk of bias), synthesize in structured format", expected_duration_minutes=400, requires_steps=[3], library_imports=["anthropic", "pandas"]),
            ProtocolStep(step_number=5, title="Synthesis and Analysis", description="Synthesize findings across studies", action="Identify common themes, assess consistency of findings, note contradictions, synthesize conclusions", expected_duration_minutes=240, requires_steps=[4], library_imports=["anthropic"]),
            ProtocolStep(step_number=6, title="Report Generation", description="Create comprehensive review report", action="Write structured report: background, methods, results, discussion, gaps identified, conclusions", expected_duration_minutes=180, requires_steps=[5], library_imports=[]),
        ]

        variables = {
            "included_papers": Variable(name="included_papers", type=VariableType.DEPENDENT, description="Number of papers meeting inclusion criteria", unit="count", measurement_method="Count after screening"),
            "evidence_quality": Variable(name="evidence_quality", type=VariableType.DEPENDENT, description="Average quality score of included studies", unit="score_0_10", measurement_method="Risk of bias assessment"),
        }

        statistical_tests = []  # Qualitative synthesis, no statistical tests

        resources = ResourceRequirements(compute_hours=2.0, memory_gb=4, gpu_required=False, estimated_cost_usd=50.0, api_calls_estimated=200, estimated_duration_days=5.0, required_libraries=["anthropic", "pandas"], python_version="3.9+", can_parallelize=False)

        return ExperimentProtocol(
            name=f"Systematic Review: {hypothesis.statement[:60]}",
            hypothesis_id=hypothesis.id or "",
            experiment_type=ExperimentType.LITERATURE_SYNTHESIS,
            domain=hypothesis.domain,
            description=f"Systematic literature review to test: {hypothesis.statement}. This protocol follows PRISMA guidelines for systematic reviews.",
            objective="Systematically identify, analyze, and synthesize existing literature to answer research question",
            steps=steps,
            variables=variables,
            control_groups=[],
            statistical_tests=statistical_tests,
            sample_size=None,  # Depends on search results
            sample_size_rationale="Sample size determined by systematic search results and inclusion criteria",
            power_analysis_performed=False,
            resource_requirements=resources,
            validation_checks=[],
            random_seed=None,
            reproducibility_notes="Document complete search strategy, save all search results, maintain screening log with exclusion reasons, use PRISMA checklist",
        )


class MetaAnalysisTemplate(TemplateBase):
    """Template for meta-analysis of quantitative studies."""

    def __init__(self):
        super().__init__(
            name="meta_analysis",
            experiment_type=ExperimentType.LITERATURE_SYNTHESIS,
            title="Meta-Analysis Template",
            description="Quantitatively combine results from multiple studies.",
            version="1.0.0"
        )
        self.metadata.suitable_for = ["Effect size estimation", "Pooled analysis", "Publication bias"]
        self.metadata.rigor_score = 0.82

    def is_applicable(self, hypothesis: Hypothesis) -> bool:
        """Check if hypothesis requires meta-analysis."""
        statement = hypothesis.statement.lower()
        keywords = ["meta-analysis", "combined effect", "pooled", "across studies", "effect size"]
        return any(kw in statement for kw in keywords) and ExperimentType.LITERATURE_SYNTHESIS in hypothesis.suggested_experiment_types

    def generate_protocol(self, params: TemplateCustomizationParams) -> ExperimentProtocol:
        """Generate meta-analysis protocol."""
        hypothesis = params.hypothesis

        steps = [
            ProtocolStep(step_number=1, title="Literature Search", description="Systematic search for quantitative studies", action="Search databases for studies with numerical results, apply inclusion criteria (must report effect sizes or statistics to calculate them)", expected_duration_minutes=240, library_imports=["anthropic"]),
            ProtocolStep(step_number=2, title="Effect Size Extraction", description="Extract effect sizes from studies", action="For each study: extract effect size (d, r, OR, etc.) or raw statistics, extract sample size, calculate SE, note study quality", expected_duration_minutes=360, requires_steps=[1], library_imports=["pandas", "numpy"]),
            ProtocolStep(step_number=3, title="Heterogeneity Assessment", description="Test for heterogeneity across studies", action="Calculate I² and Q statistics, assess between-study variance (τ²), decide on fixed vs random effects", expected_duration_minutes=45, requires_steps=[2], library_imports=["scipy", "statsmodels"]),
            ProtocolStep(step_number=4, title="Meta-Analysis Computation", description="Compute pooled effect size", action="Run random-effects meta-analysis, calculate pooled effect and CI, create forest plot", expected_duration_minutes=60, requires_steps=[3], library_imports=["scipy", "matplotlib"]),
            ProtocolStep(step_number=5, title="Publication Bias Assessment", description="Check for publication bias", action="Create funnel plot, run Egger's test, conduct trim-and-fill analysis, assess selective reporting", expected_duration_minutes=45, requires_steps=[4], library_imports=["scipy", "matplotlib"]),
            ProtocolStep(step_number=6, title="Sensitivity Analysis", description="Test robustness of findings", action="Leave-one-out analysis, subgroup analyses, meta-regression if enough studies", expected_duration_minutes=90, requires_steps=[5], library_imports=["scipy"]),
        ]

        variables = {
            "effect_size": Variable(name="effect_size", type=VariableType.DEPENDENT, description="Standardized effect size from each study", unit="cohen_d_or_r", measurement_method="Extract from papers or calculate from statistics"),
            "sample_size": Variable(name="sample_size", type=VariableType.INDEPENDENT, description="Sample size of each study", unit="count"),
        }

        statistical_tests = [
            StatisticalTestSpec(test_type=StatisticalTest.CUSTOM, description="Random-effects meta-analysis with DerSimonian-Laird estimator", null_hypothesis="H0: True effect size is zero", alternative="two-sided", alpha=0.05, variables=["effect_size"], required_power=0.8)
        ]

        resources = ResourceRequirements(compute_hours=1.5, memory_gb=4, gpu_required=False, estimated_cost_usd=30.0, api_calls_estimated=100, estimated_duration_days=3.0, required_libraries=["scipy", "statsmodels", "matplotlib", "pandas", "numpy"], python_version="3.9+", can_parallelize=False)

        return ExperimentProtocol(
            name=f"Meta-Analysis: {hypothesis.statement[:60]}",
            hypothesis_id=hypothesis.id or "",
            experiment_type=ExperimentType.LITERATURE_SYNTHESIS,
            domain=hypothesis.domain,
            description=f"Quantitative meta-analysis to test: {hypothesis.statement}. Combines effect sizes from multiple studies to estimate pooled effect and assess heterogeneity.",
            objective="Estimate pooled effect size and assess consistency across studies",
            steps=steps,
            variables=variables,
            control_groups=[],
            statistical_tests=statistical_tests,
            sample_size=None,  # Number of studies varies
            sample_size_rationale="Meta-analysis requires minimum 5-10 studies for meaningful analysis, final N depends on literature search",
            power_analysis_performed=False,
            resource_requirements=resources,
            validation_checks=[],
            random_seed=42,
            reproducibility_notes="Document search strategy completely, save extracted data in CSV, record meta-analysis software/package versions, follow PRISMA guidelines",
        )


# Register templates
def register_all_literature_templates():
    """Register all literature synthesis templates."""
    register_template(SystematicReviewTemplate())
    register_template(MetaAnalysisTemplate())


register_all_literature_templates()
