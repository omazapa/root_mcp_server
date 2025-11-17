# root-mcp: MCP Server for ROOT

Minimal MCP (Model Context Protocol) server that allows Claude (or any MCP client) to execute Python and C++ code directly using PyROOT, without HTTP endpoints or external APIs.

## Features

- **Direct Python execution**: Run Python code with PyROOT available automatically
- **Direct C++ execution**: Run C++ code via ROOT's cling interpreter
- **In-process**: All code runs in the same process (no subprocess isolation)
- **CLI via MCP SDK**: Use the official `mcp[cli]` SDK for easy client integration

## Installation

Install the package with its CLI dependencies:

```bash
pip install -e '.[cli]'
# Or directly:
pip install -e .
```

Note: This package assumes PyROOT is available. If using the Snap version of ROOT:

```bash
/snap/bin/root-framework.pyroot -m pip install -e '.[cli]'
```

## Usage

### Start the MCP server

```bash
root-mcp
```

Or with the snap interpreter:

```bash
/snap/bin/root-framework.pyroot -m root_mcp_server.cli
```

### Tools available

The server exposes two tools:

1. **`run_python`**: Execute Python code with `ROOT` in scope
2. **`run_cpp`**: Execute C++ code via `ROOT.gInterpreter`

Both return `{ok: bool, stdout: str, stderr: str, error: str|null}`.
