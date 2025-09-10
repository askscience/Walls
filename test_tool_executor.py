#!/usr/bin/env python3
from rag.tool_executor import ToolCallExecutor

executor = ToolCallExecutor()

# Test text with JSON tool calls
test_text = '''Here is a tool call:
```json
{"name": "set_text", "arguments": {"text": "Hello World"}}
```

And another one:
```json
{"name": "save_file", "arguments": {"filename": "test.txt"}}
```'''

print("Testing tool call extraction...")
calls = executor.extract_json_tool_calls(test_text)
print(f"Found {len(calls)} tool calls:")
for i, call in enumerate(calls, 1):
    print(f"  {i}. {call}")

if calls:
    print("\nTesting tool execution...")
    for call in calls:
        result = executor.execute_tool_call(call)
        print(f"Result for {call['name']}: {result}")
else:
    print("No tool calls found to execute.")