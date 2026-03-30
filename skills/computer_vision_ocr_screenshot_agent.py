#!/usr/bin/env python3

import argparse
import subprocess
import sys
from pathlib import Path

def check_tool_installed(tool_name):
    try:
        subprocess.run([tool_name, '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print(f"Error: {tool_name} is not installed. Please install it to use this script.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error: {tool_name} failed to run. {e.stderr.decode().strip()}", file=sys.stderr)
        sys.exit(1)

def run_easyocr(image_path):
    try:
        result = subprocess.run(['easyocr', image_path, '--gpu', 'false'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode().strip()
    except FileNotFoundError:
        print("Error: easyocr command not found. Please ensure easyocr is installed and accessible in your PATH.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error: easyocr failed to process the image. {e.stderr.decode().strip()}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="A CLI wrapper for EasyOCR to perform OCR on screenshots.")
    parser.add_argument('image_path', type=str, help='Path to the screenshot image file')
    args = parser.parse_args()

    image_path = Path(args.image_path)
    if not image_path.exists():
        print(f"Error: The file {image_path} does not exist.", file=sys.stderr)
        sys.exit(1)

    check_tool_installed('easyocr')
    result = run_easyocr(str(image_path))
    print(result)

if __name__ == "__main__":
    main()

"""
Usage example:
$ ~/aria/skills/computer_vision_ocr_screenshot_agent.py /path/to/screenshot.png
"""