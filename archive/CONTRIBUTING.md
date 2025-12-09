# Contributing to Kosmos

Thank you for your interest in contributing to Kosmos!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/jimmc414/Kosmos.git
   cd Kosmos
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```

3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Verify setup:
   ```bash
   kosmos doctor
   ```

## Code Standards

### Python Style

- Follow PEP 8
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use f-strings for string formatting (or %-style for logger calls)

### Logging

- Use module-level logger: `logger = logging.getLogger(__name__)`
- Never use bare `except:` - always specify exception type
- Always log exceptions before silent fallback:

  ```python
  except Exception as e:
      logger.debug("Context message: %s", e)
      # fallback behavior
  ```

### Exception Handling

- Catch specific exceptions when possible
- Log context before re-raising or falling back
- Use WARNING for recoverable issues that indicate problems
- Use DEBUG for expected fallbacks in optional features

### Debug Logging Patterns

When adding debug logging gated by config flags:

```python
# Check config flag
try:
    from kosmos.config import get_config
    if get_config().logging.log_feature_name:
        logger.debug("[PREFIX] Message: %s", value)
except Exception:
    pass  # Config not available
```

## Testing

### Running Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# E2E tests (requires Docker)
pytest tests/e2e/ -v

# With coverage
pytest --cov=kosmos --cov-report=html
```

### Writing Tests

- Place unit tests in `tests/unit/<module>/test_<file>.py`
- Use pytest fixtures from `conftest.py`
- Mock external services (LLM, database, Docker)
- Follow AAA pattern: Arrange, Act, Assert

Example test structure:
```python
def test_feature_does_something(mock_llm_client):
    # Arrange
    agent = SomeAgent(client=mock_llm_client)

    # Act
    result = agent.do_something()

    # Assert
    assert result.status == "success"
```

## Pull Request Process

1. Create feature branch from `master`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make changes with tests

3. Run tests and ensure all pass:
   ```bash
   pytest tests/unit/ tests/integration/ -v
   ```

4. Update documentation if needed

5. Submit PR with clear description:
   - What the change does
   - Why it's needed
   - How to test it

## Debug Mode

When debugging issues, use trace mode for maximum visibility:

```bash
kosmos run --trace --objective "..." --max-iterations 2
```

This enables all debug logging including:
- `[LLM]` - LLM call details (model, tokens, latency)
- `[MSG]` - Agent message routing
- `[WORKFLOW]` - State machine transitions
- `[DECISION]` - Research director decisions
- `[ITER]` - Per-iteration summaries

## Code Review Checklist

Before submitting, ensure:
- [ ] No bare `except:` clauses
- [ ] All exceptions are logged before silent handling
- [ ] Type hints on all public functions
- [ ] Tests for new functionality
- [ ] Documentation updated if needed

## Questions?

Open an issue for questions or suggestions.
