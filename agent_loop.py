"""
ARIA v6 — Agent Loop
The main autonomous execution loop. Unlimited iterations with
self-healing, stuck detection, and duplicate command prevention.
"""

import re
import asyncio
import logging
import time
from typing import Optional

from core.tool_executor import execute, extract_code_blocks
from core.memory import ConversationMemory
from core.planner import TaskPlanner

log = logging.getLogger("ARIA.loop")

# Safety limits — not iteration caps, but sanity guards
MAX_CONSECUTIVE_FAILURES = 5
MAX_STUCK_ITERATIONS = 3
MAX_TOTAL_ITERATIONS = 50  # Ultimate safety net, much higher than the old 5


class AgentLoop:
    """
    The main autonomous execution loop for ARIA.
    
    Runs continuously until:
    1. The LLM responds without code blocks (task complete)
    2. The LLM uses the [ASK] tag (needs human input)
    3. User sends 'stop'/'cancel'
    4. Safety limits are hit (stuck detection, not hard iteration caps)
    """

    def __init__(self, llm_client, model_name: str, memory: ConversationMemory):
        self.llm = llm_client
        self.model_name = model_name
        self.temperature = 0.4
        self.max_tokens = 2048
        self.memory = memory
        self.planner = TaskPlanner()
        
        # State tracking for loop safety
        self._executed_commands: set = set()
        self._consecutive_failures: int = 0
        self._no_progress_count: int = 0
        self._cancel_requested: bool = False
        self._is_running: bool = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    def request_cancel(self):
        """Request the loop to stop gracefully."""
        self._cancel_requested = True

    async def ask_llm(self) -> str:
        """Call the LLM with the current conversation."""
        try:
            completion = await self.llm.chat.completions.create(
                model=self.model_name,
                messages=self.memory.messages,
                temperature=self.temperature,
                top_p=0.9,
                max_tokens=self.max_tokens
            )
            if completion.choices:
                return completion.choices[0].message.content.strip()
            return "I received an empty response."
        except Exception as e:
            log.error(f"LLM API Error: {e}")
            return f"ERROR: Failed to contact the AI brain. {e}"

    async def run(self, status_callback=None, action_callback=None) -> str:
        """
        Run the agentic loop until task completion.
        
        Args:
            status_callback: async func(text) to report status updates
            action_callback: async func(text) to report action steps
            
        Returns:
            Final response text from the agent.
        """
        self._is_running = True
        self._cancel_requested = False
        self._executed_commands.clear()
        self._consecutive_failures = 0
        self._no_progress_count = 0
        
        iteration = 0
        final_response = ""

        try:
            while iteration < MAX_TOTAL_ITERATIONS:
                iteration += 1

                # Check for cancellation
                if self._cancel_requested:
                    final_response = "🛑 Task interrupted by user."
                    break

                # Get LLM response — skip "Thinking" on step 1 to avoid
                # blink for simple chat (response → "Thinking..." → response)
                if status_callback and iteration > 1:
                    await status_callback(f"🧠 Thinking... (step {iteration})")

                reply = await self.ask_llm()
                self.memory.push("assistant", reply)

                # ─── Check for [ASK] tag — LLM needs human help ───
                if "[ASK]" in reply:
                    final_response = reply.replace("[ASK]", "❓").strip()
                    break

                # ─── Extract code blocks ────────────────────────
                code_blocks = extract_code_blocks(reply)

                # No code blocks = task is complete, agent is just talking
                if not code_blocks:
                    clean = re.sub(r'```(?:bash|shell|sh|python|python3|js|javascript|node)?\s*\n.*?```', 
                                   '', reply, flags=re.DOTALL).strip()
                    final_response = clean if clean else "Task completed ✓"
                    break

                # ─── Execute code blocks ────────────────────────
                outputs = []
                had_duplicate = False

                for code in code_blocks:
                    code_stripped = code.strip()

                    # Duplicate command detection — non-fatal: let the LLM try
                    # a different approach instead of stopping dead
                    if code_stripped in self._executed_commands:
                        note = (
                            f"OBSERVATION (duplicate skipped):\n"
                            f"You already ran this exact command. "
                            f"Please use a simpler/different command to get the same info "
                            f"(e.g. use `free -h`, `top -bn1`, `date` instead of complex scripts)."
                        )
                        self.memory.push("user", note)
                        outputs = [note]
                        had_duplicate = True
                        break

                    self._executed_commands.add(code_stripped)

                    # Report the action
                    if action_callback:
                        await action_callback(f"⚙️ Step {iteration}:\n```bash\n{code_stripped[:300]}\n```")

                    # Execute in thread to not block
                    output = await asyncio.to_thread(execute, code_stripped)
                    outputs.append(f"$ {code_stripped}\n{output}")

                    # Track failures
                    if "ERROR" in output:
                        self._consecutive_failures += 1
                    else:
                        self._consecutive_failures = 0

                if had_duplicate:
                    # Non-fatal: the note was pushed to memory above.
                    # Skip feeding results again and let the loop continue
                    # so the LLM can try a different command.
                    continue

                # ─── Feed results back to the LLM ──────────────
                combined = "OBSERVATION:\n" + "\n---\n".join(outputs)
                self.memory.push("user", combined)

                # ─── Stuck detection ────────────────────────────
                if self._consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                    final_response = (
                        f"⚠️ I've hit {MAX_CONSECUTIVE_FAILURES} consecutive errors. "
                        f"Something seems fundamentally wrong with my approach. "
                        f"Please review and tell me how to proceed."
                    )
                    break

            else:
                # Hit MAX_TOTAL_ITERATIONS
                final_response = (
                    f"⚠️ Reached the safety limit of {MAX_TOTAL_ITERATIONS} steps. "
                    f"The task might need human guidance to continue."
                )

        finally:
            self._is_running = False
            # Auto-save session after each task
            self.memory.save_session()

        return final_response
