# Novita MCP Blog

A demonstration of building Model Context Protocol (MCP) servers using the Novita API. This repository provides two server implementations and a sample client for interacting with Novita's AI services.

## Features

- **FastMCP Server (`server.py`)**: Full-featured MCP server with tools for models, text-to-image, video, and speech generation.
- **Low-Level Server (`low-level-server.py`)**: Minimal MCP server for basic model listing and retrieval.
- **Sample Client (`client.py`)**: Script to interact with and list available tools from the servers.

## Prerequisites

- Python 3
- [Novita API Key](https://novita.ai/) (sign up to obtain one)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Studio1HQ/Novita_MCP_Blog.git
   cd Novita_MCP_Blog
   ```
2. Install the MCP Python SDK:
   ```bash
   pip install "mcp[cli]"
   ```

## Configuration

Add your Novita API key to your environment variables:
```bash
export NOVITA_API_KEY=sk_...
```

Or configure it in your MCP host (e.g., Claude, VS Code, Cursor) as shown below.

## Usage

To use the servers, add the following to your MCP configuration file:

```json
{
    "fastmcp": {
        "command": "python",
        "args": ["server.py"],
        "env": {"NOVITA_API_KEY": "sk_..."}
    },
    "low-level-server": {
        "command": "python",
        "args": ["low-level-server.py"],
        "env": {"NOVITA_API_KEY": "sk_..."}
    }
}
```

For VS Code, you can use [inputs](https://code.visualstudio.com/docs/copilot/chat/mcp-servers#_configuration-format) to manage your API keys securely.

### Available Tools

**FastMCP Server (`server.py`):**
- List Models: List all models hosted on Novita
- Get Model: Retrieve a specific LLM from Novita
- Text to Image: Generate images from text
- Task Result: Check the status of a running task
- Generate Video: Generate videos from prompts
- Text to Speech: Generate speech from text

**Low-Level Server (`low-level-server.py`):**
- List Models
- Get Model

## Listing Tools with the Client Script

You can list the available tools in each server using the `client.py` script:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="python",
    args=["server.py",], # Replace with 'low-level-server.py' to list the tools of the low level server 
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
```

> **Note:** Ensure your Novita API key is set as an environment variable when running this script.
