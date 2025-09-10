#!/usr/bin/env python3
"""
Simple test script to send fake tool calls to MCP servers
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_server_simple(server_name, server_path):
    """Test a single MCP server with basic requests"""
    print(f"\n=== Testing {server_name} MCP Server ===")
    
    try:
        # Start the server process
        process = await asyncio.create_subprocess_exec(
            sys.executable, server_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print(f"📤 Sending initialization request...")
        init_data = json.dumps(init_request) + "\n"
        process.stdin.write(init_data.encode())
        await process.stdin.drain()
        
        # Read initialization response with timeout
        try:
            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
            if response_line:
                init_response = json.loads(response_line.decode().strip())
                print(f"✅ Server initialized: {init_response}")
            else:
                print("❌ No initialization response received")
                return
        except asyncio.TimeoutError:
            print("❌ Initialization timeout")
            return
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        print(f"📤 Sending initialized notification...")
        notif_data = json.dumps(initialized_notification) + "\n"
        process.stdin.write(notif_data.encode())
        await process.stdin.drain()
        
        # Send list_tools request
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print(f"📤 Sending tools/list request...")
        list_data = json.dumps(list_tools_request) + "\n"
        process.stdin.write(list_data.encode())
        await process.stdin.drain()
        
        # Read tools list response with timeout
        try:
            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
            if response_line:
                tools_response = json.loads(response_line.decode().strip())
                print(f"📥 Tools response: {tools_response}")
                
                if 'result' in tools_response:
                    tools = tools_response['result'].get('tools', [])
                    print(f"✅ Found {len(tools)} tools: {[tool['name'] for tool in tools]}")
                    
                    # Test first available tool if any
                    if tools:
                        test_tool = tools[0]['name']
                        tool_request = {
                            "jsonrpc": "2.0",
                            "id": 3,
                            "method": "tools/call",
                            "params": {
                                "name": test_tool,
                                "arguments": {}
                            }
                        }
                        
                        print(f"📤 Testing tool: {test_tool}")
                        tool_data = json.dumps(tool_request) + "\n"
                        process.stdin.write(tool_data.encode())
                        await process.stdin.drain()
                        
                        # Read tool call response
                        try:
                            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
                            if response_line:
                                tool_response = json.loads(response_line.decode().strip())
                                print(f"📥 Tool response: {tool_response}")
                                if 'result' in tool_response:
                                    print(f"✅ Tool call successful!")
                                else:
                                    print(f"❌ Tool call failed: {tool_response.get('error', 'Unknown error')}")
                        except asyncio.TimeoutError:
                            print("❌ Tool call timeout")
                else:
                    print(f"❌ Error in tools list: {tools_response.get('error', 'Unknown error')}")
            else:
                print("❌ No tools list response received")
        except asyncio.TimeoutError:
            print("❌ Tools list timeout")
        
        # Terminate the process
        process.terminate()
        await process.wait()
        
    except Exception as e:
        print(f"❌ Error testing {server_name}: {str(e)}")
        if 'process' in locals():
            process.terminate()
            await process.wait()

async def main():
    """Test all MCP servers"""
    print("🧪 Testing MCP Servers with Simple Protocol")
    
    # Test configurations for each server
    servers = [
        {"name": "RAG", "path": "rag/server.py"},
        {"name": "Browser", "path": "browser/server.py"},
        {"name": "Radio Player", "path": "radio_player/server.py"},
        {"name": "Word Editor", "path": "word_editor/server.py"}
    ]
    
    # Test each server
    for server in servers:
        await test_server_simple(server["name"], server["path"])
        await asyncio.sleep(1)  # Brief pause between tests
    
    print("\n🎉 MCP Server testing completed!")

if __name__ == "__main__":
    asyncio.run(main())