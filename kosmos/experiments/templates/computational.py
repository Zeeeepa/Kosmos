"""
Computational experiment templates.

Provides templates for computational simulations and algorithmic experiments.
"""

from kosmos.models.hypothesis import Hypothesis, ExperimentType
from kosmos.models.experiment import (
    ExperimentProtocol,
    ProtocolStep,
    Variable,
    VariableType,
    ControlGroup,
    ResourceRequirements,
    StatisticalTestSpec,
    StatisticalTest,
)
from kosmos.experiments.templates.base import (
    TemplateBase,
    TemplateCustomizationParams,
    register_template,
)


class AlgorithmComparisonTemplate(TemplateBase):
    """Template for comparing algorithm performance."""

    def __init__(self):
        super().__init__(
            name="algorithm_comparison",
            experiment_type=ExperimentType.COMPUTATIONAL,
            title="Algorithm Comparison Template",
            description="Compare performance of different algorithms on benchmark tasks.",
            version="1.0.0"
        )
        self.metadata.suitable_for = ["Algorithm evaluation", "Performance benchmarking", "Runtime analysis"]
        self.metadata.rigor_score = 0.80

    def is_applicable(self, hypothesis: Hypothesis) -> bool:
        """Check if hypothesis involves algorithm comparison."""
        statement = hypothesis.statement.lower()
        keywords = ["algorithm", "faster", "slower", "efficient", "performance", "runtime", "complexity"]
        return any(kw in statement for kw in keywords) and ExperimentType.COMPUTATIONAL in hypothesis.suggested_experiment_types

    def generate_protocol(self, params: TemplateCustomizationParams) -> ExperimentProtocol:
        """Generate algorithm comparison protocol."""
        hypothesis = params.hypothesis

        steps = [
            ProtocolStep(step_number=1, title="Algorithm Implementation", description="Implement or import algorithms to compare", action="Implement both algorithms with same interface, ensure correctness with unit tests", expected_duration_minutes=120, library_imports=["numpy"]),
            ProtocolStep(step_number=2, title="Benchmark Setup", description="Create benchmark datasets of varying sizes", action="Generate test datasets with N=[100, 1000, 10000, 100000] samples, ensure reproducibility with fixed seed", expected_duration_minutes=30, requires_steps=[1], library_imports=["numpy"]),
            ProtocolStep(step_number=3, title="Performance Measurement", description="Run algorithms and measure runtime", action="For each dataset size: run each algorithm 30 times, measure wall-clock time with time.perf_counter(), record memory usage", expected_duration_minutes=180, requires_steps=[2], library_imports=["time", "tracemalloc"]),
            ProtocolStep(step_number=4, title="Statistical Analysis", description="Compare runtime distributions", action="For each dataset size: run t-test comparing mean runtimes, calculate effect sizes, fit complexity curves (O(n), O(n log n), O(n²))", expected_duration_minutes=45, requires_steps=[3], library_imports=["scipy", "numpy"]),
            ProtocolStep(step_number=5, title="Visualization", description="Create performance comparison plots", action="Plot runtime vs dataset size for both algorithms, add complexity curve fits, create box plots for each size", expected_duration_minutes=30, requires_steps=[4], library_imports=["matplotlib"]),
        ]

        variables = {
            "algorithm": Variable(name="algorithm", type=VariableType.INDEPENDENT, description="Algorithm being tested", values=["algorithm_A", "algorithm_B"], unit="category"),
            "dataset_size": Variable(name="dataset_size", type=VariableType.INDEPENDENT, description="Size of input dataset", values=[100, 1000, 10000, 100000], unit="count"),
            "runtime_seconds": Variable(name="runtime_seconds", type=VariableType.DEPENDENT, description="Algorithm execution time", unit="seconds", measurement_method="time.perf_counter()"),
            "memory_mb": Variable(name="memory_mb", type=VariableType.DEPENDENT, description="Peak memory usage", unit="megabytes", measurement_method="tracemalloc"),
        }

        control_groups = [
            ControlGroup(name="baseline_algorithm", description="Baseline algorithm for comparison", variables={"algorithm": "algorithm_A"}, rationale="Established baseline algorithm", sample_size=30)
        ]

        statistical_tests = [
            StatisticalTestSpec(test_type=StatisticalTest.T_TEST, description="Compare mean runtime at each dataset size", null_hypothesis="H0: No difference in mean runtime", alternative="two-sided", alpha=0.05, variables=["runtime_seconds"], groups=["algorithm_A", "algorithm_B"], required_power=0.8, expected_effect_size=0.5)
        ]

        resources = ResourceRequirements(compute_hours=5.0, memory_gb=8, gpu_required=False, estimated_cost_usd=5.0, estimated_duration_days=0.5, required_libraries=["numpy", "scipy", "matplotlib"], python_version="3.9+", can_parallelize=True, parallelization_factor=4)

        return ExperimentProtocol(
            name=f"Algorithm Comparison: {hypothesis.statement[:60]}",
            hypothesis_id=hypothesis.id or "",
            experiment_type=ExperimentType.COMPUTATIONAL,
            domain=hypothesis.domain,
            description=f"Computational experiment comparing algorithm performance to test: {hypothesis.statement}",
            objective="Compare runtime and memory efficiency of algorithms across dataset sizes",
            steps=steps,
            variables=variables,
            control_groups=control_groups,
            statistical_tests=statistical_tests,
            sample_size=120,  # 30 runs * 4 dataset sizes
            sample_size_rationale="30 replications per condition for robust mean estimation and statistical power",
            power_analysis_performed=True,
            resource_requirements=resources,
            validation_checks=[],
            random_seed=42,
            reproducibility_notes="Fix random seed, record Python and library versions, use same hardware for all runs",
        )


class SimulationExperimentTemplate(TemplateBase):
    """Template for simulation-based experiments."""

    def __init__(self):
        super().__init__(
            name="simulation_experiment",
            experiment_type=ExperimentType.COMPUTATIONAL,
            title="Simulation Experiment Template",
            description="Test hypotheses using computational simulations.",
            version="1.0.0"
        )
        self.metadata.suitable_for = ["Monte Carlo simulations", "Agent-based models", "Physical simulations", "Stochastic processes"]
        self.metadata.rigor_score = 0.78

    def is_applicable(self, hypothesis: Hypothesis) -> bool:
        """Check if hypothesis involves simulation."""
        statement = hypothesis.statement.lower()
        keywords = ["simulat", "model", "predict", "agent", "monte carlo", "stochastic"]
        return any(kw in statement for kw in keywords) and ExperimentType.COMPUTATIONAL in hypothesis.suggested_experiment_types

    def generate_protocol(self, params: TemplateCustomizationParams) -> ExperimentProtocol:
        """Generate simulation protocol."""
        hypothesis = params.hypothesis

        steps = [
            ProtocolStep(step_number=1, title="Simulation Setup", description="Implement simulation model", action="Code simulation with configurable parameters, validate against simple test cases", expected_duration_minutes=180, library_imports=["numpy", "scipy"]),
            ProtocolStep(step_number=2, title="Parameter Configuration", description="Set up experimental conditions", action="Define parameter ranges, create experimental design (factorial or Latin hypercube sampling)", expected_duration_minutes=60, requires_steps=[1], library_imports=["numpy"]),
            ProtocolStep(step_number=3, title="Simulation Execution", description="Run simulations for all conditions", action="For each parameter combination: run N=1000 simulations, record outcomes, save intermediate results", expected_duration_minutes=300, requires_steps=[2], library_imports=["numpy", "multiprocessing"]),
            ProtocolStep(step_number=4, title="Statistical Analysis", description="Analyze simulation results", action="Aggregate results across replications, compute mean and CI for each condition, run ANOVA or regression on outcomes", expected_duration_minutes=45, requires_steps=[3], library_imports=["scipy", "statsmodels"]),
            ProtocolStep(step_number=5, title="Visualization", description="Create results visualizations", action="Plot outcome distributions, create heatmaps for parameter effects, visualize convergence", expected_duration_minutes=40, requires_steps=[4], library_imports=["matplotlib", "seaborn"]),
        ]

        variables = {
            "parameter": Variable(name="parameter", type=VariableType.INDEPENDENT, description="Simulation parameter to vary", unit="TBD"),
            "outcome": Variable(name="outcome", type=VariableType.DEPENDENT, description="Simulation outcome measure", unit="TBD", measurement_method="Aggregate over simulation runs"),
        }

        statistical_tests = [
            StatisticalTestSpec(test_type=StatisticalTest.ANOVA, description="Test effect of parameters on outcome", null_hypothesis="H0: No effect of parameters", alternative="two-sided", alpha=0.05, variables=["outcome"], required_power=0.8, expected_effect_size=0.25)
        ]

        resources = ResourceRequirements(compute_hours=12.0, memory_gb=16, gpu_required=False, estimated_cost_usd=15.0, estimated_duration_days=1.0, required_libraries=["numpy", "scipy", "statsmodels", "matplotlib"], python_version="3.9+", can_parallelize=True, parallelization_factor=8)

        return ExperimentProtocol(
            name=f"Simulation Experiment: {hypothesis.statement[:60]}",
            hypothesis_id=hypothesis.id or "",
            experiment_type=ExperimentType.COMPUTATIONAL,
            domain=hypothesis.domain,
            description=f"Computational simulation experiment to test: {hypothesis.statement}",
            objective="Use simulation to test hypothesis under controlled conditions",
            steps=steps,
            variables=variables,
            control_groups=[],
            statistical_tests=statistical_tests,
            sample_size=1000,  # Simulation runs
            sample_size_rationale="1000 replications to achieve stable mean estimates and narrow confidence intervals",
            power_analysis_performed=True,
            resource_requirements=resources,
            validation_checks=[],
            random_seed=42,
            reproducibility_notes="Fix all random seeds, document simulation parameters, save complete parameter configuration",
        )


# Register templates
def register_all_computational_templates():
    """Register all computational templates."""
    register_template(AlgorithmComparisonTemplate())
    register_template(SimulationExperimentTemplate())


register_all_computational_templates()
