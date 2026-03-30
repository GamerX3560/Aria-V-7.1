"""
ARIA v7 — Skill Evolver
Autonomously discovers, evaluates, and installs new skills.
Auto-generated skills go into ~/aria/skills/evolved/ to keep
the main skills directory clean.
"""

import os
import json
import time
import subprocess
import logging
from pathlib import Path
from typing import List, Optional

log = logging.getLogger("ARIA.evolver")

ARIA_DIR = Path.home() / "aria"
SKILLS_DIR = ARIA_DIR / "skills"
EVOLVED_DIR = SKILLS_DIR / "evolved"
EVOLUTION_LOG = ARIA_DIR / "memory" / "evolution_log.json"


class SkillEvolver:
    """
    Autonomous skill discovery and installation pipeline.
    
    Pipeline:
    1. Discover — scan awesome-skills repos, GitHub, user requests
    2. Evaluate — check if the new skill is safe and useful
    3. Install — create the skill wrapper in skills/evolved/
    4. Register — update skill_loader so ARIA can use it
    
    Auto-generated/random skills go in skills/evolved/ to keep
    the main skills/ directory clean (as per user request).
    """

    def __init__(self):
        EVOLVED_DIR.mkdir(parents=True, exist_ok=True)
        self._log = self._load_log()

    def _load_log(self) -> dict:
        try:
            with open(EVOLUTION_LOG, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"evolved_skills": [], "rejected": [], "total_installed": 0}

    def _save_log(self):
        EVOLUTION_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(EVOLUTION_LOG, 'w') as f:
            json.dump(self._log, f, indent=2)

    def discover_from_awesome_skills(self) -> List[dict]:
        """Scan the awesome-skills repos for new skill candidates."""
        candidates = []
        search_dirs = [
            ARIA_DIR / "reference_repos" / "antigravity-awesome-skills",
            ARIA_DIR / "reference_repos" / "awesome-openclaw-skills",
            ARIA_DIR / "reference_repos" / "awesome-codex-skills",
            ARIA_DIR / "repo_sources" / "awesome-openclaw-skills",
        ]
        
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            for skill_md in search_dir.rglob("SKILL.md"):
                try:
                    content = skill_md.read_text(errors="ignore")
                    meta = self._parse_yaml_frontmatter(content)
                    name = meta.get("name", skill_md.parent.name)
                    
                    # Skip already installed
                    if self._is_installed(name):
                        continue
                    
                    candidates.append({
                        "name": name,
                        "description": meta.get("description", ""),
                        "source_path": str(skill_md),
                        "type": "skill_md",
                    })
                except Exception:
                    continue
        
        log.info(f"Discovered {len(candidates)} new skill candidates")
        return candidates

    def discover_from_command(self, tool_name: str) -> Optional[dict]:
        """
        Check if a command-line tool exists and create a skill for it.
        Uses `which` and `--help` to gather info.
        """
        try:
            which_result = subprocess.run(
                ["which", tool_name], capture_output=True, text=True, timeout=5
            )
            if which_result.returncode != 0:
                return None
            
            # Get help text
            help_result = subprocess.run(
                [tool_name, "--help"], capture_output=True, text=True, timeout=5
            )
            help_text = (help_result.stdout or help_result.stderr or "")[:500]
            
            return {
                "name": tool_name,
                "path": which_result.stdout.strip(),
                "description": help_text.split("\n")[0] if help_text else f"CLI tool: {tool_name}",
                "type": "cli_tool",
            }
        except Exception:
            return None

    def create_skill_wrapper(self, name: str, description: str, 
                            command: str, category: str = "utility") -> str:
        """
        Generate a Python skill wrapper and save to skills/evolved/.
        
        Returns:
            Path to the created skill file.
        """
        safe_name = name.replace("-", "_").replace(" ", "_").lower()
        skill_path = EVOLVED_DIR / f"{safe_name}_skill.py"
        
        content = f'''"""
Auto-generated ARIA skill: {name}
Category: {category}
Description: {description}
Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}
"""

import subprocess
import sys

def run(args=None):
    """Execute the {name} skill."""
    cmd = """{command}"""
    if args:
        cmd += " " + " ".join(args) if isinstance(args, list) else " " + str(args)
    
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=60
        )
        output = result.stdout.strip()
        if result.returncode != 0:
            output += f"\\nError: {{result.stderr.strip()}}"
        return output if output else "(completed successfully)"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 60s"
    except Exception as e:
        return f"Error: {{e}}"

if __name__ == "__main__":
    args = sys.argv[1:] if len(sys.argv) > 1 else None
    print(run(args))
'''
        skill_path.write_text(content)
        
        # Record in evolution log
        self._log["evolved_skills"].append({
            "name": name,
            "path": str(skill_path),
            "description": description,
            "category": category,
            "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        })
        self._log["total_installed"] = self._log.get("total_installed", 0) + 1
        self._save_log()
        
        log.info(f"Created evolved skill: {skill_path}")
        return str(skill_path)

    def list_evolved_skills(self) -> List[dict]:
        """List all auto-generated skills."""
        return self._log.get("evolved_skills", [])

    def get_stats(self) -> str:
        """Get evolution stats."""
        total = self._log.get("total_installed", 0)
        evolved = len(list(EVOLVED_DIR.glob("*.py")))
        return (
            f"🧬 Skill Evolution Stats:\n"
            f"  Evolved skills: {evolved}\n"
            f"  Total created: {total}\n"
            f"  Rejected: {len(self._log.get('rejected', []))}"
        )

    def _is_installed(self, name: str) -> bool:
        """Check if a skill is already installed."""
        safe = name.replace("-", "_").replace(" ", "_").lower()
        return (
            (EVOLVED_DIR / f"{safe}_skill.py").exists() or
            (SKILLS_DIR / f"{safe}.py").exists()
        )

    @staticmethod
    def _parse_yaml_frontmatter(text: str) -> dict:
        if not text.startswith("---"):
            return {}
        end = text.find("---", 3)
        if end == -1:
            return {}
        result = {}
        for line in text[3:end].strip().split("\n"):
            if ":" in line:
                key, _, value = line.partition(":")
                result[key.strip()] = value.strip()
        return result
