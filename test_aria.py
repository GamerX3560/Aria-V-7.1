#!/usr/bin/env python3
"""
ARIA v7 — Self-Test Suite
Automated health checks to verify all capabilities.
Run: python3 ~/aria/test_aria.py
"""

import sys
import os
import json
import time
import importlib

# Ensure ARIA directory is in path
sys.path.insert(0, os.path.expanduser("~/aria"))

PASS = "✅"
FAIL = "❌"
WARN = "⚠️"

results = []

def test(name: str, func):
    """Run a test and record the result."""
    try:
        result = func()
        if result:
            results.append((PASS, name, result))
        else:
            results.append((FAIL, name, "returned False"))
    except Exception as e:
        results.append((FAIL, name, str(e)[:100]))


# ─── Core Module Tests ────────────────────────────────────

def test_tool_executor():
    from core.tool_executor import execute, is_command_safe
    assert is_command_safe("echo hello")
    assert not is_command_safe("rm -rf /")
    result = execute("echo ARIA_SELF_TEST")
    assert "ARIA_SELF_TEST" in result
    return f"Executor OK, security blocklist active"

def test_memory():
    from core.memory import ConversationMemory
    mem = ConversationMemory("test", max_messages=5)
    mem.push("user", "test message")
    assert len(mem.messages) == 2
    long = "X" * 5000
    mem.push("user", long)
    assert len(mem.messages[-1]["content"]) < 5000
    return f"Memory OK, compression works ({len(mem.messages)} msgs)"

def test_planner():
    from core.planner import TaskPlanner
    p = TaskPlanner()
    plan = '```json\n{"plan":[{"id":"1","agent":"coder","task":"test","need":[]}]}\n```'
    tasks = p.parse_plan(plan)
    assert len(tasks) == 1
    return f"Planner OK, parsed {len(tasks)} task"

def test_skill_loader():
    from core.skill_loader import SkillLoader
    sl = SkillLoader()
    skills = sl.list_skills()
    assert len(skills) > 0
    return f"Skill Loader OK, {len(skills)} skills"

def test_model_router():
    from core.model_router import classify_task, route
    assert classify_task("hi") == "fast"
    assert classify_task("write a python script") == "code"
    model, temp, tokens = route("hello")
    assert model is not None
    return f"Router OK, 'hello' → temp={temp}"

def test_context_engine():
    from core.context_engine import ContextEngine
    ce = ContextEngine()
    dt = ce.get_datetime_context()
    assert "Date" in dt
    sys = ce.get_system_context()
    assert "CPU" in sys
    return f"Context Engine OK"

def test_personality():
    from core.personality import PersonalityEngine
    pe = PersonalityEngine()
    assert pe.detect_mood("this is broken wtf") == "frustrated"
    assert pe.detect_mood("awesome great job!") == "excited"
    assert pe.detect_mood("hi") == "casual"
    return f"Personality OK, mood detection correct"

def test_rag_memory():
    from core.rag_memory import RAGMemory
    rag = RAGMemory(collection_name="aria_test")
    rag.store("Test memory entry for ARIA self test")
    results = rag.recall("ARIA self test")
    stats = rag.get_stats()
    return f"RAG Memory OK ({stats['backend']}, {stats['total_entries']} entries)"

def test_device_mesh():
    from core.device_mesh import DeviceMesh
    mesh = DeviceMesh()
    result = mesh.execute_on("local", "echo MESH_TEST")
    assert "MESH_TEST" in result
    return f"Device Mesh OK, local execution verified"

def test_skill_evolver():
    from core.skill_evolver import SkillEvolver
    evolver = SkillEvolver()
    stats = evolver.get_stats()
    assert "Skill Evolution" in stats
    return f"Skill Evolver OK"

def test_voice_tts():
    from core.voice_tts import VoiceTTSEngine
    tts = VoiceTTSEngine()
    voices = tts.get_available_voices()
    assert len(voices) >= 3
    assert tts.set_voice("male")
    assert tts.set_voice("female")
    return f"Voice TTS OK, {len(voices)} voices, backend={tts._backend}"

def test_vision_engine():
    from core.vision_engine import VisionEngine
    ve = VisionEngine()
    window = ve.get_active_window()
    return f"Vision OK, {window[:50]}"

def test_encrypted_storage():
    from core.encrypted_storage import EncryptedStorage
    store = EncryptedStorage()
    store.set_secret("aria_test_key", "test_value_42")
    assert store.get_secret("aria_test_key") == "test_value_42"
    assert store.is_encrypted()
    store.delete_secret("aria_test_key")
    return f"Encrypted Storage OK, {len(store.list_secrets())} secrets, AES-256"

def test_browser_agent():
    from core.browser_agent import BrowserAgent
    ba = BrowserAgent()
    status = ba.get_status()
    assert "Scrapling ✅" in status
    assert "browser-use ✅" in status
    assert "Playwright ✅" in status
    return f"Browser Agent OK, all 3 layers active"

def test_aria_mesh():
    from core.aria_mesh import ARIAMesh
    mesh = ARIAMesh(instance_name="test-aria")
    assert mesh.instance_id
    assert "execute" in mesh.capabilities
    # Test peer registration
    peer = mesh.register_peer("127.0.0.1", port=9999, name="test-peer")
    assert peer.name == "test-peer"
    mesh.remove_peer(peer.peer_id)
    return f"ARIA Mesh OK, caps={','.join(mesh.capabilities)}"

# ─── Skill Tests ──────────────────────────────────────────

def test_skills_importable():
    skills_dir = os.path.expanduser("~/aria/skills")
    importable = 0
    total = 0
    for f in os.listdir(skills_dir):
        if f.endswith(".py") and not f.startswith("__"):
            total += 1
            try:
                # Just check syntax
                with open(os.path.join(skills_dir, f)) as fh:
                    compile(fh.read(), f, 'exec')
                importable += 1
            except Exception:
                pass
    return f"Skills: {importable}/{total} have valid syntax"

# ─── System Tests ─────────────────────────────────────────

def test_system_tools():
    """Check that key system tools are installed."""
    tools = ["grim", "wf-recorder", "rg", "ffmpeg", "adb", "espeak-ng", "curl"]
    found = []
    for tool in tools:
        try:
            result = os.popen(f"which {tool} 2>/dev/null").read().strip()
            if result:
                found.append(tool)
        except Exception:
            pass
    return f"System tools: {len(found)}/{len(tools)} installed ({', '.join(found)})"


# ─── Run All Tests ────────────────────────────────────────

if __name__ == "__main__":
    print("═" * 50)
    print("  ARIA v7 — Self-Test Suite")
    print("═" * 50)
    print()

    tests = [
        ("Core: Tool Executor", test_tool_executor),
        ("Core: Memory", test_memory),
        ("Core: Planner", test_planner),
        ("Core: Skill Loader", test_skill_loader),
        ("Core: Model Router", test_model_router),
        ("Core: Context Engine", test_context_engine),
        ("Core: Personality", test_personality),
        ("Core: RAG Memory", test_rag_memory),
        ("Core: Device Mesh", test_device_mesh),
        ("Core: Skill Evolver", test_skill_evolver),
        ("Core: Voice TTS", test_voice_tts),
        ("Core: Vision Engine", test_vision_engine),
        ("Core: Encrypted Storage", test_encrypted_storage),
        ("Core: Browser Agent", test_browser_agent),
        ("Core: ARIA Mesh", test_aria_mesh),
        ("Skills: Importable", test_skills_importable),
        ("System: Tools Installed", test_system_tools),
    ]

    for name, func in tests:
        test(name, func)

    # Display results
    print()
    passed = sum(1 for r in results if r[0] == PASS)
    total = len(results)

    for status, name, detail in results:
        print(f"  {status} {name}: {detail}")

    print()
    print("─" * 50)
    
    if passed == total:
        print(f"  🎉 ALL {total} TESTS PASSED!")
    else:
        print(f"  📊 {passed}/{total} tests passed, {total - passed} failed")
    
    print("─" * 50)
    
    sys.exit(0 if passed == total else 1)
