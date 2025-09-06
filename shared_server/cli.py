#!/usr/bin/env python3
"""CLI utility for managing the shared server system."""

import argparse
import sys
from typing import List

from .client import ServerClient, is_app_running
from .config import get_config


def cmd_status(args):
    """Show status of all registered apps and MCP servers."""
    config = get_config()
    apps = config.app_config.get('apps', {})
    
    print("\n=== Shared Server Status ===")
    print(f"{'App Name':<15} {'Enabled':<8} {'Status':<10} {'Port':<6} {'Description'}")
    print("-" * 70)
    
    if not apps:
        print("No apps configured.")
    else:
        for app_name, app_config in apps.items():
            enabled = "✓" if app_config.get('enabled', True) else "✗"
            port = app_config.get('port', 'N/A')
            description = app_config.get('description', '')
            
            if app_config.get('enabled', True):
                running = is_app_running(app_name)
                status = "RUNNING" if running else "STOPPED"
            else:
                status = "DISABLED"
                
            print(f"{app_name:<15} {enabled:<8} {status:<10} {port:<6} {description}")
    
    # Show MCP servers
    mcp_servers = config.mcp_config.get('mcp_servers', {})
    if mcp_servers:
        print("\n=== MCP Servers ===")
        print(f"{'Server Name':<15} {'Port':<6} {'Status':<10} {'Description'}")
        print("-" * 70)
        for server_name, server_config in mcp_servers.items():
            port = server_config.get('port', 'N/A')
            enabled = '✓' if server_config.get('enabled', True) else '✗'
            description = server_config.get('description', 'No description')
            print(f"{server_name:<15} {port:<6} {enabled:<10} {description}")
    
    print()


def cmd_send(args):
    """Send a command to a specific app."""
    app_name = args.app
    command = args.app_command
    
    # Parse additional arguments as key=value pairs
    cmd_args = {}
    for arg in args.args:
        if '=' in arg:
            key, value = arg.split('=', 1)
            # Try to parse as int/float, otherwise keep as string
            try:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                pass
            cmd_args[key] = value
        else:
            # Positional argument, add as 'arg0', 'arg1', etc.
            key = f'arg{len(cmd_args)}'
            cmd_args[key] = arg
            
    try:
        client = ServerClient(app_name)
        response = client.send_command(command, cmd_args)
        
        if response.get('status') == 'success':
            print(f"✓ {response.get('message', 'Command executed successfully')}")
            if 'data' in response:
                from pprint import pprint
                pprint(response['data'])
        else:
            print(f"✗ {response.get('message', 'Command failed')}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


def cmd_config(args):
    """Show or modify configuration."""
    config = get_config()
    
    if args.action == 'show':
        if args.app:
            app_config = config.get_app_config(args.app)
            if not app_config:
                print(f"No configuration found for app '{args.app}'")
                return
            print(f"Configuration for {args.app}:")
            for key, value in app_config.items():
                print(f"  {key}: {value}")
        else:
            print("Server Configuration:")
            server_config = config.get_server_config()
            for key, value in server_config.items():
                print(f"  {key}: {value}")
            print("\nApps:")
            for app_name in config.config.get('apps', {}):
                enabled = config.is_app_enabled(app_name)
                port = config.get_app_port(app_name)
                print(f"  {app_name}: port={port}, enabled={enabled}")
                
    elif args.action == 'set':
        if not args.app:
            print("App name required for 'set' action")
            sys.exit(1)
            
        if args.port:
            config.set_app_port(args.app, args.port)
            print(f"Set port for {args.app} to {args.port}")
            
        if args.enabled is not None:
            config.enable_app(args.app, args.enabled)
            status = "enabled" if args.enabled else "disabled"
            print(f"{args.app} {status}")
            
        config.save_config()
        
    elif args.action == 'reset':
        # Reset to defaults
        config.config = config._load_config()
        config.save_config()
        print("Configuration reset to defaults")


def cmd_list_commands(args):
    """List available commands for an app."""
    app_name = args.app
    
    # App-specific command lists
    commands = {
        'radio_player': [
            'play - Start/resume playback',
            'pause - Pause playback',
            'stop - Stop playback',
            'next - Next station',
            'prev - Previous station',
            'volume level=<0-100> - Set volume',
            'status - Get current status',
            'add url=<url> name=<name> - Add custom station',
            'search name=<name> - Search stations'
        ],
        'words': [
            'set_text text=<text> - Set document text',
            'insert_text offset=<pos> text=<text> - Insert text at position',
            'open path=<file> - Open document',
            'save path=<file> - Save document'
        ],
        'browser': [
            'open url=<url> - Open URL',
            'back - Navigate back',
            'forward - Navigate forward',
            'reload - Reload page',
            'bookmark_add [url=<url>] [name=<name>] - Add bookmark',
            'click selector=<css> - Click element by CSS selector',
            'click_text text=<text> - Click link/button by text',
            'get_html_sync - Get current page HTML',
            'summarize - Summarize current page into JSON'
        ]
    }
    
    if app_name in commands:
        print(f"Available commands for {app_name}:")
        for cmd in commands[app_name]:
            print(f"  {cmd}")
    else:
        print(f"No command list available for '{app_name}'")
        print("Try sending 'help' command to the app directly.")


def cmd_mcp(args):
    """Handle MCP server management commands."""
    from .server import get_shared_server
    
    server = get_shared_server()
    
    if args.mcp_action == 'start':
        if args.server_name == 'all':
            # Start all enabled MCP servers
            success = server.start_all_mcp_servers()
            if success:
                print("✓ Started all enabled MCP servers")
            else:
                print("✗ Failed to start some MCP servers")
                sys.exit(1)
        elif args.server_name:
            success = server.start_mcp_server(args.server_name)
            if success:
                print(f"✓ Started MCP server: {args.server_name}")
            else:
                print(f"✗ Failed to start MCP server: {args.server_name}")
                sys.exit(1)
        else:
            print("Error: server name required for start command (use 'all' to start all servers)")
            sys.exit(1)
    
    elif args.mcp_action == 'stop':
        if args.server_name == 'all':
            # Stop all running MCP servers
            success = server.stop_all_mcp_servers()
            if success:
                print("✓ Stopped all MCP servers")
            else:
                print("✗ Failed to stop some MCP servers")
                sys.exit(1)
        elif args.server_name:
            success = server.stop_mcp_server(args.server_name)
            if success:
                print(f"✓ Stopped MCP server: {args.server_name}")
            else:
                print(f"✗ Failed to stop MCP server: {args.server_name}")
                sys.exit(1)
        else:
            print("Error: server name required for stop command (use 'all' to stop all servers)")
            sys.exit(1)
    
    elif args.mcp_action == 'restart':
        if args.server_name == 'all':
            # Restart all enabled MCP servers
            success = server.restart_all_mcp_servers()
            if success:
                print("✓ Restarted all enabled MCP servers")
            else:
                print("✗ Failed to restart some MCP servers")
                sys.exit(1)
        elif args.server_name:
            success = server.restart_mcp_server(args.server_name)
            if success:
                print(f"✓ Restarted MCP server: {args.server_name}")
            else:
                print(f"✗ Failed to restart MCP server: {args.server_name}")
                sys.exit(1)
        else:
            print("Error: server name required for restart command (use 'all' to restart all servers)")
            sys.exit(1)
    
    elif args.mcp_action == 'enable':
        if args.server_name:
            success = server.enable_mcp_server(args.server_name)
            if success:
                print(f"✓ Enabled MCP server: {args.server_name}")
            else:
                print(f"✗ Failed to enable MCP server: {args.server_name}")
                sys.exit(1)
        else:
            print("Error: server name required for enable command")
            sys.exit(1)
    
    elif args.mcp_action == 'disable':
        if args.server_name:
            success = server.disable_mcp_server(args.server_name)
            if success:
                print(f"✓ Disabled MCP server: {args.server_name}")
            else:
                print(f"✗ Failed to disable MCP server: {args.server_name}")
                sys.exit(1)
        else:
            print("Error: server name required for disable command")
            sys.exit(1)
    
    elif args.mcp_action == 'list':
        # List all configured MCP servers
        from .config import get_config
        config = get_config()
        mcp_servers = config.get_mcp_servers()
        
        if not mcp_servers:
            print("No MCP servers configured.")
            return
        
        print("\n=== Available MCP Servers ===")
        for server_name, server_config in mcp_servers.items():
            enabled = "enabled" if server_config.get("enabled", False) else "disabled"
            port = server_config.get("port", "N/A")
            description = server_config.get("description", "No description")
            print(f"  {server_name:<15} (port {port}) - {enabled} - {description}")
    
    elif args.mcp_action == 'status':
        if args.server_name:
            # Display specific server status
            from .config import get_config
            config = get_config()
            mcp_servers = config.get_mcp_servers()
            
            if args.server_name not in mcp_servers:
                print(f"MCP server '{args.server_name}' not found.")
                return
            
            server_config = mcp_servers[args.server_name]
            print(f"\nMCP Server: {args.server_name}")
            print(f"Enabled: {server_config.get('enabled', False)}")
            print(f"Port: {server_config.get('port', 'N/A')}")
            print(f"Description: {server_config.get('description', '')}")
            
            # Check if server is running
            process_id = server_config.get("process_id")
            if process_id:
                try:
                    import psutil
                    if psutil.pid_exists(process_id):
                        print(f"Status: running (PID: {process_id})")
                    else:
                        print("Status: stopped")
                except ImportError:
                    # Fallback without psutil
                    import os
                    try:
                        os.kill(process_id, 0)
                        print(f"Status: running (PID: {process_id})")
                    except (OSError, TypeError):
                        print("Status: stopped")
            else:
                print("Status: stopped")
        else:
            # Display all MCP server status
            from .config import get_config
            config = get_config()
            mcp_servers = config.get_mcp_servers()
            
            if not mcp_servers:
                print("No MCP servers configured.")
                return
            
            print("\n=== MCP Server Status ===")
            print(f"{'Server':<15} {'Status':<10} {'Enabled':<8} {'Port':<6} {'PID':<8}")
            print("-" * 55)
            
            for server_name, server_config in mcp_servers.items():
                enabled = "✓" if server_config.get("enabled", False) else "✗"
                port = str(server_config.get("port", "N/A"))
                
                # Check if server is running
                status = "stopped"
                process_id = server_config.get("process_id")
                pid_display = str(process_id or "N/A")
                
                if process_id:
                    try:
                        import psutil
                        if psutil.pid_exists(process_id):
                            status = "running"
                    except ImportError:
                        # Fallback without psutil
                        import os
                        try:
                            os.kill(process_id, 0)
                            status = "running"
                        except (OSError, TypeError):
                            pass
                
                print(f"{server_name:<15} {status:<10} {enabled:<8} {port:<6} {pid_display:<8}")
    
    else:
        print(f"Unknown MCP action: {args.mcp_action}")
        print("Available actions: start, stop, restart, enable, disable, status, list")
        sys.exit(1)


def main(argv: List[str] = None):
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="walls-server",
        description="Manage the Walls shared server system"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show status of all apps')
    
    # Send command
    send_parser = subparsers.add_parser('send', help='Send command to an app')
    send_parser.add_argument('app', help='Target application name')
    send_parser.add_argument('app_command', help='Command to send')
    send_parser.add_argument('args', nargs='*', help='Command arguments (key=value or positional)')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('action', choices=['show', 'set', 'reset'], help='Configuration action')
    config_parser.add_argument('--app', help='Target application for config operations')
    config_parser.add_argument('--port', type=int, help='Set port for app')
    config_parser.add_argument('--enabled', type=bool, help='Enable/disable app')
    
    # List commands
    list_parser = subparsers.add_parser('commands', help='List available commands for an app')
    list_parser.add_argument('app', help='Application name')
    
    # MCP command
    mcp_parser = subparsers.add_parser('mcp', help='Manage MCP servers')
    mcp_parser.add_argument('mcp_action', choices=['start', 'stop', 'restart', 'enable', 'disable', 'status', 'list'], help='MCP action')
    mcp_parser.add_argument('server_name', nargs='?', help='MCP server name (or "all" for start/stop)')
    
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return
        
    if args.command == 'status':
        cmd_status(args)
    elif args.command == 'send':
        cmd_send(args)
    elif args.command == 'config':
        cmd_config(args)
    elif args.command == 'commands':
        cmd_list_commands(args)
    elif args.command == 'mcp':
        cmd_mcp(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()