"""CLI entry point for the root-mcp server.

Note: Do not print to stdout before/while the MCP stdio transport is active.
We write startup messages to stderr to avoid corrupting the protocol stream.
"""

import sys
from root_mcp_server.server import server


def main():
    """Start the MCP server in stdio mode for the agent to call tools.

    This script is the console entrypoint (console_scripts) installed by the package.
    """
    print("Starting root-mcp server (stdio)...", file=sys.stderr)
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
