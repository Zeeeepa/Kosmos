"""
Code execution engine.

Executes generated Python code safely with output capture, error handling, and retry logic.
Supports both direct execution and Docker-based sandboxed execution.
"""

import sys
from kosmos.utils.compat import model_to_dict
import io
import traceback
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any, Optional
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

# Optional sandbox import
try:
    from kosmos.execution.sandbox import DockerSandbox, SandboxExecutionResult
    SANDBOX_AVAILABLE = True
except ImportError:
    SANDBOX_AVAILABLE = False
    logger.warning("Docker sandbox not available. Install docker package for sandboxed execution.")


class ExecutionResult:
    """Result of code execution."""

    def __init__(
        self,
        success: bool,
        return_value: Any = None,
        stdout: str = "",
        stderr: str = "",
        error: Optional[str] = None,
        error_type: Optional[str] = None,
        execution_time: float = 0.0,
        profile_result: Optional[Any] = None  # ProfileResult from kosmos.core.profiling
    ):
        self.success = success
        self.return_value = return_value
        self.stdout = stdout
        self.stderr = stderr
        self.error = error
        self.error_type = error_type
        self.execution_time = execution_time
        self.profile_result = profile_result

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            'success': self.success,
            'return_value': self.return_value,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'error': self.error,
            'error_type': self.error_type,
            'execution_time': self.execution_time
        }

        # Include profile data if available
        if self.profile_result:
            try:
                result['profile_data'] = model_to_dict(self.profile_result)
            except Exception as e:
                logger.debug("Failed to serialize profile data: %s", e)
                result['profile_data'] = None

        return result


class CodeExecutor:
    """
    Executes Python code with safety measures and output capture.

    Provides:
    - Stdout/stderr capture
    - Return value extraction
    - Error handling
    - Execution retry logic
    - Optional Docker sandbox isolation
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        allowed_globals: Optional[Dict[str, Any]] = None,
        use_sandbox: bool = False,
        sandbox_config: Optional[Dict[str, Any]] = None,
        enable_profiling: bool = False,
        profiling_mode: str = "light"
    ):
        """
        Initialize code executor.

        Args:
            max_retries: Maximum number of retry attempts on error
            retry_delay: Delay between retries in seconds
            allowed_globals: Optional dictionary of allowed global variables
            use_sandbox: If True, use Docker sandbox for execution
            sandbox_config: Optional sandbox configuration (cpu_limit, memory_limit, timeout)
            enable_profiling: If True, profile code execution (default: False)
            profiling_mode: Profiling mode: light, standard, full (default: light)
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.allowed_globals = allowed_globals or {}
        self.use_sandbox = use_sandbox
        self.sandbox_config = sandbox_config or {}
        self.enable_profiling = enable_profiling
        self.profiling_mode = profiling_mode

        # Initialize sandbox if requested
        self.sandbox = None
        if self.use_sandbox:
            if not SANDBOX_AVAILABLE:
                raise RuntimeError("Docker sandbox requested but not available. Install docker package.")

            self.sandbox = DockerSandbox(**self.sandbox_config)
            logger.info("Docker sandbox initialized for code execution")

    def execute(
        self,
        code: str,
        local_vars: Optional[Dict[str, Any]] = None,
        retry_on_error: bool = False
    ) -> ExecutionResult:
        """
        Execute Python code and capture results.

        Args:
            code: Python code to execute
            local_vars: Optional local variables to make available
            retry_on_error: If True, retry on execution errors

        Returns:
            ExecutionResult with output and results
        """
        attempt = 0
        last_error = None

        while attempt < (self.max_retries if retry_on_error else 1):
            attempt += 1

            try:
                logger.info(f"Executing code (attempt {attempt})")
                result = self._execute_once(code, local_vars)

                if result.success:
                    logger.info(f"Code executed successfully in {result.execution_time:.2f}s")
                    return result
                else:
                    last_error = result.error
                    if retry_on_error and attempt < self.max_retries:
                        logger.warning(f"Execution failed, retrying in {self.retry_delay}s...")
                        time.sleep(self.retry_delay)
                    else:
                        return result

            except Exception as e:
                logger.error(f"Unexpected error during execution: {e}")
                last_error = str(e)
                if retry_on_error and attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    return ExecutionResult(
                        success=False,
                        error=str(e),
                        error_type=type(e).__name__
                    )

        # All retries failed
        return ExecutionResult(
            success=False,
            error=f"Failed after {self.max_retries} attempts. Last error: {last_error}",
            error_type="MaxRetriesExceeded"
        )

    def _execute_once(
        self,
        code: str,
        local_vars: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """Execute code once with output capture and optional profiling."""

        # Route to sandbox if enabled
        if self.use_sandbox:
            return self._execute_in_sandbox(code, local_vars)

        # Initialize profiler if enabled
        profiler = None
        profile_result = None
        if self.enable_profiling:
            try:
                from kosmos.core.profiling import ExecutionProfiler, ProfilingMode
                mode = ProfilingMode(self.profiling_mode)
                profiler = ExecutionProfiler(mode=mode)
            except Exception as e:
                logger.warning(f"Failed to initialize profiler: {e}")

        # Otherwise execute directly
        start_time = time.time()

        # Prepare execution environment
        exec_globals = self._prepare_globals()
        exec_locals = local_vars.copy() if local_vars else {}

        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        try:
            # Start profiling if enabled
            if profiler:
                profiler._start_profiling()

            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Execute code
                exec(code, exec_globals, exec_locals)

            # Stop profiling if enabled
            if profiler:
                profiler._stop_profiling()
                profile_result = profiler.get_result()

            execution_time = time.time() - start_time

            # Extract return value (look for 'results' variable)
            return_value = exec_locals.get('results', exec_locals.get('result'))

            return ExecutionResult(
                success=True,
                return_value=return_value,
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue(),
                execution_time=execution_time,
                profile_result=profile_result
            )

        except Exception as e:
            # Stop profiling even on error
            if profiler:
                try:
                    profiler._stop_profiling()
                    profile_result = profiler.get_result()
                except Exception:
                    pass

            execution_time = time.time() - start_time

            # Capture full traceback
            error_traceback = traceback.format_exc()

            logger.error(f"Code execution failed: {e}\n{error_traceback}")

            return ExecutionResult(
                success=False,
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue() + "\n" + error_traceback,
                error=str(e),
                error_type=type(e).__name__,
                execution_time=execution_time,
                profile_result=profile_result
            )

    def _execute_in_sandbox(
        self,
        code: str,
        local_vars: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """Execute code in Docker sandbox."""
        logger.info("Executing code in Docker sandbox")

        # Prepare data files if data_path provided
        data_files = {}
        if local_vars and 'data_path' in local_vars:
            data_path = local_vars['data_path']
            # Extract filename from path
            import os
            filename = os.path.basename(data_path)
            data_files[filename] = data_path

            # Update code to use mounted data file
            code = f"data_path = '/workspace/data/{filename}'\n{code}"

        # Execute in sandbox
        sandbox_result = self.sandbox.execute(code, data_files=data_files if data_files else None)

        # Convert SandboxExecutionResult to ExecutionResult
        return ExecutionResult(
            success=sandbox_result.success,
            return_value=sandbox_result.return_value,
            stdout=sandbox_result.stdout,
            stderr=sandbox_result.stderr,
            error=sandbox_result.error,
            error_type=sandbox_result.error_type,
            execution_time=sandbox_result.execution_time
        )

    def _prepare_globals(self) -> Dict[str, Any]:
        """Prepare global namespace for code execution."""
        # Start with allowed globals
        exec_globals = self.allowed_globals.copy()

        # Add standard builtins
        exec_globals['__builtins__'] = __builtins__

        return exec_globals

    def execute_with_data(
        self,
        code: str,
        data_path: str,
        retry_on_error: bool = False
    ) -> ExecutionResult:
        """
        Execute code with data file path provided.

        Args:
            code: Python code to execute (expects `data_path` variable)
            data_path: Path to data file (made available as variable)
            retry_on_error: If True, retry on errors

        Returns:
            ExecutionResult

        Note:
            The data_path variable is prepended to code and also provided
            in local_vars for templates that use `pd.read_csv(data_path)`.
        """
        # Prepend data_path assignment so templates can use it (Issue #51)
        # This ensures data_path is defined even if templates use it directly
        augmented_code = f"# Data path injected by executor\ndata_path = {repr(data_path)}\n\n{code}"

        # Also inject as local variable for safety
        local_vars = {'data_path': data_path}

        return self.execute(augmented_code, local_vars, retry_on_error)


class CodeValidator:
    """
    Validates generated code for safety and correctness.

    Checks for:
    - Syntax errors
    - Dangerous imports
    - Dangerous operations
    """

    # Dangerous modules that should not be imported
    DANGEROUS_MODULES = [
        'os', 'subprocess', 'sys', 'shutil', 'importlib',
        'socket', 'urllib', 'requests', 'http',
        '__import__', 'eval', 'exec', 'compile'
    ]

    # Dangerous functions/operations
    DANGEROUS_PATTERNS = [
        'open(',  # File operations (except specific allowed cases)
        'eval(',
        'exec(',
        'compile(',
        '__import__',
        'globals(',
        'locals(',
        'vars(',
    ]

    @staticmethod
    def validate(code: str, allow_file_read: bool = True) -> Dict[str, Any]:
        """
        Validate code for safety.

        Args:
            code: Python code to validate
            allow_file_read: If True, allow read-only file operations

        Returns:
            Dictionary with:
                - valid: Boolean
                - errors: List of error messages
                - warnings: List of warning messages
        """
        errors = []
        warnings = []

        # Check syntax
        try:
            import ast
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Syntax error: {e}")
            return {'valid': False, 'errors': errors, 'warnings': warnings}

        # Check for dangerous imports
        for module in CodeValidator.DANGEROUS_MODULES:
            if f"import {module}" in code or f"from {module}" in code:
                errors.append(f"Dangerous import detected: {module}")

        # Check for dangerous patterns
        for pattern in CodeValidator.DANGEROUS_PATTERNS:
            if pattern in code:
                # Special case: allow open() for reading if permitted
                if pattern == 'open(' and allow_file_read:
                    # Check if it's read-only (contains "'r'" or no mode specified)
                    if "'w'" in code or "'a'" in code or "'x'" in code or "mode='w'" in code:
                        errors.append(f"Dangerous operation detected: write mode file operations")
                    else:
                        warnings.append(f"File read operation detected: {pattern}")
                else:
                    errors.append(f"Dangerous operation detected: {pattern}")

        # Check for network operations
        network_keywords = ['socket', 'http', 'urllib', 'requests', 'api']
        for keyword in network_keywords:
            if keyword in code.lower():
                warnings.append(f"Potential network operation detected: {keyword}")

        is_valid = len(errors) == 0

        logger.info(f"Code validation: {'PASSED' if is_valid else 'FAILED'}, "
                   f"{len(errors)} errors, {len(warnings)} warnings")

        return {
            'valid': is_valid,
            'errors': errors,
            'warnings': warnings
        }


class RetryStrategy:
    """
    Strategy for retrying failed code execution.

    Provides different retry approaches:
    - Simple retry (same code)
    - Modified retry (with error feedback)
    - LLM-assisted retry (if LLM available)
    """

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        """
        Initialize retry strategy.

        Args:
            max_retries: Maximum retry attempts
            base_delay: Base delay between retries (exponential backoff)
        """
        self.max_retries = max_retries
        self.base_delay = base_delay

    def should_retry(self, attempt: int, error_type: str) -> bool:
        """Determine if execution should be retried."""
        if attempt >= self.max_retries:
            return False

        # Don't retry on certain errors
        non_retryable_errors = [
            'SyntaxError',
            'ImportError',
            'ModuleNotFoundError'
        ]

        return error_type not in non_retryable_errors

    def get_delay(self, attempt: int) -> float:
        """Get delay for retry attempt (exponential backoff)."""
        return self.base_delay * (2 ** (attempt - 1))

    def modify_code_for_retry(
        self,
        original_code: str,
        error: str,
        attempt: int
    ) -> Optional[str]:
        """
        Modify code based on error for retry.

        Args:
            original_code: Original code that failed
            error: Error message
            attempt: Retry attempt number

        Returns:
            Modified code or None if no modification strategy
        """
        # Simple modifications based on common errors
        modified_code = original_code

        # Add error handling for common issues
        if 'KeyError' in error:
            # Wrap in try-except
            modified_code = f"""try:
{original_code}
except KeyError as e:
    print(f"KeyError: {{e}}. Using default value.")
    results = {{'error': 'KeyError', 'details': str(e)}}
"""

        elif 'FileNotFoundError' in error:
            # Add existence check
            modified_code = f"""import os
if not os.path.exists('data.csv'):
    print("Data file not found, using dummy data")
    import pandas as pd
    df = pd.DataFrame()
else:
{original_code}
"""

        else:
            # No specific modification
            return None

        return modified_code


def execute_protocol_code(
    code: str,
    data_path: Optional[str] = None,
    max_retries: int = 2,
    validate_safety: bool = True,
    use_sandbox: bool = False,
    sandbox_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to execute protocol code with full pipeline.

    Args:
        code: Generated code to execute
        data_path: Optional path to data file
        max_retries: Maximum retry attempts
        validate_safety: If True, validate code safety first
        use_sandbox: If True, execute in Docker sandbox
        sandbox_config: Optional sandbox configuration

    Returns:
        Dictionary with execution results
    """
    # Validate code if requested
    if validate_safety:
        validation = CodeValidator.validate(code, allow_file_read=True)
        if not validation['valid']:
            return {
                'success': False,
                'error': 'Code validation failed',
                'validation_errors': validation['errors'],
                'validation_warnings': validation['warnings']
            }

    # Execute code
    executor = CodeExecutor(
        max_retries=max_retries,
        use_sandbox=use_sandbox,
        sandbox_config=sandbox_config or {}
    )

    if data_path:
        result = executor.execute_with_data(code, data_path, retry_on_error=True)
    else:
        result = executor.execute(code, retry_on_error=True)

    # Convert to dict and add validation info
    result_dict = result.to_dict()
    if validate_safety:
        result_dict['validation_warnings'] = validation.get('warnings', [])

    return result_dict
