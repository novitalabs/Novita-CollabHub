import os
import asyncio
import requests
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

base_url = "https://api.novita.ai/v3"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['NOVITA_API_KEY']}"
}

app = Server("Novita_API")


async def list_models_tool():
    """
    Lists all available models from the Novita API.
    """
    url = base_url + "/openai/models"
    response = requests.get(url, headers=headers)
    data = response.json()["data"]

    text = ""
    for i, model in enumerate(data, start=1):
        text += f"Model id: {model['id']}\n"
        text += f"Model description: {model['description']}\n"
        text += f"Model type: {model['model_type']}\n\n"

    return [types.TextContent(type="text", text=text)]


async def get_model_tool(arguments: dict):
    """
    Given a model ID and a user message, fetch a response from the Novita API.
    """
    model_id = arguments.get("model_id")
    message = arguments.get("message")

    if not model_id or not message:
        raise ValueError("Both 'model_id' and 'message' are required.")

    url = base_url + "/openai/chat/completions"

    payload = {
        "model": model_id,
        "messages": [
            {
                "content": message,
                "role": "user",
            }
        ],
        "max_tokens": 200,
        "response_format": {
            "type": "text",
        },
    }

    response = requests.post(url, json=payload, headers=headers)
    content = response.json()["choices"][0]["message"]["content"]
    return [types.TextContent(type="text", text=content)]

@app.call_tool()
async def manage_tool(name: str, arguments: dict ) -> list[types.TextContent]:
    if name == "list_models":
        return await list_models_tool()
    
    if name == "get_model":
        return await get_model_tool(arguments)
    
    else:
        raise ValueError(f"Unknown tool: {name}")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="list_models",
            description="List all available models from the Novita API.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_model",
            description="Provide a model ID and a message to get a response from the Novita API.",
            inputSchema={
                "type": "object",
                "required": ["model_id", "message"],
                "properties": {
                    "model_id": {
                        "type": "string",
                        "description": "The ID of the model to use.",
                    },
                    "message": {
                        "type": "string",
                        "description": "The input message to send.",
                    },
                },
            },
        ),
    ]


async def main():
    async with stdio_server() as streams:
        await app.run(streams[0], streams[1], app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
