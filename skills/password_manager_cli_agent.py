#!/usr/bin/env python3

import argparse
import subprocess
import sys

def run_pass_command(command):
    try:
        result = subprocess.run(['pass'] + command, check=True, text=True, capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"
    except FileNotFoundError:
        return "Error: 'pass' command not found. Please ensure 'pass' is installed."

def list_passwords():
    return run_pass_command(['ls'])

def show_password(service):
    return run_pass_command(['show', service])

def insert_password(service, password):
    try:
        result = subprocess.run(['pass', 'insert', '-m', service], input=password, text=True, check=True, capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"
    except FileNotFoundError:
        return "Error: 'pass' command not found. Please ensure 'pass' is installed."

def delete_password(service):
    return run_pass_command(['rm', service])

def main():
    parser = argparse.ArgumentParser(description="CLI wrapper for pass, the standard Unix password manager.")
    parser.add_argument('action', choices=['list', 'show', 'insert', 'delete'], help='Action to perform')
    parser.add_argument('service', nargs='?', help='Service name for show, insert, and delete actions')
    parser.add_argument('--password', help='Password to insert (required for insert action)')

    args = parser.parse_args()

    if args.action == 'list':
        print(list_passwords())
    elif args.action == 'show':
        if not args.service:
            print("Error: Service name is required for show action.")
            sys.exit(1)
        print(show_password(args.service))
    elif args.action == 'insert':
        if not args.service or not args.password:
            print("Error: Service name and password are required for insert action.")
            sys.exit(1)
        print(insert_password(args.service, args.password))
    elif args.action == 'delete':
        if not args.service:
            print("Error: Service name is required for delete action.")
            sys.exit(1)
        print(delete_password(args.service))

if __name__ == '__main__':
    main()