#!/bin/bash
# Wrapper to run pytest with a timeout
TIMEOUT_DURATION="120s"
echo "Running pytest with timeout of $TIMEOUT_DURATION..."
# Use the pytest found in path
PYTEST_BIN=$(which pytest)
if [ -z "$PYTEST_BIN" ]; then
    # Fallback to known path if which fails
    PYTEST_BIN="/home/jim/miniconda3/envs/llm/bin/pytest"
fi

timeout $TIMEOUT_DURATION "$PYTEST_BIN" "$@"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 124 ]; then
  echo "ERROR: pytest timed out after $TIMEOUT_DURATION"
  # We exit with 0 or 1 depending on if we want to fail the build or just report
  # exiting with 124 is standard for timeout
  exit 124
fi

exit $EXIT_CODE
