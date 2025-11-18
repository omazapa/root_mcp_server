#!/usr/bin/env python3
"""Test client to call the root-mcp server via MCP stdio transport."""
import asyncio
import sys
import os

# Ensure mcp is importable
try:
    from mcp.client.stdio import stdio_client, StdioServerParameters
    from mcp.client.session import ClientSession
except ImportError:
    print("ERROR: mcp package not installed. Run: pip install mcp[cli]", file=sys.stderr)
    sys.exit(1)


async def test_root_mcp():
    """Launch the MCP server and call run_python and run_cpp tools."""
    # Path to thisroot.sh (adjust if needed)
    thisroot = "/home/ozapatam/Projects/CERN/ROOT/root/build/bin/thisroot.sh"

    server_params = StdioServerParameters(
        command="bash",
        args=["-c", f"source {thisroot} && exec /usr/bin/python3 -m root_mcp_server.cli"],
        env=os.environ.copy()
    )

    print("Launching root-mcp server...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            print("Connected to server. Initializing...")
            await session.initialize()

            # List available tools
            print("\n=== Available tools ===")
            tools_response = await session.list_tools()
            for tool in tools_response.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Call run_python
            print("\n=== Calling run_python ===")
            python_code = "import ROOT; print(ROOT.gROOT.GetVersion())"
            result = await session.call_tool("run_python", arguments={"code": python_code})
            print(f"Result: {result}")

            # Call run_cpp
            print("\n=== Calling run_cpp ===")
            cpp_code = 'std::cout << "Hello from C++!" << std::endl;'
            result2 = await session.call_tool("run_cpp", arguments={"code": cpp_code})
            print(f"Result: {result2}")

    print("\nTest completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_root_mcp())
