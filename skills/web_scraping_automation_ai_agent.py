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

def run_scrapy_command(command, args):
    try:
        result = subprocess.run(['scrapy'] + command + args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running Scrapy command: {e.stderr}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='A CLI wrapper for Scrapy, a web scraping automation tool.')
    parser.add_argument('command', choices=['crawl', 'list', 'startproject', 'shell', 'version'], help='Scrapy command to run')
    parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the Scrapy command')

    args = parser.parse_args()

    check_tool_installed('scrapy')

    run_scrapy_command([args.command], args.args)

if __name__ == '__main__':
    main()

"""
Usage example:
$ ./web_scraping_automation_ai_agent.py crawl example_spider
"""