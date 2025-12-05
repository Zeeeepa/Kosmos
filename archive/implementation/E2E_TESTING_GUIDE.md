# Kosmos End-to-End Testing Guide

This guide provides comprehensive instructions for setting up and running end-to-end tests for the Kosmos autonomous AI scientist system.

---

## Prerequisites

### Required Software

1. **Python 3.11+**
   ```bash
   python --version  # Should be 3.11 or higher
   ```

2. **Docker** (Critical for Gap 4 - Code Execution)
   ```bash
   # Install Docker (Ubuntu/Debian)
   sudo apt-get update
   sudo apt-get install docker.io docker-compose

   # Start Docker service
   sudo systemctl start docker
   sudo systemctl enable docker

   # Add user to docker group (avoid sudo)
   sudo usermod -aG docker $USER
   newgrp docker

   # Verify installation
   docker --version
   docker run hello-world
   ```

3. **Git**
   ```bash
   git --version
   ```

### Required API Keys

At least one of the following:

| Provider | Environment Variable | How to Obtain |
|----------|---------------------|---------------|
| Anthropic (recommended) | `ANTHROPIC_API_KEY` | https://console.anthropic.com/ |
| OpenAI | `OPENAI_API_KEY` | https://platform.openai.com/ |

**Optional but recommended:**
- `SEMANTIC_SCHOLAR_API_KEY` - Higher rate limits for literature search
- `PUBMED_API_KEY` - Higher rate limits for biomedical literature

---

## Setup Instructions

### Step 1: Clone and Install

```bash
# Clone repository
git clone https://github.com/jimmc414/Kosmos.git
cd Kosmos

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR: venv\Scripts\activate  # Windows

# Install in development mode
pip install -e ".[dev]"
```

### Step 2: Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit .env and set required values:
# - ANTHROPIC_API_KEY=sk-ant-...
# OR
# - OPENAI_API_KEY=sk-...
```

**Minimal .env for E2E testing:**
```bash
# LLM Provider
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key-here

# Database (SQLite for testing)
DATABASE_URL=sqlite:///kosmos_test.db

# Logging
LOG_LEVEL=INFO
```

### Step 3: Initialize Database

```bash
# Run database migrations
alembic upgrade head

# Verify
alembic current
```

### Step 4: Build Docker Sandbox (Critical)

```bash
# Navigate to sandbox directory
cd docker/sandbox

# Build the sandbox image
docker build -t kosmos-sandbox:latest .

# Verify image
docker images | grep kosmos-sandbox

# Test the sandbox
docker run --rm kosmos-sandbox:latest python3 -c "import pandas; import numpy; print('Sandbox OK')"

# Return to project root
cd ../..
```

### Step 5: Verify Setup

```bash
# Run the diagnostics command
python -c "
from kosmos.config import get_config
config = get_config()
print(f'LLM Provider: {config.llm_provider}')
print(f'Database: {config.database.url}')
missing = config.validate_dependencies()
if missing:
    print(f'Missing: {missing}')
else:
    print('All dependencies OK')
"
```

---

## Running E2E Tests

### Quick Verification (Smoke Tests)

```bash
# Run smoke tests first to verify basic functionality
pytest tests/smoke/ -v
```

**Expected output:** 7/7 passing

### Unit Tests (No API Keys Required)

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific gap tests
pytest tests/unit/compression/ -v      # Gap 0
pytest tests/unit/world_model/ -v      # Gap 1
pytest tests/unit/orchestration/ -v    # Gap 2
pytest tests/unit/agents/ -v           # Gap 3
pytest tests/unit/validation/ -v       # Gap 5
```

**Expected output:** 273/273 passing

### Integration Tests (Some Require API Keys)

```bash
# Run integration tests
pytest tests/integration/ -v

# Run with verbose output for debugging
pytest tests/integration/ -v --tb=long
```

**Expected output:** ~43/96 passing (some require external services)

### E2E Tests (Require Docker + API Keys)

```bash
# Run all E2E tests
pytest tests/e2e/ -v -m e2e

# Run specific E2E test files
pytest tests/e2e/test_autonomous_research.py -v
pytest tests/e2e/test_full_research_workflow.py -v
pytest tests/e2e/test_system_sanity.py -v

# Run with timeout (E2E tests can be slow)
pytest tests/e2e/ -v --timeout=300
```

**Expected output with proper setup:** 4/4 passing

### Full Test Suite

```bash
# Run everything with coverage
pytest tests/ -v --cov=kosmos --cov-report=html

# View coverage report
open htmlcov/index.html  # Mac
# OR: xdg-open htmlcov/index.html  # Linux
```

---

## Running a Live Research Workflow

### Minimal Test (1 cycle, 2 tasks)

```python
import asyncio
from kosmos.workflow.research_loop import ResearchWorkflow

async def test_minimal():
    workflow = ResearchWorkflow(
        research_objective="Test the relationship between temperature and enzyme activity",
        artifacts_dir="./test_artifacts"
    )

    result = await workflow.run(num_cycles=1, tasks_per_cycle=2)

    print(f"Cycles completed: {result['cycles_completed']}")
    print(f"Tasks generated: {result['total_tasks_generated']}")
    print(f"Validation rate: {result.get('validation_rate', 'N/A')}")

    # Generate report
    report = await workflow.generate_report()
    print(report)

asyncio.run(test_minimal())
```

### Using the CLI

```bash
# Basic run
kosmos run "Investigate KRAS mutations in cancer drug resistance" \
    --num-cycles 2 \
    --tasks-per-cycle 5

# With domain specification
kosmos run "How does temperature affect protein folding?" \
    --num-cycles 3 \
    --tasks-per-cycle 10 \
    --domain biology
```

---

## What to Expect

### Successful E2E Test Output

```
tests/e2e/test_autonomous_research.py::TestAutonomousResearchE2E::test_multi_cycle_autonomous_operation PASSED
tests/e2e/test_autonomous_research.py::TestAutonomousResearchE2E::test_component_integration PASSED
tests/e2e/test_autonomous_research.py::TestAutonomousResearchE2E::test_workflow_produces_report PASSED
tests/e2e/test_full_research_workflow.py::TestBiologyResearchWorkflow::test_full_biology_workflow PASSED
```

### Research Workflow Output

A successful run produces:
1. **Artifacts directory** with JSON state files
2. **Research report** in Markdown format
3. **Validated findings** with ScholarEval scores
4. **Execution metrics** (time, tasks, validation rate)

### Expected Timings

| Test Type | Duration |
|-----------|----------|
| Smoke tests | ~10 seconds |
| Unit tests | ~2 minutes |
| Integration tests | ~5 minutes |
| E2E tests | ~10-30 minutes |
| Full research cycle (5 cycles) | ~1-2 hours |

---

## Troubleshooting

### Docker Issues

**Error: "Docker not available"**
```bash
# Check Docker is running
sudo systemctl status docker

# Start Docker if needed
sudo systemctl start docker

# Verify sandbox image exists
docker images | grep kosmos-sandbox

# Rebuild if needed
cd docker/sandbox && docker build -t kosmos-sandbox:latest . && cd ../..
```

**Error: "Permission denied"**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### API Key Issues

**Error: "ANTHROPIC_API_KEY is required"**
```bash
# Verify environment variable is set
echo $ANTHROPIC_API_KEY

# Or check .env file
cat .env | grep ANTHROPIC_API_KEY
```

**Error: "Invalid API key"**
- Verify the key is correct at https://console.anthropic.com/
- Check for trailing whitespace in .env file

### Database Issues

**Error: "No such table"**
```bash
# Run migrations
alembic upgrade head

# Or reset database
rm kosmos.db kosmos_test.db
alembic upgrade head
```

### Import Issues

**Error: "ModuleNotFoundError: No module named 'kosmos'"**
```bash
# Ensure package is installed
pip install -e .

# Verify installation
pip show kosmos
```

**Error: "arxiv package not available"**
This is expected on Python 3.11+. The system will fall back to Semantic Scholar for literature search.

### Test Failures

**Integration tests failing**
```bash
# Run with verbose output
pytest tests/integration/ -v --tb=long

# Skip tests requiring external services
pytest tests/integration/ -v -m "not requires_api"
```

**E2E tests timing out**
```bash
# Increase timeout
pytest tests/e2e/ -v --timeout=600

# Or run individual tests
pytest tests/e2e/test_autonomous_research.py::TestAutonomousResearchE2E::test_multi_cycle_autonomous_operation -v
```

---

## Test Categories and Markers

| Marker | Description | Command |
|--------|-------------|---------|
| `unit` | Unit tests (no external deps) | `pytest -m unit` |
| `integration` | Integration tests | `pytest -m integration` |
| `e2e` | End-to-end tests | `pytest -m e2e` |
| `slow` | Long-running tests | `pytest -m slow` |
| `docker` | Tests requiring Docker | `pytest -m docker` |

---

## Checklist for E2E Testing

### Before Running E2E Tests

- [ ] Python 3.11+ installed
- [ ] Virtual environment activated
- [ ] Package installed (`pip install -e .`)
- [ ] `.env` file configured with API key
- [ ] Database migrations applied (`alembic upgrade head`)
- [ ] Docker installed and running
- [ ] Docker sandbox image built (`kosmos-sandbox:latest`)
- [ ] Smoke tests pass (`pytest tests/smoke/ -v`)
- [ ] Unit tests pass (`pytest tests/unit/ -v`)

### Running E2E Tests

- [ ] Integration tests reviewed (`pytest tests/integration/ -v`)
- [ ] E2E tests executed (`pytest tests/e2e/ -v -m e2e`)
- [ ] Results documented

### Post-Test Verification

- [ ] Check artifacts directory for outputs
- [ ] Review generated reports
- [ ] Verify database contains expected records
- [ ] Check logs for errors (`tail -f kosmos.log`)

---

## Additional Resources

- **README.md** - Project overview and quick start
- **CODE_REVIEW_REPORT_1125.md** - Detailed code review findings
- **docs/** - Additional documentation
- **tests/requirements/** - Test requirement specifications

---

## Support

If you encounter issues:
1. Check this guide's troubleshooting section
2. Review the code review report for known issues
3. Open an issue at https://github.com/jimmc414/Kosmos/issues

---

*Last updated: 2025-11-25*
