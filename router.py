#!/usr/bin/env python3
"""
ARIA v7 — Autonomous Agent System
Telegram bot entry point with full Jarvis-level capabilities.

Integrates ALL 12 core modules:
1. Agent Loop (unlimited execution)
2. Multi-Model Router (task → optimal model config)
3. Context Engine (live time/weather/system/apps)
4. Proactive Monitor (autonomous alerts)
5. Memory (auto-compressing + session persistence)
6. RAG Memory (vector DB, never forgets)
7. Task Planner (JSON decomposition)
8. Tool Executor (security sandbox)
9. Skill Loader (dynamic discovery)
10. Personality Engine (mood detection, adaptive tone)
11. Voice TTS (male/female/aria voices)
12. Vision Engine (screen awareness)
13. Device Mesh (PC + Android + SSH)
14. Skill Evolver (auto-discover new tools)
"""

import os
import sys
import re
import json
import logging
import asyncio
from pathlib import Path

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
from openai import AsyncOpenAI

# ─── Core Imports ─────────────────────────────────────────
from core.agent_loop import AgentLoop
from core.memory import ConversationMemory
from core.skill_loader import SkillLoader
from core.planner import TaskPlanner
from core.model_router import route as route_model, classify_task
from core.context_engine import ContextEngine
from core.proactive_monitor import ProactiveMonitor
from core.personality import PersonalityEngine
from core.rag_memory import RAGMemory
from core.voice_tts import VoiceTTSEngine
from core.vision_engine import VisionEngine
from core.device_mesh import DeviceMesh
from core.skill_evolver import SkillEvolver
from core.encrypted_storage import EncryptedStorage

# ─── Logging ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("ARIA")

# ─── Configuration ────────────────────────────────────────
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER = os.environ.get("TELEGRAM_USER_ID")

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "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")
BASE_URL = os.environ.get("ARIA_LLM_BASE_URL", "https://integrate.api.nvidia.com/v1")
MODEL_NAME = os.environ.get("ARIA_MODEL", "qwen/qwen2.5-coder-32b-instruct")

ARIA_DIR = Path.home() / "aria"
IDENTITY_PATH = ARIA_DIR / "identity.yaml"
VAULT_PATH = ARIA_DIR / "vault.json"

# ─── Global Instances ────────────────────────────────────
llm_client = AsyncOpenAI(api_key=NVIDIA_API_KEY, base_url=BASE_URL)
skill_loader = SkillLoader()
context_engine = ContextEngine()
personality_engine = PersonalityEngine()
rag_memory = RAGMemory()
voice_tts = VoiceTTSEngine()
vision_engine = VisionEngine()
device_mesh = DeviceMesh()
skill_evolver = SkillEvolver()
encrypted_store = EncryptedStorage()
proactive_monitor = ProactiveMonitor()

def load_identity_raw() -> str:
    try:
        return IDENTITY_PATH.read_text()
    except Exception:
        return ""


# ─── System Prompt ────────────────────────────────────────
def build_system_prompt(user_message: str = "") -> str:
    """Build the complete system prompt with ALL modules contributing."""
    identity = load_identity_raw()
    skills = skill_loader.get_skills_for_prompt()
    planner_instructions = TaskPlanner.get_planner_prompt()
    context = context_engine.get_full_context()
    
    # Personality mood detection
    mood = personality_engine.detect_mood(user_message) if user_message else "neutral"
    personality_section = personality_engine.get_style_prompt(mood)
    
    # RAG recall for relevant past memories
    rag_context = rag_memory.get_relevant_context(user_message) if user_message else ""
    
    # Vision — current screen state (text-based, efficient)
    screen_context = vision_engine.get_screen_text_context()

    return f"""You are ARIA v7, a hyper-intelligent autonomous AI Agent running on Arch Linux with Hyprland.
You are the most advanced personal AI assistant — smarter than Jarvis, with unlimited execution and multi-sensory awareness.

YOUR ARCHITECTURE:
You control the user's system by issuing commands in ```bash blocks.
When you output a bash block, the system automatically executes it and feeds the terminal output back to you as "OBSERVATION:".
You can run as many commands as needed — there is NO iteration limit.
When finished, speak normally WITHOUT a bash block.

MULTI-MODEL BRAIN:
You automatically get the optimal model config for each task type:
- Simple chat → fast (lower tokens)
- Code → deterministic (low temperature)
- Creative → high creativity (high temperature)
- Reasoning → thorough (medium temperature)

AGENT CAPABILITIES:
- Execute code in any language (Python, Bash, Go, JS, C, etc.)
- Browse the web stealthily (Scrapling anti-bot bypass)
- Search, read, and manipulate any file
- Install packages, configure services, manage the OS
- Decompose complex tasks into sub-agent plans
- See the screen (text-based vision + OCR on demand)
- Speak responses aloud (with male/female voice switching)
- Recall ANY past conversation via semantic memory search
- Execute commands on Android phone via ADB root shell
- Execute commands on remote machines via SSH
- Auto-discover and install new skills autonomously
- Monitor system health and send proactive alerts

VOICE COMMANDS:
- To speak aloud: respond normally, the voice engine handles TTS
- User can switch voice: "switch to male voice", "switch to female voice"
- To read screen: "what's on my screen?" triggers OCR

DEVICE MESH:
- Local PC: direct execution
- Android: `adb shell su -c "command"` (rooted devices)
- Remote: SSH to other ARIA instances

RULES FOR ACTIONS:
- GUI apps must use & (e.g. firefox &). Blocking commands should NOT.
- After opening an app, verify with `pgrep -il <name>`.
- PACKAGE MANAGER: Always use `--noconfirm` with yay or pacman.
- ROOT: Use `echo "GamerX" | sudo -S <command>` for sudo.
- TIMEOUTS: If timed out, try a different approach. Do NOT repeat.
- UNCERTAINTY: Output `[ASK]` followed by your question. Do NOT guess.
- COMPLETION: Respond conversationally WITHOUT ```bash blocks when done.

{planner_instructions}

{context}

{personality_section}

{rag_context}

{screen_context}

SYSTEM: Ryzen 5 3400G | RX 6600 8GB | 16GB RAM | Arch Linux + Hyprland

--- USER IDENTITY & DECISION RULES ---
{identity}
--------------------------------------

--- AVAILABLE TOOLS & SKILLS ---
{skills}
— Evolved skills: {len(skill_evolver.list_evolved_skills())} auto-generated tools in ~/aria/skills/evolved/
— Device Mesh: {len(device_mesh._devices)} connected devices
--------------------------------
"""


# ─── Per-User Agent State ─────────────────────────────────
_agent_loops: dict = {}

def get_agent_loop(user_id: str, user_message: str = "") -> AgentLoop:
    """Get or create the agent loop for a user."""
    if user_id not in _agent_loops:
        memory = ConversationMemory(
            system_prompt=build_system_prompt(user_message),
            max_messages=50,
            max_message_len=3000
        )
        _agent_loops[user_id] = AgentLoop(llm_client, MODEL_NAME, memory)
    return _agent_loops[user_id]


# ─── Message Handler ─────────────────────────────────────
async def handle_message(update: Update, context):
    """Main message handler — full Jarvis pipeline."""
    if not update.message or not update.message.text:
        return
    if AUTHORIZED_USER and str(update.effective_user.id) != str(AUTHORIZED_USER):
        return

    text = update.message.text.strip()
    if not text:
        return

    user_id = str(update.effective_user.id)

    # ─── Voice switching commands ──────────────────────
    text_lower = text.lower()
    if "switch to male voice" in text_lower:
        voice_tts.set_voice("male")
        await update.message.reply_text("🎙️ Voice switched to male.")
        return
    elif "switch to female voice" in text_lower:
        voice_tts.set_voice("female")
        await update.message.reply_text("🎙️ Voice switched to female.")
        return
    elif "switch to aria voice" in text_lower:
        voice_tts.set_voice("aria")
        await update.message.reply_text("🎙️ Voice switched to ARIA default.")
        return

    # ─── Cancel command ────────────────────────────────
    if text_lower in ('stop', 'cancel', 'halt'):
        agent = get_agent_loop(user_id)
        if agent.is_running:
            agent.request_cancel()
            await update.message.reply_text("🛑 Cancel signal sent.")
        else:
            await update.message.reply_text("No active task to cancel.")
        return

    log.info(f'[MSG] "{text[:80]}"')

    # ─── Route to optimal model ────────────────────────
    model_name, temperature, max_tokens = route_model(text)

    # ─── Get agent loop ────────────────────────────────
    agent = get_agent_loop(user_id, text)
    
    # Update system prompt with live context + personality
    agent.memory.update_system_prompt(build_system_prompt(text))
    agent.memory.push("user", text)

    # Store in RAG memory (never forget)
    rag_memory.store_conversation("user", text)

    # ─── Status message ────────────────────────────────
    greeting = personality_engine.get_greeting()
    status_msg = await update.message.reply_text(f"🧠 {greeting} Processing...")
    last_status_text = ""

    async def status_callback(msg):
        nonlocal last_status_text
        if msg != last_status_text:
            try:
                await status_msg.edit_text(msg)
                last_status_text = msg
            except Exception:
                pass

    async def action_callback(msg):
        nonlocal last_status_text
        try:
            short = msg[:4000]
            if short != last_status_text:
                await status_msg.edit_text(short, parse_mode="Markdown")
                last_status_text = short
        except Exception:
            pass

    try:
        # Override model config in the agent loop
        agent.model_name = model_name
        
        result = await agent.run(
            status_callback=status_callback,
            action_callback=action_callback,
        )
        
        # Store assistant response in RAG memory
        if result:
            rag_memory.store_conversation("assistant", result)

        # Send the final result
        if result:
            chunks = [result[i:i+4000] for i in range(0, len(result), 4000)]
            for i, chunk in enumerate(chunks):
                if i == 0:
                    try:
                        await status_msg.edit_text(chunk)
                    except Exception:
                        await update.message.reply_text(chunk)
                else:
                    await update.message.reply_text(chunk)
            
            # Speak the response if it's short enough
            if len(result) < 500:
                voice_tts.speak_async(result)
        else:
            try:
                await status_msg.edit_text("Task completed ✓")
            except Exception:
                pass

    except Exception as e:
        log.error(f"Handler error: {e}", exc_info=True)
        try:
            await status_msg.edit_text(f"❌ Error: {str(e)[:500]}")
        except Exception:
            await update.message.reply_text(f"❌ Error: {str(e)[:500]}")


# ─── Bot Commands ─────────────────────────────────────────
async def cmd_status(update: Update, context):
    if AUTHORIZED_USER and str(update.effective_user.id) != str(AUTHORIZED_USER):
        return
    user_id = str(update.effective_user.id)
    agent = get_agent_loop(user_id)
    rag_stats = rag_memory.get_stats()
    sys_ctx = context_engine.get_system_context()
    
    await update.message.reply_text(
        f"🤖 ARIA v7 — Autonomous Agent\n\n"
        f"Model: {MODEL_NAME}\n"
        f"Context: {len(agent.memory.messages)} msgs ({agent.memory.context_length} chars)\n"
        f"Skills: {len(skill_loader.list_skills())} loaded\n"
        f"Evolved: {len(skill_evolver.list_evolved_skills())} auto-skills\n"
        f"RAG: {rag_stats['total_entries']} memories ({rag_stats['backend']})\n"
        f"Voice: {voice_tts.current_voice} ({voice_tts._backend})\n"
        f"Devices: {len(device_mesh._devices)} in mesh\n"
        f"Monitor: {'🟢' if proactive_monitor._running else '⚪'}\n"
        f"Loop: {'🟢 Running' if agent.is_running else '⚪ Idle'}\n\n"
        f"{sys_ctx}"
    )

async def cmd_reset(update: Update, context):
    if AUTHORIZED_USER and str(update.effective_user.id) != str(AUTHORIZED_USER):
        return
    user_id = str(update.effective_user.id)
    agent = get_agent_loop(user_id)
    agent.memory.clear()
    await update.message.reply_text("Context cleared ✓")

async def cmd_memory(update: Update, context):
    if AUTHORIZED_USER and str(update.effective_user.id) != str(AUTHORIZED_USER):
        return
    user_id = str(update.effective_user.id)
    agent = get_agent_loop(user_id)
    facts = agent.memory.get_facts_summary()
    rag_stats = rag_memory.get_stats()
    await update.message.reply_text(
        f"📋 Short-term Memory:\n{facts}\n\n"
        f"🧠 Long-term RAG Memory:\n"
        f"  Backend: {rag_stats['backend']}\n"
        f"  Entries: {rag_stats['total_entries']}"
    )

async def cmd_skills(update: Update, context):
    if AUTHORIZED_USER and str(update.effective_user.id) != str(AUTHORIZED_USER):
        return
    skills = skill_loader.list_skills()
    evolved = skill_evolver.list_evolved_skills()
    lines = [f"⚡ {len(skills)} Core Skills + {len(evolved)} Evolved Skills:"]
    for s in skills[:25]:
        lines.append(f"  • {s}")
    if len(skills) > 25:
        lines.append(f"  ... and {len(skills) - 25} more")
    if evolved:
        lines.append(f"\n🧬 Evolved Skills:")
        for e in evolved[:10]:
            lines.append(f"  • {e['name']} ({e.get('category', 'utility')})")
    await update.message.reply_text("\n".join(lines))

async def cmd_save(update: Update, context):
    if AUTHORIZED_USER and str(update.effective_user.id) != str(AUTHORIZED_USER):
        return
    user_id = str(update.effective_user.id)
    agent = get_agent_loop(user_id)
    agent.memory.save_session()
    await update.message.reply_text("💾 Session saved ✓")

async def cmd_reload(update: Update, context):
    if AUTHORIZED_USER and str(update.effective_user.id) != str(AUTHORIZED_USER):
        return
    skill_loader.reload()
    await update.message.reply_text(f"🔄 Reloaded {len(skill_loader.list_skills())} skills ✓")

async def cmd_devices(update: Update, context):
    if AUTHORIZED_USER and str(update.effective_user.id) != str(AUTHORIZED_USER):
        return
    await update.message.reply_text(device_mesh.list_devices())

async def cmd_voice(update: Update, context):
    if AUTHORIZED_USER and str(update.effective_user.id) != str(AUTHORIZED_USER):
        return
    voices = voice_tts.get_available_voices()
    lines = [f"🎙️ Voice Engine (current: {voice_tts.current_voice})"]
    for v in voices:
        marker = " ←" if v["name"] == voice_tts.current_voice else ""
        lines.append(f"  • {v['name']}: {v['description']}{marker}")
    lines.append(f"\nBackend: {voice_tts._backend}")
    lines.append("Switch: 'switch to male/female/aria voice'")
    await update.message.reply_text("\n".join(lines))

async def cmd_vision(update: Update, context):
    if AUTHORIZED_USER and str(update.effective_user.id) != str(AUTHORIZED_USER):
        return
    text_ctx = vision_engine.get_screen_text_context()
    await update.message.reply_text(f"👁️ Screen Awareness:\n\n{text_ctx}")

async def cmd_test(update: Update, context):
    if AUTHORIZED_USER and str(update.effective_user.id) != str(AUTHORIZED_USER):
        return
    await update.message.reply_text("🧪 Running self-test... (this takes 10-20 seconds)")
    from core.tool_executor import execute
    result = execute("python3 ~/aria/test_aria.py", timeout=60)
    chunks = [result[i:i+4000] for i in range(0, len(result), 4000)]
    for chunk in chunks:
        await update.message.reply_text(chunk)


# ─── Main ─────────────────────────────────────────────────
def main():
    if not TELEGRAM_TOKEN:
        log.error("TELEGRAM_BOT_TOKEN not set. Export it and try again.")
        sys.exit(1)

    log.info("═══════════════════════════════════════")
    log.info("  ARIA v7 — Autonomous Agent System")
    log.info(f"  Model: {MODEL_NAME}")
    log.info(f"  API: {BASE_URL}")
    log.info(f"  Skills: {len(skill_loader.list_skills())} loaded")
    log.info(f"  RAG: {rag_memory.get_stats()['total_entries']} memories")
    log.info(f"  Voice: {voice_tts.current_voice} ({voice_tts._backend})")
    log.info(f"  Devices: {len(device_mesh._devices)} in mesh")
    log.info("═══════════════════════════════════════")

    # Post-init hook to start background services
    async def post_init(application):
        """Start background services after the bot is initialized."""
        # Wire bot instance into proactive monitor for sending alerts
        if AUTHORIZED_USER:
            proactive_monitor.bot = application.bot
            proactive_monitor.chat_id = AUTHORIZED_USER
            # Start monitoring as background task
            asyncio.create_task(proactive_monitor.start())
            log.info("Proactive Monitor started as background task")
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(post_init).build()
    
    # Commands
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("memory", cmd_memory))
    app.add_handler(CommandHandler("skills", cmd_skills))
    app.add_handler(CommandHandler("save", cmd_save))
    app.add_handler(CommandHandler("reload", cmd_reload))
    app.add_handler(CommandHandler("devices", cmd_devices))
    app.add_handler(CommandHandler("voice", cmd_voice))
    app.add_handler(CommandHandler("vision", cmd_vision))
    app.add_handler(CommandHandler("test", cmd_test))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    log.info("Telegram bot started. Polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
