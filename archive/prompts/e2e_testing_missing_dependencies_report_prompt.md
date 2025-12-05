# Prompt: Analyze Missing Dependencies for Effective End-to-End Testing

## Objective

Analyze the Kosmos AI Scientist codebase to produce a comprehensive report identifying all missing dependencies, configuration gaps, and environmental requirements that are preventing effective end-to-end (E2E) testing. The report should provide actionable remediation steps for each identified issue.

---

## Skill Integration

The Kosmos E2E testing skill can automatically generate a dependency report using:

```bash
# Generate E2E_TESTING_DEPENDENCY_REPORT.md
python -c "from lib.report_generator import generate_dependency_report; generate_dependency_report()"
```

This prompt provides guidance for manual analysis or when additional depth is needed beyond the automated report.

---

## Project Context

**Kosmos** is an autonomous AI scientist system implementing 6 critical gaps from the research paper "Kosmos: An AI Scientist for Autonomous Discovery" (Lu et al., 2024). The system has:
- 339 unit tests passing
- Many E2E and integration tests skipped or failing due to missing dependencies
- Complex external service requirements (LLM providers, Docker, databases, APIs)

**Current Test Status Summary**:
- Unit Tests: 273 passing (gap modules)
- Integration Tests: 43 passing (many skipped)
- E2E Tests: 23 tests (most require API keys or Docker)
- Import Errors: ~10 test files fail to import due to transitive dependencies

---

## Known Skip Reasons (From Codebase Analysis)

### Category 1: Missing API Keys / Credentials

| Skip Condition | Environment Variable | Tests Affected |
|----------------|---------------------|----------------|
| `not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY")` | ANTHROPIC_API_KEY, OPENAI_API_KEY | 8+ E2E tests |
| `requires_api_key` marker | ANTHROPIC_API_KEY, SEMANTIC_SCHOLAR_API_KEY | Integration tests |
| `requires_claude` marker | ANTHROPIC_API_KEY | LiteratureAnalyzer, ConceptExtractor, HypothesisGenerator |
| `requires_neo4j` marker | NEO4J_URI | Knowledge graph tests |

### Category 2: Missing External Services

| Skip Reason | Service Required | Tests Affected |
|-------------|------------------|----------------|
| `"Docker daemon not available"` | Docker Engine | DockerManager, Sandbox, ProductionExecutor |
| `"Neo4j authentication not configured"` | Neo4j Database | KnowledgeGraph tests |
| `"ChromaDB not available"` | ChromaDB | VectorDB tests |
| `"Execution environment not available"` | Docker + Jupyter | All sandboxed execution tests |

### Category 3: Implementation/API Issues

| Skip Reason | Root Cause | Component |
|-------------|------------|-----------|
| `"PromptTemplate.format() internal framework issue - deferred to Phase 2"` | Framework mismatch | ExperimentDesigner |
| `"CodeGenerator requires ExperimentProtocol object - complex setup"` | Complex initialization | CodeGenerator |
| `"Sandbox API needs investigation"` | API not fully implemented | Sandbox execution |
| `"DataAnalysis module API needs deeper investigation - complex setup"` | API mismatch | StatisticalAnalysis |
| `"DataAnalyst agent API needs deeper investigation - complex setup"` | API mismatch | DataAnalystAgent |
| `"Hypothesis model ID missing autoincrement=True - model definition issue"` | SQLAlchemy model bug | Database persistence |
| `"ProfileData class not implemented (use ProfileResult instead)"` | Class mismatch | Profiling |
| `"CacheManager class not implemented"` | Missing implementation | Cache module |
| `"CacheEntry class not implemented"` | Missing implementation | Cache module |

### Category 4: Python Package Import Errors

| Package | Failure Reason | Tests Affected |
|---------|----------------|----------------|
| `arxiv` | `sgmllib3k` incompatibility with Python 3.11+ | arxiv_client, unified_search, citations, hypothesis_generator, literature_analyzer |
| `scipy` | Not installed or version conflict | guardrails, code_validator, verifier, reproducibility |
| `matplotlib` | Not installed | visualization tests |
| `plotly` | Not installed | analysis_pipeline (HTML export) |

### Category 5: Async/Concurrency Features Not Implemented

| Skip Reason | Missing Component | Phase |
|-------------|-------------------|-------|
| `"Requires Phase 2/3 async implementation (AsyncClaudeClient, ParallelExperimentExecutor)"` | AsyncClaudeClient, ParallelExperimentExecutor | Phase 2/3 |

---

## Dependency Categories to Analyze

### 1. Python Package Dependencies

Analyze `pyproject.toml` for:
- **Core dependencies** (required for basic operation)
- **Optional dependencies** ([dev], [test], [science], [execution], [monitoring])
- **Version conflicts** (NumPy 1.x vs 2.x, scipy pinning)
- **Platform-specific issues** (arxiv/sgmllib3k on Python 3.11+)

```toml
# Key sections to analyze:
dependencies = [...]                    # Core packages
[project.optional-dependencies]
dev = [...]                             # Development tools
test = [...]                            # Test framework
science = [...]                         # Heavy bioinformatics (scanpy, anndata)
execution = ["docker>=7.0.0"]           # Docker client
```

### 2. External Service Dependencies

| Service | Purpose | Required For | Configuration |
|---------|---------|--------------|---------------|
| **Anthropic API** | Claude LLM inference | All LLM calls | ANTHROPIC_API_KEY |
| **OpenAI API** | GPT inference (alternative) | All LLM calls | OPENAI_API_KEY |
| **Docker Engine** | Sandboxed code execution | Gap 4 tests | Docker daemon running |
| **Neo4j** | Knowledge graph storage | Graph queries | NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD |
| **Redis** | Distributed caching | Cache tests | REDIS_URL |
| **ChromaDB** | Vector embeddings | Semantic search | CHROMA_PERSIST_DIRECTORY |
| **PostgreSQL** | Production database | Full DB tests | DATABASE_URL |
| **Jupyter Kernel Gateway** | Code execution in containers | Sandbox execution | Docker + image |
| **Semantic Scholar** | Literature search | Literature tests | SEMANTIC_SCHOLAR_API_KEY |

### 3. Configuration Dependencies

Environment variables that must be set:

```bash
# Required (at least one LLM provider)
ANTHROPIC_API_KEY=sk-ant-...
# OR
OPENAI_API_KEY=sk-...

# Required for full functionality
DATABASE_URL=sqlite:///kosmos.db  # or postgresql://...

# Required for Gap 4 (Execution)
ENABLE_SANDBOXING=true  # Requires Docker

# Optional but affects test coverage
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=...
REDIS_URL=redis://localhost:6379/0
SEMANTIC_SCHOLAR_API_KEY=...
```

### 4. Infrastructure Dependencies

| Component | Requirement | Verification Command |
|-----------|-------------|---------------------|
| Docker Engine | Running daemon | `docker info` |
| Docker Compose | v2+ | `docker compose version` |
| Neo4j | Running instance | `nc -zv localhost 7687` |
| Redis | Running instance | `redis-cli ping` |
| PostgreSQL | Running instance | `pg_isready` |

### 5. Python Environment Dependencies

| Check | Purpose | Verification |
|-------|---------|--------------|
| Python version | Compatibility (3.10 recommended) | `python --version` |
| Package availability | Core packages installed | `pip list` |
| Version conflicts | NumPy, scipy versions | Check import errors |

**Known Python 3.11+ Issues:**
- `arxiv` package fails due to `sgmllib3k` incompatibility
- Some scipy sub-packages may have issues

### 6. Test Infrastructure Dependencies

```bash
# Test framework packages
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
pytest-timeout>=2.2.0
pytest-xdist>=3.5.0      # Parallel execution
responses>=0.24.0         # HTTP mocking
freezegun>=1.4.0          # DateTime mocking
faker>=22.0.0             # Fake data generation
```

---

## Analysis Tasks

### Task 1: Package Dependency Audit

For each test file with import errors:
1. Trace the import chain to identify the failing package
2. Determine if the package is in `dependencies` or `optional-dependencies`
3. Check for version conflicts
4. Verify Python version compatibility

**Expected Output**:
```
Test File: tests/unit/literature/test_arxiv_client.py
Import Error: ModuleNotFoundError: No module named 'sgmllib'
Root Cause: arxiv package depends on sgmllib3k which is incompatible with Python 3.11+
Package Location: pyproject.toml dependencies (line 61)
Remediation Options:
  1. Pin Python version to 3.10
  2. Use alternative arxiv client
  3. Mock arxiv module in tests
  4. Make arxiv an optional dependency
```

### Task 2: Service Availability Matrix

Create a matrix showing which tests require which services:

| Test Category | Anthropic | Docker | Neo4j | Redis | ChromaDB |
|---------------|-----------|--------|-------|-------|----------|
| Unit (gap modules) | Mock | No | No | No | No |
| Unit (literature) | Mock | No | No | No | No |
| Unit (knowledge) | Mock | No | Yes | No | Yes |
| Unit (execution) | No | Yes | No | No | No |
| Integration | Real/Mock | No | Mock | Mock | Mock |
| E2E | Real | Yes | Optional | Optional | Optional |

### Task 3: Configuration Gap Analysis

For each skipped test, identify:
1. Which environment variables are missing
2. Default values vs required values
3. Where the check occurs in code
4. Mock/bypass options

### Task 4: API Compatibility Audit

For tests skipped due to "API needs investigation":
1. Compare test expectations vs actual implementation
2. Identify method signature changes
3. Identify class/module restructuring
4. Propose test updates or implementation fixes

### Task 5: Transitive Dependency Analysis

For import errors caused by transitive dependencies:
1. Map the full import chain
2. Identify which source modules import problematic packages
3. Propose conditional imports or lazy loading
4. Identify test isolation strategies

---

## Report Structure

Generate a report with the following sections:

### Executive Summary
- Total tests blocked by dependencies
- Breakdown by category (packages, services, config, API issues)
- Estimated effort to resolve each category
- Priority recommendations

### Section 1: Python Package Issues
For each problematic package:
- Package name and version
- Where it's defined (pyproject.toml location)
- Which tests are affected
- Root cause analysis
- Remediation options with pros/cons

### Section 2: External Service Requirements
For each service:
- Service name and purpose
- Which tests require it
- Configuration requirements
- Docker Compose setup (if applicable)
- Mock alternatives available
- CI/CD implications

### Section 3: Configuration Gaps
For each missing configuration:
- Environment variable name
- Where it's checked
- Default behavior without it
- Tests affected
- Remediation (set value, mock, or make optional)

### Section 4: API/Implementation Issues
For each API mismatch:
- Test file and test name
- Expected API (what test assumes)
- Actual API (current implementation)
- Fix location (test or implementation)
- Estimated effort

### Section 4.5: Service Availability Matrix

The skill provides an automated service matrix via `get_service_matrix()`:

| Test Category | Anthropic | Docker | Neo4j | Redis | ChromaDB |
|---------------|-----------|--------|-------|-------|----------|
| unit_gap_modules | Mock | No | No | No | No |
| unit_literature | Mock | No | No | No | No |
| unit_knowledge | Mock | No | Yes | No | Yes |
| unit_execution | No | Yes | No | No | No |
| integration | Real/Mock | No | Mock | Mock | Mock |
| e2e | Real | Yes | Optional | Optional | Optional |

### Section 5: Dependency Resolution Strategy

#### Tier 1: Quick Wins (< 1 day)
- Install missing Python packages
- Set environment variables
- Add mocks for optional services

#### Tier 2: Medium Effort (1-3 days)
- Fix API mismatches in tests
- Add conditional imports
- Create Docker Compose test environment

#### Tier 3: Significant Work (> 3 days)
- Replace incompatible packages
- Implement missing features
- Refactor for better test isolation

### Section 6: CI/CD Recommendations
- GitHub Actions workflow configuration
- Test matrix (Python versions, dependency profiles)
- Service containers (Docker services for Neo4j, Redis, etc.)
- Secret management for API keys
- Test parallelization strategy

### Section 6.5: Recommended Test Tier

Based on infrastructure detection, the skill recommends:
- `full_e2e`: Has LLM + Docker + Neo4j
- `partial_e2e`: Has LLM + Docker
- `api_only`: Has LLM only
- `mock_only`: No external providers available

### Section 6.6: Dependency → Blocked Tests Matrix

For each dependency issue, map to affected tests:

| Dependency | Status | Blocked Test Files | Blocked Test Count | Priority |
|------------|--------|-------------------|-------------------|----------|
| ANTHROPIC_API_KEY | Missing | tests/e2e/*, tests/integration/* | ~15 | P0 |
| Docker | Not Running | tests/unit/execution/*, tests/e2e/* | ~10 | P0 |
| Neo4j | Not Configured | tests/unit/knowledge/test_graph.py | ~5 | P1 |
| arxiv package | Import Error | tests/unit/literature/test_arxiv*.py | ~8 | P2 |
| ... | ... | ... | ... | ... |

This matrix enables downstream tools to calculate fix priority by test impact.

### Section 6.7: Fix Sequencing Dependencies

Some fixes must be done in order:

```
Docker daemon running
    └── Before: Docker sandbox image build
            └── Before: ProductionExecutor tests

Python packages installed
    └── Before: Module import tests
            └── Before: Integration tests

LLM API key set
    └── Before: Real LLM tests
            └── Before: Full E2E workflow
```

### Section 7: Test Environment Profiles

Define clear profiles:

**Profile: Minimal (CI-friendly)**
```
Python packages: Core only
Services: None (all mocked)
Config: Minimal .env
Expected tests passing: ~300
```

**Profile: Integration**
```
Python packages: Core + test
Services: SQLite only
Config: API keys required
Expected tests passing: ~350
```

**Profile: Full**
```
Python packages: All optional
Services: Docker, Neo4j, Redis, PostgreSQL
Config: Full .env
Expected tests passing: ~400+
```

---

## Specific Files to Analyze

### Test Files with Skip Markers
```
tests/e2e/test_full_research_workflow.py
tests/e2e/test_system_sanity.py
tests/e2e/test_autonomous_research.py
tests/integration/test_concurrent_research.py
tests/integration/test_phase2_e2e.py
tests/integration/test_phase3_e2e.py
tests/unit/execution/test_docker_manager.py
tests/unit/knowledge/test_graph.py
tests/unit/knowledge/test_vector_db.py
tests/unit/knowledge/test_concept_extractor.py
tests/unit/agents/test_literature_analyzer.py
tests/unit/agents/test_hypothesis_generator.py
tests/unit/literature/test_semantic_scholar.py
tests/unit/core/test_profiling.py
tests/unit/core/test_cache.py
```

### Configuration Files
```
pyproject.toml           # Package dependencies
.env.example             # Environment variable template
tests/conftest.py        # Pytest fixtures and markers
docker-compose.yml       # Service definitions (if exists)
alembic.ini              # Database migration config
```

### Source Files with Conditional Imports
```
kosmos/core/llm.py
kosmos/execution/docker_manager.py
kosmos/knowledge/graph.py
kosmos/knowledge/vector_db.py
kosmos/literature/arxiv_client.py
```

---

## Validation Checklist

After generating the report, verify:

- [ ] All skipped tests are accounted for
- [ ] All import errors are traced to root cause
- [ ] Each remediation option is actionable
- [ ] CI/CD recommendations are implementable
- [ ] Test profiles are realistic and documented
- [ ] Priority ordering makes sense for the team
- [ ] Effort estimates are reasonable

---

## Output Format

Produce the report as a Markdown document with:
1. Clear section headings
2. Tables for structured data
3. Code blocks for configuration examples
4. Checkboxes for action items
5. Links to relevant source files (relative paths)

The report should be saved as `E2E_TESTING_DEPENDENCY_REPORT.md` in the project root.

**Note:** The skill can auto-generate this report:
```python
from lib.report_generator import generate_dependency_report
generate_dependency_report()  # Saves to E2E_TESTING_DEPENDENCY_REPORT.md
```

---

## Instructions

Using the context provided above and full access to the Kosmos codebase:

1. **Scan all test files** for skip markers, skipif conditions, and import errors
2. **Trace dependencies** from failing imports back to their source packages
3. **Check configuration** requirements against `.env.example` and actual code checks
4. **Identify service requirements** from test fixtures and production code
5. **Analyze API mismatches** between tests and current implementation
6. **Generate the comprehensive report** following the structure above
7. **Prioritize remediation steps** by impact and effort
8. **Provide CI/CD configuration** recommendations for automated testing

Focus on producing actionable findings that will enable the team to systematically resolve dependency issues and achieve comprehensive E2E test coverage.
