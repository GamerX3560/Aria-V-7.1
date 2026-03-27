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

def resize_image(input_file, output_file, width, height):
    try:
        subprocess.run(['vips', 'resize', input_file, output_file, f'{width}x{height}'], check=True)
        print(f"Image resized successfully: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error resizing image: {e.stderr.decode().strip()}")

def crop_image(input_file, output_file, left, top, width, height):
    try:
        subprocess.run(['vips', 'crop', input_file, output_file, left, top, width, height], check=True)
        print(f"Image cropped successfully: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error cropping image: {e.stderr.decode().strip()}")

def flip_image(input_file, output_file, direction):
    try:
        subprocess.run(['vips', 'flip', input_file, output_file, direction], check=True)
        print(f"Image flipped successfully: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error flipping image: {e.stderr.decode().strip()}")

def main():
    check_tool_installed('vips')

    parser = argparse.ArgumentParser(description='A CLI wrapper for vips image editor.')
    subparsers = parser.add_subparsers(dest='command', help='Sub-command help')

    # Resize parser
    resize_parser = subparsers.add_parser('resize', help='Resize an image')
    resize_parser.add_argument('input_file', help='Input image file')
    resize_parser.add_argument('output_file', help='Output image file')
    resize_parser.add_argument('width', type=int, help='Width of the resized image')
    resize_parser.add_argument('height', type=int, help='Height of the resized image')

    # Crop parser
    crop_parser = subparsers.add_parser('crop', help='Crop an image')
    crop_parser.add_argument('input_file', help='Input image file')
    crop_parser.add_argument('output_file', help='Output image file')
    crop_parser.add_argument('left', type=int, help='Left coordinate of the crop area')
    crop_parser.add_argument('top', type=int, help='Top coordinate of the crop area')
    crop_parser.add_argument('width', type=int, help='Width of the crop area')
    crop_parser.add_argument('height', type=int, help='Height of the crop area')

    # Flip parser
    flip_parser = subparsers.add_parser('flip', help='Flip an image')
    flip_parser.add_argument('input_file', help='Input image file')
    flip_parser.add_argument('output_file', help='Output image file')
    flip_parser.add_argument('direction', choices=['horizontal', 'vertical'], help='Direction to flip the image')

    args = parser.parse_args()

    if args.command == 'resize':
        resize_image(args.input_file, args.output_file, args.width, args.height)
    elif args.command == 'crop':
        crop_image(args.input_file, args.output_file, args.left, args.top, args.width, args.height)
    elif args.command == 'flip':
        flip_image(args.input_file, args.output_file, args.direction)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()

"""
Usage examples:
- Resize an image: python3 image_editor_cli_python_agent.py resize input.jpg output.jpg 800 600
- Crop an image: python3 image_editor_cli_python_agent.py crop input.jpg output.jpg 100 100 400 300
- Flip an image horizontally: python3 image_editor_cli_python_agent.py flip input.jpg output.jpg horizontal
"""