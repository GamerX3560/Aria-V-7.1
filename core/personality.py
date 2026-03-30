"""
ARIA v7 — Personality Engine
Emotional awareness, humor, and adaptive conversation style.
Makes ARIA feel alive, like a real companion.
"""

import re
import json
import logging
from pathlib import Path
from typing import Optional

log = logging.getLogger("ARIA.personality")

ARIA_DIR = Path.home() / "aria"
SOUL_PATH = ARIA_DIR / "SOUL.md"
PERSONALITY_STATE_PATH = ARIA_DIR / "memory" / "personality_state.json"

# ─── Mood Detection Patterns ─────────────────────────────
MOOD_PATTERNS = {
    "frustrated": [
        r"(why (won'?t|doesn'?t|isn'?t|can'?t)|not working|broken|stuck|annoyed|ugh|wtf|damn|still not|again\?!)",
        r"(i (told|said|already|asked) you|fix (this|it)|wrong|bad|terrible|useless)",
    ],
    "excited": [
        r"(awesome|amazing|perfect|incredible|wow|love it|great job|nice|cool|fire|💯|🔥|❤️|yesss)",
        r"(that'?s (exactly|perfect|brilliant)|well done|nailed it)",
    ],
    "curious": [
        r"(how (does|do|can|would)|what (is|are|if)|why (does|do|is)|explain|tell me|teach me)",
        r"(could you|can you|is it possible|i wonder|curious|interested)",
    ],
    "urgent": [
        r"(asap|urgent|hurry|quick|fast|immediately|right now|emergency|deadline|need this now)",
        r"(quickly|rapidly|time-?sensitive)",
    ],
    "casual": [
        r"^(hey|hi|hello|yo|sup|heyy|hii|wassup|what'?s up)[\s!?.]*$",
        r"(lol|haha|lmao|rofl|😂|🤣|just (asking|wondering|chatting))",
    ],
    "grateful": [
        r"(thanks|thank you|thx|ty|appreciate|grateful|helped|saved me)",
    ],
}

# ─── Response Style Adjustments ───────────────────────────
STYLE_ADJUSTMENTS = {
    "frustrated": {
        "tone": "empathetic, calm, solution-focused",
        "instruction": "The user seems frustrated. Be extra patient. Acknowledge their frustration briefly, then provide a clear, direct solution. Avoid unnecessary verbosity.",
        "emoji_mood": "🤝",
    },
    "excited": {
        "tone": "enthusiastic, matching energy",
        "instruction": "The user is excited! Match their energy. Use exclamation marks, celebrate the win, and keep the positive momentum going.",
        "emoji_mood": "🎉",
    },
    "curious": {
        "tone": "educational, thorough, encouraging",
        "instruction": "The user is curious and wants to learn. Give detailed explanations with examples. Be encouraging of their curiosity.",
        "emoji_mood": "🧠",
    },
    "urgent": {
        "tone": "efficient, no fluff, action-first",
        "instruction": "The user needs something done NOW. Skip pleasantries. Give the shortest possible solution. Execute immediately.",
        "emoji_mood": "⚡",
    },
    "casual": {
        "tone": "friendly, relaxed, conversational",
        "instruction": "This is casual conversation. Be warm, use humor, feel free to add personality. You're a friend, not a tool.",
        "emoji_mood": "😎",
    },
    "grateful": {
        "tone": "warm, humble, appreciative",
        "instruction": "The user is thanking you. Accept gracefully, don't be overly modest. Maybe suggest next steps or offer further help.",
        "emoji_mood": "😊",
    },
    "neutral": {
        "tone": "balanced, professional, helpful",
        "instruction": "Standard interaction. Be helpful and clear.",
        "emoji_mood": "🤖",
    },
}


class PersonalityEngine:
    """
    Adaptive personality that detects user mood and adjusts ARIA's tone.
    
    Features:
    - User mood detection from message patterns
    - Dynamic tone adjustment per message
    - Relationship memory (humor history, inside jokes)
    - Personality traits from SOUL.md
    """

    def __init__(self):
        self._state = self._load_state()
        self._interaction_count = self._state.get("interaction_count", 0)
        self._humor_used = self._state.get("humor_used", [])

    def _load_state(self) -> dict:
        try:
            with open(PERSONALITY_STATE_PATH, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"interaction_count": 0, "humor_used": [], "mood_history": []}

    def _save_state(self):
        PERSONALITY_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(PERSONALITY_STATE_PATH, 'w') as f:
            json.dump(self._state, f, indent=2)

    def detect_mood(self, text: str) -> str:
        """Detect the user's mood from their message."""
        text_lower = text.lower()
        scores = {}
        
        for mood, patterns in MOOD_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    score += 1
            if score > 0:
                scores[mood] = score
        
        if not scores:
            return "neutral"
        
        detected = max(scores, key=scores.get)
        
        # Track mood history
        self._state.setdefault("mood_history", []).append({
            "mood": detected,
            "text_preview": text[:50]
        })
        # Keep last 50 entries
        self._state["mood_history"] = self._state["mood_history"][-50:]
        self._save_state()
        
        return detected

    def get_style_prompt(self, mood: str) -> str:
        """Get the personality adjustment for the current mood."""
        style = STYLE_ADJUSTMENTS.get(mood, STYLE_ADJUSTMENTS["neutral"])
        
        self._interaction_count += 1
        self._state["interaction_count"] = self._interaction_count
        self._save_state()
        
        # Build personality section
        parts = [
            f"--- 🎭 PERSONALITY (mood: {mood} {style['emoji_mood']}) ---",
            f"TONE: {style['tone']}",
            f"BEHAVIOR: {style['instruction']}",
        ]
        
        # Add relationship depth hints
        if self._interaction_count > 100:
            parts.append("NOTE: You've interacted with this user 100+ times. You know them well. Be natural, use their name (Mangesh), reference past interactions when relevant.")
        elif self._interaction_count > 20:
            parts.append("NOTE: You're building a relationship with this user. Be increasingly personable.")
        
        parts.append("--- END PERSONALITY ---")
        return "\n".join(parts)

    def get_greeting(self, user_name: str = "Mangesh") -> str:
        """Generate a contextual greeting based on time and mood history."""
        import datetime
        hour = datetime.datetime.now().hour
        
        if hour < 6:
            time_greeting = f"Still up, {user_name}? 🌙"
        elif hour < 12:
            time_greeting = f"Good morning, {user_name}! ☀️"
        elif hour < 17:
            time_greeting = f"Good afternoon, {user_name}! 🌤️"
        elif hour < 21:
            time_greeting = f"Good evening, {user_name}! 🌆"
        else:
            time_greeting = f"Hey {user_name}! 🌙"
        
        return time_greeting
