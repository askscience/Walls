#!/usr/bin/env python3
"""
Debug script to test MCP server communication directly
"""

import asyncio
import json
import subprocess
import sys

async def test_mcp_server():
    """Test MCP server communication directly"""
    
    # Start the browser MCP server
    process = await asyncio.create_subprocess_exec(
        sys.executable, "MCP/browser/server.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd="/Users/eev/Nextcloud/Walls"
    )
    
    try:
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "debug-client", "version": "1.0.0"}
            }
        }
        
        print("Sending initialization request...")
        init_data = json.dumps(init_request) + "\n"
        process.stdin.write(init_data.encode())
        await process.stdin.drain()
        
        # Read initialization response
        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
        if response_line:
            init_response = json.loads(response_line.decode().strip())
            print(f"Initialization response: {json.dumps(init_response, indent=2)}")
        else:
            print("No initialization response received")
            return
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        notif_data = json.dumps(initialized_notification) + "\n"
        process.stdin.write(notif_data.encode())
        await process.stdin.drain()
        
        # Send tool call request
        tool_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "open_url",
                "arguments": {"url": "https://example.com"}
            }
        }
        
        print("Sending tool call request...")
        tool_data = json.dumps(tool_request) + "\n"
        process.stdin.write(tool_data.encode())
        await process.stdin.drain()
        
        # Read tool call response
        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=30.0)
        if response_line:
            tool_response = json.loads(response_line.decode().strip())
            print(f"Tool call response: {json.dumps(tool_response, indent=2)}")
        else:
            print("No tool call response received")
        
        # Check for any stderr output
        try:
            stderr_data = await asyncio.wait_for(process.stderr.read(), timeout=1.0)
            if stderr_data:
                print(f"Server stderr: {stderr_data.decode()}")
        except asyncio.TimeoutError:
            pass
            
    except Exception as e:
        print(f"Error during test: {e}")
        
    finally:
        process.terminate()
        await process.wait()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())