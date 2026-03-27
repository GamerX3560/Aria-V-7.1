"""
ARIA v6 — Task Planner
Decomposes complex multi-step tasks into sub-agent plans.
Inspired by agenticSeek's PlannerAgent architecture.
"""

import json
import logging
from typing import List, Dict, Optional, Tuple

log = logging.getLogger("ARIA.planner")

# Available agent types that can be assigned tasks
AGENT_TYPES = ["coder", "browser", "file", "casual"]

PLANNER_INSTRUCTIONS = """
You are ARIA's Task Planner. When a task is complex (involves multiple steps, different tools, or requires planning), 
you must decompose it into a structured JSON plan.

OUTPUT FORMAT: Write your plan inside a ```json block:

```json
{
  "plan": [
    {"id": "1", "agent": "browser", "task": "Search the web for X", "need": []},
    {"id": "2", "agent": "coder", "task": "Write a script using the data from step 1", "need": ["1"]},
    {"id": "3", "agent": "file", "task": "Save the output to ~/results.txt", "need": ["2"]}
  ]
}
```

RULES:
- Each task has: id (string), agent (one of: coder, browser, file, casual), task (description), need (list of dependency IDs)
- "need" links to previous task IDs whose output this task requires
- Available agents: coder (code/scripts), browser (web), file (filesystem), casual (chat/analysis)
- Keep plans concise — 2-5 steps. Don't over-decompose simple tasks.
- If the task is simple enough for one agent, just do it directly without a plan.
"""


class TaskPlanner:
    """
    Manages multi-step task planning and execution.
    
    For complex tasks, generates a JSON plan, then delegates each step
    to the appropriate sub-agent, passing results between them.
    """

    def __init__(self):
        self.current_plan: List[dict] = []
        self.results: Dict[str, str] = {}
        self.is_planning = False

    @staticmethod
    def get_planner_prompt() -> str:
        """Get the planner instructions to inject into the system prompt."""
        return PLANNER_INSTRUCTIONS

    def parse_plan(self, llm_output: str) -> List[dict]:
        """
        Parse a JSON plan from the LLM's output.
        
        Args:
            llm_output: Raw text from the LLM containing a ```json block.
            
        Returns:
            List of task dicts, or empty list if parsing fails.
        """
        import re
        # Extract JSON from code block
        match = re.search(r'```json\s*\n(.*?)```', llm_output, re.DOTALL)
        if not match:
            return []

        try:
            data = json.loads(match.group(1).strip())
        except json.JSONDecodeError as e:
            log.warning(f"Failed to parse plan JSON: {e}")
            return []

        if "plan" not in data:
            return []

        tasks = []
        for task in data["plan"]:
            # Validate required fields
            if not all(k in task for k in ("id", "agent", "task")):
                log.warning(f"Skipping malformed task: {task}")
                continue
            # Validate agent type
            if task["agent"].lower() not in AGENT_TYPES:
                log.warning(f"Unknown agent type: {task['agent']}")
                continue
            tasks.append({
                "id": str(task["id"]),
                "agent": task["agent"].lower(),
                "task": task["task"],
                "need": task.get("need", []),
            })

        self.current_plan = tasks
        log.info(f"Parsed plan with {len(tasks)} tasks")
        return tasks

    def get_task_context(self, task: dict) -> str:
        """
        Build the context string for a task, including results from dependencies.
        """
        parts = [f"YOUR TASK: {task['task']}"]
        
        if task["need"]:
            parts.append("\nINFO FROM PREVIOUS STEPS:")
            for dep_id in task["need"]:
                if dep_id in self.results:
                    parts.append(f"  [Step {dep_id} result]: {self.results[dep_id][:1500]}")

        return "\n".join(parts)

    def record_result(self, task_id: str, result: str, success: bool):
        """Store the result of a completed task."""
        status = "SUCCESS" if success else "FAILED"
        self.results[task_id] = f"[{status}] {result}"
        log.info(f"Task {task_id}: {status}")

    def format_plan_display(self) -> str:
        """Format the current plan for display to the user."""
        if not self.current_plan:
            return "No active plan."
        
        lines = ["📋 **Task Plan:**"]
        for task in self.current_plan:
            status = "✅" if task["id"] in self.results else "⏳"
            agent_icon = {"coder": "💻", "browser": "🌐", "file": "📁", "casual": "💬"}.get(task["agent"], "🔧")
            lines.append(f"  {status} Step {task['id']}: {agent_icon} [{task['agent']}] {task['task']}")
        
        return "\n".join(lines)

    def is_complete(self) -> bool:
        """Check if all tasks in the plan have results."""
        if not self.current_plan:
            return True
        return all(t["id"] in self.results for t in self.current_plan)

    def get_next_task(self) -> Optional[dict]:
        """Get the next unfinished task whose dependencies are all met."""
        for task in self.current_plan:
            if task["id"] in self.results:
                continue  # Already done
            # Check if all dependencies are completed
            if all(dep in self.results for dep in task["need"]):
                return task
        return None

    def reset(self):
        """Clear the current plan and results."""
        self.current_plan.clear()
        self.results.clear()
        self.is_planning = False
