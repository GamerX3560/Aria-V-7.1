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

def record_screen(output_file, duration=None, fps=None, audio=False):
    command = ['wf-recorder', '-f', output_file]
    if duration:
        command.extend(['--duration', str(duration)])
    if fps:
        command.extend(['--fps', str(fps)])
    if audio:
        command.append('--audio')
    
    try:
        subprocess.run(command, check=True)
        print(f"Screen recording saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error: Recording failed. {e.stderr.decode().strip()}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    check_tool_installed('wf-recorder')

    parser = argparse.ArgumentParser(description='CLI wrapper for wf-recorder, a screen recording tool for Wayland.')
    parser.add_argument('output_file', help='The output file for the screen recording (e.g., output.mp4)')
    parser.add_argument('--duration', type=int, help='Duration of the recording in seconds')
    parser.add_argument('--fps', type=int, help='Frames per second for the recording')
    parser.add_argument('--audio', action='store_true', help='Include audio in the recording')

    args = parser.parse_args()

    record_screen(args.output_file, args.duration, args.fps, args.audio)

if __name__ == '__main__':
    main()