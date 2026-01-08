# 🛠️ Novita Sandbox × Claude SDK Developer Guide

## 🚀 Development Environment Setup

### Prerequisites

- **Node.js**: v20+ (LTS version recommended)
- **npm**: v9+
- **TypeScript**: Included in project, no global installation needed

### Install Dependencies

```bash
git clone <repo-url>
cd anthropic-ai-sdk-demo
npm install
```

### Environment Variables

Create a `.env` file (optional, you can also input interactively at runtime):

```bash
# Novita API Key, https://novita.ai/settings/key-management
NOVITA_API_KEY=your_api_key_here
```

---

## 🏃 Running & Debugging

### Development Mode

```bash
npm run agent
```

### Debug Mode

Enable verbose logging in the CLI:

```bash
📝 Your request > debug on
✅ Verbose logging enabled
```

When enabled, it outputs:

- Sandbox creation/destruction logs
- HTTP health check details
- Tool call parameters and responses
- Server process status

---

## 🏗️ Code Architecture

### Core Class: `SandboxAgent`

```
SandboxAgent
├── State Management
│   ├── sandbox: Sandbox | null         # Novita Sandbox instance
│   ├── anthropic: Anthropic | null     # Anthropic SDK client
│   ├── messages: MessageParam[]        # Conversation history
│   ├── serverHandle: CommandHandle     # HTTP server process handle
│   └── previewUrl: string | null       # Current preview URL
│
├── Lifecycle Methods
│   ├── initialize()                    # Create sandbox, register tools
│   ├── cleanup()                       # Clean up resources, close sandbox
│   └── refreshSandboxTimeout()         # Refresh sandbox timeout
│
├── Conversation Processing
│   ├── chat(userMessage)               # Main entry point (Agentic Loop)
│   ├── streamResponse()                # Stream response handling
│   └── processToolCalls()              # Tool call processing
│
└── Tool Implementations
    ├── handleWriteFile(input)          # Write file to sandbox
    └── handleGetPreviewUrl()           # Start server, get URL
```

### Agentic Loop Workflow

```
User Input
    │
    ▼
┌─────────────────┐
│ Refresh Sandbox │
│    Timeout      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Call Claude API │◄────────────────┐
└────────┬────────┘                 │
         │                          │
         ▼                          │
┌─────────────────┐                 │
│ Stream Response │                 │
└────────┬────────┘                 │
         │                          │
         ▼                          │
    ┌────────────┐                  │
    │ Tool Call? │                  │
    └─────┬──────┘                  │
     Yes  │   No                    │
          │    └──────► End         │
          ▼                         │
    ┌────────────┐                  │
    │ Execute    │                  │
    │   Tool     │                  │
    └─────┬──────┘                  │
          │                         │
          ▼                         │
    ┌────────────┐                  │
    │ Add Tool   │──────────────────┘
    │  Results   │
    └────────────┘
```

### Tool Definition Structure

```typescript
const TOOLS: Anthropic.Beta.Messages.BetaTool[] = [
  {
    name: "write_file",
    description: "Create or modify a file in the sandbox",
    input_schema: {
      type: "object",
      properties: {
        path: { type: "string", description: "File path" },
        content: { type: "string", description: "File content" },
      },
      required: ["path", "content"],
    },
  },
  {
    name: "get_preview_url",
    description: "Start server and get preview URL",
    input_schema: { type: "object", properties: {} },
  },
];
```

---

## 🔧 Extension Development

### Adding New Tools

1. **Define tool schema**:

```typescript
// Add to TOOLS array
{
  name: "run_command",
  description: "Execute a shell command in the sandbox",
  input_schema: {
    type: "object",
    properties: {
      command: { type: "string", description: "Command to execute" },
      timeout: { type: "number", description: "Timeout in ms" },
    },
    required: ["command"],
  },
}
```

2. **Implement tool handler**:

```typescript
private async handleRunCommand(input: unknown): Promise<string> {
  const { command, timeout = 30000 } = input as { command: string; timeout?: number };

  if (!this.sandbox) throw new Error("Sandbox not initialized");

  try {
    const result = await this.sandbox.commands.run(command, { timeout });
    return `stdout: ${result.stdout}\nstderr: ${result.stderr}`;
  } catch (error) {
    return `Execution failed: ${error instanceof Error ? error.message : String(error)}`;
  }
}
```

3. **Register the handler**:

```typescript
private registerToolHandlers(): void {
  this.toolHandlers.set("write_file", this.handleWriteFile.bind(this));
  this.toolHandlers.set("get_preview_url", this.handleGetPreviewUrl.bind(this));
  this.toolHandlers.set("run_command", this.handleRunCommand.bind(this));  // New
}
```

### Customizing System Prompt

Modify the `SYSTEM_PROMPT` constant to adjust AI behavior:

```typescript
const SYSTEM_PROMPT = `You are a professional frontend development assistant...

Additional rules:
6. All pages must support dark mode
7. Prefer CSS Grid for layouts
8. Add necessary ARIA attributes for accessibility`;
```

### Adjusting Configuration

```typescript
const CONFIG = {
  model: "zai-org/glm-4.7", // Change model
  maxTokens: 16384, // Adjust output length
  serverPort: 3000, // Change server port
  sandboxTimeoutMs: 10 * 60 * 1000, // Sandbox timeout
  healthCheck: {
    maxRetries: 30, // Health check retry count
    intervalMs: 2000, // Check interval
  },
} as const;
```

---

## 📦 Build & Release

### Build CommonJS Bundle (for debugging)

```bash
npm run build:cjs
```

### Build Cross-Platform Executables

```bash
npm run build:release
```

Uses pkg to generate platform-native executables and SHA256 checksums.

**Supported target platforms**:

- macOS x64 (Intel)
- macOS arm64 (Apple Silicon)
- Linux x64
- Windows x64

### Build Artifacts

```
release/
├── agent-macos-arm64      # macOS Apple Silicon
├── agent-macos-x64        # macOS Intel
├── agent-linux-x64        # Linux
├── agent-win-x64.exe      # Windows
├── agent-en-macos-arm64   # English version...
├── ...
└── checksums.txt          # SHA256 checksums
```

---

## 🔍 Core Mechanisms Deep Dive

### Context Management

Leverages Claude Beta API's `context-management` feature to automatically clean up long conversation history:

```typescript
const CONTEXT_MANAGEMENT_CONFIG = {
  edits: [
    {
      type: "clear_tool_uses_20250919",
      trigger: { type: "input_tokens", value: 10000 }, // Trigger when exceeding 10k tokens
      keep: { type: "tool_uses", value: 2 }, // Keep last 2 tool calls
      clear_tool_inputs: true, // Clear tool inputs
    },
  ],
};
```

**How it works**:

- When context exceeds 10,000 tokens, API automatically cleans up old tool call records
- Keeps the last 2 tool calls to ensure AI has sufficient context
- Prevents "memory pollution" that causes behavior degradation

### Server Self-Healing Mechanism

```typescript
// Check if process is alive
private async checkServerProcessAlive(): Promise<boolean> {
  const result = await this.sandbox.commands.run(
    `kill -0 ${this.serverHandle.pid} 2>/dev/null && echo "alive" || echo "dead"`
  );
  return result.stdout.trim() === "alive";
}

// Clean up port occupation
private async killPortProcess(port: number): Promise<void> {
  await this.sandbox.commands.run(
    `lsof -ti :${port} 2>/dev/null | xargs -r kill -9 2>/dev/null; echo "done"`
  );
}
```

### Streaming Response Handling

```typescript
for await (const event of stream) {
  if (event.type === "content_block_delta") {
    if (event.delta.type === "text_delta") {
      process.stdout.write(event.delta.text); // Real-time output
    } else if (event.delta.type === "input_json_delta") {
      // Stream tool parameters, show progress
    }
  }
}
```

---

## 🧪 Testing & Validation

### Manual Testing Checklist

- [ ] First launch, interactive API Key input
- [ ] Generate simple HTML page
- [ ] Multi-turn conversation to modify page
- [ ] `debug` command to view status
- [ ] `restart` command to restart server
- [ ] `cat index.html` to view file content
- [ ] Auto-restart after server timeout
- [ ] Auto-rebuild after sandbox destruction

### Debugging Tips

```bash
# Enable verbose logging
📝 Your request > debug on

# View complete status
📝 Your request > debug

# View generated files
📝 Your request > cat index.html

# If sandbox service is unresponsive
📝 Your request > restart
```

## 📚 Related Resources

- [Anthropic SDK Documentation](https://docs.anthropic.com/claude/reference/client-sdks)
- [Novita Sandbox API](https://novita.ai/docs/sandbox/overview)
- [Claude Context Management](https://platform.claude.com/docs/en/build-with-claude/context-editing)
- [pkg Packaging Tool](https://github.com/yao-pkg/pkg)
- [esbuild Documentation](https://esbuild.github.io/)

---
