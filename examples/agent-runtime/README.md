<div align="center">
  <h1>Novita Agent Runtime Sample Projects</h1>
  
  <h2>Build and Deploy AI Agents with Any Framework and Model</h2>
  
  <p>
    <a href="#-quick-start">Quick Start</a> •
    <a href="https://novita.ai/docs/guides/sandbox-agent-runtime-introduction">Documentation</a> •
    <a href="#-repository-structure">Repository Structure</a>
  </p>
</div>

---

Welcome to the Novita Agent Runtime sample projects repository!

**Novita Agent Runtime** is a framework-agnostic, model-agnostic lightweight AI agent runtime framework that enables you to deploy and run AI agents safely and quickly. Whether you're using [LangGraph](https://www.langchain.com/langgraph), [Microsoft AutoGen](https://www.microsoft.com/en-us/research/project/autogen/), [Google ADK](https://docs.cloud.google.com/agent-builder/agent-development-kit/overview), or [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/), Novita Agent Runtime provides the infrastructure support you need. By eliminating the heavy lifting of building and managing agent infrastructure, Novita Agent Runtime allows you to use your favorite frameworks and models, deploying with just a few lines of code and commands.

This repository provides samples and tutorials to help you quickly understand and integrate Novita Agent Runtime capabilities into your applications.

> [!IMPORTANT]
> The samples provided in this repository are for experimental and educational purposes only. They demonstrate concepts and techniques but are not intended for direct production use.

## 📁 Repository Structure

### 🔌 [`examples/agent-runtime/agentic-frameworks/`](./agentic-frameworks/)
**AI Agent Framework Integrations**

Demonstrates how to integrate Novita Agent Runtime with popular AI agent frameworks. Each framework sample includes complete implementation and detailed documentation.

**[LangGraph](./agentic-frameworks/langgraph/)**
**[AutoGen](./agentic-frameworks/autogen/)**
**[Google ADK](./agentic-frameworks/google-adk/)**
**[OpenAI Agents SDK](./agentic-frameworks/openai-agents-sdk/)**

Each sample includes:
- ✅ Complete agent implementation code
- ✅ Local development, testing, and deployment guide (in `README.md` file)
- ✅ Complete test suite (local and sandbox environments, in `tests` directory)

## 🚀 Quick Start

### Prerequisites

Before you begin, make sure you have:

- **Python 3.9+** and **Node.js 20+**
- **Novita AI API Key** - [Get it from console](https://novita.ai/settings/key-management)

### Step 1: Choose a Framework Sample

Select an AI agent framework you're familiar with to get started:

```bash
# Clone the repository
git clone git@github.com:novitalabs/Novita-CollabHub.git
cd Novita-CollabHub

# Navigate to your chosen framework directory
cd examples/agent-runtime/agentic-frameworks/langgraph  # or autogen, google-adk, openai-agents-sdk
```

### Step 2: Install Dependencies and Configure

```bash
# Create Python virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env file and add your API keys
```

### Step 3: Local Testing

```bash
# Start the agent
python app.py

# Test in another terminal
bash tests/test_local_basic.sh
```

Success! You should see responses from your agent.

### Step 4: Deploy to Novita Agent Runtime

```bash
# Install Novita Sandbox CLI
npm install novita-sandbox-cli@beta

# Configure and deploy (automatically creates all required resources)
npx novita-sandbox-cli agent configure
npx novita-sandbox-cli agent launch

# Test deployed agent, different projects may require different --env parameters
npx novita-sandbox-cli agent invoke "Hello, Agent!" --env NOVITA_API_KEY="<your-api-key>"
```

Congratulations! Your agent is now running on Novita Agent Runtime!

Check the detailed README documentation in each framework directory for more information.

## 💡 Features

### 🔄 Framework Agnostic
Use any AI agent framework - LangGraph, AutoGen, Google ADK, OpenAI Agents SDK, or others. Deploy directly without code modifications.

### 🤖 Model Agnostic
Support any LLM - OpenAI, Anthropic, Google Gemini, DeepSeek, or other compatible models. Choose the model that best fits your needs.

### ⚡ Rapid Deployment
One-click deployment with Novita Sandbox CLI. Automatically creates all required resources, from local development to production in minutes.

### 🔒 Secure and Reliable
Enterprise-grade security with sandboxed isolated runtime environment ensuring safe agent execution.

### 📊 Complete Testing
Each sample includes a complete test suite covering basic functionality, streaming responses, and multi-turn conversations.

### 📖 Comprehensive Documentation
Including detailed usage instructions, API references, and troubleshooting guides.

## 🔗 Related Resources

- [Novita Agent Runtime Documentation](https://novita.ai/docs/guides/sandbox-agent-runtime-introduction)
- [Novita Agent Sandbox Documentation](https://novita.ai/docs/guides/sandbox-overview)

## 🤝 Contributing

We welcome contributions! If you'd like to contribute code or improve the samples:

- Add new framework samples
- Improve existing samples
- Report issues
- Suggest improvements

Please submit an Issue or Pull Request.
---


