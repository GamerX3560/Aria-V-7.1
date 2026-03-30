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

def run_scrcpy(args):
    command = ['scrcpy']
    if args.serial:
        command.extend(['-s', args.serial])
    if args.record:
        command.extend(['--record', args.record])
    if args.bit_rate:
        command.extend(['--bit-rate', args.bit_rate])
    if args.max_size:
        command.extend(['--max-size', str(args.max_size)])
    if args.turn_screen_off:
        command.append('--turn-screen-off')
    if args.no_control:
        command.append('--no-control')
    if args.fullscreen:
        command.append('--fullscreen')

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: scrcpy failed to run. {e.stderr.decode().strip()}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='CLI wrapper for scrcpy, an Android screen mirroring tool.',
                                     epilog='Example: python3 android_adb_automation_scrcpy_agent.py -s 192.168.1.100:5555 --record output.mp4')
    parser.add_argument('-s', '--serial', help='Serial number of the device to connect to.')
    parser.add_argument('--record', help='Record the screen to a file.')
    parser.add_argument('--bit-rate', help='Set the bit rate (e.g., 2M for 2 Mbps).')
    parser.add_argument('--max-size', type=int, help='Set the maximum size of the video frame (e.g., 1024).')
    parser.add_argument('--turn-screen-off', action='store_true', help='Turn the device screen off.')
    parser.add_argument('--no-control', action='store_true', help='Disable device control (touch, keys).')
    parser.add_argument('--fullscreen', action='store_true', help='Start in fullscreen mode.')

    args = parser.parse_args()

    check_tool_installed('scrcpy')
    run_scrcpy(args)

if __name__ == '__main__':
    main()