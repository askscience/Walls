#!/usr/bin/env python3
"""
Test script for auto-launch functionality

This script tests whether MCP servers can automatically launch
their corresponding GUI applications when tools are called.
"""

import asyncio
import json
import sys
import os

# Add MCP directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'browser'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'radio_player'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'word_editor'))

# Import the app launcher to test directly
from app_launcher import ensure_browser_running, ensure_radio_player_running, ensure_word_editor_running

async def test_browser_launch():
    """Test browser auto-launch functionality."""
    print("\n=== Testing Browser Auto-Launch ===")
    try:
        result = await ensure_browser_running()
        print(f"Browser launch result: {json.dumps(result, indent=2)}")
        return result['success']
    except Exception as e:
        print(f"Browser launch failed: {e}")
        return False

async def test_radio_player_launch():
    """Test radio player auto-launch functionality."""
    print("\n=== Testing Radio Player Auto-Launch ===")
    try:
        result = await ensure_radio_player_running()
        print(f"Radio player launch result: {json.dumps(result, indent=2)}")
        return result['success']
    except Exception as e:
        print(f"Radio player launch failed: {e}")
        return False

async def test_word_editor_launch():
    """Test word editor auto-launch functionality."""
    print("\n=== Testing Word Editor Auto-Launch ===")
    try:
        result = await ensure_word_editor_running()
        print(f"Word editor launch result: {json.dumps(result, indent=2)}")
        return result['success']
    except Exception as e:
        print(f"Word editor launch failed: {e}")
        return False

async def main():
    """Run all auto-launch tests."""
    print("Starting auto-launch functionality tests...")
    
    # Test each application
    browser_success = await test_browser_launch()
    await asyncio.sleep(2)  # Brief pause between tests
    
    radio_success = await test_radio_player_launch()
    await asyncio.sleep(2)
    
    word_editor_success = await test_word_editor_launch()
    
    # Summary
    print("\n=== Test Results Summary ===")
    print(f"Browser auto-launch: {'✓ PASS' if browser_success else '✗ FAIL'}")
    print(f"Radio Player auto-launch: {'✓ PASS' if radio_success else '✗ FAIL'}")
    print(f"Word Editor auto-launch: {'✓ PASS' if word_editor_success else '✗ FAIL'}")
    
    total_success = browser_success + radio_success + word_editor_success
    print(f"\nOverall: {total_success}/3 applications successfully auto-launched")
    
    if total_success == 3:
        print("🎉 All auto-launch tests passed!")
    else:
        print("⚠️  Some auto-launch tests failed. Check the logs above for details.")

if __name__ == "__main__":
    asyncio.run(main())