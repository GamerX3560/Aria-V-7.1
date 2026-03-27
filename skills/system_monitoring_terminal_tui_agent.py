#!/usr/bin/env python3

import argparse
import subprocess
import sys

def check_tool_installed(tool_name):
    try:
        subprocess.run([tool_name, '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print(f"Error: {tool_name} is not installed. Please install it to use this script.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error: {tool_name} failed to run. {e.stderr.decode().strip()}", file=sys.stderr)
        sys.exit(1)

def run_glances(args):
    command = ['glances']
    if args.cpu:
        command.append('--process-cpu')
    if args.memory:
        command.append('--process-memory')
    if args.disk:
        command.append('--process-disk')
    if args.network:
        command.append('--process-network')
    if args.full:
        command.append('--full')
    if args.interval:
        command.extend(['-t', str(args.interval)])
    if args.output:
        command.extend(['-o', args.output])

    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error: Glances failed to run. {e.stderr}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='CLI wrapper for Glances, a system monitoring tool.')
    parser.add_argument('--cpu', action='store_true', help='Show CPU usage per process')
    parser.add_argument('--memory', action='store_true', help='Show memory usage per process')
    parser.add_argument('--disk', action='store_true', help='Show disk I/O usage per process')
    parser.add_argument('--network', action='store_true', help='Show network I/O usage per process')
    parser.add_argument('--full', action='store_true', help='Show all information')
    parser.add_argument('--interval', type=int, help='Set the refresh interval (seconds)')
    parser.add_argument('--output', choices=['stdout', 'csv', 'json', 'html'], help='Set the output format')

    args = parser.parse_args()

    check_tool_installed('glances')
    run_glances(args)

if __name__ == '__main__':
    main()