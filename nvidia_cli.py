#!/usr/bin/env python3
import sys
import argparse
from openai import OpenAI
from pathlib import Path

# Nvidia NIM Configuration
NVIDIA_API_KEY = "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"
MODEL_NAME = "qwen/qwen3-coder-480b-a35b-instruct"
BASE_URL = "https://integrate.api.nvidia.com/v1"

def ask_nvidia(prompt: str):
    client = OpenAI(
        base_url=BASE_URL,
        api_key=NVIDIA_API_KEY
    )

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            top_p=0.8,
            max_tokens=4096,
            stream=False # Synchronous for easy CLI shell capture
        )
        
        if completion.choices:
            print(completion.choices[0].message.content)
            
    except Exception as e:
        print(f"Error contacting Nvidia NIM: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ARIA Nvidia NIM CLI")
    parser.add_argument("-f", "--file", type=str, help="Path to prompt file")
    
    args = parser.parse_args()
    
    if args.file:
        prompt_path = Path(args.file)
        if prompt_path.exists():
            with open(prompt_path, 'r') as f:
                ask_nvidia(f.read())
        else:
            print(f"Error: Prompt file {args.file} not found.", file=sys.stderr)
            sys.exit(1)
    else:
        # Direct string input from stdin/args if needed
        # (This matches how gemini_cli.py was used)
        pass
