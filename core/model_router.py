"""
ARIA v7 — Multi-Model Router
Routes tasks to the optimal AI model based on task complexity and type.

Strategy:
- Simple chat/greetings → Nvidia NIM (fast, unlimited API)
- Code generation → Nvidia NIM Qwen Coder 32B (specialized)
- Deep reasoning → Nvidia NIM (or future local model)
- Vision tasks → Nvidia NIM vision model (when available)

The Nvidia API is unlimited usage with per-minute rate limits,
so we use it for everything but route to different MODEL names.
"""

import re
import logging
from typing import Tuple

log = logging.getLogger("ARIA.router")

# ─── Model Registry ──────────────────────────────────────
# All models available via Nvidia NIM or local inference
MODELS = {
    "default": {
        "name": "qwen/qwen2.5-coder-32b-instruct",
        "description": "General purpose + code — best all-rounder",
        "temperature": 0.4,
        "max_tokens": 2048,
    },
    "fast": {
        "name": "meta/llama-3.1-8b-instruct",   # ← 8B model: 5-10x faster than 32B
        "description": "Fast responses for chat, math, quick answers",
        "temperature": 0.5,
        "max_tokens": 512,   # Short answers for speed
    },
    "code": {
        "name": "qwen/qwen2.5-coder-32b-instruct",
        "description": "Specialized code generation",
        "temperature": 0.2,
        "max_tokens": 4096,
    },
    "reasoning": {
        "name": "qwen/qwen2.5-coder-32b-instruct",
        "description": "Deep analysis and reasoning",
        "temperature": 0.3,
        "max_tokens": 2048,
    },
    "creative": {
        "name": "qwen/qwen2.5-coder-32b-instruct",
        "description": "Creative writing, stories, jokes",
        "temperature": 0.8,
        "max_tokens": 2048,
    },
}

# ─── Task Classification Patterns ─────────────────────────
TASK_PATTERNS = {
    "code": [
        r"\b(write|create|build|make|code|script|program|debug|fix|implement|develop)\b.*\b(python|bash|javascript|go|rust|c\+\+|java|html|css|function|class|api|server|app)\b",
        r"\b(pip install|npm|cargo|git clone|make|cmake|compile)\b",
        r"```",
        r"\b(error|traceback|bug|crash|exception|stack trace)\b",
    ],
    "web": [
        r"\b(search|browse|find online|look up|google|web|website|url|http|download|scrape)\b",
        r"\b(news|weather|price|stock|latest|trending|review)\b",
        r"\b(movies4u|youtube|twitter|reddit|github)\b",
    ],
    "file": [
        r"\b(find file|locate|move|copy|rename|delete|organize|folder|directory|ls|tree)\b",
        r"\b(open|read|save|write to|create file|edit file)\b",
        r"~/|/home/|\.txt|\.py|\.pdf|\.jpg|\.mp4",
    ],
    "reasoning": [
        r"\b(analyze|explain|compare|why|how does|evaluate|assess|plan|strategy|research)\b",
        r"\b(pros and cons|trade-?offs|architecture|design|approach)\b",
        r"\b(deep research|investigate|study|report)\b",
    ],
    "creative": [
        r"\b(story|joke|poem|song|creative|imagine|write me a|tell me a)\b",
        r"\b(funny|humor|entertaining|fiction)\b",
    ],
    "fast": [
        r"^(hi|hello|hey|yo|sup|thanks|thank you|ok|okay|bye|good|great|nice|cool|yes|no|sure)[\s!?.]*$",
        r"^.{1,20}$",          # Very short messages
        r"\b(what time|date today|how are you|who are you|what is your name)\b",
        r"^\s*[\d\s\+\-\*\/\(\)\^\.]+\s*[=?]?\s*$",  # Pure math: 23*34, (5+3)*2
        r"\bwhat is\s+[\d\s\+\-\*\/\(\)]+\s*\??$",   # "what is 23*34?"
        r"\b(convert|calculate|how many|how much).{1,40}$",  # simple calculations
    ],
}


def classify_task(text: str) -> str:
    """
    Classify a user message into a task type.
    
    Returns one of: 'code', 'web', 'file', 'reasoning', 'creative', 'fast', 'default'
    """
    text_lower = text.lower().strip()
    
    scores = {}
    for category, patterns in TASK_PATTERNS.items():
        score = 0
        for pattern in patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            score += len(matches)
        if score > 0:
            scores[category] = score
    
    if not scores:
        return "default"
    
    # Return the highest-scoring category
    best = max(scores, key=scores.get)
    log.info(f"Task classification: '{text[:50]}...' → {best} (scores: {scores})")
    return best


def get_model_config(task_type: str) -> dict:
    """Get the model configuration for a task type."""
    return MODELS.get(task_type, MODELS["default"])


def route(text: str) -> Tuple[str, float, int]:
    """
    Route a message to the optimal model.
    
    Returns:
        Tuple of (model_name, temperature, max_tokens)
    """
    task_type = classify_task(text)
    config = get_model_config(task_type)
    
    log.info(f"Routed to model: {config['name']} ({task_type}) temp={config['temperature']}")
    return config["name"], config["temperature"], config["max_tokens"]


# ─── Future: Add custom models ────────────────────────────
def register_model(name: str, model_id: str, description: str, 
                   temperature: float = 0.4, max_tokens: int = 4096):
    """Register a new model in the router."""
    MODELS[name] = {
        "name": model_id,
        "description": description,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    log.info(f"Registered model: {name} → {model_id}")
