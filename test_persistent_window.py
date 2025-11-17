#!/usr/bin/env python3
"""Test that ROOT graphics objects persist after execution."""
import asyncio
import sys

try:
    from mcp.client.stdio import stdio_client, StdioServerParameters
    from mcp.client.session import ClientSession
except ImportError:
    print("ERROR: mcp package not installed. Run: pip install mcp[cli]", file=sys.stderr)
    sys.exit(1)


async def main():
    """Test persistent ROOT graphics objects."""
    server_params = StdioServerParameters(
        command="bash",
        args=[
            "-lc",
            "source /home/ozapatam/Projects/CERN/ROOT/root/build/bin/thisroot.sh && /usr/bin/python3 -m root_mcp_server.cli"
        ],
        env=None
    )
    
    print("Starting ROOT MCP server with graphics enabled...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Create first histogram
            print("\n=== Creating first histogram (h1) ===")
            code1 = """
import ROOT
h1 = ROOT.TH1F("h1", "First Histogram", 50, -3, 3)
for i in range(5000):
    h1.Fill(ROOT.gRandom.Gaus(0, 1))
c1 = ROOT.TCanvas("c1", "Canvas 1", 800, 600)
h1.Draw()
c1.Update()
print(f"Created h1 (entries: {h1.GetEntries()}) and c1")
"""
            result1 = await session.call_tool("root_python", arguments={"code": code1})
            print(result1.content[0].text)
            
            await asyncio.sleep(1)
            
            # Create second histogram
            print("\n=== Creating second histogram (h2) ===")
            code2 = """
import ROOT
h2 = ROOT.TH1F("h2", "Second Histogram", 100, 0, 10)
for i in range(10000):
    h2.Fill(ROOT.gRandom.Exp(2))
c2 = ROOT.TCanvas("c2", "Canvas 2", 800, 600)
h2.Draw()
c2.Update()
print(f"Created h2 (entries: {h2.GetEntries()}) and c2")
"""
            result2 = await session.call_tool("root_python", arguments={"code": code2})
            print(result2.content[0].text)
            
            await asyncio.sleep(1)
            
            # Check that objects are still accessible
            print("\n=== Checking objects are still alive ===")
            code3 = """
import ROOT
# Try to access previously created canvases
c1 = ROOT.gROOT.FindObject("c1")
c2 = ROOT.gROOT.FindObject("c2")
h1 = ROOT.gROOT.FindObject("h1")
h2 = ROOT.gROOT.FindObject("h2")

if c1:
    print(f"✓ Canvas c1 still exists")
else:
    print(f"✗ Canvas c1 was garbage collected")
    
if c2:
    print(f"✓ Canvas c2 still exists")
else:
    print(f"✗ Canvas c2 was garbage collected")
    
if h1:
    print(f"✓ Histogram h1 still exists (entries: {h1.GetEntries()})")
else:
    print(f"✗ Histogram h1 was garbage collected")
    
if h2:
    print(f"✓ Histogram h2 still exists (entries: {h2.GetEntries()})")
else:
    print(f"✗ Histogram h2 was garbage collected")
"""
            result3 = await session.call_tool("root_python", arguments={"code": code3})
            print(result3.content[0].text)
            
            print("\n=== Keeping session alive for 5 more seconds ===")
            await asyncio.sleep(5)
            
    print("\nSession ended. All objects should have been kept alive during the session!")


if __name__ == "__main__":
    asyncio.run(main())
