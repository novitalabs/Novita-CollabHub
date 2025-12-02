# Novita Agent Runtime - OpenAI Agents SDK Example

**Build AI agents with OpenAI Agents SDK and deploy to Novita Agent Runtime in minutes.**

This example demonstrates how to deploy an AI agent with OpenAI Function Calling and multiple tool integrations to Novita Agent Runtime.

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

- ✅ **OpenAI Function Calling** - Standard OpenAI tool integration pattern
- ✅ **Multiple tools** - Time query, calculation, and weather tools
- ✅ **Simple architecture** - Easy to understand and extend
- ✅ **Compatible with OpenAI API** - Works with any OpenAI-compatible endpoint

## 🚀 Quick Start

### What You Need

Before starting, install these requirements:

- **Python 3.9+** and **Node.js 20+**
- **Novita AI API Key** - [Get it from console](https://novita.ai/settings/key-management)

### Run Locally

**1. Clone the repository**

```bash
git clone git@github.com:novitalabs/Novita-CollabHub.git
cd agent-runtime-example/integrations/agentic-frameworks/openai-agents-sdk
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
| `NOVITA_API_KEY` | Your Novita API key | ✅ Yes | [Novita API Keys](https://novita.ai/settings/key-management) |
| `MODEL_NAME` | Model name to use | No | Default: `deepseek/deepseek-v3.1-terminus` |
| `OPENAI_API_BASE` | OpenAI-compatible API endpoint | No | Default: `https://api.novita.ai/v3/openai` |
| `OPENAI_TIMEOUT` | API timeout in seconds | No | Default: `60` |
| `NOVITA_AGENT_ID` | Agent ID after deployment | Only for CLI testing | From `.novita-agent.yaml` after deployment |

**5. Start the agent locally**

```bash
python app.py
```

The agent runs at `http://localhost:8080`. Test it:

```bash
bash tests/test_local_basic.sh
```

You should see the agent using various tools to answer questions.

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
npx novita-sandbox-cli agent invoke "What time is it now?" --env NOVITA_API_KEY="<your-api-key>"
```

The CLI reads `agent_id` automatically from `.novita-agent.yaml`.

**5. Invoke the agent from your application with SDK**

Save the Agent ID from `.novita-agent.yaml` to `.env` file:

```bash
NOVITA_AGENT_ID=agent-xxxx  # Copy from .novita-agent.yaml status.agent_id
```

Test SDK invocation:

```bash
python tests/test_sandbox_basic.py
```

## 📁 Project Structure

```
openai-agents-sdk/
├── app.py                       # Agent program
├── tests/                       # All test files
│   ├── test_local_basic.sh      # Local basic test
│   └── test_sandbox_basic.py    # Remote basic test
├── .env.example                 # Environment variable template
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── README.md
├── README_zh.md
└── LICENSE
```

## 🏗️ Agent Capabilities

This example agent showcases OpenAI Function Calling with three useful tools:

### 🛠️ Built-in Tools

The agent has access to three tools:

1. **get_current_time** - Get current UTC time
   ```json
   {
     "name": "get_current_time",
     "description": "Get the current time",
     "parameters": {
       "timezone": "UTC"
     }
   }
   ```

2. **calculate** - Perform mathematical calculations
   ```json
   {
     "name": "calculate",
     "description": "Calculate a mathematical expression",
     "parameters": {
       "expression": "2 + 3 * 4"
     }
   }
   ```

3. **get_weather** - Query weather information for cities (demo data)
   ```json
   {
     "name": "get_weather",
     "description": "Get weather for a city",
     "parameters": {
       "city": "New York"
     }
   }
   ```

### 🔄 Function Calling Flow

The agent follows OpenAI's standard function calling pattern:

1. **First LLM call** - Agent receives user query and tool definitions
2. **Tool selection** - Agent decides which tools to use (if any)
3. **Tool execution** - Selected tools are executed with appropriate parameters
4. **Second LLM call** - Agent synthesizes tool results into final response

This approach ensures accurate tool usage and natural language responses.

### 🔌 Extensibility

Adding new tools is straightforward:

1. Define your Python function
2. Add the function definition to `TOOLS` list
3. Map the function in `TOOL_FUNCTIONS` dictionary

The agent automatically integrates new tools into its capabilities.

## 🧪 Testing

### Local testing (development)

Local tests run against `app.py` on `localhost:8080`.

**Start the agent:**

```bash
python app.py
```

**Run tests in another terminal:**

```bash
bash tests/test_local_basic.sh
```

The test suite validates all three tools:
- Weather query tool
- Information search tool
- Calculation tool

> **Windows users:** Use Git Bash or WSL to run bash scripts.

### Production testing (in agent sandbox)

Production tests invoke the deployed agent using the SDK.

**Requirements:**
- Agent deployed with `agent launch` command
- `NOVITA_AGENT_ID` added to `.env` file

**Run tests:**

```bash
python tests/test_sandbox_basic.py
```

The test should pass if the agent is configured correctly.

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
  "service": "OpenAI Agents SDK Runtime"
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

**Example request:**
```json
{
  "prompt": "What time is it now?"
}
```

**Response:**
```json
{
  "result": "The current time (UTC) is: 2025-11-14 10:30:45",
  "status": "success"
}
```

**Example with tool usage:**

Request:
```json
{
  "prompt": "Calculate 123 + 456 and tell me the weather in New York"
}
```

Response:
```json
{
  "result": "The calculation result is 579. In New York, it's currently sunny with a temperature of 15°C and good air quality.",
  "status": "success"
}
```

## 🔧 Troubleshooting

### Function calling not working

**Cause:** Model doesn't support function calling or configuration issue.

**Solution:** 
1. Verify your model supports function calling (most modern models do)
2. Check that `tools` parameter is properly formatted
3. Ensure `tool_choice: "auto"` is set in the API call

### Tools not being called when expected

**Cause:** Model might not recognize when to use tools.

**Solution:** 
1. Improve tool descriptions to be more specific
2. Adjust system message to encourage tool usage
3. Try using a more capable model

### Import errors when running locally

**Cause:** Dependencies not installed or wrong Python environment.

**Solution:** 
1. Activate your virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Verify installation: `pip list | grep openai`

### API connection errors

**Cause:** Incorrect API endpoint or API key.

**Solution:**
1. Verify `OPENAI_API_BASE` is correct
2. Check `NOVITA_API_KEY` is valid
3. Test API connectivity: `curl https://api.novita.ai/v3/openai/models`

## 📚 Resources

- [Novita Agent Runtime Documentation](https://novita.ai/docs/guides/sandbox-agent-runtime-introduction)
- [Novita Agent Sandbox Documentation](https://novita.ai/docs/guides/sandbox-overview)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Need help?** Open an issue or contact support at [novita.ai](https://novita.ai)

