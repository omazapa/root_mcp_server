"""MCP server definition using the official MCP SDK.

This module exposes a FastMCP server object with two tools:
- run_python(code: str)
- run_cpp(code: str)

Both tools execute code in-process using PyROOT (via RootExecutor).
"""

from mcp.server import FastMCP
from root_mcp_server.executor import RootExecutor


# Initialize executor (will fail if PyROOT not available)
executor = RootExecutor()

# Create FastMCP server
server = FastMCP(name="root-mcp")


@server.tool(name="run_python", description="Execute Python code with PyROOT available in scope.")
def run_python(code: str):
    """Execute Python code; returns execution result as a dict."""
    return executor.run_python(code)


@server.tool(name="run_cpp", description="Execute C++ code via ROOT's cling interpreter.")
def run_cpp(code: str):
    """Execute C++/cling code; returns execution result as a dict."""
    return executor.run_cpp(code)


def get_tools():
    """Return tools metadata (FastMCP exposes tools automatically, helper kept for compatibility)."""
    return ["run_python", "run_cpp"]
