# Browser-Use Remote Chromium Connection Solution

This is a complete solution that enables `browser-use` to connect locally via Chrome DevTools Protocol (CDP) to a remote Chromium instance running in an E2B sandbox.

## Core Problem

In cloud sandbox environments, `browser-use` connecting to remote Chromium faces two main challenges:

1. **Host Header Security Restriction** - Chromium rejects CDP connection requests from non-local domain names
2. **WebSocket URL Rewriting** - Need to rewrite internal addresses (`127.0.0.1:9222`) to externally accessible addresses

## Solution Architecture

### Overall Flow

```
Local browser-use → E2B External Domain:9223 → Go Reverse Proxy → Chromium:9222
```

### Core Components

1. **Manually Downloaded Chromium** - Latest version, avoiding package manager limitations
2. **Enhanced Go Reverse Proxy** - Intelligent handling of Host header and WebSocket URL rewriting  
3. **E2B Sandbox** - Provides containerized runtime environment

## Workflow

### 1. Container Startup Phase
- Download the latest Chromium binary files from Google official sources
- Start Chromium, bind to internal address `127.0.0.1:9222`
- Start Go reverse proxy, listen on external address `0.0.0.0:9223`

### 2. Connection Establishment Phase  
- `browser-use` initiates connection request to E2B external domain
- Reverse proxy intercepts the request, rewrites Host header to `127.0.0.1:9222`
- Chromium receives "local request", passes security validation

### 3. CDP Protocol Interaction Phase

`browser-use` follows the standard Chrome DevTools Protocol connection flow:

**Step 1: Get WebSocket Connection Info**
```
browser-use → GET https://9223-sandbox-host/json/version/
            ↓ (Reverse proxy rewrites Host header)
            → GET http://127.0.0.1:9222/json/version/
```

**Chrome Original Response:**
```json
{
  "Browser": "Chrome/138.0.7204.168",
  "webSocketDebuggerUrl": "ws://127.0.0.1:9222/devtools/browser/abc123"
}
```

**Reverse Proxy Dynamic Response Rewrite:**
```json
{
  "Browser": "Chrome/138.0.7204.168", 
  "webSocketDebuggerUrl": "wss://9223-sandbox-host/devtools/browser/abc123"
}
```

**Step 2: Establish WebSocket Connection**
```
browser-use → WSS wss://9223-sandbox-host/devtools/browser/abc123
            ↓ (Reverse proxy handles WebSocket upgrade + Host rewrite)
            → WS ws://127.0.0.1:9222/devtools/browser/abc123
```

**Key Rewrite Points:**
- `ws://` → `wss://` (E2B HTTPS environment requires secure WebSocket)
- `127.0.0.1:9222` → `9223-sandbox-host` (Rewrite to externally accessible address)
- Host header: `sandbox-host` → `127.0.0.1:9222` (Bypass Chromium security restrictions)

**Why Rewriting is Needed:**
- Chromium's security mechanism only allows local addresses to access CDP
- E2B sandbox provides services externally via HTTPS, requiring WSS protocol
- `browser-use` needs to obtain the correct external WebSocket URL to connect

### 4. Real-time Communication Phase
- After WebSocket connection is established, all CDP commands are transparently proxied
- `browser-use` sends operation commands (click, input, screenshot, etc.)
- Chromium returns page state and response data
- Reverse proxy ensures bidirectional communication stability

## Key Features

### 🛡️ Security Bypass
- Intelligent Host header rewriting to bypass Chromium security restrictions
- Support for multiple URL format recognition and conversion

### 🔌 Protocol Compatibility  
- Full support for HTTP and WebSocket protocols
- Automatic handling of `/json/version` and `/json` endpoints

### 📊 Production Ready
- Built-in health check (`/health`) and performance monitoring (`/metrics`)
- Configurable timeout, log levels, and other parameters

### 🎯 High Performance
- Only intercept and process necessary endpoints
- Other traffic is directly proxied transparently, minimizing overhead

## Deployment Methods

### One-Click Build (Recommended)
```bash
# Run one-click build script
./build.sh
```

The build script will automatically:
1. Check Go and E2B CLI dependencies
2. Compile Go reverse proxy to Linux x86 binary file  
3. Build E2B Template

### Manual Build
If manual build is needed, execute step by step:

```bash
# 1. Compile reverse proxy
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -ldflags="-s -w" -o reverse-proxy reverse-proxy.go

# 2. Build template
e2b template build -c "/app/.browser-use/start-up.sh"
```

### Local Connection
```python
from e2b_code_interpreter import Sandbox
from browser_use import Agent

# Create sandbox
sandbox = Sandbox(template="your-template-id")

# Get Chrome connection address (port 9223)
host = sandbox.get_host(9223)
cdp_url = f"https://{host}"

# Connect browser-use
agent = Agent(
    task="Your task",
    llm=llm,
    use_vision=True
)

# Use remote Chrome
result = agent.run(cdp_url=cdp_url)
```

## Network Architecture

```
┌─────────────────┐    HTTPS     ┌──────────────────┐
│   browser-use   │─────────────→│  E2B External    │
│     (Local)     │              │   Domain:9223    │
└─────────────────┘              └──────────────────┘
                                           │
                                           │ HTTP
                                           ▼
                                 ┌──────────────────┐
                                 │   Go Reverse     │
                                 │     Proxy        │
                                 │ (Host Rewrite)   │
                                 └──────────────────┘
                                           │
                                           │ HTTP  
                                           ▼
                                 ┌──────────────────┐
                                 │     Chromium     │
                                 │  127.0.0.1:9222  │
                                 └──────────────────┘
```

## Solution Advantages

- ✅ **Ready to Use** - One-time configuration, stable operation
- ✅ **Latest Version** - Always uses Google's latest Chromium build
- ✅ **Performance Optimized** - Precise interception, minimal proxy overhead  
- ✅ **Comprehensive Monitoring** - Built-in health checks and performance metrics
- ✅ **Container Friendly** - Specifically designed for Docker/E2B environments
- ✅ **Complete Protocol** - Full support for CDP's HTTP and WebSocket communication
