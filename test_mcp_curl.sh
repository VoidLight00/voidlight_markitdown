#!/bin/bash
# Simple curl-based MCP server test script

echo "=== VoidLight MarkItDown MCP Server Curl Test ==="
echo

# Configuration
SERVER_PORT=3001
SERVER_URL="http://localhost:$SERVER_PORT"
TEST_FILE="/Users/voidlight/voidlight_markitdown/test_korean_document.txt"

# Start server in background
echo "Starting MCP server on port $SERVER_PORT..."
source /Users/voidlight/voidlight_markitdown/mcp-env/bin/activate
voidlight-markitdown-mcp --http --port $SERVER_PORT &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Function to cleanup on exit
cleanup() {
    echo "Stopping server..."
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
}
trap cleanup EXIT

# Test 1: Check if server is running
echo "Test 1: Server Health Check"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" $SERVER_URL/
echo

# Test 2: Test SSE endpoint
echo "Test 2: SSE Endpoint"
timeout 2 curl -N -H "Accept: text/event-stream" $SERVER_URL/sse 2>/dev/null
echo "SSE endpoint is accessible"
echo

# Test 3: Send MCP initialization via SSE
echo "Test 3: MCP Protocol Test via SSE"
echo "Sending initialization request..."

# Create a test initialization message
INIT_MSG=$(cat <<EOF
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "protocolVersion": "1.0.0",
    "capabilities": {
      "tools": {}
    },
    "clientInfo": {
      "name": "curl-test",
      "version": "1.0.0"
    }
  },
  "id": 1
}
EOF
)

# Try to send via messages endpoint
echo "Attempting to send initialization..."
curl -X POST \
  -H "Content-Type: application/json" \
  -d "$INIT_MSG" \
  $SERVER_URL/messages/ \
  2>/dev/null | jq . 2>/dev/null || echo "Message endpoint returned an error"
echo

# Test 4: Direct STDIO mode test
echo "Test 4: STDIO Mode Test"
echo "Testing STDIO protocol directly..."

# Create a temporary file with test messages
TEMP_FILE=$(mktemp)
cat > $TEMP_FILE <<EOF
{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"1.0.0","capabilities":{"tools":{}},"clientInfo":{"name":"stdio-test","version":"1.0.0"}},"id":1}
{"jsonrpc":"2.0","method":"tools/list","id":2}
{"jsonrpc":"2.0","method":"tools/call","params":{"name":"convert_korean_document","arguments":{"uri":"file://$TEST_FILE","normalize_korean":true}},"id":3}
EOF

# Run STDIO test
echo "Running STDIO protocol test..."
timeout 5 voidlight-markitdown-mcp < $TEMP_FILE 2>/dev/null | while IFS= read -r line; do
    echo "Response: $line" | head -c 200
    echo "..."
done

rm -f $TEMP_FILE

echo
echo "=== Test Complete ==="