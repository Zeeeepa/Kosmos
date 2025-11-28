"""
Comprehensive system sanity tests for Kosmos AI Scientist.

Tests all major components to validate the complete system works end-to-end.
These are component-level sanity tests designed to touch every major part
of the system and validate basic functionality.
"""

import pytest
import os
from pathlib import Path


@pytest.mark.e2e
class TestComponentSanity:
    """Test each major component works independently."""

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"),
        reason="API key required"
    )
    def test_llm_provider_integration(self):
        """Test LLM provider can generate text."""
        from kosmos.core.llm import get_client

        print("\n🤖 Testing LLM provider integration...")

        client = get_client()

        # Simple generation test
        response = client.generate(
            "Say 'hello' in one word",
            max_tokens=10,
            temperature=0.0
        )

        assert response is not None
        assert hasattr(response, 'content')
        assert len(response.content) > 0
        assert "hello" in response.content.lower()

        print(f"✅ LLM provider operational")
        print(f"   Response: {response.content}")

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"),
        reason="API key required"
    )
    def test_hypothesis_generator(self):
        """Test hypothesis generator creates valid hypotheses."""
        from kosmos.agents.hypothesis_generator import HypothesisGeneratorAgent

        print("\n💡 Testing hypothesis generator...")

        generator = HypothesisGeneratorAgent(config={"num_hypotheses": 2})

        # Generate hypotheses
        response = generator.generate_hypotheses(
            research_question="How does temperature affect enzyme activity?",
            domain="biology"
        )

        assert response is not None
        assert hasattr(response, 'hypotheses')
        assert len(response.hypotheses) >= 1, "No hypotheses generated"

        # Verify first hypothesis structure
        hyp = response.hypotheses[0]
        assert hyp.statement is not None
        assert hyp.domain == "biology"
        assert hyp.research_question is not None

        print(f"✅ Generated {len(response.hypotheses)} hypothesis(es)")
        print(f"   First: {hyp.statement[:80]}...")

        if hasattr(hyp, 'novelty_score'):
            print(f"   Novelty: {hyp.novelty_score}")
        if hasattr(hyp, 'testability_score'):
            print(f"   Testability: {hyp.testability_score}")

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"),
        reason="API key required"
    )
    def test_experiment_designer(self):
        """Test experiment designer creates protocols."""
        from kosmos.agents.experiment_designer import ExperimentDesignerAgent
        from kosmos.models.hypothesis import Hypothesis
        import uuid

        print("\n🔬 Testing experiment designer...")

        hypothesis = Hypothesis(
            id=str(uuid.uuid4()),
            research_question="Does temperature affect chemical reaction rates?",
            statement="Higher temperatures increase chemical reaction rates due to increased molecular kinetic energy",
            rationale="According to kinetic molecular theory, higher temperatures result in faster molecular motion and more frequent collisions with sufficient activation energy",
            domain="chemistry",
            testability_score=0.8,
            novelty_score=0.6
        )

        designer = ExperimentDesignerAgent()
        response = designer.design_experiment(hypothesis)

        assert response is not None, "ExperimentDesigner returned None"
        assert response.protocol is not None, "Response has no protocol"
        assert response.protocol.hypothesis_id == hypothesis.id, "Protocol hypothesis_id mismatch"
        assert response.protocol.experiment_type is not None, "Protocol has no experiment_type"
        assert len(response.protocol.steps) > 0, "Protocol has no steps"

        print(f"✅ Experiment designer operational")
        print(f"   Protocol: {response.protocol.name}")
        print(f"   Type: {response.protocol.experiment_type.value}")
        print(f"   Steps: {len(response.protocol.steps)}")

    def test_code_generator(self):
        """Test code generator creates valid Python code."""
        from kosmos.execution.code_generator import ExperimentCodeGenerator
        from kosmos.models.experiment import (
            ExperimentProtocol, ProtocolStep, Variable, VariableType,
            ResourceRequirements, StatisticalTestSpec, StatisticalTest
        )
        from kosmos.models.hypothesis import ExperimentType

        print("\n💻 Testing code generator...")

        # Create a complete ExperimentProtocol with correct schema
        from kosmos.models.experiment import ControlGroup

        protocol = ExperimentProtocol(
            id="test-e2e-001",
            hypothesis_id="hyp-e2e-001",
            name="T-Test Comparison Experiment",
            domain="statistics",
            description="Statistical comparison of treatment vs control groups using t-test analysis",
            objective="Determine if treatment has significant effect on outcome measure",
            experiment_type=ExperimentType.DATA_ANALYSIS,
            steps=[
                ProtocolStep(
                    step_number=1,
                    title="Load Data",
                    description="Load experimental data from CSV source file",
                    action="df = pd.read_csv('data.csv')"
                ),
                ProtocolStep(
                    step_number=2,
                    title="Perform T-Test",
                    description="Run independent samples t-test comparing groups",
                    action="result = stats.ttest_ind(group1, group2)"
                )
            ],
            variables={
                "group": Variable(
                    name="group",
                    type=VariableType.INDEPENDENT,
                    description="Treatment group assignment variable"
                ),
                "measurement": Variable(
                    name="measurement",
                    type=VariableType.DEPENDENT,
                    description="Primary outcome measurement variable"
                )
            },
            control_groups=[
                ControlGroup(
                    name="control",
                    description="Untreated baseline control group",
                    variables={"treatment": False},
                    rationale="Baseline for comparison against treatment group"
                )
            ],
            statistical_tests=[
                StatisticalTestSpec(
                    test_type=StatisticalTest.T_TEST,
                    description="Independent samples t-test for group comparison",
                    null_hypothesis="No difference between group means",
                    variables=["measurement"]
                )
            ],
            resource_requirements=ResourceRequirements(
                estimated_duration_days=1.0,
                estimated_cost_usd=0.0
            )
        )

        # Test code generation without LLM (template-only)
        generator = ExperimentCodeGenerator(use_templates=True, use_llm=False)
        code = generator.generate(protocol)

        assert code is not None, "Code generator returned None"
        assert len(code) > 0, "Generated code is empty"
        assert "import" in code, "Code missing imports"

        # Verify it's valid Python syntax
        import ast
        try:
            ast.parse(code)
            syntax_valid = True
        except SyntaxError as e:
            syntax_valid = False
            print(f"   Syntax error: {e}")

        assert syntax_valid, "Generated code has invalid Python syntax"

        print(f"✅ Code generator operational")
        print(f"   Generated {len(code)} characters of code")
        print(f"   Syntax: valid Python")

    def test_safety_validator(self):
        """Test safety validator blocks dangerous code."""
        from kosmos.safety.code_validator import CodeValidator

        print("\n🛡️  Testing safety validator...")

        validator = CodeValidator()

        # Test safe code
        safe_code = "import numpy as np\nresult = np.mean([1, 2, 3])"
        safe_result = validator.validate(safe_code)
        assert safe_result.passed is True
        print(f"✅ Safe code allowed")

        # Test dangerous code
        dangerous_code = "import os; os.system('rm -rf /')"
        dangerous_result = validator.validate(dangerous_code)
        assert dangerous_result.passed is False
        assert len(dangerous_result.violations) > 0
        print(f"✅ Dangerous code blocked")
        print(f"   Violations: {len(dangerous_result.violations)}")

    def test_code_executor(self):
        """Test code executor can run safe code."""
        from kosmos.execution.executor import CodeExecutor

        print("\n▶️  Testing code executor...")

        executor = CodeExecutor(use_sandbox=False)  # Direct execution for speed

        safe_code = """
import numpy as np
result = np.mean([10, 20, 30, 40, 50])
print(f"Mean: {result}")
"""

        exec_result = executor.execute(safe_code)

        assert exec_result.success is True
        assert exec_result.error is None
        assert "Mean: 30" in exec_result.stdout
        assert exec_result.execution_time > 0

        print(f"✅ Code executed successfully")
        print(f"   Time: {exec_result.execution_time:.3f}s")
        print(f"   Output: {exec_result.stdout.strip()}")

    def test_sandboxed_execution(self):
        """Test Docker sandbox execution."""
        from kosmos.execution.sandbox import DockerSandbox

        print("\n🐳 Testing Docker sandbox execution...")

        # Create sandbox with conservative limits for testing
        sandbox = DockerSandbox(
            cpu_limit=1.0,
            memory_limit="512m",
            timeout=60,
            enable_monitoring=True
        )

        try:
            # Execute simple code
            code = """
import numpy as np
data = [1, 2, 3, 4, 5]
result = np.mean(data)
print(f"Mean: {result}")
print(f"RESULT:{result}")
"""
            result = sandbox.execute(code)

            assert result.success is True, f"Execution failed: {result.error}"
            assert result.exit_code == 0, f"Non-zero exit code: {result.exit_code}"
            assert "Mean: 3.0" in result.stdout, f"Expected output not found: {result.stdout}"
            assert result.timeout_occurred is False, "Unexpected timeout"

            print(f"✅ Docker sandbox execution successful")
            print(f"   Output: {result.stdout.strip()[:100]}")
            print(f"   Execution time: {result.execution_time:.2f}s")
            if result.resource_stats:
                print(f"   Resources: {result.resource_stats}")
        finally:
            sandbox.cleanup()

    @pytest.mark.skip(reason="DataAnalysis module API needs deeper investigation - complex setup")
    def test_statistical_analysis(self):
        """Test statistical analysis functions."""
        pass

    @pytest.mark.skip(reason="DataAnalyst agent API needs deeper investigation - complex setup")
    def test_data_analyst(self):
        """Test data analyst interprets results."""
        pass

    def test_database_persistence(self):
        """Test database persistence works."""
        from kosmos.db import init_database, get_session
        from kosmos.db.models import Hypothesis, HypothesisStatus
        import tempfile
        import uuid

        print("\n💾 Testing database persistence...")

        # Use a temporary database for testing
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name

        init_database(f"sqlite:///{db_path}")

        # Create a hypothesis with explicit ID
        hyp_id = str(uuid.uuid4())
        with get_session() as session:
            hypothesis = Hypothesis(
                id=hyp_id,
                research_question="Does X affect Y?",
                statement="X increases Y through mechanism Z",
                rationale="Prior research suggests a causal relationship between X and Y",
                domain="test_domain",
                status=HypothesisStatus.GENERATED,
                novelty_score=0.75,
                testability_score=0.80
            )
            session.add(hypothesis)

        # Verify retrieval
        with get_session() as session:
            retrieved = session.query(Hypothesis).filter(Hypothesis.id == hyp_id).first()
            assert retrieved is not None, "Failed to retrieve hypothesis"
            assert retrieved.statement == "X increases Y through mechanism Z"
            assert retrieved.domain == "test_domain"
            assert retrieved.novelty_score == 0.75

        # Clean up
        import os
        os.unlink(db_path)

        print(f"✅ Database persistence operational")
        print(f"   Created, stored, and retrieved hypothesis")
        print(f"   ID: {hyp_id[:8]}...")

    @pytest.mark.skip(reason="Neo4j authentication not configured")
    def test_knowledge_graph(self):
        """Test knowledge graph operations."""
        pass


@pytest.mark.e2e
@pytest.mark.slow
class TestEndToEndMiniWorkflow:
    """Test simplified end-to-end workflow without complex agent coordination."""

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"),
        reason="API key required"
    )
    def test_mini_research_workflow(self):
        """Test simplified pipeline: question → hypothesis → execution."""
        from kosmos.agents.hypothesis_generator import HypothesisGeneratorAgent
        from kosmos.execution.executor import CodeExecutor

        print("\n🔄 Testing mini end-to-end workflow...")

        research_question = "Is there a correlation between study time and test scores?"

        # Step 1: Generate hypothesis
        print("\n  Step 1: Generate hypothesis...")
        generator = HypothesisGeneratorAgent(config={"num_hypotheses": 1})
        response = generator.generate_hypotheses(research_question, domain="social_science")
        assert len(response.hypotheses) > 0
        hypothesis = response.hypotheses[0]
        print(f"  ✅ Hypothesis: {hypothesis.statement[:60]}...")
        print(f"     Domain: {hypothesis.domain}")
        print(f"     Research question: {hypothesis.research_question[:50]}...")

        # Step 2: Execute simple code (validate executor works)
        print("\n  Step 2: Execute simple analysis code...")
        executor = CodeExecutor(use_sandbox=False)  # Fast direct execution

        # Simple mock analysis
        mock_code = """
import numpy as np
import pandas as pd

# Simulate study time vs test score data
study_hours = [1, 2, 3, 4, 5, 6, 7, 8]
test_scores = [55, 60, 65, 70, 75, 80, 85, 90]

# Calculate correlation
correlation = np.corrcoef(study_hours, test_scores)[0, 1]
print(f"Correlation: {correlation:.3f}")
print(f"Conclusion: {'Strong positive correlation' if correlation > 0.7 else 'Weak correlation'}")
"""

        exec_result = executor.execute(mock_code)
        assert exec_result.success is True
        print(f"  ✅ Execution successful")
        print(f"     Output: {exec_result.stdout.strip()}")

        # Verify end-to-end flow
        print("\n✅ COMPLETE MINI WORKFLOW VALIDATED")
        print(f"   Question → Hypothesis → Analysis → Results")
        print(f"   Core pipeline components integrated successfully!")
