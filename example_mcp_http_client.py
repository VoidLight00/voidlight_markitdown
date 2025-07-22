#!/usr/bin/env python3
"""
Example MCP HTTP Client for VoidLight MarkItDown Server
Demonstrates proper usage of the HTTP/SSE transport
"""

import requests
import json
import sys

class MCPHTTPClient:
    """Simple MCP HTTP client for VoidLight MarkItDown"""
    
    def __init__(self, base_url="http://localhost:3001"):
        self.base_url = base_url
        self.mcp_url = f"{base_url}/mcp"
        self.session_id = None
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'  # Required for MCP Streamable HTTP
        }
    
    def initialize(self):
        """Initialize MCP connection"""
        request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {
                    "name": "example-client",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
        
        response = requests.post(self.mcp_url, json=request, headers=self.headers)
        
        # Store session ID if provided
        if 'Mcp-Session-Id' in response.headers:
            self.session_id = response.headers['Mcp-Session-Id']
            self.headers['Mcp-Session-Id'] = self.session_id
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Initialize failed: {response.status_code} - {response.text}")
    
    def list_tools(self):
        """List available tools"""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        response = requests.post(self.mcp_url, json=request, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"List tools failed: {response.status_code} - {response.text}")
    
    def call_tool(self, tool_name, arguments):
        """Call a specific tool"""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 3
        }
        
        response = requests.post(self.mcp_url, json=request, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Tool call failed: {response.status_code} - {response.text}")
    
    def convert_to_markdown(self, uri):
        """Convert a document to markdown"""
        return self.call_tool("convert_to_markdown", {"uri": uri})
    
    def convert_korean_document(self, uri, normalize_korean=True):
        """Convert a Korean document with normalization"""
        return self.call_tool("convert_korean_document", {
            "uri": uri,
            "normalize_korean": normalize_korean
        })


def main():
    """Example usage"""
    # Create client
    client = MCPHTTPClient()
    
    try:
        # Initialize connection
        print("Initializing MCP connection...")
        init_result = client.initialize()
        print(f"Server: {init_result['result']['serverInfo']['name']} v{init_result['result']['serverInfo']['version']}")
        print(f"Protocol: {init_result['result']['protocolVersion']}")
        
        # List available tools
        print("\nListing available tools...")
        tools_result = client.list_tools()
        for tool in tools_result['result']['tools']:
            print(f"- {tool['name']}: {tool['description'].split('\\n')[0]}")
        
        # Example: Convert a Korean document
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            print(f"\nConverting Korean document: {file_path}")
            
            # Convert with normalization
            result = client.convert_korean_document(f"file://{file_path}")
            content = result['result']['content'][0]['text']
            
            print("\nConverted content:")
            print("-" * 50)
            print(content[:500] + "..." if len(content) > 500 else content)
            print("-" * 50)
        else:
            print("\nUsage: python example_mcp_http_client.py <file_path>")
            print("Example: python example_mcp_http_client.py test_korean_document.txt")
    
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())