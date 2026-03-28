"""
ARIA v6 — Casual Agent
Handles conversational responses without tool execution.
"""

from agents.base_agent import BaseAgent
from typing import Tuple


class CasualAgent(BaseAgent):
    """
    Agent for casual conversation, greetings, jokes,
    and questions that don't require tool execution.
    """

    def __init__(self):
        super().__init__(
            name="casual",
            role="casual conversation, greetings, general knowledge, and questions",
            agent_type="casual"
        )

    async def process(self, task: str, context: str = "") -> Tuple[str, bool]:
        """Casual responses — no tool execution needed."""
        self.status = "chatting"
        self.success = True
        self.last_answer = task
        self.status = "done"
        return task, True
