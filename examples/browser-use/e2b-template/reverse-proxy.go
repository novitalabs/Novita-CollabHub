package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"net/http/httputil"
	"net/url"
	"strconv"
	"strings"
	"time"
)

var (
	targetPort  int
	listenPort  int
	enableDebug bool
	timeout     int
)

func main() {
	flag.IntVar(&targetPort, "targetPort", 9222, "Target Chrome DevTools port")
	flag.IntVar(&listenPort, "listenPort", 9223, "Listen port for proxy")
	flag.BoolVar(&enableDebug, "debug", true, "Enable debug logging")
	flag.IntVar(&timeout, "timeout", 30, "HTTP client timeout in seconds")
	flag.Parse()

	if !enableDebug {
		log.SetOutput(io.Discard)
	}

	log.Printf("🚀 Starting Enhanced Chrome DevTools Reverse Proxy")
	log.Printf("📡 Listen Port: %d", listenPort)
	log.Printf("🎯 Target Port: %d (Chrome DevTools)", targetPort)
	log.Printf("🐛 Debug Mode: %v", enableDebug)
	log.Printf("⏱️  Request Timeout: %ds", timeout)
	log.Printf("=====================================")

	chromeDevToolsClient := NewChromeDevToolsClient(targetPort, timeout)

	server := &http.Server{
		Addr:         fmt.Sprintf(":%d", listenPort),
		Handler:      chromeDevToolsClient,
		ReadTimeout:  time.Duration(timeout) * time.Second,
		WriteTimeout: time.Duration(timeout) * time.Second,
	}

	log.Printf("✅ Proxy server started, waiting for connections...")
	log.Fatal(server.ListenAndServe())
}

type ChromeDevToolsClient struct {
	targetHostPort string
	client         *http.Client
	proxy          *httputil.ReverseProxy
	// Performance metrics
	requestCount int64
	errorCount   int64
	startTime    time.Time
}

func NewChromeDevToolsClient(port, timeoutSec int) *ChromeDevToolsClient {
	hostPort := net.JoinHostPort("localhost", strconv.Itoa(port))

	client := &http.Client{
		Timeout: time.Duration(timeoutSec) * time.Second,
	}

	targetURL := &url.URL{Scheme: "http", Host: hostPort}
	proxy := httputil.NewSingleHostReverseProxy(targetURL)

	// Enhance proxy Director to handle WebSocket
	originalDirector := proxy.Director
	proxy.Director = func(req *http.Request) {
		originalDirector(req)

		// Check WebSocket upgrade request
		if isWebSocketUpgrade(req) {
			log.Printf("🔌 WebSocket upgrade request: %s %s", req.Method, req.URL.Path)
			// Ensure WebSocket headers are correctly set
			req.Header.Set("Connection", "Upgrade")
			req.Header.Set("Upgrade", "websocket")
		}
	}

	return &ChromeDevToolsClient{
		targetHostPort: hostPort,
		client:         client,
		proxy:          proxy,
		startTime:      time.Now(),
	}
}

func (c *ChromeDevToolsClient) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	c.requestCount++

	// Enhanced logging
	start := time.Now()
	log.Printf("📥 [%s] %s %s (from: %s)", r.Method, r.URL.Path, r.URL.RawQuery, r.RemoteAddr)

	defer func() {
		duration := time.Since(start)
		log.Printf("📤 Request completed - duration: %v", duration)
	}()

	// Handle special endpoints
	switch {
	case r.Method == http.MethodGet && r.URL.Path == "/health":
		c.handleHealth(w, r)
		return
	case r.Method == http.MethodGet && r.URL.Path == "/metrics":
		c.handleMetrics(w, r)
		return
	case r.Method == http.MethodGet && (r.URL.Path == "/json/version" || r.URL.Path == "/json/version/"):
		c.handleJsonVersion(w, r)
		return
	case r.Method == http.MethodGet && (r.URL.Path == "/json" || r.URL.Path == "/json/" || r.URL.Path == "/json/list"):
		c.handleJsonList(w, r)
		return
	case isWebSocketUpgrade(r):
		log.Printf("🔌 Direct proxy WebSocket connection: %s", r.URL.Path)
		c.proxy.ServeHTTP(w, r)
		return
	default:
		// Other requests go directly to proxy
		c.proxy.ServeHTTP(w, r)
		return
	}
}

// Health check endpoint
func (c *ChromeDevToolsClient) handleHealth(w http.ResponseWriter, r *http.Request) {
	// Check connection to Chrome
	resp, err := c.client.Get(fmt.Sprintf("http://%s/json/version", c.targetHostPort))
	if err != nil {
		w.WriteHeader(http.StatusServiceUnavailable)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status": "unhealthy",
			"error":  err.Error(),
		})
		return
	}
	resp.Body.Close()

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":    "healthy",
		"uptime":    time.Since(c.startTime).String(),
		"target":    c.targetHostPort,
		"timestamp": time.Now().Unix(),
	})
}

// Performance metrics endpoint
func (c *ChromeDevToolsClient) handleMetrics(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"requests_total": c.requestCount,
		"errors_total":   c.errorCount,
		"uptime_seconds": time.Since(c.startTime).Seconds(),
		"target_host":    c.targetHostPort,
	})
}

/*
Handle /json/version endpoint
Response format example:

	{
	   "Browser": "Chrome/138.0.7204.168",
	   "Protocol-Version": "1.3",
	   "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36...",
	   "V8-Version": "13.8.258.29",
	   "WebKit-Version": "537.36 (@3e8d82e86e9f508e88ed406c2a24657a6c691d30)",
	   "webSocketDebuggerUrl": "ws://127.0.0.1:9222/devtools/browser/cd1460bb-b92a-48c4-b9a4-2f9d2bb56eb9"
	}
*/
func (c *ChromeDevToolsClient) handleJsonVersion(w http.ResponseWriter, r *http.Request) {
	publicHostPort := r.Host
	log.Printf("🔄 Processing /json/version - Public address: %s, Target address: %s", publicHostPort, c.targetHostPort)

	resp, err := c.client.Get(fmt.Sprintf("http://%s/json/version", c.targetHostPort))
	if err != nil {
		c.errorCount++
		log.Printf("❌ Failed to get JSON version: %v", err)
		http.Error(w, fmt.Sprintf("Failed to get JSON version: %v", err), http.StatusBadGateway)
		return
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		c.errorCount++
		log.Printf("❌ Failed to read response body: %v", err)
		http.Error(w, fmt.Sprintf("Failed to read response body: %v", err), http.StatusInternalServerError)
		return
	}

	// Use more flexible interface{} type
	var versionData map[string]interface{}
	if err := json.Unmarshal(body, &versionData); err != nil {
		c.errorCount++
		log.Printf("❌ JSON parsing failed: %v", err)
		http.Error(w, fmt.Sprintf("Failed to unmarshal response body: %v", err), http.StatusInternalServerError)
		return
	}

	// Rewrite webSocketDebuggerUrl
	if wsURLRaw, exists := versionData["webSocketDebuggerUrl"]; exists {
		if wsURLStr, ok := wsURLRaw.(string); ok {
			// More flexible URL rewriting, supporting different formats
			newWSURL := rewriteWebSocketURL(wsURLStr, c.targetHostPort, publicHostPort)
			versionData["webSocketDebuggerUrl"] = newWSURL

			log.Printf("🔧 Rewrite WebSocket URL:")
			log.Printf("   Original: %s", wsURLStr)
			log.Printf("   New: %s", newWSURL)
		}
	}

	newBody, err := json.Marshal(versionData)
	if err != nil {
		c.errorCount++
		log.Printf("❌ JSON encoding failed: %v", err)
		http.Error(w, fmt.Sprintf("Failed to marshal response body: %v", err), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Content-Length", strconv.Itoa(len(newBody)))
	w.Write(newBody)

	log.Printf("✅ /json/version response rewritten and sent")
}

/*
Handle /json endpoint
Response format example:

	[{
	   "description": "",
	   "devtoolsFrontendUrl": "https://chrome-devtools-frontend.appspot.com/serve_rev/...",
	   "id": "27E11288C91F165BAD7EE067BE0AE806",
	   "title": "127.0.0.1:9223/json/list",
	   "type": "page",
	   "url": "http://127.0.0.1:9223/json/list",
	   "webSocketDebuggerUrl": "ws://127.0.0.1:9222/devtools/page/27E11288C91F165BAD7EE067BE0AE806"
	}]
*/
func (c *ChromeDevToolsClient) handleJsonList(w http.ResponseWriter, r *http.Request) {
	publicHostPort := r.Host
	log.Printf("🔄 Processing /json - Public address: %s, Target address: %s", publicHostPort, c.targetHostPort)

	resp, err := c.client.Get(fmt.Sprintf("http://%s%s", c.targetHostPort, r.URL.Path))
	if err != nil {
		c.errorCount++
		log.Printf("❌ Failed to get JSON list: %v", err)
		http.Error(w, fmt.Sprintf("Failed to get JSON list: %v", err), http.StatusBadGateway)
		return
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		c.errorCount++
		log.Printf("❌ Failed to read response body: %v", err)
		http.Error(w, fmt.Sprintf("Failed to read response body: %v", err), http.StatusInternalServerError)
		return
	}

	// Use more flexible interface{} type
	var targetsData []map[string]interface{}
	if err := json.Unmarshal(body, &targetsData); err != nil {
		c.errorCount++
		log.Printf("❌ JSON parsing failed: %v", err)
		http.Error(w, fmt.Sprintf("Failed to unmarshal response body: %v", err), http.StatusInternalServerError)
		return
	}

	// Iterate and rewrite URLs for each target
	for i, target := range targetsData {
		// Rewrite devtoolsFrontendUrl
		if devURLRaw, exists := target["devtoolsFrontendUrl"]; exists {
			if devURLStr, ok := devURLRaw.(string); ok {
				newDevURL := strings.Replace(devURLStr, fmt.Sprintf("ws=%s", c.targetHostPort), fmt.Sprintf("ws=%s", publicHostPort), 1)
				target["devtoolsFrontendUrl"] = newDevURL
				log.Printf("🔧 Rewrite devtoolsFrontendUrl [%d]: %s -> %s", i, devURLStr, newDevURL)
			}
		}

		// Rewrite webSocketDebuggerUrl
		if wsURLRaw, exists := target["webSocketDebuggerUrl"]; exists {
			if wsURLStr, ok := wsURLRaw.(string); ok {
				newWSURL := rewriteWebSocketURL(wsURLStr, c.targetHostPort, publicHostPort)
				target["webSocketDebuggerUrl"] = newWSURL
				log.Printf("🔧 Rewrite webSocketDebuggerUrl [%d]: %s -> %s", i, wsURLStr, newWSURL)
			}
		}
	}

	newBody, err := json.Marshal(targetsData)
	if err != nil {
		c.errorCount++
		log.Printf("❌ JSON encoding failed: %v", err)
		http.Error(w, fmt.Sprintf("Failed to marshal response body: %v", err), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Content-Length", strconv.Itoa(len(newBody)))
	w.Write(newBody)

	log.Printf("✅ /json response rewritten and sent")
}

// Smart WebSocket URL rewriting function
func rewriteWebSocketURL(originalURL, targetHostPort, publicHostPort string) string {
	// Try multiple possible formats for replacement
	patterns := []string{
		fmt.Sprintf("ws://%s", targetHostPort),
		fmt.Sprintf("ws://127.0.0.1:%s", strings.Split(targetHostPort, ":")[1]),
		"ws://localhost:" + strings.Split(targetHostPort, ":")[1],
	}

	for _, pattern := range patterns {
		if strings.Contains(originalURL, pattern) {
			// E2B sandbox uses HTTPS, so use wss
			newURL := strings.Replace(originalURL, pattern, fmt.Sprintf("wss://%s", publicHostPort), 1)
			return newURL
		}
	}

	// If no matching pattern found, return original URL (may need manual check)
	log.Printf("⚠️ Warning: Unable to rewrite WebSocket URL, no matching pattern found: %s", originalURL)
	return originalURL
}

// Check if this is a WebSocket upgrade request
func isWebSocketUpgrade(r *http.Request) bool {
	return strings.ToLower(r.Header.Get("Upgrade")) == "websocket" &&
		strings.Contains(strings.ToLower(r.Header.Get("Connection")), "upgrade")
}
