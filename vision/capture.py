#!/usr/bin/env python3
import subprocess
import os
import time
import sys

def take_screenshot(region=False):
    filename = os.path.expanduser(f"~/Pictures/screenshot_{int(time.time())}.png")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if region:
        # slurp gets the region, grim takes the screenshot
        region_cmd = subprocess.run(["slurp"], capture_output=True, text=True)
        if region_cmd.returncode == 0 and region_cmd.stdout.strip():
            subprocess.run(["grim", "-g", region_cmd.stdout.strip(), filename])
    else:
        subprocess.run(["grim", filename])
    return filename

if __name__ == "__main__":
    is_region = "--region" in sys.argv
    path = take_screenshot(is_region)
    print(path)
