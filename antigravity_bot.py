#!/usr/bin/env python3
import asyncio
import os
import json
import logging
import yaml
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("AntigravityBot")

# --- Config ---
from pathlib import Path
ARIA_DIR = Path.home() / "aria"

def get_vault_secret(key: str) -> str:
    vault_path = ARIA_DIR / "vault.json"
    if vault_path.exists():
        with open(vault_path) as f:
            data = json.load(f)
            return data.get(key, "")
    return ""

TELEGRAM_TOKEN = get_vault_secret("TELEGRAM_BOT_TOKEN")
TELEGRAM_USER_ID = get_vault_secret("TELEGRAM_USER_ID")

CDP_URL = "http://localhost:9222"

async def get_ide_page(browser):
    """Finds the main Antigravity IDE page among all contexts/pages."""
    for context in browser.contexts:
        for page in context.pages:
            title = await page.title()
            if "Antigravity" in title or "Visual Studio Code" in title:
                return page
    
    # Check background pages if any
    for context in browser.contexts:
        for page in context.background_pages:
            title = await page.title()
            if "Antigravity" in title or "Visual Studio Code" in title:
                return page
    
    # Fallback to the first available page
    if browser.contexts and browser.contexts[0].pages:
        return browser.contexts[0].pages[0]
    return None

async def interact_with_ide(prompt: str) -> str:
    """Uses Playwright to interact with the Antigravity IDE."""
    log.info(f"Connecting to Antigravity on CDP {CDP_URL}...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(CDP_URL)
            page = await get_ide_page(browser)
            
            if not page:
                await browser.close()
                return "Error: Could not find the Antigravity IDE window. Make sure it's running with --remote-debugging-port=9222."
            
            # Here we use basic DOM manipulation assuming the IDE has a chat box.
            # Example CSS selectors (these need to be adjusted based on the actual UI)
            # The chat input box
            input_selector = "textarea[placeholder*='Message']"
            # The send button or we can press Enter
            
            # Wait for the input box and type the message
            await page.wait_for_selector(input_selector, timeout=5000)
            await page.fill(input_selector, prompt)
            
            # Press Enter
            await page.keyboard.press("Enter")
            
            # Wait for the response to stream (e.g. wait for a 'generating' indicator to vanish, or wait a fixed time)
            # Since generating might take a while, we wait a few seconds and grab the last message
            log.info("Prompt sent. Waiting for response generation...")
            await asyncio.sleep(15) # Adjust this wait based on typical response times
            
            # Example selector for the chat messages
            response_selector = ".chat-message-content"
            messages = await page.query_selector_all(response_selector)
            
            if messages:
                # Get the last message's text
                last_msg_element = messages[-1]
                response_text = await last_msg_element.inner_text()
            else:
                response_text = "Message sent, but I could not scrape the response from the UI."
            
            await browser.close()
            return response_text
    except Exception as e:
        log.error(f"Playwright interaction failed: {e}")
        return f"Playwright interaction failed: {str(e)}\n\n(Make sure the IDE is launched with `--remote-debugging-port=9222`)"

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != str(TELEGRAM_USER_ID):
        return
    await update.message.reply_text("Antigravity Desktop Bot is online.\n\nSend me a message and I'll type it into your running Antigravity IDE via Playwright!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != str(TELEGRAM_USER_ID):
        return
    
    user_msg = update.message.text
    log.info(f"Received from Telegram: {user_msg}")
    
    # Send a typing indicator
    await update.message.reply_text("Typing into the IDE...")
    
    # Interact with IDE
    response_text = await interact_with_ide(user_msg)
    
    # Send the scraped response back
    await update.message.reply_text(response_text)

def main():
    if not TELEGRAM_TOKEN:
        log.error("TELEGRAM_BOT_TOKEN not found in vault.json")
        return
        
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    log.info("Starting Antigravity Desktop Bot...")
    app.run_polling()

if __name__ == "__main__":
    main()
