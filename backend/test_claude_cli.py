#!/usr/bin/env python3
"""
Test script to verify Claude Code CLI is available and working
"""
import subprocess
import sys
import os

def test_claude_cli():
    """Test if Claude Code CLI is available"""
    print("Testing Claude Code CLI availability...")
    
    # Test 1: Check if 'claude' command exists
    try:
        result = subprocess.run(['which', 'claude'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Claude command found at: {result.stdout.strip()}")
        else:
            print("✗ Claude command not found in PATH")
            print("  You may need to install Claude Code CLI or add it to PATH")
            return False
    except Exception as e:
        print(f"✗ Error checking for claude command: {e}")
        return False
    
    # Test 2: Try to run claude --help
    try:
        result = subprocess.run(['claude', '--help'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Claude CLI responds to --help command")
            print(f"  Output preview: {result.stdout[:100]}...")
        else:
            print("✗ Claude CLI failed to run --help")
            print(f"  Error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("✗ Claude command not found - please install Claude Code CLI")
        return False
    except Exception as e:
        print(f"✗ Error running claude --help: {e}")
        return False
    
    # Test 3: Check for common Claude Code commands
    test_commands = ['search', 'download', 'translate']
    available_commands = []
    
    for cmd in test_commands:
        try:
            result = subprocess.run(['claude', cmd, '--help'], capture_output=True, text=True)
            if result.returncode == 0 or 'Usage:' in result.stdout or 'Usage:' in result.stderr:
                available_commands.append(cmd)
        except:
            pass
    
    if available_commands:
        print(f"✓ Available Claude commands: {', '.join(available_commands)}")
    else:
        print("✗ No Claude subcommands found")
        print("  The CLI may not be properly installed or may use different command names")
    
    # Test 4: Check alternative command names
    alternative_names = ['claude-code', 'claudecode', 'cc']
    for alt_name in alternative_names:
        try:
            result = subprocess.run(['which', alt_name], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  Found alternative command: {alt_name} at {result.stdout.strip()}")
        except:
            pass
    
    return True

def suggest_mock_implementation():
    """Suggest using mock implementation if CLI is not available"""
    print("\n" + "="*60)
    print("SUGGESTION: Claude Code CLI not available")
    print("="*60)
    print("\nSince the Claude Code CLI is not installed or accessible,")
    print("you have two options:\n")
    print("1. Install Claude Code CLI:")
    print("   - Follow the installation instructions for Claude Code")
    print("   - Ensure the 'claude' command is in your PATH\n")
    print("2. Use the mock implementation:")
    print("   - The system will fall back to mock_claude_code_search_service.py")
    print("   - This provides simulated search results for testing")
    print("\nTo use the mock service, update the import in claude_code_search.py")
    print("to use mock_claude_code_search_service instead of claude_code_cli_service")

if __name__ == "__main__":
    success = test_claude_cli()
    if not success:
        suggest_mock_implementation()
    
    sys.exit(0 if success else 1)