# Kosmos E2E Testing Cheatsheet

Quick reference for running E2E tests on Kosmos with local and external providers.

---

## Using This Skill with Claude Code

This is a Claude Code skill. To use it, simply ask Claude Code questions using these trigger phrases:

| Trigger Phrase | What It Does |
|----------------|--------------|
| "kosmos test" | Run Kosmos tests with auto-detected provider |
| "kosmos e2e" | Set up and run E2E testing |
| "test workflow" | Test the ResearchWorkflow component |
| "local testing" | Configure local model testing |
| "provider switch" | Switch between test providers |
| "benchmark models" | Compare local vs API performance |
| "setup docker" | Set up Docker sandbox for Gap 4 |

### Example Prompts for Claude Code

```
"Run Kosmos E2E tests with local models"
"Set up E2E testing for Kosmos"
"Switch from local to Claude API for testing"
"Help me test the research workflow"
"What's the status of my testing infrastructure?"
"Run a quick sanity test on Kosmos"
```

### Skill Location

This skill is installed at: `.claude/skills/kosmos-e2e-testing/`

Related skill for model management: `~/.claude/skills/local-llm/`

---

## Quick Commands

```bash
# Health check - see what's available
./scripts/health-check.sh

# Run tests (auto-detect provider)
./scripts/run-tests.sh [tier]

# Run tests with specific provider
./scripts/run-tests.sh [tier] [provider]
```

---

## Test Tiers

| Command | Duration | What It Tests |
|---------|----------|---------------|
| `./scripts/run-tests.sh sanity` | ~30s | Basic imports, config |
| `./scripts/run-tests.sh smoke` | ~2min | Unit + smoke tests |
| `./scripts/run-tests.sh e2e` | ~10min | Full workflow |
| `./scripts/run-tests.sh full` | ~20min | Everything + coverage |

---

## Provider Options

| Provider | Command | Description |
|----------|---------|-------------|
| `auto` | `./scripts/run-tests.sh e2e auto` | Auto-detect best |
| `local-fast` | `./scripts/run-tests.sh e2e local-fast` | Qwen3 4B |
| `local-reasoning` | `./scripts/run-tests.sh e2e local-reasoning` | DeepSeek-R1 8B |
| `anthropic` | `./scripts/run-tests.sh e2e anthropic` | Claude API |
| `openai` | `./scripts/run-tests.sh e2e openai` | OpenAI/GPT-4 |

---

## Local Models (Ollama)

### Setup
```bash
# Pull models
ollama pull qwen3:4b          # Fast (30-40 tok/s, 2-3GB VRAM)
ollama pull deepseek-r1:8b    # Reasoning (6-7 tok/s, 5-6GB VRAM)

# Verify
ollama list
curl http://localhost:11434/api/tags
```

### Model Comparison
| Model | Speed | VRAM | Use For |
|-------|-------|------|---------|
| qwen3:4b | 30-40 tok/s | 2-3 GB | Sanity, smoke, iteration |
| deepseek-r1:8b | 6-7 tok/s | 5-6 GB | E2E, complex reasoning |

---

## Docker Sandbox (Gap 4)

```bash
# Auto-setup
./scripts/setup-docker.sh

# Manual build
cd docker/sandbox && docker build -t kosmos-sandbox:latest .

# Verify
docker run --rm kosmos-sandbox:latest python3 -c "import pandas; print('OK')"

# Check status
docker images | grep kosmos-sandbox
```

---

## Environment Variables

### Essential
```bash
# Local (Ollama)
export LLM_PROVIDER=openai
export OPENAI_API_KEY=ollama
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_MODEL=qwen3:4b

# Anthropic
export LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# OpenAI
export LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-...
```

### Source Config Files
```bash
source .claude/skills/kosmos-e2e-testing/configs/local-fast.env
source .claude/skills/kosmos-e2e-testing/configs/local-reasoning.env
source .claude/skills/kosmos-e2e-testing/configs/anthropic.env
```

---

## Pytest Commands

```bash
# Unit tests only
pytest tests/unit/ -v

# Smoke tests
pytest tests/smoke/ -v

# E2E tests
pytest tests/e2e/ -v -m e2e

# With timeout
pytest tests/e2e/ -v --timeout=600

# With coverage
pytest tests/ --cov=kosmos --cov-report=html

# Specific test file
pytest tests/e2e/test_autonomous_research.py -v

# Specific test class
pytest tests/e2e/test_autonomous_research.py::TestAutonomousResearchE2E -v
```

---

## Python API

```python
from lib.provider_detector import detect_all, recommend_test_tier
from lib.test_runner import run_tests
from lib.config_manager import switch_provider

# Check status
status = detect_all()
print(status)

# Get recommendation
tier = recommend_test_tier(status)

# Run tests
results = run_tests(tier='e2e', provider='local-reasoning')

# Switch provider
switch_provider('anthropic')
```

---

## Troubleshooting One-Liners

```bash
# Check Ollama
curl -s http://localhost:11434/api/tags | python3 -m json.tool

# Check Docker
docker info > /dev/null && echo "OK" || echo "Docker not running"

# Check sandbox
docker images | grep kosmos-sandbox

# Check API key
[ -n "$ANTHROPIC_API_KEY" ] && echo "Set" || echo "Not set"

# Start Ollama
ollama serve &

# Start Docker
sudo systemctl start docker

# Rebuild sandbox
docker rmi kosmos-sandbox:latest && ./scripts/setup-docker.sh
```

---

## Test Markers

| Marker | Command | Description |
|--------|---------|-------------|
| `e2e` | `pytest -m e2e` | End-to-end tests |
| `slow` | `pytest -m slow` | Long-running tests |
| `docker` | `pytest -m docker` | Require Docker |
| `unit` | `pytest -m unit` | Unit tests |
| `integration` | `pytest -m integration` | Integration tests |

---

## Workflow Testing

```python
import asyncio
from kosmos.workflow.research_loop import ResearchWorkflow

async def test_workflow():
    workflow = ResearchWorkflow(
        research_objective="Test question",
        artifacts_dir="./test_artifacts"
    )
    result = await workflow.run(num_cycles=1, tasks_per_cycle=2)
    print(f"Cycles: {result['cycles_completed']}")

asyncio.run(test_workflow())
```

---

## File Locations

| File | Purpose |
|------|---------|
| `.claude/skills/kosmos-e2e-testing/` | This skill |
| `~/.claude/skills/local-llm/` | Local model management |
| `tests/e2e/` | E2E test files |
| `tests/conftest.py` | Test fixtures |
| `docker/sandbox/` | Sandbox Dockerfile |
| `.env` | Environment config |

---

## Quick Recipes

### First Time Setup
```bash
# 1. Install models
ollama pull qwen3:4b && ollama pull deepseek-r1:8b

# 2. Setup Docker
./scripts/setup-docker.sh

# 3. Run sanity check
./scripts/run-tests.sh sanity
```

### Fast Iteration
```bash
# Quick sanity with fast model
./scripts/run-tests.sh sanity local-fast
```

### Full E2E Validation
```bash
# Complete E2E with reasoning model
./scripts/run-tests.sh e2e local-reasoning
```

### Production Validation
```bash
# Final check with external API
source configs/anthropic.env
./scripts/run-tests.sh full anthropic
```

---

*Generated for Kosmos E2E Testing Skill*
