# Prompt: Create Comprehensive End-to-End Testing Plan for Kosmos AI Scientist

## Context

You are creating an end-to-end (E2E) testing plan for **Kosmos**, an open-source implementation of an autonomous AI scientist system based on the paper "Kosmos: An AI Scientist for Autonomous Discovery" (Lu et al., 2024). The system autonomously generates hypotheses, designs experiments, executes code, analyzes results, and produces publication-quality research reports.

The project implements 6 critical gaps that were unspecified in the original paper:
- **Gap 0**: Context Compression (hierarchical 3-tier achieving 20:1 ratio)
- **Gap 1**: State Manager (hybrid 4-layer artifact architecture)
- **Gap 2**: Task Generation (Plan Creator/Reviewer orchestration)
- **Gap 3**: Agent Integration (skill loader with 566 domain-specific prompts)
- **Gap 4**: Execution Environment (Docker-based Jupyter sandbox with pooling)
- **Gap 5**: Discovery Validation (ScholarEval 8-dimension quality framework)

**Current Status**: 339 unit tests passing, but E2E integration testing is the explicit next step. Many existing E2E tests are skipped due to missing dependencies or complex setup requirements.

---

## System Architecture

### Core Components

```
kosmos/
├── compression/           # Gap 0: ContextCompressor
│   ├── notebook_compressor.py    # Compress 42K notebooks → 2-line summary
│   └── literature_compressor.py  # Compress 1,500 papers
│
├── world_model/           # Gap 1: State Management
│   ├── artifacts.py       # ArtifactStateManager (JSON artifacts)
│   ├── models.py          # Pydantic schemas
│   └── simple.py          # SimpleWorldModel in-memory fallback
│
├── orchestration/         # Gap 2: Task Generation
│   ├── plan_creator.py    # PlanCreatorAgent (generates 10 tasks/cycle)
│   ├── plan_reviewer.py   # PlanReviewerAgent (5-dimension scoring)
│   ├── delegation.py      # DelegationManager (routes tasks to agents)
│   └── novelty_detector.py # NoveltyDetector (prevents redundancy)
│
├── agents/                # Gap 3: Agent System
│   ├── research_director.py      # Master orchestrator
│   ├── hypothesis_generator.py   # HypothesisGeneratorAgent
│   ├── experiment_designer.py    # ExperimentDesignerAgent
│   ├── data_analyst.py           # DataAnalystAgent
│   ├── skill_loader.py           # SkillLoader (566 prompts)
│   └── registry.py               # Agent registration
│
├── execution/             # Gap 4: Code Execution
│   ├── production_executor.py    # ProductionExecutor (unified interface)
│   ├── docker_manager.py         # DockerManager (container pooling)
│   ├── jupyter_client.py         # JupyterClient (kernel gateway)
│   ├── package_resolver.py       # PackageResolver (auto-dependencies)
│   ├── executor.py               # CodeExecutor (direct execution)
│   └── sandbox.py                # Security constraints
│
├── validation/            # Gap 5: Discovery Validation
│   └── scholar_eval.py    # ScholarEvalValidator (8-dimension scoring)
│
├── workflow/              # Integration Layer
│   └── research_loop.py   # ResearchWorkflow (main orchestration)
│
├── core/                  # LLM & Utilities
│   ├── llm.py             # Multi-provider LLM interface
│   ├── providers/         # Anthropic, OpenAI, Factory
│   ├── async_llm.py       # Async LLM operations
│   ├── cache.py           # Response caching
│   ├── logging.py         # Structured logging
│   └── convergence.py     # Research stopping logic
│
├── literature/            # Literature Search
│   ├── arxiv_client.py    # arXiv integration
│   ├── pubmed_client.py   # PubMed integration
│   ├── semantic_scholar.py # Semantic Scholar API
│   └── unified_search.py  # Multi-source search
│
├── knowledge/             # Knowledge Management
│   ├── vector_db.py       # ChromaDB integration
│   ├── embeddings.py      # SPECTER embeddings
│   └── graph.py           # Neo4j knowledge graphs
│
├── domains/               # Domain-Specific (biology, neuroscience, materials, etc.)
│
├── safety/                # Security
│   └── code_validator.py  # CodeValidator (blocks dangerous code)
│
├── cli/                   # Command-Line Interface
│   ├── main.py            # Typer app
│   └── commands/          # run, status, cache, config, etc.
│
└── db/                    # Database
    ├── models.py          # SQLAlchemy ORM
    └── operations.py      # CRUD operations
```

### Data Flow

```
Research Objective (user input)
        ↓
ResearchWorkflow.run()
        ↓
┌───────────────────────────────────────────────────────────────┐
│  FOR EACH CYCLE (1 to num_cycles):                            │
│                                                               │
│  1. Gap 1: StateManager.get_cycle_context()                   │
│     → Retrieve prior findings, hypotheses, statistics         │
│                                                               │
│  2. Gap 2: PlanCreator.create_plan()                          │
│     → Generate 10 tasks with exploration/exploitation ratio   │
│                                                               │
│  3. Gap 2: NoveltyDetector.check_plan_novelty()               │
│     → Filter redundant analyses                               │
│                                                               │
│  4. Gap 2: PlanReviewer.review_plan()                         │
│     → 5-dimension scoring (specificity, relevance, novelty,   │
│        coverage, feasibility)                                 │
│     → If rejected: revise once and re-review                  │
│                                                               │
│  5. Gap 2: DelegationManager.execute_plan()                   │
│     → Route tasks to appropriate agents                       │
│     → FOR EACH TASK:                                          │
│         a. Gap 3: SkillLoader.load_skills_for_task()          │
│         b. Agent execution (hypothesis/experiment/analysis)   │
│         c. Gap 4: ProductionExecutor.execute_code()           │
│         d. Gap 0: ContextCompressor.compress_result()         │
│         e. Gap 5: ScholarEvalValidator.evaluate_finding()     │
│         f. Gap 1: StateManager.save_finding_artifact()        │
│                                                               │
│  6. Gap 0: ContextCompressor.compress_cycle_results()         │
│     → Hierarchical compression for next cycle context         │
│                                                               │
│  7. Gap 1: StateManager.get_statistics()                      │
│     → Update tracking metrics                                 │
└───────────────────────────────────────────────────────────────┘
        ↓
ResearchWorkflow.generate_report()
        ↓
Publication-ready Markdown report
```

---

## Entry Points

### 1. Python API (Primary)

```python
from kosmos.workflow.research_loop import ResearchWorkflow

workflow = ResearchWorkflow(
    research_objective="Investigate KRAS mutations in cancer drug resistance",
    anthropic_client=client,  # Or None for mock mode
    artifacts_dir="./artifacts",
    max_cycles=20
)

result = await workflow.run(num_cycles=5, tasks_per_cycle=10)
# Returns: {cycles_completed, total_tasks_generated, total_tasks_completed,
#           task_completion_rate, validated_findings, validation_rate, total_time}

report = await workflow.generate_report()
# Returns: Markdown string with research findings
```

### 2. CLI Commands

```bash
kosmos run "Research question here" [--cycles N] [--tasks N]
kosmos status [--verbose]
kosmos cache [show|clear]
kosmos config [show|validate]
kosmos history [list|search]
kosmos profile [analyze|export]
kosmos graph [build|query]
```

### 3. ResearchDirectorAgent (Alternative Entry)

```python
from kosmos.agents.research_director import ResearchDirectorAgent

director = ResearchDirectorAgent(
    research_question="...",
    domain="biology",
    config={"max_iterations": 10}
)

result = director.execute({"action": "start_research"})
status = director.get_research_status()
```

---

## External Dependencies

### Required
| Service | Purpose | Mock Available |
|---------|---------|----------------|
| Anthropic Claude OR OpenAI | LLM inference | Yes (mock_llm_client fixture) |
| SQLite/PostgreSQL | Persistent storage | Yes (in-memory SQLite) |

### Optional (Enhance Functionality)
| Service | Purpose | Mock Available |
|---------|---------|----------------|
| Docker | Sandboxed code execution (Gap 4) | Yes (CodeExecutor with use_sandbox=False) |
| Neo4j | Knowledge graph queries | Yes (mock_knowledge_graph fixture) |
| Redis | Distributed caching | Yes (in-memory cache fallback) |
| Semantic Scholar API | Literature search | Yes (fixture with sample data) |
| PubMed API | Biomedical literature | Yes (fixture with sample XML) |
| arXiv API | Computer science papers | Yes (fixture with sample XML) |
| ChromaDB | Vector embeddings | Yes (mock_vector_db fixture) |

---

## Configuration (Environment Variables)

### Critical Settings
```bash
# LLM Provider (required)
LLM_PROVIDER=anthropic|openai
ANTHROPIC_API_KEY=sk-ant-...  # Or "999999999999999999999999999999999999999999999999" for CLI mode
OPENAI_API_KEY=sk-...

# Database
DATABASE_URL=sqlite:///kosmos.db  # Or postgresql://...

# Execution
ENABLE_SANDBOXING=true|false
MAX_EXPERIMENT_EXECUTION_TIME=300

# Research
MAX_RESEARCH_ITERATIONS=10
RESEARCH_BUDGET_USD=10.0
ENABLED_DOMAINS=biology,physics,chemistry,neuroscience
MIN_NOVELTY_SCORE=0.6

# Performance
ENABLE_CONCURRENT_OPERATIONS=true|false
MAX_CONCURRENT_EXPERIMENTS=4
PARALLEL_EXPERIMENTS=0  # 0 = sequential

# Testing
TEST_MODE=true|false

# Database Services (Optional)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=...

# Cache
REDIS_URL=redis://localhost:6379/0

# Vector DB
CHROMA_PERSIST_DIRECTORY=./chroma_db

# External APIs
SEMANTIC_SCHOLAR_API_KEY=...
```

---

## Known Issues & Limitations

1. **arxiv package incompatibility**: Fails on Python 3.11+ due to `sgmllib3k` dependency. Literature search features limited.

2. **Docker requirement**: Gap 4 execution environment requires Docker. Without it, code execution uses mock/direct implementations.

3. **Database model issues**: Some tests skip due to "Hypothesis model ID missing autoincrement=True" - model definition issue.

4. **Complex agent setup**: Some agents (ExperimentDesigner, DataAnalyst) require complex object initialization.

5. **API mismatches**: Some integration tests have API mismatches with current implementation.

6. **No R support**: Paper references R packages; implementation is Python-only.

7. **Single-user**: No multi-tenancy or user isolation.

---

## Existing Test Infrastructure

### Test Frameworks
- pytest (test runner)
- pytest-asyncio (async test support)
- pytest-cov (coverage)
- pytest-mock (mocking)
- responses (HTTP mocking)
- freezegun (datetime mocking)

### Key Fixtures (from conftest.py)
```python
# File/path fixtures
temp_dir, temp_file, fixtures_dir

# Mock fixtures
mock_llm_client, mock_anthropic_client
mock_knowledge_graph, mock_vector_db
mock_cache, mock_concept_extractor

# Gap module mocks
mock_context_compressor
mock_artifact_state_manager
mock_skill_loader
mock_scholar_eval_validator
mock_plan_creator, mock_plan_reviewer
mock_delegation_manager, mock_novelty_detector

# Sample data
sample_research_finding, sample_research_hypothesis
sample_research_plan, sample_paper_metadata
```

### Test Markers
```python
@pytest.mark.e2e           # End-to-end tests
@pytest.mark.slow          # Slow tests
@pytest.mark.integration   # Integration tests
@pytest.mark.docker        # Requires Docker
@pytest.mark.requires_api_key
@pytest.mark.requires_neo4j
@pytest.mark.requires_claude
@pytest.mark.unit          # Unit tests
@pytest.mark.smoke         # Smoke tests
```

---

## Test Scenarios to Cover

### 1. Complete Research Workflow (Happy Path)
- Single-cycle research execution
- Multi-cycle research (3, 5, 10, 20 cycles)
- Different task counts per cycle (5, 10, 15, 20)
- Report generation after workflow completion

### 2. Gap Module Integration
- Gap 0 ↔ Gap 1: Compressed context flows to state manager
- Gap 1 ↔ Gap 2: State manager provides context to plan creator
- Gap 2 ↔ Gap 3: Delegation manager routes to agents with skills
- Gap 3 ↔ Gap 4: Agents generate code executed in sandbox
- Gap 4 ↔ Gap 5: Execution results validated by ScholarEval
- Gap 5 ↔ Gap 1: Validated findings persisted to state manager

### 3. Domain-Specific Workflows
- Biology research (KRAS mutations, gene expression)
- Neuroscience research (neural pathways, memory)
- Materials science research
- Cross-domain research questions

### 4. Error Handling & Recovery
- LLM API failures (rate limits, timeouts, errors)
- Code execution failures (syntax errors, runtime errors, timeouts)
- Validation failures (findings rejected by ScholarEval)
- Cycle failures (individual cycles fail, workflow continues)
- Network failures (literature API unavailable)

### 5. Edge Cases
- Empty research objective
- Very long research objective
- Research objective in non-English language
- No testable hypotheses generated
- All findings rejected by validation
- Maximum iterations reached without convergence
- Zero tasks per cycle
- Concurrent operation conflicts

### 6. Performance & Scalability
- Time to complete N cycles
- Memory usage over extended runs
- Cache effectiveness (hit rates)
- Parallel vs sequential execution speedup
- Large artifact storage (100+ findings)

### 7. CLI Workflows
- `kosmos run` with various options
- `kosmos status` during and after research
- `kosmos cache` operations
- `kosmos config` validation
- `kosmos history` queries

### 8. Configuration Variations
- Different LLM providers (Anthropic, OpenAI, Ollama)
- With/without Docker sandboxing
- With/without Neo4j knowledge graph
- With/without Redis caching
- Different domain configurations

### 9. Data Persistence & Recovery
- Workflow resume after interruption
- State manager artifact integrity
- Database transaction rollback on errors
- Artifact file corruption handling

### 10. Security & Safety
- Code validator blocks dangerous code
- Resource limits enforced (memory, CPU, timeout)
- Network isolation in sandbox
- No arbitrary file system access

---

## Test Environment Configurations

### Tier 1: Minimal (CI-friendly, no external services)
- Mock LLM responses
- In-memory SQLite
- Direct code execution (no Docker)
- No Redis, no Neo4j
- Sample fixture data for literature
- **Test command:** `./scripts/run-tests.sh sanity`

### Tier 2: Smoke (Component validation)
- Mock LLM responses
- SQLite database
- Direct code execution
- Basic component checks
- **Test command:** `./scripts/run-tests.sh smoke`

### Tier 3: Integration (requires API keys, mocked services)
- Real LLM calls (Anthropic or OpenAI or local Ollama)
- SQLite database
- Direct code execution
- Mocked Neo4j, Redis, ChromaDB
- **Test command:** `pytest -m integration`

### Tier 4: Full E2E (requires Docker + all services)
- Real LLM calls
- PostgreSQL database
- Docker sandboxed execution
- Neo4j knowledge graph
- Redis caching
- Real literature API calls
- **Test command:** `./scripts/run-tests.sh e2e` or `./scripts/run-tests.sh full`

---

## Success Criteria

### Functional
- [ ] Complete research workflow executes without errors
- [ ] All 6 gap modules integrate correctly
- [ ] Findings are validated and persisted
- [ ] Reports are generated with correct structure
- [ ] CLI commands execute successfully

### Performance
- [ ] Single cycle completes in < 60 seconds (mock mode)
- [ ] 5 cycles complete in < 5 minutes (real LLM)
- [ ] Memory usage stays under 2GB for 20 cycles
- [ ] No memory leaks over extended runs

### Reliability
- [ ] Workflow recovers from individual cycle failures
- [ ] No data loss on interruption
- [ ] Proper cleanup on error conditions
- [ ] Singleton reset between tests

### Coverage
- [ ] All entry points tested (API, CLI, agents)
- [ ] All gap modules tested in integration
- [ ] All supported domains tested
- [ ] All configuration variations tested

---

## Deliverables Expected

1. **Test Implementation Plan**: Prioritized list of E2E tests to implement
2. **Test Code**: pytest-based test files with async support
3. **Fixtures**: Reusable fixtures for E2E scenarios
4. **Configuration**: Test environment setup scripts
5. **CI Integration**: GitHub Actions workflow for E2E tests
6. **Documentation**: Test execution guide and troubleshooting

---

## Instructions

Using the comprehensive context provided above, create a detailed end-to-end testing plan for the Kosmos AI Scientist system. Your plan should:

1. **Prioritize tests** by risk and business value (critical paths first)
2. **Define test cases** with clear preconditions, steps, and expected outcomes
3. **Specify mock strategies** for external dependencies
4. **Include test data requirements** (fixtures, sample research questions)
5. **Address all 6 gap modules** and their integrations
6. **Cover both happy paths and error scenarios**
7. **Consider different test tiers** (minimal, integration, full)
8. **Provide realistic time estimates** for implementation
9. **Include CI/CD integration recommendations**
10. **Define success metrics** and acceptance criteria

Focus on tests that will catch real integration issues between the gap modules while remaining practical to implement and maintain. The goal is to validate that the complete autonomous research workflow functions correctly from research question input to publication-ready report output.
