#!/usr/bin/env python3

import argparse
import subprocess
import sys

def run_sniffnet(interface, duration):
    try:
        result = subprocess.run(
            ['sniffnet', '-i', interface, '-t', str(duration)],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running sniffnet: {e.stderr}", file=sys.stderr)
    except FileNotFoundError:
        print("Error: sniffnet is not installed. Please install it to use this tool.", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="CLI wrapper for sniffnet, a network security scanner for Linux.")
    parser.add_argument('-i', '--interface', required=True, help='Network interface to listen on (e.g., eth0)')
    parser.add_argument('-t', '--duration', type=int, required=True, help='Duration in seconds to run the scan')
    args = parser.parse_args()

    run_sniffnet(args.interface, args.duration)

if __name__ == '__main__':
    main()

"""
Usage example:
python3 ~/aria/skills/network_security_scanner_linux_agent.py -i eth0 -t 60
"""