from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@novitalabs/novita-mcp-server"],
    env={"NOVITA_API_KEY":  os.environ["NOVITA_API_KEY"]},
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print("Available tools:", tools)

if __name__ == "__main__":
    import asyncio

    asyncio.run(run())