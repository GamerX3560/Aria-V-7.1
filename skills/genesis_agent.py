#!/usr/bin/env python3
"""
ARIA Genesis Agent — Phase C
Takes a research report, installs the winning tool, writes a Python
wrapper skill, and self-tests it. This is the "Skill Birth" engine.

Usage:
    python3 genesis_agent.py --research-file ~/aria/research/session_xxx/vision_ocr.json
    python3 genesis_agent.py --tool-name "tesseract" --install-cmd "sudo pacman -S --noconfirm tesseract" --category "OCR"
"""
import asyncio
import subprocess
import json
import sys
import os
import logging
from pathlib import Path
from datetime import datetime
from openai import AsyncOpenAI

NVIDIA_API_KEY = "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"
BASE_URL = "https://integrate.api.nvidia.com/v1"
MODEL = "qwen/qwen2.5-coder-32b-instruct"
SKILLS_DIR = Path.home() / "aria" / "skills"
GENESIS_LOG = Path.home() / "aria" / "research" / "genesis_log.json"
GENESIS_LOG.parent.mkdir(parents=True, exist_ok=True)

log = logging.getLogger("Genesis")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

aclient = AsyncOpenAI(api_key=NVIDIA_API_KEY, base_url=BASE_URL)

def run_shell(cmd: str, timeout: int = 120) -> tuple[int, str]:
    """Run a shell command and return (exit_code, output)."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout,
            env={**os.environ, "SUDO_ASKPASS": "/bin/true"}
        )
        output = (result.stdout + "\n" + result.stderr).strip()
        return result.returncode, output
    except subprocess.TimeoutExpired:
        return 1, "ERROR: Command timed out"
    except Exception as e:
        return 1, f"ERROR: {e}"

async def llm_generate(prompt: str) -> str:
    """Ask the LLM to generate code or analysis."""
    try:
        completion = await aclient.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=4096,
        )
        if completion.choices and completion.choices[0].message.content:
            return completion.choices[0].message.content.strip()
    except Exception as e:
        log.error(f"LLM generation failed: {e}")
    return ""

async def install_tool(install_cmd: str) -> bool:
    """Run the installation command."""
    log.info(f"Installing: {install_cmd}")
    # Ensure --noconfirm for pacman/yay
    if ("pacman" in install_cmd or "yay" in install_cmd) and "--noconfirm" not in install_cmd:
        install_cmd += " --noconfirm"
    # Prefix sudo with password pipe
    if "sudo" in install_cmd and "echo" not in install_cmd:
        install_cmd = install_cmd.replace("sudo ", 'echo "GamerX" | sudo -S ')
    
    code, output = run_shell(install_cmd, timeout=300)
    if code == 0:
        log.info(f"  ✓ Installation successful")
        return True
    else:
        log.error(f"  ✗ Installation failed: {output[:500]}")
        return False

async def generate_skill_wrapper(tool_name: str, category: str, install_info: str) -> str:
    """Use the LLM to write a Python wrapper script for the tool."""
    prompt = f"""You are an expert Python developer writing a CLI wrapper for ARIA, an AI assistant on Arch Linux.

TOOL: {tool_name}
CATEGORY: {category}
INSTALL INFO: {install_info}

Write a complete, production-ready Python script that:
1. Has a clear CLI interface using argparse
2. Wraps the tool's most useful features
3. Handles errors gracefully with clear error messages
4. Prints results to stdout (so ARIA can read the output)
5. Has a shebang line (#!/usr/bin/env python3)

The script should be saved as ~/aria/skills/{category.replace(' ', '_').lower()}_agent.py

IMPORTANT RULES:
- Script must be completely self-contained
- Use subprocess.run() to call the tool's CLI if needed
- Include a usage example in the docstring
- Handle the case where the tool is not installed
- Output should be plain text, not JSON (for readability in Telegram)

Return ONLY the Python code, no explanation. Start with #!/usr/bin/env python3"""

    return await llm_generate(prompt)

async def self_test_skill(skill_path: Path, category: str) -> tuple[bool, str]:
    """Run a basic smoke test on the generated skill."""
    log.info(f"Self-testing: {skill_path}")
    
    # First, check if the file is valid Python
    code, output = run_shell(f"python3 -c \"import ast; ast.parse(open('{skill_path}').read())\"")
    if code != 0:
        log.error(f"  ✗ Syntax error in generated skill")
        return False, f"Syntax error: {output}"
    
    # Try running with --help
    code, output = run_shell(f"python3 {skill_path} --help", timeout=10)
    if code == 0:
        log.info(f"  ✓ --help works")
    else:
        log.warning(f"  ⚠ --help failed: {output[:200]}")
        return False, f"Help failed: {output}"
    
    return True, "Skill passed basic tests"

async def genesis(tool_name: str, category: str, install_cmd: str = "", research_context: str = "") -> dict:
    """The full genesis pipeline: install → generate → test → register."""
    result = {
        "tool": tool_name,
        "category": category,
        "timestamp": datetime.now().isoformat(),
        "installed": False,
        "skill_created": False,
        "skill_path": "",
        "test_passed": False,
        "notes": "",
    }
    
    # Step 1: Install
    if install_cmd:
        installed = await install_tool(install_cmd)
        result["installed"] = installed
        if not installed:
            result["notes"] = "Installation failed, attempting skill generation anyway"
    else:
        result["installed"] = True  # Assume already installed
    
    # Step 2: Generate skill wrapper
    skill_code = await generate_skill_wrapper(tool_name, category, install_cmd or "pre-installed")
    
    if not skill_code or len(skill_code) < 50:
        result["notes"] += " | Skill generation failed (too short)"
        return result
    
    # Clean code block markers if present
    skill_code = skill_code.strip()
    if skill_code.startswith("```"):
        lines = skill_code.split("\n")
        skill_code = "\n".join(lines[1:])
    if skill_code.endswith("```"):
        skill_code = skill_code[:-3].strip()
    
    # Write skill file
    skill_filename = f"{category.replace(' ', '_').lower()}_agent.py"
    skill_path = SKILLS_DIR / skill_filename
    
    with open(skill_path, "w") as f:
        f.write(skill_code)
    os.chmod(skill_path, 0o755)
    
    result["skill_created"] = True
    result["skill_path"] = str(skill_path)
    log.info(f"  ✓ Skill written to {skill_path}")
    
    # Step 3: Self-test
    test_ok, test_msg = await self_test_skill(skill_path, category)
    result["test_passed"] = test_ok
    
    if not test_ok:
        # Attempt self-correction
        log.info("  Attempting self-correction...")
        fix_prompt = f"""The following Python script has an error:

ERROR: {test_msg}

ORIGINAL CODE:
{skill_code}

Fix the error and return the complete corrected Python script. Return ONLY the code."""
        
        fixed_code = await llm_generate(fix_prompt)
        if fixed_code and len(fixed_code) > 50:
            if fixed_code.startswith("```"):
                lines = fixed_code.split("\n")
                fixed_code = "\n".join(lines[1:])
            if fixed_code.endswith("```"):
                fixed_code = fixed_code[:-3].strip()
                
            with open(skill_path, "w") as f:
                f.write(fixed_code)
            
            test_ok2, test_msg2 = await self_test_skill(skill_path, category)
            result["test_passed"] = test_ok2
            if test_ok2:
                log.info("  ✓ Self-correction successful!")
            else:
                log.warning(f"  ✗ Self-correction failed: {test_msg2[:200]}")
                result["notes"] += f" | Self-correction failed: {test_msg2[:200]}"
    
    # Step 4: Log
    genesis_log = []
    if GENESIS_LOG.exists():
        try:
            with open(GENESIS_LOG) as f:
                genesis_log = json.load(f)
        except Exception:
            genesis_log = []
    genesis_log.append(result)
    with open(GENESIS_LOG, "w") as f:
        json.dump(genesis_log, f, indent=2)
    
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ARIA Genesis Agent — Skill Birth Engine")
    parser.add_argument("--tool-name", required=True, help="Name of the tool to integrate")
    parser.add_argument("--category", required=True, help="Capability category")
    parser.add_argument("--install-cmd", default="", help="Installation command")
    parser.add_argument("--research-file", default="", help="Path to research JSON for context")
    
    args = parser.parse_args()
    
    research_ctx = ""
    if args.research_file and Path(args.research_file).exists():
        with open(args.research_file) as f:
            research_ctx = json.dumps(json.load(f), indent=2)[:5000]
    
    result = asyncio.run(genesis(args.tool_name, args.category, args.install_cmd, research_ctx))
    
    if result["test_passed"]:
        print(f"✓ SUCCESS: {result['tool']} integrated as {result['skill_path']}")
    else:
        print(f"⚠ PARTIAL: {result['tool']} created but tests failed. Notes: {result['notes']}")
