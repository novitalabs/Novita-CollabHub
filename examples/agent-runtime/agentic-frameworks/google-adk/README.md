# Novita Agent Runtime - Google ADK Example

**Build AI agents with Google Agent Development Kit and deploy to Novita Agent Runtime in minutes.**

This example demonstrates how to deploy a Google Gemini-powered AI agent with native Google Search integration to Novita Agent Runtime.

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

- ✅ **Google Gemini models** - Powered by Google's latest Gemini models
- ✅ **Native Google Search** - Built-in Google Search tool integration
- ✅ **Session management** - In-memory session service for context retention
- ✅ **Simple and efficient** - Minimal setup with powerful capabilities

## 🚀 Quick Start

### What You Need

Before starting, install these requirements:

- **Python 3.9+** and **Node.js 20+**
- **Google AI API Key** - [Get it from Google AI Studio](https://aistudio.google.com/app/apikey)
- **Novita AI API Key** - [Get it from console](https://novita.ai/settings/key-management)

### Run Locally

**1. Clone the repository**

```bash
git clone git@github.com:novitalabs/Novita-CollabHub.git
cd Novita-CollabHub/examples/agent-runtime/agentic-frameworks/google-adk
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
| `GOOGLE_API_KEY` | Your Google AI API key | ✅ Yes | [Google AI Studio → API Keys](https://aistudio.google.com/app/apikey) |
| `GEMINI_MODEL` | Gemini model name | No | Default: `gemini-2.5-flash` |
| `NOVITA_API_KEY` | Your Novita API Key (for deployment) | Only for deployment | [Novita API Keys](https://novita.ai/settings/key-management) |
| `NOVITA_AGENT_ID` | Agent ID after deployment | Only for CLI invocation | From `.novita-agent.yaml` after deployment |

**5. Start the agent locally**

```bash
python app.py
```

The agent runs at `http://localhost:8080`. Test it:

```bash
bash tests/test_local_basic.sh
```

You should see responses powered by Google Gemini with search capabilities.

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

Invoke your deployed agent (pass Google API key as environment variable):

```bash
npx novita-sandbox-cli agent invoke "Tell me about Google Gemini" --env GOOGLE_API_KEY="<your-google-api-key>"
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
google-adk/
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

This example agent showcases Google ADK's core features:

### 🤖 Google Gemini Models

The agent uses Google's Gemini models (default: `gemini-2.0-flash`), providing:
- Fast and efficient responses
- Advanced reasoning capabilities
- Large context windows
- Multimodal understanding (when applicable)

You can change the model by setting `GEMINI_MODEL` in your `.env` file.

### 🔍 Native Google Search Integration

The agent has built-in Google Search capability through the `google_search` tool. When users ask questions that require current information, the agent automatically:
1. Searches Google for relevant information
2. Processes the search results
3. Synthesizes a comprehensive answer

**Example:**
```
User: "What are the latest features of Google Gemini 3.0?"
Agent: [Searches Google and provides up-to-date information]
```

### 💾 Session Management

The agent uses in-memory session service to maintain conversation context within the same sandbox instance. Sessions are identified by `session_id` from the request context.

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

> **Windows users:** Use Git Bash or WSL to run bash scripts.

### Production testing (in agent sandbox)

Production tests invoke the deployed agent using the SDK.

**Requirements:**
- Agent deployed with `agent launch` command
- `NOVITA_AGENT_ID` added to `.env` file
- `GOOGLE_API_KEY` available in environment

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
  "service": "Google ADK Agent",
  "features": ["google_search"]
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
| `user_id` | string | No | `"user1234"` | User identifier |

**Example request:**
```json
{
  "prompt": "What are the latest AI developments?",
  "user_id": "user123"
}
```

**Response:**
```json
{
  "result": "Based on recent information, here are the latest AI developments..."
}
```

## 🔧 Troubleshooting

### "Session not found" or "app name" errors

**Cause:** Session service configuration issues.

**Solution:** The agent automatically falls back to direct Gemini API calls. This is normal behavior and the agent will still function correctly.

### Google Search not returning results

**Cause:** Google Search API quota limits or connectivity issues.

**Solution:** 
1. Check your Google AI API key is valid
2. Verify you have sufficient API quota
3. Check network connectivity

### Import errors when running locally

**Cause:** Dependencies not installed or wrong Python environment.

**Solution:** 
1. Activate your virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Verify installation: `pip list | grep google-adk`

### Agent responses are slow

**Cause:** Google Search queries can take time depending on network conditions.

**Solution:** This is expected behavior when the agent needs to search. For faster responses on simple queries, the agent will respond directly without searching.

## 📚 Resources

- [Novita Agent Runtime Documentation](https://novita.ai/docs/guides/sandbox-agent-runtime-introduction)
- [Novita Agent Sandbox Documentation](https://novita.ai/docs/guides/sandbox-overview)
- [Google Agent Development Kit](https://docs.cloud.google.com/agent-builder/agent-development-kit/overview)
- [Google AI Studio](https://aistudio.google.com/)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Need help?** Open an issue or contact support at [novita.ai](https://novita.ai)

