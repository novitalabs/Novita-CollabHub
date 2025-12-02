# Novita Agent Runtime - AutoGen Example

**Build multi-agent systems with Microsoft AutoGen and deploy to Novita Agent Runtime in minutes.**

This example demonstrates how to deploy an AI agent with streaming responses, multi-turn conversations, and multi-tool integration using Microsoft AutoGen framework.

## 📋 Table of Contents

- [What This Example Includes](#-what-this-example-includes)
- [Quick Start](#-quick-start)
  - [What You Need](#what-you-need)
  - [Run Locally](#run-locally)
  - [Deploy to Novita Agent Runtime](#deploy-to-novita-agent-runtime)
- [Project Structure](#-project-structure)
- [Agent Capabilities](#-agent-capabilities)
- [Testing](#-testing)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)
- [Resources](#-resources)

## ✨ What This Example Includes

This agent example includes the following capabilities:

- ✅ **Streaming responses** - Real-time token streaming for better UX
- ✅ **Multi-turn conversations** - Automatic conversation history management
- ✅ **Multi-tool integration** - Weather query, search, and calculation tools
- ✅ **Tool reflection** - AutoGen's built-in tool use reflection capability
- ✅ **Complete test suite** - Both local and production tests

## 🚀 Quick Start

### What You Need

Before starting, install these requirements:

- **Python 3.9+** and **Node.js 20+**
- **Novita AI API Key** - [Get it from console](https://novita.ai/settings/key-management)

### Run Locally

**1. Clone the repository**

```bash
git clone git@github.com:novitalabs/Novita-CollabHub.git
cd Novita-CollabHub/examples/agent-runtime/agentic-frameworks/autogen
```

**2. Create a Python virtual environment**

```bash
python -m venv .venv

# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

**3. Install Python dependencies**

```bash
pip install -r requirements.txt
```

**4. Add your API keys to `.env`**

Copy the example file and add your keys:

```bash
cp .env.example .env
```

Edit `.env` with these required values:

| Variable | Description | Required | Where to Find It |
|----------|-------------|----------|------------------|
| `OPENAI_API_KEY` | Your Novita AI API Key for LLM access | ✅ Yes | [Novita API Keys](https://novita.ai/settings/key-management) |
| `OPENAI_BASE_URL` | OpenAI-compatible API endpoint | No | Default: `https://api.novita.ai/v3/openai` |
| `MODEL_NAME` | Model name to use | No | Default: `deepseek/deepseek-v3.1-terminus` |
| `NOVITA_API_KEY` | Your Novita AI API Key (for deployment) | For deployment only | Same as `OPENAI_API_KEY` |
| `NOVITA_AGENT_ID` | Agent ID after deployment | For CLI invocation | From `.novita-agent.yaml` after deployment |

**5. Start the agent locally**

```bash
python app.py
```

The agent runs at `http://localhost:8080`. Test it:

```bash
bash tests/test_local_basic.sh
```

You should see a JSON response with the agent's answer.

### Deploy to Novita Agent Runtime

**1. Install Novita Sandbox CLI (beta) locally**

```bash
npm install novita-sandbox-cli@beta

npx novita-sandbox-cli --version
```

**2. Configure your agent**

Run the interactive configuration (first deployment only):

```bash
npx novita-sandbox-cli agent configure
```

The CLI creates three files:
- `.novita-agent.yaml` - Agent metadata and configuration
- `novita.Dockerfile` - Sandbox template Dockerfile
- `.dockerignore` - Files to exclude from Docker build

**3. Deploy to Novita AI**

```bash
npx novita-sandbox-cli agent launch
```

After deployment succeeds, `.novita-agent.yaml` contains your agent ID:

```yaml
status:
  phase: deployed
  agent_id: agent-xxxx  # ⭐ You need this ID to invoke the agent
  last_deployed: '2025-10-23T10:35:00Z'
```

**4. Test with CLI**

Invoke your deployed agent:

```bash
npx novita-sandbox-cli agent invoke "Hello, Agent!" --env NOVITA_API_KEY="<your-api-key>"
```

The CLI reads `agent_id` automatically from `.novita-agent.yaml`.

**5. Invoke the agent from your application with SDK**

Save the Agent ID from `.novita-agent.yaml` to `.env` file:

```bash
NOVITA_AGENT_ID=agent-xxxx  # Copy from .novita-agent.yaml status.agent_id
```

Test SDK invocation:

```bash
# Non-streaming response test
python tests/test_sandbox_basic.py

# Streaming response test
python tests/test_sandbox_streaming.py

# Multi-turn conversation test
python tests/test_sandbox_multi_turn.py
```

## 📁 Project Structure

```
autogen/
├── app.py                          # Agent program
├── tests/                          # All test files
│   ├── test_local_basic.sh         # Local basic test
│   ├── test_local_streaming.sh     # Local streaming response test
│   ├── test_local_multi_turn.sh    # Local multi-turn conversation test
│   ├── test_sandbox_basic.py       # Remote basic test
│   ├── test_sandbox_streaming.py   # Remote streaming test
│   └── test_sandbox_multi_turn.py  # Remote multi-turn test
├── .env.example                    # Environment variable template
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── README.md
├── README_zh.md
└── LICENSE
```

## 🏗️ Agent Capabilities

This example agent has three main features:

### 💬 Multi-turn conversations

The agent remembers conversation history automatically. Each sandbox instance maintains its own conversation context.

**Example conversation:**
```
Turn 1:
User: "My name is Alice"
Agent: "Nice to meet you, Alice!"

Turn 2 (same session):
User: "What's my name?"
Agent: "Your name is Alice."
```

To maintain the same session when using the SDK, pass the same `runtimeSessionId` value across requests.

### 🛠️ Multi-tool capabilities

The agent has access to three tools:

1. **get_weather** - Query weather information
2. **search_information** - Search for general information (demo implementation)
3. **calculate** - Perform mathematical calculations

AutoGen's **tool reflection** feature enables the agent to evaluate tool usage and improve responses.

### 📡 Streaming and non-streaming responses

Each request can choose whether to return streaming data via the `streaming` parameter.

## 🧪 Testing

### Local testing (development)

Local tests run against `app.py` on `localhost:8080`.

**Start the agent:**

```bash
python app.py
```

**Run tests in another terminal:**

```bash
# Basic test
bash tests/test_local_basic.sh

# Streaming response test
bash tests/test_local_streaming.sh

# Multi-turn conversation test
bash tests/test_local_multi_turn.sh
```

> **Windows users:** Use Git Bash or WSL to run bash scripts.

### Production testing (in agent sandbox)

Production tests invoke the deployed agent using the SDK.

**Requirements:**
- Agent deployed with `agent launch` command
- `NOVITA_AGENT_ID` added to `.env` file

**Run tests:**

```bash
# Non-streaming response
python tests/test_sandbox_basic.py

# Streaming response
python tests/test_sandbox_streaming.py

# Multi-turn conversation
python tests/test_sandbox_multi_turn.py
```

All tests should pass if the agent is configured correctly.

## 🔌 API Reference

### Health check endpoint

Check if the agent is running properly:

```bash
GET /ping
```

**Response:**
```json
{
  "status": "healthy",
  "service": "AutoGen Agent",
  "features": ["weather", "search", "calculate", "streaming", "multi-turn"]
}
```

### Agent invocation endpoint

Send a request to the agent:

```bash
POST /invocations
```

**Request body parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | ✅ Yes | - | User message or question |
| `streaming` | boolean | No | `false` | Enable streaming output |

**Example request:**
```json
{
  "prompt": "What's the weather in New York?",
  "streaming": false
}
```

**Non-streaming response:**
```json
{
  "result": "New York is currently sunny with a temperature of 15°C..."
}
```

**Streaming response:**

Server-Sent Events (SSE) format:

```
data: {"chunk": "New York ", "type": "content"}
data: {"chunk": "is ", "type": "content"}
data: {"chunk": "currently ", "type": "content"}
...
data: {"chunk": "", "type": "end"}
```

Each `data:` line contains a JSON object with the next token chunk.

## 🔧 Troubleshooting

### Agent doesn't remember previous messages

**Cause:** Each sandbox restart creates a new conversation history.

**Solution:** Use the same `runtimeSessionId` parameter in SDK calls to maintain the same sandbox instance:

```python
response = await client.invoke_agent_runtime(
    agentId=agent_id,
    payload=payload,
    runtimeSessionId="unique-session-id",  # Same ID for multi-turn
    timeout=300
)
```

### Streaming doesn't work

**Cause:** The `streaming` parameter might be missing or set to `false`.

**Solution:** Ensure your request includes `"streaming": true`:

```json
{
  "prompt": "Your question",
  "streaming": true
}
```

### Import errors when running locally

**Cause:** Dependencies not installed or wrong Python environment.

**Solution:** 
1. Activate your virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Verify installation: `pip list | grep autogen`

### Tool reflection not working as expected

**Cause:** AutoGen's reflection feature requires specific model capabilities.

**Solution:** Ensure you're using a model that supports function calling and has sufficient reasoning capabilities. Check the `reflect_on_tool_use` parameter in `app.py`.

## 📚 Resources

- [Novita Agent Runtime Documentation](https://novita.ai/docs/guides/sandbox-agent-runtime-introduction)
- [Novita Agent Sandbox Documentation](https://novita.ai/docs/guides/sandbox-overview)
- [Microsoft AutoGen Documentation](https://microsoft.github.io/autogen/stable/)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Need help?** Open an issue or contact support at [novita.ai](https://novita.ai)

