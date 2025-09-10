#!/usr/bin/env python3

import sys
sys.path.append('/Users/eev/Nextcloud/Walls')

from rag.tool_executor import ToolCallExecutor

# Test text with proper JSON format
if len(sys.argv) > 1:
    test_text = ' '.join(sys.argv[1:])
else:
    test_text = '''Here is a tool call to test:

    ```json
    {"name": "set_text", "arguments": {"text": "Testing RAG MCP integration directly"}}
    ```

    And another one:

    ```json
    {"name": "save_file", "arguments": {"filename": "rag_mcp_test.txt", "encoding": "utf-8", "create_backup": true}}
    ```
    '''

print("Testing RAG MCP Integration...")
print("=" * 50)

executor = ToolCallExecutor()
results = executor.execute_all_tool_calls(test_text)

print("\n=== Execution Results ===")
for i, result in enumerate(results, 1):
    print(f"Result {i}: {result}")

if results:
    print(f"\n✅ Successfully executed {len(results)} tool calls via MCP!")
else:
    print("\n❌ No tool calls were executed.")