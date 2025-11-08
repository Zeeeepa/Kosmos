"""
Statistical Power Analysis.

Calculates required sample sizes and statistical power for experiments.
Uses statsmodels for power analysis calculations.
"""

import logging
from typing import Optional, Dict, Any
import math

logger = logging.getLogger(__name__)


class PowerAnalyzer:
    """
    Statistical power analysis for experiment design.

    Calculates sample sizes needed for adequate statistical power.

    Example:
        ```python
        analyzer = PowerAnalyzer()

        # T-test power analysis
        n = analyzer.ttest_sample_size(
            effect_size=0.5,  # Cohen's d
            power=0.8,
            alpha=0.05
        )
        print(f"Need {n} samples per group")

        # Check power for existing sample size
        power = analyzer.ttest_power(
            effect_size=0.5,
            n_per_group=30,
            alpha=0.05
        )
        print(f"Power: {power:.2f}")
        ```
    """

    def __init__(self):
        """Initialize power analyzer."""
        self.default_power = 0.8
        self.default_alpha = 0.05

    def ttest_sample_size(
        self,
        effect_size: float,
        power: float = 0.8,
        alpha: float = 0.05,
        alternative: str = "two-sided"
    ) -> int:
        """
        Calculate sample size for independent samples t-test.

        Args:
            effect_size: Cohen's d (small=0.2, medium=0.5, large=0.8)
            power: Desired statistical power (typically 0.8)
            alpha: Significance level (typically 0.05)
            alternative: "two-sided" or "one-sided"

        Returns:
            Required sample size per group
        """
        try:
            from statsmodels.stats.power import TTestIndPower

            power_analysis = TTestIndPower()

            # Calculate required sample size
            n = power_analysis.solve_power(
                effect_size=effect_size,
                power=power,
                alpha=alpha,
                ratio=1.0,  # Equal group sizes
                alternative=alternative
            )

            # Round up to nearest integer
            n_required = math.ceil(n)

            logger.info(
                f"T-test power analysis: d={effect_size}, power={power}, "
                f"alpha={alpha} → n={n_required} per group"
            )

            return n_required

        except ImportError:
            logger.warning("statsmodels not available, using approximation")
            return self._ttest_sample_size_approx(effect_size, power, alpha)

    def _ttest_sample_size_approx(
        self,
        effect_size: float,
        power: float = 0.8,
        alpha: float = 0.05
    ) -> int:
        """Approximate t-test sample size without statsmodels."""
        # Simplified formula (assumes two-sided, equal variance)
        # n ≈ 2 * [(z_alpha/2 + z_beta) / d]^2

        from scipy import stats

        z_alpha = stats.norm.ppf(1 - alpha / 2)  # two-sided
        z_beta = stats.norm.ppf(power)

        n = 2 * ((z_alpha + z_beta) / effect_size) ** 2

        return math.ceil(n)

    def ttest_power(
        self,
        effect_size: float,
        n_per_group: int,
        alpha: float = 0.05,
        alternative: str = "two-sided"
    ) -> float:
        """
        Calculate statistical power for t-test given sample size.

        Args:
            effect_size: Cohen's d
            n_per_group: Sample size per group
            alpha: Significance level
            alternative: "two-sided" or "one-sided"

        Returns:
            Statistical power (0.0-1.0)
        """
        try:
            from statsmodels.stats.power import TTestIndPower

            power_analysis = TTestIndPower()

            power = power_analysis.solve_power(
                effect_size=effect_size,
                nobs1=n_per_group,
                alpha=alpha,
                ratio=1.0,
                alternative=alternative
            )

            logger.info(
                f"T-test power: d={effect_size}, n={n_per_group}, "
                f"alpha={alpha} → power={power:.3f}"
            )

            return float(power)

        except ImportError:
            logger.warning("statsmodels not available for power calculation")
            return 0.8  # Fallback assumption

    def anova_sample_size(
        self,
        effect_size: float,
        num_groups: int,
        power: float = 0.8,
        alpha: float = 0.05
    ) -> int:
        """
        Calculate sample size for one-way ANOVA.

        Args:
            effect_size: Cohen's f (small=0.1, medium=0.25, large=0.4)
            num_groups: Number of groups to compare
            power: Desired statistical power
            alpha: Significance level

        Returns:
            Required sample size per group
        """
        try:
            from statsmodels.stats.power import FTestAnovaPower

            power_analysis = FTestAnovaPower()

            # Calculate required sample size
            n = power_analysis.solve_power(
                effect_size=effect_size,
                nobs=None,  # Solve for this
                alpha=alpha,
                power=power,
                k_groups=num_groups
            )

            # n is total sample size, divide by number of groups
            n_per_group = math.ceil(n / num_groups)

            logger.info(
                f"ANOVA power analysis: f={effect_size}, k={num_groups}, "
                f"power={power}, alpha={alpha} → n={n_per_group} per group"
            )

            return n_per_group

        except ImportError:
            logger.warning("statsmodels not available, using approximation")
            return self._anova_sample_size_approx(effect_size, num_groups, power, alpha)

    def _anova_sample_size_approx(
        self,
        effect_size: float,
        num_groups: int,
        power: float = 0.8,
        alpha: float = 0.05
    ) -> int:
        """Approximate ANOVA sample size without statsmodels."""
        from scipy import stats

        # Convert f to f²
        f_squared = effect_size ** 2

        # Degrees of freedom
        df1 = num_groups - 1

        # Critical F value
        f_crit = stats.f.ppf(1 - alpha, df1, 1000)  # Assume large df2

        # Approximate using t-test formula with adjusted effect size
        # This is a rough approximation
        adjusted_d = effect_size * math.sqrt(2)
        n_approx = self._ttest_sample_size_approx(adjusted_d, power, alpha)

        return n_approx

    def correlation_sample_size(
        self,
        effect_size: float,
        power: float = 0.8,
        alpha: float = 0.05
    ) -> int:
        """
        Calculate sample size for correlation test.

        Args:
            effect_size: Expected correlation r (small=0.1, medium=0.3, large=0.5)
            power: Desired statistical power
            alpha: Significance level

        Returns:
            Required total sample size
        """
        # Formula: n ≈ [(z_alpha + z_beta) / (0.5 * ln((1+r)/(1-r)))]^2 + 3
        from scipy import stats

        z_alpha = stats.norm.ppf(1 - alpha / 2)  # two-sided
        z_beta = stats.norm.ppf(power)

        # Fisher's z transformation
        if abs(effect_size) >= 1.0:
            effect_size = 0.99 if effect_size > 0 else -0.99

        fisher_z = 0.5 * math.log((1 + effect_size) / (1 - effect_size))

        n = ((z_alpha + z_beta) / fisher_z) ** 2 + 3

        n_required = math.ceil(n)

        logger.info(
            f"Correlation power analysis: r={effect_size}, power={power}, "
            f"alpha={alpha} → n={n_required}"
        )

        return n_required

    def regression_sample_size(
        self,
        effect_size: float,
        num_predictors: int,
        power: float = 0.8,
        alpha: float = 0.05
    ) -> int:
        """
        Calculate sample size for multiple regression.

        Args:
            effect_size: Cohen's f² (small=0.02, medium=0.15, large=0.35)
            num_predictors: Number of predictor variables
            power: Desired statistical power
            alpha: Significance level

        Returns:
            Required total sample size
        """
        try:
            from statsmodels.stats.power import FTestPower

            power_analysis = FTestPower()

            # Calculate required sample size
            # df1 = num_predictors, df2 = n - num_predictors - 1
            # We need to solve for n such that df2 = n - num_predictors - 1

            # Use iterative approach
            n_min = num_predictors + 10
            n_max = 10000

            for n in range(n_min, n_max):
                df2 = n - num_predictors - 1
                if df2 <= 0:
                    continue

                test_power = power_analysis.solve_power(
                    effect_size=effect_size,
                    df_num=num_predictors,
                    df_denom=df2,
                    alpha=alpha,
                    ncc=1  # non-centrality parameter calculation
                )

                if test_power >= power:
                    logger.info(
                        f"Regression power analysis: f²={effect_size}, p={num_predictors}, "
                        f"power={power}, alpha={alpha} → n={n}"
                    )
                    return n

            return n_max

        except ImportError:
            logger.warning("statsmodels not available, using approximation")
            return self._regression_sample_size_approx(effect_size, num_predictors, power, alpha)

    def _regression_sample_size_approx(
        self,
        effect_size: float,
        num_predictors: int,
        power: float = 0.8,
        alpha: float = 0.05
    ) -> int:
        """Approximate regression sample size using rule of thumb."""
        # Common rule: N >= 50 + 8*p (for R² testing)
        # Or N >= 104 + p (for individual predictors)

        # Use conservative estimate
        n_approx = max(
            50 + 8 * num_predictors,
            104 + num_predictors,
            int(num_predictors / effect_size + 10)  # Very rough
        )

        return n_approx

    def chi_square_sample_size(
        self,
        effect_size: float,
        df: int,
        power: float = 0.8,
        alpha: float = 0.05
    ) -> int:
        """
        Calculate sample size for chi-square test.

        Args:
            effect_size: Cohen's w (small=0.1, medium=0.3, large=0.5)
            df: Degrees of freedom (rows-1)*(cols-1)
            power: Desired statistical power
            alpha: Significance level

        Returns:
            Required total sample size
        """
        try:
            from statsmodels.stats.power import GofChisquarePower

            power_analysis = GofChisquarePower()

            n = power_analysis.solve_power(
                effect_size=effect_size,
                nobs=None,  # Solve for this
                alpha=alpha,
                power=power,
                n_bins=df + 1
            )

            n_required = math.ceil(n)

            logger.info(
                f"Chi-square power analysis: w={effect_size}, df={df}, "
                f"power={power}, alpha={alpha} → n={n_required}"
            )

            return n_required

        except ImportError:
            logger.warning("statsmodels not available for chi-square power analysis")
            # Rough approximation
            n_approx = int((df + 1) / (effect_size ** 2) * 10)
            return max(n_approx, 30)

    def interpret_effect_size(
        self,
        effect_size: float,
        test_type: str
    ) -> str:
        """
        Interpret effect size magnitude.

        Args:
            effect_size: Effect size value
            test_type: Type of test (t_test, anova, correlation, regression)

        Returns:
            Interpretation string (small/medium/large)
        """
        if test_type == "t_test":
            # Cohen's d
            if abs(effect_size) < 0.3:
                return "small"
            elif abs(effect_size) < 0.8:
                return "medium"
            else:
                return "large"

        elif test_type == "anova":
            # Cohen's f
            if abs(effect_size) < 0.25:
                return "small"
            elif abs(effect_size) < 0.4:
                return "medium"
            else:
                return "large"

        elif test_type == "correlation":
            # Pearson's r
            if abs(effect_size) < 0.3:
                return "small"
            elif abs(effect_size) < 0.5:
                return "medium"
            else:
                return "large"

        elif test_type == "regression":
            # Cohen's f²
            if abs(effect_size) < 0.15:
                return "small"
            elif abs(effect_size) < 0.35:
                return "medium"
            else:
                return "large"

        return "unknown"

    def generate_power_report(
        self,
        test_type: str,
        effect_size: float,
        sample_size: Optional[int] = None,
        num_groups: int = 2,
        num_predictors: int = 1,
        power: float = 0.8,
        alpha: float = 0.05
    ) -> Dict[str, Any]:
        """
        Generate comprehensive power analysis report.

        Args:
            test_type: "t_test", "anova", "correlation", or "regression"
            effect_size: Expected effect size
            sample_size: If provided, calculate power; otherwise calculate required n
            num_groups: For ANOVA
            num_predictors: For regression
            power: Desired power if calculating sample size
            alpha: Significance level

        Returns:
            Dict with power analysis results and interpretation
        """
        report = {
            "test_type": test_type,
            "effect_size": effect_size,
            "effect_size_interpretation": self.interpret_effect_size(effect_size, test_type),
            "alpha": alpha,
            "power": power,
        }

        try:
            if test_type == "t_test":
                if sample_size:
                    achieved_power = self.ttest_power(effect_size, sample_size, alpha)
                    report["sample_size_per_group"] = sample_size
                    report["achieved_power"] = achieved_power
                    report["adequate"] = achieved_power >= power
                else:
                    required_n = self.ttest_sample_size(effect_size, power, alpha)
                    report["required_sample_size_per_group"] = required_n
                    report["total_sample_size"] = required_n * 2

            elif test_type == "anova":
                required_n = self.anova_sample_size(effect_size, num_groups, power, alpha)
                report["required_sample_size_per_group"] = required_n
                report["total_sample_size"] = required_n * num_groups
                report["num_groups"] = num_groups

            elif test_type == "correlation":
                required_n = self.correlation_sample_size(effect_size, power, alpha)
                report["required_total_sample_size"] = required_n

            elif test_type == "regression":
                required_n = self.regression_sample_size(effect_size, num_predictors, power, alpha)
                report["required_total_sample_size"] = required_n
                report["num_predictors"] = num_predictors

            # Add recommendation
            if sample_size and "adequate" in report:
                if report["adequate"]:
                    report["recommendation"] = f"Sample size of {sample_size} per group is adequate (power={report['achieved_power']:.2f})"
                else:
                    needed = self.ttest_sample_size(effect_size, power, alpha)
                    report["recommendation"] = f"Increase sample size to {needed} per group for {power:.0%} power"
            elif "required_sample_size_per_group" in report:
                report["recommendation"] = f"Use {report['required_sample_size_per_group']} samples per group for {power:.0%} power"
            elif "required_total_sample_size" in report:
                report["recommendation"] = f"Use {report['required_total_sample_size']} total samples for {power:.0%} power"

        except Exception as e:
            logger.error(f"Error generating power report: {e}")
            report["error"] = str(e)

        return report
