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
        print(f"Error: {tool_name} is installed but failed to run. Please check your installation.")
        sys.exit(1)

def run_nnn(directory=None):
    command = ['nnn']
    if directory:
        command.append(directory)
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error: nnn failed with the following message:\n{e.stderr}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="CLI wrapper for nnn, a terminal file manager TUI.")
    parser.add_argument('-d', '--directory', type=str, help='Directory to open with nnn')
    args = parser.parse_args()

    check_tool_installed('nnn')
    run_nnn(args.directory)

if __name__ == "__main__":
    main()