import os
import json
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from novita_sandbox.code_interpreter import Sandbox
from openai import OpenAI

# ---------------------------------------------
# Initial Setup
# ---------------------------------------------

client = OpenAI(
    base_url="https://api.novita.ai/openai",
    api_key=os.environ["NOVITA_API_KEY"],
)

model = "meta-llama/llama-3.3-70b-instruct"

# Full tool list
tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read contents of a file inside the sandbox",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write a single file inside the sandbox",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "data": {"type": "string"},
                },
                "required": ["path", "data"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_files",
            "description": "Write multiple files inside the sandbox",
            "parameters": {
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "data": {"type": "string"},
                            },
                            "required": ["path", "data"],
                        },
                    }
                },
                "required": ["files"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_commands",
            "description": "Run a shell command inside the sandbox working directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                },
                "required": ["command"],
            },
        },
    },
]


# ---------------------------------------------
# FastAPI + WebSocket Setup
# ---------------------------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------
# Helper: Execute tool functions
# ---------------------------------------------

def make_tool_handlers(sandbox):
    def read_file(path: str):
        print(f"[LOG] read_file called with path: {path}")
        try:
            content = sandbox.files.read(path)
            print(f"[LOG] read_file result: {content}")
            return content
        except Exception as e:
            return f"Error reading file: {e}"

    def write_file(path: str, data: str):
        print(f"[LOG] write_file called with path: {path}")
        try:
            sandbox.files.write(path, data)
            return f"File created successfully at {path}"
        except Exception as e:
            return f"Error writing file: {e}"

    def write_files(files: list):
        print(f"[LOG] write_files called with {len(files)} files")
        try:
            sandbox.files.write_files(files)
            return f"{len(files)} file(s) created successfully"
        except Exception as e:
            return f"Error writing multiple files: {e}"

    def run_commands(command: str):
        print(f"[LOG] run_commands called with command: {command}")
        try:
            result = sandbox.commands.run(command)
            return result.stdout
        except Exception as e:
            return f"Error running command: {e}"

    return {
        "read_file": read_file,
        "write_file": write_file,
        "write_files": write_files,
        "run_commands": run_commands,
    }


# ---------------------------------------------
# WebSocket Endpoint (Full Agent)
# ---------------------------------------------

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print("\n[WS] Client connected")

    # Create sandbox per connection
    sandbox = Sandbox.create(timeout=1200)
    print("[WS] Sandbox created")

    tools_exec = make_tool_handlers(sandbox)
    messages = []  # persistent inside this websocket

    try:
        while True:
            data = await ws.receive_text()
            print(f"[WS] Received message: {data}")

            # Add user message
            messages.append({"role": "user", "content": data})

            # LLM call
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
            )

            assistant_msg = response.choices[0].message
            messages.append(assistant_msg)

            # If LLM wants to call tools
            if assistant_msg.tool_calls:
                print(f"[WS] Assistant requested {len(assistant_msg.tool_calls)} tool call(s).")

                results = []

                for tool_call in assistant_msg.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)

                    print(f"[WS] Tool call: {fn_name} args={fn_args}")

                    if fn_name in tools_exec:
                        result = tools_exec[fn_name](**fn_args)
                    else:
                        result = f"Error: Unknown tool {fn_name}"

                    results.append(result)

                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "content": str(result),
                    })

                # Follow-up model call
                follow_up = client.chat.completions.create(
                    model=model,
                    messages=messages,
                )
                final_answer = follow_up.choices[0].message
                messages.append(final_answer)

                await ws.send_json({
                    "reply": final_answer.content,
                    "tool_output": results,
                })

            else:
                # Simple model text output
                await ws.send_json({"reply": assistant_msg.content})

    except WebSocketDisconnect:
        print("[WS] Client disconnected")

    finally:
        sandbox.kill()
        print("[WS] Sandbox terminated")


# ---------------------------------------------
# Run server
# ---------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
