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
    except subprocess.CalledProcessError as e:
        print(f"Error: {tool_name} failed to run. {e.stderr.decode().strip()}")
        sys.exit(1)

def create_backup(repo, source, options=[]):
    try:
        command = ['borg', 'create'] + options + [f'{repo}::{source}', source]
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode().strip())
    except subprocess.CalledProcessError as e:
        print(f"Error creating backup: {e.stderr.decode().strip()}")

def list_backups(repo):
    try:
        command = ['borg', 'list', repo]
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode().strip())
    except subprocess.CalledProcessError as e:
        print(f"Error listing backups: {e.stderr.decode().strip()}")

def extract_backup(repo, archive, destination):
    try:
        command = ['borg', 'extract', f'{repo}::{archive}', '-C', destination]
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode().strip())
    except subprocess.CalledProcessError as e:
        print(f"Error extracting backup: {e.stderr.decode().strip()}")

def main():
    check_tool_installed('borg')

    parser = argparse.ArgumentParser(description='CLI wrapper for Borg, an encrypted backup tool.',
                                     epilog='Example: data_backup_sync_encrypted_agent.py create /path/to/repo /path/to/source --compression lz4')
    subparsers = parser.add_subparsers(dest='command', required=True, help='Sub-command help')

    create_parser = subparsers.add_parser('create', help='Create a new backup archive')
    create_parser.add_argument('repo', help='Repository path')
    create_parser.add_argument('source', help='Source directory to backup')
    create_parser.add_argument('--compression', help='Compression algorithm (e.g., lz4, zlib, zstd)')
    create_parser.add_argument('--exclude', help='Exclude pattern')

    list_parser = subparsers.add_parser('list', help='List archives in a repository')
    list_parser.add_argument('repo', help='Repository path')

    extract_parser = subparsers.add_parser('extract', help='Extract an archive')
    extract_parser.add_argument('repo', help='Repository path')
    extract_parser.add_argument('archive', help='Archive name')
    extract_parser.add_argument('destination', help='Destination directory for extraction')

    args = parser.parse_args()

    if args.command == 'create':
        options = []
        if args.compression:
            options.extend(['--compression', args.compression])
        if args.exclude:
            options.extend(['--exclude', args.exclude])
        create_backup(args.repo, args.source, options)
    elif args.command == 'list':
        list_backups(args.repo)
    elif args.command == 'extract':
        extract_backup(args.repo, args.archive, args.destination)

if __name__ == '__main__':
    main()