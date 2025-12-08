"""
Hypothesis data models for runtime use.

Provides Pydantic models for hypothesis generation, validation, and analysis.
Complements the SQLAlchemy Hypothesis model in kosmos.db.models.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from enum import Enum

from kosmos.config import _DEFAULT_CLAUDE_SONNET_MODEL

class ExperimentType(str, Enum):
    """Types of experiments that can test a hypothesis."""
    COMPUTATIONAL = "computational"  # Simulations, algorithms, mathematical proofs
    DATA_ANALYSIS = "data_analysis"  # Statistical analysis of existing datasets
    LITERATURE_SYNTHESIS = "literature_synthesis"  # Systematic review, meta-analysis


class HypothesisStatus(str, Enum):
    """Hypothesis lifecycle status."""
    GENERATED = "generated"
    UNDER_REVIEW = "under_review"
    TESTING = "testing"
    SUPPORTED = "supported"
    REJECTED = "rejected"
    INCONCLUSIVE = "inconclusive"


class Hypothesis(BaseModel):
    """
    Runtime hypothesis model.

    Represents a scientific hypothesis with all associated metadata.

    Example:
        ```python
        hypothesis = Hypothesis(
            statement="Increasing attention head count improves transformer performance",
            rationale="Prior work shows attention is the key mechanism...",
            domain="machine_learning",
            research_question="How does attention mechanism affect performance?",
            testability_score=0.85,
            novelty_score=0.72
        )
        ```
    """
    id: Optional[str] = None
    research_question: str = Field(..., description="Original research question")
    statement: str = Field(..., min_length=10, max_length=500, description="Clear, testable hypothesis statement")
    rationale: str = Field(..., min_length=20, description="Scientific rationale for the hypothesis")

    domain: str = Field(..., description="Scientific domain (e.g., biology, physics, ML)")
    status: HypothesisStatus = Field(default=HypothesisStatus.GENERATED)

    # Scores (0.0 - 1.0)
    testability_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    novelty_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    priority_score: Optional[float] = Field(None, ge=0.0, le=1.0)

    # Testability analysis
    suggested_experiment_types: List[ExperimentType] = Field(default_factory=list)
    estimated_resources: Optional[Dict[str, Any]] = None  # compute, time, cost estimates

    # Novelty analysis
    similar_work: List[str] = Field(default_factory=list)  # Paper IDs of similar work
    novelty_report: Optional[str] = None

    # Literature context
    related_papers: List[str] = Field(default_factory=list)  # Paper IDs used in generation

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str = Field(default="hypothesis_generator")

    # Evolution tracking (Phase 7)
    parent_hypothesis_id: Optional[str] = Field(None, description="ID of parent hypothesis (if refined/spawned)")
    generation: int = Field(default=1, ge=1, description="Generation number (1 = original, 2+ = refined)")
    refinement_count: int = Field(default=0, ge=0, description="Number of times this hypothesis was refined")
    evolution_history: List[Dict[str, Any]] = Field(default_factory=list, description="History of refinements and results")

    @field_validator('statement')
    @classmethod
    def validate_statement(cls, v: str) -> str:
        """Ensure statement is a clear, testable hypothesis."""
        if not v or v.strip() == "":
            raise ValueError("Statement cannot be empty")

        # Check for question marks (hypothesis should be a statement, not a question)
        if v.strip().endswith('?'):
            raise ValueError("Hypothesis should be a statement, not a question")

        # Encourage predictive statements
        predictive_words = ['will', 'would', 'should', 'increases', 'decreases', 'affects', 'causes', 'leads to']
        if not any(word in v.lower() for word in predictive_words):
            # Warning but don't fail - some valid hypotheses might not use these words
            pass

        return v.strip()

    @field_validator('rationale')
    @classmethod
    def validate_rationale(cls, v: str) -> str:
        """Ensure rationale provides sufficient scientific justification."""
        if not v or v.strip() == "":
            raise ValueError("Rationale cannot be empty")

        if len(v.strip()) < 20:
            raise ValueError("Rationale must be at least 20 characters to provide sufficient justification")

        return v.strip()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage or serialization."""
        return {
            "id": self.id,
            "research_question": self.research_question,
            "statement": self.statement,
            "rationale": self.rationale,
            "domain": self.domain,
            "status": self.status.value,
            "testability_score": self.testability_score,
            "novelty_score": self.novelty_score,
            "confidence_score": self.confidence_score,
            "priority_score": self.priority_score,
            "suggested_experiment_types": [e.value for e in self.suggested_experiment_types],
            "estimated_resources": self.estimated_resources,
            "similar_work": self.similar_work,
            "novelty_report": self.novelty_report,
            "related_papers": self.related_papers,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "generated_by": self.generated_by,
            "parent_hypothesis_id": self.parent_hypothesis_id,
            "generation": self.generation,
            "refinement_count": self.refinement_count,
            "evolution_history": self.evolution_history,
        }

    def is_testable(self, threshold: float = 0.3) -> bool:
        """Check if hypothesis meets minimum testability threshold."""
        if self.testability_score is None:
            return False
        return self.testability_score >= threshold

    def is_novel(self, threshold: float = 0.5) -> bool:
        """Check if hypothesis meets minimum novelty threshold."""
        if self.novelty_score is None:
            return False
        return self.novelty_score >= threshold

    model_config = ConfigDict(use_enum_values=False)


class HypothesisGenerationRequest(BaseModel):
    """
    Request for hypothesis generation.

    Example:
        ```python
        request = HypothesisGenerationRequest(
            research_question="How does dark matter affect galaxy formation?",
            domain="astrophysics",
            num_hypotheses=3,
            context={"recent_papers": [...]}
        )
        ```
    """
    research_question: str = Field(..., min_length=10, description="Research question to generate hypotheses for")
    domain: Optional[str] = Field(None, description="Scientific domain (auto-detected if not provided)")
    num_hypotheses: int = Field(default=3, ge=1, le=10, description="Number of hypotheses to generate")

    # Optional context
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context (literature, data, etc.)")
    related_paper_ids: List[str] = Field(default_factory=list, description="Relevant paper IDs for context")

    # Generation parameters
    max_iterations: int = Field(default=1, ge=1, le=5, description="Max refinement iterations")
    require_novelty_check: bool = Field(default=True, description="Run novelty check before returning")
    min_novelty_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum novelty score")

    @field_validator('research_question')
    @classmethod
    def validate_question(cls, v: str) -> str:
        """Validate research question format."""
        if not v or v.strip() == "":
            raise ValueError("Research question cannot be empty")

        if len(v.strip()) < 10:
            raise ValueError("Research question must be at least 10 characters")

        return v.strip()


class HypothesisGenerationResponse(BaseModel):
    """
    Response from hypothesis generation.

    Contains generated hypotheses with metadata.
    """
    hypotheses: List[Hypothesis]
    research_question: str
    domain: str

    # Generation metadata
    generation_time_seconds: float
    num_papers_analyzed: int = 0
    model_used: str = _DEFAULT_CLAUDE_SONNET_MODEL

    # Quality metrics
    avg_novelty_score: Optional[float] = None
    avg_testability_score: Optional[float] = None

    def get_best_hypothesis(self) -> Optional[Hypothesis]:
        """Get highest priority hypothesis."""
        if not self.hypotheses:
            return None

        # Sort by priority score if available
        scored = [h for h in self.hypotheses if h.priority_score is not None]
        if scored:
            return max(scored, key=lambda h: h.priority_score)

        # Fallback: return first hypothesis
        return self.hypotheses[0]

    def filter_testable(self, threshold: float = 0.3) -> List[Hypothesis]:
        """Return only testable hypotheses."""
        return [h for h in self.hypotheses if h.is_testable(threshold)]

    def filter_novel(self, threshold: float = 0.5) -> List[Hypothesis]:
        """Return only novel hypotheses."""
        return [h for h in self.hypotheses if h.is_novel(threshold)]


class NoveltyReport(BaseModel):
    """
    Novelty analysis report for a hypothesis.

    Provides detailed analysis of how novel the hypothesis is.
    """
    hypothesis_id: str
    novelty_score: float = Field(..., ge=0.0, le=1.0, description="Overall novelty score")

    # Similar work detection
    similar_hypotheses: List[Dict[str, Any]] = Field(default_factory=list, description="Similar existing hypotheses")
    similar_papers: List[Dict[str, Any]] = Field(default_factory=list, description="Papers with similar claims")

    # Analysis details
    max_similarity: float = Field(0.0, ge=0.0, le=1.0, description="Highest similarity found")
    prior_art_detected: bool = Field(default=False, description="True if near-duplicate found")

    # Recommendations
    is_novel: bool = Field(..., description="Meets novelty threshold")
    novelty_threshold_used: float = 0.75
    summary: str = Field(..., description="Human-readable summary")

    generated_at: datetime = Field(default_factory=datetime.utcnow)


class TestabilityReport(BaseModel):
    """
    Testability analysis report for a hypothesis.

    Assesses whether and how the hypothesis can be tested.
    """
    hypothesis_id: str
    testability_score: float = Field(..., ge=0.0, le=1.0, description="Overall testability score")

    # Testability assessment
    is_testable: bool = Field(..., description="Meets testability threshold")
    testability_threshold_used: float = 0.3

    # Suggested experiment types
    suggested_experiments: List[Dict[str, Any]] = Field(default_factory=list, description="Ranked experiment types")
    primary_experiment_type: ExperimentType

    # Resource requirements
    estimated_compute_hours: Optional[float] = None
    estimated_cost_usd: Optional[float] = None
    estimated_duration_days: Optional[float] = None
    required_data_sources: List[str] = Field(default_factory=list)

    # Challenges
    challenges: List[str] = Field(default_factory=list, description="Implementation challenges")
    limitations: List[str] = Field(default_factory=list, description="Testing limitations")

    # Recommendations
    summary: str = Field(..., description="Human-readable summary")
    recommended: bool = Field(..., description="Recommended for testing")

    generated_at: datetime = Field(default_factory=datetime.utcnow)


class PrioritizedHypothesis(BaseModel):
    """
    Hypothesis with priority scoring.

    Used for ranking and selecting which hypotheses to test first.
    """
    hypothesis: Hypothesis
    priority_score: float = Field(..., ge=0.0, le=1.0, description="Overall priority score")

    # Component scores
    novelty_score: float = Field(..., ge=0.0, le=1.0)
    feasibility_score: float = Field(..., ge=0.0, le=1.0)
    impact_score: float = Field(..., ge=0.0, le=1.0)
    testability_score: float = Field(..., ge=0.0, le=1.0)

    # Scoring weights used
    weights: Dict[str, float] = Field(default_factory=lambda: {
        "novelty": 0.30,
        "feasibility": 0.25,
        "impact": 0.25,
        "testability": 0.20
    })

    # Ranking
    rank: Optional[int] = None

    # Justification
    priority_rationale: str = Field(..., description="Why this priority score")

    def update_hypothesis_priority(self) -> None:
        """Update the hypothesis object with this priority score."""
        self.hypothesis.priority_score = self.priority_score
        self.hypothesis.updated_at = datetime.utcnow()
