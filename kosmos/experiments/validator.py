"""
Experiment Protocol Validator.

Validates experimental protocols for scientific rigor and completeness.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

from kosmos.models.experiment import (
    ExperimentProtocol,
    ValidationCheck,
    ValidationReport,
    VariableType,
)
from kosmos.experiments.statistical_power import PowerAnalyzer

logger = logging.getLogger(__name__)


class ExperimentValidator:
    """
    Validates experimental protocols for scientific rigor.

    Checks for:
    - Control groups
    - Adequate sample size
    - Proper variable definitions
    - Statistical power
    - Bias detection
    - Reproducibility

    Example:
        ```python
        validator = ExperimentValidator(
            require_control_group=True,
            min_sample_size=30,
            require_power_analysis=True
        )

        report = validator.validate(protocol)

        if report.validation_passed:
            print("Protocol passes validation!")
        else:
            for error in report.checks_performed:
                if error.status == "failed":
                    print(f"Error: {error.message}")
        ```
    """

    def __init__(
        self,
        require_control_group: bool = True,
        min_sample_size: int = 20,
        require_power_analysis: bool = True,
        min_rigor_score: float = 0.6
    ):
        """
        Initialize validator.

        Args:
            require_control_group: Whether control group is mandatory
            min_sample_size: Minimum acceptable sample size
            require_power_analysis: Whether power analysis is required
            min_rigor_score: Minimum acceptable rigor score
        """
        self.require_control_group = require_control_group
        self.min_sample_size = min_sample_size
        self.require_power_analysis = require_power_analysis
        self.min_rigor_score = min_rigor_score

        self.power_analyzer = PowerAnalyzer()

    def validate(self, protocol: ExperimentProtocol) -> ValidationReport:
        """
        Perform comprehensive validation of experiment protocol.

        Args:
            protocol: Experiment protocol to validate

        Returns:
            ValidationReport with all validation results
        """
        logger.info(f"Validating protocol: {protocol.name}")

        checks = []

        # 1. Control group validation
        checks.append(self._check_control_groups(protocol))

        # 2. Sample size validation
        checks.append(self._check_sample_size(protocol))

        # 3. Power analysis validation
        checks.append(self._check_power_analysis(protocol))

        # 4. Variable definition validation
        checks.extend(self._check_variables(protocol))

        # 5. Statistical test validation
        checks.extend(self._check_statistical_tests(protocol))

        # 6. Bias detection
        checks.extend(self._detect_biases(protocol))

        # 7. Reproducibility validation
        checks.extend(self._check_reproducibility(protocol))

        # 8. Protocol completeness
        checks.extend(self._check_completeness(protocol))

        # Count check results
        checks_passed = sum(1 for c in checks if c.status == "passed")
        checks_failed = sum(1 for c in checks if c.status == "failed")
        checks_warnings = sum(1 for c in checks if c.severity == "warning")

        # Determine overall validation status
        validation_passed = checks_failed == 0

        # Calculate rigor score
        rigor_score = self._calculate_rigor_score(protocol, checks)

        # Calculate reproducibility score
        reproducibility_score = self._calculate_reproducibility_score(protocol, checks)

        # Determine severity level
        if checks_failed > 0:
            if any(c.severity == "error" and c.check_type in ["control_group", "sample_size"] for c in checks):
                severity = "critical"
            else:
                severity = "major"
        elif checks_warnings > 0:
            severity = "minor"
        else:
            severity = "passed"

        # Generate summary and recommendations
        summary = self._generate_summary(protocol, checks, validation_passed, rigor_score)
        recommendations = self._generate_recommendations(protocol, checks)

        # Create report
        report = ValidationReport(
            protocol_id=protocol.id or "unknown",
            rigor_score=rigor_score,
            checks_performed=checks,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            checks_warnings=checks_warnings,
            has_control_group=protocol.has_control_group(),
            control_group_adequate=self._assess_control_group_adequacy(protocol),
            sample_size_adequate=protocol.sample_size is not None and protocol.sample_size >= self.min_sample_size,
            sample_size=protocol.sample_size,
            recommended_sample_size=self._recommend_sample_size(protocol),
            power_analysis_performed=protocol.power_analysis_performed,
            statistical_power=self._estimate_statistical_power(protocol),
            potential_biases=self._list_potential_biases(checks),
            bias_mitigation_suggestions=self._list_bias_mitigations(checks),
            is_reproducible=self._assess_reproducibility(protocol, checks),
            reproducibility_score=reproducibility_score,
            reproducibility_issues=self._list_reproducibility_issues(checks),
            validation_passed=validation_passed,
            severity_level=severity,
            summary=summary,
            recommendations=recommendations,
        )

        logger.info(
            f"Validation complete: {severity} "
            f"(rigor={rigor_score:.2f}, passed={checks_passed}/{len(checks)})"
        )

        return report

    def _check_control_groups(self, protocol: ExperimentProtocol) -> ValidationCheck:
        """Check if protocol has adequate control groups."""
        has_control = protocol.has_control_group()

        if self.require_control_group and not has_control:
            return ValidationCheck(
                check_type="control_group",
                description="Protocol must include at least one control group",
                severity="error",
                status="failed",
                message="No control groups defined - experiment lacks baseline comparison",
                recommendation="Add a control group with baseline/standard conditions for comparison"
            )
        elif not has_control:
            return ValidationCheck(
                check_type="control_group",
                description="Control group presence",
                severity="warning",
                status="passed",
                message="No control group - may limit interpretation",
                recommendation="Consider adding control group for stronger conclusions"
            )
        else:
            return ValidationCheck(
                check_type="control_group",
                description="Control group presence",
                severity="info",
                status="passed",
                message=f"Protocol includes {len(protocol.control_groups)} control group(s)"
            )

    def _check_sample_size(self, protocol: ExperimentProtocol) -> ValidationCheck:
        """Check if sample size is adequate."""
        if protocol.sample_size is None:
            return ValidationCheck(
                check_type="sample_size",
                description="Sample size specification",
                severity="warning",
                status="failed",
                message="Sample size not specified",
                recommendation="Specify sample size based on power analysis"
            )

        if protocol.sample_size < self.min_sample_size:
            return ValidationCheck(
                check_type="sample_size",
                description="Sample size adequacy",
                severity="error",
                status="failed",
                message=f"Sample size ({protocol.sample_size}) below minimum ({self.min_sample_size})",
                recommendation=f"Increase sample size to at least {self.min_sample_size}"
            )

        return ValidationCheck(
            check_type="sample_size",
            description="Sample size adequacy",
            severity="info",
            status="passed",
            message=f"Sample size ({protocol.sample_size}) meets minimum requirement"
        )

    def _check_power_analysis(self, protocol: ExperimentProtocol) -> ValidationCheck:
        """Check if power analysis was performed."""
        if self.require_power_analysis and not protocol.power_analysis_performed:
            return ValidationCheck(
                check_type="power_analysis",
                description="Statistical power analysis",
                severity="warning",
                status="failed",
                message="No power analysis performed",
                recommendation="Conduct power analysis to justify sample size"
            )

        if protocol.power_analysis_performed and protocol.sample_size_rationale:
            return ValidationCheck(
                check_type="power_analysis",
                description="Statistical power analysis",
                severity="info",
                status="passed",
                message="Power analysis performed and documented"
            )

        return ValidationCheck(
            check_type="power_analysis",
            description="Statistical power analysis",
            severity="info",
            status="passed",
            message="Power analysis check skipped"
        )

    def _check_variables(self, protocol: ExperimentProtocol) -> List[ValidationCheck]:
        """Check variable definitions."""
        checks = []

        # Check for independent variables
        independent_vars = protocol.get_independent_variables()
        if not independent_vars:
            checks.append(ValidationCheck(
                check_type="variables",
                description="Independent variables",
                severity="error",
                status="failed",
                message="No independent variables defined",
                recommendation="Define at least one independent (manipulated) variable"
            ))
        else:
            checks.append(ValidationCheck(
                check_type="variables",
                description="Independent variables",
                severity="info",
                status="passed",
                message=f"{len(independent_vars)} independent variable(s) defined"
            ))

        # Check for dependent variables
        dependent_vars = protocol.get_dependent_variables()
        if not dependent_vars:
            checks.append(ValidationCheck(
                check_type="variables",
                description="Dependent variables",
                severity="error",
                status="failed",
                message="No dependent variables defined",
                recommendation="Define at least one dependent (measured outcome) variable"
            ))
        else:
            checks.append(ValidationCheck(
                check_type="variables",
                description="Dependent variables",
                severity="info",
                status="passed",
                message=f"{len(dependent_vars)} dependent variable(s) defined"
            ))

        return checks

    def _check_statistical_tests(self, protocol: ExperimentProtocol) -> List[ValidationCheck]:
        """Check statistical test specifications."""
        checks = []

        if not protocol.statistical_tests:
            checks.append(ValidationCheck(
                check_type="statistical_tests",
                description="Statistical tests",
                severity="warning",
                status="failed",
                message="No statistical tests specified",
                recommendation="Define statistical tests to analyze results"
            ))
        else:
            checks.append(ValidationCheck(
                check_type="statistical_tests",
                description="Statistical tests",
                severity="info",
                status="passed",
                message=f"{len(protocol.statistical_tests)} statistical test(s) defined"
            ))

            # Check if tests have proper parameters
            for test in protocol.statistical_tests:
                if not test.null_hypothesis:
                    checks.append(ValidationCheck(
                        check_type="statistical_tests",
                        description=f"{test.test_type} null hypothesis",
                        severity="warning",
                        status="failed",
                        message=f"Test {test.test_type} missing null hypothesis",
                        recommendation="Define clear null hypothesis for each test"
                    ))

        return checks

    def _detect_biases(self, protocol: ExperimentProtocol) -> List[ValidationCheck]:
        """Detect potential sources of bias."""
        checks = []

        # Selection bias
        if not protocol.random_seed:
            checks.append(ValidationCheck(
                check_type="bias_detection",
                description="Selection bias (random assignment)",
                severity="warning",
                status="failed",
                message="No random seed specified - may introduce selection bias",
                details={"bias_type": "selection"},
                recommendation="Set random seed for random assignment to conditions"
            ))

        # Confounding variables
        confounding_vars = [v for v in protocol.variables.values() if v.type == VariableType.CONFOUNDING]
        if confounding_vars:
            checks.append(ValidationCheck(
                check_type="bias_detection",
                description="Confounding variables identified",
                severity="info",
                status="passed",
                message=f"Protocol acknowledges {len(confounding_vars)} potential confound(s)",
                details={"confounds": [v.name for v in confounding_vars]}
            ))

        return checks

    def _check_reproducibility(self, protocol: ExperimentProtocol) -> List[ValidationCheck]:
        """Check reproducibility features."""
        checks = []

        # Random seed
        if protocol.random_seed is not None:
            checks.append(ValidationCheck(
                check_type="reproducibility",
                description="Random seed",
                severity="info",
                status="passed",
                message=f"Random seed set to {protocol.random_seed}"
            ))
        else:
            checks.append(ValidationCheck(
                check_type="reproducibility",
                description="Random seed",
                severity="warning",
                status="failed",
                message="No random seed - results may not be reproducible",
                recommendation="Set random seed for reproducibility"
            ))

        # Reproducibility notes
        if protocol.reproducibility_notes:
            checks.append(ValidationCheck(
                check_type="reproducibility",
                description="Reproducibility documentation",
                severity="info",
                status="passed",
                message="Reproducibility notes provided"
            ))
        else:
            checks.append(ValidationCheck(
                check_type="reproducibility",
                description="Reproducibility documentation",
                severity="warning",
                status="failed",
                message="No reproducibility notes",
                recommendation="Document steps needed to reproduce results"
            ))

        return checks

    def _check_completeness(self, protocol: ExperimentProtocol) -> List[ValidationCheck]:
        """Check protocol completeness."""
        checks = []

        # Steps
        if len(protocol.steps) < 3:
            checks.append(ValidationCheck(
                check_type="completeness",
                description="Protocol steps",
                severity="warning",
                status="failed",
                message=f"Only {len(protocol.steps)} steps - protocol may be incomplete",
                recommendation="Add more detailed steps for clarity"
            ))

        # Resource estimates
        if not protocol.resource_requirements.estimated_cost_usd:
            checks.append(ValidationCheck(
                check_type="completeness",
                description="Cost estimate",
                severity="info",
                status="failed",
                message="No cost estimate provided",
                recommendation="Estimate experiment cost"
            ))

        if not protocol.resource_requirements.estimated_duration_days:
            checks.append(ValidationCheck(
                check_type="completeness",
                description="Duration estimate",
                severity="info",
                status="failed",
                message="No duration estimate provided",
                recommendation="Estimate experiment duration"
            ))

        return checks

    def _calculate_rigor_score(
        self,
        protocol: ExperimentProtocol,
        checks: List[ValidationCheck]
    ) -> float:
        """Calculate overall scientific rigor score (0.0-1.0)."""
        score = 1.0

        # Penalize errors and warnings
        errors = [c for c in checks if c.severity == "error"]
        warnings = [c for c in checks if c.severity == "warning"]

        score -= len(errors) * 0.15
        score -= len(warnings) * 0.05

        # Bonuses for good practices
        if protocol.has_control_group():
            score += 0.1
        if protocol.power_analysis_performed:
            score += 0.1
        if protocol.random_seed is not None:
            score += 0.05

        return max(0.0, min(1.0, score))

    def _calculate_reproducibility_score(
        self,
        protocol: ExperimentProtocol,
        checks: List[ValidationCheck]
    ) -> float:
        """Calculate reproducibility score (0.0-1.0)."""
        score = 0.0
        total_factors = 5

        if protocol.random_seed is not None:
            score += 1
        if protocol.reproducibility_notes:
            score += 1
        if protocol.resource_requirements.required_libraries:
            score += 1
        if protocol.resource_requirements.python_version:
            score += 1
        if len(protocol.steps) >= 5:  # Detailed steps
            score += 1

        return score / total_factors

    def _assess_control_group_adequacy(self, protocol: ExperimentProtocol) -> bool:
        """Assess if control groups are adequate."""
        if not protocol.control_groups:
            return False

        # Check if control groups have proper definition
        for cg in protocol.control_groups:
            if not cg.rationale or len(cg.rationale) < 20:
                return False

        return True

    def _recommend_sample_size(self, protocol: ExperimentProtocol) -> Optional[int]:
        """Recommend sample size based on power analysis."""
        if not protocol.statistical_tests:
            return None

        # Use first statistical test for recommendation
        test = protocol.statistical_tests[0]
        effect_size = test.expected_effect_size or 0.5  # Default medium effect

        try:
            if test.test_type.value == "t_test":
                return self.power_analyzer.ttest_sample_size(effect_size)
            elif test.test_type.value == "anova":
                num_groups = len(test.groups) if test.groups else 3
                return self.power_analyzer.anova_sample_size(effect_size, num_groups)
            elif test.test_type.value == "correlation":
                return self.power_analyzer.correlation_sample_size(effect_size)
        except Exception as e:
            logger.warning(f"Could not calculate recommended sample size: {e}")

        return None

    def _estimate_statistical_power(self, protocol: ExperimentProtocol) -> Optional[float]:
        """Estimate statistical power if sample size is known."""
        if not protocol.sample_size or not protocol.statistical_tests:
            return None

        test = protocol.statistical_tests[0]
        effect_size = test.expected_effect_size or 0.5

        try:
            if test.test_type.value == "t_test":
                n_per_group = protocol.sample_size // 2
                return self.power_analyzer.ttest_power(effect_size, n_per_group)
        except Exception as e:
            logger.warning(f"Could not estimate statistical power: {e}")

        return None

    def _assess_reproducibility(
        self,
        protocol: ExperimentProtocol,
        checks: List[ValidationCheck]
    ) -> bool:
        """Assess if experiment is reproducible."""
        reproducibility_checks = [c for c in checks if c.check_type == "reproducibility"]
        failed = [c for c in reproducibility_checks if c.status == "failed"]
        return len(failed) == 0

    def _list_potential_biases(self, checks: List[ValidationCheck]) -> List[Dict[str, str]]:
        """Extract potential biases from checks."""
        bias_checks = [c for c in checks if c.check_type == "bias_detection" and c.status == "failed"]
        return [
            {
                "type": c.details.get("bias_type", "unknown") if c.details else "unknown",
                "description": c.message or ""
            }
            for c in bias_checks
        ]

    def _list_bias_mitigations(self, checks: List[ValidationCheck]) -> List[str]:
        """Extract bias mitigation suggestions."""
        bias_checks = [c for c in checks if c.check_type == "bias_detection" and c.recommendation]
        return [c.recommendation for c in bias_checks if c.recommendation]

    def _list_reproducibility_issues(self, checks: List[ValidationCheck]) -> List[str]:
        """Extract reproducibility issues."""
        repro_checks = [c for c in checks if c.check_type == "reproducibility" and c.status == "failed"]
        return [c.message or "" for c in repro_checks]

    def _generate_summary(
        self,
        protocol: ExperimentProtocol,
        checks: List[ValidationCheck],
        passed: bool,
        rigor_score: float
    ) -> str:
        """Generate validation summary."""
        if passed:
            return f"Protocol '{protocol.name}' passes validation with rigor score {rigor_score:.2f}. All critical checks passed."
        else:
            errors = [c for c in checks if c.severity == "error"]
            warnings = [c for c in checks if c.severity == "warning"]
            return f"Protocol '{protocol.name}' has {len(errors)} error(s) and {len(warnings)} warning(s). Rigor score: {rigor_score:.2f}. See recommendations for improvements."

    def _generate_recommendations(
        self,
        protocol: ExperimentProtocol,
        checks: List[ValidationCheck]
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        # Collect all check recommendations
        for check in checks:
            if check.status == "failed" and check.recommendation:
                recommendations.append(check.recommendation)

        # Add general recommendations
        if protocol.sample_size and protocol.sample_size < 50:
            recommendations.append("Consider increasing sample size for more robust results")

        if not protocol.reproducibility_notes:
            recommendations.append("Add detailed reproducibility notes")

        return list(dict.fromkeys(recommendations))  # Remove duplicates
