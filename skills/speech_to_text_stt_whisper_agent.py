#!/usr/bin/env python3

import argparse
import subprocess
import sys

def check_tool_installed(tool_name):
    try:
        subprocess.run([sys.executable, "-m", tool_name, "--help"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print(f"Error: {tool_name} module is not installed. Please install it to use this script.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError:
        pass

def transcribe_audio(input_file):
    try:
        result = subprocess.run([sys.executable, '-m', 'whisper', input_file], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
    except FileNotFoundError:
        print("Error: whisper module not found.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to transcribe audio file. {e.stderr}", file=sys.stderr)
        sys.exit(1)

def main():
    check_tool_installed('whisper')
    
    parser = argparse.ArgumentParser(description="CLI wrapper for Whisper, an AI assistant for speech-to-text transcription.")
    parser.add_argument("input_file", help="Path to the audio file to transcribe")
    args = parser.parse_args()

    transcribe_audio(args.input_file)

if __name__ == "__main__":
    main()