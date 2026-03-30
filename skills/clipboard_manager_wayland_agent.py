#!/usr/bin/env python3

import argparse
import subprocess
import sys

def check_tool_installed(tool_name):
    try:
        subprocess.run([tool_name, '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print(f"Error: {tool_name} is not installed. Please install it to use this script.")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print(f"Error: {tool_name} is not working correctly. Please check your installation.")
        sys.exit(1)

def list_clipboard_contents():
    try:
        result = subprocess.run(['copyq', 'list'], check=True, stdout=subprocess.PIPE, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to list clipboard contents. {e.stderr}")
        sys.exit(1)

def add_to_clipboard(text):
    try:
        subprocess.run(['copyq', 'add', text], check=True)
        print(f"Added '{text}' to clipboard.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to add text to clipboard. {e.stderr}")
        sys.exit(1)

def clear_clipboard():
    try:
        subprocess.run(['copyq', 'remove', '0:-1'], check=True)
        print("Clipboard cleared.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to clear clipboard. {e.stderr}")
        sys.exit(1)

def main():
    check_tool_installed('copyq')

    parser = argparse.ArgumentParser(description='CLI wrapper for CopyQ, a clipboard manager for Wayland.')
    subparsers = parser.add_subparsers(dest='command', help='Sub-command help')

    list_parser = subparsers.add_parser('list', help='List clipboard contents')
    add_parser = subparsers.add_parser('add', help='Add text to clipboard')
    add_parser.add_argument('text', type=str, help='Text to add to clipboard')
    clear_parser = subparsers.add_parser('clear', help='Clear clipboard')

    args = parser.parse_args()

    if args.command == 'list':
        list_clipboard_contents()
    elif args.command == 'add':
        add_to_clipboard(args.text)
    elif args.command == 'clear':
        clear_clipboard()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()

"""
Usage examples:
- List clipboard contents: python3 clipboard_manager_wayland_agent.py list
- Add text to clipboard: python3 clipboard_manager_wayland_agent.py add "Hello, World!"
- Clear clipboard: python3 clipboard_manager_wayland_agent.py clear
"""