"""
ARIA v6 — Base Agent
Abstract base class for all specialized sub-agents.
Inspired by agenticSeek's Agent architecture.
"""

import logging
from abc import abstractmethod
from typing import Tuple, Optional

log = logging.getLogger("ARIA.agent")


class BaseAgent:
    """
    Abstract base class for ARIA sub-agents.
    
    Each agent has:
    - A name and role description
    - A specialized system prompt
    - Tool execution capabilities
    - Success/failure tracking
    """

    def __init__(self, name: str, role: str, agent_type: str):
        self.name = name
        self.role = role
        self.agent_type = agent_type
        self.success = True
        self.last_answer = ""
        self.status = "idle"

    @abstractmethod
    async def process(self, task: str, context: str = "") -> Tuple[str, bool]:
        """
        Process a task and return (result, success).
        
        Args:
            task: The task description.
            context: Optional context from previous agent results.
            
        Returns:
            Tuple of (result_text, was_successful)
        """
        pass

    def get_system_prompt_section(self) -> str:
        """Get this agent's contribution to the system prompt."""
        return f"[{self.agent_type.upper()} AGENT: {self.name}] Role: {self.role}"

    def __repr__(self):
        return f"<{self.agent_type}Agent:{self.name}>"
