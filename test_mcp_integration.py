#!/usr/bin/env python3
"""Test script to verify MCP integration with Word Editor."""

import asyncio
import sys
import os

# Add the rag directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rag'))

from tool_executor import ToolCallExecutor

async def test_mcp_integration():
    """Test the complete MCP integration."""
    print("🧪 Testing MCP Integration with Word Editor")
    print("=" * 50)
    
    executor = ToolCallExecutor()
    
    # Test 1: Set text
    print("\n📝 Test 1: Setting text...")
    set_text_result = await executor.execute_tool_call_async({
        'name': 'set_text',
        'arguments': {
            'text': 'Hello from MCP Integration Test!\n\nThis text was set via the RAG system using MCP tool calling.'
        }
    })
    
    if set_text_result.get('success'):
        print("✅ Set text: SUCCESS")
    else:
        print(f"❌ Set text: FAILED - {set_text_result.get('error')}")
    
    # Test 2: Save file
    print("\n💾 Test 2: Saving file...")
    save_file_result = await executor.execute_tool_call_async({
        'name': 'save_file',
        'arguments': {
            'file_path': '/tmp/mcp_integration_test.txt'
        }
    })
    
    if save_file_result.get('success'):
        print("✅ Save file: SUCCESS")
    else:
        print(f"❌ Save file: FAILED - {save_file_result.get('error')}")
    
    # Test 3: Get text to verify
    print("\n📖 Test 3: Getting current text...")
    get_text_result = await executor.execute_tool_call_async({
        'name': 'get_text',
        'arguments': {}
    })
    
    if get_text_result.get('success'):
        print("✅ Get text: SUCCESS")
        # Extract the actual text from the nested response structure
        result_data = get_text_result.get('result', {})
        if 'content' in result_data and result_data['content']:
            content = result_data['content'][0].get('text', '')
            print(f"📄 Current text preview: {content[:100]}...")
    else:
        print(f"❌ Get text: FAILED - {get_text_result.get('error')}")
    
    print("\n" + "=" * 50)
    print("🎉 MCP Integration Test Complete!")
    
    # Summary
    tests_passed = sum([
        set_text_result.get('success', False),
        save_file_result.get('success', False),
        get_text_result.get('success', False)
    ])
    
    print(f"📊 Results: {tests_passed}/3 tests passed")
    
    if tests_passed == 3:
        print("🎯 All tests passed! MCP integration is working properly.")
    elif tests_passed >= 2:
        print("⚠️  Most tests passed. MCP integration is mostly functional.")
    else:
        print("❌ Multiple tests failed. MCP integration needs attention.")
    
    return tests_passed == 3

if __name__ == "__main__":
    success = asyncio.run(test_mcp_integration())
    sys.exit(0 if success else 1)