#!/usr/bin/env python3
"""
Test script for the Ollama MCP Bridge
Tests basic functionality and tool integration.
"""

import requests
import json
import time
import sys
from pathlib import Path

def test_bridge_health(bridge_url="http://localhost:8000"):
    """Test if the bridge is running and healthy."""
    try:
        response = requests.get(f"{bridge_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"[SUCCESS] Bridge is healthy at {bridge_url}")
            return True
        else:
            print(f"[ERROR] Bridge health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Cannot connect to bridge at {bridge_url}: {e}")
        return False

def test_chat_completion(bridge_url="http://localhost:8000", model="llama3.2:1b"):
    """Test basic chat completion through the bridge."""
    try:
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello! Can you tell me what MCP tools are available?"
                }
            ],
            "stream": False
        }
        
        print(f"[INFO] Testing chat completion with model: {model}")
        response = requests.post(f"{bridge_url}/api/chat", json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            message = result.get('message', {}).get('content', 'No content')
            print(f"[SUCCESS] Chat completion successful")
            print(f"[RESPONSE] {message[:200]}..." if len(message) > 200 else f"[RESPONSE] {message}")
            return True
        else:
            print(f"[ERROR] Chat completion failed: {response.status_code}")
            print(f"[ERROR] Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Chat completion request failed: {e}")
        return False

def test_tool_usage(bridge_url="http://localhost:8000", model="llama3.2:1b"):
    """Test MCP tool usage through the bridge."""
    try:
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": "Can you search for some reggaeton radio stations using the radio player?"
                }
            ],
            "stream": False
        }
        
        print(f"[INFO] Testing MCP tool usage (radio player)")
        response = requests.post(f"{bridge_url}/api/chat", json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            message = result.get('message', {}).get('content', 'No content')
            print(f"[SUCCESS] Tool usage test successful")
            print(f"[RESPONSE] {message[:300]}..." if len(message) > 300 else f"[RESPONSE] {message}")
            return True
        else:
            print(f"[ERROR] Tool usage test failed: {response.status_code}")
            print(f"[ERROR] Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Tool usage request failed: {e}")
        return False

def main():
    """Run all bridge tests."""
    print("[INFO] Starting Ollama MCP Bridge Tests")
    print("[INFO] Make sure the bridge is running first!")
    print("[INFO] Run: cd ollama-mcp-bridge && uv run ollama-mcp-bridge")
    print()
    
    bridge_url = "http://localhost:8000"
    
    # Test 1: Health check
    print("=== Test 1: Bridge Health Check ===")
    if not test_bridge_health(bridge_url):
        print("[FATAL] Bridge is not running. Please start it first.")
        sys.exit(1)
    print()
    
    # Test 2: Basic chat
    print("=== Test 2: Basic Chat Completion ===")
    if not test_chat_completion(bridge_url):
        print("[WARNING] Basic chat failed, but continuing...")
    print()
    
    # Test 3: Tool usage
    print("=== Test 3: MCP Tool Usage ===")
    if not test_tool_usage(bridge_url):
        print("[WARNING] Tool usage test failed")
    print()
    
    print("[INFO] Bridge testing completed!")
    print("[INFO] If tests passed, your bridge is working correctly.")
    print("[INFO] You can now use any Ollama client with the bridge at http://localhost:8000")

if __name__ == "__main__":
    main()