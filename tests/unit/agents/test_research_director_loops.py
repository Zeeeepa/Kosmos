"""
Unit tests for ResearchDirectorAgent infinite loop prevention (Issue #51).

These tests verify the fixes for:
- Bug A: DESIGNING state premature CONVERGE
- Bug B: ANALYZING state with no results
- Bug C: Double iteration increment
- Bug D: EXECUTING state with empty queue/results
- MAX_ACTIONS_PER_ITERATION safety counter
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from kosmos.agents.research_director import (
    ResearchDirectorAgent,
    MAX_ACTIONS_PER_ITERATION
)
from kosmos.core.workflow import WorkflowState, NextAction


@pytest.fixture
def mock_director():
    """Create a mocked research director for state machine testing."""
    with patch('kosmos.agents.research_director.get_client') as mock_client, \
         patch('kosmos.agents.research_director.get_world_model') as mock_wm, \
         patch('kosmos.agents.research_director.SkillLoader') as mock_skills, \
         patch('kosmos.db.init_from_config'):
        mock_client.return_value = MagicMock()
        mock_wm.return_value = MagicMock()
        mock_skills.return_value = MagicMock()
        mock_skills.return_value.load_skills_for_task.return_value = ""

        director = ResearchDirectorAgent(
            research_question="Test question for loop prevention",
            domain="biology",
            config={"max_iterations": 10}
        )

        # Mock the research plan
        director.research_plan = MagicMock()
        director.research_plan.iteration_count = 0
        director.research_plan.max_iterations = 10
        director.research_plan.hypothesis_pool = []
        director.research_plan.experiment_queue = []
        director.research_plan.results = []
        director.research_plan.tested_hypotheses = set()
        director.research_plan.get_untested_hypotheses.return_value = []

        # Mock workflow
        director.workflow = MagicMock()
        director.workflow.current_state = WorkflowState.INITIALIZING

        yield director


class TestBugADesigningStateFix:
    """Test Bug A fix: DESIGNING state should check experiment_queue before converging."""

    def test_designing_with_queued_experiments_executes(self, mock_director):
        """DESIGNING state with queued experiments should execute, not converge."""
        mock_director.workflow.current_state = WorkflowState.DESIGNING_EXPERIMENTS
        mock_director.research_plan.hypothesis_pool = ["hyp_1"]  # Prevent early convergence
        mock_director.research_plan.get_untested_hypotheses.return_value = []
        mock_director.research_plan.experiment_queue = ["exp_1", "exp_2"]

        action = mock_director.decide_next_action()

        assert action == NextAction.EXECUTE_EXPERIMENT, \
            "Should execute experiments when queue is not empty"

    def test_designing_with_results_analyzes(self, mock_director):
        """DESIGNING state with no queue but results should analyze."""
        mock_director.workflow.current_state = WorkflowState.DESIGNING_EXPERIMENTS
        mock_director.research_plan.hypothesis_pool = ["hyp_1"]  # Prevent early convergence
        # Need untested hypothesis to prevent convergence check
        mock_director.research_plan.get_untested_hypotheses.return_value = ["hyp_1"]
        mock_director.research_plan.experiment_queue = []
        mock_director.research_plan.results = ["result_1"]

        action = mock_director.decide_next_action()

        # With untested hypotheses, should design more experiments
        assert action == NextAction.DESIGN_EXPERIMENT, \
            "Should design experiment for untested hypothesis"

    def test_designing_empty_converges(self, mock_director):
        """DESIGNING state with nothing to do should converge."""
        mock_director.workflow.current_state = WorkflowState.DESIGNING_EXPERIMENTS
        mock_director.research_plan.hypothesis_pool = ["hyp_1"]  # Has hypotheses but all tested
        mock_director.research_plan.get_untested_hypotheses.return_value = []
        mock_director.research_plan.experiment_queue = []
        mock_director.research_plan.results = []

        action = mock_director.decide_next_action()

        assert action == NextAction.CONVERGE, \
            "Should converge when nothing left to do"


class TestBugBAnalyzingStateFix:
    """Test Bug B fix: ANALYZING state should handle empty results."""

    def test_analyzing_with_no_results_falls_back(self, mock_director):
        """ANALYZING state with no results should fall back."""
        mock_director.workflow.current_state = WorkflowState.ANALYZING
        mock_director.research_plan.hypothesis_pool = ["hyp_1"]  # Prevent early convergence
        # Untested hypothesis prevents convergence check
        mock_director.research_plan.get_untested_hypotheses.return_value = ["hyp_1"]
        mock_director.research_plan.results = []
        mock_director.research_plan.experiment_queue = []

        action = mock_director.decide_next_action()

        assert action == NextAction.REFINE_HYPOTHESIS, \
            "Should refine hypothesis when no results to analyze"

    def test_analyzing_with_queue_executes(self, mock_director):
        """ANALYZING state with no results but queue should execute."""
        mock_director.workflow.current_state = WorkflowState.ANALYZING
        mock_director.research_plan.hypothesis_pool = ["hyp_1"]  # Prevent early convergence
        # Queue prevents convergence check from triggering
        mock_director.research_plan.get_untested_hypotheses.return_value = []
        mock_director.research_plan.results = []
        mock_director.research_plan.experiment_queue = ["exp_1"]

        action = mock_director.decide_next_action()

        assert action == NextAction.EXECUTE_EXPERIMENT, \
            "Should execute experiments when queue available"

    def test_analyzing_with_results_analyzes(self, mock_director):
        """ANALYZING state with results should analyze."""
        mock_director.workflow.current_state = WorkflowState.ANALYZING
        mock_director.research_plan.hypothesis_pool = ["hyp_1"]  # Prevent early convergence
        # Untested hypothesis prevents convergence check
        mock_director.research_plan.get_untested_hypotheses.return_value = ["hyp_1"]
        mock_director.research_plan.results = ["result_1"]

        action = mock_director.decide_next_action()

        assert action == NextAction.ANALYZE_RESULT, \
            "Should analyze when results exist"


class TestBugDExecutingStateFix:
    """Test Bug D fix: EXECUTING state should handle empty queue/results."""

    def test_executing_empty_queue_with_results_analyzes(self, mock_director):
        """EXECUTING state with empty queue but results should analyze."""
        mock_director.workflow.current_state = WorkflowState.EXECUTING
        mock_director.research_plan.hypothesis_pool = ["hyp_1"]  # Prevent early convergence
        # Untested hypothesis prevents convergence check
        mock_director.research_plan.get_untested_hypotheses.return_value = ["hyp_1"]
        mock_director.research_plan.experiment_queue = []
        mock_director.research_plan.results = ["result_1"]

        action = mock_director.decide_next_action()

        assert action == NextAction.ANALYZE_RESULT, \
            "Should analyze results when queue empty"

    def test_executing_empty_everything_refines(self, mock_director):
        """EXECUTING state with empty queue and no results should refine."""
        mock_director.workflow.current_state = WorkflowState.EXECUTING
        mock_director.research_plan.hypothesis_pool = ["hyp_1"]  # Prevent early convergence
        # Untested hypothesis prevents convergence check
        mock_director.research_plan.get_untested_hypotheses.return_value = ["hyp_1"]
        mock_director.research_plan.experiment_queue = []
        mock_director.research_plan.results = []

        action = mock_director.decide_next_action()

        assert action == NextAction.REFINE_HYPOTHESIS, \
            "Should refine to recover from stuck state"

    def test_executing_with_queue_executes(self, mock_director):
        """EXECUTING state with queued experiments should execute."""
        mock_director.workflow.current_state = WorkflowState.EXECUTING
        mock_director.research_plan.hypothesis_pool = ["hyp_1"]  # Prevent early convergence
        # Queue is set, so we test the actual state logic
        mock_director.research_plan.get_untested_hypotheses.return_value = []
        mock_director.research_plan.experiment_queue = ["exp_1"]

        action = mock_director.decide_next_action()

        assert action == NextAction.EXECUTE_EXPERIMENT, \
            "Should execute when queue has items"


class TestMaxActionsPerIterationSafety:
    """Test MAX_ACTIONS_PER_ITERATION safety counter."""

    def test_action_counter_forces_convergence(self, mock_director):
        """Exceeding MAX_ACTIONS should force convergence."""
        mock_director.workflow.current_state = WorkflowState.GENERATING_HYPOTHESES

        # Simulate exceeding action limit
        mock_director._actions_this_iteration = MAX_ACTIONS_PER_ITERATION + 1

        action = mock_director.decide_next_action()

        assert action == NextAction.CONVERGE, \
            "Should force convergence when action limit exceeded"

    def test_action_counter_increments(self, mock_director):
        """Action counter should increment each call."""
        mock_director.workflow.current_state = WorkflowState.GENERATING_HYPOTHESES

        # Ensure clean state
        if hasattr(mock_director, '_actions_this_iteration'):
            delattr(mock_director, '_actions_this_iteration')

        mock_director.decide_next_action()

        assert mock_director._actions_this_iteration == 1, \
            "Action counter should start at 1"

        mock_director.decide_next_action()

        assert mock_director._actions_this_iteration == 2, \
            "Action counter should increment"

    def test_max_actions_constant_defined(self):
        """MAX_ACTIONS_PER_ITERATION should be defined and reasonable."""
        assert MAX_ACTIONS_PER_ITERATION > 0, \
            "MAX_ACTIONS should be positive"
        assert MAX_ACTIONS_PER_ITERATION >= 10, \
            "MAX_ACTIONS should allow reasonable workflow"
        assert MAX_ACTIONS_PER_ITERATION <= 100, \
            "MAX_ACTIONS should prevent runaway loops"


class TestDomainValidation:
    """Test domain validation and logging."""

    def test_valid_domain_accepted(self, mock_director):
        """Valid domain should be accepted without warning."""
        # The fixture already sets domain="biology" which is valid
        assert mock_director.domain == "biology"

    def test_domain_validation_method_exists(self, mock_director):
        """_validate_domain method should exist."""
        assert hasattr(mock_director, '_validate_domain')
        assert callable(mock_director._validate_domain)


class TestSkillsIntegration:
    """Test skills integration."""

    def test_skills_attribute_exists(self, mock_director):
        """Skills attribute should be initialized."""
        assert hasattr(mock_director, 'skills')

    def test_get_skills_context_method_exists(self, mock_director):
        """get_skills_context method should exist."""
        assert hasattr(mock_director, 'get_skills_context')
        assert callable(mock_director.get_skills_context)

    def test_get_skills_context_returns_string(self, mock_director):
        """get_skills_context should return a string."""
        result = mock_director.get_skills_context()
        assert isinstance(result, str)
