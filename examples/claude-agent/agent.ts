import "dotenv/config";
import Anthropic from "@anthropic-ai/sdk";
import { Sandbox, CommandHandle } from "novita-sandbox/code-interpreter";
import open from "open";
import * as readline from "readline";

// ============================================================================
// Types
// ============================================================================

interface WriteFileInput {
  path: string;
  content: string;
}

interface ToolHandler {
  (input: unknown): Promise<string>;
}

interface ToolResult {
  type: "tool_result";
  tool_use_id: string;
  content: string;
}

// ============================================================================
// Configuration
// ============================================================================

const CONFIG = {
  model: "zai-org/glm-4.7",
  maxTokens: 16384, // Increased to 16K to support long code
  serverPort: 3000,
  sandboxTimeoutMs: 10 * 60 * 1000, // 10 minutes
  maxContinueAttempts: 3, // Maximum 3 continuation attempts
  healthCheck: {
    maxRetries: 30,
    intervalMs: 2000,
    quickCheckRetries: 5,
    quickCheckIntervalMs: 500,
  },
} as const;

const SYSTEM_PROMPT = `You are a professional frontend development assistant, skilled in creating modern web pages using Tailwind CSS.

Rules:
1. When the user asks to create or modify a web page, use the write_file tool to write files
2. After writing files, use the get_preview_url tool to start the server and get the preview URL
3. When the user asks to modify an existing web page, directly modify the corresponding file, the server will update automatically
4. Always use Tailwind CSS CDN for quick styling
5. Code should be concise, modern, and beautiful`;

const TOOLS: Anthropic.Beta.Messages.BetaTool[] = [
  {
    name: "write_file",
    description: "Create or modify a file in the sandbox",
    input_schema: {
      type: "object",
      properties: {
        path: { type: "string", description: "File path, e.g., index.html" },
        content: { type: "string", description: "Complete file content" },
      },
      required: ["path", "content"],
    },
  },
  {
    name: "get_preview_url",
    description: "Start the web server and get the preview URL (returns existing URL if server is already running)",
    input_schema: { type: "object", properties: {} },
  },
];

const CONTEXT_MANAGEMENT_CONFIG = {
  edits: [
    {
      type: "clear_tool_uses_20250919" as const,
      trigger: { type: "input_tokens", value: 10000 },
      keep: { type: "tool_uses", value: 2 },
      clear_tool_inputs: true,
    },
  ],
};

// ============================================================================
// Utilities
// ============================================================================

// Global debug mode switch
let DEBUG_MODE = false;

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

function logDebug(context: string, message: string, data?: unknown): void {
  if (!DEBUG_MODE) return;
  
  const timestamp = new Date().toISOString().slice(11, 19); // Only show time HH:MM:SS
  console.log(`[${timestamp}] 🔍 [${context}] ${message}`);
  if (data !== undefined) {
    // Simplified output: only show key fields
    const simplified = simplifyDebugData(data);
    if (simplified) {
      console.log(`   └─ ${simplified}`);
    }
  }
}

function simplifyDebugData(data: unknown): string {
  if (typeof data !== "object" || data === null) {
    return String(data);
  }
  
  const obj = data as Record<string, unknown>;
  const parts: string[] = [];
  
  // Only show key fields
  const keyFields = ["status", "ok", "error", "pid", "url", "previewUrl", "isHealthy", "isReady", "sandboxId"];
  for (const key of keyFields) {
    if (key in obj) {
      parts.push(`${key}=${JSON.stringify(obj[key])}`);
    }
  }
  
  return parts.length > 0 ? parts.join(", ") : JSON.stringify(data);
}

async function waitForServer(
  url: string,
  maxRetries: number,
  intervalMs: number,
  silent = false
): Promise<boolean> {
  let spinner: Spinner | null = null;
  
  if (!silent) {
    spinner = new Spinner(`Waiting for server to be ready... (0/${maxRetries})`);
    spinner.start();
    logDebug("waitForServer", `Starting health check`, { url, maxRetries, intervalMs });
  }

  for (let i = 0; i < maxRetries; i++) {
    if (spinner) {
      spinner.update(`Waiting for server to be ready... (${i + 1}/${maxRetries})`);
    }
    
    try {
      const response = await fetch(url, { method: "HEAD" });
      if (!silent) {
        logDebug("waitForServer", `Received response`, { 
          attempt: i + 1, 
          status: response.status, 
          ok: response.ok,
          statusText: response.statusText
        });
      }
      if (response.ok) {
        if (spinner) {
          spinner.stop(`✅ Server is ready`);
        }
        return true;
      }
    } catch (error) {
      // Server not ready yet, continue retrying
      if (!silent) {
        logDebug("waitForServer", `Request failed (${i + 1}/${maxRetries})`, { 
          error: error instanceof Error ? error.message : String(error)
        });
      }
    }
    await sleep(intervalMs);
  }

  if (spinner) {
    spinner.stop(`❌ Server response timeout`);
  }
  if (!silent) {
    logDebug("waitForServer", `Health check failed, max retries reached`, { maxRetries });
  }
  return false;
}

async function openBrowser(url: string): Promise<void> {
  console.log(`🌐 Opening browser: ${url}`);
  await open(url);
}

function createReadlineInterface(): readline.Interface {
  return readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
}

// Spinner animation class
class Spinner {
  private frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"];
  private currentFrame = 0;
  private interval: ReturnType<typeof setInterval> | null = null;
  private message: string;

  constructor(message: string) {
    this.message = message;
  }

  start(): void {
    process.stdout.write(`\r${this.frames[0]} ${this.message}`);
    this.interval = setInterval(() => {
      this.currentFrame = (this.currentFrame + 1) % this.frames.length;
      process.stdout.write(`\r${this.frames[this.currentFrame]} ${this.message}`);
    }, 80);
  }

  update(message: string): void {
    this.message = message;
    process.stdout.write(`\r${this.frames[this.currentFrame]} ${this.message}   `);
  }

  stop(finalMessage?: string): void {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
    if (finalMessage) {
      process.stdout.write(`\r${finalMessage}\n`);
    } else {
      process.stdout.write("\r" + " ".repeat(this.message.length + 5) + "\r");
    }
  }
}

async function prompt(rl: readline.Interface, question: string): Promise<string> {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer);
    });
  });
}

function maskApiKey(key: string): string {
  if (key.length <= 8) return "****";
  return key.slice(0, 4) + "****" + key.slice(-4);
}

function isValidApiKey(key: string): boolean {
  // Simple validation: non-empty and reasonable length
  return key.trim().length >= 10;
}

// ============================================================================
// Agent Core
// ============================================================================

class SandboxAgent {
  private sandbox: Sandbox | null = null;
  private anthropic: Anthropic | null = null;
  private toolHandlers: Map<string, ToolHandler> = new Map();
  private messages: Anthropic.Beta.Messages.BetaMessageParam[] = [];
  private serverHandle: CommandHandle | null = null;
  private previewUrl: string | null = null;
  private browserOpened = false;
  private apiKey: string | null = null;

  constructor() {
    // Try to get API Key from environment variables
    this.apiKey = process.env.NOVITA_API_KEY || null;
  }

  hasApiKey(): boolean {
    return this.apiKey !== null && isValidApiKey(this.apiKey);
  }

  setApiKey(key: string): boolean {
    if (!isValidApiKey(key)) {
      return false;
    }
    this.apiKey = key.trim();
    this.anthropic = new Anthropic({
      baseURL: "https://api.novita.ai/anthropic",
      apiKey: this.apiKey,
    });
    console.log(`✅ API Key set: ${maskApiKey(this.apiKey)}`);
    return true;
  }

  getPreviewUrl(): string | null {
    return this.previewUrl;
  }

  async forceRestartServer(): Promise<void> {
    if (!this.sandbox) {
      console.log("⚠️  Sandbox not initialized");
      return;
    }
    await this.restartServer();
    if (this.previewUrl) {
      console.log(`🌐 Preview URL: ${this.previewUrl}`);
    }
  }

  private ensureAnthropicClient(): void {
    if (!this.anthropic) {
      if (!this.apiKey) {
        throw new Error("API Key not set");
      }
      this.anthropic = new Anthropic({
        baseURL: "https://api.novita.ai/anthropic",
        apiKey: this.apiKey,
      });
    }
  }

  async initialize(): Promise<void> {
    if (!this.apiKey) {
      throw new Error("API Key not set, cannot initialize sandbox");
    }

    const spinner = new Spinner("Initializing sandbox environment...");
    spinner.start();
    logDebug("initialize", "Starting sandbox creation", {
      timeoutMs: CONFIG.sandboxTimeoutMs,
      hasApiKey: !!this.apiKey,
    });

    this.sandbox = await Sandbox.create({
      apiKey: this.apiKey,
      timeoutMs: CONFIG.sandboxTimeoutMs,
    });

    const sandboxId = (this.sandbox as { id?: string }).id ?? "unknown";
    logDebug("initialize", "Sandbox created successfully", {
      sandboxId,
      timeoutMs: CONFIG.sandboxTimeoutMs,
    });
    spinner.stop(`✅ Sandbox started successfully (ID: ${sandboxId})\n`);

    this.registerToolHandlers();
  }

  private async refreshSandboxTimeout(): Promise<void> {
    logDebug("refreshSandboxTimeout", "Attempting to refresh sandbox timeout", {
      hasSandbox: !!this.sandbox,
      newTimeoutMs: CONFIG.sandboxTimeoutMs,
    });

    if (this.sandbox) {
      try {
        await this.sandbox.setTimeout(CONFIG.sandboxTimeoutMs);
        logDebug("refreshSandboxTimeout", "Sandbox timeout refreshed successfully");
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        console.error("⚠️  Failed to update sandbox timeout:", error);
        logDebug("refreshSandboxTimeout", "❌ Failed to refresh sandbox timeout", {
          error: errorMessage,
          stack: error instanceof Error ? error.stack : undefined,
        });

        // Check if sandbox was destroyed (404 Not Found)
        if (errorMessage.includes("404") || errorMessage.includes("not found")) {
          logDebug("refreshSandboxTimeout", "🔄 Sandbox was destroyed, recreating...", {
            hadPreviewUrl: !!this.previewUrl,
            hadServerHandle: !!this.serverHandle,
          });

          // Clean up old state
          this.clearSandboxState();

          // Recreate sandbox
          await this.recreateSandbox();
        }
      }
    } else {
      logDebug("refreshSandboxTimeout", "⚠️ Sandbox instance does not exist, creating new sandbox...");
      await this.recreateSandbox();
    }
  }

  private clearSandboxState(): void {
    logDebug("clearSandboxState", "Cleaning up old sandbox state", {
      hadPreviewUrl: !!this.previewUrl,
      hadServerHandle: !!this.serverHandle,
      oldPreviewUrl: this.previewUrl,
      oldServerPid: this.serverHandle?.pid ?? null,
    });

    this.sandbox = null;
    this.serverHandle = null;
    this.previewUrl = null;
    this.browserOpened = false;
  }

  private async recreateSandbox(): Promise<void> {
    if (!this.apiKey) {
      throw new Error("API Key not set, cannot create sandbox");
    }

    const spinner = new Spinner("Recreating sandbox environment...");
    spinner.start();
    logDebug("recreateSandbox", "Starting new sandbox creation", {
      timeoutMs: CONFIG.sandboxTimeoutMs,
      hasApiKey: !!this.apiKey,
    });

    try {
      this.sandbox = await Sandbox.create({
        apiKey: this.apiKey,
        timeoutMs: CONFIG.sandboxTimeoutMs,
      });

      const sandboxId = (this.sandbox as { id?: string }).id ?? "unknown";
      logDebug("recreateSandbox", "New sandbox created successfully", {
        sandboxId,
        timeoutMs: CONFIG.sandboxTimeoutMs,
      });
      spinner.stop(`✅ New sandbox created (ID: ${sandboxId})`);
      console.log("📝 Note: Previously created files have been lost and need to be regenerated\n");
    } catch (error) {
      spinner.stop("❌ Failed to create new sandbox");
      logDebug("recreateSandbox", "❌ Failed to create new sandbox", {
        error: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
      });
      console.error("Error details:", error);
      throw error;
    }
  }

  private registerToolHandlers(): void {
    this.toolHandlers.set("write_file", this.handleWriteFile.bind(this));
    this.toolHandlers.set("get_preview_url", this.handleGetPreviewUrl.bind(this));
  }

  private async checkServerProcessAlive(): Promise<boolean> {
    if (!this.sandbox || !this.serverHandle?.pid) {
      return false;
    }

    try {
      // Use kill -0 to check if process exists (doesn't actually kill the process)
      const result = await this.sandbox.commands.run(
        `kill -0 ${this.serverHandle.pid} 2>/dev/null && echo "alive" || echo "dead"`
      );
      const isAlive = result.stdout.trim() === "alive";
      logDebug("checkServerProcessAlive", "Process check result", {
        pid: this.serverHandle.pid,
        isAlive,
        stdout: result.stdout.trim(),
      });
      return isAlive;
    } catch (error) {
      logDebug("checkServerProcessAlive", "Process check failed", {
        error: error instanceof Error ? error.message : String(error),
      });
      return false;
    }
  }

  private async killPortProcess(port: number): Promise<void> {
    if (!this.sandbox) return;

    try {
      // Find and kill all processes using the specified port
      const result = await this.sandbox.commands.run(
        `lsof -ti :${port} 2>/dev/null | xargs -r kill -9 2>/dev/null; echo "done"`
      );
      logDebug("killPortProcess", "Cleaning up port", {
        port,
        result: result.stdout.trim(),
      });
      
      // Wait a short time to ensure processes are fully terminated
      await sleep(200);
    } catch (error) {
      // If no process is using the port, command may fail, which is normal
      logDebug("killPortProcess", "Error cleaning up port (can be ignored)", {
        port,
        error: error instanceof Error ? error.message : String(error),
      });
    }
  }

  private async restartServer(): Promise<void> {
    if (!this.sandbox) return;

    logDebug("restartServer", "Starting server restart", {
      oldPid: this.serverHandle?.pid ?? null,
    });

    // Clean up old state
    this.serverHandle = null;

    // Clean up port
    await this.killPortProcess(CONFIG.serverPort);

    // Start new server
    try {
      this.serverHandle = await this.sandbox.commands.run(
        `npx -y http-server . -p ${CONFIG.serverPort} -c-1`,
        {
          background: true,
          onStdout: (data) => {
            if (DEBUG_MODE) {
              console.log(`[server] ${data.trim()}`);
            }
          },
          onStderr: (data) => {
            if (DEBUG_MODE) {
              console.error(`[server:err] ${data.trim()}`);
            }
          },
        }
      );
      
      console.log(`🔄 Server restarted (PID: ${this.serverHandle.pid})`);
      logDebug("restartServer", "Server restarted successfully", {
        pid: this.serverHandle.pid,
      });

      // Wait for server to be ready
      if (this.previewUrl) {
        const isReady = await waitForServer(
          this.previewUrl,
          10, // Quick check 10 times
          500, // 500ms interval
          true // Silent mode
        );
        if (isReady) {
          console.log(`✅ Server is ready`);
          // Auto-refresh browser after 3 seconds to ensure server is fully stable
          console.log(`⏳ Auto-refreshing browser in 3 seconds...`);
          setTimeout(async () => {
            await this.refreshBrowser();
          }, 3000);
        } else {
          console.log(`⚠️  Server may not be fully ready, please refresh the page later`);
        }
      }
    } catch (error) {
      console.error(`❌ Server restart failed:`, error);
      logDebug("restartServer", "Server restart failed", {
        error: error instanceof Error ? error.message : String(error),
      });
    }
  }

  private async refreshBrowser(): Promise<void> {
    if (!this.previewUrl || !this.browserOpened) {
      return;
    }

    try {
      // Use AppleScript to refresh current browser tab (macOS)
      // This is more elegant than reopening URL, won't create new tab
      const { exec } = await import("child_process");
      const { promisify } = await import("util");
      const execAsync = promisify(exec);

      // Try to refresh Chrome
      const chromeScript = `
        tell application "Google Chrome"
          if (count of windows) > 0 then
            tell active tab of front window
              reload
            end tell
          end if
        end tell
      `;

      await execAsync(`osascript -e '${chromeScript}'`).catch(() => {
        // Chrome may not be running, ignore error
      });

      console.log(`🔄 Refresh request sent to browser`);
      logDebug("refreshBrowser", "Browser refresh request sent");
    } catch (error) {
      // If refresh fails, don't affect main flow
      logDebug("refreshBrowser", "Browser refresh failed (can be ignored)", {
        error: error instanceof Error ? error.message : String(error),
      });
    }
  }

  private async handleWriteFile(input: unknown): Promise<string> {
    logDebug("handleWriteFile", "Starting file write", {
      hasSandbox: !!this.sandbox,
    });

    if (!this.sandbox) throw new Error("Sandbox not initialized");

    const { path, content } = input as WriteFileInput;

    try {
      await this.sandbox.files.write(path, content);
      console.log(`📝 File written: ${path}`);
      logDebug("handleWriteFile", "File written successfully", {
        path,
        contentLength: content.length,
      });

      // If it's an HTML file, check server status and restart if necessary
      if (path.endsWith(".html") && this.previewUrl) {
        const processAlive = await this.checkServerProcessAlive();
        if (!processAlive) {
          console.log(`⚠️  Server stopped, auto-restarting...`);
          setTimeout(async () => {
            await this.restartServer();
          }, 5000);
        }
      }

      return `File ${path} has been successfully written to sandbox`;
    } catch (error) {
      logDebug("handleWriteFile", "❌ File write failed", {
        path,
        error: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
      });
      throw error;
    }
  }

  private async handleGetPreviewUrl(): Promise<string> {
    logDebug("handleGetPreviewUrl", "Starting get preview URL request", {
      hasSandbox: !!this.sandbox,
      hasPreviewUrl: !!this.previewUrl,
      hasServerHandle: !!this.serverHandle,
      currentPreviewUrl: this.previewUrl,
      serverPid: this.serverHandle?.pid ?? null,
    });

    if (!this.sandbox) throw new Error("Sandbox not initialized");

    // Check sandbox status
    try {
      const sandboxHost = this.sandbox.getHost(CONFIG.serverPort);
      logDebug("handleGetPreviewUrl", "Sandbox status check", {
        sandboxHost,
        sandboxId: (this.sandbox as { id?: string }).id ?? "unknown",
      });
    } catch (error) {
      logDebug("handleGetPreviewUrl", "⚠️ Sandbox status check failed", {
        error: error instanceof Error ? error.message : String(error),
      });
    }

    let serverAlreadyRunning = !!(this.previewUrl && this.serverHandle);
    logDebug("handleGetPreviewUrl", "Server running status", {
      serverAlreadyRunning,
    });

    // First verify if process is actually alive
    if (serverAlreadyRunning) {
      const processAlive = await this.checkServerProcessAlive();
      if (!processAlive) {
        console.log(`⚠️  Server process has exited (PID: ${this.serverHandle!.pid}), need to restart...`);
        logDebug("handleGetPreviewUrl", "Server process has exited, cleaning up state", {
          oldPid: this.serverHandle!.pid,
        });
        this.serverHandle = null;
        this.previewUrl = null;
        serverAlreadyRunning = false;
      }
    }

    if (serverAlreadyRunning) {
      console.log(`📋 Server already running, PID: ${this.serverHandle!.pid}`);

      logDebug("handleGetPreviewUrl", "Starting quick health check", {
        url: this.previewUrl,
        retries: CONFIG.healthCheck.quickCheckRetries,
        intervalMs: CONFIG.healthCheck.quickCheckIntervalMs,
      });

      // Quick health check to ensure service is still responding
      const isHealthy = await waitForServer(
        this.previewUrl!,
        CONFIG.healthCheck.quickCheckRetries,
        CONFIG.healthCheck.quickCheckIntervalMs,
        false // Changed to false, output detailed logs
      );

      logDebug("handleGetPreviewUrl", "Health check result", { isHealthy });

      if (isHealthy) {
        console.log(`✅ Server responding normally`);
        return `Preview URL: ${this.previewUrl} (refresh browser to see updates)`;
      }

      // Server not responding, need to restart
      console.log(`⚠️  Server not responding, restarting...`);
      logDebug("handleGetPreviewUrl", "Server not responding, preparing to restart", {
        oldPid: this.serverHandle!.pid,
        oldUrl: this.previewUrl,
      });

      try {
        await this.serverHandle!.kill();
        logDebug("handleGetPreviewUrl", "Old server process terminated");
      } catch (error) {
        logDebug("handleGetPreviewUrl", "Error terminating old server process (can be ignored)", {
          error: error instanceof Error ? error.message : String(error),
        });
      }
      this.serverHandle = null;
      this.previewUrl = null;
    }

    console.log("🔧 Starting HTTP server...");
    logDebug("handleGetPreviewUrl", "Preparing to start new HTTP server", {
      port: CONFIG.serverPort,
    });

    // First clean up processes that may be using the port
    await this.killPortProcess(CONFIG.serverPort);

    // Start background server
    try {
      this.serverHandle = await this.sandbox.commands.run(
        `npx -y http-server . -p ${CONFIG.serverPort} -c-1`,
        {
          background: true,
          onStdout: (data) => {
            console.log(`[server] ${data.trim()}`);
            logDebug("server:stdout", data.trim());
          },
          onStderr: (data) => {
            console.error(`[server:err] ${data.trim()}`);
            logDebug("server:stderr", data.trim());
          },
        }
      );
      console.log(`📋 Server process PID: ${this.serverHandle.pid}`);
      logDebug("handleGetPreviewUrl", "Server process started", {
        pid: this.serverHandle.pid,
      });
    } catch (error) {
      logDebug("handleGetPreviewUrl", "❌ Failed to start server", {
        error: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
      });
      throw error;
    }

    // Get preview URL
    try {
      const host = this.sandbox.getHost(CONFIG.serverPort);
      this.previewUrl = `https://${host}`;
      logDebug("handleGetPreviewUrl", "Preview URL generated", {
        host,
        previewUrl: this.previewUrl,
      });
    } catch (error) {
      logDebug("handleGetPreviewUrl", "❌ Failed to get preview URL", {
        error: error instanceof Error ? error.message : String(error),
      });
      throw error;
    }

    // Health check
    logDebug("handleGetPreviewUrl", "Starting full health check", {
      url: this.previewUrl,
      maxRetries: CONFIG.healthCheck.maxRetries,
      intervalMs: CONFIG.healthCheck.intervalMs,
    });

    const isReady = await waitForServer(
      this.previewUrl,
      CONFIG.healthCheck.maxRetries,
      CONFIG.healthCheck.intervalMs
    );

    logDebug("handleGetPreviewUrl", "Health check completed", {
      isReady,
      browserOpened: this.browserOpened,
    });

    if (isReady && !this.browserOpened) {
      await openBrowser(this.previewUrl);
      this.browserOpened = true;
      return `Preview URL: ${this.previewUrl}`;
    }

    if (isReady) {
      return `Preview URL: ${this.previewUrl} (refresh browser to see updates)`;
    }

    logDebug("handleGetPreviewUrl", "⚠️ Server started but health check did not pass", {
      previewUrl: this.previewUrl,
    });
    return `Preview URL generated but server may not be ready: ${this.previewUrl}`;
  }

  async chat(userMessage: string): Promise<void> {
    logDebug("chat", "Starting to process user message", {
      messageLength: userMessage.length,
      currentState: {
        hasSandbox: !!this.sandbox,
        hasPreviewUrl: !!this.previewUrl,
        hasServerHandle: !!this.serverHandle,
        previewUrl: this.previewUrl,
        serverPid: this.serverHandle?.pid ?? null,
      },
    });

    this.ensureAnthropicClient();

    // Refresh sandbox timeout on each user input
    await this.refreshSandboxTimeout();

    console.log("\n" + "─".repeat(60));

    // Add user message
    this.messages.push({ role: "user", content: userMessage });

    // Agentic Loop - continue processing until no tool calls
    let continueLoop = true;
    while (continueLoop) {
      // Show waiting animation
      const waitingSpinner = new Spinner("AI is thinking...");
      waitingSpinner.start();

      // Use streaming output
      const { response, assistantContent } = await this.streamResponse(waitingSpinner);

      logDebug("chat", "Response completed", {
        stopReason: response.stop_reason,
        contentBlocks: assistantContent.length,
      });

      // Add assistant response to message history
      this.messages.push({ role: "assistant", content: assistantContent });

      // Check if truncated due to max_tokens
      if (response.stop_reason === "max_tokens") {
        console.log("\n⚠️  Output truncated, continuing generation...");
        // Add continuation prompt
        this.messages.push({ 
          role: "user", 
          content: "Please continue output from where it was truncated (do not repeat already output content)" 
        });
        continueLoop = true;
        continue;
      }

      // Process tool calls
      const { hasToolUse, toolResults } = await this.processToolCalls(assistantContent);

      // If there are tool calls, add tool results and continue loop
      if (hasToolUse && toolResults.length > 0) {
        this.messages.push({ role: "user", content: toolResults });
        continueLoop = true;
      } else {
        continueLoop = false;
      }

      // If response is end_turn, stop loop
      if (response.stop_reason === "end_turn") {
        continueLoop = false;
      }
    }
  }

  private async streamResponse(waitingSpinner?: Spinner): Promise<{
    response: { stop_reason: string | null };
    assistantContent: Anthropic.Beta.Messages.BetaContentBlockParam[];
  }> {
    const assistantContent: Anthropic.Beta.Messages.BetaContentBlockParam[] = [];
    let currentTextBlock = "";
    let currentToolUse: { id: string; name: string; input: string } | null = null;
    let stopReason: string | null = null;
    let isFirstText = true;
    let spinnerStopped = false;

    const stream = this.anthropic!.beta.messages.stream({
      model: CONFIG.model,
      max_tokens: CONFIG.maxTokens,
      system: SYSTEM_PROMPT,
      betas: ["context-management-2025-06-27"],
      tools: TOOLS,
      messages: this.messages,
    } as Parameters<typeof Anthropic.prototype.beta.messages.stream>[0]);

    // For showing write_file progress
    let lastProgressUpdate = 0;
    const PROGRESS_INTERVAL = 500; // Update progress every 500ms

    for await (const event of stream) {
      // Stop waiting animation when first event is received
      if (waitingSpinner && !spinnerStopped) {
        waitingSpinner.stop();
        spinnerStopped = true;
        process.stdout.write("🤖 ");
      }

      if (event.type === "content_block_start") {
        if (event.content_block.type === "text") {
          currentTextBlock = "";
          if (isFirstText) {
            process.stdout.write("💬 ");
            isFirstText = false;
          }
        } else if (event.content_block.type === "tool_use") {
          currentToolUse = {
            id: event.content_block.id,
            name: event.content_block.name,
            input: "",
          };
          // Show tool call starting
          if (event.content_block.name === "write_file") {
            process.stdout.write(`\n📝 Generating file content...`);
          } else {
            console.log(`\n🔨 Calling tool: ${event.content_block.name}`);
          }
        }
      } else if (event.type === "content_block_delta") {
        if (event.delta.type === "text_delta") {
          // Real-time text output
          process.stdout.write(event.delta.text);
          currentTextBlock += event.delta.text;
        } else if (event.delta.type === "input_json_delta") {
          if (currentToolUse) {
            currentToolUse.input += event.delta.partial_json;
            
            // For write_file, show generation progress
            if (currentToolUse.name === "write_file") {
              const now = Date.now();
              if (now - lastProgressUpdate > PROGRESS_INTERVAL) {
                const size = currentToolUse.input.length;
                const sizeStr = size > 1024 ? `${(size / 1024).toFixed(1)}KB` : `${size}B`;
                process.stdout.write(`\r📝 Generating file content... ${sizeStr}`);
                lastProgressUpdate = now;
              }
            }
          }
        }
      } else if (event.type === "content_block_stop") {
        if (currentTextBlock) {
          assistantContent.push({ type: "text", text: currentTextBlock });
          currentTextBlock = "";
        }
        if (currentToolUse) {
          try {
            const parsedInput = JSON.parse(currentToolUse.input || "{}");
            assistantContent.push({
              type: "tool_use",
              id: currentToolUse.id,
              name: currentToolUse.name,
              input: parsedInput,
            });
            
            // Show tool call completion info
            if (currentToolUse.name === "write_file" && parsedInput.path) {
              const contentSize = (parsedInput.content || "").length;
              const sizeStr = contentSize > 1024 ? `${(contentSize / 1024).toFixed(1)}KB` : `${contentSize}B`;
              console.log(`\r📝 Generation complete: ${parsedInput.path} (${sizeStr})`);
            }
          } catch {
            // If JSON parsing fails, use empty object
            assistantContent.push({
              type: "tool_use",
              id: currentToolUse.id,
              name: currentToolUse.name,
              input: {},
            });
            console.log(`\n⚠️ Tool parameter parsing failed`);
          }
          currentToolUse = null;
        }
      } else if (event.type === "message_stop") {
        // Message ended
      } else if (event.type === "message_delta") {
        stopReason = event.delta.stop_reason;
      }
    }

    // Ensure newline
    console.log("");

    return {
      response: { stop_reason: stopReason },
      assistantContent,
    };
  }

  private async processToolCalls(
    assistantContent: Anthropic.Beta.Messages.BetaContentBlockParam[]
  ): Promise<{
    hasToolUse: boolean;
    toolResults: ToolResult[];
  }> {
    const toolResults: ToolResult[] = [];
    let hasToolUse = false;

    for (const block of assistantContent) {
      if (block.type === "tool_use") {
        hasToolUse = true;
        const result = await this.executeTool(block.name, block.input);
        toolResults.push({
          type: "tool_result",
          tool_use_id: block.id,
          content: result,
        });
      }
    }

    return { hasToolUse, toolResults };
  }

  private async executeTool(name: string, input: unknown): Promise<string> {
    const handler = this.toolHandlers.get(name);

    if (!handler) {
      console.error(`❌ Unknown tool: ${name}`);
      return `Error: Unknown tool ${name}`;
    }

    console.log(`\n🔨 Executing tool: ${name}`);
    try {
      const result = await handler(input);
      console.log(`✅ Tool execution successful`);
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error(`❌ Tool execution failed:`, errorMessage);
      return `Error: ${errorMessage}`;
    }
  }

  clearHistory(): void {
    this.messages = [];
  }

  // ==================== Debug Features ====================

  async listSandboxFiles(): Promise<string[]> {
    if (!this.sandbox) {
      console.log("⚠️  Sandbox not initialized");
      return [];
    }

    try {
      const files = await this.sandbox.files.list(".");
      return files.map((f) => f.name);
    } catch (error) {
      console.error("❌ Failed to get file list:", error);
      return [];
    }
  }

  async readSandboxFile(path: string): Promise<string | null> {
    if (!this.sandbox) {
      console.log("⚠️  Sandbox not initialized");
      return null;
    }

    try {
      const content = await this.sandbox.files.read(path);
      return content;
    } catch (error) {
      console.error(`❌ Failed to read file ${path}:`, error);
      return null;
    }
  }

  async getServerStatus(): Promise<{ running: boolean; pid: number | null; url: string | null }> {
    const status = {
      running: false,
      pid: this.serverHandle?.pid ?? null,
      url: this.previewUrl,
    };

    if (!this.previewUrl) {
      return status;
    }

    try {
      const response = await fetch(this.previewUrl, { 
        method: "HEAD",
        signal: AbortSignal.timeout(3000),
      });
      status.running = response.ok;
    } catch {
      status.running = false;
    }

    return status;
  }

  async showDebugInfo(): Promise<void> {
    console.log("\n" + "═".repeat(60));
    console.log("🔧 Debug Information");
    console.log("═".repeat(60));

    // Sandbox status
    const sandboxId = this.sandbox ? (this.sandbox as { id?: string }).id ?? "unknown" : "not initialized";
    console.log(`\n📦 Sandbox Status:`);
    console.log(`   ID: ${sandboxId}`);
    console.log(`   Instance: ${this.sandbox ? "✅ exists" : "❌ not exists"}`);

    // Server status
    const serverStatus = await this.getServerStatus();
    const processAlive = await this.checkServerProcessAlive();
    console.log(`\n🌐 Server Status:`);
    console.log(`   PID: ${serverStatus.pid ?? "none"}`);
    console.log(`   URL: ${serverStatus.url ?? "none"}`);
    console.log(`   Process alive: ${processAlive ? "✅ yes" : "❌ no"}`);
    console.log(`   HTTP response: ${serverStatus.running ? "✅ normal" : "❌ no response"}`);

    // If process doesn't exist but has PID, show diagnostic info and offer restart
    if (serverStatus.pid && !processAlive) {
      console.log(`   ⚠️  Diagnosis: Process ${serverStatus.pid} has exited`);
      console.log(`   💡 Tip: Type 'restart' to manually restart the server`);
    }

    // View processes running in sandbox
    if (this.sandbox) {
      console.log(`\n🔍 Sandbox Processes (http-server related):`);
      try {
        const result = await this.sandbox.commands.run(`ps aux | grep -E "http-server|node" | grep -v grep | head -5`);
        if (result.stdout.trim()) {
          const lines = result.stdout.trim().split("\n");
          lines.forEach((line) => {
            // Simplified output, only show key info
            const parts = line.trim().split(/\s+/);
            if (parts.length >= 11) {
              const pid = parts[1];
              const cmd = parts.slice(10).join(" ").slice(0, 50);
              console.log(`   PID ${pid}: ${cmd}${cmd.length >= 50 ? "..." : ""}`);
            }
          });
        } else {
          console.log("   (no http-server related processes)");
        }
      } catch {
        console.log("   (unable to get process list)");
      }
    }

    // File list
    console.log(`\n📁 Sandbox Files:`);
    const files = await this.listSandboxFiles();
    if (files.length === 0) {
      console.log("   (empty)");
    } else {
      files.forEach((f) => console.log(`   - ${f}`));
    }

    // Debug mode
    console.log(`\n⚙️  Debug Mode: ${DEBUG_MODE ? "✅ enabled" : "❌ disabled"}`);
    console.log("═".repeat(60) + "\n");
  }

  async cleanup(spinner?: Spinner): Promise<void> {
    logDebug("cleanup", "Starting resource cleanup", {
      hasServerHandle: !!this.serverHandle,
      hasSandbox: !!this.sandbox,
      serverPid: this.serverHandle?.pid ?? null,
    });

    if (this.serverHandle) {
      spinner?.update("Stopping server...");
      try {
        await this.serverHandle.kill();
        logDebug("cleanup", "Server process stopped");
      } catch (error) {
        logDebug("cleanup", "Error stopping server (can be ignored)", {
          error: error instanceof Error ? error.message : String(error),
        });
      }
    }

    if (this.sandbox) {
      spinner?.update("Cleaning up sandbox resources...");
      try {
        await this.sandbox.kill();
        logDebug("cleanup", "Sandbox closed successfully");
      } catch (error) {
        logDebug("cleanup", "Error closing sandbox", {
          error: error instanceof Error ? error.message : String(error),
        });
      }
    }
  }
}

// ============================================================================
// Interactive CLI
// ============================================================================

function printWelcome(): void {
  console.log("");
  console.log("╔══════════════════════════════════════════════════════════════╗");
  console.log("║       🚀 Novita Sandbox × Claude Interactive Dev Assistant      ║");
  console.log("╠══════════════════════════════════════════════════════════════╣");
  console.log("║  Enter your requirements, AI will auto-generate and deploy   ║");
  console.log("╠══════════════════════════════════════════════════════════════╣");
  console.log("║  Commands:                                                    ║");
  console.log("║    exit, quit     - Exit program                              ║");
  console.log("║    clear          - Clear conversation history                ║");
  console.log("║    url            - View current preview URL                  ║");
  console.log("║    key <api_key>  - Set API Key                               ║");
  console.log("║    debug          - View debug info (sandbox/server/files)    ║");
  console.log("║    debug on/off   - Enable/disable detailed logging           ║");
  console.log("║    cat <file>     - View file content in sandbox              ║");
  console.log("║    restart        - Restart HTTP server                       ║");
  console.log("╚══════════════════════════════════════════════════════════════╝");
  console.log("");
}

function normalizeApiKey(input: string): string {
  let key = input.trim();
  // Auto-remove "key " prefix that user might accidentally include
  if (key.toLowerCase().startsWith("key ")) {
    key = key.slice(4).trim();
  }
  return key;
}

async function promptForApiKey(rl: readline.Interface): Promise<string> {
  console.log("⚠️  API Key not detected, please enter your Novita API Key:");
  console.log("   (Available from https://novita.ai)");
  console.log("");

  while (true) {
    const key = await prompt(rl, "🔑 API Key > ");
    const normalizedKey = normalizeApiKey(key);

    if (normalizedKey.toLowerCase() === "exit" || normalizedKey.toLowerCase() === "quit") {
      return "";
    }

    if (isValidApiKey(normalizedKey)) {
      return normalizedKey;
    }

    console.log("❌ Invalid API Key, please try again (at least 10 characters)");
  }
}

async function runInteractiveMode(): Promise<void> {
  const agent = new SandboxAgent();
  const rl = createReadlineInterface();

  printWelcome();

  try {
    // Check API Key
    if (!agent.hasApiKey()) {
      const apiKey = await promptForApiKey(rl);
      if (!apiKey) {
        console.log("\n👋 Goodbye!");
        rl.close();
        return;
      }
      agent.setApiKey(apiKey);
      console.log("");
    } else {
      console.log("✅ API Key loaded from environment variables");
      console.log("");
    }

    await agent.initialize();

    // Interactive loop
    while (true) {
      const userInput = await prompt(rl, "📝 Your request > ");
      const trimmedInput = userInput.trim();

      // Handle special commands
      if (!trimmedInput) {
        continue;
      }

      // Exit command
      if (trimmedInput.toLowerCase() === "exit" || trimmedInput.toLowerCase() === "quit") {
        console.log("\n👋 Goodbye!");
        break;
      }

      // Clear history command
      if (trimmedInput.toLowerCase() === "clear") {
        agent.clearHistory();
        console.log("🗑️  Conversation history cleared");
        continue;
      }

      // View URL command
      if (trimmedInput.toLowerCase() === "url") {
        const url = agent.getPreviewUrl();
        if (url) {
          console.log(`🌐 Current preview URL: ${url}`);
        } else {
          console.log("⚠️  Server not started yet, please create a web page first");
        }
        continue;
      }

      // Set API Key command
      if (trimmedInput.toLowerCase().startsWith("key ")) {
        const newKey = trimmedInput.slice(4).trim();
        if (agent.setApiKey(newKey)) {
          console.log("🔄 API Key updated");
        } else {
          console.log("❌ Invalid API Key");
        }
        continue;
      }

      // Debug command
      if (trimmedInput.toLowerCase() === "debug") {
        await agent.showDebugInfo();
        continue;
      }

      // Enable/disable detailed logging
      if (trimmedInput.toLowerCase() === "debug on") {
        DEBUG_MODE = true;
        console.log("✅ Detailed logging enabled");
        continue;
      }

      if (trimmedInput.toLowerCase() === "debug off") {
        DEBUG_MODE = false;
        console.log("✅ Detailed logging disabled");
        continue;
      }

      // View file content command
      if (trimmedInput.toLowerCase().startsWith("cat ")) {
        const filePath = trimmedInput.slice(4).trim();
        if (!filePath) {
          console.log("⚠️  Please specify file path, e.g.: cat index.html");
          continue;
        }
        const content = await agent.readSandboxFile(filePath);
        if (content) {
          console.log("\n" + "─".repeat(60));
          console.log(`📄 File content: ${filePath}`);
          console.log("─".repeat(60));
          // Limit output length to avoid flooding screen
          const maxLines = 100;
          const lines = content.split("\n");
          if (lines.length > maxLines) {
            console.log(lines.slice(0, maxLines).join("\n"));
            console.log(`\n... (omitted ${lines.length - maxLines} lines, total ${lines.length} lines)`);
          } else {
            console.log(content);
          }
          console.log("─".repeat(60) + "\n");
        }
        continue;
      }

      // Restart server command
      if (trimmedInput.toLowerCase() === "restart") {
        if (!agent.getPreviewUrl()) {
          console.log("⚠️  Server not started yet, please create a web page first");
          continue;
        }
        console.log("🔄 Restarting server...");
        await agent.forceRestartServer();
        continue;
      }

      // Normal conversation
      try {
        await agent.chat(trimmedInput);
      } catch (error) {
        if (error instanceof Error && error.message.includes("API Key")) {
          console.log("❌ API Key invalid or expired, please use 'key <your_api_key>' to set a new Key");
        } else {
          console.error("💥 Error processing request:", error);
        }
      }
    }
  } catch (error) {
    console.error("💥 Runtime error:", error);
  } finally {
    rl.close();
    const spinner = new Spinner("Exiting, please wait...");
    spinner.start();
    await agent.cleanup(spinner);
    spinner.stop("✅ Exited, goodbye!");
    process.exit(0);
  }
}

// ============================================================================
// Main Entry
// ============================================================================

runInteractiveMode();

