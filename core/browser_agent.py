"""
ARIA v7 — Advanced Browser Agent
Universal LLM-powered browser automation. No per-site training needed.

This is NOT a simple web scraper. ARIA's browser agent can:
- Navigate to ANY website and understand its structure via LLM vision
- Fill forms, click buttons, submit data — all autonomously
- Log into websites using credentials from EncryptedStorage
- Extract structured data from complex SPAs (React, Vue, Angular)
- Handle multi-page workflows (checkout flows, form wizards)
- Take screenshots and interpret visual elements
- Download files from complex sites

Architecture:
  Layer 1 — Scrapling (stealth fetcher for fast read-only scraping)
  Layer 2 — browser-use (LLM-driven autonomous browsing for interactive tasks)
  Layer 3 — Raw Playwright (fallback for precision DOM control)

The agent auto-selects the best layer based on the task complexity.
"""

import os
import re
import json
import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List

log = logging.getLogger("ARIA.browser")

ARIA_DIR = Path.home() / "aria"
DOWNLOADS_DIR = ARIA_DIR / "downloads"
SCREENSHOTS_DIR = ARIA_DIR / "memory" / "screenshots"


class BrowserAgent:
    """
    Universal browser agent powered by LLM intelligence.
    
    Usage:
        agent = BrowserAgent(llm_api_key="nvapi-...", llm_base_url="https://...")
        
        # Simple scrape (Layer 1 — Scrapling, fast)
        content = await agent.scrape("https://example.com")
        
        # Smart browse (Layer 2 — browser-use, autonomous)
        result = await agent.browse("Go to GitHub and star the browser-use repo")
        
        # Interactive task with credentials
        result = await agent.browse(
            "Log into Gmail and check unread emails",
            credentials={"email": "user@gmail.com", "password": "xxx"}
        )
        
        # Screenshot
        path = await agent.screenshot("https://example.com")
    """

    def __init__(self, llm_api_key: str = None, llm_base_url: str = None,
                 llm_model: str = None):
        self._api_key = llm_api_key or os.environ.get("NVIDIA_API_KEY", "")
        self._base_url = llm_base_url or os.environ.get(
            "ARIA_LLM_BASE_URL", "https://integrate.api.nvidia.com/v1"
        )
        self._model = llm_model or os.environ.get(
            "ARIA_LLM_MODEL", "nvidia/llama-3.1-nemotron-ultra-253b-v1"
        )
        self._browser = None
        self._playwright_ctx = None
        self._initialized = False

        # Ensure directories
        DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    # ─── Layer 1: Scrapling (Fast Read-Only) ──────────────

    async def scrape(self, url: str, extract_links: bool = False,
                     css_selector: str = None) -> Dict[str, Any]:
        """
        Fast stealth scrape of a URL. No browser needed.
        Best for: reading articles, getting page text, extracting links.
        
        Returns dict with: url, title, text, links (optional), html_snippet
        """
        try:
            from scrapling import StealthyFetcher
            
            fetcher = StealthyFetcher()
            # StealthyFetcher uses sync Playwright internally,
            # must run in a thread to avoid blocking the async loop
            page = await asyncio.to_thread(fetcher.fetch, url)

            # Scrapling v0.4 returns a Response object — use .css() not .css_first()
            title_els = page.css("title")
            title = title_els[0].text if title_els else ""

            result = {
                "url": url,
                "title": title,
                "status": "success",
            }

            if css_selector:
                elements = page.css(css_selector)
                result["selected"] = [el.text for el in elements]
                result["selected_count"] = len(elements)
            else:
                # Extract main text content
                body_els = page.css("body")
                if body_els:
                    text = body_els[0].get_all_text()
                    result["text"] = text[:8000] if len(text) > 8000 else text
                else:
                    result["text"] = ""

            if extract_links:
                links = []
                for a in page.css("a[href]"):
                    href = a.attrib.get("href", "")
                    link_text = str(a.text).strip() if a.text else ""
                    if href and not href.startswith("#") and not href.startswith("javascript:"):
                        links.append({"text": link_text[:100], "href": href})
                result["links"] = links[:50]

            return result

        except Exception as e:
            log.error(f"Scrape failed: {e}")
            return {"url": url, "status": "error", "error": str(e)}

    # ─── Layer 2: browser-use (LLM-Powered Autonomous) ────

    async def browse(self, task: str, url: str = None,
                     credentials: Dict[str, str] = None,
                     max_steps: int = 25,
                     timeout: int = 300) -> Dict[str, Any]:
        """
        Autonomous LLM-driven browsing. The agent understands any website
        and can perform complex multi-step interactions.
        
        No per-site training needed — the LLM reads the DOM and decides
        what to click, type, and navigate.
        
        Args:
            task: Natural language description of what to do.
                  e.g., "Find the cheapest flight from Delhi to Mumbai on March 15"
            url: Optional starting URL. If not given, agent starts from Google.
            credentials: Optional dict with login credentials to inject.
            max_steps: Maximum browsing steps before giving up.
            timeout: Total timeout in seconds.
            
        Returns:
            Dict with: status, result, steps_taken, screenshots
        """
        try:
            from browser_use import Agent, Browser, BrowserConfig
            from openai import AsyncOpenAI

            # Build the full task prompt
            full_task = task
            if url:
                full_task = f"Go to {url} and then: {task}"
            if credentials:
                cred_str = ", ".join(f"{k}: {v}" for k, v in credentials.items())
                full_task += f"\n\nUse these credentials if login is needed: {cred_str}"

            # Configure browser
            browser_config = BrowserConfig(
                headless=True,
                disable_security=False,
            )
            browser = Browser(config=browser_config)

            # Configure LLM
            llm = AsyncOpenAI(
                api_key=self._api_key,
                base_url=self._base_url,
            )

            # Create the autonomous agent
            agent = Agent(
                task=full_task,
                llm=llm,
                browser=browser,
                max_actions_per_step=5,
            )

            # Run the agent
            result = await asyncio.wait_for(
                agent.run(max_steps=max_steps),
                timeout=timeout
            )

            # Extract final result
            final_result = result.final_result() if hasattr(result, 'final_result') else str(result)
            history = result.history() if hasattr(result, 'history') else []

            await browser.close()

            return {
                "status": "success",
                "result": final_result,
                "steps_taken": len(history) if history else 0,
                "task": task,
            }

        except asyncio.TimeoutError:
            log.error(f"Browser agent timed out after {timeout}s")
            return {"status": "timeout", "error": f"Task timed out after {timeout}s", "task": task}
        except ImportError as e:
            log.error(f"browser-use not properly installed: {e}")
            return {"status": "error", "error": f"Missing dependency: {e}", "task": task}
        except Exception as e:
            log.error(f"Browser agent error: {e}")
            return {"status": "error", "error": str(e)[:500], "task": task}

    # ─── Layer 3: Direct Playwright (Fine Control) ────────

    async def _ensure_playwright(self):
        """Initialize Playwright browser if not already running."""
        if self._playwright_ctx:
            return
        try:
            from playwright.async_api import async_playwright
            self._playwright_ctx = await async_playwright().start()
            self._browser = await self._playwright_ctx.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-gpu"]
            )
            log.info("Playwright browser launched")
        except Exception as e:
            log.error(f"Playwright init failed: {e}")

    async def screenshot(self, url: str, full_page: bool = False) -> str:
        """
        Take a screenshot of any URL.
        Returns the file path to the saved screenshot.
        """
        await self._ensure_playwright()
        if not self._browser:
            return "Error: Browser not available"

        try:
            context = await self._browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Save screenshot
            filename = f"screenshot_{hash(url) % 100000}.png"
            filepath = str(SCREENSHOTS_DIR / filename)
            await page.screenshot(path=filepath, full_page=full_page)
            
            await context.close()
            log.info(f"Screenshot saved: {filepath}")
            return filepath

        except Exception as e:
            log.error(f"Screenshot failed: {e}")
            return f"Error: {e}"

    async def execute_js(self, url: str, script: str) -> str:
        """
        Navigate to a URL and execute arbitrary JavaScript.
        Returns the result of the JS evaluation.
        """
        await self._ensure_playwright()
        if not self._browser:
            return "Error: Browser not available"

        try:
            context = await self._browser.new_context()
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            result = await page.evaluate(script)
            await context.close()
            return str(result)
        except Exception as e:
            return f"Error: {e}"

    async def download_file(self, url: str, filename: str = None) -> str:
        """
        Download a file from a URL using the browser (handles JS-protected downloads).
        Returns path to the downloaded file.
        """
        await self._ensure_playwright()
        if not self._browser:
            return "Error: Browser not available"

        try:
            context = await self._browser.new_context(
                accept_downloads=True,
            )
            page = await context.new_page()

            # Start waiting for download before triggering it
            async with page.expect_download(timeout=60000) as download_info:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            download = await download_info.value
            save_path = str(DOWNLOADS_DIR / (filename or download.suggested_filename))
            await download.save_as(save_path)
            await context.close()
            
            log.info(f"Downloaded: {save_path}")
            return save_path

        except Exception as e:
            log.error(f"Download failed: {e}")
            return f"Error: {e}"

    # ─── Smart Task Router ────────────────────────────────

    async def auto(self, task: str, url: str = None, **kwargs) -> Dict[str, Any]:
        """
        Intelligent auto-routing: picks the best layer for the task.
        
        - Simple reads → Scrapling (fast, no browser overhead)
        - Interactive tasks → browser-use (LLM autonomous)
        - Screenshots → Playwright direct
        - Downloads → Playwright with download handler
        
        This is the main entry point ARIA's agent loop should call.
        """
        task_lower = task.lower()

        # Route: Screenshot
        if any(kw in task_lower for kw in ["screenshot", "capture screen", "take a picture of"]):
            target_url = url or self._extract_url(task) or "https://google.com"
            path = await self.screenshot(target_url, full_page="full" in task_lower)
            return {"status": "success", "result": f"Screenshot saved: {path}", "path": path}

        # Route: Simple scrape / read
        if url and any(kw in task_lower for kw in ["read", "scrape", "get text", "extract", "fetch"]):
            result = await self.scrape(url, extract_links="link" in task_lower)
            return result

        # Route: Download
        if any(kw in task_lower for kw in ["download", "save file"]):
            target_url = url or self._extract_url(task)
            if target_url:
                path = await self.download_file(target_url)
                return {"status": "success", "result": f"Downloaded: {path}", "path": path}

        # Route: Everything else → autonomous LLM browser agent
        result = await self.browse(task, url=url, **kwargs)
        return result

    def _extract_url(self, text: str) -> Optional[str]:
        """Extract the first URL from text."""
        match = re.search(r'https?://[^\s<>"\']+', text)
        return match.group(0) if match else None

    # ─── Cleanup ──────────────────────────────────────────

    async def close(self):
        """Shutdown the browser."""
        if self._browser:
            await self._browser.close()
        if self._playwright_ctx:
            await self._playwright_ctx.stop()
        self._browser = None
        self._playwright_ctx = None

    def get_status(self) -> str:
        """Get browser agent status."""
        layers = []
        try:
            import scrapling
            layers.append("Scrapling ✅")
        except ImportError:
            layers.append("Scrapling ❌")

        try:
            import browser_use
            layers.append("browser-use ✅")
        except ImportError:
            layers.append("browser-use ❌")

        try:
            import playwright
            layers.append("Playwright ✅")
        except ImportError:
            layers.append("Playwright ❌")

        return (
            f"🌐 Browser Agent Status:\n"
            f"  Layers: {' | '.join(layers)}\n"
            f"  Active Browser: {'Yes' if self._browser else 'No'}\n"
            f"  Downloads: {DOWNLOADS_DIR}\n"
            f"  Screenshots: {SCREENSHOTS_DIR}"
        )
