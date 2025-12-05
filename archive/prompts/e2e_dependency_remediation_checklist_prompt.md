# Prompt: Generate E2E Dependency Remediation Checklist

## Purpose

Generate a comprehensive, trackable checklist for fixing all dependencies required to bring Kosmos E2E testing to production state. This is a **living document** designed for multi-week execution with clear milestones and progress tracking.

---

## Prerequisites

Before running this prompt, ensure you have generated:
1. `E2E_TESTING_DEPENDENCY_REPORT.md` - Dependency analysis (Step 1)
2. `E2E_TESTING_IMPLEMENTATION_PLAN.md` - Implementation plan (Step 2)

---

## Reference Files to Read

**From Previous Steps (READ FIRST):**
1. **`E2E_TESTING_DEPENDENCY_REPORT.md`** - Dependency analysis
   - Section 6.6: Dependency → Blocked Tests Matrix
   - Section 6.7: Fix Sequencing Dependencies
2. **`E2E_TESTING_IMPLEMENTATION_PLAN.md`** - Implementation plan
   - Appendix A: Fix → Test Unlock Map (use this for "Tests Unlocked" in checklist)
   - Recommended Fix Order

**Skill Documentation:**
3. **`.claude/skills/kosmos-e2e-testing/SKILL.md`** - Skill capabilities and known issues
4. **`.claude/skills/kosmos-e2e-testing/reference.md`** - Environment variables and configuration

**Project Files:**
5. **`pyproject.toml`** - Package dependencies
6. **`docker-compose.yml`** - Service definitions (if exists)

---

## Output Document Structure

Generate `E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md` with this structure:

```markdown
# Kosmos E2E Dependency Remediation Checklist

**Generated:** [date]
**Target:** Production-ready E2E testing
**Estimated Total Effort:** [X days/weeks]
**Current State:** [from dependency report: mock_only/api_only/partial_e2e/full_e2e]
**Target State:** full_e2e

---

## Progress Overview

| Milestone | Status | Target Date | Actual Date |
|-----------|--------|-------------|-------------|
| M1: Environment Setup | ⬜ Not Started | | |
| M2: Core Services Running | ⬜ Not Started | | |
| M3: All APIs Configured | ⬜ Not Started | | |
| M4: Docker Sandbox Ready | ⬜ Not Started | | |
| M5: Full E2E Passing | ⬜ Not Started | | |

**Legend:** ⬜ Not Started | 🔄 In Progress | ✅ Complete | ❌ Blocked

---

## Milestone 1: Environment Setup
**Goal:** Python environment and core packages working
**Unlocks:** Sanity tests, basic imports

### 1.1 Python Version
- [ ] **Verify Python version**
  ```bash
  python --version
  # Required: 3.10.x recommended (3.11+ has arxiv compatibility issues)
  ```
  - Current: [version from report]
  - Action needed: [yes/no]
  - If yes: [specific instructions]

### 1.2 Core Package Installation
- [ ] **Install core dependencies**
  ```bash
  pip install -e ".[dev]"
  ```
  - Verification:
    ```bash
    python -c "import kosmos; print('OK')"
    ```

### 1.3 Package Compatibility Fixes
For each problematic package from the dependency report:

- [ ] **Fix: [package name]**
  - Issue: [from dependency report]
  - Solution:
    ```bash
    [specific fix command]
    ```
  - Verification:
    ```bash
    python -c "import [package]; print('OK')"
    ```
  - Tests unlocked: [list]

### Milestone 1 Verification
```bash
# Run sanity tests
./scripts/run-tests.sh sanity
# OR
pytest tests/smoke/test_imports.py -v
```
- [ ] All imports pass
- [ ] Sanity tests green

---

## Milestone 2: Core Services Running
**Goal:** Database and basic services operational
**Unlocks:** Smoke tests, unit tests with DB

### 2.1 SQLite Database
- [ ] **Initialize database**
  ```bash
  # Check if exists
  ls -la kosmos.db

  # If not, initialize
  alembic upgrade head
  ```
  - Verification:
    ```bash
    sqlite3 kosmos.db ".tables"
    ```

### 2.2 Neo4j Setup (Optional but recommended)
- [ ] **Start Neo4j**
  ```bash
  # Option A: Docker
  docker run -d \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password \
    neo4j:latest

  # Option B: Docker Compose (if available)
  docker compose up -d neo4j
  ```
- [ ] **Configure environment**
  ```bash
  export NEO4J_URI=bolt://localhost:7687
  export NEO4J_USER=neo4j
  export NEO4J_PASSWORD=password
  ```
- [ ] **Add to .env file**
  ```bash
  echo "NEO4J_URI=bolt://localhost:7687" >> .env
  echo "NEO4J_USER=neo4j" >> .env
  echo "NEO4J_PASSWORD=password" >> .env
  ```
  - Verification:
    ```bash
    nc -zv localhost 7687
    # OR
    curl http://localhost:7474
    ```
  - Tests unlocked: Knowledge graph tests

### 2.3 Redis Setup (Optional)
- [ ] **Start Redis**
  ```bash
  # Option A: Docker
  docker run -d --name redis -p 6379:6379 redis:latest

  # Option B: Docker Compose
  docker compose up -d redis
  ```
- [ ] **Configure environment**
  ```bash
  export REDIS_URL=redis://localhost:6379/0
  echo "REDIS_URL=redis://localhost:6379/0" >> .env
  ```
  - Verification:
    ```bash
    redis-cli ping
    # Expected: PONG
    ```
  - Tests unlocked: Cache tests

### 2.4 ChromaDB Setup
- [ ] **Install ChromaDB**
  ```bash
  pip install chromadb
  ```
- [ ] **Configure persist directory**
  ```bash
  export CHROMA_PERSIST_DIRECTORY=./chroma_db
  mkdir -p ./chroma_db
  echo "CHROMA_PERSIST_DIRECTORY=./chroma_db" >> .env
  ```
  - Verification:
    ```bash
    python -c "import chromadb; c = chromadb.Client(); print('OK')"
    ```
  - Tests unlocked: Vector DB tests, semantic search

### Milestone 2 Verification
```bash
# Run smoke tests
./scripts/run-tests.sh smoke
# OR
pytest tests/smoke/ tests/unit/ -v --ignore=tests/unit/execution
```
- [ ] Database accessible
- [ ] Smoke tests green

---

## Milestone 3: All APIs Configured
**Goal:** LLM providers and external APIs working
**Unlocks:** Integration tests, real LLM calls

### 3.1 LLM Provider Setup

#### Option A: Local Ollama (Recommended for development)
- [ ] **Install Ollama**
  ```bash
  # Linux
  curl -fsSL https://ollama.com/install.sh | sh

  # Start service
  ollama serve
  ```
- [ ] **Pull required models**
  ```bash
  ollama pull qwen3:4b        # Fast model for sanity/smoke
  ollama pull deepseek-r1:8b  # Reasoning model for E2E
  ```
- [ ] **Configure environment**
  ```bash
  export LLM_PROVIDER=openai
  export OPENAI_API_KEY=ollama
  export OPENAI_BASE_URL=http://localhost:11434/v1
  export OPENAI_MODEL=qwen3:4b
  ```
  - Verification:
    ```bash
    curl http://localhost:11434/api/tags
    ```

#### Option B: Anthropic API
- [ ] **Set API key**
  ```bash
  export ANTHROPIC_API_KEY=sk-ant-...
  export LLM_PROVIDER=anthropic
  echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
  echo "LLM_PROVIDER=anthropic" >> .env
  ```
  - Verification:
    ```bash
    python -c "import anthropic; c = anthropic.Anthropic(); print('OK')"
    ```

#### Option C: OpenAI API
- [ ] **Set API key**
  ```bash
  export OPENAI_API_KEY=sk-...
  export LLM_PROVIDER=openai
  echo "OPENAI_API_KEY=sk-..." >> .env
  echo "LLM_PROVIDER=openai" >> .env
  ```

### 3.2 External API Keys

- [ ] **Semantic Scholar API** (optional, improves literature search)
  ```bash
  # Get key from: https://www.semanticscholar.org/product/api
  export SEMANTIC_SCHOLAR_API_KEY=...
  echo "SEMANTIC_SCHOLAR_API_KEY=..." >> .env
  ```
  - Tests unlocked: Literature search with rate limits

### Milestone 3 Verification
```bash
# Run integration tests
pytest -m integration -v

# Or test LLM connectivity
python -c "
from kosmos.core.llm import get_llm_client
client = get_llm_client()
print('LLM client initialized:', type(client))
"
```
- [ ] LLM provider responds
- [ ] Integration tests green

---

## Milestone 4: Docker Sandbox Ready
**Goal:** Secure code execution environment for Gap 4
**Unlocks:** E2E tests, full workflow tests

### 4.1 Docker Installation
- [ ] **Verify Docker installed and running**
  ```bash
  docker info
  docker --version
  ```
  - If not installed: [Install Docker](https://docs.docker.com/engine/install/)

### 4.2 Build Sandbox Image
- [ ] **Run setup script**
  ```bash
  ./.claude/skills/kosmos-e2e-testing/scripts/setup-docker.sh
  ```
  - OR manual build:
    ```bash
    cd docker/sandbox
    docker build -t kosmos-sandbox:latest .
    ```
- [ ] **Verify image**
  ```bash
  docker images | grep kosmos-sandbox
  docker run --rm kosmos-sandbox:latest python3 -c "import pandas; print('OK')"
  ```

### 4.3 Configure Execution Environment
- [ ] **Set environment variables**
  ```bash
  export ENABLE_SANDBOXING=true
  export KOSMOS_SANDBOX_IMAGE=kosmos-sandbox:latest
  export MAX_EXPERIMENT_EXECUTION_TIME=300
  echo "ENABLE_SANDBOXING=true" >> .env
  ```

### Milestone 4 Verification
```bash
# Run E2E tests
./scripts/run-tests.sh e2e

# Or test sandbox directly
python -c "
from kosmos.execution.production_executor import ProductionExecutor, ProductionConfig
import asyncio

async def test():
    config = ProductionConfig(timeout_seconds=30)
    executor = ProductionExecutor(config)
    await executor.initialize()
    result = await executor.execute_code('print(1+1)')
    print('Sandbox result:', result)
    await executor.cleanup()

asyncio.run(test())
"
```
- [ ] Sandbox container runs
- [ ] Code execution works
- [ ] E2E tests green

---

## Milestone 5: Full E2E Passing
**Goal:** All tests passing, production ready
**Unlocks:** Full confidence in system

### 5.1 Run Full Test Suite
- [ ] **Execute all tests**
  ```bash
  ./scripts/run-tests.sh full
  # OR
  pytest tests/ -v --cov=kosmos --cov-report=html
  ```

### 5.2 Fix Remaining Failures
For each failing test:
- [ ] **Test:** `[test_file::test_name]`
  - Error: [error message]
  - Fix: [specific fix]
  - Verification: `pytest [test_file::test_name] -v`

### 5.3 Coverage Verification
- [ ] **Check coverage**
  ```bash
  pytest --cov=kosmos --cov-report=term-missing
  ```
  - Target: >70% coverage
  - Current: [X]%

### 5.4 Full Workflow Validation
- [ ] **Run complete research workflow**
  ```bash
  kosmos run "Test research question about LLM efficiency" --cycles 1
  ```
  - All 6 gaps exercised
  - Report generated
  - No errors

### Milestone 5 Verification
```bash
# Final validation
./scripts/run-tests.sh full
echo "Exit code: $?"
```
- [ ] All tests passing
- [ ] Coverage threshold met
- [ ] Full workflow completes

---

## Quick Reference: Environment Variables

Copy this to your `.env` file and fill in values:

```bash
# LLM Provider (required - choose one)
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=
# OR
LLM_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_BASE_URL=http://localhost:11434/v1  # For Ollama
OPENAI_MODEL=qwen3:4b

# Database
DATABASE_URL=sqlite:///kosmos.db

# Neo4j (optional)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./chroma_db

# External APIs (optional)
SEMANTIC_SCHOLAR_API_KEY=

# Execution
ENABLE_SANDBOXING=true
KOSMOS_SANDBOX_IMAGE=kosmos-sandbox:latest
MAX_EXPERIMENT_EXECUTION_TIME=300

# Testing
TEST_MODE=false
```

---

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| `arxiv` import fails | Use Python 3.10 or mock arxiv |
| Docker permission denied | `sudo usermod -aG docker $USER` then re-login |
| Neo4j connection refused | Check if container is running: `docker ps` |
| Ollama not responding | Start service: `ollama serve` |
| API rate limits | Add delays or use local Ollama |
| Tests timeout | Increase timeout: `pytest --timeout=900` |

---

## Progress Log

Use this section to track your daily progress:

### [Date]
- Completed:
- Blocked by:
- Next:

### [Date]
- Completed:
- Blocked by:
- Next:

---

## Notes

[Add any project-specific notes, workarounds, or decisions here]

---

*Generated by Kosmos E2E Testing - Dependency Remediation Checklist Prompt*
```

---

## Instructions

1. **Read both previous outputs thoroughly:**
   - `E2E_TESTING_DEPENDENCY_REPORT.md` (Step 1) - what's broken
   - `E2E_TESTING_IMPLEMENTATION_PLAN.md` (Step 2) - fix priorities and test mappings
2. **Use the Fix → Test Unlock Map** from Step 2's Appendix A to populate "Tests unlocked" for each checklist item
3. **Use the Fix Sequencing Dependencies** from Step 1's Section 6.7 to order checklist items correctly
4. **Cross-reference** with the skill documentation for accurate commands
5. **Generate** the checklist following the structure above
6. **Customize** based on actual findings:
   - Remove items that are already working
   - Add items specific to issues found
   - Adjust verification commands for the actual environment
   - Use effort estimates from Step 2
7. **Be specific** - every item should have:
   - Exact commands to run
   - Verification steps
   - What tests it unlocks (from Step 2)
   - Dependencies on other fixes (from Step 1)
8. **Include time estimates** from Step 2's Fix → Test Unlock Map

---

## Key Principles

1. **Milestone-based** - Clear checkpoints to measure progress
2. **Verifiable** - Every step has a verification command
3. **Trackable** - Checkboxes and progress log for multi-week execution
4. **Sequenced** - Dependencies between items are respected
5. **Actionable** - Copy-paste commands, no ambiguity
6. **Living document** - Progress log section for ongoing updates

---

## When to Run This Prompt

- **After** generating the dependency report (Step 1)
- **After** generating the implementation plan (Step 2) - so you know which fixes unlock which tests
- **Before** starting the actual remediation work

The output checklist becomes your execution guide for the coming weeks.
