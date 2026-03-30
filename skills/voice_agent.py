import asyncio
import os
from pathlib import Path
from loguru import logger as log

try:
    from playwright.async_api import async_playwright
except ImportError:
    log.error("Playwright not installed. Run: pip install playwright && playwright install")

class VoiceCallingAgent:
    """Agent for automating Web WhatsApp and Web Telegram to make voice calls."""
    
    def __init__(self):
        self.user_data_dir = Path.home() / ".config" / "aria" / "browser_data"
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
    
    async def _init_browser(self, p):
        """Initialize persistent browser context."""
        context = await p.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=False, # Must be visible for WebRTC permissions and QR code login
            permissions=['microphone', 'camera'],
            args=[
                '--use-fake-ui-for-media-stream', # Auto-grant A/V permissions
            ]
        )
        return context

    async def call_whatsapp(self, contact_name: str) -> str:
        """Automate WhatsApp Web to call a contact."""
        try:
            async with async_playwright() as p:
                context = await self._init_browser(p)
                page = await context.new_page()
                
                log.info(f"Opening WhatsApp Web to call {contact_name}...")
                await page.goto("https://web.whatsapp.com/")
                
                # Check for login requirement
                try:
                    await page.wait_for_selector('div[title="Search input textbox"]', timeout=15000)
                except Exception:
                    return "WhatsApp Web is not logged in. Please scan the QR code in the browser that just opened, then try again."

                # Search for contact
                await page.fill('div[title="Search input textbox"]', contact_name)
                await page.keyboard.press("Enter")
                
                # Wait for chat to load
                await asyncio.sleep(2)
                
                # Look for the Voice Call button (aria-label="Voice call")
                try:
                    call_btn = await page.wait_for_selector('[aria-label="Voice call"]', timeout=5000)
                    await call_btn.click()
                    return f"Successfully initiated voice call to {contact_name} on WhatsApp."
                except Exception:
                    return f"Could not find Voice Call button for {contact_name}. Are you sure they are a valid contact?"
                    
        except Exception as e:
            return f"WhatsApp automation failed: {e}"

    async def call_telegram(self, contact_name: str) -> str:
        """Automate Telegram Web to call a contact."""
        try:
            async with async_playwright() as p:
                context = await self._init_browser(p)
                page = await context.new_page()
                
                log.info(f"Opening Telegram Web to call {contact_name}...")
                await page.goto("https://web.telegram.org/a/")
                
                # Check for login
                try:
                    await page.wait_for_selector('#telegram-search-input', timeout=15000)
                except Exception:
                    return "Telegram Web is not logged in. Please log in to the browser that just opened, then try again."

                # Search
                await page.fill('#telegram-search-input', contact_name)
                await page.keyboard.press("Enter")
                await asyncio.sleep(2)
                
                # Click call button (header right actions)
                try:
                    call_btn = await page.wait_for_selector('.HeaderActions .Button.call', timeout=5000)
                    await call_btn.click()
                    return f"Successfully initiated voice call to {contact_name} on Telegram."
                except Exception:
                    return f"Could not find Voice Call button for {contact_name} on Telegram."
                    
        except Exception as e:
            return f"Telegram automation failed: {e}"

async def handle_voice_command(app: str, contact_name: str) -> str:
    """Router hook for making voice calls."""
    agent = VoiceCallingAgent()
    if app.lower() == "whatsapp":
        return await agent.call_whatsapp(contact_name)
    elif app.lower() == "telegram":
        return await agent.call_telegram(contact_name)
        return f"Unsupported calling app: {app}. Use whatsapp or telegram."

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ARIA Voice Calling Agent")
    parser.add_argument("app", choices=["whatsapp", "telegram"], help="App to call on")
    parser.add_argument("contact", type=str, help="Name of the contact to call")
    
    args = parser.parse_args()
    print(asyncio.run(handle_voice_command(args.app, args.contact)))
