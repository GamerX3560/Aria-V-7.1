"""
ARIA v6 — Coder Agent
Specializes in writing, debugging, and executing code.
"""

from agents.base_agent import BaseAgent
from core.tool_executor import execute
from typing import Tuple


class CoderAgent(BaseAgent):
    """
    Specialized agent for code-related tasks:
    - Writing scripts in Python, Bash, Go, JS, etc.
    - Debugging errors
    - Installing packages
    - Running and testing code
    """

    def __init__(self):
        super().__init__(
            name="coder",
            role="writing code, debugging scripts, installing packages, and running programs",
            agent_type="coder"
        )

    async def process(self, task: str, context: str = "") -> Tuple[str, bool]:
        """Execute code-related tasks by running them through the tool executor."""
        self.status = "coding"
        try:
            result = execute(task)
            success = "ERROR" not in result
            self.success = success
            self.last_answer = result
            self.status = "done"
            return result, success
        except Exception as e:
            self.status = "error"
            self.success = False
            return f"Coder agent error: {e}", False
