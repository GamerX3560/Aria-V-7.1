#!/usr/bin/env python3
"""
Batch Genesis: Auto-generate skill wrapper agents for all installed tools.
Runs genesis_agent.py for each tool sequentially.
"""
import asyncio
import sys
import logging
from pathlib import Path

sys.path.insert(0, "/home/gamerx/aria/skills")
from genesis_agent import genesis

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("BatchGenesis")

# Tools to generate skill wrappers for
# Format: (tool_name, category, install_info)
TOOLS = [
    ("ffmpeg", "media transcoding AMD GPU", "sudo pacman -S ffmpeg (already installed)"),
    ("vips", "image editor CLI python", "sudo pacman -S libvips (already installed)"),
    ("wf-recorder", "screen recording wayland", "sudo pacman -S wf-recorder (already installed)"),
    ("easyocr", "computer vision OCR screenshot", "pip install easyocr (already installed)"),
    ("ocrmypdf", "PDF manipulation python", "pip install ocrmypdf (already installed)"),
    ("whisper", "speech to text STT whisper", "pip install openai-whisper (already installed)"),
    ("scrapy", "web scraping automation AI", "pip install scrapy (already installed)"),
    ("glances", "system monitoring terminal TUI", "sudo pacman -S glances (already installed)"),
    ("nnn", "terminal file manager TUI", "sudo pacman -S nnn (already installed)"),
    ("borg", "data backup sync encrypted", "sudo pacman -S borg (already installed)"),
    ("pass", "password manager CLI", "sudo pacman -S pass (already installed)"),
    ("scrcpy", "android ADB automation scrcpy", "sudo pacman -S scrcpy (already installed)"),
    ("copyq", "clipboard manager wayland", "sudo pacman -S copyq (already installed)"),
    ("llama.cpp", "local LLM inference engine", "built from source at ~/aria/tools/llama.cpp/build/bin/llama-cli"),
    ("sniffnet", "network security scanner linux", "yay -S sniffnet"),
]

async def main():
    log.info(f"Generating {len(TOOLS)} skill wrapper agents...")
    results = []
    
    for i, (tool, category, install_info) in enumerate(TOOLS):
        log.info(f"\n{'='*50}")
        log.info(f"[{i+1}/{len(TOOLS)}] Generating: {tool} ({category})")
        log.info(f"{'='*50}")
        
        result = await genesis(tool, category, install_cmd="already installed", research_context=install_info)
        results.append(result)
        
        if result["test_passed"]:
            log.info(f"  ✓ {tool} skill created and tested!")
        else:
            log.info(f"  ⚠ {tool} skill created but tests incomplete")
        
        await asyncio.sleep(1)
    
    # Summary
    log.info(f"\n{'='*60}")
    log.info("BATCH GENESIS COMPLETE")
    log.info(f"{'='*60}")
    log.info(f"  Total tools: {len(TOOLS)}")
    log.info(f"  Skills created: {sum(1 for r in results if r['skill_created'])}")
    log.info(f"  Tests passed: {sum(1 for r in results if r['test_passed'])}")
    
    # List created skills
    for r in results:
        status = "✓" if r["test_passed"] else "⚠"
        log.info(f"  {status} {r['tool']}: {r.get('skill_path', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(main())
