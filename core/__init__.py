"""
ARIA v6 Core — The Brain
Multi-agent orchestration, memory, planning, and tool execution.
"""

from core.agent_loop import AgentLoop
from core.memory import ConversationMemory
from core import tool_executor
from core.planner import TaskPlanner
from core.skill_loader import SkillLoader

__version__ = "6.0.0"
__all__ = ["AgentLoop", "ConversationMemory", "tool_executor", "TaskPlanner", "SkillLoader"]
