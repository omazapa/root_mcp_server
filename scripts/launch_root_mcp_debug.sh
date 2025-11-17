#!/usr/bin/env bash
# Wrapper to source ROOT's thisroot.sh then start the MCP server under debugpy
# Adjust the path to thisroot.sh if your build dir differs
set -euo pipefail

THISROOT="/home/ozapatam/Projects/CERN/ROOT/root/build/bin/thisroot.sh"
if [ ! -f "$THISROOT" ]; then
  echo "thisroot.sh not found at $THISROOT" >&2
  exit 1
fi

# Source ROOT environment
# shellcheck disable=SC1090
source "$THISROOT"

# Start Python with debugpy listening on port 5678 and wait for debugger to attach
/usr/bin/python3 -m debugpy --listen 5678 --wait-for-client -m root_mcp_server.cli
