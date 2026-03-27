"""
ARIA v6 — Dynamic Skill Loader
Scans directories for SKILL.md files and Python skill scripts,
building a live tool registry for the system prompt.
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict

log = logging.getLogger("ARIA.skills")

ARIA_DIR = Path.home() / "aria"
SKILLS_DIR = ARIA_DIR / "skills"
REGISTRY_PATH = ARIA_DIR / "SKILLS_REGISTRY.md"


class SkillLoader:
    """
    Discovers, parses, and registers skills from multiple sources:
    1. Python scripts in ~/aria/skills/
    2. SKILL.md files in any subdirectory
    3. The static SKILLS_REGISTRY.md
    """

    def __init__(self):
        self._skills: Dict[str, dict] = {}
        self._registry_content: str = ""
        self.reload()

    def reload(self):
        """Discover all skills from disk."""
        self._skills.clear()
        self._scan_python_skills()
        self._scan_skill_md_files()
        self._load_static_registry()
        log.info(f"Loaded {len(self._skills)} skills total")

    def _scan_python_skills(self):
        """Scan ~/aria/skills/ for Python skill scripts."""
        if not SKILLS_DIR.exists():
            return
        for f in SKILLS_DIR.iterdir():
            if f.suffix == ".py" and not f.name.startswith("__"):
                name = f.stem
                # Try to extract docstring as description
                desc = self._extract_docstring(f)
                self._skills[name] = {
                    "name": name,
                    "path": str(f),
                    "type": "python",
                    "command": f"python3 ~/aria/skills/{f.name}",
                    "description": desc or f"Python skill: {name}",
                }

    def _scan_skill_md_files(self):
        """Scan for SKILL.md files with YAML frontmatter."""
        # Scan in the skills directory and any subdirectories
        for skill_md in SKILLS_DIR.rglob("SKILL.md"):
            try:
                content = skill_md.read_text(errors="ignore")
                meta = self._parse_yaml_frontmatter(content)
                if meta:
                    name = meta.get("name", skill_md.parent.name)
                    self._skills[f"md:{name}"] = {
                        "name": name,
                        "path": str(skill_md),
                        "type": "skill_md",
                        "description": meta.get("description", ""),
                        "instructions": content,
                    }
            except Exception as e:
                log.warning(f"Failed to parse {skill_md}: {e}")

    def _load_static_registry(self):
        """Load the static SKILLS_REGISTRY.md content."""
        try:
            self._registry_content = REGISTRY_PATH.read_text()
        except FileNotFoundError:
            self._registry_content = ""

    @staticmethod
    def _extract_docstring(path: Path) -> str:
        """Extract the module docstring from a Python file."""
        try:
            text = path.read_text(errors="ignore")
            match = re.search(r'^"""(.*?)"""', text, re.DOTALL)
            if match:
                return match.group(1).strip().split("\n")[0]  # First line only
            match = re.search(r"^'''(.*?)'''", text, re.DOTALL)
            if match:
                return match.group(1).strip().split("\n")[0]
        except Exception:
            pass
        return ""

    @staticmethod
    def _parse_yaml_frontmatter(text: str) -> dict:
        """Parse simple YAML frontmatter from a SKILL.md file."""
        if not text.startswith("---"):
            return {}
        end = text.find("---", 3)
        if end == -1:
            return {}
        frontmatter = text[3:end].strip()
        result = {}
        for line in frontmatter.split("\n"):
            if ":" in line:
                key, _, value = line.partition(":")
                result[key.strip()] = value.strip()
        return result

    def get_skills_for_prompt(self) -> str:
        """
        Generate a formatted skills section for the system prompt.
        Combines the static registry with dynamically discovered skills.
        """
        parts = []

        # Static registry
        if self._registry_content:
            parts.append(self._registry_content)

        # Dynamic Python skills not in registry
        dynamic = []
        for skill in self._skills.values():
            if skill["type"] == "python":
                # Check if already mentioned in static registry
                if skill["name"] not in self._registry_content:
                    dynamic.append(f"- `{skill['command']}` — {skill['description']}")
        
        if dynamic:
            parts.append("\n## Auto-Discovered Skills\n" + "\n".join(dynamic))

        return "\n".join(parts)

    def get_skill(self, name: str) -> dict:
        """Get a specific skill by name."""
        return self._skills.get(name)

    def list_skills(self) -> List[str]:
        """List all skill names."""
        return list(self._skills.keys())
