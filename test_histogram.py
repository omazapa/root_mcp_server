"""Test ROOT MCP server with histogram graphics."""

import asyncio
from mcp.client.stdio import stdio_client, StdioServerParameters

async def test_histogram():
    """Test histogram plotting with ROOT MCP server."""
    server_params = StdioServerParameters(
        command="/usr/bin/python3",
        args=["-m", "root_mcp_server.cli"],
        env=None
    )

    print("Launching root-mcp server with graphics enabled...")

    async with stdio_client(server_params) as (read, write):
        async with read:
            async with write:
                print("Connected. Creating histogram...")

                # Create and display histogram
                histogram_code = """
import ROOT
import time

# Create a histogram
h = ROOT.TH1F("h", "Gaussian Distribution", 100, -5, 5)

# Fill with random gaussian
for _ in range(10000):
    h.Fill(ROOT.gRandom.Gaus(0, 1))

# Create canvas and draw
c = ROOT.TCanvas("c", "Test Canvas", 800, 600)
h.Draw()
c.Update()

# Save to file
c.SaveAs("/tmp/test_histogram.png")
print("Histogram saved to /tmp/test_histogram.png")

# Keep window open for 5 seconds
time.sleep(5)
print("Done")
"""

                result = await write.call_tool("run_python", arguments={"code": histogram_code})
                print(f"\nResult: {result}")

                print("\nHistogram test completed!")

if __name__ == "__main__":
    asyncio.run(test_histogram())
