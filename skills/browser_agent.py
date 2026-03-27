#!/usr/bin/env python3
import asyncio
import sys
import os
from langchain_openai import ChatOpenAI
from browser_use import Agent

# Nvidia NIM config
BASE_URL = "https://integrate.api.nvidia.com/v1"
API_KEY = "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"
# We use the hyper-fast Qwen 32B model, but LLaMA 70B is also a great choice for browser DOM parsing
MODEL_NAME = "meta/llama-3.1-70b-instruct"

# Monkey-patch ChatOpenAI class to satisfy browser-use's strict LLM checks
class PatchedChatOpenAI(ChatOpenAI):
    @property
    def provider(self):
        return "openai"
    @property
    def model(self):
        return getattr(self, "model_name", "")
    def __setattr__(self, name, value):
        # Brute-force bypass Pydantic V2 locked models
        object.__setattr__(self, name, value)

async def main(task_description: str):
    # Setup OpenAI-compatible LLM
    llm = PatchedChatOpenAI(
        base_url=BASE_URL,
        api_key=API_KEY,
        model=MODEL_NAME
    )
    
    # Provide strict rules to prevent guessing in complex DOMs
    strict_task = (
        "CRITICAL RULE: If you encounter a CAPTCHA, a complex menu you cannot navigate, "
        "or if you are unsure how to proceed, DO NOT GUESS and DO NOT randomly click. "
        "You must output exactly `[ASK] I am stuck on the browser: ` followed by what you see, and then stop.\n\n"
        f"USER TASK: {task_description}"
    )
    
    # Initialize the browser agent
    agent = Agent(
        task=strict_task,
        llm=llm
    )
    
    print(f"Starting browser agent for task: '{task_description}'")
    print("Agent is now in control of the browser. Please wait...")
    try:
        # Run agent
        result = await agent.run()
        print("\n=== FINAL RESULT ===")
        print(result)
    except Exception as e:
        print(f"\nERROR: Browser agent failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 browser_agent.py <task description>")
        sys.exit(1)
        
    task_desc = " ".join(sys.argv[1:])
    asyncio.run(main(task_desc))
