"""
Data analysis experiment templates.

Provides templates for statistical analysis experiments based on
kosmos-figures patterns.
"""

from typing import List, Dict, Any, Optional
import re

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


class TTestComparisonTemplate(TemplateBase):
    """
    Template for two-group comparison using t-test.

    Based on kosmos-figures Figure 2 pattern: comparing means between two groups.

    Applicable when hypothesis involves:
    - Comparing two groups
    - Mean/average comparisons
    - "Greater than", "less than", "different from" language
    """

    def __init__(self):
        super().__init__(
            name="t_test_comparison",
            experiment_type=ExperimentType.DATA_ANALYSIS,
            title="T-Test Comparison Template",
            description="Compare means between two groups using independent samples t-test. Based on proven statistical patterns.",
            version="1.0.0"
        )
        self.metadata.suitable_for = [
            "Two-group comparisons",
            "Mean difference testing",
            "Before/after comparisons",
            "Treatment vs control"
        ]
        self.metadata.rigor_score = 0.85

    def is_applicable(self, hypothesis: Hypothesis) -> bool:
        """Check if hypothesis is suitable for t-test."""
        statement = hypothesis.statement.lower()

        # Look for comparison keywords
        comparison_keywords = [
            "greater than", "less than", "higher than", "lower than",
            "more than", "fewer than", "different from",
            "compare", "versus", "vs", "between"
        ]

        # Look for two-group indicators
        two_group_indicators = [
            "two groups", "two conditions", "experimental and control",
            "treatment and control", "before and after"
        ]

        has_comparison = any(keyword in statement for keyword in comparison_keywords)
        suggests_two_groups = any(indicator in statement for indicator in two_group_indicators)

        # Also check if experiment type matches
        type_matches = ExperimentType.DATA_ANALYSIS in hypothesis.suggested_experiment_types

        return (has_comparison or suggests_two_groups) and type_matches

    def generate_protocol(
        self,
        params: TemplateCustomizationParams
    ) -> ExperimentProtocol:
        """Generate t-test comparison protocol."""
        hypothesis = params.hypothesis

        # Extract variable names from hypothesis (simplified)
        statement = hypothesis.statement
        outcome_var = "outcome_variable"
        group_var = "group"

        # Define steps
        steps = [
            ProtocolStep(
                step_number=1,
                title="Data Loading and Validation",
                description="Load dataset and validate data quality",
                action="Load data from specified source, check for missing values, verify data types",
                expected_duration_minutes=15,
                expected_output="Validated dataset with N samples",
                validation_check="No missing values in key variables, N >= 20 per group",
                library_imports=["pandas", "numpy"]
            ),
            ProtocolStep(
                step_number=2,
                title="Exploratory Data Analysis",
                description="Examine data distributions and check assumptions",
                action="Generate descriptive statistics, create histograms/boxplots, test normality (Shapiro-Wilk), check variance homogeneity (Levene's test)",
                expected_duration_minutes=20,
                requires_steps=[1],
                expected_output="Descriptive stats table, distribution plots, assumption test results",
                validation_check="Review assumption tests (normality, equal variances)",
                library_imports=["pandas", "matplotlib", "seaborn", "scipy"]
            ),
            ProtocolStep(
                step_number=3,
                title="Statistical Test Execution",
                description="Perform independent samples t-test",
                action="Run scipy.stats.ttest_ind() or ttest_welch if variances unequal, calculate effect size (Cohen's d), compute confidence intervals",
                expected_duration_minutes=10,
                requires_steps=[2],
                expected_output="t-statistic, p-value, effect size, 95% CI for difference",
                validation_check="All statistics calculated, degrees of freedom correct",
                library_imports=["scipy", "numpy"]
            ),
            ProtocolStep(
                step_number=4,
                title="Results Visualization",
                description="Create publication-quality plots",
                action="Generate bar plot with error bars (mean ± SEM), add significance indicators, create violin plots showing distributions",
                expected_duration_minutes=15,
                requires_steps=[3],
                expected_output="Figure with group comparison (bar plot + error bars + p-value)",
                validation_check="Plot shows means, error bars, sample sizes, significance level",
                library_imports=["matplotlib", "seaborn"]
            ),
            ProtocolStep(
                step_number=5,
                title="Interpretation and Reporting",
                description="Interpret results in context of hypothesis",
                action="Compare p-value to alpha (0.05), assess effect size magnitude (small/medium/large), report conclusion with confidence intervals",
                expected_duration_minutes=10,
                requires_steps=[4],
                expected_output="Statistical summary report with interpretation",
                validation_check="Conclusion directly addresses hypothesis, includes effect size and CI",
                library_imports=[]
            ),
        ]

        # Define variables
        variables = {
            group_var: Variable(
                name=group_var,
                type=VariableType.INDEPENDENT,
                description="Group assignment (experimental vs control)",
                values=["experimental", "control"],
                unit="category"
            ),
            outcome_var: Variable(
                name=outcome_var,
                type=VariableType.DEPENDENT,
                description="Measured outcome variable",
                unit="TBD",
                measurement_method="Continuous measurement"
            ),
        }

        # Control group
        control_groups = [
            ControlGroup(
                name="control_group",
                description="Baseline/control condition for comparison",
                variables={group_var: "control"},
                rationale="Required for hypothesis testing - provides baseline to compare experimental condition against",
                sample_size=30
            )
        ]

        # Statistical test
        statistical_tests = [
            StatisticalTestSpec(
                test_type=StatisticalTest.T_TEST,
                description=f"Compare mean {outcome_var} between experimental and control groups",
                null_hypothesis="H0: No difference in mean outcome between groups",
                alternative="two-sided",
                alpha=0.05,
                variables=[outcome_var],
                groups=["experimental", "control"],
                required_power=0.8,
                expected_effect_size=0.5  # Medium effect
            )
        ]

        # Resource requirements
        resources = self.estimate_resources(params)

        # Create protocol
        protocol = ExperimentProtocol(
            name=f"T-Test Comparison: {hypothesis.statement[:60]}",
            hypothesis_id=hypothesis.id or "",
            experiment_type=ExperimentType.DATA_ANALYSIS,
            domain=hypothesis.domain,
            description=f"Statistical comparison of two groups using independent samples t-test to test the hypothesis: {hypothesis.statement}. This experiment will compare means between experimental and control groups, assess statistical significance, and calculate effect sizes.",
            objective="Determine if there is a statistically significant difference between two group means",
            steps=steps,
            variables=variables,
            control_groups=control_groups,
            statistical_tests=statistical_tests,
            sample_size=60,  # 30 per group
            sample_size_rationale="Power analysis: 30 per group provides 80% power to detect medium effect (d=0.5) at alpha=0.05",
            power_analysis_performed=True,
            resource_requirements=resources,
            validation_checks=[],
            random_seed=42,
            reproducibility_notes="Record software versions (scipy, numpy), use same random seed, document data preprocessing steps",
        )

        return protocol


class CorrelationAnalysisTemplate(TemplateBase):
    """
    Template for correlation analysis.

    Based on kosmos-figures Figure 3 pattern: examining relationships between variables.

    Applicable when hypothesis involves:
    - Relationships between variables
    - "Correlated with", "associated with", "related to"
    - Continuous variables
    """

    def __init__(self):
        super().__init__(
            name="correlation_analysis",
            experiment_type=ExperimentType.DATA_ANALYSIS,
            title="Correlation Analysis Template",
            description="Analyze relationship strength between two continuous variables using Pearson or Spearman correlation.",
            version="1.0.0"
        )
        self.metadata.suitable_for = [
            "Relationship testing",
            "Continuous variable associations",
            "Predictive relationships"
        ]
        self.metadata.rigor_score = 0.80

    def is_applicable(self, hypothesis: Hypothesis) -> bool:
        """Check if hypothesis is suitable for correlation analysis."""
        statement = hypothesis.statement.lower()

        correlation_keywords = [
            "correlat", "associat", "relationship", "related",
            "linked to", "connected", "correspond"
        ]

        has_correlation = any(keyword in statement for keyword in correlation_keywords)
        type_matches = ExperimentType.DATA_ANALYSIS in hypothesis.suggested_experiment_types

        return has_correlation and type_matches

    def generate_protocol(
        self,
        params: TemplateCustomizationParams
    ) -> ExperimentProtocol:
        """Generate correlation analysis protocol."""
        hypothesis = params.hypothesis

        steps = [
            ProtocolStep(
                step_number=1,
                title="Data Loading and Preparation",
                description="Load data and prepare variables for correlation analysis",
                action="Load dataset, extract variables of interest, handle missing data, check data types",
                expected_duration_minutes=20,
                expected_output="Clean dataset with variables ready for analysis",
                validation_check="No missing values, both variables continuous, N >= 30",
                library_imports=["pandas", "numpy"]
            ),
            ProtocolStep(
                step_number=2,
                title="Assumption Checking",
                description="Test assumptions for parametric correlation",
                action="Check normality (Shapiro-Wilk), create Q-Q plots, check for outliers (z-score > 3), assess linearity (scatterplot)",
                expected_duration_minutes=25,
                requires_steps=[1],
                expected_output="Assumption test results, scatterplot with fitted line",
                validation_check="Determine if Pearson (parametric) or Spearman (non-parametric) appropriate",
                library_imports=["scipy", "matplotlib", "seaborn"]
            ),
            ProtocolStep(
                step_number=3,
                title="Correlation Calculation",
                description="Calculate correlation coefficient and significance",
                action="Compute Pearson or Spearman correlation, calculate p-value, compute confidence interval for r, calculate R²",
                expected_duration_minutes=10,
                requires_steps=[2],
                expected_output="Correlation coefficient (r), p-value, 95% CI, R²",
                validation_check="All statistics calculated, interpretation note added",
                library_imports=["scipy", "numpy"]
            ),
            ProtocolStep(
                step_number=4,
                title="Visualization",
                description="Create scatter plot with regression line",
                action="Generate scatterplot, add regression line with 95% CI band, annotate with r and p-value, add Spearman if non-linear",
                expected_duration_minutes=20,
                requires_steps=[3],
                expected_output="Publication-quality scatterplot with statistics",
                validation_check="Plot shows data points, trend line, CI band, r and p annotated",
                library_imports=["matplotlib", "seaborn"]
            ),
            ProtocolStep(
                step_number=5,
                title="Interpretation",
                description="Interpret correlation strength and significance",
                action="Assess effect size (|r| < 0.3 weak, 0.3-0.7 moderate, > 0.7 strong), compare p to alpha, note correlation ≠ causation",
                expected_duration_minutes=15,
                requires_steps=[4],
                expected_output="Interpretation report with caveats",
                validation_check="Conclusion addresses hypothesis, acknowledges limitations",
                library_imports=[]
            ),
        ]

        variables = {
            "variable_x": Variable(
                name="variable_x",
                type=VariableType.INDEPENDENT,
                description="First continuous variable",
                unit="TBD",
                measurement_method="Continuous measurement"
            ),
            "variable_y": Variable(
                name="variable_y",
                type=VariableType.DEPENDENT,
                description="Second continuous variable",
                unit="TBD",
                measurement_method="Continuous measurement"
            ),
        }

        statistical_tests = [
            StatisticalTestSpec(
                test_type=StatisticalTest.CORRELATION,
                description="Test correlation between variable_x and variable_y",
                null_hypothesis="H0: No correlation (r = 0)",
                alternative="two-sided",
                alpha=0.05,
                variables=["variable_x", "variable_y"],
                required_power=0.8,
                expected_effect_size=0.3  # Moderate correlation
            )
        ]

        resources = self.estimate_resources(params)

        protocol = ExperimentProtocol(
            name=f"Correlation Analysis: {hypothesis.statement[:60]}",
            hypothesis_id=hypothesis.id or "",
            experiment_type=ExperimentType.DATA_ANALYSIS,
            domain=hypothesis.domain,
            description=f"Correlation analysis to test the hypothesis: {hypothesis.statement}. This experiment will measure the strength and significance of the relationship between two continuous variables.",
            objective="Quantify the strength and direction of relationship between two variables",
            steps=steps,
            variables=variables,
            control_groups=[],  # No control groups for correlation
            statistical_tests=statistical_tests,
            sample_size=85,  # For r=0.3, power=0.8, alpha=0.05
            sample_size_rationale="Power analysis: N=85 provides 80% power to detect moderate correlation (r=0.3) at alpha=0.05",
            power_analysis_performed=True,
            resource_requirements=resources,
            validation_checks=[],
            random_seed=42,
            reproducibility_notes="Document scipy version, record data preprocessing, save raw and processed data",
        )

        return protocol


class RegressionAnalysisTemplate(TemplateBase):
    """
    Template for regression analysis.

    Applicable when hypothesis involves:
    - Predicting outcomes
    - "Predicts", "explains variance", "accounts for"
    - Multiple predictors
    """

    def __init__(self):
        super().__init__(
            name="regression_analysis",
            experiment_type=ExperimentType.DATA_ANALYSIS,
            title="Regression Analysis Template",
            description="Predict outcome variable from one or more predictors using linear regression.",
            version="1.0.0"
        )
        self.metadata.suitable_for = [
            "Prediction tasks",
            "Multiple predictor analysis",
            "Variance explained",
            "Causal modeling"
        ]
        self.metadata.rigor_score = 0.82

    def is_applicable(self, hypothesis: Hypothesis) -> bool:
        """Check if hypothesis is suitable for regression."""
        statement = hypothesis.statement.lower()

        regression_keywords = [
            "predict", "explain", "account for", "variance",
            "influence", "effect of", "impact of"
        ]

        has_regression = any(keyword in statement for keyword in regression_keywords)
        type_matches = ExperimentType.DATA_ANALYSIS in hypothesis.suggested_experiment_types

        return has_regression and type_matches

    def generate_protocol(
        self,
        params: TemplateCustomizationParams
    ) -> ExperimentProtocol:
        """Generate regression analysis protocol."""
        hypothesis = params.hypothesis

        steps = [
            ProtocolStep(
                step_number=1,
                title="Data Preparation",
                description="Prepare data for regression analysis",
                action="Load data, identify predictors and outcome, handle missing data (listwise deletion or imputation), check for multicollinearity (VIF)",
                expected_duration_minutes=30,
                expected_output="Clean dataset with predictors and outcome ready",
                validation_check="No missing data, VIF < 10 for all predictors, N >= 10*p (p=number of predictors)",
                library_imports=["pandas", "numpy", "statsmodels"]
            ),
            ProtocolStep(
                step_number=2,
                title="Assumption Testing",
                description="Test regression assumptions",
                action="Test linearity (scatterplots), normality of residuals (Q-Q plot, Shapiro-Wilk), homoscedasticity (residual plot), independence (Durbin-Watson)",
                expected_duration_minutes=30,
                requires_steps=[1],
                expected_output="Assumption diagnostic plots and tests",
                validation_check="All major assumptions met or violations noted",
                library_imports=["matplotlib", "seaborn", "scipy", "statsmodels"]
            ),
            ProtocolStep(
                step_number=3,
                title="Model Fitting",
                description="Fit regression model and assess fit",
                action="Fit OLS model using statsmodels, extract coefficients and p-values, calculate R², adjusted R², AIC/BIC",
                expected_duration_minutes=15,
                requires_steps=[2],
                expected_output="Fitted model with coefficients, standard errors, p-values, R²",
                validation_check="Model converged, all statistics calculated",
                library_imports=["statsmodels"]
            ),
            ProtocolStep(
                step_number=4,
                title="Model Diagnostics",
                description="Check for influential cases and outliers",
                action="Calculate Cook's distance, leverage, DFFITS, create influence plots",
                expected_duration_minutes=20,
                requires_steps=[3],
                expected_output="Diagnostic plots, list of influential cases",
                validation_check="Influential cases identified and evaluated",
                library_imports=["statsmodels", "matplotlib"]
            ),
            ProtocolStep(
                step_number=5,
                title="Results Interpretation",
                description="Interpret model results in context",
                action="Interpret coefficients (standardized beta for effect sizes), assess model fit (R²), determine which predictors significant, compare to hypothesis",
                expected_duration_minutes=20,
                requires_steps=[4],
                expected_output="Comprehensive results summary with interpretation",
                validation_check="All coefficients interpreted, hypothesis addressed",
                library_imports=[]
            ),
        ]

        variables = {
            "outcome": Variable(
                name="outcome",
                type=VariableType.DEPENDENT,
                description="Outcome variable to predict",
                unit="TBD",
                measurement_method="Continuous measurement"
            ),
            "predictor_1": Variable(
                name="predictor_1",
                type=VariableType.INDEPENDENT,
                description="Primary predictor variable",
                unit="TBD"
            ),
        }

        statistical_tests = [
            StatisticalTestSpec(
                test_type=StatisticalTest.REGRESSION,
                description="Multiple regression predicting outcome from predictors",
                null_hypothesis="H0: All regression coefficients = 0 (R² = 0)",
                alternative="two-sided",
                alpha=0.05,
                variables=["outcome", "predictor_1"],
                required_power=0.8,
                expected_effect_size=0.15  # Medium f²
            )
        ]

        resources = self.estimate_resources(params)
        resources.compute_hours = 2.0  # Regression is slightly more intensive

        protocol = ExperimentProtocol(
            name=f"Regression Analysis: {hypothesis.statement[:60]}",
            hypothesis_id=hypothesis.id or "",
            experiment_type=ExperimentType.DATA_ANALYSIS,
            domain=hypothesis.domain,
            description=f"Linear regression analysis to test the hypothesis: {hypothesis.statement}. This experiment will model the relationship between predictor variables and an outcome, testing the significance of predictors and assessing model fit.",
            objective="Model predictive relationship and test significance of predictors",
            steps=steps,
            variables=variables,
            control_groups=[],
            statistical_tests=statistical_tests,
            sample_size=107,  # For f²=0.15 (medium), p=2 predictors, power=0.8, alpha=0.05
            sample_size_rationale="Power analysis: N=107 provides 80% power to detect medium effect (f²=0.15) with 2 predictors at alpha=0.05",
            power_analysis_performed=True,
            resource_requirements=resources,
            validation_checks=[],
            random_seed=42,
            reproducibility_notes="Record statsmodels version, save model object, document any data transformations applied",
        )

        return protocol


# Register all data analysis templates
def register_all_data_analysis_templates():
    """Register all data analysis templates in the global registry."""
    register_template(TTestComparisonTemplate())
    register_template(CorrelationAnalysisTemplate())
    register_template(RegressionAnalysisTemplate())


# Auto-register on import
register_all_data_analysis_templates()
