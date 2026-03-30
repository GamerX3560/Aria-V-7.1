"""
ARIA v6 — File Agent
File search, organization, and filesystem operations.
"""

from agents.base_agent import BaseAgent
from core.tool_executor import execute
from typing import Tuple


class FileAgent(BaseAgent):
    """
    Specialized agent for filesystem tasks:
    - Finding files
    - Organizing directories
    - Reading/writing files
    - Managing backups
    """

    def __init__(self):
        super().__init__(
            name="file",
            role="finding files, organizing directories, reading/writing files, and managing the filesystem",
            agent_type="file"
        )

    async def process(self, task: str, context: str = "") -> Tuple[str, bool]:
        """Execute filesystem tasks."""
        self.status = "file_ops"
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
            return f"File agent error: {e}", False
