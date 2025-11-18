"""MCP server definition using the official MCP SDK.

This module exposes a FastMCP server object with two tools:
- root_python(code: str)
- root_cpp(code: str)

Both tools execute code in-process using PyROOT (via RootExecutor).
"""

import asyncio
import sys
from mcp.server import FastMCP
from root_mcp_server.executor import RootExecutor


# Initialize executor with graphics enabled to keep ROOT objects alive
executor = RootExecutor(enable_graphics=True)

# Create FastMCP server
server = FastMCP(name="root-mcp")


@server.tool(name="root_python", description="Execute Python code with PyROOT available in scope.")
async def root_python(code: str):
    """Execute Python code; returns execution result as a dict.

    Args:
        code: Python code to execute (ROOT is automatically available)
    """
    # Log code execution to stderr (MCP console)
    print("\n" + "="*60, file=sys.stderr)
    print("EXECUTING PYTHON CODE:", file=sys.stderr)
    for i, line in enumerate(code.split('\n'), 1):
        print(f"{i:3d} | {line}", file=sys.stderr)
    print("="*60, file=sys.stderr)

    # Run blocking executor in thread pool to avoid blocking the event loop
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, executor.run_python, code)

    # Log execution result
    if result.get('ok'):
        print("✓ EXECUTION SUCCESS", file=sys.stderr)
    else:
        print("❌ EXECUTION FAILED", file=sys.stderr)
        print(f"Error: {result.get('error')}", file=sys.stderr)
        print(f"Type: {result.get('error_type')}", file=sys.stderr)

    if result.get('stdout'):
        print(f"STDOUT:\n{result.get('stdout')}", file=sys.stderr)
    if result.get('stderr'):
        print(f"STDERR:\n{result.get('stderr')}", file=sys.stderr)
    print("", file=sys.stderr)

    return result


@server.tool(name="root_cpp", description="Execute C++ code via ROOT's cling interpreter.")
async def root_cpp(code: str):
    """Execute C++/cling code; returns execution result as a dict.

    Args:
        code: C++ code to execute via ROOT.gInterpreter
    """
    # Log code execution to stderr (MCP console)
    print("\n" + "="*60, file=sys.stderr)
    print("EXECUTING C++ CODE:", file=sys.stderr)
    for i, line in enumerate(code.split('\n'), 1):
        print(f"{i:3d} | {line}", file=sys.stderr)
    print("="*60, file=sys.stderr)

    # Run blocking executor in thread pool to avoid blocking the event loop
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, executor.run_cpp, code)

    # Log execution result
    if result.get('ok'):
        print("✓ EXECUTION SUCCESS", file=sys.stderr)
    else:
        print("❌ EXECUTION FAILED", file=sys.stderr)
        print(f"Error: {result.get('error')}", file=sys.stderr)
        print(f"Type: {result.get('error_type')}", file=sys.stderr)

    if result.get('stdout'):
        print(f"STDOUT:\n{result.get('stdout')}", file=sys.stderr)
    if result.get('stderr'):
        print(f"STDERR:\n{result.get('stderr')}", file=sys.stderr)
    print("", file=sys.stderr)

    return result


def get_tools():
    """Return tools metadata (FastMCP exposes tools automatically, helper kept for compatibility)."""
    return ["root_python", "root_cpp"]
