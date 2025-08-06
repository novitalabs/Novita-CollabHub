#!/bin/bash

echo "=== Chrome Startup Debug ==="
echo "Current user: $(whoami)"
echo "User ID: $(id)"
echo "Groups: $(groups)"

# Set script directory
SCRIPT_DIR="/app/scripts"
echo "Script directory: $SCRIPT_DIR"

# Ensure we're in the correct directory
cd $SCRIPT_DIR || exit 1
echo "Current working directory: $(pwd)"

# Check directory structure
echo "Checking directory structure:"
ls -la $SCRIPT_DIR/
echo ""

if [ -d "$SCRIPT_DIR/latest" ]; then
    echo "Checking latest directory:"
    ls -la $SCRIPT_DIR/latest/
    echo ""
else
    echo "❌ latest directory does not exist!"
    exit 1
fi

# Find Chrome executable
CHROME_BINARY=""
for binary in "$SCRIPT_DIR/latest/chrome" "$SCRIPT_DIR/latest/chrome-linux/chrome" "$SCRIPT_DIR/latest/chrome-wrapper"; do
    if [ -f "$binary" ] && [ -x "$binary" ]; then
        CHROME_BINARY="$binary"
        echo "✅ Found Chrome binary: $CHROME_BINARY"
        break
    fi
done

if [ -z "$CHROME_BINARY" ]; then
    echo "❌ Cannot find executable Chrome binary!"
    echo "Trying to find all possible files:"
    find $SCRIPT_DIR -name "*chrome*" -type f 2>/dev/null
    exit 1
fi

# Check if reverse proxy exists
if [ ! -f "/app/reverse-proxy" ]; then
    echo "❌ Reverse proxy does not exist!"
    exit 1
else
    echo "✅ Reverse proxy available"
fi

echo "Starting Chromium with reverse proxy..."

# Start Chromium (bind to 127.0.0.1:9222)
echo "Startup command: $CHROME_BINARY --headless --disable-gpu --remote-debugging-port=9222 ..."
echo "Running as user: $(whoami)"
$CHROME_BINARY \
  --remote-debugging-port=9222 \
  --headless=new \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --no-first-run \
  --user-data-dir="/app/user-data-dir" &

CHROME_PID=$!
echo "Chromium started with PID: $CHROME_PID"

# Check if process is still running
sleep 2
if kill -0 $CHROME_PID 2>/dev/null; then
    echo "✅ Chromium process running normally (PID: $CHROME_PID)"
else
    echo "❌ Chromium process has exited!"
    exit 1
fi

# Check if port is listening
echo "Checking if Chrome is listening on port 9222..."
for i in {1..10}; do
    if netstat -tlnp 2>/dev/null | grep :9222 > /dev/null; then
        echo "✅ Chrome is listening on port 9222"
        break
    else
        echo "Waiting for Chrome to listen on port... (attempt $i/10)"
        sleep 1
    fi
done

# Start reverse proxy: 0.0.0.0:9223 -> 127.0.0.1:9222 (supports Host header rewriting)
echo "Starting reverse proxy 0.0.0.0:9223 -> 127.0.0.1:9222..."
/app/reverse-proxy &

PROXY_PID=$!
echo "reverse proxy started with PID: $PROXY_PID"

# Check proxy process
sleep 1
if kill -0 $PROXY_PID 2>/dev/null; then
    echo "✅ Reverse proxy process running normally (PID: $PROXY_PID)"
else
    echo "❌ Reverse proxy process has exited!"
    exit 1
fi

echo "✅ DevTools should now be accessible on 0.0.0.0:9223"
echo "🌐 HTTP requests and WebSocket connections will automatically rewrite Host header"
echo "=== Startup Complete ==="

# Wait for any process to exit
wait 