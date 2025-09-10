#!/usr/bin/env python3
"""
Tool Call Executor for RAG System

This script extracts JSON tool calls from RAG responses and executes them
via the MCP servers running on the shared server infrastructure.
"""

import asyncio
import json
import re
import subprocess
import sys
from typing import Dict, Any, Optional, List
import importlib.util


class ToolCallExecutor:
    """Executes tool calls extracted from RAG responses."""
    
    def __init__(self, base_dir: str = "/Users/eev/Nextcloud/Walls"):
        """Initialize the tool executor with MCP server paths."""
        self.base_dir = base_dir
        # MCP server script paths (for AI tool execution via stdio protocol)
        # These communicate via JSON-RPC over stdin/stdout, NOT HTTP
        self.mcp_servers = {
            "browser": "MCP/browser/server.py",      # Browser MCP server (AI tools)
            "word_editor": "MCP/word_editor/server.py",  # Word Editor MCP server (AI tools)
            "radio_player": "MCP/radio_player/server.py", # Radio Player MCP server (AI tools)
            "rag": "MCP/rag/server.py"          # RAG MCP server (AI tools)
        }
        
        # APP server ports (for application control) - NOT used for AI tool calls
        # radio_player: 9000, browser: 9002, word_editor: 9003, words: 8765
        # These are managed separately by the shared server system
    
    def extract_json_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        """Extract JSON tool calls from text response using robust parsing.
        
        Args:
            text: The text containing potential JSON tool calls
            
        Returns:
            List of extracted tool call dictionaries
        """
        tool_calls: List[Dict[str, Any]] = []
    
        # Remove <think> blocks to avoid noisy JSON-like content inside them
        filtered_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
        def try_parse_and_append(candidate: str):
            try:
                obj = json.loads(candidate)
                if isinstance(obj, dict) and 'name' in obj and 'arguments' in obj:
                    tool_calls.append(obj)
                    print(f"🔍 Found tool call: {obj['name']}")
            except json.JSONDecodeError:
                pass
    
        # 1) Parse fenced code blocks first (```json ... ``` or ``` ... ```)
        code_blocks = re.findall(r"```(?:json)?\s*(.*?)```", filtered_text, flags=re.DOTALL | re.IGNORECASE)
        for block in code_blocks:
            # Block may contain surrounding text; extract balanced JSON(s) within
            for candidate in self._find_balanced_json_objects(block):
                try_parse_and_append(candidate)
    
        # 2) Fallback: scan entire filtered_text for balanced JSON objects
        if not tool_calls:
            for candidate in self._find_balanced_json_objects(filtered_text):
                try_parse_and_append(candidate)
    
        if not tool_calls:
            print(f"🔍 Debug: No tool calls found. Searched {len(filtered_text)} chars after filtering think blocks.")
        return tool_calls
    
    def _find_balanced_json_objects(self, text: str) -> List[str]:
        """Find balanced JSON object substrings within text.
        Returns a list of substrings that are likely complete JSON objects containing a tool call.
        """
        results: List[str] = []
        stack = []
        start_idx = None
        i = 0
        while i < len(text):
            ch = text[i]
            if ch == '"':
                # Skip over string contents safely, honoring escapes
                i += 1
                while i < len(text):
                    if text[i] == '\\':
                        i += 2
                        continue
                    if text[i] == '"':
                        break
                    i += 1
            elif ch == '{':
                if not stack:
                    start_idx = i
                stack.append('{')
            elif ch == '}':
                if stack:
                    stack.pop()
                    if not stack and start_idx is not None:
                        candidate = text[start_idx:i+1]
                        # Only yield candidates that look like tool calls to reduce noise
                        if '"name"' in candidate and '"arguments"' in candidate:
                            results.append(candidate)
                        start_idx = None
            i += 1
        return results
    
    def generate_missing_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        """Generate tool calls from AI thinking when JSON is missing.
        
        Args:
            text: The AI response text containing thinking but no JSON
            
        Returns:
            List of generated tool call dictionaries
        """
        tool_calls: List[Dict[str, Any]] = []
        
        # Extract thinking content
        think_match = re.search(r'<think>(.*?)</think>', text, re.DOTALL | re.IGNORECASE)
        if not think_match:
            return tool_calls
        
        thinking_raw = think_match.group(1)
        thinking_lower = thinking_raw.lower()
        
        # Prefer create_document if explicitly mentioned and supported by mapping
        if 'create_document' in thinking_lower and self.determine_server_for_tool('create_document'):
            path_match = re.search(r"(?:file_path|path is|path to|filename is|save to)\s*['\"](.+?)['\"]", thinking_raw, flags=re.IGNORECASE | re.DOTALL)
            text_match = re.search(r"(?:text is|text to|content is|with content)\s*['\"](.+?)['\"]", thinking_raw, flags=re.IGNORECASE | re.DOTALL)
            if path_match and text_match:
                tool_calls.append({
                    "name": "create_document",
                    "arguments": {
                        "file_path": path_match.group(1),
                        "text": text_match.group(1)
                    }
                })
                print(f"🔧 Generated create_document tool call for: {path_match.group(1)}")

        # Fallback to set_text and/or save_file
        if not tool_calls:
            # set_text
            if any(k in thinking_lower for k in ['set_text', 'set text', 'set', 'text']):
                text_match = re.search(r"(?:text is|text to|set text to|content is)\s*['\"](.+?)['\"]", thinking_raw, flags=re.IGNORECASE | re.DOTALL)
                if text_match:
                    text_content = text_match.group(1)
                    tool_calls.append({
                        "name": "set_text",
                        "arguments": {"text": text_content}
                    })
                    print(f"🔧 Generated set_text tool call with: {text_content[:80]}...")
            
            # save_file (independent)
            if any(k in thinking_lower for k in ['save_file', 'save file', 'save', 'file']):
                file_match = re.search(r"(?:file path is|save to|filename is|path is)\s*['\"]([^'\"\s]+)['\"]", thinking_raw, flags=re.IGNORECASE)
                if file_match:
                    file_path = file_match.group(1)
                    # Only add if not already added by create_document
                    if not any(tc.get('name') == 'save_file' for tc in tool_calls):
                        tool_calls.append({
                            "name": "save_file",
                            "arguments": {"file_path": file_path}
                        })
                        print(f"🔧 Generated save_file tool call for: {file_path}")

        return tool_calls
    
    
    # Removed duplicate determine_server_for_tool here; the canonical definition is below.
    
    def _load_tool_schemas(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Dynamically load TOOL_SCHEMAS dict for a given MCP server.
        Returns None if schemas cannot be loaded.
        """
        schemas_path = f"{self.base_dir}/MCP/{server_name}/schemas/tool_schemas.py"
        try:
            spec = importlib.util.spec_from_file_location(f"mcp_{server_name}_tool_schemas", schemas_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)  # type: ignore[attr-defined]
                return getattr(module, "TOOL_SCHEMAS", None)
        except Exception as e:
            print(f"⚠️  Failed to load tool schemas for server '{server_name}': {e}")
        return None

    def _validate_tool_call(self, tool_name: str, arguments: Any) -> Optional[str]:
        """Validate tool call arguments against the MCP tool schema.
        Returns None if valid; otherwise returns an error message string.
        """
        if not isinstance(arguments, dict):
            return "Tool arguments must be a JSON object"
        server_path = self.determine_server_for_tool(tool_name)
        if not server_path:
            return f"Unknown tool: {tool_name}"
        # server_path is like 'MCP/browser/server.py' - extract server name folder
        try:
            # Derive server name from mapping by reverse lookup
            # Our determine_server_for_tool returns a path like 'MCP/browser/server.py' or similar
            parts = server_path.split('/')
            if len(parts) >= 3 and parts[0] == 'MCP':
                server_name = parts[1]
            else:
                # Fall back to known map by probing known server names in path
                server_name = 'browser' if 'browser' in server_path else (
                    'word_editor' if 'word_editor' in server_path else (
                        'radio_player' if 'radio_player' in server_path else (
                            'rag' if 'rag' in server_path else ''
                        )
                    )
                )
            if not server_name:
                return f"Cannot determine server for tool: {tool_name}"
        except Exception:
            return f"Cannot determine server for tool: {tool_name}"

        schemas = self._load_tool_schemas(server_name)
        if not schemas:
            # If schemas unavailable, skip strict validation but warn
            print(f"⚠️  Schemas not found for server '{server_name}', skipping validation")
            return None
        schema = schemas.get(tool_name)
        if not schema:
            return f"Tool '{tool_name}' not found in server '{server_name}' schemas"

        # Check required fields
        required = schema.get('required', [])
        missing = [k for k in required if k not in arguments]
        if missing:
            return f"Missing required argument(s): {', '.join(missing)}"

        # Basic type checking for provided arguments
        props: Dict[str, Any] = schema.get('properties', {})
        type_map = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'object': dict,
            'array': list,
        }
        for key, value in arguments.items():
            if key in props and 'type' in props[key]:
                expected = props[key]['type']
                py_type = type_map.get(expected)
                if py_type and not isinstance(value, py_type):
                    return f"Invalid type for '{key}': expected {expected}"

        # additionalProperties: False enforcement
        if schema.get('additionalProperties') is False:
            allowed = set(props.keys())
            extra = [k for k in arguments.keys() if k not in allowed]
            if extra:
                return f"Unexpected argument(s): {', '.join(extra)}"

        return None
    
    def extract_json_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        """Extract JSON tool calls from text response using robust parsing.
        
        Args:
            text: The text containing potential JSON tool calls
            
        Returns:
            List of extracted tool call dictionaries
        """
        tool_calls: List[Dict[str, Any]] = []
    
        # Remove <think> blocks to avoid noisy JSON-like content inside them
        filtered_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
        def try_parse_and_append(candidate: str):
            try:
                obj = json.loads(candidate)
                if isinstance(obj, dict) and 'name' in obj and 'arguments' in obj:
                    tool_calls.append(obj)
                    print(f"🔍 Found tool call: {obj['name']}")
            except json.JSONDecodeError:
                pass
    
        # 1) Parse fenced code blocks first (```json ... ``` or ``` ... ```)
        code_blocks = re.findall(r"```(?:json)?\s*(.*?)```", filtered_text, flags=re.DOTALL | re.IGNORECASE)
        for block in code_blocks:
            # Block may contain surrounding text; extract balanced JSON(s) within
            for candidate in self._find_balanced_json_objects(block):
                try_parse_and_append(candidate)
    
        # 2) Fallback: scan entire filtered_text for balanced JSON objects
        if not tool_calls:
            for candidate in self._find_balanced_json_objects(filtered_text):
                try_parse_and_append(candidate)
    
        if not tool_calls:
            print(f"🔍 Debug: No tool calls found. Searched {len(filtered_text)} chars after filtering think blocks.")
        return tool_calls
    
    def _find_balanced_json_objects(self, text: str) -> List[str]:
        """Find balanced JSON object substrings within text.
        Returns a list of substrings that are likely complete JSON objects containing a tool call.
        """
        results: List[str] = []
        stack = []
        start_idx = None
        i = 0
        while i < len(text):
            ch = text[i]
            if ch == '"':
                # Skip over string contents safely, honoring escapes
                i += 1
                while i < len(text):
                    if text[i] == '\\':
                        i += 2
                        continue
                    if text[i] == '"':
                        break
                    i += 1
            elif ch == '{':
                if not stack:
                    start_idx = i
                stack.append('{')
            elif ch == '}':
                if stack:
                    stack.pop()
                    if not stack and start_idx is not None:
                        candidate = text[start_idx:i+1]
                        # Only yield candidates that look like tool calls to reduce noise
                        if '"name"' in candidate and '"arguments"' in candidate:
                            results.append(candidate)
                        start_idx = None
            i += 1
        return results
    
    def generate_missing_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        """Generate tool calls from AI thinking when JSON is missing.
        
        Args:
            text: The AI response text containing thinking but no JSON
            
        Returns:
            List of generated tool call dictionaries
        """
        tool_calls: List[Dict[str, Any]] = []
        
        # Extract thinking content
        think_match = re.search(r'<think>(.*?)</think>', text, re.DOTALL | re.IGNORECASE)
        if not think_match:
            return tool_calls
        
        thinking_raw = think_match.group(1)
        thinking_lower = thinking_raw.lower()
        
        # Prefer create_document if explicitly mentioned
        if 'create_document' in thinking_lower:
            path_match = re.search(r"(?:file_path|path is|path to|filename is|save to)\s*['\"](.+?)['\"]", thinking_raw, flags=re.IGNORECASE | re.DOTALL)
            text_match = re.search(r"(?:text is|text to|content is|with content)\s*['\"](.+?)['\"]", thinking_raw, flags=re.IGNORECASE | re.DOTALL)
            if path_match and text_match:
                tool_calls.append({
                    "name": "create_document",
                    "arguments": {
                        "file_path": path_match.group(1),
                        "text": text_match.group(1)
                    }
                })
                print(f"🔧 Generated create_document tool call for: {path_match.group(1)}")

        # Fallback to set_text and/or save_file
        if not tool_calls:
            # set_text
            if any(k in thinking_lower for k in ['set_text', 'set text', 'set', 'text']):
                text_match = re.search(r"(?:text is|text to|set text to|content is)\s*['\"](.+?)['\"]", thinking_raw, flags=re.IGNORECASE | re.DOTALL)
                if text_match:
                    text_content = text_match.group(1)
                    tool_calls.append({
                        "name": "set_text",
                        "arguments": {"text": text_content}
                    })
                    print(f"🔧 Generated set_text tool call with: {text_content[:80]}...")
            
            # save_file (independent)
            if any(k in thinking_lower for k in ['save_file', 'save file', 'save', 'file']):
                file_match = re.search(r"(?:file path is|save to|filename is|path is)\s*['\"]([^'\"\s]+)['\"]", thinking_raw, flags=re.IGNORECASE)
                if file_match:
                    file_path = file_match.group(1)
                    # Only add if not already added by create_document
                    if not any(tc.get('name') == 'save_file' for tc in tool_calls):
                        tool_calls.append({
                            "name": "save_file",
                            "arguments": {"file_path": file_path}
                        })
                        print(f"🔧 Generated save_file tool call for: {file_path}")

        return tool_calls
    
    def determine_server_for_tool(self, tool_name: str) -> Optional[str]:
        """Determine which MCP server handles a specific tool.
        
        Args:
            tool_name: Name of the tool to execute
            
        Returns:
            Path of the MCP server script that handles this tool, or None if unknown
        """
        # Tool to server mapping
        tool_server_map = {
            # Browser tools
            "open_url": "browser",
            "navigate_to": "browser", 
            "click_element": "browser",
            "add_bookmark": "browser",
            "get_page_content": "browser",
            "take_screenshot": "browser",
            "get_bookmarks": "browser",
            "send_cli_command": "browser",
            "check_gui_status": "browser",
            
            # Word editor tools
            "set_text": "word_editor",
            "append_text": "word_editor",
            "open_file": "word_editor",
            "save_file": "word_editor",
            "create_document": "word_editor",
            "get_text": "word_editor",
            "insert_text": "word_editor",
            "replace_text": "word_editor",
            "send_cli_command": "word_editor",
            "check_gui_status": "word_editor",
            
            # Radio player tools
            "play_station": "radio_player",
            "stop_playback": "radio_player",
            "pause_playback": "radio_player",
            "resume_playback": "radio_player",
            "get_playback_status": "radio_player",
            "get_current_station": "radio_player",
            "add_favorite_station": "radio_player",
            "remove_favorite_station": "radio_player",
            "list_favorite_stations": "radio_player",
            "get_station_info": "radio_player",
            "search_stations": "radio_player",
            "search_by_genre": "radio_player",
            "search_by_country": "radio_player",
            "get_popular_stations": "radio_player",
            "set_volume": "radio_player",
            "get_volume": "radio_player",
            
            # RAG tools
            "rag_index_all": "rag",
            "rag_add_document": "rag",
            "rag_delete_document": "rag",
            "rag_query": "rag",
            "rag_interactive_query": "rag",
            "rag_start_watching": "rag",
            "rag_stop_watching": "rag",
            "rag_health_check": "rag",
            "rag_get_status": "rag"
        }
        
        server_name = tool_server_map.get(tool_name)
        if server_name:
            return self.mcp_servers.get(server_name)
        return None
    
    async def execute_tool_call_async(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single tool call using MCP stdio protocol.
        
        Args:
            tool_call: Dictionary containing 'name' and 'arguments'
            
        Returns:
            Dictionary with execution result
        """
        tool_name = tool_call.get('name')
        arguments = tool_call.get('arguments', {})
        
        if not tool_name:
            return {"success": False, "error": "Tool name not specified", "stage": "validation"}

        # Client-side validation before contacting MCP server
        validation_error = self._validate_tool_call(tool_name, arguments)
        if validation_error:
            print(f"❌ Validation failed for tool '{tool_name}': {validation_error}")
            return {"success": False, "error": f"Validation failed: {validation_error}", "name": tool_name, "arguments": arguments, "stage": "validation"}
        
        server_path = self.determine_server_for_tool(tool_name)
        if not server_path:
            return {"success": False, "error": f"Unknown tool: {tool_name}", "name": tool_name, "stage": "routing"}
        
        full_server_path = f"{self.base_dir}/{server_path}"
        
        try:
            print(f"🔧 Executing {tool_name} via MCP server: {server_path}")
            print(f"📋 Arguments: {json.dumps(arguments, indent=2)}")
            
            # Start the MCP server process using virtual environment
            venv_script = f"{self.base_dir}/run_with_venv.sh"
            process = await asyncio.create_subprocess_exec(
                venv_script, "python", full_server_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.base_dir
            )
            
            # Send initialization request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "rag-tool-executor", "version": "1.0.0"}
                }
            }
            
            init_data = json.dumps(init_request) + "\n"
            process.stdin.write(init_data.encode())
            await process.stdin.drain()
            
            # Read initialization response (skip log lines, find JSON)
            init_response = None
            for _ in range(10):  # Try up to 10 lines
                response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
                if not response_line:
                    break
                
                line_text = response_line.decode().strip()
                if line_text.startswith('{'):
                    try:
                        init_response = json.loads(line_text)
                        break
                    except json.JSONDecodeError:
                        continue
            
            if not init_response:
                return {"error": "No valid JSON initialization response from MCP server"}
            
            if "error" in init_response:
                return {"error": f"MCP initialization failed: {init_response['error']}"}
            
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
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            tool_data = json.dumps(tool_request) + "\n"
            process.stdin.write(tool_data.encode())
            await process.stdin.drain()
            
            # Read tool call response (skip log lines, find JSON)
            tool_response = None
            for _ in range(10):  # Try up to 10 lines
                response_line = await asyncio.wait_for(process.stdout.readline(), timeout=30.0)
                if not response_line:
                    break
                
                response_text = response_line.decode().strip()
                print(f"🔍 Raw MCP server line: '{response_text}'")
                
                if response_text.startswith('{'):
                    try:
                        tool_response = json.loads(response_text)
                        print(f"✅ Found valid JSON response")
                        break
                    except json.JSONDecodeError as e:
                        print(f"⚠️  JSON parse error: {e}")
                        continue
            
            if not tool_response:
                return {"success": False, "error": "No valid JSON response from MCP server for tool call", "name": tool_name, "stage": "execution"}
            
            # Terminate the process
            process.terminate()
            await process.wait()
            
            if "result" in tool_response:
                print(f"✅ Tool executed successfully")
                return {"success": True, "result": tool_response["result"]}
            else:
                error_msg = tool_response.get("error", "Unknown error")
                print(f"❌ Tool execution failed: {error_msg}")
                return {"success": False, "error": error_msg, "name": tool_name, "stage": "execution"}
                
        except Exception as e:
            error_msg = f"Exception during tool execution: {str(e)}"
            print(f"❌ Tool execution failed: {error_msg}")
            
            # Try to read any remaining output for debugging
            if 'process' in locals() and process.stdout:
                try:
                    remaining_output = await asyncio.wait_for(process.stdout.read(), timeout=1.0)
                    if remaining_output:
                        print(f"🔍 Remaining MCP server output: '{remaining_output.decode()}'")
                except:
                    pass
            
            if 'process' in locals():
                process.terminate()
                await process.wait()
            return {"success": False, "error": error_msg, "name": tool_name, "stage": "exception"}
    
    def execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous wrapper for execute_tool_call_async."""
        return asyncio.run(self.execute_tool_call_async(tool_call))
    
    async def execute_all_tool_calls_async(self, text: str) -> List[Dict[str, Any]]:
        """Extract and execute all tool calls from text asynchronously.
        
        Args:
            text: Text containing potential tool calls
            
        Returns:
            List of execution results
        """
        tool_calls = self.extract_json_tool_calls(text)
        results = []
        
        if not tool_calls:
            print("ℹ️  No tool calls found in the text")
            return results
        
        print(f"🔍 Found {len(tool_calls)} tool call(s)")
        
        for i, tool_call in enumerate(tool_calls, 1):
            print(f"\n--- Executing Tool Call {i}/{len(tool_calls)} ---")
            # Validate each call; skip invalid ones but record error
            validation_error = self._validate_tool_call(tool_call.get('name'), tool_call.get('arguments', {}))
            if validation_error:
                err = {"success": False, "error": f"Validation failed: {validation_error}", "name": tool_call.get('name'), "arguments": tool_call.get('arguments', {}), "stage": "validation"}
                print(f"❌ Skipping invalid tool call: {err}")
                results.append(err)
                continue
            result = await self.execute_tool_call_async(tool_call)
            results.append(result)
        
        return results    
    def execute_all_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        """Synchronous wrapper for execute_all_tool_calls_async."""
        return asyncio.run(self.execute_all_tool_calls_async(text))


def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python tool_executor.py <rag_response_text>")
        print("   or: python tool_executor.py --test")
        sys.exit(1)
    
    if sys.argv[1] == "--test":
        # Test with sample tool call
        test_text = '''
        The browser MCP server can be used to open Wikipedia. The appropriate action is to call the `open_url` tool with the URL for Wikipedia.
        
        **Tool Call:**
        ```json
        {
          "name": "open_url",
          "arguments": {
            "url": "https://en.wikipedia.org"
          }
        }
        ```
        
        This will navigate to the Wikipedia homepage in the browser.
        '''
        
        executor = ToolCallExecutor()
        results = executor.execute_all_tool_calls(test_text)
        
        print("\n=== Execution Results ===")
        for i, result in enumerate(results, 1):
            print(f"Result {i}: {json.dumps(result, indent=2)}")
    else:
        # Execute tool calls from provided text
        text = " ".join(sys.argv[1:])
        
        executor = ToolCallExecutor()
        results = executor.execute_all_tool_calls(text)
        
        print("\n=== Execution Results ===")
        for i, result in enumerate(results, 1):
            print(f"Result {i}: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    main()
