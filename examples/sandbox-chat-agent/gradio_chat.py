import gradio as gr
from openai import OpenAI
import os
import json
import threading
import time
import atexit
from novita_sandbox.code_interpreter import Sandbox

# -------------------------
# Global State
# -------------------------
client = OpenAI(
    base_url="https://api.novita.ai/openai",
    api_key=os.environ["NOVITA_API_KEY"],
)

model = "meta-llama/llama-3.3-70b-instruct"

sandbox = None
sandbox_timer = None

# -------------------------
# Sandbox Management
# -------------------------
def create_sandbox():
    global sandbox
    if sandbox is None:
        sandbox = Sandbox.create(timeout=1200)
        print("[DEBUG] Sandbox created.")
        return "🟢 Sandbox ON"
    return "Sandbox already running."

def kill_sandbox():
    global sandbox
    if sandbox is not None:
        try:
            sandbox.kill()
        except Exception:
            pass
        sandbox = None
        print("[DEBUG] Sandbox killed.")
        return "🔴 Sandbox OFF"
    return "Sandbox already off."

def sandbox_auto_off():
    print("[DEBUG] Auto-off countdown started (1200 sec).")
    time.sleep(1200)
    print("[DEBUG] Auto-off triggered.")
    kill_sandbox()

# -------------------------
# Sandbox Usage Guard
# -------------------------
def require_sandbox():
    if sandbox is None:
        return "❌ Sandbox is OFF. Turn it ON to use this feature."
    return None

# -------------------------
# Tool Functions
# -------------------------
def read_file(path: str):
    print(f"[DEBUG] read_file called with path: {path}")
    err = require_sandbox()
    if err:
        return err

    try:
        content = sandbox.files.read(path)
        print(f"[DEBUG] read_file result: {content}")
        return content
    except Exception as e:
        print(f"[DEBUG] read_file error: {e}")
        return f"Error reading file: {e}"

def write_file(path: str, data: str):
    print(f"[DEBUG] write_file called with path: {path}")
    err = require_sandbox()
    if err:
        return err

    try:
        sandbox.files.write(path, data)
        msg = f"File created successfully at {path}"
        print(f"[DEBUG] {msg}")
        return msg
    except Exception as e:
        print(f"[DEBUG] write_file error: {e}")
        return f"Error writing file: {e}"

def write_files(files: list):
    print(f"[DEBUG] write_files called with {len(files)} files")
    err = require_sandbox()
    if err:
        return err

    try:
        sandbox.files.write_files(files)
        msg = f"{len(files)} file(s) created successfully"
        print(f"[DEBUG] {msg}")
        return msg
    except Exception as e:
        print(f"[DEBUG] write_files error: {e}")
        return f"Error writing multiple files: {e}"

def run_commands(command: str):
    print(f"[DEBUG] run_commands called with command: {command}")
    err = require_sandbox()
    if err:
        return err

    try:
        result = sandbox.commands.run(command)
        print(f"[DEBUG] run_commands result: {result.stdout}")
        return result.stdout
    except Exception as e:
        print(f"[DEBUG] run_commands error: {e}")
        return f"Error running command: {e}"

# -------------------------
# Register tools
# -------------------------
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
            "description": "Run a shell command inside the sandbox",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        },
    },
]

# -------------------------
# Chat + Tool Call Debug
# -------------------------
messages = []

def set_model(selected_model):
    global model
    model = selected_model
    return f"✅ Model switched to **{model}**"

def chat_fn(user_message, history):
    global messages, model

    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
    )

    assistant_msg = response.choices[0].message
    messages.append(assistant_msg)

    # DEBUG tool call logging
    if assistant_msg.tool_calls:
        print(f"[DEBUG] Assistant requested {len(assistant_msg.tool_calls)} tool call(s).")

        for tc in assistant_msg.tool_calls:
            print(f"[DEBUG] Tool call detected: {tc.function.name} with args {tc.function.arguments}")

            fn_name = tc.function.name
            fn_args = json.loads(tc.function.arguments)

            if fn_name == "read_file":
                result = read_file(**fn_args)
            elif fn_name == "write_file":
                result = write_file(**fn_args)
            elif fn_name == "write_files":
                result = write_files(**fn_args)
            elif fn_name == "run_commands":
                result = run_commands(**fn_args)
            else:
                result = f"Unknown tool {fn_name}"

            print(f"[DEBUG] Tool call result: {result}")

            messages.append({
                "tool_call_id": tc.id,
                "role": "tool",
                "content": str(result),
            })

        followup = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        final_msg = followup.choices[0].message
        messages.append(final_msg)
        return final_msg.content

    return assistant_msg.content

# -------------------------
# Command Interface
# -------------------------
def execute_command(command):
    if not command.strip():
        return "⚠️ Please enter a command."
    output = run_commands(command)
    return f"```bash\n{output}\n```"

# -------------------------
# UI
# -------------------------
with gr.Blocks(title="Novita Sandbox App") as demo:
    gr.Markdown("## 🧠 Novita Sandbox Agent")
    gr.Markdown("Interact with a Novita sandbox-enabled LLM with code execution capability.")

    with gr.Row(equal_height=True):
        # Chat
        with gr.Column(scale=2):
            gr.Markdown("### 💬 Chat Interface")
            gr.ChatInterface(chat_fn)

        # Controls
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ Controls")

            # Sandbox Switch
            sandbox_switch = gr.Checkbox(label="Sandbox On/Off", value=False)
            sandbox_status = gr.Markdown("🔴 Sandbox OFF")

            def toggle_sandbox(is_on):
                global sandbox_timer
                if is_on:
                    msg = create_sandbox()
                    sandbox_timer = threading.Thread(target=sandbox_auto_off, daemon=True)
                    sandbox_timer.start()
                    return "🟢 Sandbox ON"
                else:
                    msg = kill_sandbox()
                    return "🔴 Sandbox OFF"

            sandbox_switch.change(toggle_sandbox, inputs=sandbox_switch, outputs=sandbox_status)

            # Model Selector
            model_selector = gr.Dropdown(
                label="Select Model",
                choices=[
                    "meta-llama/llama-3.3-70b-instruct",
                    "deepseek/deepseek-v3.2-exp",
                    "qwen/qwen3-coder-30b-a3b-instruct",
                    "openai/gpt-oss-120b",
                    "moonshotai/kimi-k2-instruct",
                ],
                value=model,
            )
            model_status = gr.Markdown(f"Current model: **{model}**")
            model_selector.change(set_model, inputs=model_selector, outputs=model_status)

            # Command Runner
            command_input = gr.Textbox(label="Command", placeholder="e.g., ls")
            run_btn = gr.Button("Run", variant="primary")
            command_output = gr.Markdown("Command output here...")
            run_btn.click(execute_command, inputs=command_input, outputs=command_output)

# Cleanup
atexit.register(lambda: (kill_sandbox(), print("[DEBUG] Sandbox terminated.")))

if __name__ == "__main__":
    demo.launch()
