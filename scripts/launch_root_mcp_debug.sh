#!/usr/bin/env bash
# Wrapper to start the MCP server under debugpy
set -euo pipefail

# Start Python with debugpy listening on port 5678 and wait for debugger to attach
/usr/bin/python3 -m debugpy --listen 5678 --wait-for-client -m root_mcp_server.cli
