#!/usr/bin/env python3

import argparse
import subprocess
import sys
from shutil import which

def check_tool_installed(tool_name):
    if which(tool_name) is None:
        print(f"Error: {tool_name} is not installed. Please install it to use this script.")
        sys.exit(1)

def ocrmypdf_cli(input_file, output_file, language='eng', deskew=False, force_ocr=False):
    try:
        command = ['ocrmypdf']
        if language:
            command.extend(['--language', language])
        if deskew:
            command.append('--deskew')
        if force_ocr:
            command.append('--force-ocr')
        command.extend([input_file, output_file])
        
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print("OCR processing completed successfully.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error during OCR processing: {e.stderr}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="A CLI wrapper for ocrmypdf to enhance PDFs with OCR.",
                                     epilog="Example: pdf_manipulation_python_agent.py input.pdf output.pdf --language eng --deskew")
    parser.add_argument('input_file', help='The input PDF file to process.')
    parser.add_argument('output_file', help='The output PDF file to save the processed document.')
    parser.add_argument('--language', default='eng', help='The language code for OCR (default: eng).')
    parser.add_argument('--deskew', action='store_true', help='Automatically deskew pages.')
    parser.add_argument('--force-ocr', action='store_true', help='Force OCR even if text is already present.')

    args = parser.parse_args()

    check_tool_installed('ocrmypdf')
    ocrmypdf_cli(args.input_file, args.output_file, args.language, args.deskew, args.force_ocr)

if __name__ == '__main__':
    main()