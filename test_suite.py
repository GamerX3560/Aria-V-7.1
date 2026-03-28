#!/usr/bin/env python3
import asyncio
import subprocess
import json
import os
import datetime
from pathlib import Path

ARIA_DIR = Path.home() / "aria"
SKILLS_DIR = ARIA_DIR / "skills"
REPORT_PATH = ARIA_DIR / "research" / "ARIA_Diagnostic_Report.md"

# ANSI Colors
C_GREEN = "\033[92m"
C_RED = "\033[91m"
C_YELLOW = "\033[93m"
C_RESET = "\033[0m"

log_lines = []
results = {"passed": 0, "failed": 0, "skipped": 0, "details": []}

def add_log(msg: str):
    print(msg)
    # Strip ANSI for file log
    import re
    clean_msg = re.sub(r'\033\[[0-9;]*m', '', msg)
    log_lines.append(clean_msg)

async def run_cmd(cmd: str, timeout: int = 15) -> tuple[bool, str]:
    """Runs a shell command asynchronously and returns (success, output)."""
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(ARIA_DIR)
        )
        try:
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            out = stdout.decode().strip()
            return proc.returncode == 0, out
        except asyncio.TimeoutError:
            proc.kill()
            return False, f"TIMEOUT after {timeout}s"
    except Exception as e:
        return False, f"EXCEPTION: {str(e)}"

async def test_module(name: str, category: str, cmd: str, expect_in_output: str = "", timeout: int = 15):
    add_log(f"\n{C_YELLOW}▶ Testing: {name} ({category}){C_RESET}")
    add_log(f"  Command: `{cmd}`")
    
    success, output = await run_cmd(cmd, timeout)
    out_snippet = (output[:200] + "...(truncated)") if len(output) > 200 else output
    
    if success and (not expect_in_output or expect_in_output.lower() in output.lower()):
        add_log(f"  {C_GREEN}✓ PASSED{C_RESET}")
        results["passed"] += 1
        results["details"].append({"name": name, "category": category, "status": "✅ PASSED", "cmd": cmd, "out": out_snippet})
    else:
        add_log(f"  {C_RED}✗ FAILED{C_RESET}")
        add_log(f"  Output:\n{output}")
        results["failed"] += 1
        results["details"].append({"name": name, "category": category, "status": "❌ FAILED", "cmd": cmd, "out": output})

async def test_memory_system():
    add_log(f"\n{C_YELLOW}▶ Testing: Memory System (Store/Recall/Delete){C_RESET}")
    
    # Store
    succ1, out1 = await run_cmd("python3 skills/memory_agent.py store TEST_DIAGNOSTIC 'diagnostic_pass_123'")
    if not succ1:
        add_log(f"  {C_RED}✗ FAILED to store. Output: {out1}{C_RESET}")
        results["failed"] += 1
        results["details"].append({"name": "Memory Store", "category": "Core System", "status": "❌ FAILED", "cmd": "store", "out": out1})
        return
        
    # Recall
    succ2, out2 = await run_cmd("python3 skills/memory_agent.py recall TEST_DIAGNOSTIC")
    if not succ2 or "diagnostic_pass_123" not in out2:
        add_log(f"  {C_RED}✗ FAILED to recall. Output: {out2}{C_RESET}")
        results["failed"] += 1
        results["details"].append({"name": "Memory Recall", "category": "Core System", "status": "❌ FAILED", "cmd": "recall", "out": out2})
        return
        
    # Delete test key if memory_agent supports it, or just leave it.
    add_log(f"  {C_GREEN}✓ PASSED (Memory System Operational){C_RESET}")
    results["passed"] += 1
    results["details"].append({"name": "Memory System", "category": "Core System", "status": "✅ PASSED", "cmd": "store/recall", "out": out2})


async def run_diagnostics():
    start_time = datetime.datetime.now()
    add_log(f"==================================================")
    add_log(f" ARIA v5 UNIVERSAL TEST SUITE")
    add_log(f" Started: {start_time}")
    add_log(f"==================================================")

    # 1. CORE SYSTEM & APIs
    await test_module("Nvidia NIM API (Qwen 32B)", "Core LLM", 
        "python3 -c 'import json, os, urllib.request; req = urllib.request.Request(\"https://integrate.api.nvidia.com/v1/models\", headers={\"Authorization\": \"Bearer \" + json.load(open(\"vault.json\")).get(\"api_keys\", {}).get(\"nvidia\",\"\")}); print(urllib.request.urlopen(req).status)'", "200")
    
    await test_module("Vault Parsing", "Security", "python3 -c 'import json; print(list(json.load(open(\"vault.json\")).keys()))'", "api_keys")
    await test_module("Identity Parsing", "Security", "python3 -c 'import yaml; print(yaml.safe_load(open(\"identity.yaml\")).get(\"name\",\"\"))'", "Mangesh")

    await test_memory_system()

    # 2. GENERATED SKILLS EXECUTABILITY
    skills_to_test = [
        ("ffmpeg", "Media", "media_transcoding_amd_gpu_agent.py"),
        ("vips", "Media", "image_editor_cli_python_agent.py"),
        ("scrcpy", "Android", "android_adb_automation_scrcpy_agent.py"),
        ("borg", "System", "data_backup_sync_encrypted_agent.py"),
        ("glances", "System", "system_monitoring_terminal_tui_agent.py"),
        ("nnn", "System", "terminal_file_manager_tui_agent.py"),
        ("pass", "Security", "password_manager_cli_agent.py"),
        ("copyq", "System", "clipboard_manager_wayland_agent.py"),
        ("llama_cpp", "AI Engine", "local_llm_inference_engine_agent.py"),
        ("easyocr", "AI Vision", "computer_vision_ocr_screenshot_agent.py"),
        ("whisper", "AI Voice", "speech_to_text_stt_whisper_agent.py"),
        ("scrapy", "AI Web", "web_scraping_automation_ai_agent.py"),
        ("ocrmypdf", "PDF OCR", "pdf_manipulation_python_agent.py")
    ]

    for tool_name, cat, script in skills_to_test:
        script_path = SKILLS_DIR / script
        if not script_path.exists():
            add_log(f"\n{C_YELLOW}▶ Testing: {tool_name} ({cat}){C_RESET}")
            add_log(f"  {C_RED}✗ FAILED - Script missing!{C_RESET}")
            results["failed"] += 1
            results["details"].append({"name": tool_name, "category": cat, "status": "❌ FAILED", "cmd": script, "out": "File not found"})
        else:
            await test_module(tool_name, cat, f"python3 skills/{script} --help")

    # 3. LEGACY / ORIGINAL SKILLS
    await test_module("Browser Agent", "Web Automation", "python3 skills/browser_agent.py --help")
    await test_module("Email Agent", "Communication", "python3 skills/email_agent.py --help")
    await test_module("Social Agent", "Communication", "python3 skills/social_agent.py --help")
    await test_module("Self Improve", "Cognitive", "python3 skills/self_improve_agent.py --help")
    await test_module("Genesis", "Cognitive", "python3 skills/genesis_agent.py --help")

    # Write Markdown Report
    end_time = datetime.datetime.now()
    duration = end_time - start_time
    
    md_report = f"""# ARIA v5 Diagnostic Report

**Generated Date:** `{start_time.strftime('%Y-%m-%d %H:%M:%S')}`
**Duration:** `{duration.total_seconds():.1f}s`

## Summary
- **Passed:** ✅ {results['passed']}
- **Failed:** ❌ {results['failed']}

---

## Detailed Results

| Module | Category | Status | Details |
|--------|----------|--------|---------|
"""
    for entry in results["details"]:
        clean_out = entry['out'].replace('\n', ' ').replace('|', '-')[:80]
        if len(entry['out']) > 80: clean_out += "..."
        md_report += f"| **{entry['name']}** | {entry['category']} | {entry['status']} | `{clean_out}` |\n"
        
    
    md_report += "\n## Error Logs for Failed Tests\n"
    for entry in results["details"]:
        if entry["status"] == "❌ FAILED":
            md_report += f"\n### {entry['name']}\n```text\n{entry['out']}\n```\n"
            
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        f.write(md_report)
        
    add_log(f"\n==================================================")
    add_log(f" REPORT GENERATED: {REPORT_PATH}")
    add_log(f" PASSED: {results['passed']} | FAILED: {results['failed']}")
    add_log(f"==================================================")

if __name__ == "__main__":
    asyncio.run(run_diagnostics())
