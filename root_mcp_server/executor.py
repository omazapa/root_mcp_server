"""Core MCP server for ROOT execution (Python and C++ via PyROOT)."""
# pylint: disable=no-member,broad-except
# ROOT module has dynamic attributes that pylint cannot detect

import io
import sys
import os
import tempfile
import contextlib
import traceback
from typing import Any, Dict, Optional
from dataclasses import asdict, dataclass

try:
    import ROOT  # type: ignore
except ImportError:
    ROOT = None  # type: ignore


@dataclass
class ExecutionResult:
    """Result of executing Python or C++ code."""

    ok: bool
    stdout: str
    stderr: str
    error: Optional[str] = None
    error_type: Optional[str] = None
    timed_out: bool = False


class RootExecutor:
    """Executes Python and C++ code using PyROOT in-process."""

    def __init__(self, enable_graphics=False):
        if ROOT is None:
            raise RuntimeError("PyROOT not available. Install ROOT")

        # Initialize TApplication to enable ROOT event loop
        # This is needed for certain ROOT operations even in batch mode
        if not ROOT.gApplication:  # type: ignore
            ROOT.TApplication("root_mcp", None, None)  # type: ignore

        # Set batch mode unless graphics explicitly enabled
        ROOT.gROOT.SetBatch(not enable_graphics)  # type: ignore

        # Enable implicit multi-threading if available (for better performance)
        try:
            if hasattr(ROOT, 'EnableImplicitMT'):
                ROOT.EnableImplicitMT()  # type: ignore
        except Exception:
            pass  # Not all ROOT builds have MT support

    def run_python(self, code: str) -> Dict[str, Any]:
        """Execute Python code with ROOT available in scope."""
        out_buf, err_buf = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(out_buf), contextlib.redirect_stderr(err_buf):
                globals_dict = {"ROOT": ROOT, "__name__": "__root_mcp__"}
                exec(code, globals_dict)  # pylint: disable=exec-used
            result = ExecutionResult(
                ok=True,
                stdout=out_buf.getvalue(),
                stderr=err_buf.getvalue(),
            )
        except Exception as e:  # pylint: disable=broad-except
            with contextlib.redirect_stdout(out_buf), contextlib.redirect_stderr(err_buf):
                traceback.print_exc()
            result = ExecutionResult(
                ok=False,
                stdout=out_buf.getvalue(),
                stderr=err_buf.getvalue(),
                error=str(e),
                error_type=type(e).__name__,
            )
        return asdict(result)

    def run_cpp(self, code: str) -> Dict[str, Any]:
        """Execute C++ code via ROOT's cling interpreter."""
        # Capture both Python and process-level stdout/stderr to avoid corrupting MCP stdio
        py_out, py_err = io.StringIO(), io.StringIO()
        tmp_out_fd, tmp_out_path = tempfile.mkstemp()
        tmp_err_fd, tmp_err_path = tempfile.mkstemp()

        # Save real stdout/stderr fds
        saved_stdout_fd = os.dup(1)
        saved_stderr_fd = os.dup(2)

        try:
            # Redirect OS-level fds 1 and 2 to our temp files
            os.dup2(tmp_out_fd, 1)
            os.dup2(tmp_err_fd, 2)

            with contextlib.redirect_stdout(py_out), contextlib.redirect_stderr(py_err):
                # ProcessLine returns 0 on success, non-zero on error
                ret_code = None
                try:
                    # Try Declare first (for multi-line declarations)
                    ROOT.gInterpreter.Declare(code)  # type: ignore
                    ret_code = 0  # Declare doesn't return a value, assume success if no exception
                except Exception:
                    # Fall back to ProcessLine which returns error code
                    ret_code = ROOT.gInterpreter.ProcessLine(code)  # type: ignore

            # Attempt to flush Python-level buffers
            try:
                sys.stdout.flush()
                sys.stderr.flush()
            except Exception:
                pass

            # Restore original fds before reading files (to not block server stdio)
            os.dup2(saved_stdout_fd, 1)
            os.dup2(saved_stderr_fd, 2)

            # Close temp fds before reading
            try:
                os.close(tmp_out_fd)
            except Exception:
                pass
            try:
                os.close(tmp_err_fd)
            except Exception:
                pass

            # Read captured OS-level outputs
            with open(tmp_out_path, "r", encoding="utf-8", errors="replace") as f:
                os_out = f.read()
            with open(tmp_err_path, "r", encoding="utf-8", errors="replace") as f:
                os_err = f.read()

            # Combine outputs
            combined_stdout = (py_out.getvalue() or "") + (os_out or "")
            combined_stderr = (py_err.getvalue() or "") + (os_err or "")

            # Check for errors: ret_code != 0 OR stderr contains error keywords
            error_keywords = ["error:", "Error:", "fatal error:"]
            has_stderr_error = any(keyword in combined_stderr for keyword in error_keywords)

            if ret_code != 0 or has_stderr_error:
                error_msg = (
                    f"C++ execution failed (return code: {ret_code})"
                    if ret_code != 0
                    else "C++ compilation error detected"
                )
                result = ExecutionResult(
                    ok=False,
                    stdout=combined_stdout,
                    stderr=combined_stderr,
                    error=error_msg,
                    error_type="ClingError",
                )
            else:
                result = ExecutionResult(
                    ok=True,
                    stdout=combined_stdout,
                    stderr=combined_stderr,
                )
        except Exception as e:
            # Ensure fds are restored on error
            try:
                os.dup2(saved_stdout_fd, 1)
                os.dup2(saved_stderr_fd, 2)
            except Exception:
                pass

            with contextlib.redirect_stdout(py_out), contextlib.redirect_stderr(py_err):
                traceback.print_exc()
            result = ExecutionResult(
                ok=False,
                stdout=py_out.getvalue(),
                stderr=py_err.getvalue(),
                error=str(e),
                error_type=type(e).__name__,
            )
        finally:
            # Close saved fds
            try:
                os.close(saved_stdout_fd)
            except Exception:
                pass
            try:
                os.close(saved_stderr_fd)
            except Exception:
                pass
            # Ensure temp fds are closed if not already
            try:
                os.close(tmp_out_fd)
            except Exception:
                pass
            try:
                os.close(tmp_err_fd)
            except Exception:
                pass
            # Clean up temp files
            try:
                os.unlink(tmp_out_path)
            except Exception:
                pass
            try:
                os.unlink(tmp_err_path)
            except Exception:
                pass

        return asdict(result)
