"""
Result Summarization.

Natural language summaries of experiment results using Claude.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from kosmos.core.llm import get_client
from kosmos.models.result import ExperimentResult
from kosmos.models.hypothesis import Hypothesis

logger = logging.getLogger(__name__)


class ResultSummary:
    """Structured natural language summary of results."""

    def __init__(
        self,
        experiment_id: str,
        summary: str,
        key_findings: List[str],
        hypothesis_comparison: str,
        limitations: List[str],
        future_work: List[str],
        created_at: Optional[datetime] = None
    ):
        """
        Initialize result summary.

        Args:
            experiment_id: ID of experiment
            summary: 2-3 paragraph natural language summary
            key_findings: List of 3-5 key findings
            hypothesis_comparison: Comparison to original hypothesis
            limitations: List of limitations and caveats
            future_work: List of suggested follow-up experiments
            created_at: Timestamp
        """
        self.experiment_id = experiment_id
        self.summary = summary
        self.key_findings = key_findings
        self.hypothesis_comparison = hypothesis_comparison
        self.limitations = limitations
        self.future_work = future_work
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "experiment_id": self.experiment_id,
            "summary": self.summary,
            "key_findings": self.key_findings,
            "hypothesis_comparison": self.hypothesis_comparison,
            "limitations": self.limitations,
            "future_work": self.future_work,
            "created_at": self.created_at.isoformat()
        }

    def to_markdown(self) -> str:
        """Convert to markdown format."""
        md = f"# Experiment Result Summary: {self.experiment_id}\n\n"
        md += f"## Summary\n\n{self.summary}\n\n"
        md += "## Key Findings\n\n"
        for i, finding in enumerate(self.key_findings, 1):
            md += f"{i}. {finding}\n"
        md += f"\n## Hypothesis Assessment\n\n{self.hypothesis_comparison}\n\n"
        md += "## Limitations\n\n"
        for limitation in self.limitations:
            md += f"- {limitation}\n"
        md += "\n## Recommended Future Work\n\n"
        for i, work in enumerate(self.future_work, 1):
            md += f"{i}. {work}\n"
        return md


class ResultSummarizer:
    """
    Natural language result summarization using Claude.

    Capabilities:
    - Generate plain-language summaries of results
    - Extract key findings
    - Compare results to hypothesis
    - Identify limitations
    - Suggest follow-up experiments

    Example:
        ```python
        summarizer = ResultSummarizer()

        summary = summarizer.generate_summary(
            result=experiment_result,
            hypothesis=original_hypothesis,
            interpretation=data_analyst_interpretation
        )

        print(summary.summary)
        print("\\n".join(summary.key_findings))
        ```
    """

    def __init__(self):
        """Initialize result summarizer."""
        self.llm_client = get_client()
        logger.info("ResultSummarizer initialized")

    def generate_summary(
        self,
        result: ExperimentResult,
        hypothesis: Optional[Hypothesis] = None,
        interpretation: Optional[Dict[str, Any]] = None,
        literature_context: Optional[str] = None
    ) -> ResultSummary:
        """
        Generate comprehensive natural language summary.

        Args:
            result: ExperimentResult object
            hypothesis: Optional original hypothesis
            interpretation: Optional interpretation from DataAnalystAgent
            literature_context: Optional literature context

        Returns:
            ResultSummary object
        """
        logger.info(f"Generating summary for experiment {result.experiment_id}")

        # Build prompt
        prompt = self._build_summary_prompt(result, hypothesis, interpretation, literature_context)

        # Get Claude summary
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                system="You are a scientific writer creating clear, accurate summaries of "
                       "experimental results for a scientific audience. Be precise but accessible.",
                max_tokens=1500,
                temperature=0.4
            )

            # Parse response
            summary = self._parse_summary_response(response, result.experiment_id)

            logger.info(f"Completed summary for {result.experiment_id}")
            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return self._create_fallback_summary(result, hypothesis)

    def extract_key_findings(
        self,
        result: ExperimentResult,
        max_findings: int = 5
    ) -> List[str]:
        """
        Extract key findings from result.

        Args:
            result: ExperimentResult object
            max_findings: Maximum number of findings

        Returns:
            List of key finding strings
        """
        findings = []

        # Primary result
        if result.primary_test and result.primary_p_value is not None:
            finding = f"{result.primary_test}: "
            if result.primary_p_value < 0.001:
                finding += f"highly significant (p={result.primary_p_value:.4e})"
            elif result.primary_p_value < 0.05:
                finding += f"significant (p={result.primary_p_value:.4f})"
            else:
                finding += f"not significant (p={result.primary_p_value:.4f})"

            if result.primary_effect_size is not None:
                finding += f", effect size = {result.primary_effect_size:.3f}"

            findings.append(finding)

        # Additional statistical tests (skip the primary test)
        for test in result.statistical_tests[:max_findings-1]:
            if test.test_name != result.primary_test:
                test_finding = f"{test.test_name}: p={test.p_value:.4f}"
                if test.effect_size is not None:
                    test_finding += f", effect size = {test.effect_size:.3f}"
                findings.append(test_finding)

        return findings[:max_findings]

    def compare_to_hypothesis(
        self,
        result: ExperimentResult,
        hypothesis: Hypothesis
    ) -> str:
        """
        Compare result to original hypothesis.

        Args:
            result: ExperimentResult object
            hypothesis: Original hypothesis

        Returns:
            Comparison string
        """
        comparison_parts = []

        # Overall support
        if result.supports_hypothesis is True:
            comparison_parts.append(
                f"The experimental results SUPPORT the hypothesis: \"{hypothesis.statement}\""
            )
        elif result.supports_hypothesis is False:
            comparison_parts.append(
                f"The experimental results DO NOT SUPPORT the hypothesis: \"{hypothesis.statement}\""
            )
        else:
            comparison_parts.append(
                f"The experimental results are INCONCLUSIVE regarding the hypothesis: \"{hypothesis.statement}\""
            )

        # Evidence strength
        if result.primary_p_value is not None:
            if result.primary_p_value < 0.01:
                comparison_parts.append("The statistical evidence is strong (p < 0.01).")
            elif result.primary_p_value < 0.05:
                comparison_parts.append("The statistical evidence is moderate (p < 0.05).")
            else:
                comparison_parts.append("The statistical evidence is weak (p > 0.05).")

        # Effect size consideration
        if result.primary_effect_size is not None:
            if abs(result.primary_effect_size) >= 0.8:
                comparison_parts.append("The effect size is large, suggesting practical significance.")
            elif abs(result.primary_effect_size) >= 0.5:
                comparison_parts.append("The effect size is medium.")
            elif abs(result.primary_effect_size) >= 0.2:
                comparison_parts.append("The effect size is small.")
            else:
                comparison_parts.append("The effect size is negligible.")

        return " ".join(comparison_parts)

    def identify_limitations(
        self,
        result: ExperimentResult,
        hypothesis: Optional[Hypothesis] = None
    ) -> List[str]:
        """
        Identify limitations of experiment.

        Args:
            result: ExperimentResult object
            hypothesis: Optional hypothesis

        Returns:
            List of limitation strings
        """
        limitations = []

        # Check for execution issues
        if result.status != "success":
            limitations.append(f"Experiment did not complete successfully (status: {result.status})")

        # Check sample size (if available from metadata)
        for test in result.statistical_tests:
            if test.sample_size is not None and test.sample_size < 30:
                limitations.append(
                    f"Small sample size (n={test.sample_size}) may limit statistical power"
                )
                break

        # Check for missing confidence intervals from primary test
        primary_test_result = result.get_primary_test_result()
        has_ci = False
        if primary_test_result and primary_test_result.confidence_interval:
            ci = primary_test_result.confidence_interval
            has_ci = ci.get('lower') is not None and ci.get('upper') is not None
        if not has_ci:
            limitations.append("Confidence intervals not reported, limiting precision of estimate")

        # Generic limitations
        limitations.append("Replication in independent dataset recommended to confirm findings")
        limitations.append("Potential confounding variables should be considered in interpretation")

        return limitations

    def suggest_future_work(
        self,
        result: ExperimentResult,
        hypothesis: Optional[Hypothesis] = None,
        max_suggestions: int = 5
    ) -> List[str]:
        """
        Suggest follow-up experiments.

        Args:
            result: ExperimentResult object
            hypothesis: Optional hypothesis
            max_suggestions: Maximum suggestions

        Returns:
            List of suggestion strings
        """
        suggestions = []

        # Based on result support
        if result.supports_hypothesis is True:
            suggestions.append("Replicate findings in independent cohort to validate results")
            suggestions.append("Investigate mechanism underlying observed effect")
            suggestions.append("Test dose-response relationship if applicable")
        elif result.supports_hypothesis is False:
            suggestions.append("Investigate why hypothesis was not supported")
            suggestions.append("Test alternative hypotheses based on unexpected findings")
        else:
            suggestions.append("Increase sample size to improve statistical power")
            suggestions.append("Refine experimental design to reduce variability")

        # Generic suggestions
        suggestions.append("Conduct sensitivity analysis to test robustness of findings")
        suggestions.append("Explore potential moderating variables")

        return suggestions[:max_suggestions]

    # ========================================================================
    # INTERNAL METHODS
    # ========================================================================

    def _build_summary_prompt(
        self,
        result: ExperimentResult,
        hypothesis: Optional[Hypothesis],
        interpretation: Optional[Dict[str, Any]],
        literature_context: Optional[str]
    ) -> str:
        """Build prompt for summary generation."""
        prompt_parts = []

        if hypothesis:
            prompt_parts.append(f"HYPOTHESIS: {hypothesis.statement}\n")

        prompt_parts.append(f"""
EXPERIMENTAL RESULTS:
- Primary Test: {result.primary_test}
- P-value: {result.primary_p_value}
- Effect Size: {result.primary_effect_size}
- Hypothesis Supported: {result.supports_hypothesis}
- Status: {result.status}
""")

        if interpretation:
            prompt_parts.append(f"\nINTERPRETATION: {interpretation.get('summary', '')}\n")

        if literature_context:
            prompt_parts.append(f"\nLITERATURE CONTEXT: {literature_context[:500]}\n")

        prompt_parts.append("""
Please provide a comprehensive summary in the following format:

SUMMARY: (2-3 paragraphs explaining the experiment, results, and implications)

KEY FINDINGS:
1. [First key finding]
2. [Second key finding]
3. [Third key finding]

HYPOTHESIS ASSESSMENT: (How do results relate to the hypothesis?)

LIMITATIONS:
- [Limitation 1]
- [Limitation 2]
- [Limitation 3]

FUTURE WORK:
1. [Suggested experiment 1]
2. [Suggested experiment 2]
3. [Suggested experiment 3]
""")

        return "\n".join(prompt_parts)

    def _parse_summary_response(self, response: str, experiment_id: str) -> ResultSummary:
        """Parse Claude response into ResultSummary."""
        # Simple parsing (in production, would use more robust parsing)
        lines = response.split('\n')

        summary = ""
        key_findings = []
        hypothesis_comparison = ""
        limitations = []
        future_work = []

        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith("SUMMARY:"):
                current_section = "summary"
                summary = line.replace("SUMMARY:", "").strip()
            elif line.startswith("KEY FINDINGS:"):
                current_section = "findings"
            elif line.startswith("HYPOTHESIS ASSESSMENT:"):
                current_section = "hypothesis"
                hypothesis_comparison = line.replace("HYPOTHESIS ASSESSMENT:", "").strip()
            elif line.startswith("LIMITATIONS:"):
                current_section = "limitations"
            elif line.startswith("FUTURE WORK:"):
                current_section = "future_work"
            elif line and current_section:
                if current_section == "summary" and not line.startswith(("KEY", "HYPOTHESIS", "LIMITATIONS", "FUTURE")):
                    summary += " " + line
                elif current_section == "findings" and (line[0].isdigit() or line.startswith('-')):
                    key_findings.append(line.lstrip('0123456789.-) '))
                elif current_section == "hypothesis" and not line.startswith(("LIMITATIONS", "FUTURE")):
                    hypothesis_comparison += " " + line
                elif current_section == "limitations" and line.startswith('-'):
                    limitations.append(line.lstrip('- '))
                elif current_section == "future_work" and (line[0].isdigit() or line.startswith('-')):
                    future_work.append(line.lstrip('0123456789.-) '))

        return ResultSummary(
            experiment_id=experiment_id,
            summary=summary.strip(),
            key_findings=key_findings,
            hypothesis_comparison=hypothesis_comparison.strip(),
            limitations=limitations,
            future_work=future_work
        )

    def _create_fallback_summary(
        self,
        result: ExperimentResult,
        hypothesis: Optional[Hypothesis]
    ) -> ResultSummary:
        """Create fallback summary if Claude fails."""
        summary = f"Experiment {result.experiment_id} completed with status {result.status}. "
        summary += f"Primary test ({result.primary_test}) yielded p-value of {result.primary_p_value}. "

        if result.supports_hypothesis is not None:
            summary += f"Results {'support' if result.supports_hypothesis else 'do not support'} the hypothesis."

        return ResultSummary(
            experiment_id=result.experiment_id,
            summary=summary,
            key_findings=self.extract_key_findings(result),
            hypothesis_comparison=self.compare_to_hypothesis(result, hypothesis) if hypothesis else "No hypothesis provided for comparison.",
            limitations=self.identify_limitations(result, hypothesis),
            future_work=self.suggest_future_work(result, hypothesis)
        )
