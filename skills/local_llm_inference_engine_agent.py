#!/usr/bin/env python3

import argparse
import subprocess
import sys

def check_tool_installed(tool_name):
    try:
        subprocess.run([tool_name, '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print(f"Error: {tool_name} is not installed. Please install it to use this script.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError:
        print(f"Error: {tool_name} is installed but failed to run. Please check your installation.", file=sys.stderr)
        sys.exit(1)

def run_llama_cpp(args):
    try:
        result = subprocess.run(['llama.cpp'] + args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error: llama.cpp failed with the following message:\n{e.stderr}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='CLI wrapper for llama.cpp, a local LLM inference engine.')
    parser.add_argument('--prompt', '-p', type=str, required=True, help='The prompt to send to the LLM.')
    parser.add_argument('--model', '-m', type=str, default='default_model.bin', help='The model file to use.')
    parser.add_argument('--threads', '-t', type=int, default=4, help='Number of threads to use.')
    parser.add_argument('--n_predict', '-n', type=int, default=128, help='Number of tokens to predict.')
    parser.add_argument('--top_k', '-k', type=int, default=40, help='Value for top-k sampling.')
    parser.add_argument('--top_p', '-P', type=float, default=0.9, help='Value for nucleus sampling.')
    parser.add_argument('--temp', type=float, default=0.7, help='Temperature value for sampling.')
    parser.add_argument('--repeat_last_n', type=int, default=64, help='Number of last tokens to consider for penalizing repetition.')
    parser.add_argument('--repeat_penalty', type=float, default=1.3, help='Penalty for repeated tokens.')

    args = parser.parse_args()

    check_tool_installed('llama.cpp')

    llama_args = [
        '-m', args.model,
        '-t', str(args.threads),
        '-n', str(args.n_predict),
        '-k', str(args.top_k),
        '-P', str(args.top_p),
        '--temp', str(args.temp),
        '--repeat_last_n', str(args.repeat_last_n),
        '--repeat_penalty', str(args.repeat_penalty),
        '-p', args.prompt
    ]

    run_llama_cpp(llama_args)

if __name__ == '__main__':
    main()

"""
Usage example:
./local_llm_inference_engine_agent.py --prompt "Explain the concept of machine learning."
"""