#!/usr/bin/env python3
import json
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

MEMORY_PATH = Path.home() / "aria" / "memory.json"

def load_memory():
    if not MEMORY_PATH.exists():
        return {"facts": {}, "skills": {}}
    try:
        with open(MEMORY_PATH, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"facts": {}, "skills": {}}

def save_memory(data):
    # Atomic write
    tmp = str(MEMORY_PATH) + ".tmp"
    with open(tmp, 'w') as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, MEMORY_PATH)

def memory_store(key, value):
    mem = load_memory()
    if "facts" not in mem:
        mem["facts"] = {}
    mem["facts"][key] = {
        "value": value,
        "added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_memory(mem)
    print(f"STORED: '{key}' = '{value}'")

def memory_recall(query):
    mem = load_memory()
    results = []
    q = query.lower()
    for key, info in mem.get("facts", {}).items():
        if q in key.lower() or q in str(info.get("value", "")).lower():
            results.append(f"- {key}: {info['value']} (added {info.get('added', 'unknown')})")
    
    if results:
        print(f"RECAlLED facts matching '{query}':")
        print("\n".join(results))
    else:
        print(f"No facts found matching '{query}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ARIA Memory Agent")
    subparsers = parser.add_subparsers(dest="command")

    store_parser = subparsers.add_parser("store")
    store_parser.add_argument("key", type=str)
    store_parser.add_argument("value", type=str)

    recall_parser = subparsers.add_parser("recall")
    recall_parser.add_argument("query", type=str)
    
    list_parser = subparsers.add_parser("list")

    args = parser.parse_args()

    if args.command == "store":
        memory_store(args.key, args.value)
    elif args.command == "recall":
        memory_recall(args.query)
    elif args.command == "list":
        memory_recall("") # empty query matches everything
    else:
        parser.print_help()
