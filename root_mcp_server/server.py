"""MCP server definition using the official MCP SDK.

This module exposes a FastMCP server object with two tools:
- run_python(code: str)
- run_cpp(code: str)

Both tools execute code in-process using PyROOT (via RootExecutor).
"""

import asyncio
from mcp.server import FastMCP
from root_mcp_server.executor import RootExecutor


# Initialize executor (will fail if PyROOT not available)
executor = RootExecutor()

# Create FastMCP server
server = FastMCP(name="root-mcp")


@server.tool(name="run_python", description="Execute Python code with PyROOT available in scope.")
async def run_python(code: str):
    """Execute Python code; returns execution result as a dict.
    
    Args:
        code: Python code to execute (ROOT is automatically available)
    """
    # Run blocking executor in thread pool to avoid blocking the event loop
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, executor.run_python, code)


@server.tool(name="run_cpp", description="Execute C++ code via ROOT's cling interpreter.")
async def run_cpp(code: str):
    """Execute C++/cling code; returns execution result as a dict.
    
    Args:
        code: C++ code to execute via ROOT.gInterpreter
    """
    # Run blocking executor in thread pool to avoid blocking the event loop
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, executor.run_cpp, code)


def get_tools():
    """Return tools metadata (FastMCP exposes tools automatically, helper kept for compatibility)."""
    return ["run_python", "run_cpp"]
